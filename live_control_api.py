#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Live Control API - Job Management Layer
========================================
API điều khiển lifecycle của TikTok LIVE viewing jobs.

KHÔNG sửa logic launcher.
CHỈ quản lý jobs và profiles.
"""

import asyncio
import time
import uuid
import threading
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

from launch_live_ram_optimized_v2 import RAMOptimizedLiveLauncherV2
from core.managers.profile_manager import ProfileManager


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# DATA MODELS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class JobStatus(str, Enum):
    """Job status enum"""
    PENDING = "pending"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class JobInfo:
    """Job information"""
    job_id: str
    live_url: str
    target_views: int
    duration_minutes: int
    status: JobStatus
    profiles_assigned: List[str]
    profiles_running: List[str]
    start_timestamp: Optional[float] = None
    end_timestamp: Optional[float] = None
    created_at: float = None
    error: Optional[str] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = time.time()
    
    def to_dict(self):
        """Convert to dict for JSON response"""
        data = asdict(self)
        data['status'] = self.status.value
        return data
    
    def get_remaining_seconds(self) -> int:
        """Calculate remaining seconds"""
        if self.status != JobStatus.RUNNING or self.end_timestamp is None:
            return 0
        remaining = self.end_timestamp - time.time()
        return max(0, int(remaining))


class StartJobRequest(BaseModel):
    """Request model for starting a job"""
    live_url: str = Field(..., description="TikTok LIVE URL")
    target_views: int = Field(..., ge=1, le=100, description="Number of profiles to launch (1-100)")
    duration_minutes: int = Field(..., ge=1, le=1440, description="Duration in minutes (1-1440)")
    use_direct_url: bool = Field(default=True, description="Use direct URL entry (faster)")
    viewport_width: int = Field(default=720, ge=360, description="Viewport width")
    viewport_height: int = Field(default=1280, ge=640, description="Viewport height")


class StartJobResponse(BaseModel):
    """Response model for starting a job"""
    job_id: str
    status: str
    profiles_launched: List[str]
    end_timestamp: float
    message: str


class JobStatusResponse(BaseModel):
    """Response model for job status"""
    job_id: str
    live_url: str
    target_views: int
    profiles_assigned: List[str]
    profiles_running: int
    remaining_seconds: int
    status: str
    start_timestamp: Optional[float]
    end_timestamp: Optional[float]
    error: Optional[str] = None


class StopJobResponse(BaseModel):
    """Response model for stopping a job"""
    job_id: str
    status: str
    profiles_stopped: int
    message: str


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# JOB MANAGER (Thread-Safe)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class JobManager:
    """
    Manages all LIVE viewing jobs.
    Thread-safe storage and lifecycle management.
    """
    
    def __init__(self):
        self._jobs: Dict[str, JobInfo] = {}
        self._lock = threading.Lock()
        self._profile_manager = ProfileManager()
        self._launcher = None  # Will be initialized when needed
        self._active_tasks: Dict[str, asyncio.Task] = {}
        self._stop_events: Dict[str, asyncio.Event] = {}
    
    def create_job(
        self,
        live_url: str,
        target_views: int,
        duration_minutes: int
    ) -> JobInfo:
        """
        Create a new job.
        
        Args:
            live_url: TikTok LIVE URL
            target_views: Number of profiles to launch
            duration_minutes: Duration in minutes
        
        Returns:
            JobInfo object
        """
        with self._lock:
            # Generate job ID
            job_id = f"job_{uuid.uuid4().hex[:8]}"
            
            # Select profiles
            all_profiles = self._profile_manager.get_all_profiles()
            if len(all_profiles) < target_views:
                raise ValueError(
                    f"Not enough profiles. Requested: {target_views}, "
                    f"Available: {len(all_profiles)}"
                )
            
            # Assign profiles (first N available)
            profiles_assigned = list(all_profiles.keys())[:target_views]
            
            # Calculate end timestamp
            end_timestamp = time.time() + (duration_minutes * 60)
            
            # Create job
            job = JobInfo(
                job_id=job_id,
                live_url=live_url,
                target_views=target_views,
                duration_minutes=duration_minutes,
                status=JobStatus.PENDING,
                profiles_assigned=profiles_assigned,
                profiles_running=[],
                end_timestamp=end_timestamp
            )
            
            self._jobs[job_id] = job
            
            return job
    
    def get_job(self, job_id: str) -> Optional[JobInfo]:
        """Get job by ID"""
        with self._lock:
            return self._jobs.get(job_id)
    
    def get_all_jobs(self) -> List[JobInfo]:
        """Get all jobs"""
        with self._lock:
            return list(self._jobs.values())
    
    def update_job_status(self, job_id: str, status: JobStatus, error: str = None):
        """Update job status"""
        with self._lock:
            if job_id in self._jobs:
                self._jobs[job_id].status = status
                if error:
                    self._jobs[job_id].error = error
                if status == JobStatus.RUNNING and self._jobs[job_id].start_timestamp is None:
                    self._jobs[job_id].start_timestamp = time.time()
    
    def update_running_profiles(self, job_id: str, profiles: List[str]):
        """Update list of running profiles"""
        with self._lock:
            if job_id in self._jobs:
                self._jobs[job_id].profiles_running = profiles
    
    def register_stop_event(self, job_id: str, event: asyncio.Event):
        """Register stop event for a job"""
        self._stop_events[job_id] = event
    
    def trigger_stop(self, job_id: str):
        """Trigger stop event for a job"""
        if job_id in self._stop_events:
            self._stop_events[job_id].set()


# Global job manager
JOB_MANAGER = JobManager()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# JOB EXECUTOR
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def execute_job(
    job_id: str,
    live_url: str,
    profiles: List[str],
    duration_minutes: int,
    use_direct_url: bool = True,
    viewport_width: int = 720,
    viewport_height: int = 1280
):
    """
    Execute a job by launching profiles.
    
    This function:
    1. Launches all profiles
    2. Monitors them during duration
    3. Auto-stops when time expires
    4. Handles manual stop requests
    """
    
    print(f"\n{'='*70}")
    print(f"🚀 EXECUTING JOB: {job_id}")
    print(f"{'='*70}")
    print(f"Live URL:        {live_url}")
    print(f"Profiles:        {len(profiles)}")
    print(f"Duration:        {duration_minutes} minutes")
    print(f"{'='*70}\n")
    
    # Update status to STARTING
    JOB_MANAGER.update_job_status(job_id, JobStatus.STARTING)
    
    # Create stop event
    stop_event = asyncio.Event()
    JOB_MANAGER.register_stop_event(job_id, stop_event)
    
    # Initialize launcher (disable API to avoid port conflict)
    launcher = RAMOptimizedLiveLauncherV2(enable_api=False)
    
    # Launch profiles with delay
    launched_profiles = []
    failed_profiles = []
    
    for i, profile_name in enumerate(profiles, 1):
        print(f"\n[{i}/{len(profiles)}] Launching profile: {profile_name}")
        
        try:
            # Launch profile in background
            task = asyncio.create_task(
                launcher.launch_profile(
                    profile_name=profile_name,
                    live_url=live_url,
                    use_direct_url=use_direct_url,
                    hidden=True,  # Always hidden for batch jobs
                    duration_minutes=duration_minutes,
                    viewport_width=viewport_width,
                    viewport_height=viewport_height
                )
            )
            
            launched_profiles.append(profile_name)
            
            # Small delay between launches
            if i < len(profiles):
                await asyncio.sleep(3)
        
        except Exception as e:
            print(f"❌ Failed to launch {profile_name}: {e}")
            failed_profiles.append(profile_name)
    
    # Update status to RUNNING
    JOB_MANAGER.update_job_status(job_id, JobStatus.RUNNING)
    JOB_MANAGER.update_running_profiles(job_id, launched_profiles)
    
    print(f"\n✅ Job {job_id} started")
    print(f"   Launched: {len(launched_profiles)}/{len(profiles)}")
    if failed_profiles:
        print(f"   Failed: {failed_profiles}")
    
    # Monitor job until duration expires or manual stop
    end_time = time.time() + (duration_minutes * 60)
    
    try:
        while time.time() < end_time:
            # Check for manual stop
            if stop_event.is_set():
                print(f"\n⚠️  Job {job_id} stopped manually")
                break
            
            # Wait 10 seconds before next check
            try:
                await asyncio.wait_for(stop_event.wait(), timeout=10)
                break  # Stop event was set
            except asyncio.TimeoutError:
                pass  # Continue monitoring
        
        # Time expired or stopped
        if not stop_event.is_set():
            print(f"\n⏰ Job {job_id} duration expired")
        
        # Update status to STOPPING
        JOB_MANAGER.update_job_status(job_id, JobStatus.STOPPING)
        
        # Profiles will auto-exit when their duration expires
        # We just need to wait a bit for cleanup
        await asyncio.sleep(5)
        
        # Update status to COMPLETED
        JOB_MANAGER.update_job_status(job_id, JobStatus.COMPLETED)
        JOB_MANAGER.update_running_profiles(job_id, [])
        
        print(f"\n✅ Job {job_id} completed")
    
    except Exception as e:
        print(f"\n❌ Job {job_id} failed: {e}")
        JOB_MANAGER.update_job_status(job_id, JobStatus.FAILED, error=str(e))
        JOB_MANAGER.update_running_profiles(job_id, [])


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FASTAPI APPLICATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

app = FastAPI(
    title="TikTok LIVE Control API",
    description="API điều khiển lifecycle của TikTok LIVE viewing jobs",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "TikTok LIVE Control API",
        "version": "1.0.0",
        "endpoints": {
            "start_job": "POST /api/control/start",
            "get_status": "GET /api/control/status/{job_id}",
            "stop_job": "POST /api/control/stop/{job_id}",
            "list_jobs": "GET /api/control/jobs",
            "health": "GET /health"
        }
    }


@app.get("/health")
async def health_check():
    """Health check"""
    jobs = JOB_MANAGER.get_all_jobs()
    running_jobs = [j for j in jobs if j.status == JobStatus.RUNNING]
    
    return {
        "status": "healthy",
        "total_jobs": len(jobs),
        "running_jobs": len(running_jobs),
        "timestamp": time.time()
    }


@app.post("/api/control/start", response_model=StartJobResponse)
async def start_job(request: StartJobRequest, background_tasks: BackgroundTasks):
    """
    Start a new LIVE viewing job.
    
    Request:
    {
        "live_url": "https://www.tiktok.com/@abc/live",
        "target_views": 5,
        "duration_minutes": 30
    }
    
    Response:
    {
        "job_id": "job_abc123",
        "status": "starting",
        "profiles_launched": ["001", "002", "003", "004", "005"],
        "end_timestamp": 1703125400,
        "message": "Job started successfully"
    }
    """
    
    try:
        # Create job
        job = JOB_MANAGER.create_job(
            live_url=request.live_url,
            target_views=request.target_views,
            duration_minutes=request.duration_minutes
        )
        
        # Execute job in background
        background_tasks.add_task(
            execute_job,
            job_id=job.job_id,
            live_url=request.live_url,
            profiles=job.profiles_assigned,
            duration_minutes=request.duration_minutes,
            use_direct_url=request.use_direct_url,
            viewport_width=request.viewport_width,
            viewport_height=request.viewport_height
        )
        
        return StartJobResponse(
            job_id=job.job_id,
            status=job.status.value,
            profiles_launched=job.profiles_assigned,
            end_timestamp=job.end_timestamp,
            message="Job started successfully"
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start job: {e}")


@app.get("/api/control/status/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    """
    Get status of a job.
    
    Response:
    {
        "job_id": "job_abc123",
        "live_url": "https://www.tiktok.com/@abc/live",
        "target_views": 5,
        "profiles_assigned": ["001", "002", "003", "004", "005"],
        "profiles_running": 5,
        "remaining_seconds": 842,
        "status": "running",
        "start_timestamp": 1703123400,
        "end_timestamp": 1703125400
    }
    """
    
    job = JOB_MANAGER.get_job(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail=f"Job not found: {job_id}")
    
    return JobStatusResponse(
        job_id=job.job_id,
        live_url=job.live_url,
        target_views=job.target_views,
        profiles_assigned=job.profiles_assigned,
        profiles_running=len(job.profiles_running),
        remaining_seconds=job.get_remaining_seconds(),
        status=job.status.value,
        start_timestamp=job.start_timestamp,
        end_timestamp=job.end_timestamp,
        error=job.error
    )


@app.post("/api/control/stop/{job_id}", response_model=StopJobResponse)
async def stop_job(job_id: str):
    """
    Stop a running job.
    
    Response:
    {
        "job_id": "job_abc123",
        "status": "stopping",
        "profiles_stopped": 5,
        "message": "Job stop initiated"
    }
    """
    
    job = JOB_MANAGER.get_job(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail=f"Job not found: {job_id}")
    
    if job.status not in [JobStatus.STARTING, JobStatus.RUNNING]:
        raise HTTPException(
            status_code=400,
            detail=f"Job cannot be stopped. Current status: {job.status.value}"
        )
    
    # Trigger stop
    JOB_MANAGER.trigger_stop(job_id)
    JOB_MANAGER.update_job_status(job_id, JobStatus.STOPPING)
    
    return StopJobResponse(
        job_id=job.job_id,
        status="stopping",
        profiles_stopped=len(job.profiles_running),
        message="Job stop initiated"
    )


@app.get("/api/control/jobs")
async def list_jobs():
    """
    List all jobs.
    
    Response:
    {
        "jobs": [
            {
                "job_id": "job_abc123",
                "live_url": "...",
                "target_views": 5,
                "status": "running",
                "profiles_running": 5,
                "remaining_seconds": 842
            },
            ...
        ],
        "total": 2
    }
    """
    
    jobs = JOB_MANAGER.get_all_jobs()
    
    jobs_data = []
    for job in jobs:
        jobs_data.append({
            "job_id": job.job_id,
            "live_url": job.live_url,
            "target_views": job.target_views,
            "status": job.status.value,
            "profiles_assigned": job.profiles_assigned,
            "profiles_running": len(job.profiles_running),
            "remaining_seconds": job.get_remaining_seconds(),
            "created_at": job.created_at,
            "start_timestamp": job.start_timestamp,
            "end_timestamp": job.end_timestamp
        })
    
    return {
        "jobs": jobs_data,
        "total": len(jobs_data),
        "timestamp": time.time()
    }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SERVER MANAGEMENT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def start_control_api(host: str = "127.0.0.1", port: int = 8001):
    """
    Start Control API server.
    
    Args:
        host: Server host (default: localhost)
        port: Server port (default: 8001)
    """
    print("\n" + "="*70)
    print("🚀 TIKTOK LIVE CONTROL API")
    print("="*70)
    print(f"\nStarting server at http://{host}:{port}")
    print("\nEndpoints:")
    print(f"  POST   /api/control/start")
    print(f"  GET    /api/control/status/{{job_id}}")
    print(f"  POST   /api/control/stop/{{job_id}}")
    print(f"  GET    /api/control/jobs")
    print(f"  GET    /health")
    print("\n" + "="*70 + "\n")
    
    config = uvicorn.Config(
        app,
        host=host,
        port=port,
        log_level="info"
    )
    server = uvicorn.Server(config)
    server.run()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MAIN
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if __name__ == "__main__":
    try:
        start_control_api(host="127.0.0.1", port=8001)
    except KeyboardInterrupt:
        print("\n\n⚠️  Server stopped")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
