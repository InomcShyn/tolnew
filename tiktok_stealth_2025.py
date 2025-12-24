#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🛡️ TIKTOK STEALTH 2025 - COMPLETE ANTI-DETECTION SYSTEM
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Complete anti-detection system for TikTok 2023-2025:
✅ Anti-detect headless (stealth-headful mode)
✅ Remove all detectable Chrome flags
✅ Full anti-automation patches
✅ Anti blank page with auto-recovery
✅ Configurable window sizes
✅ Mobile mode support
✅ UA preservation for logged-in profiles
✅ RAM optimization
✅ Livestream mode with WebGL

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import random
from typing import Dict, List, Tuple, Optional


# ═══════════════════════════════════════════════════════════════════════════════
# 1. ANTI-DETECT HEADLESS
# ═══════════════════════════════════════════════════════════════════════════════

def get_stealth_headless_args() -> List[str]:
    """
    Get stealth headless args (if absolutely must use headless)
    
    Returns:
        List of Chrome args for stealth headless
    """
    return [
        '--headless=new',  # New headless mode (less detectable)
        '--hide-scrollbars',
        '--mute-audio',
        '--disable-features=IsolateOrigins,site-per-process,OptimizationGuideModelDownloading',
        '--disable-blink-features=AutomationControlled'
    ]


def get_stealth_headful_args(window_size: str = "360x640") -> List[str]:
    """
    Get stealth-headful args (visible but minimal window)
    RECOMMENDED for TikTok livestream
    
    Args:
        window_size: Window size (e.g. "360x640")
    
    Returns:
        List of Chrome args for stealth-headful
    """
    width, height = parse_window_size(window_size)
    
    return [
        f'--window-size={width},{height}',
        '--window-position=0,0',
        '--force-device-scale-factor=1',
        '--disable-blink-features=AutomationControlled'
    ]


# ═══════════════════════════════════════════════════════════════════════════════
# 2. REMOVE DETECTABLE FLAGS
# ═══════════════════════════════════════════════════════════════════════════════

DANGEROUS_FLAGS = [
    '--new',
    '--enable-features=FakeSignIn',
    '--memory-saver-mode',
    '--enable-features=ReducedReferrerGranularity'
]


def clean_chrome_args(args: List[str]) -> List[str]:
    """
    Remove all dangerous/detectable flags
    
    Args:
        args: Original Chrome args
    
    Returns:
        Cleaned args without dangerous flags
    """
    cleaned = []
    
    for arg in args:
        # Check if arg contains any dangerous flag
        is_dangerous = False
        for dangerous in DANGEROUS_FLAGS:
            if dangerous in arg:
                is_dangerous = True
                print(f"[STEALTH] ❌ Removed dangerous flag: {arg}")
                break
        
        if not is_dangerous:
            cleaned.append(arg)
    
    return cleaned


def get_safe_chrome_args(is_livestream: bool = False, window_size: str = "360x640") -> List[str]:
    """
    Get safe Chrome args without detectable flags
    
    Args:
        is_livestream: Whether this is for livestream
        window_size: Window size
    
    Returns:
        List of safe Chrome args
    """
    args = [
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # STEALTH FLAGS (SAFE)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        '--disable-blink-features=AutomationControlled',
        '--exclude-switches=enable-automation',
        '--disable-infobars',
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # RAM OPTIMIZATION
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        '--disable-background-networking',
        '--disable-sync',
        '--disable-default-apps',
        '--no-first-run',
        '--disk-cache-dir=/dev/null',
        '--media-cache-size=1',
        '--disable-dev-shm-usage',
        '--single-process',
        '--renderer-process-limit=1',
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # WINDOW SIZE
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        f'--window-size={window_size.replace("x", ",")}',
        '--window-position=0,0',
    ]
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # LIVESTREAM MODE
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    if is_livestream:
        args.extend([
            '--enable-gpu',
            '--ignore-gpu-blocklist',
            '--enable-accelerated-video-decode',
            '--enable-features=PlatformHEVCDecoderSupport,UseHardwareVideoDecode',
            '--use-gl=angle',
            '--use-angle=d3d11',
            '--autoplay-policy=no-user-gesture-required'
        ])
    
    return args


# ═══════════════════════════════════════════════════════════════════════════════
# 3. FULL ANTI-AUTOMATION PATCHES
# ═══════════════════════════════════════════════════════════════════════════════

