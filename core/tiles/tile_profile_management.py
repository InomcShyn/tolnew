import os
import json
import random
from core.utils.proxy_utils import parse_proxy_string

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
        print(f"[PROFILE] [CLONE] Creating profile '{profile_name}'")
        
        # Đường dẫn profile đích
        target_profile_path = os.path.join(manager.profiles_dir, profile_name)
        
        # Kiểm tra profile đã tồn tại chưa
        if os.path.exists(target_profile_path):
            print(f"[WARNING] [CLONE] Profile '{profile_name}' already exists, skipping")
            return False, f"Profile '{profile_name}' already exists"
        
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
        print(f"[PROFILE] [FRESH] Creating new profile '{profile_name}'")
        
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
        
        print(f"[SUCCESS] [FRESH] Profile '{profile_name}' created successfully")
        return True, f"Profile '{profile_name}' created successfully"
        
    except Exception as e:
        error_msg = f"Error creating fresh profile: {str(e)}"
        print(f"[ERROR] [FRESH] {error_msg}")
        return False, error_msg


def create_profile_with_extension(manager, profile_name, source_profile="Default", auto_install_extension=True):
    '''
    Create new profile with automatic extension installation
    
    Note: Playwright version không cần cài extension thủ công
    Extensions được tạo tự động khi cần (proxy auth, profile title)
    '''
    try:
        print(f"[PROFILE] [PROFILE-EXT] Creating profile '{profile_name}'...")
        # Create fresh profile from scratch (skip source_profile)
        success, message = clone_chrome_profile(manager, profile_name)
        if not success:
            return False, f"Failed to create profile: {message}"
        
        # Auto install extension if requested
        if auto_install_extension:
            print(f"ℹ️ [PROFILE-EXT] Playwright: Extensions created automatically when needed")
            # Call ensure_extension_installed for compatibility
            # (returns True in Playwright version)
            ext_success = manager.ensure_extension_installed(profile_name)
            if ext_success:
                return True, f"Profile created successfully (extensions auto-managed)"
            else:
                return True, f"Profile created (extension management not needed)"
        else:
            return True, f"Profile created successfully: {message}"
    except Exception as e:
        print(f"[ERROR] [PROFILE-EXT] Error creating profile: {str(e)}")
        return False, f"Error creating profile: {str(e)}"


# parse_proxy_string is now imported from core.utils.proxy_utils


