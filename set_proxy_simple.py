#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script đơn giản để set proxy cho từng profile cụ thể
SET PROXY TRUC TIEP VAO CHROME PROFILE (khong qua extension)

Cach dung: python set_proxy_simple.py <profile_name> <proxy_string>
"""

import os
import json
import sys

# Fix encoding for Windows console
if sys.platform == 'win32':
    try:
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
    except Exception:
        pass

# Import ChromeProfileManager
try:
    from core.chrome_manager import ChromeProfileManager
except ImportError:
    print("[ERROR] Khong the import ChromeProfileManager. Dam bao ban dang chay tu thu muc goc cua project.")
    sys.exit(1)

def set_proxy_for_profile(profile_name, proxy_string):
    """
    Set proxy cho một profile cụ thể - TRỰC TIẾP VÀO CHROME PROFILE
    
    Args:
        profile_name: Tên profile (ví dụ: P-419619-0001)
        proxy_string: Proxy string (ví dụ: http://ip:port:user:pass hoặc null)
    """
    try:
        # Khởi tạo ChromeProfileManager
        manager = ChromeProfileManager()
        
        # Kiểm tra profile có tồn tại không
        profile_path = os.path.join(manager.profiles_dir, profile_name)
        if not os.path.exists(profile_path):
            print(f"[ERROR] Khong tim thay profile: {profile_name}")
            return False
        
        # Set proxy (se tu dong luu vao profile_settings.json VA Chrome Preferences)
        if proxy_string.lower() == 'null':
            manager._set_profile_proxy(profile_name, None)
            print(f"[SUCCESS] Da xoa proxy cho profile: {profile_name}")
        else:
            manager._set_profile_proxy(profile_name, proxy_string)
            print(f"[SUCCESS] Da set proxy cho profile: {profile_name}")
            print(f"   Proxy: {proxy_string}")
            print(f"   [INFO] Da luu vao profile_settings.json")
            print(f"   [INFO] Da luu vao Chrome Preferences")
            print(f"   [INFO] Proxy se tu dong ap dung khi launch Chrome")
        
        return True
    
    except Exception as e:
        print(f"[ERROR] Loi: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main function"""
    if len(sys.argv) < 3:
        print("="*80)
        print("SET PROXY CHO PROFILE")
        print("="*80)
        print("\nCach dung:")
        print("  python set_proxy_simple.py <profile_name> <proxy_string>")
        print("\nVi du:")
        print("  python set_proxy_simple.py P-419619-0001 http://123.45.67.89:8080:user:pass")
        print("  python set_proxy_simple.py P-419619-0001 socks5://123.45.67.89:1080:user:pass")
        print("  python set_proxy_simple.py P-419619-0001 null")
        print("\nFormat proxy:")
        print("  http://ip:port:user:pass")
        print("  socks5://ip:port:user:pass")
        print("  http://ip:port  (khong co username/password)")
        print("  null (de xoa proxy)")
        print("\nProxy se duoc set TRUC TIEP vao Chrome profile:")
        print("  - Luu vao profile_settings.json")
        print("  - Luu vao Chrome Preferences (Default/Preferences)")
        print("  - Tu dong ap dung khi launch Chrome (khong can extension)")
        print("\nDanh sach profiles:")
        
        # Hiển thị danh sách profiles
        profiles_dir = "chrome_profiles"
        if os.path.exists(profiles_dir):
            profiles = [d for d in os.listdir(profiles_dir) 
                       if os.path.isdir(os.path.join(profiles_dir, d))]
            for profile in sorted(profiles):
                print(f"  - {profile}")
        return
    
    profile_name = sys.argv[1]
    proxy_string = sys.argv[2]
    
    set_proxy_for_profile(profile_name, proxy_string)


if __name__ == "__main__":
    main()

