#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ultra Low RAM Mode với Stealth
Target: 150-200MB RAM per profile
Đảm bảo không bị detect bot
"""

# Chrome flags cho ultra low RAM + stealth
ULTRA_LOW_RAM_STEALTH_FLAGS = [
    # ============================================================
    # STEALTH - Chống detect bot (QUAN TRỌNG)
    # ============================================================
    "--disable-blink-features=AutomationControlled",  # Ẩn automation
    "--disable-dev-shm-usage",  # Tránh shared memory issues
    
    # ============================================================
    # RAM OPTIMIZATION - Giảm memory usage
    # ============================================================
    # Renderer process
    "--renderer-process-limit=1",  # Chỉ 1 renderer process
    "--single-process",  # Single process mode (tiết kiệm nhất)
    
    # Memory management
    "--aggressive-cache-discard",  # Xóa cache aggressive
    "--disable-background-timer-throttling",
    "--disable-backgrounding-occluded-windows",
    "--disable-breakpad",  # Disable crash reporting
    "--disable-component-update",  # Disable component updates
    "--disable-domain-reliability",
    "--disable-features=TranslateUI,BlinkGenPropertyTrees",
    "--disable-ipc-flooding-protection",
    "--disable-renderer-backgrounding",
    
    # GPU & Graphics (disable để save RAM)
    "--disable-gpu",
    "--disable-gpu-compositing",
    "--disable-software-rasterizer",
    "--disable-accelerated-2d-canvas",
    "--disable-3d-apis",
    
    # Media (disable audio/video processing)
    "--disable-audio-output",  # No audio
    "--autoplay-policy=user-gesture-required",  # No autoplay
    "--mute-audio",
    
    # Extensions & Plugins
    "--disable-extensions-except=",  # Disable all extensions (hoặc chỉ load cần thiết)
    "--disable-plugins",
    "--disable-plugins-discovery",
    
    # Network
    "--disable-background-networking",
    "--disable-sync",
    "--disable-default-apps",
    
    # ============================================================
    # BASIC SETTINGS
    # ============================================================
    "--no-first-run",
    "--no-default-browser-check",
    "--password-store=basic",
    "--disable-popup-blocking",
    
    # ============================================================
    # WINDOW SETTINGS (cho view TikTok)
    # ============================================================
    "--window-size=800,600",  # Small window = less RAM
    "--window-position=0,0",
]


# BEST: Stealth + Low RAM (Recommended by user - tested & verified)
BEST_STEALTH_LOW_RAM = [
    # ============================================================
    # STEALTH - Chống detect bot (CRITICAL)
    # ============================================================
    "--disable-blink-features=AutomationControlled",
    "--disable-dev-shm-usage",
    
    # ============================================================
    # RAM OPTIMIZATION (không phá fingerprint)
    # ============================================================
    "--renderer-process-limit=2",  # 2 renderers (balance tốt)
    "--aggressive-cache-discard",
    "--disable-background-timer-throttling",
    "--disable-breakpad",
    "--disable-domain-reliability",
    "--disable-component-update",
    "--disable-backgrounding-occluded-windows",
    
    # ============================================================
    # GPU (tối ưu nhưng không bị detect)
    # ============================================================
    "--disable-gpu-compositing",  # Chỉ disable compositing, giữ GPU
    
    # ============================================================
    # MEDIA
    # ============================================================
    "--autoplay-policy=user-gesture-required",
    
    # ============================================================
    # NETWORK
    # ============================================================
    "--disable-background-networking",
    "--disable-sync",
    
    # ============================================================
    # BASIC
    # ============================================================
    "--no-first-run",
    "--no-default-browser-check",
    "--password-store=basic",
    "--disable-popup-blocking",
    
    # ============================================================
    # WINDOW
    # ============================================================
    "--window-size=800,600",
]

# OPTIMIZED: Thêm một số flags để giảm RAM hơn nữa (✅ PATCH 12: GPU ENABLED)
OPTIMIZED_STEALTH_LOW_RAM = [
    # ============================================================
    # STEALTH - Chống detect bot
    # ============================================================
    "--disable-blink-features=AutomationControlled",
    "--disable-dev-shm-usage",
    
    # ✅ PATCH 12: GPU - KEEP ENABLED
    # Removed: --disable-gpu-compositing, --disable-software-rasterizer
    # Removed: --disable-accelerated-2d-canvas
    
    # ============================================================
    # RAM OPTIMIZATION (aggressive hơn nhưng vẫn safe)
    # ============================================================
    "--renderer-process-limit=1",  # 1 renderer (tiết kiệm hơn)
    "--aggressive-cache-discard",
    "--disable-background-timer-throttling",
    "--disable-breakpad",
    "--disable-domain-reliability",
    "--disable-component-update",
    "--disable-backgrounding-occluded-windows",
    "--disable-renderer-backgrounding",
    "--disable-ipc-flooding-protection",
    
    # ============================================================
    # MEDIA (tối ưu hơn)
    # ============================================================
    "--autoplay-policy=user-gesture-required",
    "--mute-audio",
    
    # ============================================================
    # NETWORK
    # ============================================================
    "--disable-background-networking",
    "--disable-sync",
    "--disable-default-apps",
    
    # ============================================================
    # FEATURES (disable không cần thiết)
    # ============================================================
    "--disable-features=TranslateUI,BlinkGenPropertyTrees",
    
    # ============================================================
    # BASIC
    # ============================================================
    "--no-first-run",
    "--no-default-browser-check",
    "--password-store=basic",
    "--disable-popup-blocking",
    
    # ============================================================
    # WINDOW (nhỏ hơn = ít RAM hơn)
    # ============================================================
    "--window-size=640,480",
]

# EXTREME: Maximum RAM saving (✅ PATCH 11: GPU ENABLED)
EXTREME_LOW_RAM = [
    # STEALTH
    "--disable-blink-features=AutomationControlled",
    "--disable-dev-shm-usage",
    
    # ✅ PATCH 11: GPU - KEEP ENABLED (no disable flags)
    # Removed: --disable-gpu, --disable-gpu-compositing, --disable-software-rasterizer
    # Removed: --disable-accelerated-2d-canvas, --disable-3d-apis
    
    # EXTREME RAM OPTIMIZATION
    "--single-process",
    "--aggressive-cache-discard",
    "--disable-background-timer-throttling",
    "--disable-breakpad",
    "--disable-domain-reliability",
    "--disable-component-update",
    "--disable-backgrounding-occluded-windows",
    "--disable-renderer-backgrounding",
    "--disable-ipc-flooding-protection",
    
    # MEDIA
    "--autoplay-policy=user-gesture-required",
    "--disable-audio-output",
    "--mute-audio",
    
    # NETWORK
    "--disable-background-networking",
    "--disable-sync",
    "--disable-default-apps",
    
    # FEATURES
    "--disable-features=TranslateUI,BlinkGenPropertyTrees,AudioServiceOutOfProcess",
    "--disable-plugins",
    "--disable-plugins-discovery",
    
    # BASIC
    "--no-first-run",
    "--no-default-browser-check",
    "--password-store=basic",
    "--disable-popup-blocking",
    
    # WINDOW
    "--window-size=640,480",
]


# JavaScript injection để stealth
STEALTH_JS = """
// Ẩn automation indicators
Object.defineProperty(navigator, 'webdriver', {
    get: () => undefined
});

