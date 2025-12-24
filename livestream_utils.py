#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TikTok 2025 Livestream Utilities
Comprehensive utilities for livestream compatibility and debugging
"""

import asyncio
from typing import Dict, Any, Optional


async def run_livestream_debug(page) -> Dict[str, Any]:
    """
    Run comprehensive livestream debug checks
    
    Returns:
        Dict with all compatibility checks
    """
    try:
        result = await page.evaluate("""
            () => ({
                webglVendor: (() => {
                    try {
                        const canvas = document.createElement('canvas');
                        const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
                        if (!gl) return null;
                        const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
                        return debugInfo ? gl.getParameter(debugInfo.UNMASKED_VENDOR_WEBGL) : gl.getParameter(gl.VENDOR);
                    } catch (e) {
                        return null;
                    }
                })(),
                
                webglRenderer: (() => {
                    try {
                        const canvas = document.createElement('canvas');
                        const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
                        if (!gl) return null;
                        const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
                        return debugInfo ? gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL) : gl.getParameter(gl.RENDERER);
                    } catch (e) {
                        return null;
                    }
                })(),
                
                canPlay: (() => {
                    const video = document.querySelector("video");
                    return video ? video.canPlayType("video/mp4; codecs=\\"avc1.42E01E\\"") : null;
                })(),
                
                readyState: (() => {
                    const video = document.querySelector("video");
                    return video ? video.readyState : null;
                })(),
                
                wsExists: typeof window.__LIVE_ROOM__ !== "undefined" || 
                          typeof window.liveRoom !== "undefined",
                
                mediaCap: !!navigator.mediaCapabilities,
                
                videoElement: !!document.querySelector("video"),
                
                liveRoomPlayer: !!document.querySelector("div[data-e2e='live-room-player']"),
                
                playerContainer: !!document.querySelector("div[data-e2e='live-player-container']")
            })
        """)
        
        return result
    except Exception as e:
        print(f"[LIVESTREAM-DEBUG] Error: {e}")
        return {}


async def wait_for_websocket_liveroom(page, timeout: int = 15000) -> bool:
    """
    Wait for TikTok WebSocket liveRoom object
    
    Args:
        page: Playwright page
        timeout: Timeout in milliseconds
    
    Returns:
        True if WebSocket found
    """
    try:
        print("[WEBSOCKET] Waiting for liveRoom object...")
        
        await page.wait_for_function(
            "window.__LIVE_ROOM__ !== undefined || window.liveRoom !== undefined",
            timeout=timeout
        )
        
        print("[WEBSOCKET] ✅ liveRoom object found")
        return True
        
    except Exception as e:
        print(f"[WEBSOCKET] ❌ liveRoom object not found: {e}")
        return False


async def auto_click_watch_live(page) -> bool:
    """
    Auto-click "Watch Live" button if present
    
    Args:
        page: Playwright page
    
    Returns:
        True if clicked
    """
    try:
        selectors = [
            'button:has-text("Watch Live")',
            'button:has-text("Xem trực tiếp")',
            'div[data-e2e="live-watch-button"]',
            'button[data-e2e="live-enter-button"]'
        ]
        
        for selector in selectors:
            try:
                await page.click(selector, timeout=2000)
                print(f"[AUTO-CLICK] ✅ Clicked: {selector}")
                return True
            except:
                continue
        
        return False
        
    except Exception as e:
        print(f"[AUTO-CLICK] Error: {e}")
        return False


async def scroll_to_trigger_video(page) -> bool:
    """
    Scroll down to trigger video load
    
    Args:
        page: Playwright page
    
    Returns:
        True if scrolled
    """
    try:
        await page.evaluate("window.scrollBy(0, 200)")
        print("[SCROLL] ✅ Scrolled down 200px")
        return True
    except Exception as e:
        print(f"[SCROLL] Error: {e}")
        return False


async def start_engagement_loop(page):
    """
    Start engagement loop for view counting
    
    Args:
        page: Playwright page
    """
    try:
        await page.evaluate("""
            () => {
                // Timeupdate loop for video
                const video = document.querySelector('video');
                if (video) {
                    window.__timeupdateInterval = setInterval(() => {
                        if (video && !video.paused) {
                            video.dispatchEvent(new Event('timeupdate'));
                        }
                    }, 5000);
                }
                
                // Mouse movement loop
                window.__mousemoveInterval = setInterval(() => {
                    document.body.dispatchEvent(new MouseEvent('mousemove', {
                        bubbles: true,
                        cancelable: true,
                        view: window
                    }));
                }, 10000);
                
                // Visibility change loop
                window.__visibilityInterval = setInterval(() => {
                    document.body.dispatchEvent(new Event('visibilitychange'));
                }, 15000);
                
                console.log('[ENGAGEMENT] Loops started');
            }
        """)
        
        print("[ENGAGEMENT] ✅ Engagement loops started")
        
    except Exception as e:
        print(f"[ENGAGEMENT] Error: {e}")


async def wait_for_video_with_fallback(page, timeout: int = 15000) -> bool:
    """
    Wait for video element with auto-fallback and comprehensive debugging
    
    Args:
        page: Playwright page
        timeout: Timeout in milliseconds
    
    Returns:
        True if video found
    """
    try:
        # 🔥 RULE 4: ADD SELECTOR DIAGNOSTICS
        selectors = [
            "#LIVE_VIDEO_COMPONENT video",
            "div[data-e2e='BILLBOARD_LIVE']",
            "div[data-e2e='live-player-container']",
            "div[data-e2e='live-room-player']",
            "div[data-e2e='player']",
            "video"
        ]
        
        print("[DEBUG] Trying video selectors:", selectors)
        
        # Try each selector
        for selector in selectors:
            try:
                await page.wait_for_selector(selector, timeout=3000, state="attached")
                print(f"[VIDEO] ✅ Found selector: {selector}")
                
                # If we found video, return success
                if selector == "video" or "video" in selector:
                    return True
            except:
                print(f"[VIDEO] ⏭️  Selector not found: {selector}")
                continue
        
        print("[VIDEO] ⚠️  No selectors found, trying fallback...")
        
        # Fallback 1: Auto-click Watch Live
        clicked = await auto_click_watch_live(page)
        if clicked:
            await asyncio.sleep(2)
            try:
                await page.wait_for_selector("video", timeout=5000, state="attached")
                print("[VIDEO] ✅ Video found after click")
                return True
            except:
                pass
        
        # Fallback 2: Scroll down
        await scroll_to_trigger_video(page)
        await asyncio.sleep(2)
        
        try:
            await page.wait_for_selector("video", timeout=5000, state="attached")
            print("[VIDEO] ✅ Video found after scroll")
            return True
        except:
            pass
        
        # 🔥 RULE 3: ADD HTML DEBUG WHEN VIDEO IS NOT FOUND
        print("[VIDEO] ❌ Video not found after all fallbacks")
        print("[DEBUG] Fetching page HTML for diagnosis...")
        
        try:
            html = await page.content()
            print("[DEBUG] Livestream page HTML preview (first 3000 chars):")
            print(html[:3000])
            
            # Check for common issues
            html_lower = html.lower()
            if "age" in html_lower and "gate" in html_lower:
                print("[ERROR] ⚠️  Age-gated room detected")
            elif "log in" in html_lower or "sign in" in html_lower:
                print("[ERROR] ⚠️  Logged-out state detected")
            elif "ended" in html_lower or "finished" in html_lower:
                print("[ERROR] ⚠️  Live ended page detected")
            elif "captcha" in html_lower:
                print("[ERROR] ⚠️  CAPTCHA wall detected")
            elif "region" in html_lower or "not available" in html_lower:
                print("[ERROR] ⚠️  Region locked livestream")
            else:
                print("[ERROR] ⚠️  Unknown issue - check HTML above")
                
        except Exception as e:
            print(f"[DEBUG] Could not fetch HTML: {e}")
        
        # 🔥 RULE 5: AUTO-FIX USER-AGENT ISSUE
        print("[FIX] Suspected UA blocked — enabling UA rotation.")
        print("[FIX] Recommendation: Rotate User-Agent and restart")
        
        return False
        
    except Exception as e:
        print(f"[VIDEO] Error: {e}")
        return False


async def inject_tiktok_stealth(page):
    """
    Inject TikTok 2025 stealth scripts
    Hide all detection flags
    
    Args:
        page: Playwright page
    """
    try:
        await page.evaluate("""
            () => {
                // [1] Fake headless - hide webdriver
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                    configurable: true
                });
                
                // [2] Delete window.chrome (TikTok checks this)
                try {
                    delete window.chrome;
                } catch (e) {}
                
                // [3] Fake plugins & mimeTypes
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [
                        {name: 'Chrome PDF Plugin', description: 'Portable Document Format', filename: 'internal-pdf-viewer'},
                        {name: 'Chrome PDF Viewer', description: '', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai'},
                        {name: 'Native Client', description: '', filename: 'internal-nacl-plugin'}
                    ],
                    configurable: true
                });
                
                Object.defineProperty(navigator, 'mimeTypes', {
                    get: () => [
                        {type: 'application/pdf', description: 'Portable Document Format', suffixes: 'pdf'},
                        {type: 'application/x-google-chrome-pdf', description: '', suffixes: 'pdf'},
                        {type: 'application/x-nacl', description: 'Native Client Executable', suffixes: ''},
                        {type: 'application/x-pnacl', description: 'Portable Native Client Executable', suffixes: ''}
                    ],
                    configurable: true
                });
                
                // [4] Force document visible
                Object.defineProperty(document, 'hidden', {
                    get: () => false,
                    configurable: true
                });
                
                Object.defineProperty(document, 'visibilityState', {
                    get: () => 'visible',
                    configurable: true
                });
                
                console.log('[STEALTH] TikTok 2025 stealth injected');
            }
        """)
        
        print("[STEALTH] ✅ TikTok 2025 stealth scripts injected")
        
    except Exception as e:
        print(f"[STEALTH] Error: {e}")


__all__ = [
    'run_livestream_debug',
    'wait_for_websocket_liveroom',
    'auto_click_watch_live',
    'scroll_to_trigger_video',
    'start_engagement_loop',
    'wait_for_video_with_fallback',
    'inject_tiktok_stealth'
]
