#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 LAUNCH LIVESTREAM TIKTOK - STEALTH 2025 VERSION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

UPGRADED WITH TIKTOK STEALTH 2025:
✅ Full Anti-Detection (navigator.webdriver, WebGL, permissions, chrome.runtime)
✅ Remove Dangerous Flags (--new, --enable-features=FakeSignIn, etc.)
✅ Anti Blank Page Recovery
✅ Configurable Window Sizes (320x540 → 1280x720, 1x1)
✅ Mobile Mode Support
✅ UA Preservation for Logged-in Profiles
✅ RAM Optimization (150-200MB per profile)
✅ Livestream Mode (GPU WebGL ON + Audio enabled)

TARGET: 150-200MB RAM per profile, 60-80 profiles on 16GB RAM
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import os
import sys
import time
import asyncio
import psutil
import configparser
import json
from pathlib import Path
from typing import List, Optional, Dict
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.getcwd())

# Import STEALTH 2025 system
from core.managers.browser_manager_stealth_2025 import BrowserManagerStealth2025
from core.managers.profile_manager import ProfileManager
from core.managers.proxy_manager import ProxyManager
from core.playwright_stealth_2025 import WINDOW_SIZES

# Import captcha solver
from core.omocaptcha_client import OMOcaptchaClient
from core.tiktok_captcha_solver_playwright import TikTokCaptchaSolverPlaywright

# Import livestream captcha debugger
from core.livestream_captcha_debug import (
    LivestreamCaptchaDebugger,
    debug_livestream_after_captcha
)

# Import RAM monitor
try:
    from system_monitor.ram_monitor import start_ram_monitor, stop_ram_monitor
    RAM_MONITOR_AVAILABLE = True
except ImportError:
    RAM_MONITOR_AVAILABLE = False
    print("[WARNING] RAM monitor not available - install system_monitor module")


class FullDebugLogger:
    """Full debug logger for tracking everything during livestream launch"""
    
    def __init__(self, profile_id: str):
        self.profile_id = profile_id
        self.logs = {
            'system': [],
            'network': [],
            'websocket': [],
            'console': [],
            'performance': [],
            'video_stats': [],
            'audio_stats': [],
            'live_join': [],
            'errors': []
        }
        self.enabled = False
        
    def enable(self):
        """Enable full debug logging"""
        self.enabled = True
        print(f"[FULL-DEBUG] ✅ Enabled for {self.profile_id}")
        
    def log(self, category: str, data: str):
        """Log data to category"""
        if not self.enabled:
            return
        
        # Safety check - create category if not exists
        if category not in self.logs:
            self.logs[category] = []
            
        timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
        entry = {'time': timestamp, 'data': data}
        self.logs[category].append(entry)
        print(f"   [DEBUG-{category.upper()}] [{timestamp}] {data}")
        
    def save(self):
        """Save logs to JSON file"""
        if not self.enabled or not any(self.logs.values()):
            return
            
        filename = f'full_debug_{self.profile_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.logs, f, indent=2, ensure_ascii=False)
            print(f"   [FULL-DEBUG] ✅ Saved: {filename}")
        except Exception as e:
            print(f"   [FULL-DEBUG] ⚠️  Save error: {e}")
    
    async def setup_monitoring(self, page):
        """Setup all monitoring hooks on page"""
        if not self.enabled:
            return
            
        try:
            # Network monitoring
            async def on_request(request):
                url = request.url
                if 'tiktok.com' in url or 'webcast' in url:
                    self.log('network', f"→ {request.method} {url[:100]}")
            
            async def on_response(response):
                url = response.url
                if 'tiktok.com' in url or 'webcast' in url:
                    self.log('network', f"← {response.status} {url[:100]}")
                    
                    # Log important API responses
                    if '/room/enter' in url or '/room/info' in url:
                        try:
                            data = await response.json()
                            self.log('network', f"API: {json.dumps(data, indent=2)[:300]}")
                        except:
                            pass
            
            page.on('request', on_request)
            page.on('response', on_response)
            
            # Console monitoring
            def on_console(msg):
                self.log('console', f"{msg.type}: {msg.text}")
            
            page.on('console', on_console)
            
            # WebSocket monitoring
            def on_websocket(ws):
                self.log('websocket', f"Opened: {ws.url}")
                
                ws.on('framesent', lambda payload: 
                    self.log('websocket', f"→ Sent: {str(payload)[:150]}"))
                
                ws.on('framereceived', lambda payload: 
                    self.log('websocket', f"← Received: {str(payload)[:150]}"))
                
                ws.on('close', lambda: 
                    self.log('websocket', 'Closed'))
            
            page.on('websocket', on_websocket)
            
            print(f"   [FULL-DEBUG] ✅ Monitoring setup complete")
            
        except Exception as e:
            self.log('errors', f"Setup monitoring error: {e}")
    
    async def log_detailed_stats(self, page):
        """Log detailed video/audio/performance stats"""
        if not self.enabled:
            return
            
        try:
            # Video stats
            video_stats = await page.evaluate("""() => {
                const video = document.querySelector('video');
                if (!video) return null;
                
                return {
                    readyState: video.readyState,
                    currentTime: video.currentTime,
                    duration: video.duration,
                    paused: video.paused,
                    muted: video.muted,
                    volume: video.volume,
                    buffered: video.buffered.length > 0 ? video.buffered.end(0) : 0,
                    videoWidth: video.videoWidth,
                    videoHeight: video.videoHeight,
                    playbackRate: video.playbackRate
                };
            }""")
            
            if video_stats:
                self.log('video_stats', json.dumps(video_stats))
            
            # Audio stats
            audio_stats = await page.evaluate("""() => {
                const ctx = window._liveAudioContext;
                if (!ctx) return null;
                
                return {
                    state: ctx.state,
                    currentTime: ctx.currentTime,
                    sampleRate: ctx.sampleRate,
                    baseLatency: ctx.baseLatency || 0
                };
            }""")
            
            if audio_stats:
                self.log('audio_stats', json.dumps(audio_stats))
            
            # Performance stats
            perf_stats = await page.evaluate("""() => {
                return {
                    memory: performance.memory ? {
                        usedJSHeapSize: Math.round(performance.memory.usedJSHeapSize / 1024 / 1024),
                        totalJSHeapSize: Math.round(performance.memory.totalJSHeapSize / 1024 / 1024)
                    } : null
                };
            }""")
            
            if perf_stats and perf_stats['memory']:
                self.log('performance', json.dumps(perf_stats))
                
        except Exception as e:
            self.log('errors', f"Stats logging error: {e}")


