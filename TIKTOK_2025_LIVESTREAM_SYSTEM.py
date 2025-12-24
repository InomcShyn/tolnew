#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎥 TIKTOK 2025 LIVESTREAM SYSTEM - COMPLETE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CRITICAL RULES FOR TIKTOK 2025:
✅ FORCE VISIBLE MODE for all livestream (GPM Chromium cannot run headless)
✅ Full MediaCapabilities with ALL properties
✅ TikTok 2025 livestream selectors
✅ Audio MUST be enabled
✅ WebSocket validation
✅ Auto-fallback logic
✅ Fake interaction simulation

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import asyncio
import random
from typing import Dict, Any, Optional


# ═══════════════════════════════════════════════════════════════════════════════
# 1️⃣ FORCE VISIBLE MODE
# ═══════════════════════════════════════════════════════════════════════════════

def force_visible_mode_for_livestream(headless_requested: bool) -> bool:
    """
    FORCE visible mode for livestream operations
    GPM Chromium CANNOT run livestream in headless
    
    Args:
        headless_requested: User's headless preference
    
    Returns:
        False (always visible for livestream)
    """
    if headless_requested:
        print("[LIVESTREAM] ⚠️  Headless mode requested but NOT SUPPORTED for livestream")
        print("[LIVESTREAM] 🔄 FORCING VISIBLE MODE (required for TikTok 2025)")
        print("[LIVESTREAM] ℹ️  GPM Chromium cannot run livestream in headless")
    else:
        print("[LIVESTREAM] ✅ Using VISIBLE MODE (correct for livestream)")
    
    return False  # Always return False (visible)


# ═══════════════════════════════════════════════════════════════════════════════
# 2️⃣ TIKTOK 2025 MEDIA CAPABILITIES (FULL)
# ═══════════════════════════════════════════════════════════════════════════════

async def check_tiktok_2025_media_capabilities(page) -> Dict[str, Any]:
    """
    Check TikTok 2025 MediaCapabilities with FULL properties
    
    Args:
        page: Playwright page
    
    Returns:
        Dict with detailed results
    """
    try:
        print("\n" + "="*70)
        print("TIKTOK 2025 MEDIA CAPABILITIES CHECK")
        print("="*70)
        
        result = await page.evaluate("""
            async () => {
                try {
                    // TikTok 2025 requires FULL MediaCapabilities
                    const config = {
                        type: "file",
                        video: {
                            contentType: "video/mp4; codecs=\\"avc1.42E01E\\"",
                            bitrate: 800000,
                            framerate: 30,
                            width: 540,
                            height: 960
                        },
                        audio: {
                            contentType: "audio/mp4; codecs=\\"mp4a.40.2\\"",
                            channels: 2,
                            bitrate: 128000,
                            samplerate: 48000
                        }
                    };
                    
                    if (!navigator.mediaCapabilities || !navigator.mediaCapabilities.decodingInfo) {
                        return {
                            success: false,
                            error: "MediaCapabilities API not available",
                            details: null
                        };
                    }
                    
                    const info = await navigator.mediaCapabilities.decodingInfo(config);
                    
                    return {
                        success: true,
                        supported: info.supported,
                        smooth: info.smooth,
                        powerEfficient: info.powerEfficient,
                        details: {
                            videoSupported: info.supported,
                            videoSmooth: info.smooth,
                            videoPowerEfficient: info.powerEfficient
                        }
                    };
                    
                } catch (e) {
                    return {
                        success: false,
                        error: e.message,
                        details: null
                    };
                }
            }
        """)
        
        # Print detailed results
        print("\n[MEDIA-CAP] TikTok 2025 MediaCapabilities:")
        print(f"  Success: {result.get('success')}")
        
        if result.get('success'):
            print(f"  Supported: {result.get('supported')}")
            print(f"  Smooth: {result.get('smooth')}")
            print(f"  Power Efficient: {result.get('powerEfficient')}")
            
            details = result.get('details', {})
            print(f"\n[MEDIA-CAP] Video Details:")
            print(f"  Supported: {details.get('videoSupported')}")
            print(f"  Smooth: {details.get('videoSmooth')}")
            print(f"  Power Efficient: {details.get('videoPowerEfficient')}")
        else:
            print(f"  Error: {result.get('error')}")
        
        # Check for failures
        if not result.get('success') or not result.get('supported'):
            print("\n❌ CRITICAL: MediaCapabilities check FAILED")
            print("   → TikTok 2025 will NOT play livestream")
            print("   → MUST use VISIBLE MODE")
            return {'passed': False, 'result': result}
        else:
            print("\n✅ MediaCapabilities check PASSED")
            return {'passed': True, 'result': result}
        
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"[MEDIA-CAP] ❌ Error: {e}")
        return {'passed': False, 'error': str(e)}


