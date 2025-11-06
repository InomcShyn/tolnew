import os

def get_profile_path(manager, profile_name):
    """
    Get profile path - Sử dụng profiles_dir của tool (chrome_profiles), 
    KHÔNG phải Chrome User Data mặc định để tránh xung đột với Chrome cá nhân.
    
    Args:
        manager: ChromeProfileManager instance
        profile_name: Tên profile
    
    Returns:
        str: Đường dẫn đầy đủ đến profile folder
    """
    try:
        # Sử dụng profiles_dir của tool (chrome_profiles), KHÔNG dùng Chrome User Data mặc định
        profile_path = os.path.join(manager.profiles_dir, profile_name)
        
        # Nếu profile đã tồn tại, trả về luôn
        if os.path.exists(profile_path):
            return profile_path
        
        # Nếu không tồn tại, kiểm tra xem có trong Default folder không (cấu trúc cũ)
        default_profile_path = os.path.join(manager.profiles_dir, "Default", profile_name)
        if os.path.exists(default_profile_path):
            return default_profile_path
        
        # Nếu không tìm thấy, trả về đường dẫn mong đợi (không tạo folder tự động)
        # Để các hàm khác tự quyết định có tạo hay không
        return profile_path
        
    except Exception as e:
        print(f"[ERROR] [PROFILE-PATH] Error getting profile path for {profile_name}: {str(e)}")
        # Fallback: trả về đường dẫn trong profiles_dir
        try:
            return os.path.join(manager.profiles_dir, profile_name)
        except:
            return None
