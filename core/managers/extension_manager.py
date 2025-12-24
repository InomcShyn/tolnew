#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extension Manager - Quản lý Chrome extensions cho Playwright
Hỗ trợ cài đặt và quản lý extensions trong persistent context
"""

import os
import json
import shutil
from pathlib import Path
from typing import Optional, List, Dict, Tuple


class ExtensionManager:
    """
    Quản lý Chrome extensions
    
    LƯU Ý: Extensions chỉ hoạt động với Playwright khi:
    1. Sử dụng persistent context (launch_persistent_context)
    2. Chế độ headed (headless=False)
    3. Load qua --load-extension flag
    """
    
    def __init__(self, extensions_dir: Optional[Path] = None):
        """
        Initialize Extension Manager
        
        Args:
            extensions_dir: Thư mục chứa extensions (mặc định: ./extensions)
        """
        if extensions_dir is None:
            self.extensions_dir = Path(os.getcwd()) / "extensions"
        else:
            self.extensions_dir = Path(extensions_dir)
        
        self.extensions_dir.mkdir(exist_ok=True)
    
    def create_proxy_auth_extension(
        self,
        profile_name: str,
        username: str,
        password: str
    ) -> Tuple[bool, str]:
        """
        Tạo proxy authentication extension cho profile
        
        Args:
            profile_name: Tên profile
            username: Proxy username
            password: Proxy password
        
        Returns:
            (success, extension_path_or_error)
        """
        try:
            # Tạo folder cho extension (unique per profile)
            ext_folder_name = f"ProxyAuth_{profile_name}"
            ext_dir = self.extensions_dir / ext_folder_name
            
            # Xóa extension cũ nếu có
            if ext_dir.exists():
                try:
                    shutil.rmtree(ext_dir)
                except Exception as e:
                    print(f"[WARNING] Could not remove old extension: {e}")
            
            # Tạo folder mới
            ext_dir.mkdir(parents=True, exist_ok=True)
            
            # Tạo manifest.json (Manifest V3)
            manifest = {
                "manifest_version": 3,
                "name": f"Proxy Auth - {profile_name}",
                "version": "1.0.0",
                "description": "Auto-fill proxy authentication credentials",
                "permissions": [
                    "webRequest",
                    "webRequestAuthProvider"
                ],
                "host_permissions": [
                    "<all_urls>"
                ],
                "background": {
                    "service_worker": "background.js"
                }
            }
            
            manifest_path = ext_dir / "manifest.json"
            with open(manifest_path, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, indent=2, ensure_ascii=False)
            
            # Tạo background.js với credentials
            background_js = f"""
// Proxy authentication credentials
const PROXY_USERNAME = "{username}";
const PROXY_PASSWORD = "{password}";

// Listen for authentication requests
chrome.webRequest.onAuthRequired.addListener(
    function(details, callbackFn) {{
        console.log('[PROXY-AUTH] Authentication required for:', details.url);
        
        // Return credentials
        callbackFn({{
            authCredentials: {{
                username: PROXY_USERNAME,
                password: PROXY_PASSWORD
            }}
        }});
    }},
    {{ urls: ["<all_urls>"] }},
    ['asyncBlocking']
);

console.log('[PROXY-AUTH] Extension loaded successfully');
console.log('[PROXY-AUTH] Username:', PROXY_USERNAME);
console.log('[PROXY-AUTH] Profile: {profile_name}');
"""
            
            background_path = ext_dir / "background.js"
            with open(background_path, 'w', encoding='utf-8') as f:
                f.write(background_js)
            
            print(f"[EXTENSION] ✅ Created proxy auth extension: {ext_folder_name}")
            print(f"[EXTENSION]    Profile: {profile_name}")
            print(f"[EXTENSION]    Username: {username}")
            print(f"[EXTENSION]    Password: {'*' * len(password)}")
            
            return True, str(ext_dir)
            
        except Exception as e:
            error_msg = f"Failed to create proxy auth extension: {e}"
            print(f"[ERROR] {error_msg}")
            import traceback
            traceback.print_exc()
            return False, error_msg
    
    def create_profile_title_extension(
        self,
        profile_name: str
    ) -> Tuple[bool, str]:
        """
        Tạo extension hiển thị tên profile trong browser
        
        Args:
            profile_name: Tên profile
        
        Returns:
            (success, extension_path_or_error)
        """
        try:
            # Tạo folder cho extension
            ext_folder_name = f"ProfileTitle_{profile_name}"
            ext_dir = self.extensions_dir / ext_folder_name
            
            # Nếu đã tồn tại, return luôn
            if ext_dir.exists():
                manifest_path = ext_dir / "manifest.json"
                if manifest_path.exists():
                    return True, str(ext_dir)
            
            # Tạo folder mới
            ext_dir.mkdir(parents=True, exist_ok=True)
            
            # Tạo manifest.json
            manifest = {
                "manifest_version": 3,
                "name": f"Profile: {profile_name}",
                "version": "1.0.0",
                "description": f"Shows profile name: {profile_name}",
                "permissions": [],
                "background": {
                    "service_worker": "background.js"
                }
            }
            
            manifest_path = ext_dir / "manifest.json"
            with open(manifest_path, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, indent=2, ensure_ascii=False)
            
            # Tạo background.js đơn giản
            background_js = f"""