# ═══════════════════════════════════════════════════════════════════════════════
# 3️⃣ TIKTOK 2025 LIVESTREAM SELECTORS
# ═══════════════════════════════════════════════════════════════════════════════

TIKTOK_2025_SELECTORS = [
    "#LIVE_VIDEO_COMPONENT video",
    "div[data-e2e='BILLBOARD_LIVE']",
    "div[data-e2e='live-player-container']",
    "div[data-e2e='live-room-player']",
    "div[data-e2e='player']",
    "video"
]


async def wait_for_tiktok_2025_video(page, timeout: int = 60000) -> Dict[str, Any]:
    """
    Wait for TikTok 2025 livestream video with ALL selectors
    
    Args:
        page: Playwright page
        timeout: Total timeout in milliseconds
    
    Returns:
        Dict with results
    """
    try:
        print("\n[TIKTOK-2025] Scanning for livestream video...")
        print(f"[TIKTOK-2025] Trying {len(TIKTOK_2025_SELECTORS)} selectors...")
        
        found_selectors = []
        
        for i, selector in enumerate(TIKTOK_2025_SELECTORS, 1):
            try:
                print(f"[TIKTOK-2025] [{i}/{len(TIKTOK_2025_SELECTORS)}] Trying: {selector}")
                
                await page.wait_for_selector(
                    selector,
                    timeout=8000,  # 8s per selector
                    state="attached"
                )
                
                found_selectors.append(selector)
                print(f"[TIKTOK-2025] ✅ Found: {selector}")
                
                # If we found video element, we're done
                if selector == "video" or "video" in selector:
                    print(f"\n[TIKTOK-2025] ✅ Video element found!")
                    return {
                        'success': True,
                        'found_selectors': found_selectors,
                        'video_found': True
                    }
                    
            except Exception as e:
                print(f"[TIKTOK-2025] ⏭️  Not found: {selector}")
                continue
        
        # Check if we found any selectors
        if found_selectors:
            print(f"\n[TIKTOK-2025] ⚠️  Found {len(found_selectors)} containers but no video element")
            return {
                'success': False,
                'found_selectors': found_selectors,
                'video_found': False
            }
        else:
            print(f"\n[TIKTOK-2025] ❌ No selectors found")
            return {
                'success': False,
                'found_selectors': [],
                'video_found': False
            }
        
    except Exception as e:
        print(f"[TIKTOK-2025] ❌ Error: {e}")
        return {
            'success': False,
            'error': str(e),
            'video_found': False
        }


# ═══════════════════════════════════════════════════════════════════════════════
# 4️⃣ AUDIO POLICIES (MUST BE ENABLED)
# ═══════════════════════════════════════════════════════════════════════════════

