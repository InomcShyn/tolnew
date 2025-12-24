#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎯 BASELINE BEHAVIOR COLLECTOR - TikTok LIVE 2025
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Ghi nhận toàn bộ hành vi runtime THỦ CÔNG để:
- Xây dựng baseline chuẩn TikTok Web 2025
- So sánh view được tính vs không được tính
- Tối ưu RAM từng bước mà không phá view eligibility

LUỒNG KHỞI ĐỘNG (BẮT BUỘC):
1. python launcher.py
2. Mở gui_manager_modern
3. Khởi động profile bằng nút "Starting" (không auto-join)
4. Thao tác THỦ CÔNG trên trình duyệt để vào TikTok LIVE

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import json
import time
import psutil
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
import subprocess


class BaselineCollector:
    """Collector for TikTok LIVE baseline behavior data"""
    
    def __init__(self, profile_id: str, session_name: str = ""):
        """
        Initialize baseline collector
        
        Args:
            profile_id: Profile identifier (e.g. "001", "X-001")
            session_name: Optional session name for comparison
        """
        self.profile_id = profile_id
        self.session_name = session_name or datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create output directory
        self.output_dir = Path("baseline_data") / f"{profile_id}_{self.session_name}"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Timing
        self.start_time = time.time()
        self.start_monotonic = time.monotonic()
        
        # State tracking
        self.chrome_pid = None
        self.chrome_command = None
        self.stage_counter = 0
        
        print(f"[BASELINE] 📊 Initialized for profile: {profile_id}")
        print(f"[BASELINE] 📁 Output: {self.output_dir}")
    
    def _get_timestamp(self) -> Dict[str, Any]:
        """Get current timestamp info"""
        now = time.time()
        return {
            "timestamp_local": datetime.now().isoformat(),
            "timestamp_unix": now,
            "elapsed_seconds": round(now - self.start_time, 3),
            "monotonic": round(time.monotonic() - self.start_monotonic, 3)
        }
    
    def _get_process_info(self, pid: Optional[int] = None) -> Dict[str, Any]:
        """Get process information"""
        if pid is None:
            pid = self.chrome_pid
        
        if pid is None:
            return {
                "pid": None,
                "memory_rss_mb": 0,
                "memory_vms_mb": 0,
                "cpu_percent": 0,
                "num_threads": 0,
                "status": "not_found"
            }
        
        try:
            process = psutil.Process(pid)
            mem_info = process.memory_info()
            
            return {
                "pid": pid,
                "memory_rss_mb": round(mem_info.rss / 1024 / 1024, 2),
                "memory_vms_mb": round(mem_info.vms / 1024 / 1024, 2),
                "cpu_percent": round(process.cpu_percent(interval=0.1), 2),
                "num_threads": process.num_threads(),
                "status": process.status()
            }
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            return {
                "pid": pid,
                "error": str(e),
                "status": "error"
            }
    
    def _get_chrome_children(self, parent_pid: int) -> List[Dict[str, Any]]:
        """Get all Chrome child processes"""
        children = []
        try:
            parent = psutil.Process(parent_pid)
            for child in parent.children(recursive=True):
                try:
                    mem_info = child.memory_info()
                    children.append({
                        "pid": child.pid,
                        "name": child.name(),
                        "memory_rss_mb": round(mem_info.rss / 1024 / 1024, 2),
                        "cpu_percent": round(child.cpu_percent(interval=0.1), 2),
                        "cmdline": " ".join(child.cmdline()[:3])  # First 3 args
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
        
        return children
    
    def _save_stage(self, stage_name: str, data: Dict[str, Any], note: str = ""):
        """Save stage data to JSON file"""
        self.stage_counter += 1
        
        # Build filename
        filename = f"{self.stage_counter:02d}_{stage_name}.json"
        filepath = self.output_dir / filename
        
        # Add metadata
        full_data = {
            "stage": stage_name,
            "stage_number": self.stage_counter,
            "profile_id": self.profile_id,
            "session_name": self.session_name,
            "note": note,
            **self._get_timestamp(),
            **data
        }
        
        # Save to file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(full_data, f, indent=2, ensure_ascii=False)
        
        print(f"[BASELINE] ✅ Saved: {filename}")
        return filepath
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # STAGE 1: BOOTSTRAP (launcher.py started)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def collect_bootstrap(self, note: str = ""):
        """Collect data when launcher.py starts"""
        data = {
            "system": {
                "cpu_count": psutil.cpu_count(),
                "memory_total_gb": round(psutil.virtual_memory().total / 1024 / 1024 / 1024, 2),
                "memory_available_gb": round(psutil.virtual_memory().available / 1024 / 1024 / 1024, 2),
                "platform": os.name
            },
            "chrome_command": None,
            "chrome_pid": None
        }
        
        return self._save_stage("bootstrap", data, note)
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # STAGE 2: PROFILE STARTED (Chrome launched via "Starting" button)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def collect_profile_started(
        self,
        chrome_pid: int,
        chrome_command: str,
        window_size: str,
        user_agent: str,
        note: str = ""
    ):
        """Collect data when profile is started"""
        self.chrome_pid = chrome_pid
        self.chrome_command = chrome_command
        
        # Parse Chrome flags
        chrome_flags = chrome_command.split() if chrome_command else []
        
        data = {
            "chrome": {
                "pid": chrome_pid,
                "command_line": chrome_command,
                "flags": chrome_flags,
                "flags_count": len(chrome_flags),
                "window_size": window_size,
                "user_agent": user_agent
            },
            "process": self._get_process_info(chrome_pid),
            "children": self._get_chrome_children(chrome_pid),
            "memory_total_mb": sum(
                child["memory_rss_mb"] 
                for child in self._get_chrome_children(chrome_pid)
            ) + self._get_process_info(chrome_pid).get("memory_rss_mb", 0)
        }
        
        return self._save_stage("profile_started", data, note)
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # STAGE 3: PROFILE PAGE LOADED (https://www.tiktok.com/@username)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def collect_profile_page_loaded(
        self,
        url: str,
        dom_ready_ms: float,
        full_render_ms: float,
        browser_state: Dict[str, Any],
        note: str = ""
    ):
        """
        Collect data when profile page is loaded
        
        Args:
            url: Profile URL
            dom_ready_ms: DOMContentLoaded time
            full_render_ms: Full render time
            browser_state: Browser state from JS injection
        """
        data = {
            "navigation": {
                "url": url,
                "dom_ready_ms": dom_ready_ms,
                "full_render_ms": full_render_ms
            },
            "browser_state": browser_state,
            "process": self._get_process_info(),
            "memory_total_mb": sum(
                child["memory_rss_mb"] 
                for child in self._get_chrome_children(self.chrome_pid)
            ) + self._get_process_info().get("memory_rss_mb", 0)
        }
        
        return self._save_stage("profile_page_loaded", data, note)
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # STAGE 4: LIVE BADGE DETECTED
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def collect_live_badge_detected(
        self,
        badge_selector: str,
        badge_element: Dict[str, Any],
        dom_state: Dict[str, Any],
        note: str = ""
    ):
        """Collect data when LIVE badge is detected"""
        data = {
            "live_badge": {
                "selector": badge_selector,
                "element": badge_element,
                "detected_at": self._get_timestamp()
            },
            "dom_state": dom_state,
            "process": self._get_process_info()
        }
        
        return self._save_stage("live_badge_detected", data, note)
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # STAGE 5: LIVE CLICKED (User clicks LIVE badge)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def collect_live_clicked(
        self,
        url_before: str,
        url_after: str,
        navigation_type: str,
        history_length: int,
        transition_ms: float,
        note: str = ""
    ):
        """Collect data when LIVE is clicked"""
        data = {
            "navigation": {
                "url_before": url_before,
                "url_after": url_after,
                "navigation_type": navigation_type,
                "history_length": history_length,
                "transition_ms": transition_ms
            },
            "process": self._get_process_info()
        }
        
        return self._save_stage("live_clicked", data, note)
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # STAGE 6: LIVE PLAYING (Video is playing)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def collect_live_playing(
        self,
        video_state: Dict[str, Any],
        audio_state: Dict[str, Any],
        websocket_state: Dict[str, Any],
        note: str = ""
    ):
        """Collect data when LIVE is playing"""
        data = {
            "video": video_state,
            "audio": audio_state,
            "websocket": websocket_state,
            "process": self._get_process_info(),
            "memory_total_mb": sum(
                child["memory_rss_mb"] 
                for child in self._get_chrome_children(self.chrome_pid)
            ) + self._get_process_info().get("memory_rss_mb", 0)
        }
        
        return self._save_stage("live_playing", data, note)
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # STAGE 7: VIEW WINDOW ELAPSED (8-12 seconds watched)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def collect_view_window_elapsed(
        self,
        watch_duration_s: float,
        view_eligibility: Dict[str, Any],
        final_state: Dict[str, Any],
        note: str = ""
    ):
        """Collect data after view window elapsed"""
        data = {
            "watch_duration_s": watch_duration_s,
            "view_eligibility": view_eligibility,
            "final_state": final_state,
            "process": self._get_process_info(),
            "children": self._get_chrome_children(self.chrome_pid),
            "memory_total_mb": sum(
                child["memory_rss_mb"] 
                for child in self._get_chrome_children(self.chrome_pid)
            ) + self._get_process_info().get("memory_rss_mb", 0)
        }
        
        return self._save_stage("view_window_elapsed", data, note)
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # CUSTOM STAGE (for additional data points)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def collect_custom(self, stage_name: str, data: Dict[str, Any], note: str = ""):
        """Collect custom stage data"""
        return self._save_stage(stage_name, data, note)
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # SUMMARY & COMPARISON
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def generate_summary(self):
        """Generate summary of collected data"""
        summary_file = self.output_dir / "00_summary.json"
        
        # Load all stage files
        stages = []
        for file in sorted(self.output_dir.glob("*.json")):
            if file.name == "00_summary.json":
                continue
            with open(file, 'r', encoding='utf-8') as f:
                stages.append(json.load(f))
        
        # Build summary
        summary = {
            "profile_id": self.profile_id,
            "session_name": self.session_name,
            "total_stages": len(stages),
            "total_duration_s": stages[-1]["elapsed_seconds"] if stages else 0,
            "stages": [
                {
                    "number": s["stage_number"],
                    "name": s["stage"],
                    "elapsed_s": s["elapsed_seconds"],
                    "note": s.get("note", "")
                }
                for s in stages
            ],
            "memory_progression": [
                {
                    "stage": s["stage"],
                    "memory_mb": s.get("memory_total_mb") or s.get("process", {}).get("memory_rss_mb", 0)
                }
                for s in stages
            ],
            "generated_at": datetime.now().isoformat()
        }
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        print(f"[BASELINE] 📊 Summary generated: {summary_file}")
        return summary_file


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# BROWSER STATE INJECTION SCRIPT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def get_browser_state_script() -> str:
    """Get JavaScript to collect browser state"""
    return """
    (() => {
        const state = {
            // Document state
            document: {
                visibilityState: document.visibilityState,
                hidden: document.hidden,
                hasFocus: document.hasFocus(),
                readyState: document.readyState,
                url: window.location.href
            },
            
            // Window state
            window: {
                innerWidth: window.innerWidth,
                innerHeight: window.innerHeight,
                outerWidth: window.outerWidth,
                outerHeight: window.outerHeight,
                devicePixelRatio: window.devicePixelRatio
            },
            
            // Navigator state
            navigator: {
                userAgent: navigator.userAgent,
                webdriver: navigator.webdriver,
                userActivation: {
                    hasBeenActive: navigator.userActivation?.hasBeenActive || false,
                    isActive: navigator.userActivation?.isActive || false
                },
                deviceMemory: navigator.deviceMemory,
                hardwareConcurrency: navigator.hardwareConcurrency,
                languages: navigator.languages
            },
            
            // AudioContext availability
            audio: {
                AudioContext: typeof AudioContext !== 'undefined',
                webkitAudioContext: typeof webkitAudioContext !== 'undefined',
                contextState: null
            },
            
            // DOM elements
            dom: {
                videoElements: document.querySelectorAll('video').length,
                canvasElements: document.querySelectorAll('canvas').length,
                iframeElements: document.querySelectorAll('iframe').length
            },
            
            // Performance
            performance: {
                memory: performance.memory ? {
                    usedJSHeapSize: Math.round(performance.memory.usedJSHeapSize / 1024 / 1024),
                    totalJSHeapSize: Math.round(performance.memory.totalJSHeapSize / 1024 / 1024),
                    jsHeapSizeLimit: Math.round(performance.memory.jsHeapSizeLimit / 1024 / 1024)
                } : null,
                timing: {
                    domContentLoaded: performance.timing.domContentLoadedEventEnd - performance.timing.navigationStart,
                    loadComplete: performance.timing.loadEventEnd - performance.timing.navigationStart
                }
            }
        };
        
        // Try to get AudioContext state
        try {
            const AudioCtx = window.AudioContext || window.webkitAudioContext;
            if (AudioCtx) {
                const ctx = new AudioCtx();
                state.audio.contextState = ctx.state;
                ctx.close();
            }
        } catch (e) {
            state.audio.error = e.message;
        }
        
        return state;
    })();
    """