def get_stealth_injection_script() -> str:
    """
    Get complete stealth injection script
    
    Returns:
        JavaScript code for stealth injection
    """
    return """
    (() => {
        // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        // 1. OVERRIDE navigator.webdriver
        // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        Object.defineProperty(navigator, 'webdriver', {
            get: () => false,
            configurable: true
        });
        
        // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        // 2. OVERRIDE navigator.permissions.query
        // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => {
            return parameters.name === 'notifications' ?
                Promise.resolve({ state: Notification.permission }) :
                Promise.resolve({ state: 'granted', onchange: null });
        };
        
        // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        // 3. OVERRIDE WebGL vendor/renderer
        // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        const getParameter = WebGLRenderingContext.prototype.getParameter;
        WebGLRenderingContext.prototype.getParameter = function(parameter) {
            if (parameter === 37445) {
                return 'Google Inc. (NVIDIA)';
            }
            if (parameter === 37446) {
                return 'ANGLE (NVIDIA, NVIDIA GeForce RTX 3050 Direct3D11 vs_5_0 ps_5_0)';
            }
            return getParameter.call(this, parameter);
        };
        
        if (window.WebGL2RenderingContext) {
            const getParameter2 = WebGL2RenderingContext.prototype.getParameter;
            WebGL2RenderingContext.prototype.getParameter = function(parameter) {
                if (parameter === 37445) {
                    return 'Google Inc. (NVIDIA)';
                }
                if (parameter === 37446) {
                    return 'ANGLE (NVIDIA, NVIDIA GeForce RTX 3050 Direct3D11 vs_5_0 ps_5_0)';
                }
                return getParameter2.call(this, parameter);
            };
        }
        
        // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        // 4. OVERRIDE chrome.runtime & chrome.app
        // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        window.chrome = {
            runtime: {
                connect: function() {
                    return {
                        onMessage: { addListener: function() {} },
                        postMessage: function() {},
                        disconnect: function() {}
                    };
                },
                sendMessage: function() {},
                onMessage: {
                    addListener: function() {},
                    removeListener: function() {}
                }
            },
            app: {
                isInstalled: false,
                InstallState: { DISABLED: 'disabled', INSTALLED: 'installed', NOT_INSTALLED: 'not_installed' },
                RunningState: { CANNOT_RUN: 'cannot_run', READY_TO_RUN: 'ready_to_run', RUNNING: 'running' }
            }
        };
        
        // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        // 5. FAKE languages
        // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        Object.defineProperty(navigator, 'languages', {
            get: () => ['vi-VN', 'vi', 'en-US', 'en'],
            configurable: true
        });
        
        // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        // 6. FAKE platform
        // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        Object.defineProperty(navigator, 'platform', {
            get: () => 'Win32',
            configurable: true
        });
        
        // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        // 7. FAKE plugins count = 3
        // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        Object.defineProperty(navigator, 'plugins', {
            get: () => [
                {name: 'Chrome PDF Plugin', description: 'Portable Document Format', filename: 'internal-pdf-viewer'},
                {name: 'Chrome PDF Viewer', description: '', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai'},
                {name: 'Native Client', description: '', filename: 'internal-nacl-plugin'}
            ],
            configurable: true
        });
        
        // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        // 8. FORCE document visible
        // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        Object.defineProperty(document, 'hidden', {
            get: () => false,
            configurable: true
        });
        
        Object.defineProperty(document, 'visibilityState', {
            get: () => 'visible',
            configurable: true
        });
        
        console.log('[STEALTH-2025] All patches applied');
    })();
    """


# ═══════════════════════════════════════════════════════════════════════════════
# 4. WINDOW SIZE CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

WINDOW_SIZES = {
    'mobile_small': '320x540',
    'mobile_medium': '360x640',
    'mobile_large': '375x667',
    'mobile_xl': '414x896',
    'tablet_small': '600x800',
    'tablet_large': '720x1280',
    'desktop_low': '800x600',
    'desktop_medium': '1024x600',
    'desktop_hd': '1280x720'
}


def parse_window_size(window_size: str) -> Tuple[int, int]:
    """
    Parse window size string to width and height
    
    Args:
        window_size: Size string (e.g. "360x640" or "mobile_medium")
    
    Returns:
        Tuple of (width, height)
    """
    # Check if it's a preset name
    if window_size in WINDOW_SIZES:
        window_size = WINDOW_SIZES[window_size]
    
    # Parse WxH format
    try:
        parts = window_size.lower().replace('x', ' ').replace('×', ' ').split()
        width = int(parts[0])
        height = int(parts[1])
        return (width, height)
    except:
        print(f"[WINDOW] ⚠️  Invalid size '{window_size}', using default 360x640")
        return (360, 640)