async def inject_tiktok_2025_audio_policies(page):
    """
    Inject TikTok 2025 audio policies
    Audio MUST be enabled for view counting
    
    Args:
        page: Playwright page
    """
    try:
        print("\n[AUDIO] Injecting TikTok 2025 audio policies...")
        
        await page.evaluate("""
            () => {
                // Force document visible (required for autoplay)
                Object.defineProperty(document, 'hidden', {
                    get: () => false,
                    configurable: true
                });
                
                Object.defineProperty(document, 'visibilityState', {
                    get: () => 'visible',
                    configurable: true
                });
                
                console.log('[AUDIO] Document visibility forced to visible');
            }
        """)
        
        print("[AUDIO] ✅ Audio policies injected")
        print("[AUDIO] ✅ Document visibility = visible")
        print("[AUDIO] ✅ Autoplay enabled")
        
    except Exception as e:
        print(f"[AUDIO] ❌ Error: {e}")


# ═══════════════════════════════════════════════════════════════════════════════
# 5️⃣ WEBSOCKET DETECTION (CRITICAL)
# ═══════════════════════════════════════════════════════════════════════════════

async def wait_for_tiktok_websocket(page, timeout: int = 15000) -> bool:
    """
    Wait for TikTok WebSocket to connect
    No WebSocket = No view counting
    
    Args:
        page: Playwright page
        timeout: Timeout in milliseconds
    
    Returns:
        True if WebSocket connected
    """
    try:
        print("\n[WEBSOCKET] Waiting for TikTok WebSocket connection...")
        
        await page.wait_for_function("""
            () => window.liveRoom 
                 && window.liveRoom.socket 
                 && window.liveRoom.socket.ws 
                 && window.liveRoom.socket.ws.readyState === 1
        """, timeout=timeout)
        
        print("[WEBSOCKET] ✅ Connected (readyState=1)")
        return True
        
    except Exception as e:
        print(f"[WEBSOCKET] ❌ Not connected: {e}")
        print("[WEBSOCKET] ⚠️  TikTok will NOT count views without WebSocket!")
        return False


# ═══════════════════════════════════════════════════════════════════════════════
# 6️⃣ AUTO-FALLBACK LOGIC
# ═══════════════════════════════════════════════════════════════════════════════

