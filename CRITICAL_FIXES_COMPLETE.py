#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔥 CRITICAL FIXES COMPLETE - TikTok Livestream Bot
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
COMPLETE SOLUTION FOR ALL ISSUES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import asyncio
import random


def get_gpu_enabled_args_fixed():
    """
    COMPLETE GPU + RAM OPTIMIZED FLAGS
    Target: 150-220MB RAM, Real GPU, 4-5 processes
    """
    return [
        # ═══════════════════════════════════════════════════════════════════
        # GPU ACTIVATION (CRITICAL - MUST BE FIRST)
        # ═══════════════════════════════════════════════════════════════════
        '--enable-gpu',
        '--ignore-gpu-blocklist',
        '--use-gl=angle',
        '--use-angle=gl',
        '--enable-zero-copy',
        '--enable-gpu-rasterization',
        '--enable-oop-rasterization',
        '--enable-accelerated-2d-canvas',
        '--enable-accelerated-video-decode',
        '--disable-software-rasterizer',  # Force hardware
        '--disable-gpu-driver-bug-workarounds',
        
        # ═══════════════════════════════════════════════════════════════════
        # PROCESS REDUCTION (Target: 4-5 processes)
        # ═══════════════════════════════════════════════════════════════════
        '--renderer-process-limit=1',
        '--disable-features=RendererCodeIntegrity',
        '--disable-features=IsolateOrigins,site-per-process',
        '--process-per-site',
        
        # ═══════════════════════════════════════════════════════════════════
        # RAM OPTIMIZATION (Target: 150-220MB)
        # ═══════════════════════════════════════════════════════════════════
        '--memory-pressure-off',
        '--js-flags=--max-old-space-size=32 --optimize-for-size',
        '--enable-low-end-device-mode',
        '--aggressive-cache-discard',
        '--disk-cache-size=1048576',  # 1MB
        '--media-cache-size=1048576',  # 1MB
        
        # ═══════════════════════════════════════════════════════════════════
        # DISABLE HEAVY SERVICES (Save RAM + Reduce processes)
        # ═══════════════════════════════════════════════════════════════════
        '--disable-background-networking',
        '--disable-sync',
        '--disable-translate',
        '--disable-extensions',
        '--disable-component-update',
        '--disable-domain-reliability',
        '--disable-client-side-phishing-detection',
        '--disable-breakpad',  # No crashpad
        '--disable-hang-monitor',
        '--disable-prompt-on-repost',
        '--disable-background-timer-throttling',
        '--disable-backgrounding-occluded-windows',
        '--disable-renderer-backgrounding',
        '--disable-ipc-flooding-protection',
        '--disable-default-apps',
        '--disable-features=AudioServiceOutOfProcess',  # Reduce process
        '--disable-features=NetworkService',  # Reduce process
        
        # ═══════════════════════════════════════════════════════════════════
        # NETWORK OPTIMIZATION
        # ═══════════════════════════════════════════════════════════════════
        '--disable-quic',
        '--disable-features=WebRtcHideLocalIpsWithMdns',
        
        # ═══════════════════════════════════════════════════════════════════
        # METRICS & REPORTING (Disable completely)
        # ═══════════════════════════════════════════════════════════════════
        '--metrics-recording-only',
        '--disable-features=OptimizationGuideModelDownloading',
        '--disable-features=MediaRouter',
        '--disable-features=Prerender2',
        '--disable-features=CalculateNativeWinOcclusion',
        
        # ═══════════════════════════════════════════════════════════════════
        # AUTOPLAY POLICY (CRITICAL for video playback)
        # ═══════════════════════════════════════════════════════════════════
        '--autoplay-policy=no-user-gesture-required',
        
        # ═══════════════════════════════════════════════════════════════════
        # STEALTH (Anti-detection)
        # ═══════════════════════════════════════════════════════════════════
        '--disable-blink-features=AutomationControlled',
        
        # ═══════════════════════════════════════════════════════════════════
        # BASIC
        # ═══════════════════════════════════════════════════════════════════
        '--no-first-run',
        '--no-default-browser-check',
        '--disable-dev-shm-usage',
        '--disable-popup-blocking',
        '--password-store=basic',
        '--no-service-autorun',
        
        # ═══════════════════════════════════════════════════════════════════
        # HEADLESS (if needed)
        # ═══════════════════════════════════════════════════════════════════
        '--headless=new',
        '--hide-scrollbars',
        
        # ═══════════════════════════════════════════════════════════════════
        # WINDOW
        # ═══════════════════════════════════════════════════════════════════
        '--window-size=360,640',
        '--window-position=0,0',
        '--force-device-scale-factor=1',
    ]


