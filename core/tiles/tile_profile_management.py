import os
import json
import random

# Các hàm quản lý profile được tách ra từ chrome_manager.py

def create_profile_directory(manager):
    """Create profiles directory if not exists"""
    if not os.path.exists(manager.profiles_dir):
        os.makedirs(manager.profiles_dir)


def clone_chrome_profile(manager, profile_name, source_profile="Default", profile_type="work"):
    """
    Tạo profile mới (wrapper for compatibility).
    Thực chất là tạo profile mới hoàn toàn, không clone từ source.
    
    Args:
        profile_name (str): Tên profile mới cần tạo
        source_profile (str): Profile nguồn (ignored, kept for compatibility)
        profile_type (str): Loại profile (ignored, kept for compatibility)
    
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        print(f"[PROFILE] [CLONE] Đang tạo profile '{profile_name}'")
        
        # Đường dẫn profile đích
        target_profile_path = os.path.join(manager.profiles_dir, profile_name)
        
        # Kiểm tra profile đã tồn tại chưa
        if os.path.exists(target_profile_path):
            print(f"[WARNING] [CLONE] Profile '{profile_name}' đã tồn tại, bỏ qua")
            return False, f"Profile '{profile_name}' đã tồn tại"
        
        # Tạo profile mới hoàn toàn
        return create_fresh_profile(manager, profile_name, profile_type)
        
    except Exception as e:
        error_msg = f"Error creating profile: {str(e)}"
        print(f"[ERROR] [CLONE] {error_msg}")
        import traceback
        traceback.print_exc()
        return False, error_msg


def create_fresh_profile(manager, profile_name, profile_type="work"):
    """Tạo profile mới hoàn toàn (không clone)"""
    try:
        print(f"[PROFILE] [FRESH] Đang tạo profile mới '{profile_name}'")
        
        target_profile_path = os.path.join(manager.profiles_dir, profile_name)
        os.makedirs(target_profile_path, exist_ok=True)
        
        # Tạo Default folder
        default_path = os.path.join(target_profile_path, "Default")
        os.makedirs(default_path, exist_ok=True)
        
        # Tạo Preferences cơ bản
        prefs_path = os.path.join(default_path, "Preferences")
        import uuid
        import random as rnd
        
        basic_prefs = {
            "profile": {
                "name": profile_name,
                "avatar_icon": f"chrome://theme/IDR_PROFILE_AVATAR_{rnd.randint(0, 26)}"
            },
            "browser": {
                "show_home_button": False
            },
            "bookmark_bar": {
                "show_on_all_tabs": False
            },
            "extensions": {
                "settings": {},
                "alerts": {},
                "chrome_url_overrides": {},
                "commands": {},
                "last_chrome_version": "",
                "install_signature": {},
                "pending": {}
            },
            "google": {},
            "signin": {"allowed": False},
            "intl": {
                "accept_languages": "en-US,en;q=0.9"
            },
            "notifications": {
                "default_content_setting": 2
            }
        }
        
        with open(prefs_path, 'w', encoding='utf-8') as f:
            json.dump(basic_prefs, f, indent=2)
        
        # Tạo Extensions folder
        extensions_dir = os.path.join(default_path, "Extensions")
        os.makedirs(extensions_dir, exist_ok=True)
        
        print(f"[SUCCESS] [FRESH] Profile '{profile_name}' đã được tạo mới")
        return True, f"Profile '{profile_name}' created successfully"
        
    except Exception as e:
        error_msg = f"Error creating fresh profile: {str(e)}"
        print(f"[ERROR] [FRESH] {error_msg}")
        return False, error_msg


def create_profile_with_extension(manager, profile_name, source_profile="Default", auto_install_extension=True):
    '''
    Create new profile with automatic SwitchyOmega 3 extension installation
    '''
    try:
        print(f"[PROFILE] [PROFILE-EXT] Creating profile '{profile_name}' with extension installation...")
        # Create fresh profile from scratch (skip source_profile)
        success, message = clone_chrome_profile(manager, profile_name)
        if not success:
            return False, f"Failed to create profile: {message}"
        # Auto install extension if requested
        if auto_install_extension:
            print(f"[TOOL] [PROFILE-EXT] Auto-installing SwitchyOmega 3 for new profile '{profile_name}'...")
            ext_success, ext_message = manager.install_extension_for_profile(profile_name)
            if ext_success:
                return True, f"Profile created and extension installed: {ext_message}"
            else:
                return True, f"Profile created but extension installation failed: {ext_message}"
        else:
            return True, f"Profile created successfully: {message}"
    except Exception as e:
        print(f"[ERROR] [PROFILE-EXT] Error creating profile with extension: {str(e)}")
        return False, f"Error creating profile with extension: {str(e)}"


def parse_proxy_string(proxy_string):
    """
    Parse proxy string into components.
    
    Supported formats:
    - http://server:port:username:password
    - socks4://server:port:username:password
    - socks5://server:port:username:password
    - server:port:username:password (defaults to http)
    - http://server:port (no auth)
    - server:port (no auth, defaults to http)
    
    Returns: dict with keys: protocol, server, port, username, password
    """
    try:
        protocol = 'http'  # Default
        username = ''
        password = ''
        
        # Check if protocol is specified
        if '://' in proxy_string:
            parts = proxy_string.split('://', 1)
            protocol = parts[0].lower()  # http, socks4, socks5
            rest = parts[1]
        else:
            rest = proxy_string
        
        # Parse rest: server:port:username:password or server:port
        parts = rest.split(':')
        
        if len(parts) >= 4:
            # server:port:username:password
            server = parts[0]
            port = parts[1]
            username = parts[2]
            password = ':'.join(parts[3:])  # In case password contains ':'
        elif len(parts) >= 2:
            # server:port (no auth)
            server = parts[0]
            port = parts[1]
        else:
            raise ValueError(f"Invalid proxy format: {proxy_string}")
        
        return {
            'protocol': protocol,
            'server': server,
            'port': port,
            'username': username,
            'password': password
        }
    except Exception as e:
        raise ValueError(f"Failed to parse proxy '{proxy_string}': {e}")


def create_profiles_bulk(manager, base_name, quantity, version, use_random_format, proxy_list, use_random_hardware, use_random_ua=False):
    '''
    Create multiple profiles in bulk
    '''
    try:
        print(f"[BULK-CREATE] 🚀 Creating {quantity} profiles with Chrome version: {version}")
        print(f"[BULK-CREATE] 📋 Settings: Random format={use_random_format}, Random hardware={use_random_hardware}, Random UA={use_random_ua}")
        print(f"[BULK-CREATE] 🌐 Using {len(proxy_list)} proxies")
        
        # Validate version
        if not version or not version.strip():
            print(f"[ERROR] [BULK-CREATE] Chrome version is required but not provided!")
            return False, "Chrome version is required"
        
        version = version.strip()
        created_profiles = []
        for i in range(quantity):
            try:
                # Generate profile name
                if use_random_format:
                    prefix_num = random.randint(100000, 999999)
                    suffix_num = f"{i+1:04d}"
                    profile_name = f"P-{prefix_num}-{suffix_num}"
                else:
                    profile_name = f"{base_name}_{i+1:04d}"
                print(f"[BULK-CREATE] Creating profile {i+1}/{quantity}: {profile_name}")
                
                # Create profile using existing method
                success, message = clone_chrome_profile(manager, profile_name)
                if not success:
                    print(f"[ERROR] [BULK-CREATE] Failed to create {profile_name}: {message}")
                    continue
                
                # Set Chrome version in profile_settings.json
                profile_path = os.path.join(manager.profiles_dir, profile_name)
                settings_path = os.path.join(profile_path, 'profile_settings.json')
                
                # Load existing settings or create new
                settings_data = {}
                if os.path.exists(settings_path):
                    try:
                        with open(settings_path, 'r', encoding='utf-8') as f:
                            settings_data = json.load(f)
                    except Exception as e:
                        print(f"[WARNING] [BULK-CREATE] Could not read existing settings for {profile_name}: {e}")
                
                # Set browser version in software section
                if 'software' not in settings_data:
                    settings_data['software'] = {}
                settings_data['software']['browser_version'] = version
                # Also set at top level for compatibility
                settings_data['browser_version'] = version
                
                # Apply proxy if available
                if proxy_list and i < len(proxy_list):
                    proxy_string = proxy_list[i]
                    try:
                        # Parse proxy using dedicated function
                        proxy_config = parse_proxy_string(proxy_string)
                        
                        # Save proxy to settings
                        settings_data['proxy'] = {
                            'enabled': True,
                            'server': proxy_config['server'],
                            'port': proxy_config['port'],
                            'username': proxy_config['username'],
                            'password': proxy_config['password'],
                            'protocol': proxy_config['protocol']
                        }
                        print(f"[SUCCESS] [BULK-CREATE] Applied {proxy_config['protocol']} proxy {proxy_config['server']}:{proxy_config['port']} to {profile_name}")
                    except Exception as e:
                        print(f"[WARNING] [BULK-CREATE] Could not parse proxy for {profile_name}: {e}")
                elif proxy_list:
                    print(f"[INFO] [BULK-CREATE] No proxy for {profile_name} (index {i} >= {len(proxy_list)} proxies)")
                
                # Save settings
                try:
                    with open(settings_path, 'w', encoding='utf-8') as f:
                        json.dump(settings_data, f, indent=2, ensure_ascii=False)
                    print(f"[SUCCESS] [BULK-CREATE] Saved settings for {profile_name}")
                except Exception as e:
                    print(f"[WARNING] [BULK-CREATE] Could not save settings for {profile_name}: {e}")
                
                # Optionally: apply hardware, UA, extension (bổ sung thêm nếu muốn tách)
                created_profiles.append(profile_name)
            except Exception as e:
                print(f"[ERROR] [BULK-CREATE] Error: {str(e)}")
                import traceback
                traceback.print_exc()
                continue
        return True, created_profiles
    except Exception as e:
        print(f"[ERROR] [BULK-CREATE] Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False, str(e)


def is_profile_in_use(manager, profile_name_or_path):
    """
    Detect if a Chrome profile is currently running (has lock/marker files).
    Returns True if running, False otherwise.
    """
    try:
        if os.path.isabs(profile_name_or_path):
            profile_path = profile_name_or_path
        else:
            profile_path = manager.get_profile_path(profile_name_or_path)
        if not profile_path or not os.path.exists(profile_path):
            return False
        markers = ('DevToolsActivePort','SingletonLock','SingletonCookie','SingletonSocket','RunningChromeVersion')
        for base in (profile_path, os.path.join(profile_path, 'Default')):
            for fname in markers:
                fpath = os.path.join(base, fname)
                if os.path.exists(fpath):
                    return True
        return False
    except Exception:
        return False
