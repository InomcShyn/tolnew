#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Collect Baseline Now - Script để thu thập baseline từ Chrome đang chạy

Cách dùng:
1. Mở Chrome thủ công (launcher.py hoặc manual)
2. Vào trang TikTok LIVE
3. Đảm bảo video đang chạy
4. Chạy script này
"""

import asyncio
import sys
from pathlib import Path

# Add to path
sys.path.insert(0, str(Path(__file__).parent))

from playwright.async_api import async_playwright


async def find_running_chrome():
    """Tìm Chrome đang chạy và connect"""
    
    print("\n" + "="*70)
    print("FINDING RUNNING CHROME")
    print("="*70 + "\n")
    
    try:
        async with async_playwright() as p:
            # Try to connect to existing Chrome
            # Thường Chrome debug port là 9222
            try:
                browser = await p.chromium.connect_over_cdp("http://localhost:9222")
                print("✅ Connected to Chrome on port 9222")
            except:
                print("❌ Cannot connect to Chrome on port 9222")
                print("\nMake sure Chrome is running with:")
                print("  --remote-debugging-port=9222")
                return None
            
            # Get contexts and pages
            contexts = browser.contexts
            if not contexts:
                print("❌ No browser contexts found")
                return None
            
            print(f"✅ Found {len(contexts)} context(s)")
            
            # Find TikTok page
            for context in contexts:
                pages = context.pages
                print(f"   Context has {len(pages)} page(s)")
                
                for page in pages:
                    url = page.url
                    print(f"   - {url[:80]}")
                    
                    if 'tiktok.com' in url and '/live' in url:
                        print(f"\n✅ Found TikTok LIVE page!")
                        return page
            
            print("\n⚠️  No TikTok LIVE page found")
            print("   Please navigate to a TikTok LIVE page first")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


async def collect_from_running_chrome():
    """Thu thập baseline từ Chrome đang chạy"""
    
    # Find Chrome
    page = await find_running_chrome()
    
    if not page:
        print("\n" + "="*70)
        print("CANNOT PROCEED")
        print("="*70)
        print("\nPlease:")
        print("1. Start Chrome with: --remote-debugging-port=9222")
        print("2. Navigate to TikTok LIVE")
        print("3. Make sure video is playing")
        print("4. Run this script again")
        return
    
    # Get profile ID from user
    print("\n" + "="*70)
    print("COLLECT BASELINE")
    print("="*70 + "\n")
    
    profile_id = input("Enter profile ID (e.g., 001): ").strip()
    if not profile_id:
        profile_id = "manual"
    
    # Collect baseline
    from analysis.manual_start_baseline import collect_manual_baseline
    
    print(f"\nCollecting baseline for profile: {profile_id}")
    print("Please wait...\n")
    
    try:
        await collect_manual_baseline(profile_id, page)
        
        print("\n" + "="*70)
        print("✅ BASELINE COLLECTED SUCCESSFULLY")
        print("="*70)
        print("\nNext steps:")
        print("1. Run AUTO mode: python launch_livestream_tiktok.py")
        print("2. Compare: python analysis/run_comparison.py")
        
    except Exception as e:
        print(f"\n❌ Error collecting baseline: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Main function"""
    
    print("\n" + "="*70)
    print("MANUAL BASELINE COLLECTOR")
    print("="*70)
    print("\nThis script collects baseline data from running Chrome.")
    print("\nPrerequisites:")
    print("  ✅ Chrome is running")
    print("  ✅ You are on TikTok LIVE page")
    print("  ✅ Video is playing")
    print("  ✅ Chrome started with --remote-debugging-port=9222")
    print("\n" + "="*70 + "\n")
    
    input("Press Enter to continue...")
    
    asyncio.run(collect_from_running_chrome())


if __name__ == "__main__":
    main()