class Stealth2025LivestreamLauncher:
    """
    TikTok Livestream Launcher with Stealth 2025
    
    Features:
    - Full anti-detection (navigator.webdriver, WebGL, permissions)
    - Remove dangerous Chrome flags
    - Anti blank page recovery
    - Configurable window sizes
    - Mobile mode support
    - UA preservation
    - RAM optimization (150-200MB per profile)
    - Livestream mode (GPU + Audio)
    - Captcha auto-solve
    """
    
    def __init__(self):
        # Initialize managers
        self.profile_manager = ProfileManager()
        self.proxy_manager = ProxyManager(self.profile_manager)
        self.browser_manager = BrowserManagerStealth2025(
            self.profile_manager,
            self.proxy_manager
        )
        
        self.launched_profiles = []
        self.loop = None
        self.ram_monitor_task = None
        
        # Initialize captcha solver
        self.captcha_solver = None
        self.captcha_solver_type = None  # 'v2' or 'playwright'
        self._init_captcha_solver()
        
        # Profile tracking
        self.profile_info = {}  # {profile_name: {ua, gpu, viewport, ram, pid}}
        
        # Full debug mode
        self.full_debug_mode = False
        
        print("\n" + "="*70)
        print("🛡️  TIKTOK LIVESTREAM LAUNCHER - STEALTH 2025")
        print("="*70)
        print("✅ Anti-Detection: Full (webdriver, WebGL, permissions)")
        print("✅ Dangerous Flags: Removed")
        print("✅ Window Sizes: Configurable (1x1 → 1280x720)")
        print("✅ Mobile Mode: Supported")
        print("✅ UA Preservation: Automatic")
        print("✅ RAM Optimization: 150-200MB per profile")
        print("✅ Captcha Solver: " + (f"Enabled ({self.captcha_solver_type})" if self.captcha_solver else "Disabled"))
        print("✅ RAM Monitor: " + ("Available" if RAM_MONITOR_AVAILABLE else "Not available"))
        print("="*70 + "\n")
    
    def _init_captcha_solver(self):
        """Initialize captcha solver from config"""
        try:
            config = configparser.ConfigParser()
            config.read('config.ini')
            
            api_key = config.get('CAPTCHA', 'omocaptcha_api_key', fallback='')
            
            if api_key and api_key.strip():
                print(f"[CAPTCHA] ✅ OMOcaptcha API key loaded")
                omocaptcha_client = OMOcaptchaClient(api_key=api_key.strip())
                
                # Use V2 solver (HTML-based) like bulk run - more reliable
                try:
                    from core.tiktok_captcha_solver_v2 import TikTokCaptchaSolverV2
                    self.captcha_solver = TikTokCaptchaSolverV2(
                        omocaptcha_client,
                        debug_level="INFO",
                        artifacts_dir="logs/captcha_livestream"
                    )
                    self.captcha_solver_type = "V2-HTML"
                    print(f"[CAPTCHA] ✅ Using V2 solver (HTML-based, same as bulk run)")
                except ImportError:
                    # Fallback to Playwright solver
                    self.captcha_solver = TikTokCaptchaSolverPlaywright(omocaptcha_client)
                    self.captcha_solver_type = "Playwright"
                    print(f"[CAPTCHA] ⚠️  V2 not available, using Playwright solver")
            else:
                print(f"[CAPTCHA] ⚠️  No API key - captcha auto-solve disabled")
        except Exception as e:
            print(f"[CAPTCHA] ⚠️  Failed to load: {e}")
    
    def get_all_profiles(self):
        """Get all profiles"""
        return self.profile_manager.get_all_profiles()
    
    def kill_all_chrome(self):
        """Kill all Chrome processes"""
        try:
            print("\n" + "=" * 70)
            print("KILLING ALL CHROME PROCESSES")
            print("=" * 70)
            
            killed_count = 0
            chrome_processes = []
            
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    proc_name = proc.info['name'].lower()
                    if 'chrome' in proc_name or 'chromium' in proc_name:
                        chrome_processes.append(proc)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            if not chrome_processes:
                print("\n✅ No Chrome processes running")
                return True
            
            print(f"\nFound {len(chrome_processes)} Chrome processes")
            
            for proc in chrome_processes:
                try:
                    proc.terminate()
                    killed_count += 1
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            time.sleep(2)
            
            for proc in chrome_processes:
                try:
                    if proc.is_running():
                        proc.kill()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            print(f"\n✅ Killed {killed_count} Chrome processes")
            print("=" * 70)
            
            return True
            
        except Exception as e:
            print(f"\n❌ Error killing Chrome: {e}")
            return False
    
    async def launch_profile_async(
        self,
        profile_name: str,
        url: str,
        window_size: str = "1x1",
        mobile_mode: bool = False,
        force_headless: bool = False,
        max_retries: int = 3
    ):
        """
        Launch single profile with Stealth 2025
        
        Args:
            profile_name: Profile name
            url: TikTok livestream URL
            window_size: Window size (e.g. "1x1", "360x640", "mobile_medium")
            mobile_mode: Use mobile mode
            force_headless: Force headless (not recommended for livestream)
            max_retries: Max retry attempts
        
        Returns:
            bool: Success status
        """
        # Initialize debug logger
        debug_logger = FullDebugLogger(profile_name)
        if self.full_debug_mode:
            debug_logger.enable()
            print(f"[DEBUG-CHECK] Full debug enabled for {profile_name}")
            debug_logger.log('system', 'Debug logger initialized')
            print(f"[DEBUG-CHECK] Logged first message")
        
        last_error = None
        
        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    print(f"   Retry {attempt}/{max_retries-1}...")
                    wait_time = 2 ** attempt
                    await asyncio.sleep(wait_time)
                
                # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                # CONTEXTUAL LIVESTREAM ENTRY (2025 REQUIREMENT)
                # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                # WHY: TikTok requires profile-context entry for view counting
                # WHAT: Navigate to profile → Detect LIVE badge → Enter livestream
                # NOT: Direct /live URL navigation (classified as bot-like)
                
                print(f"   [ENTRY-FLOW] Using PROFILE-CONTEXT entry (2025 requirement)")
                print(f"   [WINDOW] Size: {window_size}")
                print(f"   [MODE] Mobile: {mobile_mode} | Headless: {force_headless}")
                
                # Extract username from livestream URL
                import re
                username_match = re.search(r'@([^/]+)', url)
                if not username_match:
                    last_error = "Cannot extract username from URL"
                    print(f"   ❌ {last_error}")
                    debug_logger.log('errors', last_error)
                    if attempt < max_retries - 1:
                        continue
                    else:
                        debug_logger.save()
                        return False
                
                username = username_match.group(1)
                profile_url = f"https://www.tiktok.com/@{username}"
                
                print(f"   [STEP 1] Navigating to profile: @{username}")
                
                # Launch browser with PROFILE URL (not live URL)
                page = await self.browser_manager.launch_profile_stealth(
                    profile_name=profile_name,
                    url=profile_url,  # ← PROFILE URL, not live URL
                    window_size=window_size,
                    mobile_mode=mobile_mode,
                    force_headless=force_headless,
                    ultra_low_ram=True
                )
                
                if not page:
                    last_error = "Failed to launch profile"
                    debug_logger.log('errors', f"Launch failed: {last_error}")
                    if attempt < max_retries - 1:
                        continue
                    else:
                        debug_logger.save()
                        return False
                
                print(f"   ✅ Browser launched with profile page")
                debug_logger.log('entry_flow', 'PROFILE_LOADED')
                
                # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                # STEP 2: CAPTCHA DETECTION & RESOLUTION (CRITICAL)
                # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                # WHY: Captcha MUST be solved before any LIVE detection
                # WHAT: Detect captcha → Wait for resolution → Verify profile stable
                
                print(f"   [STEP 2] Checking for captcha...")
                
                # Check for captcha
                has_captcha = await page.evaluate("""
                    () => {
                        const captchaSelectors = [
                            'iframe[src*="captcha"]',
                            '[class*="captcha"]',
                            '[id*="captcha"]',
                            '.secsdk-captcha-wrapper',
                            '[data-e2e="captcha"]'
                        ];
                        
                        for (const sel of captchaSelectors) {
                            const elem = document.querySelector(sel);
                            if (elem && elem.offsetParent !== null) {
                                return {
                                    found: true,
                                    selector: sel
                                };
                            }
                        }
                        
                        return {found: false};
                    }
                """)
                
                if has_captcha.get('found'):
                    print(f"   ⚠️  CAPTCHA detected")
                    debug_logger.log('entry_flow', 'CAPTCHA_DETECTED')
                    
                    # Use existing captcha solver
                    from core.livestream_captcha_debug import LivestreamCaptchaDebugger
                    debugger = LivestreamCaptchaDebugger(profile_name)
                    
                    captcha_solved = False
                    
                    if self.captcha_solver:
                        print(f"   [CAPTCHA] Trying API ({self.captcha_solver_type}, 10 attempts)...")
                        try:
                            solution = await self.captcha_solver.solve_captcha(page, max_retries=10)
                            if solution:
                                print(f"   ✅ API solved captcha!")
                                debug_logger.log('entry_flow', 'CAPTCHA_SOLVED_API')
                                captcha_solved = True
                            else:
                                print(f"   ⚠️  API failed after 10 attempts")
                                print(f"   💡 TIP: Check balance → python check_omocaptcha_balance.py")
                        except Exception as e:
                            print(f"   ⚠️  API error: {str(e)[:50]}")
                    
                    # If API didn't solve, try manual
                    if not captcha_solved:
                        print(f"   👤 Please solve captcha manually (180s timeout)...")
                        print(f"   💡 Browser window should be visible")
                        resolved = await debugger.wait_for_captcha_resolved(page, timeout=180)
                        if resolved:
                            print(f"   ✅ Captcha solved manually!")
                            debug_logger.log('entry_flow', 'CAPTCHA_SOLVED_MANUAL')
                            captcha_solved = True
                        else:
                            print(f"   ❌ Captcha timeout (180s)")
                            debug_logger.log('entry_flow', 'CAPTCHA_TIMEOUT')
                    
                    # Check if captcha was solved
                    if not captcha_solved:
                        if attempt < max_retries - 1:
                            print(f"   🔄 Retrying entire flow...")
                            continue
                        else:
                            print(f"   ❌ Failed after {max_retries} attempts")
                            debug_logger.save()
                            return False
                    
                    # After captcha solved, wait for profile to stabilize
                    print(f"   ⏳ Stabilizing (3s)...")
                    await asyncio.sleep(3)
                else:
                    print(f"   ✅ No captcha")
                
                # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                # STEP 3: PROFILE STABILIZATION + DWELL TIME + SCROLL
                # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                # WHY: Simulate human reading profile before entering live
                # WHAT: Wait → Scroll slightly → Wait again
                
                print(f"   [STEP 3] Dwell time (3s)...")
                await asyncio.sleep(3)
                
                # Simulate human scrolling (reading profile)
                print(f"   [STEP 3] Simulating profile scroll...")
                try:
                    await page.evaluate("""
                        () => {
                            window.scrollBy({
                                top: 150,
                                behavior: 'smooth'
                            });
                        }
                    """)
                    await asyncio.sleep(1.5)
                    await page.evaluate("""
                        () => {
                            window.scrollBy({
                                top: -50,
                                behavior: 'smooth'
                            });
                        }
                    """)
                    await asyncio.sleep(1.5)
                except Exception as e:
                    print(f"   ⚠️  Scroll simulation failed: {e}")
                
                debug_logger.log('entry_flow', 'PROFILE_STABLE')
                
                # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                # STEP 4: LIVE BADGE DETECTION (STRICT - NO FALLBACK)
                # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                # WHY: Only enter livestream if LIVE badge is present
                # WHAT: Detect badge → If not found, ABORT (no fallback)
                
                print(f"   [STEP 4] Detecting LIVE badge...")
                
                live_badge_detected = await page.evaluate("""
                    () => {
                        // Check for LIVE badge indicators
                        const selectors = [
                            '[data-e2e="user-live-badge"]',
                            '[data-e2e="live-badge"]',
                            'a[href*="/live"]',
                            '.live-badge',
                            '[class*="LiveBadge"]',
                            'span:has-text("LIVE")',
                            'div:has-text("LIVE")'
                        ];
                        
                        for (const sel of selectors) {
                            try {
                                const elem = document.querySelector(sel);
                                if (elem && elem.offsetParent !== null) {
                                    return {
                                        found: true,
                                        selector: sel,
                                        text: elem.textContent,
                                        href: elem.href || null
                                    };
                                }
                            } catch (e) {}
                        }
                        
                        return {found: false};
                    }
                """)
                
                if not live_badge_detected.get('found'):
                    print(f"   ❌ LIVE badge not found - stream not available")
                    debug_logger.log('entry_flow', 'LIVE_NOT_AVAILABLE')
                    debug_logger.save()
                    return False
                
                print(f"   ✅ LIVE badge found")
                debug_logger.log('entry_flow', 'LIVE_BADGE_FOUND')
                
                # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                # STEP 5: LIVE ENTRY VIA BADGE CLICK (STRICT - CLICK ONLY)
                # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                # WHY: Most natural user behavior is clicking badge
                # WHAT: Click badge → Wait for navigation → Verify livestream page
                
                print(f"   [STEP 5] Clicking LIVE badge...")
                
                try:
                    # Try to click LIVE badge
                    clicked = await page.evaluate("""
                        () => {
                            const selectors = [
                                '[data-e2e="user-live-badge"]',
                                '[data-e2e="live-badge"]',
                                'a[href*="/live"]'
                            ];
                            
                            for (const sel of selectors) {
                                const elem = document.querySelector(sel);
                                if (elem && elem.offsetParent !== null) {
                                    elem.click();
                                    return {clicked: true, selector: sel};
                                }
                            }
                            
                            return {clicked: false};
                        }
                    """)
                    
                    if not clicked.get('clicked'):
                        print(f"   ❌ Click failed")
                        debug_logger.log('entry_flow', 'LIVE_CLICK_FAILED')
                        
                        if attempt < max_retries - 1:
                            continue
                        else:
                            debug_logger.save()
                            return False
                    
                    print(f"   ✅ Badge clicked")
                    debug_logger.log('entry_flow', 'LIVE_CLICKED')
                    
                    await asyncio.sleep(3)
                    
                    # Verify we're on livestream page
                    current_url = page.url
                    if '/live' not in current_url:
                        print(f"   ⚠️  Not on livestream page")
                        debug_logger.log('entry_flow', 'LIVE_ENTRY_FAILED')
                        
                        if attempt < max_retries - 1:
                            continue
                        else:
                            debug_logger.save()
                            return False
                    
                except Exception as e:
                    print(f"   ❌ Click error: {e}")
                    debug_logger.log('entry_flow', 'LIVE_CLICK_ERROR')
                    
                    if attempt < max_retries - 1:
                        continue
                    else:
                        debug_logger.save()
                        return False
                
                print(f"   ✅ Livestream entered")
                debug_logger.log('entry_flow', 'LIVE_ENTERED')
                
                # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                # STEP 6: MEDIA WARM-UP WINDOW (CRITICAL)
                # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                # WHY: Media pipeline needs time to initialize
                # WHAT: Wait 15s for AudioContext + Video + WebSocket
                
                print(f"   [STEP 6] Warm-up (15s)...")
                debug_logger.log('entry_flow', 'WARMUP_START')
                
                await asyncio.sleep(15)
                
                print(f"   ✅ Warm-up done")
                debug_logger.log('entry_flow', 'WARMUP_DONE')
                
                # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                # MEDIA SAFETY VERIFICATION (READ-ONLY)
                # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                try:
                    media_safety = await page.evaluate("""
                        () => {
                            const video = document.querySelector('video');
                            const audioCtx = window.AudioContext || window.webkitAudioContext;
                            
                            // Test AudioContext creation
                            let audioContextTest = null;
                            try {
                                audioContextTest = new (window.AudioContext || window.webkitAudioContext)();
                            } catch (e) {
                                audioContextTest = null;
                            }
                            
                            return {
                                // Video state
                                video_exists: !!video,
                                video_ready_state: video ? video.readyState : null,
                                video_paused: video ? video.paused : null,
                                video_muted: video ? video.muted : null,
                                
                                // Audio context (CRITICAL for view counting)
                                audio_context_available: !!audioCtx,
                                audio_context_creatable: !!audioContextTest,
                                audio_context_state: audioContextTest ? audioContextTest.state : 'not_created',
                                
                                // Page state
                                visibility_state: document.visibilityState,
                                is_focused: document.hasFocus(),
                                
                                // Autoplay policy
                                autoplay_policy: navigator.userActivation ? {
                                    has_been_active: navigator.userActivation.hasBeenActive,
                                    is_active: navigator.userActivation.isActive
                                } : 'not_available'
                            };
                        }
                    """)
                    
                    # Log media safety
                    print(f"   [MEDIA-SAFETY] Verification:")
                    print(f"      AudioContext: {'✅ Available' if media_safety.get('audio_context_available') else '❌ NOT Available'}")
                    print(f"      AudioContext State: {media_safety.get('audio_context_state')}")
                    print(f"      Video Element: {'✅ Exists' if media_safety.get('video_exists') else '⚠️  Not found'}")
                    print(f"      Video Ready: {media_safety.get('video_ready_state')}")
                    print(f"      Page Visible: {'✅ Yes' if media_safety.get('visibility_state') == 'visible' else '❌ No'}")
                    
                    debug_logger.log('media_safety', f"audio_context_available={media_safety.get('audio_context_available')}")
                    debug_logger.log('media_safety', f"audio_context_state={media_safety.get('audio_context_state')}")
                    debug_logger.log('media_safety', f"video_exists={media_safety.get('video_exists')}")
                    debug_logger.log('media_safety', f"video_ready_state={media_safety.get('video_ready_state')}")
                    debug_logger.log('media_safety', f"visibility_state={media_safety.get('visibility_state')}")
                    
                    # Determine view eligibility (READ-ONLY, no action taken)
                    view_eligible = (
                        media_safety.get('audio_context_available') and
                        media_safety.get('audio_context_state') not in ['not_created', 'closed'] and
                        media_safety.get('visibility_state') == 'visible'
                    )
                    
                    debug_logger.log('final_state', f"VIEW_ELIGIBLE={view_eligible}")
                    
                    if view_eligible:
                        print(f"   ✅ View eligible: Media pipeline valid")
                    else:
                        print(f"   ⚠️  View may not count: Media pipeline issue")
                        if not media_safety.get('audio_context_available'):
                            print(f"      → AudioContext NOT available (CRITICAL)")
                        if media_safety.get('audio_context_state') in ['not_created', 'closed']:
                            print(f"      → AudioContext state: {media_safety.get('audio_context_state')} (CRITICAL)")
                        
                except Exception as e:
                    print(f"   ⚠️  Media safety check failed: {e}")
                    debug_logger.log('errors', f"Media safety check: {str(e)[:100]}")
                
                # Collect startup data for comparison (AUTO mode)
                try:
                    from analysis.startup_compare import log_full_startup
                    print(f"   [STARTUP-LOG] Collecting AUTO mode data...")
                    await log_full_startup("AUTO", profile_name, page)
                except Exception as e:
                    print(f"   [STARTUP-LOG] ⚠️  Collection error: {e}")
                
                # Setup full debug monitoring if enabled
                if self.full_debug_mode:
                    await debug_logger.setup_monitoring(page)
                
                # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                # LIVE JOIN 2025 - PROPER IMPLEMENTATION
                # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                
                from core.live_join_2025 import execute_live_join_2025
                
                try:
                    live_join_state, fail_reason, live_join_details = await execute_live_join_2025(
                        page=page,
                        profile_id=profile_name
                    )
                    
                    # Log result
                    if self.full_debug_mode:
                        debug_logger.log('live_join', f"{live_join_state}:{fail_reason or 'OK'}")
                except Exception as e:
                    print(f"\n   ❌ LIVE JOIN 2025 ERROR: {e}")
                    import traceback
                    traceback.print_exc()
                    
                    if self.full_debug_mode:
                        debug_logger.log('errors', f"LIVE_JOIN_ERROR:{str(e)[:50]}")
                        debug_logger.save()
                    
                    # Set failed state
                    live_join_state = "LIVE_JOIN_FAILED"
                    fail_reason = "EXCEPTION"
                
                # Handle captcha if detected
                if fail_reason == "CAPTCHA_BLOCKING":
                    print(f"\n   {'='*60}")
                    print(f"   CAPTCHA HANDLING")
                    print(f"   {'='*60}")
                    
                    debugger = LivestreamCaptchaDebugger(profile_name)
                    
                    # Try auto-solve if solver available
                    if self.captcha_solver:
                        try:
                            print(f"   [CAPTCHA] Attempting auto-solve...")
                            solution = await self.captcha_solver.solve_captcha(page, max_retries=10)
                            
                            if solution:
                                print(f"   [CAPTCHA] ✅ Auto-solved")
                                # Retry LIVE JOIN after captcha solved
                                print(f"   [CAPTCHA] Retrying LIVE JOIN...")
                                live_join_state, fail_reason, live_join_details = await execute_live_join_2025(
                                    page=page,
                                    profile_id=profile_name
                                )
                            else:
                                print(f"   [CAPTCHA] ⚠️  Auto-solve failed")
                                print(f"   [CAPTCHA] Waiting for manual solve...")
                                resolved = await debugger.wait_for_captcha_resolved(page, timeout=180)
                                if resolved:
                                    # Retry LIVE JOIN
                                    live_join_state, fail_reason, live_join_details = await execute_live_join_2025(
                                        page=page,
                                        profile_id=profile_name
                                    )
                        except Exception as e:
                            print(f"   [CAPTCHA] ⚠️  Error: {e}")
                    else:
                        print(f"   [CAPTCHA] No auto-solver, waiting for manual solve...")
                        resolved = await debugger.wait_for_captcha_resolved(page, timeout=180)
                        if resolved:
                            # Retry LIVE JOIN
                            live_join_state, fail_reason, live_join_details = await execute_live_join_2025(
                                page=page,
                                profile_id=profile_name
                            )
                
                # Check final result
                if live_join_state == "LIVE_JOINED":
                    print(f"\n   ✅ LIVE JOIN SUCCESS - View will be counted")
                else:
                    print(f"\n   ❌ LIVE JOIN FAILED: {fail_reason}")
                    print(f"   ⚠️  View will NOT be counted")
                
                print(f"   {'='*60}\n")
                
                # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                # RAM TRACKING
                # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                
                try:
                    import psutil
                    process = psutil.Process()
                    ram_mb = process.memory_info().rss / 1024 / 1024
                    
                    print(f"   [RAM] Current: {ram_mb:.1f}MB")
                    
                    if ram_mb > 220:
                        print(f"   [RAM] ⚠️  High RAM usage (target: 150-200MB)")
                    else:
                        print(f"   [RAM] ✅ RAM within target")
                except Exception as e:
                    print(f"   [RAM] ⚠️  Could not get RAM info: {e}")
                
                # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                # VERIFY PAGE RESPONSIVE
                # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                
                try:
                    await asyncio.wait_for(page.evaluate('1 + 1'), timeout=5.0)
                    print(f"   ✅ Page responsive")
                except Exception as e:
                    last_error = f"Page not responsive: {e}"
                    if attempt < max_retries - 1:
                        continue
                    else:
                        return False
                
                # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                # COLLECT PROFILE INFO
                # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                
                try:
                    # Get WebGL info
                    gpu_info = await page.evaluate("""
                        () => {
                            const canvas = document.createElement('canvas');
                            const gl = canvas.getContext('webgl');
                            if (!gl) return {vendor: 'N/A', renderer: 'N/A'};
                            
                            const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
                            return {
                                vendor: debugInfo ? gl.getParameter(debugInfo.UNMASKED_VENDOR_WEBGL) : 'N/A',
                                renderer: debugInfo ? gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL) : 'N/A'
                            };
                        }
                    """)
                    
                    # Get UA
                    user_agent = await page.evaluate('navigator.userAgent')
                    
                    # Get webdriver status
                    webdriver = await page.evaluate('navigator.webdriver')
                    
                    self.profile_info[profile_name] = {
                        'ua': user_agent[:60] + '...' if len(user_agent) > 60 else user_agent,
                        'gpu_vendor': gpu_info['vendor'],
                        'gpu_renderer': gpu_info['renderer'][:40] + '...' if len(gpu_info['renderer']) > 40 else gpu_info['renderer'],
                        'window_size': window_size,
                        'mobile': mobile_mode,
                        'webdriver': webdriver
                    }
                    
                    print(f"   [GPU] {gpu_info['vendor']}")
                    print(f"   [WEBDRIVER] {webdriver} {'✅' if not webdriver else '❌'}")
                    
                except Exception as e:
                    print(f"   [INFO] ⚠️  Could not get profile info: {e}")
                
                # Success
                # Save debug logs before return
                debug_logger.save()
                
                self.launched_profiles.append(profile_name)
                return True
                
            except Exception as e:
                error_msg = str(e)
                last_error = error_msg
                debug_logger.log('errors', f"EXC:{error_msg[:50]}")
                
                if "Connection closed" in error_msg or "timeout" in error_msg.lower():
                    if attempt < max_retries - 1:
                        print(f"   Connection error, retrying...")
                    else:
                        print(f"❌ Error after {max_retries} attempts: {e}")
                        debug_logger.save()
                        return False
                else:
                    print(f"❌ Error: {e}")
                    if attempt < max_retries - 1:
                        continue
                    else:
                        debug_logger.save()
                        return False
        
        debug_logger.save()
        return False
    
    async def launch_multiple_async(
        self,
        profiles: List[str],
        url: str,
        window_size: str = "1x1",
        mobile_mode: bool = False,
        force_headless: bool = False,
        delay: float = 2.0
    ):
        """Launch multiple profiles with Stealth 2025"""
        print("\n" + "=" * 70)
        print("LAUNCHING PROFILES - STEALTH 2025 MODE")
        print("=" * 70)
        print(f"Profiles: {len(profiles)}")
        print(f"URL: {url}")
        print(f"Window Size: {window_size}")
        print(f"Mobile Mode: {'YES' if mobile_mode else 'NO'}")
        print(f"Force Headless: {'YES (not recommended for livestream)' if force_headless else 'NO'}")
        print(f"Delay: {delay}s")
        print(f"Target RAM: 150-200MB per profile")
        print("=" * 70)
        
        # Start Playwright
        print("\n[PLAYWRIGHT] Starting...")
        await self.browser_manager.start()
        print("[PLAYWRIGHT] ✅ Started")
        
        # Start RAM monitor if available
        if RAM_MONITOR_AVAILABLE:
            print("\n[RAM-MONITOR] Starting...")
            self.ram_monitor_task = asyncio.create_task(
                start_ram_monitor(self.launched_profiles)
            )
        
        success_count = 0
        failed_count = 0
        start_time = time.time()
        
        for i, profile_name in enumerate(profiles, 1):
            print(f"\n[{i}/{len(profiles)}] Launching {profile_name}...")
            
            success = await self.launch_profile_async(
                profile_name=profile_name,
                url=url,
                window_size=window_size,
                mobile_mode=mobile_mode,
                force_headless=force_headless
            )
            
            if success:
                print(f"✅ {profile_name} launched")
                success_count += 1
            else:
                print(f"❌ {profile_name} failed")
                failed_count += 1
            
            if i < len(profiles):
                await asyncio.sleep(delay)
        
        total_time = time.time() - start_time
        
        # Results
        print("\n" + "=" * 70)
        print("RESULTS")
        print("=" * 70)
        print(f"✅ Success: {success_count}/{len(profiles)}")
        print(f"❌ Failed: {failed_count}/{len(profiles)}")
        print(f"⏱️  Total time: {total_time:.1f}s")
        print(f"⚡ Average: {total_time/len(profiles):.2f}s per profile")
        
        # Show profile info
        if self.profile_info:
            print("\n" + "=" * 70)
            print("PROFILE INFO (Stealth 2025)")
            print("=" * 70)
            for profile, info in list(self.profile_info.items())[:5]:  # Show first 5
                print(f"\n{profile}:")
                print(f"  Window: {info['window_size']} | Mobile: {info['mobile']}")
                print(f"  GPU: {info['gpu_vendor']}")
                print(f"  Webdriver: {info['webdriver']} {'✅' if not info['webdriver'] else '❌'}")
                print(f"  UA: {info['ua']}")
            
            if len(self.profile_info) > 5:
                print(f"\n... and {len(self.profile_info) - 5} more profiles")
        
        print("=" * 70)
        
        return success_count, failed_count
    
    def launch_multiple(
        self,
        profiles: List[str],
        url: str,
        window_size: str = "1x1",
        mobile_mode: bool = False,
        force_headless: bool = False,
        delay: float = 2.0
    ):
        """Sync wrapper for launch_multiple_async"""
        if self.loop is None or self.loop.is_closed():
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
        
        return self.loop.run_until_complete(
            self.launch_multiple_async(
                profiles=profiles,
                url=url,
                window_size=window_size,
                mobile_mode=mobile_mode,
                force_headless=force_headless,
                delay=delay
            )
        )
    
    def cleanup(self):
        """Cleanup resources"""
        try:
            # Stop RAM monitor
            if self.ram_monitor_task and RAM_MONITOR_AVAILABLE:
                print("\n[RAM-MONITOR] Stopping...")
                self.ram_monitor_task.cancel()
            
            # Stop browser manager
            if self.loop and not self.loop.is_closed():
                self.loop.run_until_complete(self.browser_manager.stop())
        except:
            pass
        
        if self.loop and not self.loop.is_closed():
            try:
                self.loop.close()
            except:
                pass


