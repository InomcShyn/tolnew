#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Live Metrics Internal API
==========================
Local web API để expose metrics từ TikTok LIVE sessions đang chạy.

KHÔNG thay đổi logic xem LIVE.
CHỈ đọc dữ liệu (read-only) từ page context.
"""

import time
import threading
from typing import Dict, Optional
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SHARED METRICS STORE (In-Memory)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class LiveMetricsStore:
    """
    Shared in-memory store for live metrics.
    Thread-safe storage accessed by both launcher and API server.
    """
    
    def __init__(self):
        self._metrics = {}  # {profile_name: metrics_dict}
        self._lock = threading.Lock()
    
    def update_metrics(self, profile_name: str, metrics: Dict):
        """
        Update metrics for a profile.
        Called by launcher during Phase 4.
        
        Args:
            profile_name: Profile identifier (e.g. "001", "X-001")
            metrics: Metrics dictionary
        """
        with self._lock:
            self._metrics[profile_name] = {
                **metrics,
                'last_updated': time.time()
            }
    
    def get_metrics(self, profile_name: str) -> Optional[Dict]:
        """
        Get metrics for a profile.
        Called by API endpoint.
        
        Args:
            profile_name: Profile identifier
        
        Returns:
            Metrics dict or None if not found
        """
        with self._lock:
            return self._metrics.get(profile_name)
    
    def get_all_metrics(self) -> Dict:
        """
        Get metrics for all profiles.
        
        Returns:
            Dict of {profile_name: metrics}
        """
        with self._lock:
            return self._metrics.copy()
    
    def remove_metrics(self, profile_name: str):
        """
        Remove metrics for a profile.
        Called when session ends.
        
        Args:
            profile_name: Profile identifier
        """
        with self._lock:
            if profile_name in self._metrics:
                del self._metrics[profile_name]


# Global shared store
METRICS_STORE = LiveMetricsStore()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FASTAPI APPLICATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

app = FastAPI(
    title="TikTok LIVE Metrics API",
    description="Internal API for real-time TikTok LIVE metrics",
    version="1.0.0"
)

# Enable CORS for web app access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "TikTok LIVE Metrics API",
        "version": "1.0.0",
        "endpoints": {
            "get_metrics": "/api/live/{profile_name}",
            "list_all": "/api/live",
            "health": "/health"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    all_metrics = METRICS_STORE.get_all_metrics()
    return {
        "status": "healthy",
        "active_sessions": len(all_metrics),
        "timestamp": time.time()
    }


@app.get("/api/live")
async def list_all_sessions():
    """
    List all active LIVE sessions.
    
    Returns:
        {
            "sessions": [
                {
                    "profile_name": "001",
                    "creator": "presscuse",
                    "status": "live",
                    "viewer_count": 1234
                },
                ...
            ],
            "total": 2,
            "timestamp": 1703123456.789
        }
    """
    all_metrics = METRICS_STORE.get_all_metrics()
    
    sessions = []
    for profile_name, metrics in all_metrics.items():
        sessions.append({
            "profile_name": profile_name,
            "creator": metrics.get("creator", "unknown"),
            "status": metrics.get("status", "unknown"),
            "viewer_count": metrics.get("viewer_count", -1),
            "last_updated": metrics.get("last_updated", 0)
        })
    
    return {
        "sessions": sessions,
        "total": len(sessions),
        "timestamp": time.time()
    }


@app.get("/api/live/{profile_name}")
async def get_live_metrics(profile_name: str):
    """
    Get real-time metrics for a specific LIVE session.
    
    Args:
        profile_name: Profile identifier (e.g. "001", "X-001")
    
    Returns:
        {
            "profile_name": "001",
            "creator": "presscuse",
            "live_url": "https://www.tiktok.com/@presscuse/live",
            "status": "live | offline | error",
            "viewer_count": 1234,
            "like_count": 56789,
            "live_duration_seconds": 2712,
            "live_start_timestamp": 1703120000,
            "server_timestamp": 1703123456,
            "navigation_context": {
                "visibility": "visible",
                "has_focus": true,
                "user_activation": true,
                "navigation_type": "navigate"
            },
            "memory": {
                "total_mb": 198,
                "js_heap_mb": 82
            }
        }
    """
    metrics = METRICS_STORE.get_metrics(profile_name)
    
    if not metrics:
        raise HTTPException(
            status_code=404,
            detail=f"No active session found for profile: {profile_name}"
        )
    
    # Check if data is stale (> 2 minutes old)
    last_updated = metrics.get('last_updated', 0)
    if time.time() - last_updated > 120:
        metrics['status'] = 'stale'
        metrics['warning'] = 'Data is stale (>2 minutes old)'
    
    return JSONResponse(content=metrics)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SERVER MANAGEMENT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def start_api_server(host: str = "127.0.0.1", port: int = 8000):
    """
    Start FastAPI server in background thread.
    
    Args:
        host: Server host (default: localhost)
        port: Server port (default: 8000)
    """
    config = uvicorn.Config(
        app,
        host=host,
        port=port,
        log_level="info",
        access_log=False  # Disable access logs to reduce noise
    )
    server = uvicorn.Server(config)
    
    # Run in background thread
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    
    print(f"\n✅ Live Metrics API started at http://{host}:{port}")
    print(f"   Endpoints:")
    print(f"   - GET /api/live/{'{profile_name}'}")
    print(f"   - GET /api/live (list all)")
    print(f"   - GET /health\n")
    
    return server


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MAIN - STANDALONE TEST
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🚀 LIVE METRICS INTERNAL API - STANDALONE MODE")
    print("="*70)
    print("\nStarting API server...")
    
    # Start server
    start_api_server(host="127.0.0.1", port=8000)
    
    # Add some test data
    print("\nAdding test data...")
    METRICS_STORE.update_metrics("001", {
        "profile_name": "001",
        "creator": "presscuse",
        "live_url": "https://www.tiktok.com/@presscuse/live",
        "status": "live",
        "viewer_count": 1234,
        "like_count": 56789,
        "live_duration_seconds": 2712,
        "live_start_timestamp": int(time.time()) - 2712,
        "server_timestamp": int(time.time()),
        "navigation_context": {
            "visibility": "visible",
            "has_focus": True,
            "user_activation": True,
            "navigation_type": "navigate"
        },
        "memory": {
            "total_mb": 198,
            "js_heap_mb": 82
        }
    })
    
    print("\n✅ Test data added for profile '001'")
    print("\nTry these URLs:")
    print("  - http://127.0.0.1:8000/")
    print("  - http://127.0.0.1:8000/api/live")
    print("  - http://127.0.0.1:8000/api/live/001")
    print("  - http://127.0.0.1:8000/health")
    print("\nPress Ctrl+C to stop...\n")
    
    try:
        # Keep running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Server stopped")
