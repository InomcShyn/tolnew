#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test proxy final"""

from core.chrome_manager import ChromeProfileManager

def main():
    print("Launching Chrome with proxy...")
    manager = ChromeProfileManager()
    success, result = manager.launch_chrome_profile(
        'P-419619-0001',
        start_url='https://httpbin.org/ip',
        hidden=False
    )
    
    if success:
        print("\n✅ Chrome launched successfully!")
        print("Check if popup appears or not")
    else:
        print(f"\n❌ Failed: {result}")

if __name__ == "__main__":
    main()
