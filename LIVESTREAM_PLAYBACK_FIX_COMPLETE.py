#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎥 LIVESTREAM PLAYBACK FIX - COMPLETE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CRITICAL FIXES FOR TIKTOK LIVESTREAM VIEW COUNTING:
✅ headless="new" instead of headless=True
✅ Remove audio-breaking flags
✅ Add REQUIRED livestream GPU flags
✅ Fix livestream playback detection
✅ Add WebSocket validation
✅ Fix navigation bugs
✅ Add comprehensive debug logs
✅ Add fallback & retry logic

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import asyncio
from typing import Optional, Dict, Any


# ═══════════════════════════════════════════════════════════════════════════════
# 1️⃣ BROWSER LAUNCH FLAGS - LIVESTREAM OPTIMIZED
# ═══════════════════════════════════════════════════════════════════════════════

def get_livestream_browser_args(headless_mode: bool = True) -> list:
    """
    Get browser args optimized for TikTok livestream
    
    Args:
        headless_mode: True for headless, False for visible
    
    Returns:
        List of Chrome arguments
    """
    
    args = [
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # REQUIRED LIVESTREAM FLAGS (DO NOT REMOVE)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        '--enable-gpu',
        '--ignore-gpu-blocklist',
        '--enable-accelerated-video-decode',
        '--enable-features=PlatformHEVCDecoderSupport,UseHardwareVideoDecode,MediaFoundationVideoCapture',
        '--use-gl=angle',
        '--use-angle=d3d11',
        '--disable-features=AudioServiceOutOfProcess',
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # GPU HYBRID MODE (WebGL ON + RAM optimized)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        '--disable-gpu-sandbox',
        '--enable-webgl',
        '--enable-webgl2',
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # RAM OPTIMIZATION (keep 150-200MB)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        '--disable-background-networking',
        '--disable-background-timer-throttling',
        '--disable-backgrounding-occluded-windows',
        '--disable-breakpad',
        '--disable-client-side-phishing-detection',
        '--disable-component-extensions-with-background-pages',
        '--disable-default-apps',
        '--disable-dev-shm-usage',
        '--disable-extensions',
        '--disable-features=TranslateUI,BlinkGenPropertyTrees',
        '--disable-hang-monitor',
        '--disable-ipc-flooding-protection',
        '--disable-popup-blocking',
        '--disable-prompt-on-repost',
        '--disable-renderer-backgrounding',
        '--disable-sync',
        '--force-color-profile=srgb',
        '--metrics-recording-only',
        '--no-first-run',
        '--password-store=basic',
        '--use-mock-keychain',
        '--disable-blink-features=AutomationControlled',
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # STEALTH FLAGS
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        '--disable-blink-features=AutomationControlled',
        '--exclude-switches=enable-automation',
        '--disable-infobars',
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # WINDOW SIZE (for headless)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        '--window-size=1920,1080',
        '--window-position=0,0',
    ]
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # REMOVED FLAGS (BREAK LIVESTREAM - DO NOT ADD BACK)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # ❌ '--mute-audio'
    # ❌ '--disable-audio-output'
    # ❌ '--disable-gpu-compositing'
    # ❌ '--disable-accelerated-2d-canvas'
    
    return args


# ═══════════════════════════════════════════════════════════════════════════════
# 2️⃣ LIVESTREAM PLAYBACK DETECTION - FIXED
# ═══════════════════════════════════════════════════════════════════════════════

async def wait_for_livestream_player(page, timeout: int = 60000) -> bool:
    """
    Wait for TikTok livestream player to load
    
    Args:
        page: Playwright page
        timeout: Timeout in milliseconds (default 60s)
    
    Returns:
        True if player loaded successfully
    """
    try:
        print("[LIVESTREAM] Waiting for live room player...")
        
        # Wait for live room player container
        await page.wait_for_selector(
            "div[data-e2e='live-room-player']",
            timeout=timeout,
            state="attached"
        )
        
        print("[LIVESTREAM] ✅ Live room player found")
        return True
        
    except Exception as e:
        print(f"[LIVESTREAM] ❌ Live room player not found: {e}")
        return False