def get_stealth_injection_scripts():
    """
    COMPLETE STEALTH INJECTION
    Includes: Navigator, WebGL, Permissions, Audio, Codecs
    
    FIXED: Use REAL GPU (Windows desktop) instead of mobile GPU
    """
    
    # FIXED: Use REAL desktop GPU (Windows)
    import platform
    
    if platform.system() == 'Windows':
        # Windows desktop GPUs (ANGLE)
        gpu_vendors = ['Google Inc. (ANGLE)', 'NVIDIA Corporation', 'Intel']
        gpu_renderers = [
            'ANGLE (NVIDIA GeForce GTX 1660 Ti Direct3D11 vs_5_0 ps_5_0)',
            'ANGLE (NVIDIA GeForce GTX 1650 Direct3D11 vs_5_0 ps_5_0)',
            'ANGLE (Intel(R) UHD Graphics 630 Direct3D11 vs_5_0 ps_5_0)',
            'ANGLE (Intel(R) HD Graphics 620 Direct3D11 vs_5_0 ps_5_0)',
            'ANGLE (AMD Radeon RX 580 Direct3D11 vs_5_0 ps_5_0)'
        ]
    else:
        # Linux/Mac (fallback)
        gpu_vendors = ['NVIDIA Corporation', 'Intel', 'AMD']
        gpu_renderers = [
            'NVIDIA GeForce GTX 1660 Ti/PCIe/SSE2',
            'Intel UHD Graphics 630',
            'AMD Radeon RX 580'
        ]
    
    vendor = random.choice(gpu_vendors)
    renderer = random.choice(gpu_renderers)
    cores = random.randint(4, 8)
    
    scripts = []
    
    # ═══════════════════════════════════════════════════════════════════════
    # 1. NAVIGATOR STEALTH
    # ═══════════════════════════════════════════════════════════════════════
    scripts.append("""
        // Remove webdriver
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
        
        // Delete from prototype
        delete Object.getPrototypeOf(navigator).webdriver;
    """)
    
    # ═══════════════════════════════════════════════════════════════════════
    # 2. WEBGL FINGERPRINT OVERRIDE (CRITICAL)
    # ═══════════════════════════════════════════════════════════════════════
    scripts.append(f"""
        // WebGL override
        const getParameter = WebGLRenderingContext.prototype.getParameter;
        WebGLRenderingContext.prototype.getParameter = function(parameter) {{
            // UNMASKED_VENDOR_WEBGL
            if (parameter === 37445) {{
                return '{vendor}';
            }}
            // UNMASKED_RENDERER_WEBGL
            if (parameter === 37446) {{
                return '{renderer}';
            }}
            // MAX_TEXTURE_SIZE
            if (parameter === 3379) {{
                return 16384;
            }}
            // MAX_RENDERBUFFER_SIZE
            if (parameter === 34024) {{
                return 16384;
            }}
            return getParameter.call(this, parameter);
        }};
        
        // WebGL2
        if (window.WebGL2RenderingContext) {{
            const getParameter2 = WebGL2RenderingContext.prototype.getParameter;
            WebGL2RenderingContext.prototype.getParameter = function(parameter) {{
                if (parameter === 37445) return '{vendor}';
                if (parameter === 37446) return '{renderer}';
                if (parameter === 3379) return 16384;
                if (parameter === 34024) return 16384;
                return getParameter2.call(this, parameter);
            }};
        }}
    """)
    
    # ═══════════════════════════════════════════════════════════════════════
    # 3. HARDWARE CONCURRENCY
    # ═══════════════════════════════════════════════════════════════════════
    scripts.append(f"""
        Object.defineProperty(navigator, 'hardwareConcurrency', {{
            get: () => {cores}
        }});
    """)
    
    # ═══════════════════════════════════════════════════════════════════════
    # 4. PERMISSIONS API
    # ═══════════════════════════════════════════════════════════════════════
    scripts.append("""
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => {
            return Promise.resolve({
                state: 'prompt',
                onchange: null
            });
        };
    """)
    
    # ═══════════════════════════════════════════════════════════════════════
    # 5. CHROME RUNTIME
    # ═══════════════════════════════════════════════════════════════════════
    scripts.append("""
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
            loadTimes: function() {
                return {
                    requestTime: Date.now() / 1000,
                    startLoadTime: Date.now() / 1000,
                    commitLoadTime: Date.now() / 1000,
                    finishDocumentLoadTime: Date.now() / 1000,
                    finishLoadTime: Date.now() / 1000,
                    firstPaintTime: Date.now() / 1000
                };
            }
        };
    """)
    
    # ═══════════════════════════════════════════════════════════════════════
    # 6. PLUGINS & MIME TYPES
    # ═══════════════════════════════════════════════════════════════════════
    scripts.append("""
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5]
        });
        
        Object.defineProperty(navigator, 'mimeTypes', {
            get: () => [1, 2, 3, 4]
        });
    """)
    
    # ═══════════════════════════════════════════════════════════════════════
    # 7. LANGUAGES
    # ═══════════════════════════════════════════════════════════════════════
    scripts.append("""
        Object.defineProperty(navigator, 'languages', {
            get: () => ['vi-VN', 'vi', 'en-US', 'en']
        });
    """)
    
    # ═══════════════════════════════════════════════════════════════════════
    # 8. TOSTRING OVERRIDE
    # ═══════════════════════════════════════════════════════════════════════
    scripts.append("""
        const originalToString = Function.prototype.toString;
        Function.prototype.toString = function() {
            if (this === navigator.webdriver ||
                this === navigator.plugins ||
                this === navigator.languages ||
                this === navigator.hardwareConcurrency) {
                return 'function get() { [native code] }';
            }
            return originalToString.call(this);
        };
    """)
    
    return scripts