// Profile title extension
console.log('[PROFILE-TITLE] Profile: {profile_name}');
"""
            
            background_path = ext_dir / "background.js"
            with open(background_path, 'w', encoding='utf-8') as f:
                f.write(background_js)
            
            print(f"[EXTENSION] ✅ Created profile title extension: {ext_folder_name}")
            
            return True, str(ext_dir)
            
        except Exception as e:
            error_msg = f"Failed to create profile title extension: {e}"
            print(f"[WARNING] {error_msg}")
            return False, error_msg
    
    def get_profile_extensions(self, profile_name: str) -> List[str]:
        """
        Lấy danh sách extension paths cho profile
        
        Args:
            profile_name: Tên profile
        
        Returns:
            List các đường dẫn đến extension folders
        """
        extension_paths = []
        
        if not self.extensions_dir.exists():
            return extension_paths
        
        # Tìm extensions cho profile này
        # Format: ProxyAuth_{profile_name}, ProfileTitle_{profile_name}
        for ext_dir in self.extensions_dir.iterdir():
            if ext_dir.is_dir():
                # Check if extension belongs to this profile
                if profile_name in ext_dir.name or ext_dir.name.startswith('Global_'):
                    manifest_path = ext_dir / "manifest.json"
                    if manifest_path.exists():
                        extension_paths.append(str(ext_dir))
        
        return extension_paths
    
    def install_extension_from_crx(
        self,
        crx_path: str,
        extension_name: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Cài đặt extension từ file .crx
        
        Args:
            crx_path: Đường dẫn đến file .crx
            extension_name: Tên extension (optional)
        
        Returns:
            (success, extension_path_or_error)
        """
        # TODO: Implement CRX extraction and installation
        return False, "CRX installation not implemented yet"
    
    def install_extension_from_store(
        self,
        extension_id: str,
        extension_name: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Cài đặt extension từ Chrome Web Store
        
        Args:
            extension_id: Chrome extension ID
            extension_name: Tên extension (optional)
        
        Returns:
            (success, extension_path_or_error)
        """
        # TODO: Implement Chrome Web Store download
        return False, "Chrome Web Store installation not implemented yet"
    
    def remove_extension(self, extension_name: str) -> Tuple[bool, str]:
        """
        Xóa extension
        
        Args:
            extension_name: Tên extension folder
        
        Returns:
            (success, message)
        """
        try:
            ext_dir = self.extensions_dir / extension_name
            
            if not ext_dir.exists():
                return False, f"Extension not found: {extension_name}"
            
            shutil.rmtree(ext_dir)
            print(f"[EXTENSION] Removed extension: {extension_name}")
            
            return True, f"Extension removed: {extension_name}"
            
        except Exception as e:
            error_msg = f"Failed to remove extension: {e}"
            print(f"[ERROR] {error_msg}")
            return False, error_msg
    
    def list_extensions(self) -> List[Dict[str, str]]:
        """
        Liệt kê tất cả extensions
        
        Returns:
            List các extension info dicts
        """
        extensions = []
        
        if not self.extensions_dir.exists():
            return extensions
        
        for ext_dir in self.extensions_dir.iterdir():
            if ext_dir.is_dir():
                manifest_path = ext_dir / "manifest.json"
                if manifest_path.exists():
                    try:
                        with open(manifest_path, 'r', encoding='utf-8') as f:
                            manifest = json.load(f)
                        
                        extensions.append({
                            'folder': ext_dir.name,
                            'name': manifest.get('name', 'Unknown'),
                            'version': manifest.get('version', 'Unknown'),
                            'description': manifest.get('description', ''),
                            'path': str(ext_dir)
                        })
                    except Exception as e:
                        print(f"[WARNING] Failed to read manifest for {ext_dir.name}: {e}")
        
        return extensions
    
    def cleanup_profile_extensions(self, profile_name: str) -> int:
        """
        Xóa tất cả extensions của profile
        
        Args:
            profile_name: Tên profile
        
        Returns:
            Số lượng extensions đã xóa
        """
        count = 0
        
        for ext_path in self.get_profile_extensions(profile_name):
            ext_name = Path(ext_path).name
            success, _ = self.remove_extension(ext_name)
            if success:
                count += 1
        
        return count
