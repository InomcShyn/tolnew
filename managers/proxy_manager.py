#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Proxy Manager - Quản lý proxy cho profiles
Converted from core/tiles/tile_proxy_management.py
"""

import os
import json
from typing import Dict, Optional, Tuple
from pathlib import Path


class ProxyManager:
    """Quản lý proxy configuration"""
    
    def __init__(self, profile_manager):
        self.profile_manager = profile_manager
    
    def parse_proxy_string(self, proxy_string: str) -> Dict:
        """
        Parse proxy string thành dict
        
        Hỗ trợ 2 formats:
        1. Standard: protocol://username:password@server:port
        2. Legacy: server:port:username:password hoặc protocol://server:port:username:password
        
        Returns:
            Dict với keys: protocol, server, port, username, password
        """
        if not proxy_string or proxy_string.lower() == 'null':
            return {}
        
        try:
            # Parse protocol
            if '://' in proxy_string:
                protocol, rest = proxy_string.split('://', 1)
            else:
                protocol = 'http'
                rest = proxy_string
            
            # Check if standard format: username:password@server:port
            if '@' in rest:
                # Standard format
                auth_part, server_part = rest.split('@', 1)
                
                # Parse auth
                if ':' in auth_part:
                    username, password = auth_part.split(':', 1)
                else:
                    username = auth_part
                    password = ''
                
                # Parse server:port
                if ':' in server_part:
                    server, port = server_part.split(':', 1)
                else:
                    server = server_part
                    port = '8080'  # Default port
                
                return {
                    'protocol': protocol,
                    'server': server,
                    'port': port,
                    'username': username,
                    'password': password
                }
            else:
                # Legacy format: server:port:username:password
                parts = rest.split(':')
                
                if len(parts) < 2:
                    return {}
                
                result = {
                    'protocol': protocol,
                    'server': parts[0],
                    'port': parts[1],
                }
                
                if len(parts) >= 4:
                    result['username'] = parts[2]
                    result['password'] = ':'.join(parts[3:])  # Password có thể chứa ':'
                
                return result
            
        except Exception as e:
            print(f"Error parsing proxy: {e}")
            import traceback
            traceback.print_exc()
            return {}
    
    def format_proxy_for_playwright(self, proxy_dict: Dict) -> Optional[Dict]:
        """
        Format proxy dict cho Playwright
        
        Returns:
            Dict format cho Playwright hoặc None
        """
        if not proxy_dict or not proxy_dict.get('server'):
            return None
        
        result = {
            'server': f"{proxy_dict['protocol']}://{proxy_dict['server']}:{proxy_dict['port']}"
        }
        
        if proxy_dict.get('username'):
            result['username'] = proxy_dict['username']
            result['password'] = proxy_dict.get('password', '')
        
        return result
    
    def set_profile_proxy(self, profile_name: str, proxy_string: str) -> bool:
        """
        Set proxy cho profile - Lưu vào config.ini VÀ GPM format
        
        Args:
            profile_name: Tên profile
            proxy_string: Proxy string
        
        Returns:
            success (bool)
        """
        try:
            # 1. Lưu vào config.ini
            import configparser
            config = configparser.ConfigParser()
            config_file = 'config.ini'
            
            # Read existing config
            if Path(config_file).exists():
                config.read(config_file, encoding='utf-8')
            
            # Ensure PROXY section exists
            if not config.has_section('PROXY'):
                config.add_section('PROXY')
            
            # Set proxy for profile
            config.set('PROXY', profile_name.lower(), proxy_string)
            
            # Save config
            with open(config_file, 'w', encoding='utf-8') as f:
                config.write(f)
            
            print(f"[PROXY] Saved proxy to config.ini: {proxy_string}")
            
            # 2. Đồng bộ sang GPM format
            try:
                from core.tiles.tile_gpm_proxy import sync_proxy_to_gpm
                
                profile_path = os.path.join(self.profile_manager.profiles_dir, profile_name)
                success, message = sync_proxy_to_gpm(profile_path, proxy_string)
                
                if success:
                    print(f"[PROXY] Synced to GPM format: {message}")
                else:
                    print(f"[PROXY] Warning - GPM sync failed: {message}")
                    # Không return False vì config.ini đã lưu thành công
                    
            except Exception as gpm_error:
                print(f"[PROXY] Warning - GPM sync error: {gpm_error}")
                # Không return False vì config.ini đã lưu thành công
            
            return True
                
        except Exception as e:
            print(f"[PROXY] Error setting proxy: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def get_profile_proxy(self, profile_name: str) -> Optional[str]:
        """
        Lấy proxy từ config.ini hoặc GPM format
        
        Priority:
        1. config.ini
        2. GPM format (gpm_pi.dat)
        """
        # 1. Thử đọc từ config.ini
        try:
            import configparser
            config = configparser.ConfigParser()
            config_file = 'config.ini'
            
            if Path(config_file).exists():
                config.read(config_file, encoding='utf-8')
                
                if config.has_section('PROXY'):
                    proxy = config.get('PROXY', profile_name.lower(), fallback=None)
                    
                    if proxy and proxy.lower() not in ('null', '', 'none'):
                        return proxy
            
        except Exception as e:
            print(f"[PROXY] Error reading config.ini: {e}")
        
        # 2. Thử đọc từ GPM format
        try:
            from core.tiles.tile_gpm_proxy import read_gpm_proxy
            
            profile_path = os.path.join(self.profile_manager.profiles_dir, profile_name)
            gpm_proxy = read_gpm_proxy(profile_path)
            
            if gpm_proxy:
                print(f"[PROXY] Found proxy in GPM format: {gpm_proxy}")
                return gpm_proxy
                
        except Exception as e:
            print(f"[PROXY] Could not read GPM proxy: {e}")
        
        return None
    
    def get_proxy_config_for_playwright(self, profile_name: str) -> Optional[Dict]:
        """
        Lấy proxy config cho Playwright
        
        Returns:
            Dict format cho Playwright hoặc None
        """
        proxy_string = self.get_profile_proxy(profile_name)
        
        if not proxy_string:
            return None
        
        proxy_dict = self.parse_proxy_string(proxy_string)
        return self.format_proxy_for_playwright(proxy_dict)
    
    def bulk_set_proxy(self, profile_proxy_map: Dict[str, str]) -> Tuple[int, int]:
        """
        Set proxy cho nhiều profiles
        
        Args:
            profile_proxy_map: Dict mapping profile_name -> proxy_string
        
        Returns:
            (success_count, failed_count)
        """
        success_count = 0
        failed_count = 0
        
        for profile_name, proxy_string in profile_proxy_map.items():
            success, msg = self.set_profile_proxy(profile_name, proxy_string)
            
            if success:
                success_count += 1
            else:
                failed_count += 1
                print(f"Failed to set proxy for {profile_name}: {msg}")
        
        return success_count, failed_count
    
    def remove_profile_proxy(self, profile_name: str) -> bool:
        """Xóa proxy khỏi profile"""
        try:
            import configparser
            config = configparser.ConfigParser()
            config_file = 'config.ini'
            
            if not Path(config_file).exists():
                return True  # Already no proxy
            
            config.read(config_file, encoding='utf-8')
            
            if not config.has_section('PROXY'):
                return True  # Already no proxy
            
            # Remove proxy option
            if config.has_option('PROXY', profile_name.lower()):
                config.remove_option('PROXY', profile_name.lower())
                
                # Save config
                with open(config_file, 'w', encoding='utf-8') as f:
                    config.write(f)
                
                print(f"[PROXY] Removed proxy for {profile_name}")
            
            return True
            
        except Exception as e:
            print(f"[PROXY] Error removing proxy: {e}")
            return False
    
    def test_proxy(self, proxy_string: str) -> Tuple[bool, str]:
        """
        Test proxy connection
        
        Returns:
            (success, message)
        """
        try:
            import requests
            
            proxy_dict = self.parse_proxy_string(proxy_string)
            
            if not proxy_dict:
                return False, "Invalid proxy format"
            
            # Build proxy URL
            if proxy_dict.get('username'):
                proxy_url = f"{proxy_dict['protocol']}://{proxy_dict['username']}:{proxy_dict['password']}@{proxy_dict['server']}:{proxy_dict['port']}"
            else:
                proxy_url = f"{proxy_dict['protocol']}://{proxy_dict['server']}:{proxy_dict['port']}"
            
            proxies = {
                'http': proxy_url,
                'https': proxy_url
            }
            
            # Test connection
            response = requests.get('http://httpbin.org/ip', proxies=proxies, timeout=10)
            
            if response.status_code == 200:
                ip = response.json().get('origin', 'Unknown')
                return True, f"Proxy OK! IP: {ip}"
            else:
                return False, f"Proxy failed with status {response.status_code}"
                
        except Exception as e:
            return False, f"Proxy test error: {e}"