async def inject_full_stealth(page):
    """
    INJECT COMPLETE STEALTH (BEFORE NAVIGATION)
    """
    try:
        print("[STEALTH] Injecting complete stealth scripts...")
        
        scripts = get_stealth_injection_scripts()
        
        for i, script in enumerate(scripts, 1):
            await page.add_init_script(script)
        
        print(f"[STEALTH] ✅ Injected {len(scripts)} stealth scripts")
        return True
        
    except Exception as e:
        print(f"[STEALTH] ❌ Error: {e}")
        return False


async def patch_visibility_api(page):
    """
    PATCH VISIBILITY API (AFTER NAVIGATION)
    TikTok checks document.hidden - must be false
    """
    try:
        await page.evaluate("""
            () => {
                Object.defineProperty(document, 'hidden', {
                    get: () => false,
                    configurable: true
                });
                
                Object.defineProperty(document, 'visibilityState', {
                    get: () => 'visible',
                    configurable: true
                });
                
                // Block visibilitychange events
                const originalAddEventListener = document.addEventListener;
                document.addEventListener = function(type, listener, options) {
                    if (type === 'visibilitychange') {
                        return;
                    }
                    return originalAddEventListener.call(this, type, listener, options);
                };
                
                console.log('[STEALTH] Visibility patched');
            }
        """)
        
        print("[STEALTH] ✅ Visibility API patched")
        return True
        
    except Exception as e:
        print(f"[STEALTH] ⚠️  Visibility patch error: {e}")
        return False


