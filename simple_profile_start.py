#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 SIMPLE PROFILE START - Giống "Starting" trong launcher.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Chỉ mở Chrome với profile đã login, KHÔNG tự động navigate
User tự thao tác trên browser

Features:
- ✅ Mở Chrome với profile
- ✅ Mở TikTok homepage (không auto-navigate đến livestream)
- ✅ Không block JS files
- ✅ User tự vào livestream
- ✅ Giữ browser mở để user thao tác

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.insert(0, os.getcwd())

from core.chrome_manager import ChromeProfileManager
from core.managers.profile_manager import ProfileManager


def simple_start_profile(profile_name: str, hidden: bool = False):
    """
    Mở Chrome với profile - Giống "Starting" trong launcher.py
    
    Args:
        profile_name: Tên profile (e.g. "001")
        hidden: True = minimize window, False = visible window
    """
    print("\n" + "="*70)
    print("🚀 SIMPLE PROFILE START")
    print("="*70)
    print(f"Profile: {profile_name}")
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
    
    print(f"[LAUNCH] Starting profile: {profile_name}")
    
    # Initialize ChromeProfileManager
    chrome_manager = ChromeProfileManager()
    
    # Launch Chrome profile - exactly like launcher.py "Starting" button
    try:
        success, result = chrome_manager.launch_chrome_profile(
            profile_name,
            hidden=hidden,           # Minimize window if True
            auto_login=False,        # No autofill (profile already logged in)
            login_data=None,         # No login data
            start_url="https://www.tiktok.com"  # Open TikTok homepage
        )
        
        if success:
            print(f"\n✅ Profile launched successfully!")
            print(f"\n📌 Browser is now open at TikTok homepage")
            print(f"📌 You can manually navigate to livestream")
            print(f"📌 Press Ctrl+C to close browser\n")
            
            # Keep script running
            try:
                input("Press Enter to close browser...")
            except KeyboardInterrupt:
                print("\n\n⚠️  Closing browser...")
            
            return True
        else:
            print(f"\n❌ Failed to launch profile")
            print(f"Error: {result}")
            return False
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main function"""
    print("\n" + "="*70)
    print("🚀 SIMPLE PROFILE START")
    print("="*70)
    print("\nGiống 'Starting' trong launcher.py:")
    print("  ✅ Mở Chrome với profile đã login")
    print("  ✅ KHÔNG tự động navigate")
    print("  ✅ KHÔNG block JS files")
    print("  ✅ User tự thao tác trên browser")
    print("="*70 + "\n")
    
    # Get profile name
    profile_name = input("Profile name (e.g. 001): ").strip()
    
    if not profile_name:
        print("❌ Profile name is required")
        return
    
    # Ask for hidden mode
    hidden_input = input("Hidden mode? (y/n, default: n): ").strip().lower()
    hidden = (hidden_input == 'y')
    
    # Start profile
    simple_start_profile(profile_name, hidden)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