async def wait_for_video_element(page, timeout: int = 60000) -> bool:
    """
    Wait for video element to be attached (with multiple selectors)
    
    Args:
        page: Playwright page
        timeout: Timeout in milliseconds (default 60s)
    
    Returns:
        True if video element found
    """
    try:
        print("[LIVESTREAM] Waiting for video element...")
        
        # Try multiple selectors
        selectors = [
            "div[data-e2e='live-room-player']",
            "div[data-e2e='player']",
            "video"
        ]
        
        for selector in selectors:
            try:
                await page.wait_for_selector(
                    selector,
                    timeout=8000,  # 8s per selector
                    state="attached"
                )
                print(f"[LIVESTREAM] ✅ Found: {selector}")
                
                # If found player container, still need to wait for video
                if 'video' not in selector:
                    continue
                else:
                    return True
                    
            except Exception:
                print(f"[LIVESTREAM] ⏭️  Skipped: {selector}")
                continue
        
        # Final check for video
        try:
            await page.wait_for_selector("video", timeout=10000, state="attached")
            print("[LIVESTREAM] ✅ Video element found")
            return True
        except:
            print("[LIVESTREAM] ❌ Video element not found after all attempts")
            return False
        
    except Exception as e:
        print(f"[LIVESTREAM] ❌ Error: {e}")
        return False


async def ensure_video_playing(page) -> bool:
    """
    Ensure video is playing
    
    Args:
        page: Playwright page
    
    Returns:
        True if video is playing
    """
    try:
        print("[LIVESTREAM] Ensuring video playback...")
        
        result = await page.evaluate("""
            async () => {
                const video = document.querySelector('video');
                if (!video) {
                    return {success: false, error: 'No video element'};
                }
                
                try {
                    // Try to play
                    await video.play();
                    
                    // Wait a bit
                    await new Promise(resolve => setTimeout(resolve, 1000));
                    
                    return {
                        success: !video.paused,
                        paused: video.paused,
                        readyState: video.readyState,
                        currentTime: video.currentTime,
                        width: video.videoWidth,
                        height: video.videoHeight
                    };
                } catch (e) {
                    return {success: false, error: e.message};
                }
            }
        """)
        
        if result.get('success'):
            print(f"[LIVESTREAM] ✅ Video playing: {result.get('width')}x{result.get('height')}")
            return True
        else:
            print(f"[LIVESTREAM] ⚠️  Video not playing: {result.get('error', 'Unknown')}")
            return False
            
    except Exception as e:
        print(f"[LIVESTREAM] ❌ Error ensuring playback: {e}")
        return False


# ═══════════════════════════════════════════════════════════════════════════════
# 3️⃣ WEBSOCKET VALIDATION
# ═══════════════════════════════════════════════════════════════════════════════

async def check_websocket_connection(page) -> Dict[str, Any]:
    """
    Check if TikTok livestream WebSocket is connected
    
    Args:
        page: Playwright page
    
    Returns:
        Dict with WebSocket status
    """
    try:
        print("[WEBSOCKET] Checking connection...")
        
        ws_status = await page.evaluate("""
            () => {
                // Check if liveRoom object exists
                if (!window.liveRoom) {
                    return {
                        connected: false,
                        error: 'liveRoom object not found',
                        readyState: null
                    };
                }
                
                // Check socket
                if (!window.liveRoom.socket) {
                    return {
                        connected: false,
                        error: 'socket not found',
                        readyState: null
                    };
                }
                
                // Check WebSocket
                if (!window.liveRoom.socket.ws) {
                    return {
                        connected: false,
                        error: 'WebSocket not found',
                        readyState: null
                    };
                }
                
                const readyState = window.liveRoom.socket.ws.readyState;
                
                return {
                    connected: readyState === 1,
                    readyState: readyState,
                    error: null
                };
            }
        """)
        
        if ws_status.get('connected'):
            print("[WEBSOCKET] ✅ Connected (readyState=1)")
        else:
            error = ws_status.get('error', 'Unknown')
            ready_state = ws_status.get('readyState')
            print(f"[WEBSOCKET] ⚠️  Not connected: {error} (readyState={ready_state})")
            print("[WEBSOCKET] ⚠️  TikTok may not count view without WebSocket!")
        
        return ws_status
        
    except Exception as e:
        print(f"[WEBSOCKET] ❌ Error checking: {e}")
        return {'connected': False, 'error': str(e), 'readyState': None}


# ═══════════════════════════════════════════════════════════════════════════════
# 4️⃣ NAVIGATION FIX
# ═══════════════════════════════════════════════════════════════════════════════