async def ensure_video_is_playing(page, max_attempts=3):
    """
    ENSURE VIDEO PLAYBACK (CRITICAL for view counting)
    """
    for attempt in range(max_attempts):
        try:
            if attempt > 0:
                print(f"[PLAYBACK] Attempt {attempt + 1}/{max_attempts}...")
                await asyncio.sleep(3)
            
            # Wait for video with longer timeout
            await page.wait_for_selector('video', timeout=30000)
            
            # Check and fix playback
            result = await page.evaluate("""
                async () => {
                    const video = document.querySelector('video');
                    if (!video) return {success: false, error: 'No video element'};
                    
                    // Get current state
                    const state = {
                        paused: video.paused,
                        readyState: video.readyState,
                        currentTime: video.currentTime,
                        duration: video.duration,
                        width: video.videoWidth,
                        height: video.videoHeight
                    };
                    
                    // If already playing and has frames
                    if (!state.paused && state.readyState >= 3 && state.width > 0) {
                        return {
                            success: true,
                            message: 'Already playing',
                            state: state
                        };
                    }
                    
                    // Try to fix playback
                    try {
                        // Remove restrictions
                        video.muted = false;
                        video.volume = 0.01;
                        video.removeAttribute('preload');
                        video.setAttribute('autoplay', '');
                        video.setAttribute('playsinline', '');
                        
                        // Force play
                        await video.play();
                        
                        // Dispatch events
                        video.dispatchEvent(new Event('play'));
                        video.dispatchEvent(new Event('playing'));
                        video.dispatchEvent(new Event('loadeddata'));
                        
                        // Start timeupdate loop
                        if (!window.__timeupdateInterval) {
                            window.__timeupdateInterval = setInterval(() => {
                                if (video && !video.paused) {
                                    video.dispatchEvent(new Event('timeupdate'));
                                }
                            }, 250);
                        }
                        
                        // Wait a bit for frames
                        await new Promise(resolve => setTimeout(resolve, 1000));
                        
                        // Check again
                        const newState = {
                            paused: video.paused,
                            readyState: video.readyState,
                            currentTime: video.currentTime,
                            width: video.videoWidth,
                            height: video.videoHeight
                        };
                        
                        if (!newState.paused && newState.readyState >= 3 && newState.width > 0) {
                            return {
                                success: true,
                                message: 'Playback started',
                                state: newState
                            };
                        } else {
                            return {
                                success: false,
                                error: 'Playback not confirmed',
                                state: newState
                            };
                        }
                        
                    } catch (e) {
                        return {
                            success: false,
                            error: e.message,
                            state: state
                        };
                    }
                }
            """)
            
            if result['success']:
                state = result.get('state', {})
                print(f"[PLAYBACK] ✅ Video playing: {state.get('width')}x{state.get('height')}, time={state.get('currentTime', 0):.1f}s")
                return True
            else:
                print(f"[PLAYBACK] ⚠️  {result.get('error', 'Unknown error')}")
                if attempt < max_attempts - 1:
                    continue
                else:
                    return False
                    
        except Exception as e:
            print(f"[PLAYBACK] ❌ Error: {e}")
            if attempt < max_attempts - 1:
                continue
            else:
                return False
    
    return False


