"""
Get All Profile Names from chrome_profiles
Lấy toàn bộ tên profiles trong thư mục chrome_profiles
"""

import os

def get_all_profile_names(profiles_dir='chrome_profiles'):
    """
    Lấy toàn bộ tên profiles trong thư mục chrome_profiles
    
    Args:
        profiles_dir (str): Đường dẫn đến thư mục profiles (mặc định: 'chrome_profiles')
    
    Returns:
        list: Danh sách tên profiles
    """
    profiles = []
    
    if not os.path.exists(profiles_dir):
        print(f"❌ Không tìm thấy thư mục: {profiles_dir}")
        return profiles
    
    try:
        for item in os.listdir(profiles_dir):
            item_path = os.path.join(profiles_dir, item)
            if os.path.isdir(item_path):
                profiles.append(item)
        
        # Sắp xếp theo tên
        profiles.sort()
        
    except Exception as e:
        print(f"❌ Lỗi khi đọc thư mục: {e}")
    
    return profiles

def get_profile_names_with_details(profiles_dir='chrome_profiles'):
    """
    Lấy tên profiles kèm thông tin chi tiết
    
    Returns:
        list: Danh sách dict chứa thông tin profile
    """
    profiles = []
    
    if not os.path.exists(profiles_dir):
        print(f"❌ Không tìm thấy thư mục: {profiles_dir}")
        return profiles
    
    try:
        for item in os.listdir(profiles_dir):
            item_path = os.path.join(profiles_dir, item)
            if os.path.isdir(item_path):
                # Lấy thông tin chi tiết
                profile_info = {
                    'name': item,
                    'path': item_path,
                    'has_settings': os.path.exists(os.path.join(item_path, 'profile_settings.json')),
                    'has_default': os.path.exists(os.path.join(item_path, 'Default')),
                }
                profiles.append(profile_info)
        
        # Sắp xếp theo tên
        profiles.sort(key=lambda x: x['name'])
        
    except Exception as e:
        print(f"❌ Lỗi khi đọc thư mục: {e}")
    
    return profiles

def print_all_profiles(profiles_dir='chrome_profiles'):
    """In ra toàn bộ profiles"""
    print("=" * 70)
    print("📂 DANH SÁCH PROFILES")
    print("=" * 70)
    
    profiles = get_all_profile_names(profiles_dir)
    
    if not profiles:
        print("❌ Không tìm thấy profile nào")
        return
    
    print(f"\n✅ Tìm thấy {len(profiles)} profiles:\n")
    
    for i, profile in enumerate(profiles, 1):
        print(f"  {i:3d}. {profile}")
    
    print("\n" + "=" * 70)

def print_profiles_with_details(profiles_dir='chrome_profiles'):
    """In ra profiles kèm thông tin chi tiết"""
    print("=" * 70)
    print("📂 DANH SÁCH PROFILES (CHI TIẾT)")
    print("=" * 70)
    
    profiles = get_profile_names_with_details(profiles_dir)
    
    if not profiles:
        print("❌ Không tìm thấy profile nào")
        return
    
    print(f"\n✅ Tìm thấy {len(profiles)} profiles:\n")
    
    for i, profile in enumerate(profiles, 1):
        status = []
        if profile['has_settings']:
            status.append("✅ Settings")
        else:
            status.append("❌ Settings")
        
        if profile['has_default']:
            status.append("✅ Default")
        else:
            status.append("❌ Default")
        
        status_str = " | ".join(status)
        print(f"  {i:3d}. {profile['name']:<20} [{status_str}]")
    
    print("\n" + "=" * 70)

def save_profiles_to_file(output_file='profiles_list.txt', profiles_dir='chrome_profiles'):
    """Lưu danh sách profiles vào file"""
    profiles = get_all_profile_names(profiles_dir)
    
    if not profiles:
        print("❌ Không tìm thấy profile nào")
        return False
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            for profile in profiles:
                f.write(f"{profile}\n")
        
        print(f"✅ Đã lưu {len(profiles)} profiles vào: {output_file}")
        return True
        
    except Exception as e:
        print(f"❌ Lỗi khi lưu file: {e}")
        return False

def filter_profiles_by_pattern(pattern, profiles_dir='chrome_profiles'):
    """
    Lọc profiles theo pattern
    
    Args:
        pattern (str): Pattern để lọc (ví dụ: 'X-', '001', 'test')
        profiles_dir (str): Thư mục profiles
    
    Returns:
        list: Danh sách profiles khớp với pattern
    """
    all_profiles = get_all_profile_names(profiles_dir)
    filtered = [p for p in all_profiles if pattern.lower() in p.lower()]
    return filtered

def count_profiles(profiles_dir='chrome_profiles'):
    """Đếm số lượng profiles"""
    profiles = get_all_profile_names(profiles_dir)
    return len(profiles)

# ============================================================
# MAIN - Interactive Menu
# ============================================================

if __name__ == '__main__':
    print("\n")
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║  📂 GET ALL PROFILE NAMES                                       ║")
    print("╚══════════════════════════════════════════════════════════════════╝")
    print()
    print("Chức năng:")
    print("  1. Hiển thị danh sách profiles (đơn giản)")
    print("  2. Hiển thị danh sách profiles (chi tiết)")
    print("  3. Lưu danh sách vào file")
    print("  4. Tìm kiếm profiles theo pattern")
    print("  5. Đếm số lượng profiles")
    print("  6. Thoát")
    print()
    
    while True:
        choice = input("Chọn chức năng (1-6): ").strip()
        
        if choice == '1':
            print()
            print_all_profiles()
            print()
            
        elif choice == '2':
            print()
            print_profiles_with_details()
            print()
            
        elif choice == '3':
            print()
            output_file = input("Tên file output (Enter = profiles_list.txt): ").strip()
            if not output_file:
                output_file = 'profiles_list.txt'
            save_profiles_to_file(output_file)
            print()
            
        elif choice == '4':
            print()
            pattern = input("Nhập pattern tìm kiếm (ví dụ: X-, 001): ").strip()
            if pattern:
                profiles = filter_profiles_by_pattern(pattern)
                print(f"\n✅ Tìm thấy {len(profiles)} profiles khớp với '{pattern}':\n")
                for i, profile in enumerate(profiles, 1):
                    print(f"  {i:3d}. {profile}")
            else:
                print("❌ Pattern không hợp lệ")
            print()
            
        elif choice == '5':
            print()
            count = count_profiles()
            print(f"📊 Tổng số profiles: {count}")
            print()
            
        elif choice == '6':
            print("\n👋 Tạm biệt!\n")
            break
            
        else:
            print("❌ Lựa chọn không hợp lệ\n")
