"""
Profile Utilities
Các hàm tiện ích để làm việc với Chrome profiles
"""

import os
import json

def get_all_profile_names(profiles_dir='chrome_profiles'):
    """
    Lấy toàn bộ tên profiles
    
    Args:
        profiles_dir (str): Đường dẫn thư mục profiles
    
    Returns:
        list: Danh sách tên profiles (sorted)
    """
    profiles = []
    
    if not os.path.exists(profiles_dir):
        return profiles
    
    try:
        for item in os.listdir(profiles_dir):
            item_path = os.path.join(profiles_dir, item)
            if os.path.isdir(item_path):
                profiles.append(item)
        
        profiles.sort()
        
    except Exception as e:
        print(f"[PROFILE-UTILS] Error reading profiles: {e}")
    
    return profiles

def get_profile_info(profile_name, profiles_dir='chrome_profiles'):
    """
    Lấy thông tin chi tiết của một profile
    
    Args:
        profile_name (str): Tên profile
        profiles_dir (str): Thư mục profiles
    
    Returns:
        dict: Thông tin profile hoặc None nếu không tìm thấy
    """
    profile_path = os.path.join(profiles_dir, profile_name)
    
    if not os.path.exists(profile_path):
        return None
    
    info = {
        'name': profile_name,
        'path': profile_path,
        'exists': True,
        'has_settings': False,
        'has_default': False,
        'settings': None,
    }
    
    # Check settings file
    settings_file = os.path.join(profile_path, 'profile_settings.json')
    if os.path.exists(settings_file):
        info['has_settings'] = True
        try:
            with open(settings_file, 'r', encoding='utf-8') as f:
                info['settings'] = json.load(f)
        except:
            pass
    
    # Check Default folder
    default_folder = os.path.join(profile_path, 'Default')
    if os.path.exists(default_folder):
        info['has_default'] = True
    
    return info

def profile_exists(profile_name, profiles_dir='chrome_profiles'):
    """
    Kiểm tra profile có tồn tại không
    
    Args:
        profile_name (str): Tên profile
        profiles_dir (str): Thư mục profiles
    
    Returns:
        bool: True nếu tồn tại
    """
    profile_path = os.path.join(profiles_dir, profile_name)
    return os.path.exists(profile_path) and os.path.isdir(profile_path)

def filter_profiles(pattern, profiles_dir='chrome_profiles'):
    """
    Lọc profiles theo pattern
    
    Args:
        pattern (str): Pattern để lọc
        profiles_dir (str): Thư mục profiles
    
    Returns:
        list: Danh sách profiles khớp
    """
    all_profiles = get_all_profile_names(profiles_dir)
    return [p for p in all_profiles if pattern.lower() in p.lower()]

def count_profiles(profiles_dir='chrome_profiles'):
    """
    Đếm số lượng profiles
    
    Args:
        profiles_dir (str): Thư mục profiles
    
    Returns:
        int: Số lượng profiles
    """
    return len(get_all_profile_names(profiles_dir))

def get_profiles_with_settings(profiles_dir='chrome_profiles'):
    """
    Lấy danh sách profiles có file settings
    
    Args:
        profiles_dir (str): Thư mục profiles
    
    Returns:
        list: Danh sách tên profiles có settings
    """
    all_profiles = get_all_profile_names(profiles_dir)
    profiles_with_settings = []
    
    for profile in all_profiles:
        settings_file = os.path.join(profiles_dir, profile, 'profile_settings.json')
        if os.path.exists(settings_file):
            profiles_with_settings.append(profile)
    
    return profiles_with_settings

def get_profiles_without_settings(profiles_dir='chrome_profiles'):
    """
    Lấy danh sách profiles không có file settings
    
    Args:
        profiles_dir (str): Thư mục profiles
    
    Returns:
        list: Danh sách tên profiles không có settings
    """
    all_profiles = get_all_profile_names(profiles_dir)
    profiles_without_settings = []
    
    for profile in all_profiles:
        settings_file = os.path.join(profiles_dir, profile, 'profile_settings.json')
        if not os.path.exists(settings_file):
            profiles_without_settings.append(profile)
    
    return profiles_without_settings