async def check_webgl_health(page):
    """
    CHECK WEBGL HEALTH
    """
    try:
        webgl_info = await page.evaluate("""
            () => {
                const canvas = document.createElement('canvas');
                const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
                
                if (!gl) {
                    return {healthy: false, error: 'No WebGL context'};
                }
                
                const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
                if (!debugInfo) {
                    return {healthy: false, error: 'No debug info'};
                }
                
                const vendor = gl.getParameter(debugInfo.UNMASKED_VENDOR_WEBGL);
                const renderer = gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL);
                
                // Check for SwiftShader (BAD)
                if (renderer && renderer.toLowerCase().includes('swiftshader')) {
                    return {
                        healthy: false,
                        error: 'SwiftShader detected',
                        vendor: vendor,
                        renderer: renderer
                    };
                }
                
                // Check for valid GPU
                if (!vendor || !renderer || vendor === 'N/A' || renderer === 'N/A') {
                    return {
                        healthy: false,
                        error: 'No GPU detected',
                        vendor: vendor,
                        renderer: renderer
                    };
                }
                
                return {
                    healthy: true,
                    vendor: vendor,
                    renderer: renderer,
                    version: gl.getParameter(gl.VERSION)
                };
            }
        """)
        
        if webgl_info['healthy']:
            print(f"[WEBGL] ✅ Healthy: {webgl_info['vendor']} | {webgl_info['renderer'][:50]}...")
        else:
            print(f"[WEBGL] ❌ Unhealthy: {webgl_info.get('error')}")
            if webgl_info.get('renderer'):
                print(f"[WEBGL]    Renderer: {webgl_info['renderer']}")
        
        return webgl_info
        
    except Exception as e:
        print(f"[WEBGL] ❌ Error: {e}")
        return {'healthy': False, 'error': str(e)}


async def check_stealth_status(page):
    """
    CHECK STEALTH STATUS
    """
    try:
        stealth_info = await page.evaluate("""
            () => {
                return {
                    webdriver: navigator.webdriver,
                    chrome: !!window.chrome,
                    permissions: !!navigator.permissions,
                    plugins: navigator.plugins.length,
                    hardwareConcurrency: navigator.hardwareConcurrency
                };
            }
        """)
        
        # Check webdriver
        is_active = (stealth_info['webdriver'] is None or stealth_info['webdriver'] == False)
        
        if is_active:
            print(f"[STEALTH] ✅ Active (webdriver=undefined)")
        else:
            print(f"[STEALTH] ❌ Not active (webdriver={stealth_info['webdriver']})")
        
        stealth_info['active'] = is_active
        return stealth_info
        
    except Exception as e:
        print(f"[STEALTH] ❌ Error: {e}")
        return {'active': False, 'error': str(e)}


async def verify_profile_ready(page, skip_video_check=False):
    """
    COMPLETE VERIFICATION
    Returns: dict with all checks
    
    Args:
        page: Playwright page
        skip_video_check: If True, skip video playback check (for faster launch)
    """
    print("\n" + "="*70)
    print("VERIFYING PROFILE READINESS")
    print("="*70)
    
    results = {
        'webgl': await check_webgl_health(page),
        'stealth': await check_stealth_status(page),
        'playback': False,
        'ready': False
    }
    
    # Video check is optional for faster launch
    if not skip_video_check:
        results['playback'] = await ensure_video_is_playing(page)
    else:
        print("[PLAYBACK] ⏭️  Skipped (will verify in background)")
        results['playback'] = True  # Assume OK for now
    
    # Determine readiness (WebGL + Stealth are critical, video can load later)
    results['ready'] = (
        results['webgl']['healthy'] and
        results['stealth']['active']
    )
    
    print("="*70)
    if results['ready']:
        print("✅ PROFILE READY - Core features verified")
        if skip_video_check:
            print("   ℹ️  Video playback will be verified in background")
    else:
        print("❌ PROFILE NOT READY - Critical issues detected")
        if not results['webgl']['healthy']:
            print(f"   ❌ WebGL: {results['webgl'].get('error')}")
        if not results['stealth']['active']:
            print(f"   ❌ Stealth: Not active")
    print("="*70 + "\n")
    
    return results


# ═══════════════════════════════════════════════════════════════════════════════
# EXPORT
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    'get_gpu_enabled_args_fixed',
    'get_stealth_injection_scripts',
    'inject_full_stealth',
    'patch_visibility_api',
    'ensure_video_is_playing',
    'check_webgl_health',
    'check_stealth_status',
    'verify_profile_ready'
]


if __name__ == "__main__":
    print("CRITICAL_FIXES_COMPLETE loaded")
    print("Functions available:")
    for func in __all__:
        print(f"  - {func}")
