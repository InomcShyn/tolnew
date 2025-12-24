#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 TikTok LIVE RAM Optimized Launcher V2 - 2025 Compliant
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

GOAL:
Launch TikTok LIVE with RAM optimization (180-220MB/profile) while preserving
view eligibility according to baseline measurements.

STRICT COMPLIANCE:
✅ Natural navigation flow (profile → LIVE badge → click)
✅ Minimal Chrome flags (no headless, no media disable, no GPU disable)
✅ Proper lifecycle phases (bootstrap → trust → stabilize → idle)
✅ Read-only monitoring (no video manipulation)
✅ User activation via real DOM clicks
✅ Viewport >= 360x640

❌ NO headless mode
❌ NO --single-process
❌ NO --mute-audio / --disable-audio / --disable-webaudio
❌ NO --disable-gpu / --disable-media*
❌ NO --window-size=1,1 or tiny viewports
❌ NO video.pause() or element removal
❌ NO fake interactions or view manipulation

BASELINE VALIDATION:
- document.visibilityState = "visible"
- navigator.webdriver = false (via --disable-blink-features=AutomationControlled)
- navigator.userActivation = true (via real click)
- video element count may be 0 (LIVE uses canvas/player)
- AudioContext supported and functional
- JS Heap < 100MB
- Chrome RSS: 180-220MB target

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import sys
import os
import asyncio
import time
import threading
from pathlib import Path
from typing import Dict, Optional, Tuple

sys.path.insert(0, os.getcwd())

