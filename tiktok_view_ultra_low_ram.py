#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TikTok View Bot - Ultra Low RAM Mode
Target: 150-200MB RAM per profile
Stealth mode: Không bị detect bot
"""

import asyncio
import random
from core.chrome_manager import ChromeProfileManager
from core.ultra_low_ram_stealth import (
    get_tiktok_view_flags,
    inject_stealth,
    simulate_human_view,
    get_memory_usage,
    cleanup_memory
)


def view_tiktok_video_ultra_low_ram_sync(
    manager: ChromeProfileManager,
    profile_name: str,
    video_url: str,
    watch_duration: int = 5,
    ultra_low_ram: bool = True
):
    """
    View TikTok video với ultra low RAM mode (SYNC version)
    
    Args:
        manager: ChromeProfileManager instance
        profile_name: Profile name
        video_url: TikTok video URL
        watch_duration: Watch duration in seconds
        ultra_low_ram: True = 150-200MB, False = 250-300MB
    
    Returns:
        bool: Success or not
    """
    try:
        print(f"\n{'='*70}")
        print(f"[ULTRA-LOW-RAM] Starting view for {profile_name}")
        print(f"[ULTRA-LOW-RAM] Mode: {'ULTRA' if ultra_low_ram else 'BALANCED'}")
        print(f"[ULTRA-LOW-RAM] Target RAM: {'150-200MB' if ultra_low_ram else '250-300MB'}")
        print(f"{'='*70}\n")
        
        # Get flags
        mode = "optimized" if ultra_low_ram else "best"
        flags = get_tiktok_view_flags(mode=mode)
        
        # Launch profile với custom flags
        print(f"[1/5] Launching profile with ultra low RAM flags...")
        success, page = manager.launch_chrome_profile(
            profile_name,
            hidden=False,  # Visible để verify
            start_url="about:blank",  # Start blank để save RAM
            custom_flags=flags  # Custom flags
        )
        
        if not success or not page:
            print(f"❌ Failed to launch profile")
            return False
        
        print(f"✅ Profile launched")
        
        # Get event loop
        loop = manager._loop
        
        # Inject stealth
        print(f"\n[2/5] Injecting stealth scripts...")
        loop.run_until_complete(inject_stealth(page))
        
        # Check initial memory
        print(f"\n[3/5] Checking initial memory...")
        initial_memory = loop.run_until_complete(get_memory_usage(page))
        
        # Simulate human view
        print(f"\n[4/5] Simulating human view...")
        view_success = loop.run_until_complete(simulate_human_view(page, video_url, watch_duration))
        
        if not view_success:
            print(f"⚠️ View failed")
            return False
        
        # Check final memory
        print(f"\n[5/5] Checking final memory...")
        final_memory = loop.run_until_complete(get_memory_usage(page))
        
        # Cleanup
        loop.run_until_complete(cleanup_memory(page))
        
        # Summary
        print(f"\n{'='*70}")
        print(f"[SUMMARY] View completed successfully")
        if initial_memory and final_memory:
            print(f"[SUMMARY] Memory: {initial_memory}MB → {final_memory}MB")
        print(f"{'='*70}\n")
        
        # Keep browser open for verification
        print(f"⏸️  Browser will stay open for 10 seconds for verification...")
        import time
        time.sleep(10)
        
        # Close
        manager.close_profile(profile_name)
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_single_view():
    """Test single view"""
    print("="*70)
    print("TIKTOK VIEW - ULTRA LOW RAM TEST")
    print("="*70)
    
    # Config
    profile_name = input("\nEnter profile name (e.g., p-966508-8219): ").strip()
    video_url = input("Enter TikTok video URL: ").strip()
    
    if not profile_name or not video_url:
        print("❌ Missing profile name or video URL")
        return
    
    # Mode selection
    print("\nSelect mode:")
    print("1. ULTRA LOW RAM (150-200MB) - Most aggressive")
    print("2. BALANCED (250-300MB) - Recommended")
    mode = input("Enter choice (1 or 2): ").strip()
    
    ultra_low_ram = (mode == "1")
    
    # Watch duration
    watch_duration = int(input("\nWatch duration (seconds, default 5): ").strip() or "5")
    
    # Initialize manager
    manager = ChromeProfileManager()
    
    # Run (sync version - no event loop needed)
    success = view_tiktok_video_ultra_low_ram_sync(
        manager,
        profile_name,
        video_url,
        watch_duration,
        ultra_low_ram
    )
    
    if success:
        print("\n✅ Test completed successfully!")
    else:
        print("\n❌ Test failed!")


def test_multiple_views():
    """Test multiple profiles viewing"""
    print("="*70)
    print("TIKTOK VIEW - MULTIPLE PROFILES TEST")
    print("="*70)
    
    # Get profiles
    manager = ChromeProfileManager()
    success, sessions = manager.get_all_tiktok_sessions()
    
    if not success or not sessions:
        print("❌ No TikTok sessions found!")
        return
    
    # Show profile info
    print(f"\n📋 Total profiles available: {len(sessions)}")
    
    # Let user choose how many
    num_profiles = input("\nHow many profiles to test? (default 5): ").strip()
    try:
        num_profiles = int(num_profiles) if num_profiles else 5
    except:
        num_profiles = 5
    
    profiles = list(sessions.keys())[:num_profiles]
    print(f"✅ Will test {len(profiles)} profiles:")
    for i, p in enumerate(profiles, 1):
        print(f"   {i}. {p}")
    
    # Video URL
    video_url = input("\nEnter TikTok video URL: ").strip()
    if not video_url:
        print("❌ Missing video URL")
        return
    
    # Mode
    print("\nSelect mode:")
    print("1. ULTRA LOW RAM (150-200MB)")
    print("2. BALANCED (250-300MB)")
    mode = input("Enter choice (1 or 2): ").strip()
    ultra_low_ram = (mode == "1")
    
    # Run (sync version - no event loop needed)
    success_count = 0
    for idx, profile_name in enumerate(profiles, 1):
        print(f"\n{'='*70}")
        print(f"[{idx}/{len(profiles)}] Processing {profile_name}")
        print(f"{'='*70}")
        
        success = view_tiktok_video_ultra_low_ram_sync(
            manager,
            profile_name,
            video_url,
            watch_duration=random.randint(3, 8),
            ultra_low_ram=ultra_low_ram
        )
        
        if success:
            success_count += 1
        
        # Delay between profiles
        if idx < len(profiles):
            delay = random.uniform(2, 5)
            print(f"\n⏳ Waiting {delay:.1f}s before next profile...")
            import time
            time.sleep(delay)
    
    # Summary
    print(f"\n{'='*70}")
    print(f"[FINAL SUMMARY]")
    print(f"Total: {len(profiles)}")
    print(f"Success: {success_count}")
    print(f"Failed: {len(profiles) - success_count}")
    print(f"{'='*70}")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("TIKTOK VIEW BOT - ULTRA LOW RAM MODE")
    print("Target: 150-200MB RAM per profile")
    print("Stealth: Anti-detection enabled")
    print("="*70)
    
    print("\nSelect test:")
    print("1. Single view test")
    print("2. Multiple profiles test")
    
    choice = input("\nEnter choice (1 or 2): ").strip()
    
    if choice == "1":
        test_single_view()
    elif choice == "2":
        test_multiple_views()
    else:
        print("❌ Invalid choice")
