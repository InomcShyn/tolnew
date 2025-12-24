#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Profile Manager - Quản lý Chrome profiles
Converted from core/tiles/tile_profile_management.py
"""

import os
import json
import shutil
from pathlib import Path
from typing import List, Dict, Optional, Tuple


class ProfileManager:
    """Quản lý Chrome profiles với Playwright"""
    
    def __init__(self, profiles_dir: str = "chrome_profiles"):
        self.profiles_dir = Path(profiles_dir)
        self.profiles_dir.mkdir(exist_ok=True)
    
    def get_all_profiles(self) -> List[str]:
        """Lấy danh sách tất cả profiles"""
        if not self.profiles_dir.exists():
            return []
        
        profiles = [
            d.name for d in self.profiles_dir.iterdir()
            if d.is_dir() and not d.name.startswith('.')
        ]
        return sorted(profiles)
    
    def get_profile_path(self, profile_name: str) -> Path:
        """Lấy đường dẫn profile"""
        return self.profiles_dir / profile_name
    
    def profile_exists(self, profile_name: str) -> bool:
        """Kiểm tra profile có tồn tại không"""
        return self.get_profile_path(profile_name).exists()
    
    def create_profile(self, profile_name: str) -> Tuple[bool, str]:
        """
        Tạo profile mới
        
        Returns:
            (success, message)
        """
        try:
            profile_path = self.get_profile_path(profile_name)
            
            if profile_path.exists():
                return False, f"Profile '{profile_name}' already exists"
            
            # Tạo folder structure
            profile_path.mkdir(parents=True, exist_ok=True)
            default_path = profile_path / "Default"
            default_path.mkdir(exist_ok=True)
            
            # Tạo Preferences cơ bản
            prefs = {
                "profile": {
                    "name": profile_name,
                    "avatar_icon": "chrome://theme/IDR_PROFILE_AVATAR_0"
                },
                "browser": {
                    "show_home_button": False
                },
                "extensions": {
                    "settings": {}
                }
            }
            
            prefs_file = default_path / "Preferences"
            with open(prefs_file, 'w', encoding='utf-8') as f:
                json.dump(prefs, f, indent=2)
            
            # Tạo profile_settings.json
            import time
            settings = {
                "profile_info": {
                    "name": profile_name,
                    "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
                }
            }
            
            settings_file = profile_path / "profile_settings.json"
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2)
            
            return True, f"Profile '{profile_name}' created successfully"
            
        except Exception as e:
            return False, f"Error creating profile: {e}"
    
    def delete_profile(self, profile_name: str) -> Tuple[bool, str]:
        """Xóa profile"""
        try:
            profile_path = self.get_profile_path(profile_name)
            
            if not profile_path.exists():
                return False, f"Profile '{profile_name}' not found"
            
            shutil.rmtree(profile_path)
            return True, f"Profile '{profile_name}' deleted"
            
        except Exception as e:
            return False, f"Error deleting profile: {e}"
    
    def get_profile_settings(self, profile_name: str) -> Dict:
        """Đọc settings của profile"""
        settings_file = self.get_profile_path(profile_name) / "profile_settings.json"
        
        if not settings_file.exists():
            return {}
        
        try:
            with open(settings_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error reading settings for {profile_name}: {e}")
            return {}
    
    def save_profile_settings(self, profile_name: str, settings: Dict) -> bool:
        """Lưu settings của profile"""
        try:
            settings_file = self.get_profile_path(profile_name) / "profile_settings.json"
            
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"Error saving settings for {profile_name}: {e}")
            return False
    
    def bulk_create_profiles(
        self,
        base_name: str,
        quantity: int,
        proxy_list: Optional[List[str]] = None
    ) -> Tuple[bool, List[str]]:
        """
        Tạo nhiều profiles cùng lúc
        
        Args:
            base_name: Tên base cho profiles
            quantity: Số lượng profiles
            proxy_list: Danh sách proxy (optional)
        
        Returns:
            (success, list of created profile names)
        """
        created = []
        
        try:
            for i in range(quantity):
                profile_name = f"{base_name}_{i+1:04d}"
                
                success, msg = self.create_profile(profile_name)
                
                if success:
                    created.append(profile_name)
                    
                    # Set proxy if provided
                    if proxy_list and i < len(proxy_list):
                        from .proxy_manager import ProxyManager
                        proxy_mgr = ProxyManager(self)
                        proxy_mgr.set_profile_proxy(profile_name, proxy_list[i])
                else:
                    print(f"Failed to create {profile_name}: {msg}")
            
            return True, created
            
        except Exception as e:
            return False, created
    
    def get_profile_count(self) -> int:
        """Đếm số lượng profiles"""
        return len(self.get_all_profiles())
    
    def is_profile_in_use(self, profile_name: str) -> bool:
        """
        Kiểm tra profile có đang được sử dụng không
        (Check lock files)
        """
        profile_path = self.get_profile_path(profile_name)
        
        if not profile_path.exists():
            return False
        
        # Check lock files
        lock_files = [
            'DevToolsActivePort',
            'SingletonLock',
            'SingletonCookie',
            'SingletonSocket',
        ]
        
        for lock_file in lock_files:
            if (profile_path / lock_file).exists():
                return True
            if (profile_path / "Default" / lock_file).exists():
                return True
        
        return False