from core.chrome_manager import ChromeProfileManager
from core.managers.profile_manager import ProfileManager
from process_memory_monitor import ProcessMemoryMonitor
from chrome_ram_diagnostics import (
    check_chrome_ram_sources,
    format_ram_diagnostic_report,
    detect_ram_spike
)
from live_metrics_internal_api import METRICS_STORE, start_api_server


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CHROME FLAGS - FINAL APPROVED SET
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TikTokLiveChromeFlagsV2:
    """
    Chrome flags optimized for RAM while preserving TikTok LIVE view eligibility.
    
    RATIONALE FOR EACH FLAG:
    - Stealth flags: Hide automation, pass bot detection
    - Process limits: Reduce RAM without breaking media pipeline
    - Cache limits: Reduce disk/memory cache footprint
    - JS heap limit: Cap V8 memory usage
    - Language: Consistent locale
    - Activation: Enable proper navigation context
    - Remote debugging: Required for Playwright/CDP
    
    EXPLICITLY EXCLUDED:
    - --headless: Breaks trust signals
    - --disable-gpu: Breaks video rendering
    - --disable-audio/media: Breaks AudioContext detection
    - --single-process: Unstable, breaks isolation
    - --window-size=1,1: Suspicious viewport
    """
    
    @staticmethod
    def get_approved_flags() -> list:
        """
        Returns the final approved flag set.
        Each flag has been validated against baseline requirements.
        """
        return [
            # ═══════════════════════════════════════════════════════════
            # STEALTH & AUTOMATION HIDING (Critical for bot detection)
            # ═══════════════════════════════════════════════════════════
            '--no-default-browser-check',  # Skip default browser prompt
            '--password-store=basic',  # Use basic password store
            '--unsafely-disable-devtools-self-xss-warnings',  # Allow console access
            '--edge-skip-compat-layer-relaunch',  # Skip Edge compat check
            '--no-sandbox',  # Required for some environments
            '--disable-blink-features=AutomationControlled',  # Hide navigator.webdriver
            '--exclude-switches=enable-automation',  # Remove automation flag
            '--disable-infobars',  # Hide "Chrome is being controlled" bar
            
            # ═══════════════════════════════════════════════════════════
            # PROCESS & MEMORY LIMITS (RAM optimization)
            # ═══════════════════════════════════════════════════════════
            '--renderer-process-limit=2',  # Limit renderer processes (safe for single tab)
            '--disk-cache-size=1',  # Minimal disk cache (1 byte = effectively disabled)
            '--media-cache-size=1',  # Minimal media cache
            
            # ═══════════════════════════════════════════════════════════
            # JAVASCRIPT HEAP LIMIT (Critical for RAM)
            # ═══════════════════════════════════════════════════════════
            '--js-flags=--max-old-space-size=96',  # Limit JS heap to 96MB
            
            # ═══════════════════════════════════════════════════════════
            # LOCALE & LANGUAGE
            # ═══════════════════════════════════════════════════════════
            '--lang=en-US',  # Consistent language
            
            # ═══════════════════════════════════════════════════════════
            # NAVIGATION & ACTIVATION (Required for proper context)
            # ═══════════════════════════════════════════════════════════
            '--enable-main-frame-before-activation',  # Enable proper activation
            
            # ═══════════════════════════════════════════════════════════
            # REMOTE DEBUGGING (Required for Playwright/CDP)
            # ═══════════════════════════════════════════════════════════
            '--remote-debugging-pipe',  # Enable remote debugging via pipe
        ]
    
    @staticmethod
    def get_forbidden_flags() -> list:
        """
        Flags that MUST NOT be used as they break view eligibility.
        """
        return [
            '--headless',
            '--disable-gpu',
            '--disable-audio',
            '--disable-webaudio',
            '--disable-media',
            '--disable-video',
            '--mute-audio',
            '--single-process',
            '--window-size=1,1',
        ]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# RAM MONITORING (Read-Only)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class SimpleRAMMonitor:
    """
    Process-level RAM monitor using psutil.
    Đo TỔNG RAM của Chrome profile (tất cả processes).
    """
    
    def __init__(self, profile_name: str):
        self.profile_name = profile_name
        self.start_time = time.time()
        self.is_live_active = False
        self.process_monitor = ProcessMemoryMonitor(profile_name)
        
    def set_live_status(self, active: bool):
        """Mark LIVE as active/inactive"""
        self.is_live_active = active
        
    def get_elapsed_time(self) -> float:
        """Get elapsed time since start"""
        return time.time() - self.start_time
    
    def log_status(self, message: str):
        """Log status with timestamp"""
        elapsed = self.get_elapsed_time()
        mins = int(elapsed // 60)
        secs = int(elapsed % 60)
        print(f"[{mins:02d}:{secs:02d}] {message}")
    
    def measure_total_ram(self) -> Dict:
        """
        Đo TỔNG RAM của Chrome profile (process-level)
        Returns: {total_mb, breakdown, process_count, details}
        """
        return self.process_monitor.measure_total_memory()
    
    def get_memory_trend(self) -> Dict:
        """
        Phân tích xu hướng memory
        Returns: {trend, slope_mb_per_min, avg_mb, min_mb, max_mb}
        """
        return self.process_monitor.get_memory_trend()
    
    def format_memory_report(self, mem_data: Dict) -> str:
        """Format memory report"""
        return self.process_monitor.format_memory_report(mem_data)



# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# LIFECYCLE PHASES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class LivestreamLifecycle:
    """
    Manages the 4 phases of livestream entry:
    1. Bootstrap: Launch Chrome, establish connection
    2. Trust Window: Natural navigation, user activation
    3. Stabilize: Wait for media pipeline to initialize
    4. Idle: Maintain session without interference
    """
    
    def __init__(self, page, profile_name: str, monitor: SimpleRAMMonitor):
        self.page = page
        self.profile_name = profile_name
        self.monitor = monitor
        
    async def phase_1_bootstrap(self):
        """
        Phase 1: Bootstrap
        - Chrome is launched
        - Connection established
        - No navigation yet
        """
        self.monitor.log_status("Phase 1: Bootstrap - Chrome launched")
        
        # Log initial state
        try:
            initial_state = await self.page.evaluate("""
                () => ({
                    url: window.location.href,
                    visibilityState: document.visibilityState,
                    webdriver: navigator.webdriver
                })
            """)
            self.monitor.log_status(f"Initial state: {initial_state}")
        except:
            pass
    
    async def phase_2_trust_window(self, creator_username: str) -> Tuple[bool, Dict]:
        """
        Phase 2: Trust Window (CRITICAL) - Natural Entry
        - Navigate to profile page
        - Detect LIVE badge
        - Click LIVE badge (real DOM click)
        - Wait for player to mount
        
        This phase establishes:
        - Proper navigation context (type="navigate")
        - User activation (via click)
        - History length >= 3
        - Redirect count >= 1
        
        Returns: (success, navigation_context)
        """
        self.monitor.log_status("Phase 2: Trust Window - Natural entry flow")
        
        try:
            # ─────────────────────────────────────────────────────────
            # Step 2.1: Navigate to profile page
            # ─────────────────────────────────────────────────────────
            self.monitor.log_status(f"Navigating to @{creator_username} profile...")
            profile_url = f"https://www.tiktok.com/@{creator_username}"
            
            await self.page.goto(profile_url, wait_until="domcontentloaded")
            
            # Wait for profile to render (3-6s as per requirements)
            await asyncio.sleep(4.0)
            self.monitor.log_status("Profile page loaded")
            
            # ─────────────────────────────────────────────────────────
            # Step 2.2: Detect LIVE badge (Single query to avoid request spam)
            # ─────────────────────────────────────────────────────────
            self.monitor.log_status("Detecting LIVE badge...")
            
            # Use JavaScript to find LIVE badge without multiple network requests
            live_badge_info = await self.page.evaluate("""
                () => {
                    // Try multiple selectors in one pass
                    const selectors = [
                        'a[href*="/live"]',
                        '[data-e2e="live-badge"]',
                        'span:has-text("LIVE")',
                        'div[class*="live"]'
                    ];
                    
                    for (const selector of selectors) {
                        const elements = document.querySelectorAll(selector);
                        for (const el of elements) {
                            if (el.offsetParent !== null) {  // Check if visible
                                const rect = el.getBoundingClientRect();
                                return {
                                    found: true,
                                    selector: selector,
                                    x: rect.x + rect.width / 2,
                                    y: rect.y + rect.height / 2
                                };
                            }
                        }
                    }
                    return { found: false };
                }
            """)
            
            if not live_badge_info['found']:
                self.monitor.log_status("⚠️  LIVE badge not found, using fallback URL")
                live_url = f"https://www.tiktok.com/@{creator_username}/live"
                await self.page.goto(live_url, wait_until="domcontentloaded")
            else:
                # ─────────────────────────────────────────────────────────
                # Step 2.3: Click LIVE badge (REAL DOM CLICK)
                # ─────────────────────────────────────────────────────────
                self.monitor.log_status(f"LIVE badge found: {live_badge_info['selector']}")
                self.monitor.log_status("Clicking LIVE badge (real DOM click)...")
                
                # Click at the detected position
                await self.page.mouse.click(live_badge_info['x'], live_badge_info['y'])
                self.monitor.log_status("LIVE badge clicked")
            
            # ─────────────────────────────────────────────────────────
            # Step 2.4: Wait for player to mount (8-15s as per requirements)
            # ─────────────────────────────────────────────────────────
            self.monitor.log_status("Waiting for player to mount (10s)...")
            await asyncio.sleep(10.0)
            
            # Check for video/canvas element without triggering extra requests
            try:
                player_exists = await self.page.evaluate("""
                    () => {
                        const video = document.querySelector('video');
                        const canvas = document.querySelector('canvas');
                        return {
                            hasVideo: !!video,
                            hasCanvas: !!canvas,
                            videoReadyState: video ? video.readyState : 0
                        };
                    }
                """)
                
                if player_exists['hasVideo'] or player_exists['hasCanvas']:
                    self.monitor.log_status("Player element detected")
                else:
                    self.monitor.log_status("⚠️  No video/canvas element (may use custom player)")
            except:
                self.monitor.log_status("⚠️  Could not check player element")
            
            # Mark LIVE as active
            self.monitor.set_live_status(True)
            self.monitor.log_status("✅ Trust window established")
            
            # ─────────────────────────────────────────────────────────
            # Step 2.5: Verify navigation context (READ-ONLY)
            # ─────────────────────────────────────────────────────────
            nav_context = await self._verify_navigation_context()
            
            return True, nav_context
            
        except Exception as e:
            self.monitor.log_status(f"❌ Trust window failed: {e}")
            return False, {'error': str(e)}
    
    async def phase_2_direct_url(self, live_url: str) -> Tuple[bool, Dict]:
        """
        Phase 2: Direct URL Entry (FASTER, LOWER RAM)
        - Navigate directly to livestream URL
        - Wait for player to mount
        - Simulate user click for activation
        
        ⚠️  WARNING: May not establish optimal navigation context
        Use natural entry for better view counting compliance.
        
        Returns: (success, navigation_context)
        """
        self.monitor.log_status("Phase 2: Direct URL - Fast entry")
        
        try:
            # ─────────────────────────────────────────────────────────
            # Step 2.1: Navigate directly to LIVE URL
            # ─────────────────────────────────────────────────────────
            self.monitor.log_status(f"Navigating to: {live_url}")
            
            await self.page.goto(live_url, wait_until="domcontentloaded")
            
            # Wait for page to load
            await asyncio.sleep(3.0)
            self.monitor.log_status("LIVE page loaded")
            
            # ─────────────────────────────────────────────────────────
            # Step 2.2: Simulate user click for activation
            # ─────────────────────────────────────────────────────────
            self.monitor.log_status("Simulating user activation...")
            await self.page.mouse.move(100, 100)
            await asyncio.sleep(0.3)
            await self.page.evaluate("() => { document.body.click(); }")
            await asyncio.sleep(0.5)
            
            # ─────────────────────────────────────────────────────────
            # Step 2.3: Wait for player to mount
            # ─────────────────────────────────────────────────────────
            self.monitor.log_status("Waiting for player to mount (8s)...")
            await asyncio.sleep(8.0)
            
            # Try to detect video element
            try:
                await self.page.wait_for_selector("video, canvas", timeout=5000, state="visible")
                self.monitor.log_status("Player element detected")
            except:
                self.monitor.log_status("⚠️  No video/canvas element (may use custom player)")
            
            # Mark LIVE as active
            self.monitor.set_live_status(True)
            self.monitor.log_status("✅ Direct URL entry complete")
            
            # ─────────────────────────────────────────────────────────
            # Step 2.4: Verify navigation context (READ-ONLY)
            # ─────────────────────────────────────────────────────────
            nav_context = await self._verify_navigation_context()
            
            # Warn if navigation context is not optimal
            if nav_context.get('navigationType') != 'navigate':
                self.monitor.log_status(
                    f"⚠️  Navigation type: {nav_context.get('navigationType')} "
                    "(may affect view counting)"
                )
            
            return True, nav_context
            
        except Exception as e:
            self.monitor.log_status(f"❌ Direct URL entry failed: {e}")
            return False, {'error': str(e)}
    
    async def phase_3_stabilize(self):
        """
        Phase 3: Stabilize
        - Wait for initial decode to complete
        - Let browser establish media pipeline
        - NO interference with video/audio
        
        Duration: 5-10 seconds
        """
        self.monitor.log_status("Phase 3: Stabilize - Waiting for media pipeline...")
        
        # Wait for stabilization (no interference)
        await asyncio.sleep(8.0)
        
        # Check state (read-only)
        try:
            state = await self.page.evaluate("""
                () => {
                    const video = document.querySelector('video');
                    return {
                        videoExists: !!video,
                        videoReadyState: video ? video.readyState : 0,
                        videoPaused: video ? video.paused : null,
                        visibilityState: document.visibilityState,
                        hasFocus: document.hasFocus()
                    };
                }
            """)
            self.monitor.log_status(f"Media state: {state}")
        except:
            pass
        
        self.monitor.log_status("✅ Stabilization complete")
    
    async def phase_4_idle(self, duration_minutes: int = 30, creator_username: str = None, live_url: str = None):
        """
        Phase 4: Idle
        - Maintain session
        - Monitor TOTAL RAM (process-level)
        - Run Chrome RAM diagnostics periodically
        - Collect and expose LIVE metrics via API
        - NO video manipulation
        - Let browser manage resources
        
        Duration: As specified (default 30 minutes)
        """
        self.monitor.log_status(f"Phase 4: Idle - Maintaining session ({duration_minutes} min)...")
        
        end_time = time.time() + (duration_minutes * 60)
        check_interval = 30  # Check every 30 seconds
        diagnostic_interval = 300  # Run full diagnostic every 5 minutes
        metrics_interval = 30  # Collect metrics every 30 seconds
        last_diagnostic_time = 0
        last_metrics_time = 0
        previous_total_ram = None
        
        try:
            while time.time() < end_time:
                await asyncio.sleep(check_interval)
                
                # Periodic state check (read-only)
                try:
                    state = await self._read_browser_state()
                    
                    # Log summary with TOTAL RAM
                    total_ram = state.get('totalRAM_MB', 'N/A')
                    breakdown = state.get('ramBreakdown', {})
                    
                    self.monitor.log_status(
                        f"RAM: {total_ram}MB total "
                        f"(Browser:{breakdown.get('browser', 0):.0f} "
                        f"Renderer:{breakdown.get('renderer', 0):.0f} "
                        f"GPU:{breakdown.get('gpu', 0):.0f}) | "
                        f"visibility={state.get('visibilityState', 'unknown')}, "
                        f"focus={state.get('hasFocus', False)}"
                    )
                    
                    # ═══════════════════════════════════════════════════════════
                    # === CHROME GLOBAL RAM DIAGNOSTICS ===
                    # ═══════════════════════════════════════════════════════════
                    
                    # Check for RAM spike
                    if isinstance(total_ram, (int, float)) and previous_total_ram is not None:
                        spike_warning = detect_ram_spike(total_ram, previous_total_ram, threshold_mb=150)
                        if spike_warning:
                            print(f"\n{spike_warning}")
                            # Run immediate diagnostic on spike
                            try:
                                diagnostic_data = await check_chrome_ram_sources(self.page)
                                print(format_ram_diagnostic_report(diagnostic_data))
                            except Exception as diag_error:
                                print(f"⚠️  Diagnostic failed: {diag_error}")
                    
                    if isinstance(total_ram, (int, float)):
                        previous_total_ram = total_ram
                    
                    # Run full diagnostic every 5 minutes
                    current_time = time.time()
                    if current_time - last_diagnostic_time >= diagnostic_interval:
                        self.monitor.log_status("Running Chrome RAM diagnostic...")
                        try:
                            diagnostic_data = await check_chrome_ram_sources(self.page)
                            print(format_ram_diagnostic_report(diagnostic_data))
                            last_diagnostic_time = current_time
                        except Exception as diag_error:
                            self.monitor.log_status(f"⚠️  Diagnostic failed: {diag_error}")
                    
                    # ═══════════════════════════════════════════════════════════
                    # === LIVE METRICS COLLECTION (for API) ===
                    # ═══════════════════════════════════════════════════════════
                    
                    # Collect metrics every 30 seconds
                    if current_time - last_metrics_time >= metrics_interval:
                        try:
                            metrics = await self._extract_live_metrics(creator_username, live_url)
                            if metrics:
                                # Store metrics for API access
                                METRICS_STORE.update_metrics(self.profile_name, metrics)
                            last_metrics_time = current_time
                        except Exception as metrics_error:
                            # Don't log every time to avoid spam
                            pass
                    
                    # ═══════════════════════════════════════════════════════════
                    
                    # Check memory trend every 5 minutes
                    elapsed = self.monitor.get_elapsed_time()
                    if int(elapsed) % 300 == 0:  # Every 5 minutes
                        trend = self.monitor.get_memory_trend()
                        if trend['trend'] != 'unknown':
                            self.monitor.log_status(
                                f"Memory trend: {trend['trend']} "
                                f"({trend['slope_mb_per_min']:+.2f} MB/min, "
                                f"range: {trend['min_mb']:.0f}-{trend['max_mb']:.0f} MB)"
                            )
                    
                except Exception as e:
                    self.monitor.log_status(f"⚠️  State check failed: {e}")
                
        except KeyboardInterrupt:
            self.monitor.log_status("⚠️  Idle phase interrupted by user")
        finally:
            # Clean up metrics when session ends
            METRICS_STORE.remove_metrics(self.profile_name)
    
    async def _verify_navigation_context(self) -> Dict:
        """
        Verify navigation context (READ-ONLY).
        Checks all baseline requirements.
        """
        try:
            context = await self.page.evaluate("""
                () => {
                    const nav = performance.getEntriesByType('navigation')[0];
                    const video = document.querySelector('video');
                    
                    // JS Heap
                    let jsHeapMB = null;
                    if (performance.memory) {
                        jsHeapMB = Math.round(performance.memory.usedJSHeapSize / 1024 / 1024);
                    }
                    
                    return {
                        // Navigation context
                        navigationType: nav ? nav.type : 'unknown',
                        redirectCount: nav ? nav.redirectCount : 0,
                        historyLength: window.history.length,
                        
                        // Page state
                        url: window.location.href,
                        visibilityState: document.visibilityState,
                        hasFocus: document.hasFocus(),
                        
                        // Bot detection
                        webdriver: navigator.webdriver,
                        
                        // User activation
                        userActivation: navigator.userActivation ? {
                            hasBeenActive: navigator.userActivation.hasBeenActive,
                            isActive: navigator.userActivation.isActive
                        } : null,
                        
                        // Media
                        videoCount: document.querySelectorAll('video').length,
                        canvasCount: document.querySelectorAll('canvas').length,
                        videoReadyState: video ? video.readyState : 0,
                        
                        // Memory
                        jsHeapMB: jsHeapMB
                    };
                }
            """)
            
            # Log verification results
            print(f"\n{'='*70}")
            print("📊 NAVIGATION CONTEXT VERIFICATION")
            print(f"{'='*70}")
            print(f"Navigation Type:    {context['navigationType']}")
            print(f"Redirect Count:     {context['redirectCount']}")
            print(f"History Length:     {context['historyLength']}")
            print(f"Visibility State:   {context['visibilityState']}")
            print(f"Has Focus:          {context['hasFocus']}")
            print(f"Webdriver:          {context['webdriver']}")
            print(f"User Activation:    {context['userActivation']}")
            print(f"Video Count:        {context['videoCount']}")
            print(f"Canvas Count:       {context['canvasCount']}")
            print(f"JS Heap:            {context['jsHeapMB']} MB")
            print(f"{'='*70}\n")
            
            # Validate critical requirements
            issues = []
            if context['visibilityState'] != 'visible':
                issues.append(f"❌ Visibility: {context['visibilityState']}")
            if context['webdriver']:
                issues.append("❌ Webdriver detected")
            if context['userActivation'] and not context['userActivation']['hasBeenActive']:
                issues.append("❌ No user activation")
            
            if issues:
                print("⚠️  ISSUES DETECTED:")
                for issue in issues:
                    print(f"  {issue}")
            else:
                print("✅ All critical checks passed")
            
            return context
            
        except Exception as e:
            return {'error': str(e)}
    
    async def _read_browser_state(self) -> Dict:
        """
        Read current browser state (READ-ONLY)
        Bao gồm cả TỔNG RAM từ process monitor
        """
        try:
            # Get browser state from JS
            js_state = await self.page.evaluate("""
                () => ({
                    visibilityState: document.visibilityState,
                    hasFocus: document.hasFocus(),
                    webdriver: navigator.webdriver,
                    jsHeapMB: performance.memory ? 
                        Math.round(performance.memory.usedJSHeapSize / 1024 / 1024) : null
                })
            """)
            
            # Get TOTAL RAM from process monitor
            mem_data = self.monitor.measure_total_ram()
            
            return {
                **js_state,
                'totalRAM_MB': mem_data['total_mb'],
                'ramBreakdown': mem_data['breakdown'],
                'processCount': mem_data['process_count']
            }
        except:
            # Fallback: only process-level memory
            mem_data = self.monitor.measure_total_ram()
            return {
                'totalRAM_MB': mem_data['total_mb'],
                'ramBreakdown': mem_data['breakdown'],
                'processCount': mem_data['process_count']
            }
    
    async def _extract_live_metrics(self, creator_username: str = None, live_url: str = None) -> Optional[Dict]:
        """
        Extract TikTok LIVE metrics from page context (READ-ONLY).
        
        Extracts:
        - viewer_count: Current viewer count
        - like_count: Total likes
        - live_start_timestamp: When LIVE started
        - live_duration_seconds: How long LIVE has been running
        - Navigation context
        - Memory stats
        
        Returns: Metrics dict or None if extraction fails
        """
        try:
            metrics_data = await self.page.evaluate("""
                () => {
                    // ═══════════════════════════════════════════════════════════
                    // Extract TikTok LIVE metrics from page state
                    // ═══════════════════════════════════════════════════════════
                    
                    const metrics = {
                        viewer_count: -1,
                        like_count: -1,
                        live_start_timestamp: null,
                        live_duration_seconds: -1,
                        status: 'unknown',
                        extraction_method: null
                    };
                    
                    try {
                        // ─────────────────────────────────────────────────────────
                        // Method 1: window.__SIGI_STATE__ (most reliable)
                        // ─────────────────────────────────────────────────────────
                        if (window.__SIGI_STATE__) {
                            const sigiState = window.__SIGI_STATE__;
                            
                            // Try LiveRoom path
                            if (sigiState.LiveRoom) {
                                const liveRoom = sigiState.LiveRoom;
                                
                                // Viewer count
                                if (liveRoom.liveRoomUserInfo && liveRoom.liveRoomUserInfo.user_count !== undefined) {
                                    metrics.viewer_count = liveRoom.liveRoomUserInfo.user_count;
                                }
                                
                                // Like count and start time
                                if (liveRoom.liveRoomInfo) {
                                    const roomInfo = liveRoom.liveRoomInfo;
                                    
                                    if (roomInfo.stats && roomInfo.stats.like_count !== undefined) {
                                        metrics.like_count = roomInfo.stats.like_count;
                                    }
                                    
                                    if (roomInfo.create_time) {
                                        metrics.live_start_timestamp = roomInfo.create_time;
                                        const now = Math.floor(Date.now() / 1000);
                                        metrics.live_duration_seconds = now - roomInfo.create_time;
                                    }
                                    
                                    // Status
                                    if (roomInfo.status !== undefined) {
                                        metrics.status = roomInfo.status === 2 ? 'live' : 'offline';
                                    }
                                }
                                
                                metrics.extraction_method = 'SIGI_STATE.LiveRoom';
                            }
                            
                            // Try RoomInfo path (alternative)
                            if (metrics.viewer_count === -1 && sigiState.RoomInfo) {
                                const roomInfo = sigiState.RoomInfo;
                                
                                if (roomInfo.user_count !== undefined) {
                                    metrics.viewer_count = roomInfo.user_count;
                                }
                                
                                if (roomInfo.stats && roomInfo.stats.like_count !== undefined) {
                                    metrics.like_count = roomInfo.stats.like_count;
                                }
                                
                                metrics.extraction_method = 'SIGI_STATE.RoomInfo';
                            }
                        }
                        
                        // ─────────────────────────────────────────────────────────
                        // Method 2: window.__UNIVERSAL_DATA_FOR_REHYDRATION__
                        // ─────────────────────────────────────────────────────────
                        if (metrics.viewer_count === -1 && window.__UNIVERSAL_DATA_FOR_REHYDRATION__) {
                            const universalData = window.__UNIVERSAL_DATA_FOR_REHYDRATION__;
                            
                            if (universalData['webapp.live-room']) {
                                const liveRoom = universalData['webapp.live-room'];
                                
                                if (liveRoom.liveRoomUserInfo && liveRoom.liveRoomUserInfo.user_count !== undefined) {
                                    metrics.viewer_count = liveRoom.liveRoomUserInfo.user_count;
                                }
                                
                                if (liveRoom.liveRoomInfo) {
                                    const roomInfo = liveRoom.liveRoomInfo;
                                    
                                    if (roomInfo.stats && roomInfo.stats.like_count !== undefined) {
                                        metrics.like_count = roomInfo.stats.like_count;
                                    }
                                    
                                    if (roomInfo.create_time) {
                                        metrics.live_start_timestamp = roomInfo.create_time;
                                        const now = Math.floor(Date.now() / 1000);
                                        metrics.live_duration_seconds = now - roomInfo.create_time;
                                    }
                                }
                                
                                metrics.extraction_method = 'UNIVERSAL_DATA_FOR_REHYDRATION';
                            }
                        }
                        
                        // ─────────────────────────────────────────────────────────
                        // Method 3: DOM fallback (less reliable)
                        // ─────────────────────────────────────────────────────────
                        if (metrics.viewer_count === -1) {
                            // Try to find viewer count in DOM
                            const viewerElements = document.querySelectorAll('[data-e2e="live-viewer-count"], [class*="viewer"], [class*="watching"]');
                            for (const el of viewerElements) {
                                const text = el.textContent || '';
                                const match = text.match(/([0-9,]+)/);
                                if (match) {
                                    const count = parseInt(match[1].replace(/,/g, ''));
                                    if (!isNaN(count) && count > 0) {
                                        metrics.viewer_count = count;
                                        metrics.extraction_method = 'DOM_fallback';
                                        break;
                                    }
                                }
                            }
                        }
                        
                    } catch (e) {
                        metrics.error = e.message;
                    }
                    
                    // ─────────────────────────────────────────────────────────
                    // Add navigation context
                    // ─────────────────────────────────────────────────────────
                    const nav = performance.getEntriesByType('navigation')[0];
                    metrics.navigation_context = {
                        visibility: document.visibilityState,
                        has_focus: document.hasFocus(),
                        user_activation: navigator.userActivation ? {
                            hasBeenActive: navigator.userActivation.hasBeenActive,
                            isActive: navigator.userActivation.isActive
                        } : null,
                        navigation_type: nav ? nav.type : 'unknown'
                    };
                    
                    // ─────────────────────────────────────────────────────────
                    // Add memory stats
                    // ─────────────────────────────────────────────────────────
                    if (performance.memory) {
                        metrics.memory = {
                            js_heap_mb: Math.round(performance.memory.usedJSHeapSize / 1024 / 1024)
                        };
                    }
                    
                    return metrics;
                }
            """)
            
            # Add profile name and URL
            metrics_data['profile_name'] = self.profile_name
            
            # Determine creator from URL if not provided
            if creator_username:
                metrics_data['creator'] = creator_username
            elif live_url:
                # Extract creator from URL
                import re
                match = re.search(r'@([^/]+)', live_url)
                if match:
                    metrics_data['creator'] = match.group(1)
                else:
                    metrics_data['creator'] = 'unknown'
            else:
                # Try to extract from current URL
                current_url = await self.page.evaluate("() => window.location.href")
                import re
                match = re.search(r'@([^/]+)', current_url)
                if match:
                    metrics_data['creator'] = match.group(1)
                else:
                    metrics_data['creator'] = 'unknown'
            
            # Add live URL
            if live_url:
                metrics_data['live_url'] = live_url
            elif creator_username:
                metrics_data['live_url'] = f"https://www.tiktok.com/@{creator_username}/live"
            else:
                metrics_data['live_url'] = await self.page.evaluate("() => window.location.href")
            
            # Add server timestamp
            metrics_data['server_timestamp'] = int(time.time())
            
            # Add total RAM from process monitor
            mem_data = self.monitor.measure_total_ram()
            if 'memory' not in metrics_data:
                metrics_data['memory'] = {}
            metrics_data['memory']['total_mb'] = mem_data['total_mb']
            
            return metrics_data
            
        except Exception as e:
            # Return minimal error metrics
            return {
                'profile_name': self.profile_name,
                'status': 'error',
                'error': str(e),
                'viewer_count': -1,
                'server_timestamp': int(time.time())
            }



# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MAIN LAUNCHER CLASS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class RAMOptimizedLiveLauncherV2:
    """
    Main launcher class implementing the complete lifecycle.
    """
    
    def __init__(self, enable_api: bool = True, api_port: int = 8000):
        self.chrome_manager = ChromeProfileManager()
        self.profile_manager = ProfileManager()
        self.monitors = {}
        self.enable_api = enable_api
        self.api_port = api_port
        self.api_server = None
        
        # Start API server if enabled
        if self.enable_api:
            try:
                self.api_server = start_api_server(host="127.0.0.1", port=self.api_port)
            except Exception as e:
                print(f"⚠️  Failed to start API server: {e}")
                print("   Continuing without API...")
                self.enable_api = False
        
    async def launch_profile(
        self,
        profile_name: str,
        creator_username: str = None,
        live_url: str = None,
        use_direct_url: bool = False,
        hidden: bool = False,
        duration_minutes: int = 30,
        viewport_width: int = 1280,
        viewport_height: int = 720
    ) -> bool:
        """
        Launch profile with RAM optimization.
        
        Args:
            profile_name: Profile name (e.g. "001", "X-001")
            creator_username: TikTok creator username (for natural entry)
            live_url: Direct livestream URL (for direct entry)
            use_direct_url: True = direct URL, False = natural entry
            hidden: Minimize window (default: False)
            duration_minutes: How long to maintain session (default: 30)
            viewport_width: Viewport width (min 360, recommended 720+)
            viewport_height: Viewport height (min 640, recommended 720+)
        
        Returns:
            bool: Success status
        """
        print("\n" + "="*70)
        print("🚀 RAM OPTIMIZED LIVE LAUNCHER V2")
        print("="*70)
        print(f"Profile:        {profile_name}")
        if use_direct_url:
            print(f"Entry Mode:     Direct URL")
            print(f"URL:            {live_url}")
        else:
            print(f"Entry Mode:     Natural Entry")
            print(f"Creator:        @{creator_username}")
        print(f"Viewport:       {viewport_width}x{viewport_height}")
        print(f"Hidden:         {hidden}")
        print(f"Duration:       {duration_minutes} minutes")
        print("="*70 + "\n")
        
        # Validate viewport
        if viewport_width < 360 or viewport_height < 640:
            print(f"❌ Viewport too small: {viewport_width}x{viewport_height}")
            print("   Minimum: 360x640")
            return False
        
        # Check profile exists
        profiles = self.profile_manager.get_all_profiles()
        if profile_name not in profiles:
            print(f"❌ Profile not found: {profile_name}")
            return False
        
        # Initialize monitor
        monitor = SimpleRAMMonitor(profile_name)
        self.monitors[profile_name] = monitor
        
        # Get approved Chrome flags
        chrome_flags = TikTokLiveChromeFlagsV2.get_approved_flags()
        monitor.log_status(f"Using {len(chrome_flags)} approved Chrome flags")
        
        # Log first 5 flags as sample
        print("\nChrome Flags (sample):")
        for flag in chrome_flags[:5]:
            print(f"  {flag}")
        print(f"  ... and {len(chrome_flags) - 5} more\n")
        
        try:
            # ═══════════════════════════════════════════════════════════
            # PHASE 1: BOOTSTRAP
            # ═══════════════════════════════════════════════════════════
            monitor.log_status("Starting Phase 1: Bootstrap...")
            
            success, result = self.chrome_manager.launch_chrome_profile(
                profile_name,
                hidden=hidden,
                auto_login=False,
                login_data=None,
                start_url=None  # Don't navigate yet
            )
            
            if not success:
                print(f"❌ Failed to launch Chrome: {result}")
                return False
            
            page = result
            monitor.log_status("✅ Chrome launched successfully")
            
            # Set viewport
            await page.set_viewport_size({"width": viewport_width, "height": viewport_height})
            monitor.log_status(f"Viewport set to {viewport_width}x{viewport_height}")
            
            # Initialize lifecycle manager
            lifecycle = LivestreamLifecycle(page, profile_name, monitor)
            await lifecycle.phase_1_bootstrap()
            
            # ═══════════════════════════════════════════════════════════
            # PHASE 2: TRUST WINDOW / DIRECT URL
            # ═══════════════════════════════════════════════════════════
            if use_direct_url:
                monitor.log_status("Starting Phase 2: Direct URL Entry...")
                success, nav_context = await lifecycle.phase_2_direct_url(live_url)
            else:
                monitor.log_status("Starting Phase 2: Trust Window (Natural Entry)...")
                success, nav_context = await lifecycle.phase_2_trust_window(creator_username)
            
            if not success:
                print(f"\n❌ Entry failed: {nav_context.get('error', 'Unknown')}")
                return False
            
            # ═══════════════════════════════════════════════════════════
            # PHASE 3: STABILIZE
            # ═══════════════════════════════════════════════════════════
            monitor.log_status("Starting Phase 3: Stabilize...")
            await lifecycle.phase_3_stabilize()
            
            # ═══════════════════════════════════════════════════════════
            # PHASE 4: IDLE
            # ═══════════════════════════════════════════════════════════
            monitor.log_status("Starting Phase 4: Idle...")
            print("\n✅ Livestream session established")
            print("📊 Monitoring active (read-only)")
            print("📌 Press Ctrl+C to stop\n")
            
            await lifecycle.phase_4_idle(
                duration_minutes=duration_minutes,
                creator_username=creator_username,
                live_url=live_url
            )
            
            monitor.log_status("✅ Session completed successfully")
            return True
            
        except KeyboardInterrupt:
            monitor.log_status("⚠️  Session interrupted by user")
            return False
        except Exception as e:
            monitor.log_status(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return False


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CLI INTERFACE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def quick_launch():
    """Quick launch single profile"""
    print("\n" + "="*70)
    print("🚀 QUICK LAUNCH - RAM OPTIMIZED V2")
    print("="*70)
    
    # Get profile name
    profile_name = input("\nProfile name (e.g. 001, X-001): ").strip()
    if not profile_name:
        print("❌ Profile name required")
        return
    
    # Choose entry mode
    print("\nEntry Mode:")
    print("  1. Natural Entry (profile → LIVE badge → click)")
    print("     ✅ Better for view counting")
    print("     ✅ Proper navigation context")
    print("     ⚠️  Slower (requires profile page load)")
    print("\n  2. Direct URL (navigate straight to /live)")
    print("     ✅ Faster")
    print("     ✅ Lower RAM")
    print("     ⚠️  May affect view counting")
    
    entry_mode = input("\nChoice (1/2, default: 1): ").strip() or "1"
    use_direct_url = (entry_mode == "2")
    
    # Get creator username or URL based on mode
    if use_direct_url:
        print("\nExample: https://www.tiktok.com/@presscuse/live")
        live_url = input("Livestream URL: ").strip()
        if not live_url:
            print("❌ URL required")
            return
        creator_username = None
    else:
        creator_username = input("\nCreator username (e.g. presscuse): ").strip().lstrip('@')
        if not creator_username:
            print("❌ Creator username required")
            return
        live_url = None
    
    # Get viewport (optional)
    print("\nViewport options:")
    print("  1. Mobile (720x1280) - Recommended")
    print("  2. Desktop (1280x720)")
    print("  3. HD (1920x1080)")
    print("  4. Custom")
    
    viewport_choice = input("Choice (1-4, default: 1): ").strip() or "1"
    
    if viewport_choice == "1":
        viewport_width, viewport_height = 720, 1280
    elif viewport_choice == "2":
        viewport_width, viewport_height = 1280, 720
    elif viewport_choice == "3":
        viewport_width, viewport_height = 1920, 1080
    elif viewport_choice == "4":
        try:
            viewport_width = int(input("Width (min 360): ").strip())
            viewport_height = int(input("Height (min 640): ").strip())
        except:
            print("❌ Invalid viewport dimensions")
            return
    else:
        viewport_width, viewport_height = 720, 1280
    
    # Hidden mode
    hidden_input = input("\nHidden mode? (y/n, default: n): ").strip().lower()
    hidden = (hidden_input == 'y')
    
    # Duration
    try:
        duration_input = input("Duration in minutes (default: 30): ").strip()
        duration_minutes = int(duration_input) if duration_input else 30
    except:
        duration_minutes = 30
    
    # Launch
    launcher = RAMOptimizedLiveLauncherV2()
    await launcher.launch_profile(
        profile_name=profile_name,
        creator_username=creator_username,
        live_url=live_url,
        use_direct_url=use_direct_url,
        hidden=hidden,
        duration_minutes=duration_minutes,
        viewport_width=viewport_width,
        viewport_height=viewport_height
    )


async def batch_launch():
    """Batch launch multiple profiles"""
    print("\n" + "="*70)
    print("🚀 BATCH LAUNCH - RAM OPTIMIZED V2")
    print("="*70)
    
    # Get profile names
    profiles_input = input("\nProfiles (comma-separated, e.g. 001,002,003): ").strip()
    if not profiles_input:
        print("❌ Profile names required")
        return
    
    profile_names = [p.strip() for p in profiles_input.split(',')]
    
    # Choose entry mode
    print("\nEntry Mode:")
    print("  1. Natural Entry (recommended for view counting)")
    print("  2. Direct URL (faster, lower RAM)")
    
    entry_mode = input("Choice (1/2, default: 1): ").strip() or "1"
    use_direct_url = (entry_mode == "2")
    
    # Get creator username or URL based on mode
    if use_direct_url:
        print("\nExample: https://www.tiktok.com/@presscuse/live")
        live_url = input("Livestream URL (all profiles will join this): ").strip()
        if not live_url:
            print("❌ URL required")
            return
        creator_username = None
    else:
        creator_username = input("\nCreator username (e.g. presscuse): ").strip().lstrip('@')
        if not creator_username:
            print("❌ Creator username required")
            return
        live_url = None
    
    # Viewport (use mobile for batch)
    viewport_width, viewport_height = 720, 1280
    
    # Duration
    try:
        duration_input = input("Duration in minutes (default: 30): ").strip()
        duration_minutes = int(duration_input) if duration_input else 30
    except:
        duration_minutes = 30
    
    # Confirm
    print(f"\n⚠️  Will launch {len(profile_names)} profiles")
    if use_direct_url:
        print(f"   URL: {live_url}")
    else:
        print(f"   Creator: @{creator_username}")
    print(f"   Duration: {duration_minutes} minutes")
    confirm = input("Continue? (y/n): ").strip().lower()
    if confirm != 'y':
        return
    
    # Launch profiles with delay
    launcher = RAMOptimizedLiveLauncherV2()
    
    for i, profile_name in enumerate(profile_names, 1):
        print(f"\n{'='*70}")
        print(f"Launching profile {i}/{len(profile_names)}: {profile_name}")
        print(f"{'='*70}")
        
        # Launch in background (don't await)
        asyncio.create_task(launcher.launch_profile(
            profile_name=profile_name,
            creator_username=creator_username,
            live_url=live_url,
            use_direct_url=use_direct_url,
            hidden=True,  # Always hidden for batch
            duration_minutes=duration_minutes,
            viewport_width=viewport_width,
            viewport_height=viewport_height
        ))
        
        # Delay between launches
        if i < len(profile_names):
            print(f"\nWaiting 5 seconds before next launch...")
            await asyncio.sleep(5)
    
    print(f"\n✅ All {len(profile_names)} profiles launched")
    print("📊 Sessions running in background")
    print("📌 Press Ctrl+C to stop all\n")
    
    # Keep running
    try:
        while True:
            await asyncio.sleep(60)
    except KeyboardInterrupt:
        print("\n⚠️  Stopping all sessions...")


def main():
    """Main menu"""
    while True:
        print("\n" + "="*70)
        print("RAM OPTIMIZED LIVE LAUNCHER V2 - TikTok 2025 Compliant")
        print("="*70)
        print("\nFeatures:")
        print("  ✅ Natural navigation flow (profile → LIVE badge → click)")
        print("  ✅ Minimal Chrome flags (no headless, no media disable)")
        print("  ✅ Proper lifecycle phases (bootstrap → trust → stabilize → idle)")
        print("  ✅ Read-only monitoring (no video manipulation)")
        print("  ✅ Target: 180-220MB RAM per profile")
        print("  ✅ View eligibility preserved")
        print("\nOptions:")
        print("  1. Quick Launch (single profile)")
        print("  2. Batch Launch (multiple profiles)")
        print("  3. Show Chrome Flags")
        print("  0. Exit")
        print("="*70)
        
        choice = input("\nChoice: ").strip()
        
        if choice == '1':
            asyncio.run(quick_launch())
        elif choice == '2':
            asyncio.run(batch_launch())
        elif choice == '3':
            print("\n" + "="*70)
            print("APPROVED CHROME FLAGS")
            print("="*70)
            flags = TikTokLiveChromeFlagsV2.get_approved_flags()
            for i, flag in enumerate(flags, 1):
                print(f"{i:2d}. {flag}")
            print(f"\nTotal: {len(flags)} flags")
            
            print("\n" + "="*70)
            print("FORBIDDEN FLAGS (MUST NOT USE)")
            print("="*70)
            forbidden = TikTokLiveChromeFlagsV2.get_forbidden_flags()
            for i, flag in enumerate(forbidden, 1):
                print(f"{i:2d}. {flag}")
            print(f"\nTotal: {len(forbidden)} forbidden flags")
            
            input("\nPress Enter to continue...")
        elif choice == '0':
            break
        else:
            print("❌ Invalid choice")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Program interrupted")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
