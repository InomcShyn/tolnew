#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Run Manual Baseline - Script đơn giản để thu thập baseline từ manual start

Cách dùng:
1. Chạy script này
2. Nhập profile ID và URL TikTok LIVE
3. Chrome sẽ mở (dùng browser_manager)
4. Tự tay navigate và xem LIVE
5. Nhấn Enter để thu thập baseline
"""

import asyncio
import sys
from pathlib import Path

# Add to path
sys.path.insert(0, str(Path(__file__).parent))

from core.managers.browser_manager import BrowserManager
from analysis.manual_start_baseline import collect_manual_baseline


async def run_manual_baseline():
    """Chạy manual baseline collection"""
    
    print("\n" + "="*70)
    print("MANUAL BASELINE COLLECTION")
    print("="*70 + "\n")
    
    # Get profile info
    profile_id = input("Enter profile ID (e.g., 001): ").strip()
    if not profile_id:
        print("❌ Profile ID required")
        return
    
    live_url = input("Enter TikTok LIVE URL: ").strip()
    if not live_url:
        print("❌ URL required")
        return
    
    print(f"\n{'='*70}")
    print("LAUNCHING CHROME")
    print(f"{'='*70}\n")
    print(f"Profile: {profile_id}")
    print(f"URL: {live_url}")
    print()
    
    # Get profile path
    profile_path = Path(f"chrome_profiles/{profile_id}")
    if not profile_path.exists():
        print(f"❌ Profile not found: {profile_path}")
        return
    
    print(f"✅ Profile found: {profile_path}")
    print()
    
    # Launch Chrome
    async with async_playwright() as p:
        print("[CHROME] Launching...")
        
        # Get Chrome path from GPM
        import json
        gpm_config_path = Path("gpm_config.json")
        chrome_path = None
        
        if gpm_config_path.exists():
            with open(gpm_config_path, 'r', encoding='utf-8') as f:
                gpm_config = json.load(f)
                profiles = gpm_config.get('profiles', [])
                for prof in profiles:
                    if prof.get('id') == profile_id:
                        chrome_version = prof.get('chrome_version', '119.0.6045.124')
                        chrome_path = f"C:\\Users\\admin\\AppData\\Local\\Programs\\GPMLogin\\gpm_browser\\gpm_browser_chromium_core_{chrome_version.split('.')[0]}\\chrome.exe"
                        break
        
        if not chrome_path or not Path(chrome_path).exists():
            # Fallback to default Chrome
            chrome_path = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
            if not Path(chrome_path).exists():
                chrome_path = None
        
        # Launch args
        args = [
            f'--user-data-dir={profile_path.absolute()}',
            '--no-first-run',
            '--no-default-browser-check',
            '--disable-blink-features=AutomationControlled',
            '--disable-features=IsolateOrigins,site-per-process',
        ]
        
        try:
            # Use launch_persistent_context for user data dir
            print(f"[CHROME] Using profile: {profile_path.absolute()}")
            if chrome_path:
                print(f"[CHROME] Using Chrome: {chrome_path}")
            
            # Launch args without user-data-dir (will be passed as parameter)
            launch_args = [
                '--no-first-run',
                '--no-default-browser-check',
                '--disable-blink-features=AutomationControlled',
                '--disable-features=IsolateOrigins,site-per-process',
            ]
            
            if chrome_path:
                context = await p.chromium.launch_persistent_context(
                    user_data_dir=str(profile_path.absolute()),
                    executable_path=chrome_path,
                    headless=False,
                    args=launch_args
                )
            else:
                context = await p.chromium.launch_persistent_context(
                    user_data_dir=str(profile_path.absolute()),
                    headless=False,
                    args=launch_args
                )
            
            print("[CHROME] ✅ Launched")
            
            # Get page
            page = context.pages[0] if context.pages else await context.new_page()
            
            print(f"[CHROME] Navigating to: {live_url}")
            await page.goto(live_url, wait_until='domcontentloaded', timeout=30000)
            
            print("\n" + "="*70)
            print("MANUAL INTERACTION REQUIRED")
            print("="*70)
            print("\nPlease:")
            print("1. ✅ Make sure you are logged in")
            print("2. ✅ Navigate to TikTok LIVE if not already there")
            print("3. ✅ Make sure video is playing")
            print("4. ✅ Wait for WebSocket to connect (a few seconds)")
            print("5. ✅ Verify you can hear audio")
            print()
            print("When ready, press Enter to collect baseline...")
            
            input()
            
            # Collect baseline
            print("\n" + "="*70)
            print("COLLECTING BASELINE")
            print("="*70 + "\n")
            
            try:
                await collect_manual_baseline(profile_id, page)
                
                print("\n" + "="*70)
                print("✅ BASELINE COLLECTED SUCCESSFULLY")
                print("="*70)
                print("\nFiles created:")
                print(f"  - analysis/manual_start_baseline_{profile_id}_*.json")
                print(f"  - analysis/manual_start_baseline_latest.json")
                print()
                print("Next steps:")
                print("1. Run AUTO mode: python launch_livestream_tiktok.py")
                print("2. Compare: python analysis/run_comparison.py")
                print()
                
            except Exception as e:
                print(f"\n❌ Error collecting baseline: {e}")
                import traceback
                traceback.print_exc()
            
            # Keep browser open
            print("Press Enter to close Chrome...")
            input()
            
            await context.close()
            
        except Exception as e:
            print(f"\n❌ Error launching Chrome: {e}")
            import traceback
            traceback.print_exc()


def main():
    """Main function"""
    
    print("\n" + "="*70)
    print("MANUAL BASELINE COLLECTION TOOL")
    print("="*70)
    print("\nThis tool helps you collect baseline data from manual Chrome start.")
    print("\nWhat it does:")
    print("  1. Launches Chrome with your profile")
    print("  2. Opens TikTok LIVE URL")
    print("  3. Waits for you to verify everything works")
    print("  4. Collects baseline data")
    print("\nWhat you need:")
    print("  ✅ Profile already logged in to TikTok")
    print("  ✅ A TikTok LIVE URL to test")
    print("  ✅ A few minutes to verify")
    print("\n" + "="*70 + "\n")
    
    try:
        asyncio.run(run_manual_baseline())
    except KeyboardInterrupt:
        print("\n\n👋 Cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