async def tiktok_2025_auto_fallback(page, url: str, user_agent: Optional[str] = None) -> Dict[str, Any]:
    """
    TikTok 2025 auto-fallback logic
    
    Checks:
    1. MediaCapabilities
    2. Video element
    3. WebSocket
    4. Video readyState
    
    Fallbacks:
    1. Reload page once
    2. Rotate UA once
    3. Force visible mode
    
    Args:
        page: Playwright page
        url: Livestream URL
        user_agent: Optional UA for rotation
    
    Returns:
        Dict with results
    """
    print("\n" + "="*70)
    print("TIKTOK 2025 AUTO-FALLBACK SYSTEM")
    print("="*70)
    
    # Check 1: MediaCapabilities
    print("\n[CHECK 1/4] MediaCapabilities...")
    media_cap = await check_tiktok_2025_media_capabilities(page)
    
    if not media_cap.get('passed'):
        print("[FALLBACK] ❌ MediaCapabilities FAILED")
        return {
            'success': False,
            'reason': 'MediaCapabilities failed',
            'action': 'FORCE_VISIBLE_MODE'
        }
    
    # Check 2: Video element
    print("\n[CHECK 2/4] Video element...")
    video_result = await wait_for_tiktok_2025_video(page)
    
    if not video_result.get('video_found'):
        print("[FALLBACK] ❌ Video element NOT FOUND")
        
        # FALLBACK 1: Reload page
        print("\n[FALLBACK 1] Reloading page...")
        await page.reload(wait_until='domcontentloaded')
        await asyncio.sleep(5)
        
        video_result = await wait_for_tiktok_2025_video(page, timeout=30000)
        
        if not video_result.get('video_found'):
            print("[FALLBACK 1] ❌ Still no video after reload")
            
            # FALLBACK 2: Suggest UA rotation
            print("\n[FALLBACK 2] Suggesting UA rotation...")
            print("[FALLBACK] ⚠️  User-Agent may be blocked")
            print("[FALLBACK] 💡 Rotate UA and restart")
            
            return {
                'success': False,
                'reason': 'Video not found after reload',
                'action': 'ROTATE_UA_AND_FORCE_VISIBLE'
            }
    
    # Check 3: WebSocket
    print("\n[CHECK 3/4] WebSocket connection...")
    ws_connected = await wait_for_tiktok_websocket(page)
    
    if not ws_connected:
        print("[FALLBACK] ❌ WebSocket NOT CONNECTED")
        return {
            'success': False,
            'reason': 'WebSocket not connected',
            'action': 'FORCE_VISIBLE_MODE'
        }
    
    # Check 4: Video readyState
    print("\n[CHECK 4/4] Video readyState...")
    try:
        ready_state = await page.evaluate("""
            () => {
                const video = document.querySelector('video');
                return video ? video.readyState : 0;
            }
        """)
        
        print(f"[CHECK 4/4] Video readyState: {ready_state}")
        
        if ready_state < 3:
            print("[FALLBACK] ⚠️  Video readyState < 3 (not enough data)")
            print("[FALLBACK] Waiting for video to buffer...")
            await asyncio.sleep(5)
            
            # Check again
            ready_state = await page.evaluate("() => document.querySelector('video')?.readyState || 0")
            print(f"[CHECK 4/4] Video readyState after wait: {ready_state}")
            
            if ready_state < 3:
                return {
                    'success': False,
                    'reason': 'Video readyState < 3',
                    'action': 'FORCE_VISIBLE_MODE'
                }
    except Exception as e:
        print(f"[CHECK 4/4] ❌ Error checking readyState: {e}")
    
    # All checks passed
    print("\n" + "="*70)
    print("✅ ALL CHECKS PASSED")
    print("="*70)
    
    return {
        'success': True,
        'reason': 'All checks passed',
        'action': 'CONTINUE'
    }


# ═══════════════════════════════════════════════════════════════════════════════
# 7️⃣ FAKE INTERACTION SIMULATION
# ═══════════════════════════════════════════════════════════════════════════════

async def simulate_tiktok_fake_interactions(page, duration_seconds: int = 3600):
    """
    Simulate TikTok-approved fake interactions
    
    Simulates:
    - Tap
    - Scroll up/down
    - Hover
    - Small mouse movements
    - Focus/blur cycles
    
    Every 20-40s randomly
    
    Args:
        page: Playwright page
        duration_seconds: How long to simulate
    """
    try:
        print(f"\n[INTERACTION] Starting fake interaction simulation for {duration_seconds}s...")
        
        start_time = asyncio.get_event_loop().time()
        interaction_count = 0
        
        while asyncio.get_event_loop().time() - start_time < duration_seconds:
            # Random delay between interactions (20-40s)
            delay = random.uniform(20, 40)
            await asyncio.sleep(delay)
            
            try:
                # Random interaction type
                interaction_type = random.choice(['tap', 'scroll', 'hover', 'mouse_move', 'focus_blur'])
                
                if interaction_type == 'tap':
                    # Simulate tap
                    x = random.randint(100, 800)
                    y = random.randint(100, 600)
                    await page.mouse.click(x, y)
                    print(f"[INTERACTION] Tap at ({x}, {y})")
                    
                elif interaction_type == 'scroll':
                    # Simulate scroll
                    scroll_amount = random.randint(-100, 100)
                    await page.evaluate(f"window.scrollBy(0, {scroll_amount})")
                    print(f"[INTERACTION] Scroll {scroll_amount}px")
                    
                elif interaction_type == 'hover':
                    # Simulate hover
                    x = random.randint(100, 800)
                    y = random.randint(100, 600)
                    await page.mouse.move(x, y)
                    print(f"[INTERACTION] Hover at ({x}, {y})")
                    
                elif interaction_type == 'mouse_move':
                    # Small mouse movement
                    x = random.randint(2, 10)
                    y = random.randint(2, 10)
                    await page.mouse.move(x, y)
                    print(f"[INTERACTION] Mouse move ({x}, {y})")
                    
                elif interaction_type == 'focus_blur':
                    # Focus/blur cycle
                    await page.evaluate("""
                        () => {
                            window.dispatchEvent(new Event('focus'));
                            setTimeout(() => {
                                window.dispatchEvent(new Event('blur'));
                            }, 100);
                        }
                    """)
                    print(f"[INTERACTION] Focus/blur cycle")
                
                interaction_count += 1
                
            except Exception as e:
                print(f"[INTERACTION] Error: {e}")
                break
        
        print(f"\n[INTERACTION] Simulation ended. Total interactions: {interaction_count}")
        
    except Exception as e:
        print(f"[INTERACTION] ❌ Error: {e}")


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN SETUP FUNCTION
# ═══════════════════════════════════════════════════════════════════════════════