def main():
    """Main function"""
    
    # Fix encoding for Windows
    if sys.platform == 'win32':
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except:
            pass
    
    launcher = Stealth2025LivestreamLauncher()
    
    while True:
        print("\n" + "=" * 70)
        print("🛡️  TIKTOK LIVESTREAM LAUNCHER - STEALTH 2025")
        print("=" * 70)
        print("\n1. Launch profiles (Minimal Window 1x1)")
        print("2. Launch profiles (Mobile 360x640)")
        print("3. Launch profiles (Desktop 1280x720)")
        print("4. Launch profiles (Custom window size)")
        print("5. Kill all Chrome processes")
        print("6. View RAM statistics")
        print("7. Toggle Full Debug Mode (Current: " + ("ON ✅" if launcher.full_debug_mode else "OFF") + ")")
        print("8. Exit")
        
        choice = input("\nChoice (1-8): ").strip()
        
        if choice in ('1', '2', '3', '4'):
            # Determine window size
            if choice == '1':
                window_size = "1x1"
                mobile_mode = False
            elif choice == '2':
                window_size = "360x640"
                mobile_mode = True
            elif choice == '3':
                window_size = "1280x720"
                mobile_mode = False
            else:  # choice == '4'
                print("\nAvailable window sizes:")
                for name, size in WINDOW_SIZES.items():
                    print(f"  {name}: {size}")
                print("\nEnter window size (e.g. '360x640' or 'mobile_medium'):")
                window_size = input("Window size: ").strip() or "360x640"
                
                print("\nEnable mobile mode? (yes/no):")
                mobile_input = input("Mobile mode: ").strip().lower()
                mobile_mode = (mobile_input == 'yes')
            
            all_profiles = launcher.get_all_profiles()
            
            if not all_profiles:
                print("\n❌ No profiles found in chrome_profiles/")
                continue
            
            print(f"\n✅ Found {len(all_profiles)} profiles")
            
            # Get number of profiles
            print(f"\nHow many profiles to launch? (1-{len(all_profiles)})")
            try:
                count = int(input("Count: ").strip())
                if count < 1 or count > len(all_profiles):
                    print(f"❌ Invalid count")
                    continue
            except ValueError:
                print("❌ Invalid input")
                continue
            
            profiles = all_profiles[:count]
            
            # Get URL
            print("\nEnter TikTok livestream URL:")
            url = input("URL: ").strip()
            
            if not url:
                print("❌ URL required")
                continue
            
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            # Get delay
            print("\nDelay between launches (seconds):")
            try:
                delay = float(input("Delay (default 2.0): ").strip() or "2.0")
                if delay < 0.5:
                    delay = 0.5
            except ValueError:
                delay = 2.0
            
            # Force headless option
            print("\nForce headless mode? (not recommended for livestream)")
            print("(yes/no, default: no):")
            headless_input = input("Force headless: ").strip().lower()
            force_headless = (headless_input == 'yes')
            
            # Confirm
            print("\n" + "=" * 70)
            print("READY TO LAUNCH - STEALTH 2025")
            print("=" * 70)
            print(f"Profiles: {count}")
            print(f"URL: {url}")
            print(f"Window Size: {window_size}")
            print(f"Mobile Mode: {'YES' if mobile_mode else 'NO'}")
            print(f"Force Headless: {'YES (not recommended)' if force_headless else 'NO (visible mode)'}")
            print(f"Delay: {delay}s")
            print(f"Target RAM: 150-200MB per profile")
            print(f"Full Debug Mode: {'ENABLED ✅ (logs saved to JSON)' if launcher.full_debug_mode else 'DISABLED'}")
            print(f"Estimated time: {count * delay:.0f}s ({count * delay / 60:.1f} min)")
            print("=" * 70)
            
            confirm = input("\nContinue? (yes/no): ").strip().lower()
            if confirm != 'yes':
                print("❌ Cancelled")
                continue
            
            # Launch
            try:
                success_count, failed_count = launcher.launch_multiple(
                    profiles=profiles,
                    url=url,
                    window_size=window_size,
                    mobile_mode=mobile_mode,
                    force_headless=force_headless,
                    delay=delay
                )
                
                print(f"\n✅ COMPLETE!")
                print(f"Launched {success_count} profiles successfully")
                
                if failed_count > 0:
                    print(f"⚠️  {failed_count} profiles failed")
                
                input("\nPress Enter to continue...")
                
            except KeyboardInterrupt:
                print("\n\n⚠️  Interrupted by user")
                input("Press Enter to continue...")
            except Exception as e:
                print(f"\n❌ Error: {e}")
                import traceback
                traceback.print_exc()
                input("Press Enter to continue...")
        
        elif choice == '5':
            launcher.kill_all_chrome()
            input("\nPress Enter to continue...")
        
        elif choice == '6':
            # View RAM statistics
            if RAM_MONITOR_AVAILABLE:
                print("\n[RAM-MONITOR] Generating report...")
                try:
                    from system_monitor.analyze_ram import generate_report
                    generate_report()
                    print("✅ Report generated: system_monitor/RAM_REPORT.md")
                except Exception as e:
                    print(f"❌ Error: {e}")
            else:
                print("\n❌ RAM monitor not available")
            
            input("\nPress Enter to continue...")
        
        elif choice == '7':
            # Toggle Full Debug Mode
            launcher.full_debug_mode = not launcher.full_debug_mode
            status = "ENABLED ✅" if launcher.full_debug_mode else "DISABLED"
            print(f"\n[FULL-DEBUG] {status}")
            
            if launcher.full_debug_mode:
                print("\n" + "=" * 70)
                print("FULL DEBUG MODE - WHAT IT TRACKS")
                print("=" * 70)
                print("✅ Network: All requests/responses to TikTok")
                print("✅ WebSocket: Connection open/close and messages")
                print("✅ Console: All browser console logs")
                print("✅ Video Stats: ReadyState, currentTime, buffered (every 5s)")
                print("✅ Audio Stats: AudioContext state and timing")
                print("✅ Performance: JS Heap memory usage")
                print("✅ Errors: All exceptions and errors")
                # Generate example filename
                example_ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                example_file = f'full_debug_<profile_id>_{example_ts}.json'
                print(f"\n📁 Logs will be saved as: {example_file}")
                print("   (Actual filename created when profile launches)")
                print("=" * 70)
            
            input("\nPress Enter to continue...")
        
        elif choice == '8':
            print("\n👋 Goodbye!")
            launcher.cleanup()
            break
        
        else:
            print("❌ Invalid choice")


if __name__ == "__main__":
    main()
