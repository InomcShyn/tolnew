#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fake Headless Module - Anti-Detection for TikTok Livestream
Bypass all headless detection methods
"""

import random
import asyncio

# ✅ Import new livestream playback detection
from LIVESTREAM_PLAYBACK_FIX_COMPLETE import (
    wait_for_livestream_player,
    wait_for_video_element,
    ensure_video_playing
)


# WebGL Vendors and Renderers (Mobile GPU)
WEBGL_VENDORS = ["Qualcomm", "ARM", "Imagination Technologies"]
WEBGL_RENDERERS = [
    "Adreno (TM) 640",
    "Adreno (TM) 650",
    "Mali-G78",
    "Mali-G77",
    "PowerVR Rogue GE8320"
]

# Plugin names (mobile Chrome)
PLUGIN_NAMES = [
    "Chrome PDF Plugin",
    "Chrome PDF Viewer",
    "Native Client"
]

# MIME types (mobile Chrome)
MIME_TYPES = [
    "application/pdf",
    "application/x-google-chrome-pdf",
    "application/x-nacl",
    "application/x-pnacl"
]


def get_stealth_scripts():
    """
    Get all stealth scripts to inject
    Returns list of JavaScript code strings
    """
    
    # Random values
    plugin_count = random.randint(3, 5)
    mime_count = random.randint(5, 10)
    hardware_concurrency = random.randint(4, 8)
    vendor = random.choice(WEBGL_VENDORS)
    renderer = random.choice(WEBGL_RENDERERS)
    
    scripts = []
    
    # 1. Override navigator.webdriver
    scripts.append("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => false
        });
    """)
    
    # 2. Override navigator.plugins
    scripts.append(f"""
        Object.defineProperty(navigator, 'plugins', {{
            get: () => {{
                const plugins = [];
                const pluginNames = {PLUGIN_NAMES[:plugin_count]};
                
                for (let i = 0; i < pluginNames.length; i++) {{
                    plugins.push({{
                        name: pluginNames[i],
                        description: pluginNames[i],
                        filename: pluginNames[i].toLowerCase().replace(/ /g, '_') + '.so',
                        length: 1
                    }});
                }}
                
                return plugins;
            }}
        }});
    """)
    
    # 3. Override navigator.mimeTypes
    scripts.append(f"""
        Object.defineProperty(navigator, 'mimeTypes', {{
            get: () => {{
                const mimeTypes = [];
                const types = {MIME_TYPES[:mime_count]};
                
                for (let i = 0; i < types.length; i++) {{
                    mimeTypes.push({{
                        type: types[i],
                        description: types[i],
                        suffixes: 'pdf',
                        enabledPlugin: {{
                            name: 'Chrome PDF Plugin'
                        }}
                    }});
                }}
                
                return mimeTypes;
            }}
        }});
    """)
    
    # 4. Override navigator.languages
    scripts.append("""
        Object.defineProperty(navigator, 'languages', {
            get: () => ['vi-VN', 'vi', 'en-US', 'en']
        });
    """)
    
    # 5. Override navigator.hardwareConcurrency
    scripts.append(f"""
        Object.defineProperty(navigator, 'hardwareConcurrency', {{
            get: () => {hardware_concurrency}
        }});
    """)
    
    # 6. WebGL spoof (CRITICAL for TikTok)
    scripts.append(f"""
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
            return getParameter.call(this, parameter);
        }};
        
        // WebGL2
        if (window.WebGL2RenderingContext) {{
            const getParameter2 = WebGL2RenderingContext.prototype.getParameter;
            WebGL2RenderingContext.prototype.getParameter = function(parameter) {{
                if (parameter === 37445) {{
                    return '{vendor}';
                }}
                if (parameter === 37446) {{
                    return '{renderer}';
                }}
                return getParameter2.call(this, parameter);
            }};
        }}
    """)
    
    # 7. Permissions spoof (CRITICAL) - ✅ PATCH 13: Improve permissions spoof
    scripts.append("""
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => {
            const permissionStates = {
                'notifications': 'prompt',
                'geolocation': 'prompt',
                'camera': 'prompt',
                'microphone': 'prompt',
                'midi': 'prompt',
                'clipboard-read': 'prompt',
                'clipboard-write': 'prompt',
                'payment-handler': 'prompt',
                'persistent-storage': 'prompt',
                'push': 'prompt',
                'speaker': 'prompt'
            };
            
            const permissionName = parameters.name || parameters;
            const state = permissionStates[permissionName] || 'prompt';
            
            return Promise.resolve({
                state: state,
                onchange: null
            });
        };
    """)
    
    # 8. Chrome runtime spoof - ✅ PATCH 14: Improve chrome.runtime spoof
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
                sendMessage: function(extensionId, message, options, callback) {
                    if (callback) setTimeout(() => callback({}), 0);
                },
                onMessage: {
                    addListener: function() {},
                    removeListener: function() {},
                    hasListener: function() { return false; }
                }
            },
            loadTimes: function() {
                return {
                    requestTime: Date.now() / 1000 - 1,
                    startLoadTime: Date.now() / 1000 - 0.5,
                    commitLoadTime: Date.now() / 1000 - 0.3,
                    finishDocumentLoadTime: Date.now() / 1000 - 0.1,
                    finishLoadTime: Date.now() / 1000,
                    firstPaintTime: Date.now() / 1000 - 0.2,
                    navigationType: 'Other',
                    wasFetchedViaSpdy: false,
                    wasNpnNegotiated: true,
                    npnNegotiatedProtocol: 'h2'
                };
            },
            csi: function() {
                return {
                    startE: Date.now(),
                    onloadT: Date.now(),
                    pageT: Date.now() - 1000
                };
            },
            app: {
                isInstalled: false
            }
        };
    """)
    
    # 9. Override toString to hide modifications
    scripts.append("""
        const originalToString = Function.prototype.toString;
        Function.prototype.toString = function() {
            if (this === navigator.webdriver ||
                this === navigator.plugins ||
                this === navigator.mimeTypes ||
                this === navigator.languages ||
                this === navigator.hardwareConcurrency) {
                return 'function get() { [native code] }';
            }
            return originalToString.call(this);
        };
    """)
    
    return scripts


async def inject_fake_headless(page):
    """
    Inject all anti-detection scripts into page
    MUST be called before page.goto()
    
    Args:
        page: Playwright page object
    """
    try:
        print("[FAKE-HEADLESS] Injecting anti-detection scripts...")
        
        # Get all stealth scripts
        scripts = get_stealth_scripts()
        
        # Inject each script
        for i, script in enumerate(scripts, 1):
            await page.add_init_script(script)
            print(f"[FAKE-HEADLESS] Injected script {i}/{len(scripts)}")
        
        print("[FAKE-HEADLESS] ✅ All scripts injected")
        
    except Exception as e:
        print(f"[FAKE-HEADLESS] ❌ Error injecting scripts: {e}")
        raise


async def patch_visibility(page):
    """
    Patch document visibility to always be visible
    TikTok won't count views if page is hidden
    Call this after page.goto()
    
    Args:
        page: Playwright page object
    """
    try:
        await page.evaluate("""
            Object.defineProperty(document, 'hidden', {
                get: () => false
            });
            
            Object.defineProperty(document, 'visibilityState', {
                get: () => 'visible'
            });
            
            // Override addEventListener for visibilitychange
            const originalAddEventListener = document.addEventListener;
            document.addEventListener = function(type, listener, options) {
                if (type === 'visibilitychange') {
                    // Don't add the listener
                    return;
                }
                return originalAddEventListener.call(this, type, listener, options);
            };
        """)
        
        print("[FAKE-HEADLESS] ✅ Visibility patched")
        
    except Exception as e:
        print(f"[FAKE-HEADLESS] ⚠️ Error patching visibility: {e}")


async def ensure_video_playback(page):
    """
    Ensure video plays and dispatches events for view counting
    ✅ UPDATED: Uses new livestream playback detection
    
    Args:
        page: Playwright page object
    """
    try:
        # Use new detection methods
        player_found = await wait_for_livestream_player(page, timeout=60000)
        if not player_found:
            print("[FAKE-HEADLESS] ⚠️  Live room player not found")
            return
        
        video_found = await wait_for_video_element(page, timeout=60000)
        if not video_found:
            print("[FAKE-HEADLESS] ⚠️  Video element not found")
            return
        
        playing = await ensure_video_playing(page)
        if playing:
            print("[FAKE-HEADLESS] ✅ Video playback ensured")
        else:
            print("[FAKE-HEADLESS] ⚠️  Video not playing")
        
    except Exception as e:
        print(f"[FAKE-HEADLESS] ⚠️  Error ensuring playback: {e}")

async def start_timeupdate_loop(page):
    """
    Start continuous timeupdate events for view counting
    TikTok tracks watchtime via timeupdate events
    
    Args:
        page: Playwright page object
    """
    try:
        await page.evaluate("""
            // Dispatch timeupdate every 250ms
            setInterval(() => {
                const video = document.querySelector('video');
                if (video && !video.paused) {
                    video.dispatchEvent(new Event('timeupdate'));
                }
            }, 250);
        """)
        
        print("[FAKE-HEADLESS] ✅ Timeupdate loop started")
        
    except Exception as e:
        print(f"[FAKE-HEADLESS] ⚠️ Error starting timeupdate: {e}")


async def simulate_human_interaction(page, duration_seconds=3600):
    """
    Simulate random human interactions
    - Random mouse movements
    - Random small scrolls
    
    Args:
        page: Playwright page object
        duration_seconds: How long to simulate (default 1 hour)
    """
    try:
        print(f"[FAKE-HEADLESS] Starting human simulation for {duration_seconds}s...")
        
        start_time = asyncio.get_event_loop().time()
        
        while asyncio.get_event_loop().time() - start_time < duration_seconds:
            # Random delay between interactions (15-40 seconds)
            delay = random.uniform(15, 40)
            await asyncio.sleep(delay)
            
            try:
                # Random mouse move (2-4 pixels)
                x = random.randint(2, 4)
                y = random.randint(2, 4)
                
                await page.mouse.move(x, y)
                
                # Sometimes do a small scroll (< 50px)
                if random.random() < 0.3:  # 30% chance
                    scroll_amount = random.randint(-50, 50)
                    await page.evaluate(f"window.scrollBy(0, {scroll_amount})")
                
            except Exception as e:
                # Page might be closed, break loop
                print(f"[FAKE-HEADLESS] Interaction error: {e}")
                break
        
        print("[FAKE-HEADLESS] Human simulation ended")
        
    except Exception as e:
        print(f"[FAKE-HEADLESS] ⚠️ Error in human simulation: {e}")


async def setup_complete_stealth(page, start_human_sim=True):
    """
    Complete stealth setup - call this after page.goto()
    
    Args:
        page: Playwright page object
        start_human_sim: Whether to start human interaction simulation
    
    Returns:
        asyncio.Task: Human simulation task (if started)
    """
    try:
        print("[FAKE-HEADLESS] Setting up complete stealth...")
        
        # Patch visibility
        await patch_visibility(page)
        
        # Wait a bit for page to load
        await asyncio.sleep(2)
        
        # Ensure video playback
        await ensure_video_playback(page)
        
        # Start timeupdate loop
        await start_timeupdate_loop(page)
        
        # Start human simulation in background
        human_sim_task = None
        if start_human_sim:
            human_sim_task = asyncio.create_task(simulate_human_interaction(page))
        
        print("[FAKE-HEADLESS] ✅ Complete stealth setup done")
        
        return human_sim_task
        
    except Exception as e:
        print(f"[FAKE-HEADLESS] ❌ Error in complete stealth setup: {e}")
        return None


def get_gpu_enabled_args():
    """
    Get Chrome args with GPU ENABLED and RAM optimized
    
    Returns:
        list: Chrome arguments
    """
    return [
        # GPU ENABLED (CRITICAL)
        '--enable-gpu',
        '--ignore-gpu-blocklist',
        '--use-gl=angle',
        '--use-angle=gl',
        '--enable-zero-copy',
        
        # RAM optimization (~150-220MB per profile)
        '--memory-pressure-off',
        '--renderer-process-limit=1',
        '--disable-features=Translate,OptimizationGuideModelDownloading,MediaRouter',
        '--enable-low-end-device-mode',
        '--js-flags=--optimize_for_size --max_old_space_size=32',
        
        # Essential flags (not bot-farm flags)
        '--no-first-run',
        '--no-default-browser-check',
        '--disable-sync',
        '--disable-background-networking',
        '--disable-default-apps',
        
        # Headless NEW mode (Chrome 119+)
        '--headless=new',
        
        # Window size (will be overridden by viewport)
        '--window-size=360,640'
    ]
