#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script để extract OMOcaptcha extension từ một profile và copy vào thư mục extensions
Sử dụng khi muốn lấy extension từ profile đã cài để dùng cho chạy hàng loạt
"""

import os
import shutil
import json
import sys

def find_omocaptcha_extension(profile_path):
    """
    Tìm OMOcaptcha extension trong profile
    
    Args:
        profile_path: Đường dẫn đến profile folder
        
    Returns:
        tuple: (extension_id, version_folder_path) hoặc (None, None) nếu không tìm thấy
    """
    known_ext_id = 'dfjghhjachoacpgpkmbpdlpppeagojhe'
    
    # Kiểm tra các vị trí có thể
    ext_dirs = [
        os.path.join(profile_path, "Default", "Extensions"),
        os.path.join(profile_path, "Extensions")
    ]
    
    for ext_dir in ext_dirs:
        if not os.path.exists(ext_dir):
            continue
            
        ext_id_path = os.path.join(ext_dir, known_ext_id)
        if os.path.exists(ext_id_path) and os.path.isdir(ext_id_path):
            # Tìm version folder
            version_folders = [d for d in os.listdir(ext_id_path) 
                             if os.path.isdir(os.path.join(ext_id_path, d))]
            
            for version_folder in version_folders:
                version_path = os.path.join(ext_id_path, version_folder)
                manifest_path = os.path.join(version_path, "manifest.json")
                
                if os.path.exists(manifest_path):
                    try:
                        with open(manifest_path, 'r', encoding='utf-8') as f:
                            manifest = json.load(f)
                        ext_name = manifest.get('name', '').lower()
                        if 'omo' in ext_name and 'captcha' in ext_name:
                            print(f"[SUCCESS] Found OMOcaptcha extension:")
                            print(f"  Extension ID: {known_ext_id}")
                            print(f"  Version: {version_folder}")
                            print(f"  Name: {manifest.get('name', 'N/A')}")
                            print(f"  Path: {version_path}")
                            return known_ext_id, version_path
                    except Exception as e:
                        print(f"[WARNING] Error reading manifest: {e}")
                        continue
    
    return None, None


def copy_extension_to_extensions_folder(version_path, target_name="OMOcaptcha"):
    """
    Copy extension vào thư mục extensions
    
    Args:
        version_path: Đường dẫn đến version folder của extension
        target_name: Tên thư mục đích trong extensions (mặc định: OMOcaptcha)
    """
    workspace_root = os.getcwd()
    target_dir = os.path.join(workspace_root, "extensions", target_name)
    
    # Tạo thư mục đích nếu chưa có
    if not os.path.exists(target_dir):
        os.makedirs(target_dir, exist_ok=True)
        print(f"[INFO] Created target directory: {target_dir}")
    else:
        # Xóa thư mục cũ nếu đã tồn tại
        print(f"[INFO] Target directory exists, removing old files...")
        shutil.rmtree(target_dir)
        os.makedirs(target_dir, exist_ok=True)
    
    # Copy tất cả files và folders
    print(f"[INFO] Copying extension from {version_path} to {target_dir}...")
    
    try:
        for item in os.listdir(version_path):
            source = os.path.join(version_path, item)
            destination = os.path.join(target_dir, item)
            
            if os.path.isdir(source):
                shutil.copytree(source, destination)
            else:
                shutil.copy2(source, destination)
        
        print(f"[SUCCESS] Extension copied successfully to: {target_dir}")
        
        # Verify manifest.json exists
        manifest_path = os.path.join(target_dir, "manifest.json")
        if os.path.exists(manifest_path):
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
            print(f"[INFO] Extension info:")
            print(f"  Name: {manifest.get('name', 'N/A')}")
            print(f"  Version: {manifest.get('version', 'N/A')}")
            print(f"  Description: {manifest.get('description', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Error copying extension: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python extract_omocaptcha_from_profile.py <profile_name_or_path>")
        print("Example: python extract_omocaptcha_from_profile.py P-419619-0001")
        print("Example: python extract_omocaptcha_from_profile.py chrome_profiles/P-419619-0001")
        sys.exit(1)
    
    profile_input = sys.argv[1]
    
    # Xác định đường dẫn profile
    if os.path.isabs(profile_input) or os.path.exists(profile_input):
        profile_path = profile_input
    else:
        # Giả sử là tên profile trong chrome_profiles
        workspace_root = os.getcwd()
        profile_path = os.path.join(workspace_root, "chrome_profiles", profile_input)
    
    if not os.path.exists(profile_path):
        print(f"[ERROR] Profile path not found: {profile_path}")
        sys.exit(1)
    
    print(f"[INFO] Searching for OMOcaptcha extension in: {profile_path}")
    
    # Tìm extension
    ext_id, version_path = find_omocaptcha_extension(profile_path)
    
    if not ext_id or not version_path:
        print(f"[ERROR] OMOcaptcha extension not found in profile: {profile_path}")
        sys.exit(1)
    
    # Copy extension
    target_name = sys.argv[2] if len(sys.argv) > 2 else "OMOcaptcha"
    success = copy_extension_to_extensions_folder(version_path, target_name)
    
    if success:
        print(f"\n[SUCCESS] OMOcaptcha extension da duoc extract thanh cong!")
        print(f"[INFO] Extension co the duoc su dung khi chay hang loat")
        print(f"[INFO] Duong dan: extensions/{target_name}/")
    else:
        print(f"\n[ERROR] Khong the extract extension")
        sys.exit(1)


if __name__ == "__main__":
    main()

