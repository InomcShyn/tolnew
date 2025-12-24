import os
import shutil
import json

def clear_profile_name_cache(manager, profile_path):
    cache_file = os.path.join(profile_path, 'Local State')
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                local_state = json.load(f)
            local_state['profile']['info_cache'] = {}
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(local_state, f, ensure_ascii=False, indent=2)
        except Exception:
            pass


def clear_existing_proxy_data(manager, driver):
    """Dummy method as placeholder, will depend on how proxy is used in session."""
    pass


def clear_proxy_credentials_cache(manager, profile_path):
    """
    Xóa cache proxy credentials trong Chrome profile.
    Fix lỗi: Khi thay đổi proxy có username/password khác, Chrome vẫn cache credentials cũ.
    
    Args:
        manager: ChromeProfileManager instance
        profile_path: Đường dẫn đến profile
    """
    try:
        # Xóa Login Data (chứa saved passwords và credentials)
        login_data_path = os.path.join(profile_path, 'Default', 'Login Data')
        if os.path.exists(login_data_path):
            try:
                os.remove(login_data_path)
                print(f"[PROXY] [CACHE] Removed Login Data (proxy credentials cache)")
            except Exception as e:
                print(f"[WARNING] [PROXY] Could not remove Login Data: {e}")
        
        # Xóa Login Data journal
        login_data_journal = os.path.join(profile_path, 'Default', 'Login Data-journal')
        if os.path.exists(login_data_journal):
            try:
                os.remove(login_data_journal)
            except Exception:
                pass
        
        # Xóa Network folder (chứa cache network credentials)
        network_path = os.path.join(profile_path, 'Default', 'Network')
        if os.path.exists(network_path):
            try:
                shutil.rmtree(network_path)
                print(f"[PROXY] [CACHE] Removed Network cache")
            except Exception as e:
                print(f"[WARNING] [PROXY] Could not remove Network cache: {e}")
        
        # Xóa Preferences proxy settings (để force reload)
        prefs_path = os.path.join(profile_path, 'Default', 'Preferences')
        if os.path.exists(prefs_path):
            try:
                with open(prefs_path, 'r', encoding='utf-8') as f:
                    prefs = json.load(f)
                
                # Xóa proxy settings cũ
                if 'proxy' in prefs:
                    del prefs['proxy']
                    print(f"[PROXY] [CACHE] Cleared proxy settings from Preferences")
                
                with open(prefs_path, 'w', encoding='utf-8') as f:
                    json.dump(prefs, f, ensure_ascii=False, indent=2)
            except Exception as e:
                print(f"[WARNING] [PROXY] Could not clear proxy from Preferences: {e}")
        
        print(f"[PROXY] [CACHE] ✅ Cleared proxy credentials cache")
        return True
        
    except Exception as e:
        print(f"[WARNING] [PROXY] Failed to clear proxy credentials cache: {e}")
        return False