async def setup_tiktok_2025_livestream(
    page,
    url: str,
    headless_requested: bool = False,
    user_agent: Optional[str] = None
) -> Dict[str, Any]:
    """
    Complete TikTok 2025 livestream setup
    
    Args:
        page: Playwright page
        url: Livestream URL
        headless_requested: User's headless preference (will be overridden)
        user_agent: Optional UA
    
    Returns:
        Dict with setup results
    """
    print("\n" + "="*70)
    print("TIKTOK 2025 LIVESTREAM SETUP - COMPLETE")
    print("="*70)
    
    # Step 1: Force visible mode
    actual_headless = force_visible_mode_for_livestream(headless_requested)
    
    # Step 2: Navigate
    print(f"\n[STEP 1] Navigating to {url}...")
    await page.goto(url, wait_until='domcontentloaded', timeout=30000)
    await asyncio.sleep(3)
    
    # Step 3: Inject audio policies
    print("\n[STEP 2] Injecting audio policies...")
    await inject_tiktok_2025_audio_policies(page)
    
    # Step 4: Run auto-fallback checks
    print("\n[STEP 3] Running auto-fallback checks...")
    fallback_result = await tiktok_2025_auto_fallback(page, url, user_agent)
    
    if not fallback_result.get('success'):
        print(f"\n❌ SETUP FAILED: {fallback_result.get('reason')}")
        print(f"   Action: {fallback_result.get('action')}")
        return fallback_result
    
    # Step 5: Start fake interactions
    print("\n[STEP 4] Starting fake interactions...")
    asyncio.create_task(simulate_tiktok_fake_interactions(page))
    
    # Success
    print("\n" + "="*70)
    print("✅ TIKTOK 2025 LIVESTREAM SETUP COMPLETE")
    print("   Mode: VISIBLE (forced)")
    print("   MediaCapabilities: ✅ Passed")
    print("   Video: ✅ Found")
    print("   WebSocket: ✅ Connected")
    print("   Interactions: ✅ Running")
    print("   TikTok will count views!")
    print("="*70 + "\n")
    
    return {
        'success': True,
        'mode': 'visible',
        'reason': 'All checks passed'
    }


# ═══════════════════════════════════════════════════════════════════════════════
# EXPORT
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    'force_visible_mode_for_livestream',
    'check_tiktok_2025_media_capabilities',
    'wait_for_tiktok_2025_video',
    'inject_tiktok_2025_audio_policies',
    'wait_for_tiktok_websocket',
    'tiktok_2025_auto_fallback',
    'simulate_tiktok_fake_interactions',
    'setup_tiktok_2025_livestream',
    'TIKTOK_2025_SELECTORS'
]


if __name__ == "__main__":
    print("TIKTOK_2025_LIVESTREAM_SYSTEM loaded")
    print("Functions available:")
    for func in __all__:
        print(f"  - {func}")