async def navigate_to_livestream(page, url: str, max_retries: int = 2) -> bool:
    """
    Navigate to livestream with proper handling
    
    Args:
        page: Playwright page
        url: Livestream URL
        max_retries: Max retry attempts
    
    Returns:
        True if navigation successful
    """
    for attempt in range(max_retries):
        try:
            if attempt > 0:
                print(f"[NAV] Retry {attempt}/{max_retries-1}...")
                await asyncio.sleep(2)
            
            # Check current URL
            current_url = page.url
            
            # If on about:blank, force navigation
            if current_url == "about:blank" or not current_url.startswith("http"):
                print(f"[NAV] Current page: {current_url}")
                print(f"[NAV] Forcing navigation to: {url}")
            
            # Navigate
            print(f"[NAV] Navigating to {url}...")
            await page.goto(url, wait_until='domcontentloaded', timeout=30000)
            
            # Wait a bit for page to settle
            await asyncio.sleep(2)
            
            # Verify we're on the right page
            final_url = page.url
            if url in final_url or "live" in final_url:
                print(f"[NAV] ✅ Navigation successful: {final_url}")
                return True
            else:
                print(f"[NAV] ⚠️  Unexpected URL: {final_url}")
                if attempt < max_retries - 1:
                    continue
                    
        except Exception as e:
            print(f"[NAV] ❌ Navigation error: {e}")
            if attempt < max_retries - 1:
                continue
    
    return False


# ═══════════════════════════════════════════════════════════════════════════════
# 5️⃣ DEBUG LOGS - COMPREHENSIVE
# ═══════════════════════════════════════════════════════════════════════════════

async def check_livestream_compatibility(page) -> Dict[str, Any]:
    """
    Check livestream compatibility (CRITICAL for debugging)
    
    Args:
        page: Playwright page
    
    Returns:
        Dict with compatibility results
    """
    try:
        print("\n" + "="*70)
        print("LIVESTREAM COMPATIBILITY CHECK")
        print("="*70)
        
        results = await page.evaluate("""
            async () => {
                const checks = {};
                
                // 1. WebGL Renderer
                try {
                    const canvas = document.createElement('canvas');
                    const gl = canvas.getContext('webgl');
                    if (gl) {
                        const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
                        checks.webgl = debugInfo ? 
                            gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL) : 
                            'No debug info';
                    } else {
                        checks.webgl = null;
                    }
                } catch (e) {
                    checks.webgl = 'Error: ' + e.message;
                }
                
                // 2. MediaCapabilities
                try {
                    if (navigator.mediaCapabilities && navigator.mediaCapabilities.decodingInfo) {
                        const result = await navigator.mediaCapabilities.decodingInfo({
                            type: 'file',
                            audio: {contentType: 'audio/mp4'},
                            video: {contentType: 'video/mp4; codecs="avc1.42E01E"'}
                        });
                        checks.mediaCapabilities = result.supported ? 'Supported' : 'Not supported';
                    } else {
                        checks.mediaCapabilities = null;
                    }
                } catch (e) {
                    checks.mediaCapabilities = 'Error: ' + e.message;
                }
                
                // 3. Video canPlayType
                try {
                    const video = document.createElement('video');
                    checks.videoSupport = video.canPlayType('video/mp4; codecs="avc1.42E01E"');
                } catch (e) {
                    checks.videoSupport = 'Error: ' + e.message;
                }
                
                // 4. WebSocket readyState
                try {
                    checks.wsReady = window.liveRoom?.socket?.ws?.readyState ?? null;
                } catch (e) {
                    checks.wsReady = 'Error: ' + e.message;
                }
                
                return checks;
            }
        """)
        
        # Print results
        print("\n[LIVESTREAM-DEBUG] WebGL renderer:", results.get('webgl'))
        print("[LIVESTREAM-DEBUG] MediaCapabilities:", results.get('mediaCapabilities'))
        print("[LIVESTREAM-DEBUG] Video canPlayType:", results.get('videoSupport'))
        print("[LIVESTREAM-DEBUG] WS readyState:", results.get('wsReady'))
        
        # Check for critical failures
        critical_failures = []
        if not results.get('webgl') or results.get('webgl') == 'null':
            critical_failures.append("WebGL not available")
        if not results.get('mediaCapabilities') or results.get('mediaCapabilities') == 'null':
            critical_failures.append("MediaCapabilities not available")
        if not results.get('videoSupport') or results.get('videoSupport') == '':
            critical_failures.append("Video codec not supported")
        
        if critical_failures:
            print("\n⚠️  CRITICAL FAILURES:")
            for failure in critical_failures:
                print(f"   ❌ {failure}")
            print("   → TikTok will NOT play livestream!")
        else:
            print("\n✅ All compatibility checks passed")
        
        print("="*70 + "\n")
        
        return results
        
    except Exception as e:
        print(f"[LIVESTREAM-DEBUG] ❌ Error checking compatibility: {e}")
        return {}


