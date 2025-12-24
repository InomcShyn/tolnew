#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🛡️ PLAYWRIGHT STEALTH 2025 - COMPLETE ANTI-DETECTION FOR TIKTOK
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Anti-detect Headless → Stealth-Headful (1x1 px window)
✅ Remove ALL dangerous Chrome flags (--new, --enable-features=FakeSignIn, etc.)
✅ Full anti-automation patches (navigator.webdriver, WebGL, permissions, etc.)
✅ Anti blank page with auto-recovery
✅ Configurable window sizes (320x540 → 1280x720)
✅ Mobile mode with random device specs
✅ UA preservation for logged-in profiles
✅ RAM optimization (150-200MB per profile)
✅ Livestream mode with WebGL + WebCodecs

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import asyncio
import random
from typing import Dict, List, Tuple, Optional
from pathlib import Path


# ═══════════════════════════════════════════════════════════════════════════════
# 1. ANTI-DETECT HEADLESS
# ═══════════════════════════════════════════════════════════════════════════════

def should_use_headless(url: Optional[str] = None, force_headless: bool = False) -> bool:
    """
    Determine if headless mode should be used
    
    TikTok livestream CANNOT work in headless mode!
    
    Args:
        url: Target URL
        force_headless: Force headless mode (not recommended for TikTok)
    
    Returns:
        True if headless should be used
    """
    # Never use headless for livestream
    if url and '/live' in url:
        print("[STEALTH] 🎥 Livestream detected → MUST use visible mode")
        return False
    
    # Respect force_headless for non-livestream
    if force_headless:
        print("[STEALTH] ⚠️  Forced headless mode (may be detected by TikTok)")
        return True
    
    # Default: Use stealth-headful (visible but minimal)
    print("[STEALTH] ✅ Using stealth-headful mode (recommended)")
    return False


def get_stealth_headless_args() -> List[str]:
    """
    Get stealth headless args (if absolutely must use headless)
    
    WARNING: TikTok can detect headless mode!
    
    Returns:
        List of Chrome args for stealth headless
    """
    return [
        '--headless=new',
        '--hide-scrollbars',
        '--mute-audio',
        '--disable-features=IsolateOrigins,site-per-process,OptimizationGuideModelDownloading',
        '--disable-blink-features=AutomationControlled'
    ]


