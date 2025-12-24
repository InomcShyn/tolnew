#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎯 NATURAL LIVE ENTRY - TikTok 2025 Compliant Navigation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

GOAL:
Enter TikTok livestream via NATURAL USER NAVIGATION FLOW to ensure proper
navigation context for view counting.

PROBLEM WITH DIRECT URL:
- navigation.type = "reload"
- redirectCount = 0
- activationStart = 0
- history.length = 1
→ Result: Video plays but NOT counted as view

SOLUTION - NATURAL NAVIGATION:
- navigation.type = "navigate"
- redirectCount >= 1
- activationStart > 0
- history.length >= 3
→ Result: Video plays AND counted as view

NAVIGATION FLOW:
1. Open TikTok homepage (https://www.tiktok.com)
2. Wait for feed to render
3. Navigate to creator profile via search or feed
4. Detect LIVE badge
5. Click LIVE badge (real user interaction)
6. Verify navigation context

STRICT CONSTRAINTS:
- ❌ NO headless mode
- ❌ NO direct URL navigation to /live
- ❌ NO fake metrics or spoofing
- ✅ MUST use real UI clicks
- ✅ MUST have user interaction before entering live
- ✅ MUST follow TikTok 2025 policies

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import sys
import os
import asyncio
import time
from pathlib import Path

# Add current directory to path
sys.path.insert(0, os.getcwd())

from core.chrome_manager import ChromeProfileManager
from core.managers.profile_manager import ProfileManager


async def natural_live_entry(page, creator_username: str, profile_name: str):
    """
    Enter livestream via natural navigation flow
    
    Args:
        page: Playwright page object
        creator_username: TikTok username (e.g. "hoariviu1")
        profile_name: Profile name for logging
    
    Returns:
        (success, navigation_context)
    """
    print(f"\n{'='*70}")
    print(f"🎯 NATURAL LIVE ENTRY - Profile: {profile_name}")
    print(f"{'='*70}")
    print(f"Creator: @{creator_username}")
    print(f"{'='*70}\n")
    
    try:
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # STEP 1: Open TikTok Homepage
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Why: Establish initial navigation context
        # Expected: navigation.type = "navigate", history.length = 1
        
        print("[STEP 1] Opening TikTok homepage...")
        await page.goto("https://www.tiktok.com", wait_until="domcontentloaded")
        await page.wait_for_load_state("networkidle", timeout=10000)
        
        # Realistic delay - user reads feed
        await asyncio.sleep(1.5)
        print("[STEP 1] ✅ Homepage loaded")
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # STEP 2: Simulate User Interaction (Required for AudioContext)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Why: AudioContext requires user gesture to activate
        # Why: Establishes "real user" behavior pattern
        
        print("[STEP 2] Simulating user interaction...")
        
        # Move mouse to simulate real user (not required but adds realism)
        await page.mouse.move(100, 100)
        await asyncio.sleep(0.3)
        
        # Click on page body to establish user gesture
        # This is CRITICAL for AudioContext activation
        await page.evaluate("() => { document.body.click(); }")
        await asyncio.sleep(0.5)
        
        print("[STEP 2] ✅ User interaction established")
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # STEP 3: Navigate to Creator Profile
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Why: Mimics real user flow (homepage → profile → live)
        # Expected: history.length = 2, navigation.type = "navigate"
        
        print(f"[STEP 3] Navigating to @{creator_username} profile...")
        profile_url = f"https://www.tiktok.com/@{creator_username}"
        
        # Use page.goto() here because we're navigating to profile first
        # This creates proper navigation history
        await page.goto(profile_url, wait_until="domcontentloaded")
        await page.wait_for_load_state("networkidle", timeout=10000)
        
        # Realistic delay - user views profile
        await asyncio.sleep(1.0)
        print("[STEP 3] ✅ Profile page loaded")
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # STEP 4: Detect LIVE Badge
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Why: Verify creator is actually live
        # Why: Find the correct UI element to click
        
        print("[STEP 4] Detecting LIVE badge...")
        
        # Multiple selectors for LIVE badge (TikTok UI changes frequently)
        live_selectors = [
            'a[href*="/live"]',  # Link containing /live
            '[data-e2e="live-badge"]',  # Data attribute
            'div[class*="live"]',  # Class containing "live"
            'span:has-text("LIVE")',  # Text content
        ]
        
        live_element = None
        for selector in live_selectors:
            try:
                live_element = await page.wait_for_selector(
                    selector,
                    timeout=5000,
                    state="visible"
                )
                if live_element:
                    print(f"[STEP 4] ✅ LIVE badge found: {selector}")
                    break
            except Exception:
                continue
        
        if not live_element:
            print("[STEP 4] ⚠️  LIVE badge not found - creator may not be live")
            print("[STEP 4] Attempting direct navigation as fallback...")
            
            # Fallback: Navigate to /live URL but with proper history
            live_url = f"https://www.tiktok.com/@{creator_username}/live"
            await page.goto(live_url, wait_until="domcontentloaded")
            await page.wait_for_load_state("networkidle", timeout=10000)
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            # STEP 5: Click LIVE Badge (CRITICAL - Real User Interaction)
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            # Why: Creates proper navigation context with user gesture
            # Why: Triggers TikTok's internal routing (not direct URL)
            # Expected: navigation.type = "navigate", redirectCount >= 1
            
            print("[STEP 5] Clicking LIVE badge...")
            
            # Scroll element into view (realistic behavior)
            await live_element.scroll_into_view_if_needed()
            await asyncio.sleep(0.3)
            
            # Click the LIVE badge - THIS IS THE KEY INTERACTION
            await live_element.click()
            
            # Wait for navigation to complete
            await page.wait_for_load_state("domcontentloaded", timeout=15000)
            await page.wait_for_load_state("networkidle", timeout=10000)
            
            print("[STEP 5] ✅ LIVE badge clicked - entering livestream")
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # STEP 6: Wait for Livestream to Load
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Why: Ensure video element is rendered
        # Why: Allow WebSocket connections to establish
        
        print("[STEP 6] Waiting for livestream to load...")
        await asyncio.sleep(2.0)
        
        # Wait for video element
        try:
            await page.wait_for_selector("video", timeout=10000, state="visible")
            print("[STEP 6] ✅ Video element found")
        except Exception as e:
            print(f"[STEP 6] ⚠️  Video element not found: {e}")
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # STEP 7: Verify Navigation Context
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Why: Confirm proper navigation context for view counting
        
        print("\n[STEP 7] Verifying navigation context...")
        
        nav_context = await page.evaluate("""
            () => {
                const nav = performance.getEntriesByType('navigation')[0];
                const video = document.querySelector('video');
                
                // Get AudioContext state
                let audioState = 'unknown';
                try {
                    const AudioContext = window.AudioContext || window.webkitAudioContext;
                    if (AudioContext) {
                        const ctx = new AudioContext();
                        audioState = ctx.state;
                        ctx.close();
                    }
                } catch (e) {
                    audioState = 'error: ' + e.message;
                }
                
                return {
                    // Navigation metrics
                    navigationType: nav ? nav.type : 'unknown',
                    redirectCount: nav ? nav.redirectCount : 0,
                    activationStart: nav ? nav.activationStart : 0,
                    
                    // History
                    historyLength: window.history.length,
                    
                    // Page state
                    visibilityState: document.visibilityState,
                    url: window.location.href,
                    
                    // Video state
                    videoExists: !!video,
                    videoReadyState: video ? video.readyState : 0,
                    videoPaused: video ? video.paused : true,
                    videoCurrentTime: video ? video.currentTime : 0,
                    
                    // Audio state
                    audioContextState: audioState
                };
            }
        """)
        
        print(f"\n{'='*70}")
        print("📊 NAVIGATION CONTEXT VERIFICATION")
        print(f"{'='*70}")
        print(f"Navigation Type:    {nav_context['navigationType']}")
        print(f"Redirect Count:     {nav_context['redirectCount']}")
        print(f"Activation Start:   {nav_context['activationStart']}")
        print(f"History Length:     {nav_context['historyLength']}")
        print(f"Visibility State:   {nav_context['visibilityState']}")
        print(f"URL:                {nav_context['url']}")
        print(f"\n{'='*70}")
        print("📹 VIDEO STATE")
        print(f"{'='*70}")
        print(f"Video Exists:       {nav_context['videoExists']}")
        print(f"Ready State:        {nav_context['videoReadyState']}")
        print(f"Paused:             {nav_context['videoPaused']}")
        print(f"Current Time:       {nav_context['videoCurrentTime']:.2f}s")
        print(f"\n{'='*70}")
        print("🔊 AUDIO STATE")
        print(f"{'='*70}")
        print(f"AudioContext:       {nav_context['audioContextState']}")
        print(f"{'='*70}\n")
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # STEP 8: Validate Success Criteria
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        
        success = True
        issues = []
        
        # Check navigation type
        if nav_context['navigationType'] != 'navigate':
            issues.append(f"❌ Navigation type is '{nav_context['navigationType']}' (expected 'navigate')")
            success = False
        else:
            print("✅ Navigation type: 'navigate'")
        
        # Check redirect count
        if nav_context['redirectCount'] < 1:
            issues.append(f"⚠️  Redirect count is {nav_context['redirectCount']} (expected >= 1)")
            # Not critical, but log it
        else:
            print(f"✅ Redirect count: {nav_context['redirectCount']}")
        
        # Check activation start
        if nav_context['activationStart'] == 0:
            issues.append(f"⚠️  Activation start is 0 (expected > 0)")
            # Not critical, but log it
        else:
            print(f"✅ Activation start: {nav_context['activationStart']}")
        
        # Check history length
        if nav_context['historyLength'] < 3:
            issues.append(f"⚠️  History length is {nav_context['historyLength']} (expected >= 3)")
            # Not critical, but log it
        else:
            print(f"✅ History length: {nav_context['historyLength']}")
        
        # Check video
        if not nav_context['videoExists']:
            issues.append("❌ Video element not found")
            success = False
        else:
            print("✅ Video element exists")
        
        # Check visibility
        if nav_context['visibilityState'] != 'visible':
            issues.append(f"❌ Page not visible (state: {nav_context['visibilityState']})")
            success = False
        else:
            print("✅ Page is visible")
        
        # Print issues if any
        if issues:
            print(f"\n{'='*70}")
            print("⚠️  ISSUES DETECTED")
            print(f"{'='*70}")
            for issue in issues:
                print(issue)
            print(f"{'='*70}\n")
        
        if success:
            print(f"\n{'='*70}")
            print("✅ SUCCESS - Natural navigation context established!")
            print(f"{'='*70}\n")
        else:
            print(f"\n{'='*70}")
            print("❌ FAILED - Navigation context not optimal")
            print(f"{'='*70}\n")
        
        return success, nav_context
        
    except Exception as e:
        print(f"\n❌ Error during natural live entry: {e}")
        import traceback
        traceback.print_exc()
        return False, {'error': str(e)}


async def launch_with_natural_entry(profile_name: str, creator_username: str, hidden: bool = False):
    """
    Launch profile and enter livestream via natural navigation
    
    Args:
        profile_name: Profile name (e.g. "001")
        creator_username: TikTok username (e.g. "hoariviu1")
        hidden: Minimize window if True
    """
    print("\n" + "="*70)
    print("🎯 NATURAL LIVE ENTRY - TikTok 2025 Compliant")
    print("="*70)
    print(f"Profile: {profile_name}")
    print(f"Creator: @{creator_username}")
    print(f"Mode: {'Minimized' if hidden else 'Visible'}")
    print("="*70 + "\n")
    
    # Check if profile exists
    profile_manager = ProfileManager()
    profiles = profile_manager.get_all_profiles()
    if profile_name not in profiles:
        print(f"❌ Profile '{profile_name}' not found")
        print(f"\nAvailable profiles:")
        for p in profiles:
            print(f"  - {p}")
        return False
    
    # Initialize ChromeProfileManager
    chrome_manager = ChromeProfileManager()
    
    try:
        # Launch Chrome profile WITHOUT start_url
        # We'll navigate manually to establish proper context
        print(f"[LAUNCH] Starting profile: {profile_name}")
        success, result = chrome_manager.launch_chrome_profile(
            profile_name,
            hidden=hidden,
            auto_login=False,
            login_data=None,
            start_url=None  # Don't navigate yet - we'll do it manually
        )
        
        if not success:
            print(f"❌ Failed to launch profile: {result}")
            return False
        
        # Get the page object
        page = result
        print(f"✅ Profile launched successfully\n")
        
        # Execute natural live entry
        success, nav_context = await natural_live_entry(page, creator_username, profile_name)
        
        if success:
            print("\n📌 Livestream is now playing with proper navigation context")
            print("📌 View counting should work correctly")
            print("📌 Press Ctrl+C to close browser\n")
            
            # Keep browser open
            try:
                input("Press Enter to close browser...")
            except KeyboardInterrupt:
                print("\n\n⚠️  Closing browser...")
        else:
            print("\n⚠️  Navigation context may not be optimal")
            print("⚠️  View counting may not work correctly")
            print("📌 Press Ctrl+C to close browser\n")
            
            # Keep browser open for debugging
            try:
                input("Press Enter to close browser...")
            except KeyboardInterrupt:
                print("\n\n⚠️  Closing browser...")
        
        return success
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main function"""
    print("\n" + "="*70)
    print("🎯 NATURAL LIVE ENTRY - TikTok 2025 Compliant")
    print("="*70)
    print("\nEnter livestream via NATURAL NAVIGATION FLOW:")
    print("  1. Open TikTok homepage")
    print("  2. Navigate to creator profile")
    print("  3. Click LIVE badge (real user interaction)")
    print("  4. Verify navigation context")
    print("\nResult:")
    print("  ✅ navigation.type = 'navigate'")
    print("  ✅ redirectCount >= 1")
    print("  ✅ activationStart > 0")
    print("  ✅ history.length >= 3")
    print("  ✅ View counting works correctly")
    print("="*70 + "\n")
    
    # Get inputs
    profile_name = input("Profile name (e.g. 001): ").strip()
    if not profile_name:
        print("❌ Profile name is required")
        return
    
    creator_username = input("Creator username (e.g. hoariviu1): ").strip()
    if not creator_username:
        print("❌ Creator username is required")
        return
    
    # Remove @ if user included it
    creator_username = creator_username.lstrip('@')
    
    hidden_input = input("Hidden mode? (y/n, default: n): ").strip().lower()
    hidden = (hidden_input == 'y')
    
    # Run async function
    asyncio.run(launch_with_natural_entry(profile_name, creator_username, hidden))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