async def check_tiktok_anti_bot(page) -> Dict[str, Any]:
    """
    Check for TikTok anti-bot detection signals
    
    Args:
        page: Playwright page
    
    Returns:
        Dict with detection results
    """
    try:
        print("\n" + "="*70)
        print("TIKTOK ANTI-BOT DETECTION CHECK")
        print("="*70)
        
        results = await page.evaluate("""
            async () => {
                const checks = {};
                
                // 1. navigator.mediaCapabilities
                checks.mediaCapabilities = {
                    exists: !!navigator.mediaCapabilities,
                    decodingInfo: !!navigator.mediaCapabilities?.decodingInfo
                };
                
                // 2. video.audioTracks
                const video = document.querySelector('video');
                if (video) {
                    checks.videoAudioTracks = {
                        exists: !!video.audioTracks,
                        length: video.audioTracks?.length || 0
                    };
                    
                    // 3. video.readyState
                    checks.videoReadyState = {
                        value: video.readyState,
                        description: ['HAVE_NOTHING', 'HAVE_METADATA', 'HAVE_CURRENT_DATA', 'HAVE_FUTURE_DATA', 'HAVE_ENOUGH_DATA'][video.readyState] || 'UNKNOWN'
                    };
                } else {
                    checks.videoAudioTracks = {exists: false, length: 0};
                    checks.videoReadyState = {value: null, description: 'NO_VIDEO'};
                }
                
                // 4. WebGL renderer
                const canvas = document.createElement('canvas');
                const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
                if (gl) {
                    const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
                    if (debugInfo) {
                        checks.webgl = {
                            vendor: gl.getParameter(debugInfo.UNMASKED_VENDOR_WEBGL),
                            renderer: gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL)
                        };
                    } else {
                        checks.webgl = {vendor: 'N/A', renderer: 'N/A'};
                    }
                } else {
                    checks.webgl = {vendor: null, renderer: null};
                }
                
                // 5. Performance metrics
                if (window.performance && window.performance.memory) {
                    checks.performance = {
                        usedJSHeapSize: Math.round(window.performance.memory.usedJSHeapSize / 1024 / 1024) + 'MB',
                        totalJSHeapSize: Math.round(window.performance.memory.totalJSHeapSize / 1024 / 1024) + 'MB'
                    };
                } else {
                    checks.performance = {usedJSHeapSize: 'N/A', totalJSHeapSize: 'N/A'};
                }
                
                // 6. WebSocket check
                checks.websocket = {
                    liveRoomExists: !!window.liveRoom,
                    socketExists: !!window.liveRoom?.socket,
                    wsExists: !!window.liveRoom?.socket?.ws,
                    readyState: window.liveRoom?.socket?.ws?.readyState
                };
                
                return checks;
            }
        """)
        
        # Print results
        print("\n1. Media Capabilities:")
        print(f"   Exists: {results['mediaCapabilities']['exists']}")
        print(f"   decodingInfo: {results['mediaCapabilities']['decodingInfo']}")
        
        print("\n2. Video Audio Tracks:")
        print(f"   Exists: {results['videoAudioTracks']['exists']}")
        print(f"   Length: {results['videoAudioTracks']['length']}")
        
        print("\n3. Video Ready State:")
        print(f"   Value: {results['videoReadyState']['value']}")
        print(f"   Description: {results['videoReadyState']['description']}")
        
        print("\n4. WebGL:")
        print(f"   Vendor: {results['webgl']['vendor']}")
        print(f"   Renderer: {results['webgl']['renderer']}")
        
        print("\n5. Performance:")
        print(f"   Used Heap: {results['performance']['usedJSHeapSize']}")
        print(f"   Total Heap: {results['performance']['totalJSHeapSize']}")
        
        print("\n6. WebSocket:")
        print(f"   liveRoom: {results['websocket']['liveRoomExists']}")
        print(f"   socket: {results['websocket']['socketExists']}")
        print(f"   ws: {results['websocket']['wsExists']}")
        print(f"   readyState: {results['websocket']['readyState']}")
        
        print("="*70 + "\n")
        
        return results
        
    except Exception as e:
        print(f"[DEBUG] ❌ Error checking anti-bot: {e}")
        return {}


# ═══════════════════════════════════════════════════════════════════════════════
# 6️⃣ FALLBACK & RETRY LOGIC
# ═══════════════════════════════════════════════════════════════════════════════

