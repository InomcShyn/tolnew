#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Natural Live Entry with Direct URL Support
Supports both username and full live URL
"""

import asyncio
import sys
import re
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from core.chrome_manager import ChromeProfileManager


async def launch_with_direct_url(profile_name: str, live_url: str, hidden: bool = False):
    """
    Launch profile and navigate directly to live URL
    
    Args:
        profile_name: Profile name (e.g. "001" or "X-001")
        live_url: Full live URL (e.g. https://www.tiktok.com/@username/live?...)
        hidden: Whether to run in hidden mode
    """
    
    # Extract username from URL for display
    username_match = re.search(r'@([^/]+)/live', live_url)
    creator_username = username_match.group(1) if username_match else "unknown"
    
    print("\n" + "="*70)
    print("🎯 NATURAL LIVE ENTRY - Direct URL Mode")
    print("="*70)
    print(f"Profile: {profile_name}")
    print(f"Creator: @{creator_username}")
    print(f"URL: {live_url}")
    print(f"Mode: {'Hidden' if hidden else 'Visible'}")
    print("="*70)
    
    # Initialize Chrome manager
    manager = ChromeProfileManager()
    
    # Launch profile
    print(f"\n[LAUNCH] Starting profile: {profile_name}")
    success, page = manager.launch_chrome_profile(
        profile_name,
        hidden=hidden,
        start_url="https://www.tiktok.com"
    )
    
    if not success:
        print("❌ Failed to launch profile")
        return
    
    print("✅ Profile launched successfully")
    
    try:
        print("\n" + "="*70)
        print(f"🎯 NATURAL LIVE ENTRY - Profile: {profile_name}")
        print("="*70)
        print(f"Creator: @{creator_username}")
        print("="*70)
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # STEP 1: Open TikTok Homepage
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        print("\n[STEP 1] Opening TikTok homepage...")
        await page.goto("https://www.tiktok.com", wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_load_state("networkidle", timeout=10000)
        print("[STEP 1] ✅ Homepage loaded")
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # STEP 2: Simulate User Interaction
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        print("\n[STEP 2] Simulating user interaction...")
        await asyncio.sleep(1.0)
        
        # Scroll a bit (realistic behavior)
        await page.evaluate("window.scrollBy(0, 300)")
        await asyncio.sleep(0.5)
        await page.evaluate("window.scrollBy(0, -100)")
        await asyncio.sleep(0.5)
        
        print("[STEP 2] ✅ User interaction established")
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # STEP 3: Navigate to Live URL
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        print(f"\n[STEP 3] Navigating to live URL...")
        print(f"[STEP 3] URL: {live_url}")
        
        await page.goto(live_url, wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_load_state("networkidle", timeout=10000)
        
        print("[STEP 3] ✅ Live URL loaded")
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # STEP 4: Wait for Livestream to Load
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        print("\n[STEP 4] Waiting for livestream to load...")
        await asyncio.sleep(2.0)
        
        # Wait for video element
        try:
            await page.wait_for_selector("video", timeout=10000, state="visible")
            print("[STEP 4] ✅ Video element found")
        except Exception as e:
            print(f"[STEP 4] ⚠️  Video element not found: {e}")
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # STEP 5: Verify Navigation Context
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        print("\n[STEP 5] Verifying navigation context...")
        
        nav_context = await page.evaluate("""
            () => {
                const nav = performance.getEntriesByType('navigation')[0];
                const video = document.querySelector('video');
                
                return {
                    navigationType: nav ? nav.type : 'unknown',
                    redirectCount: nav ? nav.redirectCount : 0,
                    activationStart: nav ? nav.activationStart : 0,
                    historyLength: window.history.length,
                    visibilityState: document.visibilityState,
                    url: window.location.href,
                    videoExists: !!video,
                    videoReadyState: video ? video.readyState : 0,
                    videoPaused: video ? video.paused : true,
                    videoCurrentTime: video ? video.currentTime : 0
                };
            }
        """)
        
        # Display results
        print("\n" + "="*70)
        print("📊 NAVIGATION CONTEXT VERIFICATION")
        print("="*70)
        print(f"Navigation Type:    {nav_context['navigationType']}")
        print(f"Redirect Count:     {nav_context['redirectCount']}")
        print(f"Activation Start:   {nav_context['activationStart']}")
        print(f"History Length:     {nav_context['historyLength']}")
        print(f"Visibility State:   {nav_context['visibilityState']}")
        print(f"URL:                {nav_context['url']}")
        print("="*70)
        print("📹 VIDEO STATE")
        print("="*70)
        print(f"Video Exists:       {nav_context['videoExists']}")
        print(f"Ready State:        {nav_context['videoReadyState']}")
        print(f"Paused:             {nav_context['videoPaused']}")
        print(f"Current Time:       {nav_context['videoCurrentTime']:.2f}s")
        print("="*70)
        
        # Check for issues
        issues = []
        if nav_context['navigationType'] != 'navigate':
            issues.append(f"⚠️  Navigation type is '{nav_context['navigationType']}' (expected 'navigate')")
        if nav_context['redirectCount'] == 0:
            issues.append("⚠️  Redirect count is 0 (expected >= 1)")
        if nav_context['activationStart'] == 0:
            issues.append("⚠️  Activation start is 0 (expected > 0)")
        if not nav_context['videoExists']:
            issues.append("⚠️  Video element not found")
        if nav_context['visibilityState'] != 'visible':
            issues.append(f"⚠️  Page is not visible (state: {nav_context['visibilityState']})")
        
        if issues:
            print("\n⚠️  ISSUES DETECTED")
            print("="*70)
            for issue in issues:
                print(issue)
            print("="*70)
        
        # Success criteria
        success_criteria = [
            nav_context['navigationType'] == 'navigate',
            nav_context['historyLength'] >= 2,
            nav_context['videoExists'],
            nav_context['visibilityState'] == 'visible'
        ]
        
        if all(success_criteria):
            print("\n" + "="*70)
            print("✅ SUCCESS - Natural navigation context established!")
            print("="*70)
            print("📌 Livestream is now playing with proper navigation context")
            print("📌 View counting should work correctly")
            print("📌 Press Ctrl+C to close browser")
            print("="*70)
        else:
            print("\n" + "="*70)
            print("⚠️  WARNING - Some criteria not met")
            print("="*70)
            print("📌 Livestream may not count views properly")
            print("📌 Check issues above")
            print("="*70)
        
        # Keep browser open
        print("\nPress Enter to close browser...")
        input()
        
    except Exception as e:
        print(f"\n❌ Error during natural entry: {e}")
        import traceback
        traceback.print_exc()
        print("\nPress Enter to close browser...")
        input()


def main():
    """Main entry point"""
    print("\n" + "="*70)
    print("🎯 NATURAL LIVE ENTRY - Direct URL Mode")
    print("="*70 + "\n")
    
    # Get inputs
    profile_name = input("Profile name (e.g. 001): ").strip()
    if not profile_name:
        print("❌ Profile name is required")
        return
    
    live_url = input("Live URL (e.g. https://www.tiktok.com/@username/live?...): ").strip()
    if not live_url:
        print("❌ Live URL is required")
        return
    
    # Validate URL
    if not live_url.startswith('http'):
        print("❌ Invalid URL - must start with http:// or https://")
        return
    
    if '/live' not in live_url:
        print("❌ Invalid URL - must contain /live")
        return
    
    hidden_input = input("Hidden mode? (y/n, default: n): ").strip().lower()
    hidden = (hidden_input == 'y')
    
    # Run async function
    asyncio.run(launch_with_direct_url(profile_name, live_url, hidden))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
