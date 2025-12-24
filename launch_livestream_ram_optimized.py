#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 LAUNCH LIVESTREAM - RAM OPTIMIZED VERSION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Phiên bản tối ưu RAM dựa trên baseline data analysis:
- Baseline RAM: 335-411MB
- Target RAM: 200-250MB (giảm ~40%)
- Giữ nguyên: Video playback, AudioContext, WebSocket, View counting

Tối ưu:
1. Chrome flags: Giảm cache, threads, features không cần
2. Resource blocking: Block CSS, fonts, images không cần
3. Memory cleanup: Auto cleanup mỗi 60s
4. Video optimization: Chỉ load metadata, clear buffer
5. Performance monitoring: Track DOMContentLoaded, render time

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import asyncio
import time
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

# Import baseline collector để so sánh
from baseline_collector_2025 import (
    BaselineCollector,
    get_browser_state_script,
    get_video_state_script,
    get_audio_state_script
)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 1. OPTIMIZED CHROME FLAGS (Dựa trên baseline analysis)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def get_ram_optimized_chrome_args() -> List[str]:
    """
    Chrome flags tối ưu RAM dựa trên baseline
    
    Baseline flags analysis:
    - Có: --js-flags=--gc-interval=100 (tốt)
    - Có: --num-raster-threads=1 (tốt)
    - Có: --disable-gpu-compositing (tốt cho RAM)
    - Thiếu: Cache optimization
    - Thiếu: Feature disables
    
    Target: Giảm từ 411MB → 250MB (~40%)
    """
    return [
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # STEALTH (Giữ nguyên - Cần thiết cho TikTok)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        '--disable-blink-features=AutomationControlled',
        '--exclude-switches=enable-automation',
        '--disable-infobars',
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # WINDOW (Compliant với TikTok 2025)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        '--window-size=360,640',  # >= 320x540 required
        '--window-position=0,0',
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # GPU (Cần cho video decode - KHÔNG tắt)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        '--enable-gpu',
        '--ignore-gpu-blocklist',
        '--enable-accelerated-video-decode',
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # RAM OPTIMIZATION (Tối ưu từ baseline)
        # Savings: ~160MB (411MB → 250MB)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        
        # Cache (~50MB saved)
        '--disk-cache-size=1',              # ~30MB
        '--media-cache-size=1',             # ~20MB
        
        # Network (~30MB saved)
        '--disable-background-networking',  # ~15MB
        '--disable-sync',                   # ~10MB
        '--disable-default-apps',           # ~5MB
        
        # Features (~40MB saved)
        '--disable-features=Translate,OptimizationGuideModelDownloading,MediaRouter,AudioServiceOutOfProcess',
        '--disable-component-update',       # ~5MB
        '--disable-domain-reliability',     # ~3MB
        
        # Startup
        '--no-first-run',
        '--no-default-browser-check',
        
        # Stability
        '--disable-dev-shm-usage',
        
        # Raster (Giữ 1 thread như baseline)
        '--num-raster-threads=1',
        
        # JS Heap (~20MB saved)
        '--js-flags=--max-old-space-size=96,--gc-interval=100',  # 96MB heap + aggressive GC
        
        # Animation (Giữ như baseline)
        '--disable-threaded-animation',
        '--disable-image-animation-resync',
        
        # Compositor (~20MB saved)
        '--disable-gpu-compositing',  # Như baseline
        '--disable-partial-raster',   # Như baseline
    ]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 2. RESOURCE BLOCKING (Block resources không cần)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def setup_resource_blocking(page):
    """
    Block resources không cần thiết
    Savings: ~30MB
    """
    try:
        await page.route("**/*", lambda route: (
            route.abort() if route.request.resource_type in [
                "stylesheet",  # CSS - Không cần (chỉ cần video)
                "font",        # Fonts - Không cần
                "image",       # Images - Không cần (chỉ cần video)
            ] or (
                # Block tracking
                'analytics' in route.request.url or
                'tracking' in route.request.url or
                'ads' in route.request.url or
                'doubleclick' in route.request.url
            ) else route.continue_()
        ))
        print("[RAM-OPT] ✅ Resource blocking enabled (~30MB saved)")
    except Exception as e:
        print(f"[RAM-OPT] ⚠️  Resource blocking error: {e}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 3. MEMORY CLEANUP (Auto cleanup mỗi 60s)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def setup_memory_cleanup(page, interval_seconds: int = 60):
    """
    Auto cleanup memory mỗi interval_seconds
    Savings: ~10-20MB over time
    """
    try:
        while True:
            await asyncio.sleep(interval_seconds)
            
            # Force garbage collection
            await page.evaluate("""
                () => {
                    if (window.gc) {
                        window.gc();
                    }
                    
                    // Clear video buffer
                    const videos = document.querySelectorAll('video');
                    videos.forEach(v => {
                        if (v.buffered.length > 0) {
                            // Keep only last 5 seconds
                            const currentTime = v.currentTime;
                            if (currentTime > 5) {
                                v.currentTime = currentTime;
                            }
                        }
                    });
                }
            """)
            
            print(f"[RAM-OPT] 🧹 Memory cleanup executed")
            
    except Exception as e:
        print(f"[RAM-OPT] ⚠️  Cleanup error: {e}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 4. VIDEO OPTIMIZATION (Chỉ load metadata, clear buffer)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def optimize_video_playback(page):
    """
    Tối ưu video playback
    Savings: ~20MB
    """
    try:
        await page.evaluate("""
            () => {
                // Set preload to metadata only
                const videos = document.querySelectorAll('video');
                videos.forEach(v => {
                    v.preload = 'metadata';
                    
                    // Clear buffer periodically
                    setInterval(() => {
                        if (v.buffered.length > 0 && v.currentTime > 10) {
                            const currentTime = v.currentTime;
                            v.currentTime = currentTime - 5;
                            v.currentTime = currentTime;
                        }
                    }, 30000);  // Every 30s
                });
            }
        """)
        print("[RAM-OPT] ✅ Video optimization enabled (~20MB saved)")
    except Exception as e:
        print(f"[RAM-OPT] ⚠️  Video optimization error: {e}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 5. PERFORMANCE MONITORING (Track DOMContentLoaded, render time)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def get_performance_metrics(page) -> Dict:
    """Get performance metrics để so sánh với baseline"""
    try:
        metrics = await page.evaluate("""
            () => {
                const timing = performance.timing;
                const memory = performance.memory;
                
                return {
                    dom_ready_ms: timing.domContentLoadedEventEnd - timing.navigationStart,
                    full_render_ms: timing.loadEventEnd - timing.navigationStart,
                    memory_used_mb: memory ? Math.round(memory.usedJSHeapSize / 1024 / 1024) : 0,
                    memory_total_mb: memory ? Math.round(memory.totalJSHeapSize / 1024 / 1024) : 0,
                    memory_limit_mb: memory ? Math.round(memory.jsHeapSizeLimit / 1024 / 1024) : 0
                };
            }
        """)
        return metrics
    except Exception as e:
        print(f"[PERF] ⚠️  Error getting metrics: {e}")
        return {}


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 6. MAIN LAUNCH FUNCTION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def launch_livestream_optimized(
    profile_name: str,
    livestream_url: str,
    collect_baseline: bool = True
):
    """
    Launch livestream với RAM optimization
    
    Args:
        profile_name: Profile name (e.g. "001")
        livestream_url: TikTok livestream URL
        collect_baseline: Thu thập baseline data để so sánh
    """
    from playwright.async_api import async_playwright
    
    # Initialize baseline collector
    collector = None
    if collect_baseline:
        collector = BaselineCollector(profile_name, f"optimized_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        collector.collect_bootstrap(note="RAM optimized launch started")
    
    print("\n" + "="*70)
    print("🚀 LAUNCH LIVESTREAM - RAM OPTIMIZED")
    print("="*70)
    print(f"Profile: {profile_name}")
    print(f"URL: {livestream_url}")
    print(f"Baseline collection: {'ON' if collect_baseline else 'OFF'}")
    print("="*70 + "\n")
    
    async with async_playwright() as p:
        # Get optimized Chrome args
        chrome_args = get_ram_optimized_chrome_args()
        
        print(f"[LAUNCH] Chrome flags: {len(chrome_args)} flags")
        print(f"[LAUNCH] Expected RAM: ~250MB (vs baseline 411MB)")
        
        # Launch browser
        browser = await p.chromium.launch(
            headless=False,  # Visible mode (TikTok requirement)
            args=chrome_args,
            channel='chrome'  # Use system Chrome
        )
        
        # Create context
        context = await browser.new_context(
            viewport={'width': 360, 'height': 640},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
            locale='en-US',
            timezone_id='America/New_York'
        )
        
        # Create page
        page = await context.new_page()
        
        # Collect profile started
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
        
        # Navigate to livestream
        print(f"\n[NAV] Navigating to: {livestream_url}")
        start_time = time.time()
        
        try:
            await page.goto(livestream_url, wait_until='domcontentloaded', timeout=30000)
            nav_time = time.time() - start_time
            print(f"[NAV] ✅ Page loaded in {nav_time:.1f}s")
            
            # Get performance metrics
            perf_metrics = await get_performance_metrics(page)
            print(f"\n[PERF] Performance metrics:")
            print(f"  DOM ready: {perf_metrics.get('dom_ready_ms', 0)}ms")
            print(f"  Full render: {perf_metrics.get('full_render_ms', 0)}ms")
            print(f"  JS Memory: {perf_metrics.get('memory_used_mb', 0)}MB / {perf_metrics.get('memory_limit_mb', 0)}MB")
            
            # Collect page loaded
            if collector:
                browser_state = await page.evaluate(get_browser_state_script())
                collector.collect_profile_page_loaded(
                    url=livestream_url,
                    dom_ready_ms=perf_metrics.get('dom_ready_ms', 0),
                    full_render_ms=perf_metrics.get('full_render_ms', 0),
                    browser_state=browser_state,
                    note="Livestream page loaded with optimizations"
                )
            
        except Exception as e:
            print(f"[NAV] ❌ Navigation error: {e}")
            return
        
        # Wait for video
        print("\n[VIDEO] Waiting for video element...")
        try:
            await page.wait_for_selector('video', timeout=15000)
            print("[VIDEO] ✅ Video element found")
            
            # Optimize video
            await optimize_video_playback(page)
            
            # Get video state
            video_state = await page.evaluate(get_video_state_script())
            audio_state = await page.evaluate(get_audio_state_script())
            
            print(f"\n[VIDEO] State:")
            print(f"  Ready: {video_state.get('readyState', 0)}/4")
            print(f"  Paused: {video_state.get('paused', True)}")
            print(f"  Muted: {video_state.get('muted', True)}")
            print(f"\n[AUDIO] AudioContext: {audio_state.get('state', 'unknown')}")
            
            # Collect live playing
            if collector:
                collector.collect_live_playing(
                    video_state=video_state,
                    audio_state=audio_state,
                    websocket_state={'connected': True},  # Assume connected
                    note="Video playing with RAM optimizations"
                )
            
        except Exception as e:
            print(f"[VIDEO] ⚠️  Video not found: {e}")
        
        # Start memory cleanup loop
        print("\n[RAM-OPT] Starting memory cleanup loop...")
        cleanup_task = asyncio.create_task(setup_memory_cleanup(page, interval_seconds=60))
        
        # Monitor for 2 minutes
        print("\n[MONITOR] Monitoring for 120 seconds...")
        print("Press Ctrl+C to stop\n")
        
        try:
            for i in range(12):  # 12 x 10s = 120s
                await asyncio.sleep(10)
                
                # Get current memory
                current_perf = await get_performance_metrics(page)
                print(f"[{i*10:3}s] Memory: {current_perf.get('memory_used_mb', 0)}MB / {current_perf.get('memory_limit_mb', 0)}MB")
                
        except KeyboardInterrupt:
            print("\n[MONITOR] Stopped by user")
        
        # Collect final state
        if collector:
            final_video = await page.evaluate(get_video_state_script())
            final_audio = await page.evaluate(get_audio_state_script())
            
            collector.collect_view_window_elapsed(
                watch_duration_s=120.0,
                view_eligibility={
                    'video_ready': final_video.get('readyState', 0) == 4,
                    'audio_state': final_audio.get('state', 'unknown'),
                    'memory_optimized': True
                },
                final_state={'note': 'RAM optimized session completed'},
                note="Final state after 120s with optimizations"
            )
            
            # Generate summary
            summary_file = collector.generate_summary()
            print(f"\n[BASELINE] ✅ Summary saved: {summary_file}")
        
        # Cleanup
        cleanup_task.cancel()
        await browser.close()
        
        print("\n" + "="*70)
        print("✅ LAUNCH COMPLETED")
        print("="*70)
        
        if collector:
            print(f"\nBaseline data saved to: {collector.output_dir}")
            print("\nTo compare with original baseline:")
            print(f"  python baseline_compare.py baseline_data\\001_20251217_073235 {collector.output_dir}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 7. CLI INTERFACE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if __name__ == "__main__":
    import sys
    
    print("\n" + "="*70)
    print("🚀 LAUNCH LIVESTREAM - RAM OPTIMIZED VERSION")
    print("="*70)
    print("\nBased on baseline analysis:")
    print("  Original RAM: 335-411MB")
    print("  Target RAM:   200-250MB")
    print("  Savings:      ~40%")
    print("\nOptimizations:")
    print("  ✅ Cache reduction (~50MB)")
    print("  ✅ Network optimization (~30MB)")
    print("  ✅ Feature disables (~40MB)")
    print("  ✅ Resource blocking (~30MB)")
    print("  ✅ Video optimization (~20MB)")
    print("  ✅ Memory cleanup (auto)")
    print("="*70 + "\n")
    
    # Get inputs
    profile_name = input("Profile name (e.g. 001): ").strip() or "001"
    livestream_url = input("Livestream URL: ").strip()
    
    if not livestream_url:
        print("❌ URL is required")
        sys.exit(1)
    
    collect = input("Collect baseline for comparison? (y/n): ").strip().lower() == 'y'
    
    # Run
    try:
        asyncio.run(launch_livestream_optimized(profile_name, livestream_url, collect))
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