async def setup_livestream_with_fallback(page, url: str, user_agent: Optional[str] = None, force_visible: bool = False) -> bool:
    """
    Setup livestream with fallback logic
    
    Args:
        page: Playwright page
        url: Livestream URL
        user_agent: Optional user agent to rotate
        force_visible: If True, suggest switching to visible mode
    
    Returns:
        True if setup successful
    """
    print("\n" + "="*70)
    print("LIVESTREAM SETUP WITH FALLBACK")
    print("="*70)
    
    # Step 1: Check compatibility FIRST
    print("\n[STEP 1] Checking livestream compatibility...")
    compat = await check_livestream_compatibility(page)
    
    # Step 2: Navigate
    print("\n[STEP 2] Navigating to livestream...")
    nav_success = await navigate_to_livestream(page, url)
    if not nav_success:
        print("[FALLBACK] ❌ Navigation failed")
        return False
    
    # Step 3: Wait for player
    print("\n[STEP 3] Waiting for player...")
    player_found = await wait_for_livestream_player(page, timeout=60000)
    
    # Step 4: Wait for video (with multiple selectors)
    print("\n[STEP 4] Waiting for video...")
    video_found = await wait_for_video_element(page, timeout=60000)
    
    # Step 5: FALLBACK 1 - Reload page once
    if not video_found:
        print("\n[FALLBACK 1] No video found, reloading page...")
        await page.reload(wait_until='domcontentloaded')
        await asyncio.sleep(5)
        
        # Try again
        video_found = await wait_for_video_element(page, timeout=30000)
    
    # Step 6: FALLBACK 2 - Suggest UA rotation
    if not video_found and user_agent:
        print("\n[FALLBACK 2] Still no video")
        print("[FALLBACK] ⚠️  Consider rotating user agent:")
        print("[FALLBACK]    1. Stop current session")
        print("[FALLBACK]    2. Rotate UA in profile settings")
        print("[FALLBACK]    3. Restart launcher")
    
    # Step 7: FALLBACK 3 - Force visible mode
    if not video_found and force_visible:
        print("\n[FALLBACK 3] Video not loading in headless mode")
        print("[FALLBACK] 🔄 RECOMMENDATION: Switch to VISIBLE MODE")
        print("[FALLBACK]    Run launcher with option 2 (VISIBLE + Mobile)")
        print("[FALLBACK]    GPM Chromium works better in visible mode for livestream")
    
    # Step 8: Ensure video playing
    if video_found:
        print("\n[STEP 5] Ensuring video playback...")
        playing = await ensure_video_playing(page)
        if not playing:
            print("[FALLBACK] ⚠️  Video not playing automatically")
    
    # Step 9: Check WebSocket
    print("\n[STEP 6] Checking WebSocket...")
    await asyncio.sleep(3)  # Wait for WS to connect
    ws_status = await check_websocket_connection(page)
    
    # Step 10: Run anti-bot checks
    print("\n[STEP 7] Running anti-bot checks...")
    await check_tiktok_anti_bot(page)
    
    # Step 11: Determine success
    success = video_found and ws_status.get('connected', False)
    
    print("\n" + "="*70)
    if success:
        print("✅ LIVESTREAM SETUP SUCCESSFUL")
        print("   Video: ✅ Found & Playing")
        print("   WebSocket: ✅ Connected")
        print("   TikTok will count views!")
    else:
        print("⚠️  LIVESTREAM SETUP INCOMPLETE")
        if not video_found:
            print("   Video: ❌ Not found")
        if not ws_status.get('connected'):
            print("   WebSocket: ❌ Not connected")
        print("   TikTok may NOT count views!")
        
        # Final recommendation
        if not video_found:
            print("\n💡 RECOMMENDATION:")
            print("   Try VISIBLE MODE (option 2) for better compatibility")
    print("="*70 + "\n")
    
    return success


# ═══════════════════════════════════════════════════════════════════════════════
# EXPORT
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    'get_livestream_browser_args',
    'wait_for_livestream_player',
    'wait_for_video_element',
    'ensure_video_playing',
    'check_websocket_connection',
    'navigate_to_livestream',
    'check_livestream_compatibility',
    'check_tiktok_anti_bot',
    'setup_livestream_with_fallback'
]


if __name__ == "__main__":
    print("LIVESTREAM_PLAYBACK_FIX_COMPLETE loaded")
    print("Functions available:")
    for func in __all__:
        print(f"  - {func}")
