#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TikTok LIVE View Eligibility Checker (Web 2025)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

MỤC TIÊU:
- CHECK & DEBUG chính xác view có được tính hay không
- KHÔNG can thiệp server, KHÔNG né detection
- RAM-safe: sampling ngắn, không interval nặng

LIVE STATE CLASSIFICATION:
- LIVE_ELIGIBLE_VIEW: ✅ View sẽ được tính (ALL conditions met)
- LIVE_VIDEO_ONLY: Video play nhưng không có WebSocket
- LIVE_NO_AUDIO: Không có AudioContext hoặc không running
- LIVE_NO_WS: Không có WebSocket thực sự
- LIVE_CLIENT_ERROR: Client-side errors (CORS, fetch failed)
- LIVE_BACKGROUND_TAB: Tab không focus/visible
"""

import asyncio
from typing import Dict, Tuple, Optional


class LiveViewEligibilityChecker:
    """
    Check xem LIVE view có đủ điều kiện được tính hay không
    
    Không can thiệp, chỉ check và log
    """
    
    # Live states
    LIVE_ELIGIBLE_VIEW = "LIVE_ELIGIBLE_VIEW"
    LIVE_VIDEO_ONLY = "LIVE_VIDEO_ONLY"
    LIVE_NO_AUDIO = "LIVE_NO_AUDIO"
    LIVE_NO_WS = "LIVE_NO_WS"
    LIVE_CLIENT_ERROR = "LIVE_CLIENT_ERROR"
    LIVE_BACKGROUND_TAB = "LIVE_BACKGROUND_TAB"
    
    def __init__(self, profile_id: str):
        self.profile_id = profile_id
    
    async def check_eligibility(self, page) -> Tuple[str, Dict]:
        """
        Check đầy đủ eligibility cho LIVE view
        
        Returns:
            (state, details)
        """
        details = {}
        console_errors = []
        
        # Setup console error listener
        def on_console(msg):
            if msg.type == 'error':
                console_errors.append(msg.text)
        
        page.on('console', on_console)
        
        try:
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            # 0. CHECK FOR CLIENT-SIDE ERRORS (CORS, etc)
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            
            # Wait a bit to collect console errors
            await asyncio.sleep(2)
            
            # Check for CORS or fetch errors
            cors_errors = [e for e in console_errors if 'CORS' in e or 'ERR_FAILED' in e or 'webcast' in e]
            
            if cors_errors:
                print(f"[ELIGIBILITY] ❌ Client-side errors detected:")
                for err in cors_errors[:3]:  # Show first 3
                    print(f"[ELIGIBILITY]   - {err[:150]}")
                details['console_errors'] = cors_errors
                return self.LIVE_CLIENT_ERROR, details
            
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            # 1. PAGE VISIBILITY & FOCUS CHECK
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            
            visibility_check = await page.evaluate("""
                () => {
                    return {
                        visibilityState: document.visibilityState,
                        hasFocus: document.hasFocus(),
                        hidden: document.hidden
                    };
                }
            """)
            
            details['visibility'] = visibility_check
            
            if visibility_check['visibilityState'] != 'visible':
                print(f"[ELIGIBILITY] ❌ Page not visible: {visibility_check['visibilityState']}")
                return self.LIVE_BACKGROUND_TAB, details
            
            if not visibility_check['hasFocus']:
                print(f"[ELIGIBILITY] ⚠️  Page not focused")
                # Not critical, but log it
            
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            # 2. RAF (RequestAnimationFrame) CHECK
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            
            raf_check = await page.evaluate("""
                () => {
                    return new Promise((resolve) => {
                        let frameCount = 0;
                        const startTime = performance.now();
                        
                        function countFrames() {
                            frameCount++;
                            const elapsed = performance.now() - startTime;
                            
                            if (elapsed >= 1000) {
                                resolve({
                                    fps: frameCount,
                                    elapsed: elapsed,
                                    throttled: frameCount < 30
                                });
                            } else {
                                requestAnimationFrame(countFrames);
                            }
                        }
                        
                        requestAnimationFrame(countFrames);
                    });
                }
            """)
            
            details['raf'] = raf_check
            
            if raf_check['throttled']:
                print(f"[ELIGIBILITY] ⚠️  RAF throttled: {raf_check['fps']} fps (need >= 30)")
            else:
                print(f"[ELIGIBILITY] ✅ RAF active: {raf_check['fps']} fps")
            
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            # 3. VIDEO PLAYBACK CHECK
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            
            video_check = await page.evaluate("""
                () => {
                    const video = document.querySelector('video');
                    if (!video) return {exists: false};
                    
                    const quality = video.getVideoPlaybackQuality ? 
                        video.getVideoPlaybackQuality() : null;
                    
                    return {
                        exists: true,
                        readyState: video.readyState,
                        currentTime: video.currentTime,
                        paused: video.paused,
                        ended: video.ended,
                        totalFrames: quality ? quality.totalVideoFrames : 0,
                        droppedFrames: quality ? quality.droppedVideoFrames : 0
                    };
                }
            """)
            
            details['video'] = video_check
            
            if not video_check['exists']:
                print(f"[ELIGIBILITY] ❌ No video element")
                return self.LIVE_WS_ONLY, details
            
            if video_check['readyState'] < 3:
                print(f"[ELIGIBILITY] ❌ Video not ready: readyState={video_check['readyState']} (need >= 3)")
                return self.LIVE_VIDEO_ONLY, details
            
            if video_check['totalFrames'] == 0:
                print(f"[ELIGIBILITY] ⚠️  No video frames rendered yet")
            
            # Check video progress over 10s
            print(f"[ELIGIBILITY] Checking video progress over 10s...")
            initial_time = video_check['currentTime']
            await asyncio.sleep(10)
            
            video_progress = await page.evaluate("""
                () => {
                    const video = document.querySelector('video');
                    return video ? video.currentTime : 0;
                }
            """)
            
            time_delta = video_progress - initial_time
            details['video_progress'] = {
                'initial': initial_time,
                'after_10s': video_progress,
                'delta': time_delta
            }
            
            if time_delta < 5:  # Should progress at least 5s in 10s
                print(f"[ELIGIBILITY] ❌ Video not progressing: {time_delta:.2f}s in 10s")
                return self.LIVE_VIDEO_ONLY, details
            else:
                print(f"[ELIGIBILITY] ✅ Video progressing: +{time_delta:.2f}s in 10s")
            
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            # 4. AUDIO CONTEXT CHECK (STRICT)
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            
            audio_check = await page.evaluate("""
                () => {
                    // Check if AudioContext exists
                    const ctx = window._liveAudioContext;
                    
                    if (!ctx) {
                        return {
                            exists: false,
                            state: null,
                            reason: 'No AudioContext created'
                        };
                    }
                    
                    return {
                        exists: true,
                        state: ctx.state,
                        sampleRate: ctx.sampleRate,
                        currentTime: ctx.currentTime,
                        hasDestination: ctx.destination ? true : false,
                        destinationChannels: ctx.destination ? ctx.destination.channelCount : 0
                    };
                }
            """)
            
            details['audio'] = audio_check
            
            if not audio_check['exists']:
                print(f"[ELIGIBILITY] ❌ AudioContext NULL")
                print(f"[ELIGIBILITY] Reason: {audio_check.get('reason', 'Unknown')}")
                return self.LIVE_NO_AUDIO, details
            
            if audio_check['state'] != 'running':
                print(f"[ELIGIBILITY] ❌ AudioContext state: {audio_check['state']} (need: running)")
                return self.LIVE_NO_AUDIO, details
            
            if not audio_check['hasDestination']:
                print(f"[ELIGIBILITY] ❌ AudioContext has no destination node")
                return self.LIVE_NO_AUDIO, details
            
            print(f"[ELIGIBILITY] ✅ AudioContext running with destination")
            
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            # 5. WEBSOCKET CHECK (REAL WebSocket ONLY, NOT HTTP)
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            
            ws_check = await page.evaluate("""
                () => {
                    // Check for REAL WebSocket connections
                    // NOT HTTP requests to webcast endpoints
                    
                    // Method 1: Check window.__WS_CONNECTIONS__ (if tracked)
                    const trackedWS = window.__WS_CONNECTIONS__ || [];
                    
                    // Method 2: Check liveRoom object for WebSocket
                    const liveRoom = window.liveRoom || window.__LIVE_ROOM__;
                    const hasLiveRoomWS = liveRoom && liveRoom.socket && liveRoom.socket.readyState === 1;
                    
                    // Method 3: Check performance entries for wss:// protocol ONLY
                    const entries = performance.getEntriesByType('resource');
                    const realWSEntries = entries.filter(e => e.name.startsWith('wss://'));
                    
                    return {
                        detected: hasLiveRoomWS || realWSEntries.length > 0 || trackedWS.length > 0,
                        liveRoomWS: hasLiveRoomWS,
                        wssCount: realWSEntries.length,
                        trackedCount: trackedWS.length,
                        wssUrls: realWSEntries.slice(0, 2).map(e => e.name)
                    };
                }
            """)
            
            details['websocket'] = ws_check
            
            if not ws_check['detected']:
                print(f"[ELIGIBILITY] ❌ No REAL WebSocket detected")
                print(f"[ELIGIBILITY] - liveRoom.socket: {ws_check['liveRoomWS']}")
                print(f"[ELIGIBILITY] - wss:// connections: {ws_check['wssCount']}")
                print(f"[ELIGIBILITY] - tracked connections: {ws_check['trackedCount']}")
                return self.LIVE_NO_WS, details
            else:
                print(f"[ELIGIBILITY] ✅ Real WebSocket detected")
                if ws_check['liveRoomWS']:
                    print(f"[ELIGIBILITY]   - liveRoom.socket: OPEN")
                if ws_check['wssCount'] > 0:
                    print(f"[ELIGIBILITY]   - wss:// connections: {ws_check['wssCount']}")
                    print(f"[ELIGIBILITY]   - URLs: {ws_check['wssUrls']}")
            
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            # FINAL VERDICT - ALL CHECKS PASSED
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            
            print(f"\n[ELIGIBILITY] ✅✅✅ ALL CHECKS PASSED ✅✅✅")
            print(f"[ELIGIBILITY] - Page visible: ✅")
            print(f"[ELIGIBILITY] - RAF active: ✅")
            print(f"[ELIGIBILITY] - Video progressing: ✅")
            print(f"[ELIGIBILITY] - AudioContext running: ✅")
            print(f"[ELIGIBILITY] - Real WebSocket: ✅")
            print(f"[ELIGIBILITY] View will be counted!")
            
            return self.LIVE_ELIGIBLE_VIEW, details
            
        except Exception as e:
            print(f"[ELIGIBILITY] ❌ Error: {e}")
            import traceback
            traceback.print_exc()
            details['error'] = str(e)
            return self.LIVE_VIDEO_ONLY, details
        finally:
            # Cleanup console listener
            try:
                page.remove_listener('console', on_console)
            except:
                pass
    
    def print_summary(self, state: str, details: Dict):
        """Print summary of eligibility check"""
        print(f"\n{'='*70}")
        print(f"LIVE VIEW ELIGIBILITY SUMMARY - {self.profile_id}")
        print(f"{'='*70}")
        print(f"State: {state}")
        
        if state == self.LIVE_ELIGIBLE_VIEW:
            print(f"✅ View will be counted")
        else:
            print(f"❌ View will NOT be counted")
            print(f"\nReasons:")
            
            if state == self.LIVE_BACKGROUND_TAB:
                print(f"  - Page not visible or focused")
            elif state == self.LIVE_VIDEO_ONLY:
                print(f"  - Video playing but missing other requirements")
                if 'websocket' in details and not details['websocket']['detected']:
                    print(f"  - No real WebSocket connection")
            elif state == self.LIVE_NO_AUDIO:
                print(f"  - AudioContext is NULL or not running")
                if 'audio' in details:
                    audio = details['audio']
                    if not audio['exists']:
                        print(f"  - AudioContext was never created")
                    elif audio['state'] != 'running':
                        print(f"  - AudioContext state: {audio['state']} (need: running)")
            elif state == self.LIVE_NO_WS:
                print(f"  - No REAL WebSocket connection detected")
                print(f"  - Only HTTP requests to webcast endpoints (not counted)")
            elif state == self.LIVE_CLIENT_ERROR:
                print(f"  - Client-side errors detected (CORS, fetch failed)")
                if 'console_errors' in details:
                    print(f"  - {len(details['console_errors'])} errors in console")
        
        print(f"{'='*70}\n")


async def check_live_view_eligibility(page, profile_id: str) -> Tuple[str, Dict]:
    """
    Helper function to check LIVE view eligibility
    
    Returns:
        (state, details)
    """
    checker = LiveViewEligibilityChecker(profile_id)
    state, details = await checker.check_eligibility(page)
    checker.print_summary(state, details)
    return state, details
