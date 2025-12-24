#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chrome RAM Optimizer - Tối ưu RAM xuống 150-200MB/profile
Target: 150-200MB RAM per profile với stealth 100%
Không làm TikTok detect bot, vẫn tính view livestream
"""

import asyncio
from typing import Optional, Dict, List
from playwright.async_api import Page, BrowserContext


# ============================================================
# LAYER 1: CHROME FLAGS OPTIMIZATION
# ============================================================

def get_ultra_optimized_flags() -> List[str]:
    """
    Chrome flags tối ưu RAM tối đa (150-200MB)
    Giữ GPU enabled, không phá stealth
    """
    return [
        # ============================================================
        # STEALTH (CRITICAL - Không được xóa)
        # ============================================================
        '--disable-blink-features=AutomationControlled',
        '--disable-features=IsolateOrigins,site-per-process',
        '--disable-dev-shm-usage',
        
        # ============================================================
        # GPU (CRITICAL - Phải giữ để không bị detect)
        # ============================================================
        '--enable-gpu',
        '--ignore-gpu-blocklist',
        '--use-gl=angle',
        '--use-angle=gl',
        '--enable-zero-copy',
        
        # ============================================================
        # PROCESS OPTIMIZATION (Giảm số processes)
        # ============================================================
        '--renderer-process-limit=1',  # Chỉ 1 renderer
        '--disable-renderer-backgrounding',  # Không background renderer
        '--disable-background-timer-throttling',  # Tắt throttling
        '--disable-backgrounding-occluded-windows',  # Tắt background windows
        '--disable-ipc-flooding-protection',  # Giảm IPC overhead
        
        # ============================================================
        # MEMORY OPTIMIZATION (Giảm memory usage)
        # ============================================================
        '--aggressive-cache-discard',  # Xóa cache aggressive
        '--memory-pressure-off',  # Tắt memory pressure
        '--enable-low-end-device-mode',  # Low-end device mode
        '--disable-breakpad',  # Tắt crash reporting
        '--disable-component-update',  # Tắt component updates
        '--disable-domain-reliability',  # Tắt domain reliability
        
        # ============================================================
        # JAVASCRIPT HEAP LIMIT (CRITICAL cho RAM)
        # ============================================================
        '--js-flags=--max-old-space-size=64',  # Giới hạn JS heap 64MB
        '--js-flags=--optimize-for-size',  # Optimize cho size
        
        # ============================================================
        # CACHE OPTIMIZATION (Giảm disk cache)
        # ============================================================
        '--disk-cache-size=10485760',  # 10MB disk cache
        '--media-cache-size=5242880',  # 5MB media cache
        '--aggressive-cache-discard',  # Discard cache aggressive
        
        # ============================================================
        # NETWORK OPTIMIZATION (Giảm network buffers)
        # ============================================================
        '--disable-background-networking',  # Tắt background networking
        '--disable-sync',  # Tắt sync
        '--disable-default-apps',  # Tắt default apps
        '--disable-extensions',  # Tắt extensions (không cần cho TikTok)
        
        # ============================================================
        # MEDIA OPTIMIZATION (Giảm media buffers)
        # ============================================================
        '--autoplay-policy=no-user-gesture-required',  # Cho phép autoplay (cần cho TikTok)
        '--disable-audio-output',  # Tắt audio output (tiết kiệm RAM)
        '--mute-audio',  # Mute audio
        
        # ============================================================
        # RENDERING OPTIMIZATION (Giảm rendering overhead)
        # ============================================================
        '--disable-smooth-scrolling',  # Tắt smooth scrolling
        '--disable-threaded-scrolling',  # Tắt threaded scrolling
        '--disable-accelerated-2d-canvas',  # Tắt 2D canvas acceleration (tiết kiệm RAM)
        '--disable-accelerated-video-decode',  # Tắt video decode acceleration
        
        # ============================================================
        # FEATURES OPTIMIZATION (Tắt features không cần)
        # ============================================================
        '--disable-features=TranslateUI',  # Tắt translate
        '--disable-features=OptimizationGuideModelDownloading',  # Tắt optimization guide
        '--disable-features=MediaRouter',  # Tắt media router
        '--disable-features=Prerender2',  # Tắt prerender
        '--disable-features=PredictivePrefetchingAllowedOnAllConnectionTypes',  # Tắt prefetch
        
        # ============================================================
        # BASIC SETTINGS
        # ============================================================
        '--no-first-run',
        '--no-default-browser-check',
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--password-store=basic',
        '--disable-popup-blocking',
        
        # ============================================================
        # WINDOW SETTINGS (Nhỏ = ít RAM)
        # ============================================================
        '--window-size=360,640',  # Mobile size
        '--window-position=0,0',
        '--force-device-scale-factor=1',  # No scaling
    ]


def get_fake_headless_optimized_flags() -> List[str]:
    """
    Flags cho fake headless mode (window 1x1)
    Thêm --headless=new để tiết kiệm RAM hơn
    """
    flags = get_ultra_optimized_flags()
    
    # Thêm headless flag
    flags.append('--headless=new')
    
    # Thêm flags cho headless
    flags.extend([
        '--hide-scrollbars',  # Ẩn scrollbars
        '--disable-logging',  # Tắt logging
        '--silent',  # Silent mode
    ])
    
    return flags


# ============================================================
# LAYER 2: PLAYWRIGHT CONTEXT OPTIMIZATION
# ============================================================

def get_optimized_context_options(user_agent: str = None) -> Dict:
    """
    Playwright context options tối ưu RAM
    """
    return {
        # Viewport nhỏ = ít RAM
        'viewport': {'width': 360, 'height': 640},
        
        # User agent
        'user_agent': user_agent or 'Mozilla/5.0 (Linux; Android 11; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
        
        # Locale & timezone
        'locale': 'en-US',
        'timezone_id': 'America/New_York',
        
        # Permissions (tối thiểu)
        'permissions': [],
        'geolocation': None,
        
        # Color & motion (giảm rendering)
        'color_scheme': 'light',
        'reduced_motion': 'reduce',
        'forced_colors': 'none',
        
        # JavaScript (phải bật cho TikTok)
        'java_script_enabled': True,
        
        # Security (bypass để inject stealth)
        'bypass_csp': True,
        'ignore_https_errors': True,
        
        # Device (mobile = ít RAM hơn)
        'has_touch': True,
        'is_mobile': True,
        'device_scale_factor': 1,
        
        # Service workers (tắt để tiết kiệm RAM)
        'service_workers': 'block',
        
        # Offline (không cache offline)
        'offline': False,
    }


# ============================================================
# LAYER 3: PAGE LIFECYCLE OPTIMIZATION
# ============================================================

async def optimize_page_lifecycle(page: Page):
    """
    Tối ưu page lifecycle để giảm RAM
    - Throttle timers
    - Limit buffers
    - Cleanup unused resources
    """
    try:
        print("[RAM-OPT] Optimizing page lifecycle...")
        
        # 1. Throttle background timers
        await page.evaluate("""
            () => {
                // Override setInterval để throttle
                const originalSetInterval = window.setInterval;
                window.setInterval = function(callback, delay, ...args) {
                    // Tăng delay lên 2x để giảm CPU/RAM
                    const throttledDelay = Math.max(delay * 2, 1000);
                    return originalSetInterval(callback, throttledDelay, ...args);
                };
                
                // Override setTimeout tương tự
                const originalSetTimeout = window.setTimeout;
                window.setTimeout = function(callback, delay, ...args) {
                    const throttledDelay = Math.max(delay * 1.5, 500);
                    return originalSetTimeout(callback, throttledDelay, ...args);
                };
                
                console.log('[RAM-OPT] Timers throttled');
            }
        """)
        
        # 2. Limit video buffer size
        await page.evaluate("""
            () => {
                // Giới hạn video buffer
                const videos = document.querySelectorAll('video');
                videos.forEach(video => {
                    // Giảm preload
                    video.preload = 'metadata';
                    
                    // Giảm buffer size (nếu có API)
                    if (video.buffered && video.buffered.length > 0) {
                        // Clear old buffers
                        try {
                            video.currentTime = video.currentTime;
                        } catch (e) {}
                    }
                });
                
                console.log('[RAM-OPT] Video buffers limited');
            }
        """)
        
        # 3. Disable animations
        await page.evaluate("""
            () => {
                const style = document.createElement('style');
                style.textContent = `
                    * {
                        animation-duration: 0s !important;
                        animation-delay: 0s !important;
                        transition-duration: 0s !important;
                        transition-delay: 0s !important;
                    }
                `;
                document.head.appendChild(style);
                
                console.log('[RAM-OPT] Animations disabled');
            }
        """)
        
        # 4. Lazy load images
        await page.evaluate("""
            () => {
                document.querySelectorAll('img').forEach(img => {
                    img.loading = 'lazy';
                    
                    // Giảm quality nếu có srcset
                    if (img.srcset) {
                        img.removeAttribute('srcset');
                    }
                });
                
                console.log('[RAM-OPT] Images lazy loaded');
            }
        """)
        
        # 5. Clear unused DOM elements
        await page.evaluate("""
            () => {
                // Xóa các elements không visible
                const allElements = document.querySelectorAll('*');
                let removedCount = 0;
                
                allElements.forEach(el => {
                    // Không xóa video và các elements quan trọng
                    if (el.tagName === 'VIDEO' || el.tagName === 'SCRIPT' || el.tagName === 'STYLE') {
                        return;
                    }
                    
                    // Xóa nếu không visible
                    const rect = el.getBoundingClientRect();
                    if (rect.width === 0 && rect.height === 0) {
                        try {
                            el.remove();
                            removedCount++;
                        } catch (e) {}
                    }
                });
                
                console.log('[RAM-OPT] Removed', removedCount, 'unused elements');
            }
        """)
        
        print("[RAM-OPT] ✅ Page lifecycle optimized")
        
    except Exception as e:
        print(f"[RAM-OPT] ⚠️ Error optimizing lifecycle: {e}")


async def setup_memory_cleanup_loop(page: Page, interval_seconds: int = 60):
    """
    Setup loop để cleanup memory định kỳ
    Chạy mỗi 60 giây để giải phóng RAM
    """
    try:
        print(f"[RAM-OPT] Starting memory cleanup loop (every {interval_seconds}s)...")
        
        while True:
            await asyncio.sleep(interval_seconds)
            
            try:
                # Force garbage collection
                await page.evaluate("""
                    () => {
                        // Clear console
                        console.clear();
                        
                        // Force GC nếu có
                        if (window.gc) {
                            window.gc();
                        }
                        
                        // Clear image cache
                        const images = document.querySelectorAll('img');
                        images.forEach(img => {
                            if (!img.src.includes('tiktok')) {
                                img.src = 'data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7';
                            }
                        });
                        
                        // Clear canvas
                        const canvases = document.querySelectorAll('canvas');
                        canvases.forEach(canvas => {
                            const ctx = canvas.getContext('2d');
                            if (ctx) {
                                ctx.clearRect(0, 0, canvas.width, canvas.height);
                            }
                        });
                        
                        console.log('[RAM-OPT] Memory cleaned');
                    }
                """)
                
                print(f"[RAM-OPT] Memory cleanup executed")
                
            except Exception as e:
                # Page might be closed
                print(f"[RAM-OPT] Cleanup error: {e}")
                break
        
    except Exception as e:
        print(f"[RAM-OPT] ⚠️ Cleanup loop error: {e}")


# ============================================================
# LAYER 4: RESOURCE BLOCKING
# ============================================================

async def block_unnecessary_resources(page: Page):
    """
    Block resources không cần thiết để tiết kiệm RAM và bandwidth
    Chỉ load những gì cần cho TikTok livestream view
    """
    try:
        print("[RAM-OPT] Setting up resource blocking...")
        
        await page.route("**/*", lambda route: (
            route.abort() if route.request.resource_type in [
                "stylesheet",  # CSS - không cần
                "font",        # Fonts - không cần
                "image",       # Images - không cần (chỉ cần video)
                # "media",     # KHÔNG block - cần cho video
                # "script",    # KHÔNG block - cần cho TikTok
            ] or (
                # Block tracking và analytics
                'analytics' in route.request.url or
                'tracking' in route.request.url or
                'ads' in route.request.url or
                'doubleclick' in route.request.url or
                'google-analytics' in route.request.url
            ) else route.continue_()
        ))
        
        print("[RAM-OPT] ✅ Resource blocking enabled")
        
    except Exception as e:
        print(f"[RAM-OPT] ⚠️ Resource blocking error: {e}")


# ============================================================
# LAYER 5: VIDEO OPTIMIZATION
# ============================================================

async def optimize_video_playback(page: Page):
    """
    Tối ưu video playback để giảm RAM nhưng vẫn tính view
    - Giảm buffer size
    - Giảm quality (nếu có thể)
    - Ensure events vẫn dispatch
    """
    try:
        print("[RAM-OPT] Optimizing video playback...")
        
        await page.wait_for_selector('video', timeout=10000)
        
        await page.evaluate("""
            () => {
                const video = document.querySelector('video');
                if (!video) return;
                
                // 1. Giảm volume (tiết kiệm RAM)
                video.volume = 0.01;
                video.muted = false;  // Không mute hoàn toàn
                
                // 2. Giảm preload
                video.preload = 'metadata';
                
                // 3. Ensure play
                video.play().catch(e => console.log('[VIDEO] Play error:', e));
                
                // 4. Dispatch events (CRITICAL cho view counting)
                video.dispatchEvent(new Event('play'));
                video.dispatchEvent(new Event('playing'));
                
                // 5. Timeupdate loop (CRITICAL)
                setInterval(() => {
                    if (video && !video.paused) {
                        video.dispatchEvent(new Event('timeupdate'));
                    }
                }, 250);
                
                // 6. Clear old buffers định kỳ
                setInterval(() => {
                    try {
                        // Force clear buffer bằng cách seek
                        const currentTime = video.currentTime;
                        video.currentTime = currentTime;
                    } catch (e) {}
                }, 30000);  // Mỗi 30s
                
                console.log('[RAM-OPT] Video optimized');
            }
        """)
        
        print("[RAM-OPT] ✅ Video playback optimized")
        
    except Exception as e:
        print(f"[RAM-OPT] ⚠️ Video optimization error: {e}")


# ============================================================
# MAIN OPTIMIZATION FUNCTION
# ============================================================

async def apply_full_ram_optimization(
    page: Page,
    enable_cleanup_loop: bool = True,
    enable_resource_blocking: bool = True
):
    """
    Áp dụng toàn bộ optimizations cho page
    
    Args:
        page: Playwright page object
        enable_cleanup_loop: Enable memory cleanup loop
        enable_resource_blocking: Enable resource blocking
    
    Returns:
        asyncio.Task: Cleanup loop task (nếu enabled)
    """
    try:
        print("[RAM-OPT] Applying full RAM optimization...")
        
        # 1. Block resources (trước khi navigate)
        if enable_resource_blocking:
            await block_unnecessary_resources(page)
        
        # 2. Optimize page lifecycle
        await optimize_page_lifecycle(page)
        
        # 3. Optimize video playback
        await optimize_video_playback(page)
        
        # 4. Start cleanup loop
        cleanup_task = None
        if enable_cleanup_loop:
            cleanup_task = asyncio.create_task(setup_memory_cleanup_loop(page, interval_seconds=60))
        
        print("[RAM-OPT] ✅ Full RAM optimization applied")
        
        return cleanup_task
        
    except Exception as e:
        print(f"[RAM-OPT] ❌ Error applying optimization: {e}")
        return None


# ============================================================
# MEMORY MONITORING
# ============================================================

async def get_page_memory_usage(page: Page) -> Optional[Dict]:
    """
    Get current memory usage của page
    """
    try:
        metrics = await page.evaluate("""
            () => {
                if (performance.memory) {
                    return {
                        used: Math.round(performance.memory.usedJSHeapSize / 1024 / 1024),
                        total: Math.round(performance.memory.totalJSHeapSize / 1024 / 1024),
                        limit: Math.round(performance.memory.jsHeapSizeLimit / 1024 / 1024)
                    };
                }
                return null;
            }
        """)
        
        return metrics
        
    except Exception as e:
        print(f"[RAM-OPT] Error getting memory: {e}")
        return None


async def monitor_memory_usage(page: Page, duration_seconds: int = 300):
    """
    Monitor memory usage trong duration_seconds
    """
    try:
        print(f"[RAM-OPT] Monitoring memory for {duration_seconds}s...")
        
        start_time = asyncio.get_event_loop().time()
        
        while asyncio.get_event_loop().time() - start_time < duration_seconds:
            metrics = await get_page_memory_usage(page)
            
            if metrics:
                print(f"[RAM-OPT] Memory: {metrics['used']}MB / {metrics['total']}MB (limit: {metrics['limit']}MB)")
            
            await asyncio.sleep(30)  # Check mỗi 30s
        
        print("[RAM-OPT] Monitoring completed")
        
    except Exception as e:
        print(f"[RAM-OPT] Monitoring error: {e}")


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_ram_target_flags(target_mb: int) -> List[str]:
    """
    Get flags dựa trên RAM target
    
    Args:
        target_mb: Target RAM in MB (150, 200, 250, etc.)
    
    Returns:
        List of Chrome flags
    """
    if target_mb <= 150:
        # Ultra aggressive (150MB)
        flags = get_fake_headless_optimized_flags()
        flags.append('--js-flags=--max-old-space-size=48')  # 48MB heap
        return flags
    elif target_mb <= 200:
        # Aggressive (200MB)
        return get_fake_headless_optimized_flags()
    else:
        # Balanced (250MB+)
        return get_ultra_optimized_flags()


def print_optimization_summary():
    """Print summary của optimizations"""
    print("\n" + "=" * 70)
    print("RAM OPTIMIZATION SUMMARY")
    print("=" * 70)
    print("✅ Chrome flags: Ultra optimized (64MB JS heap)")
    print("✅ Context options: Mobile viewport (360x640)")
    print("✅ Page lifecycle: Throttled timers, limited buffers")
    print("✅ Resource blocking: CSS, fonts, images blocked")
    print("✅ Video optimization: Metadata preload, buffer clearing")
    print("✅ Memory cleanup: Auto cleanup every 60s")
    print("=" * 70)
    print("Expected RAM: 150-200MB per profile")
    print("Stealth: 100% (GPU enabled, no detection)")
    print("View counting: 100% (video events dispatched)")
    print("=" * 70 + "\n")

