#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Livestream Captcha Debug Module
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

MỤC TIÊU:
1. DETECT CAPTCHA (không bypass, không giải)
2. HIỂN THỊ CAPTCHA đầy đủ để hệ thống hiện tại giải
3. DEBUG rõ ràng vì sao livestream KHÔNG được tính view

KHÔNG:
- Tắt captcha
- Bypass captcha
- Fake solved
- Reload khi captcha xuất hiện
- Thay đổi UA/proxy
- Thêm stealth mới
"""

import asyncio
import time
from typing import Dict, Optional, Tuple


class CaptchaType:
    """Captcha types"""
    IFRAME = "iframe"
    REDIRECT = "redirect"
    CLOUDFLARE = "cloudflare"
    UNKNOWN = "unknown"


class LiveState:
    """TikTok LIVE states (2024-2025)"""
    LIVE_OK_WITH_WS = "LIVE_OK_WITH_WS"  # ✅ View will be counted
    VIDEO_ONLY_NO_WS = "VIDEO_ONLY_NO_WS"  # ❌ View NOT counted
    AGE_GATED_ROOM = "AGE_GATED_ROOM"  # ⚠️ Age restriction
    CAPTCHA_BLOCKED = "CAPTCHA_BLOCKED"  # ⚠️ Captcha present
    SESSION_RESTRICTED = "SESSION_RESTRICTED"  # ❌ Session invalid
    PAGE_CONTEXT_CLOSED = "PAGE_CONTEXT_CLOSED"  # ❌ Context closed
    UNKNOWN_LIVE_STATE = "UNKNOWN_LIVE_STATE"  # ❓ Unknown state


class LivestreamCaptchaDebugger:
    """
    Debug captcha và livestream issues
    
    CHỈ detect và log, KHÔNG fix hay bypass
    """
    
    def __init__(self, profile_id: str):
        self.profile_id = profile_id
        self.captcha_detected_at = None
        self.captcha_resolved_at = None
        self.captcha_type = None
    
    async def detect_captcha(self, page) -> Tuple[bool, Optional[str]]:
        """
        Detect CAPTCHA (không bypass, không giải)
        
        Returns:
            (has_captcha, captcha_type)
        """
        try:
            # Check if page is still open
            if page.is_closed():
                print(f"[CAPTCHA-DETECT-ERROR] Page already closed")
                return (False, None)
            
            # COMPREHENSIVE CAPTCHA DETECTION
            captcha_check = await page.evaluate("""
                () => {
                    // 1. Check modal captcha (TikTok login/OTP captcha)
                    const modalCaptcha = document.querySelector('.TUXModal.captcha-verify-container');
                    if (modalCaptcha && modalCaptcha.offsetParent !== null) {
                        return {
                            found: true, 
                            type: 'modal',
                            selector: '.TUXModal.captcha-verify-container',
                            visible: true
                        };
                    }
                    
                    // 2. Check secsdk-captcha (rotate/puzzle captcha)
                    const secsdkCaptcha = document.querySelector('.secsdk-captcha-container');
                    if (secsdkCaptcha && secsdkCaptcha.offsetParent !== null) {
                        return {
                            found: true,
                            type: 'secsdk',
                            selector: '.secsdk-captcha-container',
                            visible: true
                        };
                    }
                    
                    // 3. Check iframe captcha
                    const iframes = document.querySelectorAll('iframe');
                    for (const iframe of iframes) {
                        const src = iframe.src || '';
                        if (src.includes('captcha') || 
                            src.includes('verify') || 
                            src.includes('security')) {
                            return {
                                found: true, 
                                type: 'iframe',
                                src: src,
                                visible: iframe.offsetParent !== null
                            };
                        }
                    }
                    
                    // 4. Check data-e2e captcha elements
                    const captchaElements = document.querySelectorAll('[data-e2e*="captcha"]');
                    if (captchaElements.length > 0) {
                        for (const el of captchaElements) {
                            if (el.offsetParent !== null) {
                                return {
                                    found: true,
                                    type: 'data-e2e',
                                    selector: el.getAttribute('data-e2e'),
                                    visible: true
                                };
                            }
                        }
                    }
                    
                    // 5. Check any element with "captcha" in class or id
                    const allElements = document.querySelectorAll('[class*="captcha" i], [id*="captcha" i]');
                    for (const el of allElements) {
                        if (el.offsetParent !== null) {
                            return {
                                found: true,
                                type: 'generic',
                                className: el.className,
                                id: el.id,
                                visible: true
                            };
                        }
                    }
                    
                    return {found: false};
                }
            """)
            
            if captcha_check['found']:
                self.captcha_type = captcha_check.get('type', 'unknown')
                self.captcha_detected_at = time.time()
                
                print(f"\n[CAPTCHA-DETECTED]")
                print(f"  profile_id: {self.profile_id}")
                print(f"  current_url: {page.url}")
                print(f"  captcha_type: {self.captcha_type}")
                print(f"  selector: {captcha_check.get('selector', 'N/A')}")
                print(f"  visible: {captcha_check.get('visible', 'N/A')}")
                print(f"  timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
                
                return True, self.captcha_type
            
            # Check URL redirect captcha
            current_url = page.url
            if any(keyword in current_url.lower() for keyword in ['/verify', '/captcha', '/security']):
                self.captcha_type = CaptchaType.REDIRECT
                self.captcha_detected_at = time.time()
                
                print(f"\n[CAPTCHA-DETECTED]")
                print(f"  profile_id: {self.profile_id}")
                print(f"  current_url: {current_url}")
                print(f"  captcha_type: {self.captcha_type}")
                print(f"  timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
                
                return True, self.captcha_type
            
            return False, None
            
        except Exception as e:
            error_msg = str(e)
            # Don't spam traceback for known errors
            if "Target page, context or browser has been closed" in error_msg or "TargetClosedError" in error_msg:
                print(f"[CAPTCHA-DETECT-ERROR] Page/browser closed - skipping captcha check")
            else:
                print(f"[CAPTCHA-DETECT-ERROR] {error_msg}")
                import traceback
                traceback.print_exc()
            return False, None
    
    async def ensure_captcha_visible(self, page) -> bool:
        """
        Đảm bảo captcha hiển thị đầy đủ (không bypass)
        
        Returns:
            bool: Success
        """
        try:
            print(f"\n[CAPTCHA-VISIBILITY] Ensuring captcha is visible...")
            
            # Bring to front
            await page.bring_to_front()
            print(f"  ✅ Page brought to front")
            
            # Check window size
            viewport = page.viewport_size
            if viewport['width'] < 900 or viewport['height'] < 700:
                print(f"  ⚠️  Window too small: {viewport['width']}x{viewport['height']}")
                print(f"  ℹ️  Captcha may not display properly")
            else:
                print(f"  ✅ Window size OK: {viewport['width']}x{viewport['height']}")
            
            return True
            
        except Exception as e:
            print(f"[CAPTCHA-VISIBILITY-ERROR] {e}")
            return False
    
    async def wait_for_captcha_resolved(self, page, timeout: int = 180) -> bool:
        """
        Chờ CAPTCHA được giải (bởi hệ thống hiện tại, không giải thay)
        
        Args:
            page: Playwright page
            timeout: Timeout in seconds
        
        Returns:
            bool: Captcha resolved
        """
        print(f"\n[CAPTCHA-WAIT] Waiting for captcha to be resolved...")
        print(f"  timeout: {timeout}s")
        print(f"  poll_interval: 2s")
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                # Check if captcha disappeared
                has_captcha, _ = await self.detect_captcha(page)
                
                if not has_captcha:
                    # Check if back to /live
                    current_url = page.url
                    if '/live' in current_url.lower():
                        self.captcha_resolved_at = time.time()
                        resolve_time_ms = int((self.captcha_resolved_at - self.captcha_detected_at) * 1000)
                        
                        print(f"\n[CAPTCHA-RESOLVED]")
                        print(f"  profile_id: {self.profile_id}")
                        print(f"  resolve_time_ms: {resolve_time_ms}")
                        print(f"  current_url: {current_url}")
                        print(f"  timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
                        
                        return True
                
                # Wait before next check
                await asyncio.sleep(2)
                
            except Exception as e:
                print(f"[CAPTCHA-WAIT-ERROR] {e}")
                await asyncio.sleep(2)
        
        print(f"\n[CAPTCHA-TIMEOUT] Captcha not resolved after {timeout}s")
        return False
    
    async def debug_page_state(self, page) -> Dict:
        """
        Debug page state sau khi captcha resolved
        
        Returns:
            Dict with page state info
        """
        try:
            state = await page.evaluate("""
                () => {
                    return {
                        readyState: document.readyState,
                        visibilityState: document.visibilityState,
                        hasFocus: document.hasFocus(),
                        webdriver: navigator.webdriver
                    };
                }
            """)
            
            print(f"\n[PAGE-STATE]")
            print(f"  profile_id: {self.profile_id}")
            print(f"  readyState: {state['readyState']}")
            print(f"  visibilityState: {state['visibilityState']}")
            print(f"  hasFocus: {state['hasFocus']}")
            print(f"  webdriver: {state['webdriver']}")
            
            return state
            
        except Exception as e:
            print(f"[PAGE-STATE-ERROR] {e}")
            return {}
    
    async def debug_video(self, page) -> Dict:
        """
        Debug video element
        
        Returns:
            Dict with video info
        """
        try:
            video_info = await page.evaluate("""
                () => {
                    const video = document.querySelector('video');
                    if (!video) {
                        return {
                            exists: false,
                            status: 'NO_VIDEO'
                        };
                    }
                    
                    const audioTracks = video.audioTracks ? video.audioTracks.length : 0;
                    
                    let status = 'VIDEO_IDLE';
                    if (video.currentTime > 0 && !video.paused) {
                        status = 'VIDEO_PLAYING';
                    }
                    
                    return {
                        exists: true,
                        readyState: video.readyState,
                        currentTime: video.currentTime,
                        paused: video.paused,
                        audioTracks: audioTracks,
                        status: status
                    };
                }
            """)
            
            print(f"\n[VIDEO-DEBUG]")
            print(f"  profile_id: {self.profile_id}")
            print(f"  video_exists: {video_info['exists']}")
            if video_info['exists']:
                print(f"  readyState: {video_info['readyState']}")
                print(f"  currentTime: {video_info['currentTime']}")
                print(f"  paused: {video_info['paused']}")
                print(f"  audioTracks: {video_info['audioTracks']}")
                print(f"  status: {video_info['status']}")
            else:
                print(f"  status: {video_info['status']}")
            
            return video_info
            
        except Exception as e:
            print(f"[VIDEO-DEBUG-ERROR] {e}")
            return {'exists': False, 'status': 'ERROR'}
    
    async def debug_websocket(self, page) -> Dict:
        """
        Debug WebSocket connections using NON-INVASIVE signals
        
        CRITICAL: WebSocket presence is REQUIRED for valid LIVE view
        
        Detection methods (2024-2025):
        1. Performance API (resource entries) - PREFERRED
        2. Network WebSocket count
        3. Runtime observation (non-intercepting)
        
        DO NOT rely on deprecated checks:
        - window.liveRoom (deprecated)
        - hardcoded global objects
        
        Returns:
            Dict with WebSocket info
        """
        try:
            ws_info = await page.evaluate("""
                () => {
                    const result = {
                        ws_detected: false,
                        ws_count: 0,
                        ws_urls: [],
                        detection_method: 'none',
                        audioContext_exists: false
                    };
                    
                    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                    // METHOD 1: Performance API (PREFERRED - Non-invasive)
                    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                    try {
                        if (window.performance && window.performance.getEntriesByType) {
                            const resources = window.performance.getEntriesByType('resource');
                            
                            for (const resource of resources) {
                                const name = resource.name || '';
                                // TikTok LIVE WebSocket patterns (2024-2025)
                                if (name.includes('webcast') || 
                                    name.includes('ws://') || 
                                    name.includes('wss://') ||
                                    name.includes('/ws/') ||
                                    name.includes('live_ws')) {
                                    result.ws_detected = true;
                                    result.ws_count++;
                                    result.ws_urls.push(name.substring(0, 100)); // Truncate
                                    result.detection_method = 'performance_api';
                                }
                            }
                        }
                    } catch (e) {
                        console.log('[WS-DEBUG] Performance API error:', e);
                    }
                    
                    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                    // METHOD 2: Check AudioContext (REQUIRED for LIVE)
                    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                    try {
                        result.audioContext_exists = (
                            typeof AudioContext !== 'undefined' || 
                            typeof webkitAudioContext !== 'undefined'
                        );
                    } catch (e) {
                        result.audioContext_exists = false;
                    }
                    
                    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                    // METHOD 3: Runtime observation (fallback)
                    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                    if (!result.ws_detected) {
                        try {
                            // Check if WebSocket constructor was called
                            // (non-invasive - just check if it exists)
                            if (typeof WebSocket !== 'undefined') {
                                // WebSocket API available (but not necessarily used)
                                result.detection_method = 'websocket_api_available';
                            }
                        } catch (e) {}
                    }
                    
                    return result;
                }
            """)
            
            print(f"\n[WEBSOCKET-DEBUG] (2024-2025 Non-invasive)")
            print(f"  profile_id: {self.profile_id}")
            print(f"  ws_detected: {ws_info['ws_detected']} {'✅' if ws_info['ws_detected'] else '❌'}")
            print(f"  ws_count: {ws_info['ws_count']}")
            print(f"  detection_method: {ws_info['detection_method']}")
            print(f"  audioContext_exists: {ws_info['audioContext_exists']} {'✅' if ws_info['audioContext_exists'] else '❌'}")
            
            if ws_info['ws_urls']:
                print(f"  ws_urls: {ws_info['ws_urls'][:2]}")  # Show first 2
            
            # ⚠️ CRITICAL WARNING
            if not ws_info['ws_detected']:
                print(f"  ⚠️  WARNING: No WebSocket detected - view will NOT be counted!")
            
            if not ws_info['audioContext_exists']:
                print(f"  ⚠️  WARNING: AudioContext missing - LIVE may not work!")
            
            return ws_info
            
        except Exception as e:
            print(f"[WEBSOCKET-DEBUG-ERROR] {e}")
            return {
                'ws_detected': False,
                'ws_count': 0,
                'audioContext_exists': False,
                'detection_method': 'error'
            }
    
    async def classify_live_state(self, page_state: Dict, video_info: Dict, ws_info: Dict) -> Tuple[str, str]:
        """
        Classify TikTok LIVE state (2024-2025)
        
        CRITICAL RULE: WebSocket presence is REQUIRED for valid LIVE view
        Video element alone is NOT sufficient
        
        Returns:
            (live_state, confidence)
        """
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # 1. Check CAPTCHA_BLOCKED
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        if self.captcha_detected_at and not self.captcha_resolved_at:
            return LiveState.CAPTCHA_BLOCKED, "high"
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # 2. Check PAGE_CONTEXT_CLOSED
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        if not page_state or page_state.get('readyState') == 'closed':
            return LiveState.PAGE_CONTEXT_CLOSED, "high"
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # 3. Check SESSION_RESTRICTED
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        if page_state.get('webdriver') == True:
            return LiveState.SESSION_RESTRICTED, "medium"
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # 4. Check LIVE_OK_WITH_WS (✅ View will be counted)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        if ws_info.get('ws_detected') and ws_info.get('audioContext_exists'):
            # Video is optional - WebSocket is the key indicator
            return LiveState.LIVE_OK_WITH_WS, "high"
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # 5. Check VIDEO_ONLY_NO_WS (❌ View NOT counted)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        if video_info.get('exists') and not ws_info.get('ws_detected'):
            # Video playing but no WebSocket = view NOT counted
            return LiveState.VIDEO_ONLY_NO_WS, "high"
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # 6. Check AGE_GATED_ROOM
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # (Would need to check for age gate UI elements)
        # For now, skip this check
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # 7. Default: UNKNOWN_LIVE_STATE
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        return LiveState.UNKNOWN_LIVE_STATE, "low"
    
    async def log_env_debug(self, page) -> Dict:
        """
        Log environment debug info (CHỈ log, KHÔNG sửa)
        
        Returns:
            Dict with env info
        """
        try:
            env_info = await page.evaluate("""
                () => {
                    const ua = navigator.userAgent;
                    const viewport = {
                        width: window.innerWidth,
                        height: window.innerHeight
                    };
                    
                    // Simple hash of UA
                    let hash = 0;
                    for (let i = 0; i < ua.length; i++) {
                        hash = ((hash << 5) - hash) + ua.charCodeAt(i);
                        hash = hash & hash;
                    }
                    
                    return {
                        ua_hash: Math.abs(hash).toString(16),
                        window_size: `${viewport.width}x${viewport.height}`,
                        webdriver: navigator.webdriver
                    };
                }
            """)
            
            print(f"\n[ENV-DEBUG]")
            print(f"  profile_id: {self.profile_id}")
            print(f"  ua_hash: {env_info['ua_hash']}")
            print(f"  window_size: {env_info['window_size']}")
            print(f"  webdriver: {env_info['webdriver']}")
            
            return env_info
            
        except Exception as e:
            print(f"[ENV-DEBUG-ERROR] {e}")
            return {}
    
    async def should_abort_profile(self, live_state: str, elapsed_seconds: float) -> bool:
        """
        Decide if profile should be aborted (FAIL FAST to save RAM)
        
        DO NOT abort immediately - prefer waiting over reloading
        
        Returns:
            bool: Should abort
        """
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # IMMEDIATE ABORT (no recovery possible)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        if live_state == LiveState.PAGE_CONTEXT_CLOSED:
            return True
        
        if live_state == LiveState.SESSION_RESTRICTED:
            return True
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # DELAYED ABORT (wait first, then abort)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        
        # CAPTCHA_BLOCKED - wait up to 180s
        if live_state == LiveState.CAPTCHA_BLOCKED:
            if elapsed_seconds > 180:
                return True
        
        # VIDEO_ONLY_NO_WS - wait up to 60s (WebSocket may initialize late)
        if live_state == LiveState.VIDEO_ONLY_NO_WS:
            if elapsed_seconds > 60:
                return True
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # DO NOT ABORT (keep running)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        if live_state == LiveState.LIVE_OK_WITH_WS:
            return False
        
        # Default: don't abort yet
        return False


async def analyze_live_state(page, profile_id: str, viewport_size: str = "unknown", ua_preserved: bool = True) -> Tuple[str, Dict]:
    """
    Complete LIVE state analysis (2024-2025)
    
    Args:
        page: Playwright page
        profile_id: Profile identifier
        viewport_size: Viewport size (e.g. "480x270")
        ua_preserved: Whether UA was preserved from login
    
    Returns:
        (live_state, debug_info)
    """
    debugger = LivestreamCaptchaDebugger(profile_id)
    
    print(f"\n{'='*70}")
    print(f"LIVE STATE ANALYSIS - {profile_id}")
    print(f"{'='*70}")
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Step 1: Page state
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    page_state = await debugger.debug_page_state(page)
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Step 2: Video
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    video_info = await debugger.debug_video(page)
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Step 3: WebSocket (CRITICAL)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    ws_info = await debugger.debug_websocket(page)
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Step 4: Classify LIVE state
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    live_state, confidence = await debugger.classify_live_state(page_state, video_info, ws_info)
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Step 5: Env debug
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    env_info = await debugger.log_env_debug(page)
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Step 6: Get RAM usage
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    try:
        import psutil
        process = psutil.Process()
        ram_mb = process.memory_info().rss / 1024 / 1024
    except:
        ram_mb = 0
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # FINAL CLASSIFICATION
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    print(f"\n{'='*70}")
    print(f"[LIVE-STATE-CLASSIFICATION]")
    print(f"{'='*70}")
    print(f"  profile_id: {profile_id}")
    print(f"  live_state: {live_state}")
    print(f"  confidence: {confidence}")
    print(f"  viewport_size: {viewport_size}")
    print(f"  ua_preserved: {ua_preserved}")
    print(f"  ram_mb: {ram_mb:.1f}")
    print(f"{'='*70}")
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # EXPLICIT WARNINGS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    if live_state == LiveState.VIDEO_ONLY_NO_WS:
        print(f"\n⚠️  WARNING: Video playing but NO WebSocket detected!")
        print(f"⚠️  This view will NOT be counted by TikTok!")
        print(f"⚠️  Possible causes:")
        print(f"    - Window size too small (need >= 480x270 for desktop, >= 360x640 for mobile)")
        print(f"    - AudioContext blocked")
        print(f"    - Session restricted")
        print(f"    - Network issues")
    
    elif live_state == LiveState.LIVE_OK_WITH_WS:
        print(f"\n✅ SUCCESS: WebSocket detected - view will be counted!")
    
    elif live_state == LiveState.CAPTCHA_BLOCKED:
        print(f"\n⚠️  CAPTCHA present - waiting for solve...")
    
    elif live_state == LiveState.SESSION_RESTRICTED:
        print(f"\n❌ ERROR: Session restricted - profile should be aborted")
    
    elif live_state == LiveState.PAGE_CONTEXT_CLOSED:
        print(f"\n❌ ERROR: Page context closed - profile should be aborted")
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Return debug info
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    debug_info = {
        'page_state': page_state,
        'video_info': video_info,
        'ws_info': ws_info,
        'env_info': env_info,
        'ram_mb': ram_mb,
        'viewport_size': viewport_size,
        'ua_preserved': ua_preserved,
        'confidence': confidence
    }
    
    return live_state, debug_info


async def debug_livestream_after_captcha(page, profile_id: str) -> Optional[str]:
    """
    Debug pipeline sau khi captcha resolved (DEPRECATED - use analyze_live_state)
    
    Returns:
        live_state or None if OK
    """
    live_state, _ = await analyze_live_state(page, profile_id)
    return live_state if live_state != LiveState.LIVE_OK_WITH_WS else None