def get_stealth_headful_args(window_size: str = "360x640") -> List[str]:
    """
    Get stealth-headful args (visible but minimal window)
    RECOMMENDED for TikTok
    
    Args:
        window_size: Window size (e.g. "360x640" or "1x1")
    
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
    '--enable-features=ReducedReferrerGranularity',
    '--enable-automation',
    '--enable-blink-features=AutomationControlled',
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


def get_safe_chrome_args(
    is_livestream: bool = False,
    window_size: str = "360x640",
    ultra_low_ram: bool = True
) -> List[str]:
    """
    Get safe Chrome args for TikTok LIVE 2025 - STRICT COMPLIANCE
    
    STRICT CONSTRAINTS (2025):
    - ❌ NO headless
    - ❌ NO window-size < 320x540
    - ❌ NO single-process
    - ❌ NO renderer-process-limit (NEW CONSTRAINT)
    - ❌ NO audio/GPU disable
    - ✅ Multi-process model (natural Chrome behavior)
    - ✅ Valid viewport (user-like)
    - ✅ Foreground, visible
    
    Args:
        is_livestream: Whether this is for livestream
        window_size: Window size (must be >= 320x540)
        ultra_low_ram: Enable RAM optimization (within constraints)
    
    Returns:
        List of compliant Chrome args
    """
    width, height = parse_window_size(window_size)
    
    # ✅ VALIDATE VIEWPORT (STRICT REQUIREMENT)
    if width < 320 or height < 540:
        print(f"[WARNING] Viewport {width}x{height} < 320x540 minimum")
        print(f"[WARNING] Using 360x640 for TikTok compliance")
        width, height = 360, 640
    
    args = [
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # STEALTH FLAGS (SAFE)
        # Purpose: Hide automation signals
        # RAM Impact: 0MB
        # TikTok Trust: ✅ Essential
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        '--disable-blink-features=AutomationControlled',
        '--exclude-switches=enable-automation',
        '--disable-infobars',
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # WINDOW SIZE (COMPLIANT - MUST BE >= 320x540)
        # Purpose: Valid viewport for TikTok view counting
        # RAM Impact: +20MB vs 1x1 (acceptable trade-off)
        # TikTok Trust: ✅ Required
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        f'--window-size={width},{height}',
        '--window-position=0,0',
    ]
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # LIVESTREAM MODE (GPU + AUDIO)
    # Purpose: Hardware decode + audio pipeline
    # RAM Impact: +35MB
    # TikTok Trust: ✅ Required for view counting
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    if is_livestream:
        args.extend([
            '--enable-gpu',
            '--ignore-gpu-blocklist',
            '--enable-accelerated-video-decode',
            '--enable-features=PlatformHEVCDecoderSupport,UseHardwareVideoDecode',
            '--use-gl=angle',
            '--use-angle=d3d11',
        ])
        print(f"[STEALTH] ✅ Livestream mode: GPU + Audio enabled")
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # RAM OPTIMIZATION (STRICT COMPLIANCE)
    # Purpose: Reduce RAM without breaking media or trust
    # RAM Impact: -75MB
    # TikTok Trust: ✅ Safe
    # 
    # ✅ REMOVED: --renderer-process-limit=1 (NEW CONSTRAINT - FORBIDDEN)
    # ✅ REMOVED: --single-process (breaks AudioContext)
    # ✅ ADJUSTED: JS heap 96MB → 112MB (more headroom)
    # ✅ ADDED: Additional feature disables for RAM
    # 
    # RESULT: Multi-process model (natural Chrome behavior)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    if ultra_low_ram:
        args.extend([
            # Network optimization (~30MB saved)
            '--disable-background-networking',  # ~15MB
            '--disable-sync',                   # ~10MB
            '--disable-default-apps',           # ~5MB
            
            # Feature optimization (~20MB saved)
            '--disable-features=Translate,OptimizationGuideModelDownloading,MediaRouter',  # ~15MB
            '--disable-component-update',       # ~3MB
            '--disable-domain-reliability',     # ~2MB
            
            # Startup optimization
            '--no-first-run',
            
            # Cache optimization (~30MB saved)
            '--disk-cache-size=1',              # ~20MB
            '--media-cache-size=1',             # ~10MB
            
            # Stability
            '--disable-dev-shm-usage',
            
            # Raster optimization (~10MB saved)
            '--num-raster-threads=2',           # vs default 4
            
            # JS heap (INCREASED for stability - was 96MB)
            '--js-flags=--max-old-space-size=112',  # 112MB heap
        ])
        print(f"[RAM] ✅ STRICT COMPLIANCE mode")
        print(f"[RAM]    Target: ~250MB (multi-process model)")
        print(f"[RAM]    Viewport: {width}x{height} (>= 320x540)")
        print(f"[RAM]    JS Heap: 112MB")
        print(f"[RAM]    Process: Multi-process (NO renderer limit)")
    
    return args


# ═══════════════════════════════════════════════════════════════════════════════
# 3. FULL ANTI-AUTOMATION PATCHES
# ═══════════════════════════════════════════════════════════════════════════════

def get_stealth_injection_script() -> str:
    """
    Get complete stealth injection script
    
    Patches:
    - navigator.webdriver = false
    - navigator.permissions.query → granted
    - WebGL vendor/renderer spoofing
    - chrome.runtime & chrome.app
    - languages, platform, plugins
    
    Returns:
        JavaScript code for stealth injection
    """
    return """
    (() => {
        console.log('[STEALTH-2025] Injecting anti-detection patches...');
        
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
            // Camera and microphone always granted
            if (parameters.name === 'camera' || parameters.name === 'microphone') {
                return Promise.resolve({ state: 'granted', onchange: null });
            }
            // Notifications use real permission
            if (parameters.name === 'notifications') {
                return Promise.resolve({ state: Notification.permission, onchange: null });
            }
            // Everything else granted
            return Promise.resolve({ state: 'granted', onchange: null });
        };
        
        // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        // 3. OVERRIDE WebGL vendor/renderer
        // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        const getParameter = WebGLRenderingContext.prototype.getParameter;
        WebGLRenderingContext.prototype.getParameter = function(parameter) {
            // 37445 = UNMASKED_VENDOR_WEBGL
            if (parameter === 37445) {
                return 'Google Inc. (NVIDIA)';
            }
            // 37446 = UNMASKED_RENDERER_WEBGL
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
        if (!window.chrome) {
            window.chrome = {};
        }
        
        window.chrome.runtime = {
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
        };
        
        window.chrome.app = {
            isInstalled: false,
            InstallState: { DISABLED: 'disabled', INSTALLED: 'installed', NOT_INSTALLED: 'not_installed' },
            RunningState: { CANNOT_RUN: 'cannot_run', READY_TO_RUN: 'ready_to_run', RUNNING: 'running' }
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
        
        console.log('[STEALTH-2025] ✅ All patches applied');
    })();
    """


async def inject_stealth_script(page):
    """
    Inject stealth script into page
    
    Args:
        page: Playwright page
    """
    try:
        script = get_stealth_injection_script()
        await page.add_init_script(script)
        print("[STEALTH] ✅ Stealth script injected")
    except Exception as e:
        print(f"[STEALTH] ❌ Failed to inject: {e}")


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
    'desktop_hd': '1280x720',
    'minimal': '1x1',  # For livestream (minimal RAM)
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


async def apply_mobile_mode(
    page,
    width: int,
    height: int,
    user_agent: Optional[str] = None
):
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
    
    Strategy:
    1. First attempt: Reload page
    2. Second attempt: Navigate again
    3. If still blank: Recommend switching to stealth-headful
    
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
                    print("[ANTI-BLANK] 💡 Set headless=False and window_size='1x1'")
                    return False
        
        return True
        
    except Exception as e:
        print(f"[ANTI-BLANK] ❌ Error: {e}")
        return False


# ═══════════════════════════════════════════════════════════════════════════════
# 7. UA PRESERVATION
# ═══════════════════════════════════════════════════════════════════════════════

def should_preserve_ua(profile_path: Path) -> Tuple[bool, Optional[str]]:
    """
    Check if profile has logged-in UA that should be preserved
    
    Args:
        profile_path: Path to profile folder
    
    Returns:
        Tuple (should_preserve, ua_string)
    """
    try:
        import json
        
        settings_path = profile_path / 'profile_settings.json'
        if not settings_path.exists():
            return (False, None)
        
        with open(settings_path, 'r', encoding='utf-8') as f:
            settings = json.load(f)
        
        # Check if profile has custom UA
        ua = settings.get('software', {}).get('user_agent') or settings.get('user_agent')
        
        if ua:
            print(f"[UA] ✅ Preserving logged-in UA: {ua[:50]}...")
            return (True, ua)
        
        return (False, None)
        
    except Exception as e:
        print(f"[UA] ⚠️  Error checking UA: {e}")
        return (False, None)


# ═══════════════════════════════════════════════════════════════════════════════
# EXPORT
# ═══════════════════════════════════════════════════════════════════════════════

def validate_chrome_args_strict(args: List[str]) -> Tuple[bool, List[str]]:
    """
    Validate Chrome args against STRICT TikTok 2025 constraints
    
    Args:
        args: List of Chrome arguments
    
    Returns:
        (is_valid, violations)
    """
    violations = []
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # CHECK FORBIDDEN FLAGS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    forbidden = [
        '--headless',
        '--single-process',
        '--renderer-process-limit',  # NEW: Completely forbidden
        '--disable-audio',
        '--disable-webaudio',
        '--mute-audio',
        '--disable-gpu',
        '--autoplay-policy',  # Let browser decide
    ]
    
    for arg in args:
        for forbidden_flag in forbidden:
            if arg.startswith(forbidden_flag):
                violations.append(f"❌ FORBIDDEN: {arg}")
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # CHECK WINDOW SIZE (MUST BE >= 320x540)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    window_size_found = False
    for arg in args:
        if arg.startswith('--window-size='):
            window_size_found = True
            size_str = arg.split('=')[1]
            try:
                w, h = map(int, size_str.split(','))
                if w < 320 or h < 540:
                    violations.append(f"❌ VIEWPORT TOO SMALL: {w}x{h} < 320x540 (REQUIRED)")
            except:
                violations.append(f"❌ INVALID WINDOW SIZE: {arg}")
    
    if not window_size_found:
        violations.append(f"⚠️  NO WINDOW SIZE: Should specify >= 320x540")
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # CHECK JS HEAP (SHOULD BE >= 96MB)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    for arg in args:
        if '--max-old-space-size=' in arg:
            try:
                heap_size = int(arg.split('=')[-1])
                if heap_size < 96:
                    violations.append(f"⚠️  JS HEAP TOO SMALL: {heap_size}MB < 96MB (may cause OOM)")
                elif heap_size < 112:
                    violations.append(f"ℹ️  JS HEAP: {heap_size}MB (recommended: 112MB+)")
            except:
                pass
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # CHECK GPU (SHOULD BE ENABLED FOR LIVESTREAM)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    has_enable_gpu = any('--enable-gpu' in arg for arg in args)
    if not has_enable_gpu:
        violations.append(f"⚠️  NO GPU: Should enable GPU for video decode")
    
    is_valid = len([v for v in violations if v.startswith('❌')]) == 0
    return is_valid, violations


__all__ = [
    'should_use_headless',
    'get_stealth_headless_args',
    'get_stealth_headful_args',
    'clean_chrome_args',
    'get_safe_chrome_args',
    'validate_chrome_args_strict',  # NEW
    'get_stealth_injection_script',
    'inject_stealth_script',
    'parse_window_size',
    'apply_mobile_mode',
    'handle_blank_page',
    'should_preserve_ua',
    'WINDOW_SIZES',
    'MOBILE_USER_AGENTS',
]


if __name__ == "__main__":
    print("PLAYWRIGHT_STEALTH_2025 loaded")
    print("\nAvailable window sizes:")
    for name, size in WINDOW_SIZES.items():
        print(f"  {name}: {size}")
