import os
import json

def set_profile_proxy(manager, profile_name, proxy_string):
    """Set proxy for a profile (từ chrome_manager.py)"""
    try:
        profile_path = os.path.join(manager.profiles_dir, profile_name)
        settings_path = os.path.join(profile_path, 'profile_settings.json')
        data = {}
        if os.path.exists(settings_path):
            with open(settings_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        # Set proxy
        data.setdefault('network', {})['proxy'] = proxy_string
        # Save settings
        with open(settings_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"[BULK-CREATE] Set proxy for {profile_name}: {proxy_string[:50]}...")
    except Exception as e:
        print(f"[WARNING] [BULK-CREATE] Could not set proxy for {profile_name}: {e}")