def get_video_state_script() -> str:
    """Get JavaScript to collect video state"""
    return """
    (() => {
        const videos = Array.from(document.querySelectorAll('video'));
        
        if (videos.length === 0) {
            return { error: 'No video elements found' };
        }
        
        // Get primary video (largest or first)
        const video = videos.reduce((prev, curr) => {
            const prevSize = prev.videoWidth * prev.videoHeight;
            const currSize = curr.videoWidth * curr.videoHeight;
            return currSize > prevSize ? curr : prev;
        });
        
        return {
            readyState: video.readyState,
            readyStateText: ['HAVE_NOTHING', 'HAVE_METADATA', 'HAVE_CURRENT_DATA', 'HAVE_FUTURE_DATA', 'HAVE_ENOUGH_DATA'][video.readyState],
            currentTime: video.currentTime,
            duration: video.duration,
            paused: video.paused,
            muted: video.muted,
            volume: video.volume,
            playbackRate: video.playbackRate,
            videoWidth: video.videoWidth,
            videoHeight: video.videoHeight,
            networkState: video.networkState,
            buffered: video.buffered.length > 0 ? {
                start: video.buffered.start(0),
                end: video.buffered.end(0)
            } : null
        };
    })();
    """


def get_audio_state_script() -> str:
    """Get JavaScript to collect audio state"""
    return """
    (() => {
        const AudioCtx = window.AudioContext || window.webkitAudioContext;
        
        if (!AudioCtx) {
            return { error: 'AudioContext not available' };
        }
        
        // Try to find existing AudioContext
        let ctx = null;
        
        // Check if TikTok has created one
        if (window.__audioContext) {
            ctx = window.__audioContext;
        } else {
            // Create temporary one to check
            try {
                ctx = new AudioCtx();
            } catch (e) {
                return { error: e.message };
            }
        }
        
        const state = {
            state: ctx.state,
            sampleRate: ctx.sampleRate,
            currentTime: ctx.currentTime,
            baseLatency: ctx.baseLatency,
            outputLatency: ctx.outputLatency
        };
        
        // Close if we created it
        if (!window.__audioContext) {
            ctx.close();
        }
        
        return state;
    })();
    """


def get_websocket_state_script() -> str:
    """Get JavaScript to collect WebSocket state"""
    return """
    (() => {
        // Find TikTok webcast websocket
        const wsPattern = /webcast.*tiktok/i;
        
        // Check if WebSocket is patched/tracked
        if (window.__websockets) {
            const tiktokWs = window.__websockets.find(ws => 
                wsPattern.test(ws.url)
            );
            
            if (tiktokWs) {
                return {
                    connected: tiktokWs.readyState === 1,
                    readyState: tiktokWs.readyState,
                    url: tiktokWs.url,
                    protocol: tiktokWs.protocol
                };
            }
        }
        
        return {
            connected: false,
            note: 'WebSocket tracking not available'
        };
    })();
    """


if __name__ == "__main__":
    print("BASELINE_COLLECTOR_2025 loaded")
    print("\nUsage:")
    print("  collector = BaselineCollector('001', 'test_session')")
    print("  collector.collect_bootstrap()")
    print("  collector.collect_profile_started(...)")
    print("  # ... etc")
    print("  collector.generate_summary()")