def create_profiles_bulk(manager, base_name, quantity, version, use_random_format, proxy_list, use_random_hardware, use_random_ua=False, start_number=None, prefix_number=None):
    '''
    Create multiple profiles in bulk
    
    Args:
        start_number: Optional starting number for profile naming. If None, auto-detect from existing profiles.
        prefix_number: Optional prefix number for random format (P-{prefix}-{number}). If None, auto-detect or generate.
    '''
    try:
        print(f"[BULK-CREATE] Creating {quantity} profiles with Chrome version: {version}")
        print(f"[BULK-CREATE] Settings: Random format={use_random_format}, Random hardware={use_random_hardware}, Random UA={use_random_ua}")
        print(f"[BULK-CREATE] Using {len(proxy_list)} proxies")
        
        # Validate version
        if not version or not version.strip():
            print(f"[ERROR] [BULK-CREATE] Chrome version is required but not provided!")
            return False, "Chrome version is required"
        
        version = version.strip()
        
        # ✅ FIX: Tìm số cuối cùng và prefix của profiles đã tồn tại để tiếp tục đánh số
        existing_profiles = manager.get_all_profiles()
        max_number = 0
        existing_prefix = None
        
        if use_random_format:
            # Format: P-{prefix}-{number}
            import re
            for profile in existing_profiles:
                match = re.match(r'P-(\d+)-(\d+)', profile)
                if match:
                    prefix = match.group(1)
                    num = int(match.group(2))
                    if num > max_number:
                        max_number = num
                        existing_prefix = prefix  # Lưu prefix của profile có số lớn nhất
        else:
            # Format: {base_name}-{number} (với dấu gạch ngang)
            import re
            for profile in existing_profiles:
                if profile.startswith(base_name + '-'):
                    match = re.search(r'-(\d+)$', profile)
                    if match:
                        num = int(match.group(1))
                        max_number = max(max_number, num)
        
        # Xác định prefix_num để sử dụng
        if use_random_format:
            if prefix_number is not None:
                # Sử dụng prefix được cung cấp từ dialog
                prefix_num = str(prefix_number)
                print(f"[BULK-CREATE] Using provided prefix: P-{prefix_num}-xxxx")
            elif existing_prefix:
                # Sử dụng lại prefix hiện có
                prefix_num = existing_prefix
                print(f"[BULK-CREATE] Reusing existing prefix: P-{prefix_num}-xxxx")
            else:
                # Không dùng prefix ngẫu nhiên nữa
                prefix_num = None
                print(f"[BULK-CREATE] Creating profiles with base name: {base_name}")
        
        # Sử dụng start_number nếu được cung cấp, nếu không thì tự động tìm
        if start_number is not None:
            max_number = start_number - 1  # Trừ 1 vì sẽ cộng lại ở dưới
            print(f"[BULK-CREATE] Using custom start number: {start_number}")
        else:
            print(f"[BULK-CREATE] Auto-detected starting from number: {max_number + 1}")
        
        created_profiles = []
        for i in range(quantity):
            try:
                # Generate profile name - tiếp tục từ số cuối cùng
                current_number = max_number + i + 1
                
                # New naming convention: {base_name}-{number}
                # Example: X-001, X-002 for single creation
                # Example: MyName-001, MyName-002 for bulk creation
                suffix_num = f"{current_number:03d}"  # 3 digits: 001, 002, etc.
                profile_name = f"{base_name}-{suffix_num}"
                
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
                
                # Apply proxy FIRST if available
                if proxy_list and i < len(proxy_list):
                    proxy_string = proxy_list[i]
                    try:
                        # Use manager's _set_profile_proxy to set proxy properly
                        # This will save to BOTH profile_settings.json AND Chrome Preferences
                        manager._set_profile_proxy(profile_name, proxy_string)
                        print(f"[SUCCESS] [BULK-CREATE] Applied proxy to {profile_name}: {proxy_string}")
                        
                        # Reload settings_data after proxy was set
                        if os.path.exists(settings_path):
                            with open(settings_path, 'r', encoding='utf-8') as f:
                                settings_data = json.load(f)
                    except Exception as e:
                        print(f"[WARNING] [BULK-CREATE] Could not set proxy for {profile_name}: {e}")
                elif proxy_list:
                    print(f"[INFO] [BULK-CREATE] No proxy for {profile_name} (index {i} >= {len(proxy_list)} proxies)")
                
                # Set browser version in software section
                if 'software' not in settings_data:
                    settings_data['software'] = {}
                settings_data['software']['browser_version'] = version
                # Also set at top level for compatibility
                settings_data['browser_version'] = version
                
                # Apply random hardware if requested
                if use_random_hardware:
                    try:
                        if 'hardware' not in settings_data:
                            settings_data['hardware'] = {}
                        
                        # Random CPU cores (2-16)
                        settings_data['hardware']['cpu_cores'] = str(random.choice([2, 4, 6, 8, 12, 16]))
                        
                        # Random RAM (4-32 GB)
                        settings_data['hardware']['device_memory'] = str(random.choice([4, 8, 16, 32]))
                        
                        # Random MAC address
                        mac = ':'.join([f'{random.randint(0, 255):02X}' for _ in range(6)])
                        settings_data['hardware']['mac_address'] = mac
                        
                        print(f"[SUCCESS] [BULK-CREATE] Applied random hardware to {profile_name}")
                    except Exception as e:
                        print(f"[WARNING] [BULK-CREATE] Could not apply random hardware: {e}")
                
                # Apply random user agent if requested (Core Copy style - WORKING)
                if use_random_ua:
                    try:
                        if 'software' not in settings_data:
                            settings_data['software'] = {}
                        
                        # Random Chrome versions (Core Copy style - proven to work)
                        chrome_versions = ['120.0.0.0', '121.0.0.0', '122.0.0.0', '123.0.0.0']
                        chrome_ver = random.choice(chrome_versions)
                        
                        # Random Windows versions (Core Copy style)
                        windows_versions = [
                            'Windows NT 10.0; Win64; x64',
                            'Windows NT 10.0; WOW64',
                            'Windows NT 11.0; Win64; x64'
                        ]
                        windows_ver = random.choice(windows_versions)
                        
                        ua = f'Mozilla/5.0 ({windows_ver}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_ver} Safari/537.36'
                        settings_data['software']['user_agent'] = ua
                        
                        print(f"[SUCCESS] [BULK-CREATE] Applied random UA to {profile_name}: {ua[:60]}...")
                    except Exception as e:
                        print(f"[WARNING] [BULK-CREATE] Could not apply random UA: {e}")
                
                # Save settings (now includes proxy + version + hardware + UA)
                try:
                    with open(settings_path, 'w', encoding='utf-8') as f:
                        json.dump(settings_data, f, indent=2, ensure_ascii=False)
                    print(f"[SUCCESS] [BULK-CREATE] Saved all settings for {profile_name}")
                except Exception as e:
                    print(f"[WARNING] [BULK-CREATE] Could not save settings for {profile_name}: {e}")
                
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