// Ẩn automation
delete navigator.__proto__.webdriver;

// Override permissions
const originalQuery = window.navigator.permissions.query;
window.navigator.permissions.query = (parameters) => (
    parameters.name === 'notifications' ?
        Promise.resolve({ state: Notification.permission }) :
        originalQuery(parameters)
);

// Chrome object
window.chrome = {
    runtime: {}
};

// Languages
Object.defineProperty(navigator, 'languages', {
    get: () => ['en-US', 'en']
});

// Plugins
Object.defineProperty(navigator, 'plugins', {
    get: () => [1, 2, 3, 4, 5]
});

// WebGL vendor
const getParameter = WebGLRenderingContext.prototype.getParameter;
WebGLRenderingContext.prototype.getParameter = function(parameter) {
    if (parameter === 37445) {
        return 'Intel Inc.';
    }
    if (parameter === 37446) {
        return 'Intel Iris OpenGL Engine';
    }
    return getParameter(parameter);
};

// Console log để verify
console.log('[STEALTH] Automation indicators hidden');
console.log('[STEALTH] navigator.webdriver:', navigator.webdriver);
"""


# Playwright context options cho ultra low RAM
def get_ultra_low_ram_context_options(user_agent: str = None):
    """Get context options for ultra low RAM mode"""
    return {
        'viewport': {'width': 800, 'height': 600},  # Small viewport
        'user_agent': user_agent or 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
        'locale': 'en-US',
        'timezone_id': 'America/New_York',
        'permissions': [],  # No permissions
        'geolocation': None,
        'color_scheme': 'light',
        'reduced_motion': 'reduce',  # Reduce animations
        'forced_colors': 'none',
        'java_script_enabled': True,  # MUST keep JS for TikTok
        'bypass_csp': True,  # Bypass CSP for stealth injection
        'ignore_https_errors': True,
        'has_touch': False,
        'is_mobile': False,
        'device_scale_factor': 1,
    }


# Strategy cho TikTok view
TIKTOK_VIEW_STRATEGY = {
    'scroll_behavior': 'smooth',  # Smooth scroll (human-like)
    'watch_duration': (3, 8),  # Watch 3-8 seconds (random)
    'interaction_delay': (0.5, 2.0),  # Delay between actions
    'scroll_distance': (200, 400),  # Scroll distance (pixels)
    'pause_probability': 0.3,  # 30% chance to pause
    'pause_duration': (1, 3),  # Pause 1-3 seconds
}


def get_tiktok_view_flags(mode: str = "best"):
    """
    Get Chrome flags for TikTok view
    
    Args:
        mode: 
            - "best" = BEST_STEALTH_LOW_RAM (200-250MB, recommended, tested)
            - "optimized" = OPTIMIZED_STEALTH_LOW_RAM (150-200MB, more aggressive)
            - "extreme" = EXTREME_LOW_RAM (100-150MB, maximum saving, có thể bị detect)
            - "ultra" = ULTRA_LOW_RAM_STEALTH_FLAGS (old, deprecated)
    
    Returns:
        List of Chrome flags
    """
    mode = mode.lower()
    
    if mode == "best":
        return BEST_STEALTH_LOW_RAM  # ✅ Recommended
    elif mode == "optimized":
        return OPTIMIZED_STEALTH_LOW_RAM  # ⚡ More aggressive
    elif mode == "extreme":
        return EXTREME_LOW_RAM  # ⚠️ Maximum saving
    elif mode == "ultra":
        return ULTRA_LOW_RAM_STEALTH_FLAGS  # Old
    else:
        return BEST_STEALTH_LOW_RAM  # Default


async def inject_stealth(page):
    """
    Inject stealth JavaScript to hide automation
    
    Args:
        page: Playwright page object
    """
    try:
        await page.add_init_script(STEALTH_JS)
        print("[STEALTH] ✅ Stealth scripts injected")
    except Exception as e:
        print(f"[STEALTH] ⚠️ Failed to inject stealth: {e}")


async def simulate_human_view(page, video_url: str, watch_duration: int = 5):
    """
    Simulate human viewing behavior
    
    Args:
        page: Playwright page object
        video_url: TikTok video URL
        watch_duration: How long to watch (seconds)
    """
    import random
    import asyncio
    
    try:
        # Navigate to video
        print(f"[VIEW] Navigating to video...")
        await page.goto(video_url, wait_until='domcontentloaded', timeout=15000)
        
        # Wait for video to load
        await asyncio.sleep(random.uniform(1, 2))
        
        # Random scroll (human-like)
        scroll_count = random.randint(1, 3)
        for i in range(scroll_count):
            scroll_distance = random.randint(200, 400)
            await page.evaluate(f"window.scrollBy(0, {scroll_distance})")
            await asyncio.sleep(random.uniform(0.5, 1.5))
        
        # Watch video
        print(f"[VIEW] Watching for {watch_duration}s...")
        await asyncio.sleep(watch_duration)
        
        # Random pause (30% chance)
        if random.random() < 0.3:
            pause_time = random.uniform(1, 3)
            print(f"[VIEW] Pausing for {pause_time:.1f}s...")
            await asyncio.sleep(pause_time)
        
        # Scroll back up sometimes
        if random.random() < 0.4:
            await page.evaluate("window.scrollBy(0, -200)")
            await asyncio.sleep(random.uniform(0.3, 0.8))
        
        print(f"[VIEW] ✅ View completed")
        return True
        
    except Exception as e:
        print(f"[VIEW] ❌ Error: {e}")
        return False


# Memory monitoring
async def get_memory_usage(page):
    """Get current memory usage of the page"""
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
        
        if metrics:
            print(f"[MEMORY] Used: {metrics['used']}MB / Total: {metrics['total']}MB / Limit: {metrics['limit']}MB")
            return metrics['used']
        
        return None
        
    except Exception as e:
        print(f"[MEMORY] Error getting metrics: {e}")
        return None


# Cleanup để giảm RAM
async def cleanup_memory(page):
    """Force cleanup memory"""
    try:
        # Clear cache
        await page.evaluate("""
            () => {
                // Clear console
                console.clear();
                
                // Force garbage collection (if available)
                if (window.gc) {
                    window.gc();
                }
                
                // Clear some DOM elements
                const videos = document.querySelectorAll('video');
                videos.forEach(v => {
                    v.pause();
                    v.src = '';
                    v.load();
                });
                
                // Clear images
                const images = document.querySelectorAll('img');
                images.forEach(img => {
                    if (img.src && !img.src.startsWith('data:')) {
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
            }
        """)
        
        print("[MEMORY] ✅ Memory cleanup executed")
        
    except Exception as e:
        print(f"[MEMORY] ⚠️ Cleanup error: {e}")


# Advanced: Block unnecessary resources
async def block_unnecessary_resources(page):
    """
    Block unnecessary resources để save bandwidth và RAM
    Chỉ load những gì cần thiết cho view
    """
    try:
        await page.route("**/*", lambda route: (
            route.abort() if route.request.resource_type in [
                "stylesheet",  # CSS (không cần cho view count)
                "font",        # Fonts
                "image",       # Images (có thể block nếu chỉ cần view count)
                # "media",     # KHÔNG block - cần cho video
                # "script",    # KHÔNG block - cần cho TikTok
            ] else route.continue_()
        ))
        
        print("[OPTIMIZE] ✅ Resource blocking enabled")
        
    except Exception as e:
        print(f"[OPTIMIZE] ⚠️ Resource blocking error: {e}")


# Advanced: Reduce viewport quality
async def reduce_viewport_quality(page):
    """
    Giảm quality của viewport để save RAM
    """
    try:
        await page.evaluate("""
            () => {
                // Reduce image quality
                document.querySelectorAll('img').forEach(img => {
                    img.loading = 'lazy';
                });
                
                // Reduce video quality
                document.querySelectorAll('video').forEach(video => {
                    video.preload = 'metadata';  // Chỉ load metadata
                });
                
                // Disable animations
                const style = document.createElement('style');
                style.textContent = `
                    * {
                        animation-duration: 0s !important;
                        transition-duration: 0s !important;
                    }
                `;
                document.head.appendChild(style);
            }
        """)
        
        print("[OPTIMIZE] ✅ Viewport quality reduced")
        
    except Exception as e:
        print(f"[OPTIMIZE] ⚠️ Quality reduction error: {e}")


# Get recommended flags based on RAM target
def get_flags_for_ram_target(target_mb: int):
    """
    Get recommended flags based on RAM target
    
    Args:
        target_mb: Target RAM in MB (e.g., 200)
    
    Returns:
        tuple: (flags, mode_name)
    """
    if target_mb <= 150:
        return EXTREME_LOW_RAM, "EXTREME (100-150MB) ⚠️"
    elif target_mb <= 200:
        return OPTIMIZED_STEALTH_LOW_RAM, "OPTIMIZED (150-200MB) ⚡"
    else:
        return BEST_STEALTH_LOW_RAM, "BEST (200-250MB) ✅"