def get_profile_chrome_version(profile_name, profiles_dir='chrome_profiles'):
    """
    Lấy Chrome version của profile
    
    Args:
        profile_name (str): Tên profile
        profiles_dir (str): Thư mục profiles
    
    Returns:
        str: Chrome version hoặc None
    """
    settings_file = os.path.join(profiles_dir, profile_name, 'profile_settings.json')
    
    if not os.path.exists(settings_file):
        return None
    
    try:
        with open(settings_file, 'r', encoding='utf-8') as f:
            settings = json.load(f)
        return settings.get('chrome_version')
    except:
        return None

def get_profiles_by_version(version_pattern, profiles_dir='chrome_profiles'):
    """
    Lấy danh sách profiles theo Chrome version
    
    Args:
        version_pattern (str): Pattern version (ví dụ: '119', '139')
        profiles_dir (str): Thư mục profiles
    
    Returns:
        list: Danh sách profiles khớp version
    """
    all_profiles = get_all_profile_names(profiles_dir)
    matching_profiles = []
    
    for profile in all_profiles:
        version = get_profile_chrome_version(profile, profiles_dir)
        if version and version_pattern in version:
            matching_profiles.append(profile)
    
    return matching_profiles

def get_profile_statistics(profiles_dir='chrome_profiles'):
    """
    Lấy thống kê về profiles
    
    Args:
        profiles_dir (str): Thư mục profiles
    
    Returns:
        dict: Thống kê profiles
    """
    all_profiles = get_all_profile_names(profiles_dir)
    
    stats = {
        'total': len(all_profiles),
        'with_settings': 0,
        'without_settings': 0,
        'with_default': 0,
        'without_default': 0,
        'versions': {},
    }
    
    for profile in all_profiles:
        profile_path = os.path.join(profiles_dir, profile)
        
        # Check settings
        settings_file = os.path.join(profile_path, 'profile_settings.json')
        if os.path.exists(settings_file):
            stats['with_settings'] += 1
            
            # Get version
            try:
                with open(settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                version = settings.get('chrome_version', 'unknown')
                
                # Count by major version
                major_version = version.split('.')[0] if version != 'unknown' else 'unknown'
                stats['versions'][major_version] = stats['versions'].get(major_version, 0) + 1
            except:
                pass
        else:
            stats['without_settings'] += 1
        
        # Check Default folder
        default_folder = os.path.join(profile_path, 'Default')
        if os.path.exists(default_folder):
            stats['with_default'] += 1
        else:
            stats['without_default'] += 1
    
    return stats

# ============================================================
# Example Usage
# ============================================================

if __name__ == '__main__':
    print("\n" + "=" * 70)
    print("📂 PROFILE UTILITIES - DEMO")
    print("=" * 70)
    
    # 1. Get all profiles
    print("\n1️⃣ Get all profile names:")
    profiles = get_all_profile_names()
    print(f"   Found {len(profiles)} profiles")
    if profiles:
        print(f"   First 5: {profiles[:5]}")
    
    # 2. Count profiles
    print("\n2️⃣ Count profiles:")
    count = count_profiles()
    print(f"   Total: {count}")
    
    # 3. Filter profiles
    print("\n3️⃣ Filter profiles (pattern: 'X-'):")
    filtered = filter_profiles('X-')
    print(f"   Found {len(filtered)} profiles")
    if filtered:
        print(f"   First 5: {filtered[:5]}")
    
    # 4. Get profiles with settings
    print("\n4️⃣ Profiles with settings:")
    with_settings = get_profiles_with_settings()
    print(f"   Found {len(with_settings)} profiles")
    
    # 5. Get profiles by version
    print("\n5️⃣ Profiles with Chrome 119:")
    version_119 = get_profiles_by_version('119')
    print(f"   Found {len(version_119)} profiles")
    
    # 6. Get statistics
    print("\n6️⃣ Profile statistics:")
    stats = get_profile_statistics()
    print(f"   Total: {stats['total']}")
    print(f"   With settings: {stats['with_settings']}")
    print(f"   Without settings: {stats['without_settings']}")
    print(f"   Versions: {stats['versions']}")
    
    print("\n" + "=" * 70 + "\n")