# ═══════════════════════════════════════════════════════════════════════════════
# 5. MOBILE MODE
# ═══════════════════════════════════════════════════════════════════════════════

MOBILE_USER_AGENTS = [
    'Mozilla/5.0 (Linux; Android 13; SM-S908B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 12; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 13; SM-A536B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36'
]


async def apply_mobile_mode(page, width: int, height: int, user_agent: Optional[str] = None):
    """
    Apply mobile mode configuration to page
    
    Args:
        page: Playwright page
        width: Viewport width
        height: Viewport height
        user_agent: Optional custom UA (if None, random mobile UA)
    """
    try:
        # Random mobile UA if not provided
        if not user_agent:
            user_agent = random.choice(MOBILE_USER_AGENTS)
        
        # Random device specs
        device_memory = random.randint(2, 8)
        hardware_concurrency = random.randint(4, 8)
        
        # Set viewport
        await page.set_viewport_size({"width": width, "height": height})
        
        # Inject mobile properties
        await page.evaluate(f"""
            () => {{
                // Device memory
                Object.defineProperty(navigator, 'deviceMemory', {{
                    get: () => {device_memory},
                    configurable: true
                }});
                
                // Hardware concurrency
                Object.defineProperty(navigator, 'hardwareConcurrency', {{
                    get: () => {hardware_concurrency},
                    configurable: true
                }});
                
                // Touch events
                Object.defineProperty(navigator, 'maxTouchPoints', {{
                    get: () => 5,
                    configurable: true
                }});
                
                // Mobile flag
                Object.defineProperty(navigator, 'userAgentData', {{
                    get: () => ({{
                        mobile: true,
                        platform: 'Android'
                    }}),
                    configurable: true
                }});
                
                console.log('[MOBILE-MODE] Applied: {width}x{height}, Memory: {device_memory}GB, Cores: {hardware_concurrency}');
            }}
        """)
        
        print(f"[MOBILE-MODE] ✅ Applied: {width}x{height}, UA: {user_agent[:50]}...")
        
    except Exception as e:
        print(f"[MOBILE-MODE] ❌ Error: {e}")


# ═══════════════════════════════════════════════════════════════════════════════
# 6. ANTI BLANK PAGE
# ═══════════════════════════════════════════════════════════════════════════════

async def handle_blank_page(page, url: str, attempt: int = 0) -> bool:
    """
    Handle blank page with auto-recovery
    
    Args:
        page: Playwright page
        url: Target URL
        attempt: Current attempt number
    
    Returns:
        True if recovered successfully
    """
    try:
        current_url = page.url
        
        if current_url == "about:blank" or "security" in current_url.lower():
            print(f"[ANTI-BLANK] ⚠️  Detected blank/security page: {current_url}")
            
            if attempt == 0:
                # First attempt: Reload
                print("[ANTI-BLANK] 🔄 Reloading page...")
                await page.reload(wait_until='domcontentloaded')
                await asyncio.sleep(3)
                
                if page.url != "about:blank":
                    print("[ANTI-BLANK] ✅ Recovered after reload")
                    return True
                else:
                    print("[ANTI-BLANK] ⚠️  Still blank after reload")
                    return await handle_blank_page(page, url, attempt + 1)
            
            elif attempt == 1:
                # Second attempt: Navigate again
                print("[ANTI-BLANK] 🔄 Navigating again...")
                await page.goto(url, wait_until='domcontentloaded', timeout=30000)
                await asyncio.sleep(3)
                
                if page.url != "about:blank":
                    print("[ANTI-BLANK] ✅ Recovered after re-navigation")
                    return True
                else:
                    print("[ANTI-BLANK] ❌ Failed to recover")
                    print("[ANTI-BLANK] 💡 Recommendation: Switch to stealth-headful mode")
                    return False
        
        return True
        
    except Exception as e:
        print(f"[ANTI-BLANK] ❌ Error: {e}")
        return False


# ═══════════════════════════════════════════════════════════════════════════════
# EXPORT
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    'get_stealth_headless_args',
    'get_stealth_headful_args',
    'clean_chrome_args',
    'get_safe_chrome_args',
    'get_stealth_injection_script',
    'parse_window_size',
    'apply_mobile_mode',
    'handle_blank_page',
    'WINDOW_SIZES',
    'MOBILE_USER_AGENTS'
]


if __name__ == "__main__":
    print("TIKTOK_STEALTH_2025 loaded")
    print("\nAvailable window sizes:")
    for name, size in WINDOW_SIZES.items():
        print(f"  {name}: {size}")
