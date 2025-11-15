#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test bulk create profiles with proxy"""

import sys
import os

# Set UTF-8 encoding for console output
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'ignore')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'ignore')

from core.chrome_manager import ChromeProfileManager

def main():
    print("Testing bulk create profiles with proxy...")
    manager = ChromeProfileManager()
    
    # Test data
    base_name = "TestBulk"
    quantity = 3
    version = "139.0.7258.139"
    use_random_format = True
    use_random_hardware = False
    use_random_ua = False
    
    # Proxy list - 3 proxies for 3 profiles
    proxy_list = [
        "27.79.170.112:10009:sA5hg:password1",
        "27.79.170.113:10010:user2:password2",
        "27.79.170.114:10011:user3:password3"
    ]
    
    print(f"\nCreating {quantity} profiles with proxies...")
    print(f"Proxy list: {len(proxy_list)} proxies")
    
    success, result = manager.create_profiles_bulk(
        base_name, 
        quantity, 
        version, 
        use_random_format, 
        proxy_list, 
        use_random_hardware, 
        use_random_ua
    )
    
    if success:
        print(f"\n✅ Success! Created {len(result)} profiles:")
        for profile_name in result:
            print(f"  - {profile_name}")
            
            # Check proxy config
            profile_path = os.path.join(os.getcwd(), "chrome_profiles", profile_name)
            settings_file = os.path.join(profile_path, "profile_settings.json")
            
            if os.path.exists(settings_file):
                import json
                with open(settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    
                if 'proxy' in settings:
                    proxy = settings['proxy']
                    print(f"    Proxy: {proxy['server']}:{proxy['port']} (user: {proxy['username']})")
                else:
                    print(f"    Proxy: None")
            else:
                print(f"    Settings file not found")
    else:
        print(f"\n❌ Failed: {result}")

if __name__ == "__main__":
    main()
