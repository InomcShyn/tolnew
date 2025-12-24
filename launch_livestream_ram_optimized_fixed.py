#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 LAUNCH LIVESTREAM - RAM OPTIMIZED + PROPER LIVE JOIN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Combines:
1. RAM optimizations from launch_livestream_ram_optimized.py
2. Proper live join logic from launch_livestream_tiktok.py

Target: 200-250MB RAM + Proper view counting
"""

import asyncio
import time
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

# Import live join logic
from core.live_join_2025 import execute_live_join_2025

# Import baseline collector
from baseline_collector_2025 import (
    BaselineCollector,
    get_browser_state_script,
    get_video_state_script,
    get_audio_state_script
)


def get_ram_optimized_chrome_args() -> List[str]:
    """RAM optimized Chrome flags"""
    return [
        # Stealth
        '--disable-blink-features=AutomationControlled',
        '--exclude-switches=enable-automation',
        '--disable-infobars',
        
        # Window
        '--window-size=360,640',
        '--window-position=0,0',
        
        # GPU (needed for video)
        '--enable-gpu',
        '--ignore-gpu-blocklist',
        '--enable-accelerated-video-decode',
        
        # RAM optimization
        '--disk-cache-size=1',
        '--media-cache-size=1',
        '--disable-background-networking',
        '--disable-sync',
        '--disable-default-apps',
        '--disable-features=Translate,OptimizationGuideModelDownloading,MediaRouter,AudioServiceOutOfProcess',
        '--disable-component-update',
        '--disable-domain-reliability',
        '--no-first-run',
        '--no-default-browser-check',
        '--disable-dev-shm-usage',
        '--num-raster-threads=1',
        '--js-flags=--max-old-space-size=96,--gc-interval=100',
        '--disable-threaded-animation',
        '--disable-image-animation-resync',
        '--disable-gpu-compositing',
        '--disable-partial-raster',
    ]


async def setup_resource_blocking(page):
    """Block unnecessary resources"""
    try:
        await page.route("**/*", lambda route: (
            route.abort() if route.request.resource_type in ["stylesheet", "font", "image"]
            or any(x in route.request.url for x in ['analytics', 'tracking', 'ads', 'doubleclick'])
            else route.continue_()
        ))
        print("[RAM-OPT] ✅ Resource blocking enabled")
    except Exception as e:
        print(f"[RAM-OPT] ⚠️  Resource blocking error: {e}")


async def setup_memory_cleanup(page, interval_seconds: int = 60):
    """Auto memory cleanup"""
    try:
        while True:
            await asyncio.sleep(interval_seconds)
            await page.evaluate("""
                () => {
                    if (window.gc) window.gc();
                    const videos = document.querySelectorAll('video');
                    videos.forEach(v => {
                        if (v.buffered.length > 0 && v.currentTime > 5) {
                            const t = v.currentTime;
                            v.currentTime = t;
                        }
                    });
                }
            """)
            print(f"[RAM-OPT] 🧹 Memory cleanup executed")
    except:
        pass


async def get_performance_metrics(page) -> Dict:
    """Get performance metrics"""
    try:
        return await page.evaluate("""
            () => {
                const timing = performance.timing;
                const memory = performance.memory;
                return {
                    dom_ready_ms: timing.domContentLoadedEventEnd - timing.navigationStart,
                    memory_used_mb: memory ? Math.round(memory.usedJSHeapSize / 1024 / 1024) : 0,
                    memory_limit_mb: memory ? Math.round(memory.jsHeapSizeLimit / 1024 / 1024) : 0
                };
            }
        """)
    except:
        return {}


async def launch_livestream_optimized(
    profile_name: str,
    livestream_url: str,
    collect_baseline: bool = True,
    monitor_duration: int = 120
):
    """
    Launch livestream with RAM optimization + proper live join
    """
    from playwright.async_api import async_playwright
    
    # Initialize baseline collector
    collector = None
    if collect_baseline:
        collector = BaselineCollector(profile_name, f"optimized_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        collector.collect_bootstrap(note="RAM optimized + live join")
    
    print("\n" + "="*70)
    print("🚀 LAUNCH LIVESTREAM - RAM OPTIMIZED + LIVE JOIN")
    print("="*70)
    print(f"Profile: {profile_name}")
    print(f"URL: {livestream_url}")
    print(f"Target RAM: ~250MB")
    print(f"Monitor: {monitor_duration}s")
    print("="*70 + "\n")
    
    async with async_playwright() as p:
        chrome_args = get_ram_optimized_chrome_args()
        
        print(f"[LAUNCH] Chrome flags: {len(chrome_args)} flags")
        
        browser = await p.chromium.launch(
            headless=False,
            args=chrome_args,
            channel='chrome'
        )
        
        context = await browser.new_context(
            viewport={'width': 360, 'height': 640},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
            locale='en-US',
            timezone_id='America/New_York'
        )
        
        page = await context.new_page()
        
        if collector:
            import psutil
            chrome_pid = browser._impl_obj._browser_process.pid if hasattr(browser._impl_obj, '_browser_process') else 0
            collector.collect_profile_started(
                chrome_pid=chrome_pid,
                chrome_command=" ".join(chrome_args),
                window_size="360x640",
                user_agent="Chrome/126.0.0.0",
                note="RAM optimized Chrome launched"
            )
        
        # Setup optimizations
        print("\n[RAM-OPT] Setting up optimizations...")
        await setup_resource_blocking(page)
        
        # Navigate
        print(f"\n[NAV] Navigating to: {livestream_url}")
        start_time = time.time()
        
        try:
            await page.goto(livestream_url, wait_until='domcontentloaded', timeout=30000)
            nav_time = time.time() - start_time
            print(f"[NAV] ✅ Page loaded in {nav_time:.1f}s")
            
            perf_metrics = await get_performance_metrics(page)
            print(f"[PERF] DOM ready: {perf_metrics.get('dom_ready_ms', 0)}ms")
            print(f"[PERF] Memory: {perf_metrics.get('memory_used_mb', 0)}MB / {perf_metrics.get('memory_limit_mb', 0)}MB")
            
            if collector:
                browser_state = await page.evaluate(get_browser_state_script())
                collector.collect_profile_page_loaded(
                    url=livestream_url,
                    dom_ready_ms=perf_metrics.get('dom_ready_ms', 0),
                    full_render_ms=0,
                    browser_state=browser_state,
                    note="Page loaded with RAM optimizations"
                )
            
        except Exception as e:
            print(f"[NAV] ❌ Navigation error: {e}")
            await browser.close()
            return
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # EXECUTE LIVE JOIN 2025 (Proper logic)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        
        print("\n" + "="*70)
        print("🎯 EXECUTING LIVE JOIN 2025")
        print("="*70)
        
        try:
            state, fail_reason, details = await execute_live_join_2025(page, profile_name)
            
            print(f"\n[LIVE-JOIN] Final state: {state}")
            if fail_reason:
                print(f"[LIVE-JOIN] Fail reason: {fail_reason}")
            
            print(f"\n[LIVE-JOIN] Details:")
            for key, value in details.items():
                print(f"  {key}: {value}")
            
            # Check if successful
            if state == "LIVE_PLAYING":
                print("\n✅ Successfully joined livestream!")
                
                # Get video/audio state
                video_state = await page.evaluate(get_video_state_script())
                audio_state = await page.evaluate(get_audio_state_script())
                
                print(f"\n[VIDEO] Ready: {video_state.get('readyState', 0)}/4")
                print(f"[VIDEO] Paused: {video_state.get('paused', True)}")
                print(f"[AUDIO] State: {audio_state.get('state', 'unknown')}")
                
                if collector:
                    collector.collect_live_playing(
                        video_state=video_state,
                        audio_state=audio_state,
                        websocket_state={'connected': True},
                        note="Live playing with RAM optimizations"
                    )
                
            else:
                print(f"\n⚠️  Failed to join livestream: {state}")
                if fail_reason:
                    print(f"Reason: {fail_reason}")
                
        except Exception as e:
            print(f"\n❌ Live join error: {e}")
            import traceback
            traceback.print_exc()
        
        # Start memory cleanup
        print("\n[RAM-OPT] Starting memory cleanup loop...")
        cleanup_task = asyncio.create_task(setup_memory_cleanup(page, interval_seconds=60))
        
        # Monitor
        print(f"\n[MONITOR] Monitoring for {monitor_duration} seconds...")
        print("Press Ctrl+C to stop\n")
        
        try:
            for i in range(monitor_duration // 10):
                await asyncio.sleep(10)
                current_perf = await get_performance_metrics(page)
                print(f"[{i*10:3}s] Memory: {current_perf.get('memory_used_mb', 0)}MB / {current_perf.get('memory_limit_mb', 0)}MB")
                
        except KeyboardInterrupt:
            print("\n[MONITOR] Stopped by user")
        
        # Final state
        if collector:
            final_video = await page.evaluate(get_video_state_script())
            final_audio = await page.evaluate(get_audio_state_script())
            
            collector.collect_view_window_elapsed(
                watch_duration_s=float(monitor_duration),
                view_eligibility={
                    'video_ready': final_video.get('readyState', 0) == 4,
                    'audio_state': final_audio.get('state', 'unknown'),
                    'memory_optimized': True
                },
                final_state={'note': 'RAM optimized session completed'},
                note=f"Final state after {monitor_duration}s"
            )
            
            summary_file = collector.generate_summary()
            print(f"\n[BASELINE] ✅ Summary: {summary_file}")
        
        # Cleanup
        cleanup_task.cancel()
        await browser.close()
        
        print("\n" + "="*70)
        print("✅ LAUNCH COMPLETED")
        print("="*70)


if __name__ == "__main__":
    import sys
    
    print("\n" + "="*70)
    print("🚀 LAUNCH LIVESTREAM - RAM OPTIMIZED + LIVE JOIN")
    print("="*70)
    print("\nFeatures:")
    print("  ✅ RAM optimization (~250MB target)")
    print("  ✅ Proper live join logic")
    print("  ✅ View counting enabled")
    print("  ✅ Baseline collection")
    print("="*70 + "\n")
    
    profile_name = input("Profile name (e.g. 001): ").strip() or "001"
    livestream_url = input("Livestream URL: ").strip()
    
    if not livestream_url:
        print("❌ URL is required")
        sys.exit(1)
    
    collect = input("Collect baseline? (y/n): ").strip().lower() == 'y'
    duration = input("Monitor duration (seconds, default 120): ").strip()
    duration = int(duration) if duration.isdigit() else 120
    
    try:
        asyncio.run(launch_livestream_optimized(profile_name, livestream_url, collect, duration))
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
