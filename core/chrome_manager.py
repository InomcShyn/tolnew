#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chrome Manager Playwright - Full replacement for core/chrome_manager.py
Chuyển đổi TOÀN BỘ ChromeProfileManager sang Playwright
"""

import os
import json
import asyncio
import configparser
import traceback
from pathlib import Path
from typing import Optional, List, Dict, Tuple, Any
from datetime import datetime

# Import Playwright managers
from .managers.profile_manager import ProfileManager
from .managers.proxy_manager import ProxyManager
from .managers.browser_manager import BrowserManager
from .managers.extension_manager import ExtensionManager
from .managers.config_manager import ConfigManager
from .utils.logging import LoggingManager
from .utils.cleanup import CleanupManager

# Import tile functions
from .tiles.tile_user_agent import generate_user_agent, generate_random_mac
from .tiles.tile_stealth_config import (
    get_stealth_configs_list,
    load_stealth_config,
    save_stealth_config,
    delete_stealth_config
)
from .tiles.tile_extension_management import (
    install_extension_from_crx,
    install_extension_for_all_profiles,
    install_extension_for_new_profiles
)
from .tiles.tile_cleanup import clear_browsing_history
from .tiles.tile_livestream import run_livestream_profiles, run_livestream_advanced


class ChromeProfileManager:
    """
    Full replacement for ChromeProfileManager
    Sử dụng Playwright thay vì Selenium
    
    Compatible API với chrome_manager.py nhưng backend là Playwright
    """
    
    def __init__(self):
        """Initialize Chrome Manager với Playwright backend"""
        # Config
        self.config_file = "config.ini"
        self.config = configparser.ConfigParser()
        
        # Directories
        self.profiles_dir = os.path.join(os.getcwd(), "chrome_profiles")
        self.chrome_data_dir = self._get_chrome_data_dir()
        
        # Initialize managers
        self.profile_mgr = ProfileManager(self.profiles_dir)
        self.proxy_mgr = ProxyManager(self.profile_mgr)
        self.extension_mgr = ExtensionManager()
        self.browser_mgr = BrowserManager(self.profile_mgr, self.proxy_mgr)
        self.config_mgr = ConfigManager(self.config_file)
        self.logging_mgr = LoggingManager(self.profiles_dir)
        self.cleanup_mgr = CleanupManager(self.browser_mgr)
        
        # Load config
        self.load_config()
        
        # GPM defaults
        self.gpm_defaults = {}
        self._load_gpm_setting()
        
        # Current profile tracking
        self.current_profile_name = None
        
        # Event loop management for Playwright
        self._loop = None
        self._playwright_started = False
    
    # ============================================================
    # CONFIG MANAGEMENT
    # ============================================================
    
    def load_config(self):
        """Load configuration from file"""
        self.config = self.config_mgr.load()
        return self.config
    
    def create_default_config(self):
        """Create default configuration file"""
        self.config_mgr.create_default()
        self.config = self.config_mgr.config
        return self.config
    
    def save_config(self):
        """Save configuration to file"""
        return self.config_mgr.save()
    
    # ============================================================
    # PROFILE MANAGEMENT
    # ============================================================
    
    def create_profile_directory(self):
        """Create profiles directory if not exists"""
        self.profile_mgr.profiles_dir.mkdir(exist_ok=True)
        return True
    
    def create_profile_with_extension(
        self, 
        profile_name: str, 
        source_profile: str = "Default",
        auto_install_extension: bool = True
    ) -> Tuple[bool, str]:
        """
        Create new profile
        Note: auto_install_extension ignored (Playwright không cần extensions)
        """
        return self.profile_mgr.create_profile(profile_name)
    
    def create_profiles_bulk(
        self,
        base_name: str,
        quantity: int,
        version: str,
        use_random_format: bool,
        proxy_list: List[str],
        use_random_hardware: bool,
        use_random_ua: bool = False,
        start_number: int = None,
        prefix_number: int = None
    ) -> Tuple[bool, List[str]]:
        """
        Create multiple profiles in bulk
        
        Args:
            base_name: Base name for profiles
            quantity: Number of profiles to create
            version: Chrome version
            use_random_format: Use random format for profile names
            proxy_list: List of proxy strings
            use_random_hardware: Use random hardware fingerprints
            use_random_ua: Use random user agents
            start_number: Optional starting number for profile naming
            prefix_number: Optional prefix number for random format
        
        Returns:
            (success, list_of_profile_names or error_message)
        """
        # Use tile function for full implementation
        from core.tiles.tile_profile_management import create_profiles_bulk as tile_create_bulk
        
        return tile_create_bulk(
            manager=self,
            base_name=base_name,
            quantity=quantity,
            version=version,
            use_random_format=use_random_format,
            proxy_list=proxy_list,
            use_random_hardware=use_random_hardware,
            use_random_ua=use_random_ua,
            start_number=start_number,
            prefix_number=prefix_number
        )
    
    def clone_chrome_profile(
        self,
        profile_name: str,
        source_profile: str = "Default",
        profile_type: str = "work"
    ) -> Tuple[bool, str]:
        """Clone/create profile"""
        return self.profile_mgr.create_profile(profile_name)
    
    def get_all_profiles(self, force_refresh: bool = False) -> List[str]:
        """
        Get all profiles
        
        Args:
            force_refresh: Force refresh (ignored, kept for compatibility)
        
        Returns:
            List of profile names
        """
        return self.profile_mgr.get_all_profiles()
    
    def get_profile_path(self, profile_name: str) -> str:
        """Get profile path"""
        return str(self.profile_mgr.get_profile_path(profile_name))
    
    def is_profile_in_use(self, profile_name_or_path: str) -> bool:
        """Check if profile is in use"""
        if os.path.isabs(profile_name_or_path):
            # Extract profile name from path
            profile_name = os.path.basename(profile_name_or_path)
        else:
            profile_name = profile_name_or_path
        
        return self.profile_mgr.is_profile_in_use(profile_name)
    
    def delete_profile(self, profile_name: str) -> Tuple[bool, str]:
        """Delete profile"""
        return self.profile_mgr.delete_profile(profile_name)
    
    # ============================================================
    # PROXY MANAGEMENT
    # ============================================================
    
    def _set_profile_proxy(self, profile_name: str, proxy_string: str) -> Tuple[bool, str]:
        """Set proxy for profile"""
        return self.proxy_mgr.set_profile_proxy(profile_name, proxy_string)
    
    def apply_proxy_via_settings(self, profile_name: str, proxy_config: Dict) -> Tuple[bool, str]:
        """Apply proxy via settings"""
        # Convert dict to string format
        proxy_string = f"{proxy_config.get('proxy_server')}:{proxy_config.get('proxy_port')}"
        if proxy_config.get('username'):
            proxy_string += f":{proxy_config['username']}:{proxy_config.get('password', '')}"
        
        return self.proxy_mgr.set_profile_proxy(profile_name, proxy_string)
    
    def apply_proxy_via_settings_string(self, profile_name: str, proxy_string: str) -> Tuple[bool, str]:
        """Apply proxy via string"""
        return self.proxy_mgr.set_profile_proxy(profile_name, proxy_string)
    
    def bulk_apply_proxy_map_via_settings(self, profile_to_proxy_map: Dict[str, str]) -> Tuple[List, int]:
        """Bulk apply proxy"""
        success_count, failed_count = self.proxy_mgr.bulk_set_proxy(profile_to_proxy_map)
        results = []
        for profile, proxy in profile_to_proxy_map.items():
            results.append({
                'profile': profile,
                'success': True,  # Simplified
                'message': 'OK'
            })
        return results, success_count
    
    def test_proxy_connection(self, proxy_string: str) -> Tuple[bool, str]:
        """Test proxy connection"""
        return self.proxy_mgr.test_proxy(proxy_string)
    
    def get_proxy_from_profile_settings(self, profile_name: str) -> Optional[str]:
        """Get proxy from profile settings"""
        return self.proxy_mgr.get_profile_proxy(profile_name)
    
    def get_profiles_with_proxy(self) -> List[str]:
        """Get profiles that have proxy configured"""
        profiles = []
        for profile in self.get_all_profiles():
            if self.proxy_mgr.get_profile_proxy(profile):
                profiles.append(profile)
        return profiles
    
    def get_profiles_without_proxy(self) -> List[str]:
        """Get profiles without proxy"""
        profiles = []
        for profile in self.get_all_profiles():
            if not self.proxy_mgr.get_profile_proxy(profile):
                profiles.append(profile)
        return profiles
    
    def configure_switchyomega_proxy(self, profile_name: str, proxy_config: Dict) -> Tuple[bool, str]:
        """
        DEPRECATED: SwitchyOmega removed in Playwright version
        Use direct proxy configuration instead
        """
        print("[WARNING] configure_switchyomega_proxy is deprecated")
        print("[INFO] Using direct proxy configuration via Playwright")
        
        # Convert to proxy string and use direct method
        try:
            server = proxy_config.get('proxy_server', '')
            port = proxy_config.get('proxy_port', '')
            username = proxy_config.get('username', '')
            password = proxy_config.get('password', '')
            
            if username and password:
                proxy_string = f"http://{server}:{port}:{username}:{password}"
            else:
                proxy_string = f"http://{server}:{port}"
            
            return self.proxy_mgr.set_profile_proxy(profile_name, proxy_string)
        except Exception as e:
            return False, f"Error: {e}"
    
    def get_switchyomega_profiles(self, profile_name: str) -> List[Dict]:
        """
        DEPRECATED: SwitchyOmega removed in Playwright version
        Returns empty list
        """
        print("[WARNING] get_switchyomega_profiles is deprecated")
        print("[INFO] SwitchyOmega extension removed in Playwright version")
        return []
    
    def bulk_configure_switchyomega(self, profile_list: List[str], proxy_config: Dict) -> Tuple[int, List]:
        """
        DEPRECATED: SwitchyOmega removed in Playwright version
        Use bulk proxy configuration instead
        """
        print("[WARNING] bulk_configure_switchyomega is deprecated")
        print("[INFO] Using direct proxy configuration via Playwright")
        
        results = []
        success_count = 0
        
        for profile_name in profile_list:
            success, message = self.configure_switchyomega_proxy(profile_name, proxy_config)
            results.append({
                'profile': profile_name,
                'success': success,
                'message': message
            })
            if success:
                success_count += 1
        
        return success_count, results
    
    # ============================================================
    # BROWSER LAUNCH (CORE METHOD)
    # ============================================================
    
    async def launch_chrome_profile_async(
        self,
        profile_name: str,
        hidden: bool = True,
        auto_login: bool = False,
        login_data: Optional[Dict] = None,
        start_url: Optional[str] = None,
        optimized_mode: bool = False,
        ultra_low_memory: bool = False,
        headless: bool = False
    ):
        """
        Launch Chrome profile với Playwright (Async version)
        
        Args:
            profile_name: Tên profile
            hidden: Minimize window to taskbar (still visible in taskbar)
            auto_login: Auto login with keyboard autofill
            login_data: Login data (username/email and password)
            start_url: URL để mở
            optimized_mode: Optimized mode
            ultra_low_memory: Ultra low memory mode (GPU HYBRID MODE always enabled)
            headless: True headless mode (no window at all, runs in background)
        
        Returns:
            (success, page_or_message)
        """
        try:
            self.current_profile_name = profile_name
            
            # Launch profile with autofill support
            # headless=True → no window at all (background only)
            # hidden=True → minimize window (still visible in taskbar)
            page = await self.browser_mgr.launch_profile(
                profile_name=profile_name,
                url=start_url,
                headless=headless,  # True headless mode if requested
                minimize=hidden if not headless else False,  # Minimize only if not headless
                ultra_low_cpu=ultra_low_memory,
                auto_login=auto_login,
                login_data=login_data
            )
            
            if page:
                return True, page
            else:
                return False, f"Failed to launch {profile_name}"
                
        except Exception as e:
            print(f"[ERROR] Launch failed: {e}")
            return False, str(e)
    
    def launch_chrome_profile(self, *args, **kwargs):
        """
        Sync wrapper for launch_chrome_profile_async
        Compatible với code cũ
        """
        # Check if we're already in an async context
        try:
            loop = asyncio.get_running_loop()
            # We're in an async context, create a task
            import nest_asyncio
            nest_asyncio.apply()
        except RuntimeError:
            # Not in async context, create new loop
            pass
        
        # Ensure we have an event loop
        try:
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        # Store loop reference
        self._loop = loop
        
        # Start Playwright if not started
        if not self._playwright_started:
            if loop.is_running():
                # Loop is running, use nest_asyncio
                import nest_asyncio
                nest_asyncio.apply()
            loop.run_until_complete(self.browser_mgr.start())
            self._playwright_started = True
        
        # Run the async function
        return loop.run_until_complete(self.launch_chrome_profile_async(*args, **kwargs))
    
    # ============================================================
    # BROWSER CONTROL
    # ============================================================
    
    def get_page(self, profile_name: str):
        """Get Page object for profile"""
        return self.browser_mgr.get_page(profile_name)
    
    def get_context(self, profile_name: str):
        """Get BrowserContext for profile"""
        return self.browser_mgr.get_context(profile_name)
    
    async def close_profile_async(self, profile_name: str):
        """Close profile (async)"""
        await self.browser_mgr.close_profile(profile_name)
    
    def close_profile(self, profile_name: str):
        """Close profile (sync wrapper)"""
        if self._loop and not self._loop.is_closed():
            self._loop.run_until_complete(self.close_profile_async(profile_name))
        else:
            asyncio.run(self.close_profile_async(profile_name))
    
    async def close_all_profiles_async(self):
        """Close all profiles (async)"""
        await self.browser_mgr.close_all_profiles()
    
    def close_all_profiles(self):
        """Close all profiles (sync wrapper)"""
        if self._loop and not self._loop.is_closed():
            self._loop.run_until_complete(self.close_all_profiles_async())
        else:
            asyncio.run(self.close_all_profiles_async())
    
    def get_running_profiles(self) -> List[str]:
        """Get list of running profiles"""
        return self.browser_mgr.get_running_profiles()
    
    # ============================================================
    # MEMORY MANAGEMENT
    # ============================================================
    
    def get_memory_usage(self):
        """Lấy thông tin sử dụng RAM của Chrome processes"""
        try:
            import psutil
            chrome_memory = 0
            chrome_processes = 0
            
            for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
                try:
                    if 'chrome' in proc.info['name'].lower():
                        chrome_memory += proc.info['memory_info'].rss
                        chrome_processes += 1
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Convert to MB
            chrome_memory_mb = chrome_memory / (1024 * 1024)
            
            return {
                'chrome_memory_mb': round(chrome_memory_mb, 2),
                'chrome_processes': chrome_processes,
                'system_memory_percent': psutil.virtual_memory().percent,
                'available_memory_gb': round(psutil.virtual_memory().available / (1024**3), 2)
            }
        except Exception as e:
            print(f"[WARNING] [MEMORY] Error getting memory info: {e}")
            return {
                'chrome_memory_mb': 0,
                'chrome_processes': 0,
                'system_memory_percent': 0,
                'available_memory_gb': 0
            }
    
    def cleanup_memory(self):
        """Dọn dẹp memory và optimize"""
        try:
            import gc
            
            # Force garbage collection
            gc.collect()
            
            # Get current memory usage
            memory_info = self.get_memory_usage()
            if memory_info:
                print(f"[CLEANUP] Chrome RAM: {memory_info['chrome_memory_mb']}MB")
                print(f"[CLEANUP] System RAM: {memory_info['system_memory_percent']}%")
                print(f"[CLEANUP] Available: {memory_info['available_memory_gb']}GB")
            
            return memory_info
        except Exception as e:
            print(f"[WARNING] [MEMORY-CLEANUP] Error: {e}")
            return None
    
    # ============================================================
    # COOKIES & SESSION
    # ============================================================
    
    async def get_cookies_async(self, profile_name: str) -> List[Dict]:
        """Get cookies from profile (async)"""
        return await self.browser_mgr.get_cookies(profile_name)
    
    def get_cookies(self, profile_name: str) -> List[Dict]:
        """Get cookies from profile (sync wrapper)"""
        return asyncio.run(self.get_cookies_async(profile_name))
    
    async def set_cookies_async(self, profile_name: str, cookies: List[Dict]):
        """Set cookies for profile (async)"""
        await self.browser_mgr.set_cookies(profile_name, cookies)
    
    def set_cookies(self, profile_name: str, cookies: List[Dict]):
        """Set cookies for profile (sync wrapper)"""
        asyncio.run(self.set_cookies_async(profile_name, cookies))
    
    # ============================================================
    # HELPER METHODS
    # ============================================================
    
    def _get_chrome_data_dir(self) -> str:
        """Get Chrome data directory"""
        tool_chrome_dir = os.path.join(os.getcwd(), "chrome_data")
        return tool_chrome_dir
    
    def _load_gpm_setting(self):
        """Load GPM settings"""
        try:
            from .managers.profile_manager import ProfileManager
            # Load GPM defaults if exists
            self.gpm_defaults = {}
        except Exception:
            self.gpm_defaults = {}
    
    def _get_omocaptcha_api_key_from_config(self) -> str:
        """Get OMOcaptcha API key from config"""
        try:
            if self.config.has_section('CAPTCHA'):
                key = self.config.get('CAPTCHA', 'omocaptcha_api_key', fallback='')
                if key and key.lower() not in ('your_api_key_here', ''):
                    return key
        except Exception:
            pass
        return ''
    
    # ============================================================
    # EXTENSION MANAGEMENT (HỖ TRỢ ĐẦY ĐỦ)
    # ============================================================
    
    def install_extension(
        self,
        extension_id: str,
        extension_name: Optional[str] = None,
        profile_name: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Cài đặt extension (stub - chưa hỗ trợ download từ Chrome Web Store)
        
        LƯU Ý: Hiện tại chỉ hỗ trợ:
        - Proxy auth extension (tự động tạo)
        - Profile title extension (tự động tạo)
        
        Args:
            extension_id: Chrome extension ID (chưa sử dụng)
            extension_name: Tên extension
            profile_name: Tên profile (optional)
        
        Returns:
            (success, message)
        """
        print("[INFO] Extension installation from Chrome Web Store not implemented yet")
        print("[INFO] Proxy auth extensions are created automatically when needed")
        return False, "Manual extension installation not supported yet"
    
    def install_extension_for_profile(
        self,
        profile_name: str,
        extension_id: str = "",
        extension_name: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Cài đặt extension cho profile cụ thể
        
        LƯU Ý: Extensions được tạo tự động khi cần:
        - Proxy auth: Tự động tạo khi profile có proxy với username/password
        - Profile title: Tự động tạo khi launch profile
        """
        return self.install_extension(extension_id, extension_name, profile_name)
    
    def check_extension_installed(
        self,
        profile_name: str,
        extension_id: str = ""
    ) -> bool:
        """
        Kiểm tra extension đã cài đặt chưa
        
        Returns:
            True nếu có extensions cho profile
        """
        extensions = self.extension_mgr.get_profile_extensions(profile_name)
        return len(extensions) > 0
    
    def list_profile_extensions(self, profile_name: str) -> List[str]:
        """
        Liệt kê extensions của profile
        
        Returns:
            List các extension paths
        """
        return self.extension_mgr.get_profile_extensions(profile_name)
    
    def list_all_extensions(self) -> List[Dict[str, str]]:
        """
        Liệt kê tất cả extensions
        
        Returns:
            List các extension info dicts
        """
        return self.extension_mgr.list_extensions()
    
    def remove_profile_extensions(self, profile_name: str) -> int:
        """
        Xóa tất cả extensions của profile
        
        Returns:
            Số lượng extensions đã xóa
        """
        return self.extension_mgr.cleanup_profile_extensions(profile_name)
    
    def create_proxy_auth_extension(
        self,
        profile_name: str,
        username: str,
        password: str
    ) -> Tuple[bool, str]:
        """
        Tạo proxy authentication extension
        
        Args:
            profile_name: Tên profile
            username: Proxy username
            password: Proxy password
        
        Returns:
            (success, extension_path_or_error)
        """
        return self.extension_mgr.create_proxy_auth_extension(
            profile_name, username, password
        )
    
    # ============================================================
    # LOGGING
    # ============================================================
    
    def _append_app_log(self, profile_name: str, message: str, level: str = "INFO"):
        """Append log message"""
        self.logging_mgr.append_app_log(profile_name, message, level)
    
    def get_chrome_log_path(self, profile_name: str) -> str:
        """Get log file path"""
        return self.logging_mgr.get_chrome_log_path(profile_name)
    
    def read_chrome_log(self, profile_name: str, tail_lines: int = 200) -> str:
        """Read log file"""
        return self.logging_mgr.read_chrome_log(profile_name, tail_lines)
    
    # ============================================================
    # CLEANUP & MAINTENANCE
    # ============================================================
    
    async def clear_browsing_history_async(
        self,
        profile_names: List[str],
        keep_passwords: bool = True,
        keep_cache: bool = True
    ) -> dict:
        """Clear browsing history (async)"""
        return await self.cleanup_mgr.clear_browsing_history(
            profile_names, keep_passwords, keep_cache
        )
    
    def clear_browsing_history(
        self,
        profile_names: List[str],
        keep_passwords: bool = True,
        keep_cache: bool = True
    ) -> dict:
        """Clear browsing history (sync wrapper)"""
        return asyncio.run(
            self.clear_browsing_history_async(profile_names, keep_passwords, keep_cache)
        )
    
    def start_daily_history_cleanup(
        self,
        hour: int = 3,
        minute: int = 0,
        profiles: Optional[List[str]] = None,
        jitter_sec: int = 90
    ):
        """Start daily cleanup schedule"""
        self.cleanup_mgr.start_daily_history_cleanup(hour, minute, profiles, jitter_sec)
    
    def stop_daily_history_cleanup(self):
        """Stop daily cleanup schedule"""
        self.cleanup_mgr.stop_daily_history_cleanup()
    
    async def stop_async(self):
        """Stop manager and cleanup (async)"""
        # Stop cleanup scheduler
        self.cleanup_mgr.stop_daily_history_cleanup()
        
        # Stop browser manager
        await self.browser_mgr.stop()
    
    def stop(self):
        """Stop manager and cleanup (sync wrapper)"""
        try:
            # Try to run cleanup in existing loop if available
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Schedule cleanup for later
                asyncio.create_task(self.stop_async())
            else:
                # Run cleanup now
                asyncio.run(self.stop_async())
        except Exception:
            # Fallback: just stop cleanup manager
            try:
                self.cleanup_mgr.stop_daily_history_cleanup()
            except:
                pass
    
    def shutdown(self):
        """Properly shutdown Playwright and cleanup resources"""
        try:
            if self._playwright_started and self._loop and not self._loop.is_closed():
                # Stop Playwright
                self._loop.run_until_complete(self.browser_mgr.stop())
                self._playwright_started = False
            
            # Stop cleanup manager (only once)
            if hasattr(self, 'cleanup_mgr') and not getattr(self, '_cleanup_stopped', False):
                self.cleanup_mgr.stop_daily_history_cleanup()
                self._cleanup_stopped = True
        except Exception as e:
            print(f"[WARNING] Error during shutdown: {e}")
    
    def __del__(self):
        """Cleanup on deletion"""
        try:
            # Only stop cleanup manager if not already stopped
            # This avoids asyncio warnings during garbage collection
            if hasattr(self, 'cleanup_mgr') and not getattr(self, '_cleanup_stopped', False):
                self.cleanup_mgr.stop_daily_history_cleanup()
                self._cleanup_stopped = True
        except:
            pass
    
    # ============================================================
    # PROFILE STATUS CHECKING
    # ============================================================
    
    def is_profile_logged_in(self, profile_name: str) -> bool:
        """
        Check if profile is logged in to TikTok
        
        Checks multiple indicators:
        1. Marker file (tiktok_logged_in.txt)
        2. Session data (tiktok_session.json)
        3. Recent cookies
        
        Args:
            profile_name: Profile name
        
        Returns:
            True if logged in, False otherwise
        """
        try:
            import time
            profile_path = os.path.join(self.profiles_dir, profile_name)
            
            # Method 1: Check marker file
            marker_file = os.path.join(profile_path, 'tiktok_logged_in.txt')
            if os.path.exists(marker_file):
                try:
                    with open(marker_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if 'timestamp=' in content:
                            import re
                            timestamp_match = re.search(r'timestamp=(\d+\.?\d*)', content)
                            if timestamp_match:
                                timestamp = float(timestamp_match.group(1))
                                current_time = time.time()
                                # Check if marker is less than 7 days old
                                if current_time - timestamp < 7 * 24 * 3600:
                                    return True
                except:
                    pass
            
            # Method 2: Check TikTok session data
            session_file = os.path.join(profile_path, 'tiktok_session.json')
            if os.path.exists(session_file):
                try:
                    with open(session_file, 'r', encoding='utf-8') as f:
                        session_data = json.load(f)
                        
                        # Check if has valid session token
                        session_token = session_data.get('session_token', '')
                        if session_token and len(session_token) > 10:
                            return True
                        
                        # Check if has recent saved_at timestamp
                        saved_at = session_data.get('saved_at', '')
                        if saved_at:
                            try:
                                dt = datetime.fromisoformat(saved_at)
                                current_time = datetime.now()
                                # Check if session is less than 7 days old
                                if (current_time - dt).days < 7:
                                    return True
                            except:
                                pass
                except:
                    pass
            
            # Method 3: Check if profile has recent TikTok cookies
            cookies_file = os.path.join(profile_path, 'Default', 'Cookies')
            if os.path.exists(cookies_file):
                try:
                    mod_time = os.path.getmtime(cookies_file)
                    current_time = time.time()
                    # Check if cookies file is recent (within 7 days)
                    if current_time - mod_time < 7 * 24 * 3600:
                        return True
                except:
                    pass
            
            return False
            
        except Exception as e:
            print(f"❌ [CHECK] Error checking login status for {profile_name}: {e}")
            return False
    
    # ============================================================
    # TIKTOK SESSION MANAGEMENT
    # ============================================================
    
    def load_tiktok_session(self, profile_name: str) -> Tuple[bool, Any]:
        """
        Load TikTok session from Chrome profile
        
        Args:
            profile_name: Profile name
        
        Returns:
            (success, session_data or error_message)
        """
        try:
            # Ensure profile_name is string (fix for integer profile names)
            profile_name = str(profile_name)
            print(f"📂 [LOAD-SESSION] Load TikTok session for {profile_name}")
            
            # Try load from config file first
            if self.config.has_section('TIKTOK_SESSIONS') and self.config.has_option('TIKTOK_SESSIONS', profile_name):
                session_json = self.config.get('TIKTOK_SESSIONS', profile_name)
                session_data = json.loads(session_json)
                print(f"✅ [LOAD-SESSION] Loaded session from config")
                return True, session_data
            
            # Try load from Chrome profile directory
            profile_path = os.path.join(self.profiles_dir, profile_name)
            session_file = os.path.join(profile_path, 'tiktok_session.json')
            
            if os.path.exists(session_file):
                with open(session_file, 'r', encoding='utf-8') as f:
                    session_data = json.load(f)
                print(f"✅ [LOAD-SESSION] Loaded session from {session_file}")
                return True, session_data
            
            print(f"⚠️ [LOAD-SESSION] No session found for {profile_name}")
            return False, "No TikTok session found"
            
        except Exception as e:
            print(f"❌ [LOAD-SESSION] Error: {e}")
            return False, f"Error loading session: {str(e)}"
    
    def save_tiktok_session(self, profile_name: str, session_data: Dict) -> Tuple[bool, str]:
        """
        Save TikTok session to Chrome profile
        
        Args:
            profile_name: Profile name
            session_data: Session data dict
        
        Returns:
            (success, message)
        """
        try:
            print(f"💾 [SAVE-SESSION] Saving TikTok session for {profile_name}")
            
            # Save to config
            if not self.config.has_section('TIKTOK_SESSIONS'):
                self.config.add_section('TIKTOK_SESSIONS')
            
            session_json = json.dumps(session_data)
            self.config.set('TIKTOK_SESSIONS', profile_name, session_json)
            self.save_config()
            
            # Save to Chrome profile directory
            profile_path = os.path.join(self.profiles_dir, profile_name)
            os.makedirs(profile_path, exist_ok=True)
            
            session_file = os.path.join(profile_path, 'tiktok_session.json')
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2)
            
            print(f"✅ [SAVE-SESSION] Session saved successfully")
            return True, "Session saved successfully"
            
        except Exception as e:
            print(f"❌ [SAVE-SESSION] Error: {e}")
            return False, f"Error saving session: {str(e)}"
    
    def clear_tiktok_session(self, profile_name: str) -> Tuple[bool, str]:
        """
        Clear TikTok session
        
        Args:
            profile_name: Profile name
        
        Returns:
            (success, message)
        """
        try:
            print(f"🗑️ [CLEAR-SESSION] Clearing TikTok session for {profile_name}")
            
            # Remove from config
            if self.config.has_section('TIKTOK_SESSIONS') and self.config.has_option('TIKTOK_SESSIONS', profile_name):
                self.config.remove_option('TIKTOK_SESSIONS', profile_name)
                self.save_config()
            
            # Remove from Chrome profile directory
            profile_path = os.path.join(self.profiles_dir, profile_name)
            session_file = os.path.join(profile_path, 'tiktok_session.json')
            
            if os.path.exists(session_file):
                os.remove(session_file)
            
            print(f"✅ [CLEAR-SESSION] Session cleared successfully")
            return True, "Session cleared successfully"
            
        except Exception as e:
            print(f"❌ [CLEAR-SESSION] Error: {e}")
            return False, f"Error clearing session: {str(e)}"
    
    def get_all_tiktok_sessions(self) -> Tuple[bool, Dict[str, Dict]]:
        """
        Get all TikTok sessions from all profiles
        
        Returns:
            (success, dict of {profile_name: session_data})
        """
        try:
            print(f"📋 [GET-ALL-SESSIONS] Getting all TikTok sessions...")
            
            all_sessions = {}
            
            # Get from config
            if self.config.has_section('TIKTOK_SESSIONS'):
                for profile_name in self.config.options('TIKTOK_SESSIONS'):
                    try:
                        session_json = self.config.get('TIKTOK_SESSIONS', profile_name)
                        session_data = json.loads(session_json)
                        all_sessions[profile_name] = session_data
                    except Exception as e:
                        print(f"⚠️ [GET-ALL-SESSIONS] Error loading session for {profile_name}: {e}")
            
            # Get from profile directories
            if os.path.exists(self.profiles_dir):
                for profile_name in os.listdir(self.profiles_dir):
                    profile_path = os.path.join(self.profiles_dir, profile_name)
                    if not os.path.isdir(profile_path):
                        continue
                    
                    session_file = os.path.join(profile_path, 'tiktok_session.json')
                    if os.path.exists(session_file) and profile_name not in all_sessions:
                        try:
                            with open(session_file, 'r', encoding='utf-8') as f:
                                session_data = json.load(f)
                            all_sessions[profile_name] = session_data
                        except Exception as e:
                            print(f"⚠️ [GET-ALL-SESSIONS] Error loading session file for {profile_name}: {e}")
            
            print(f"✅ [GET-ALL-SESSIONS] Found {len(all_sessions)} sessions")
            return True, all_sessions
            
        except Exception as e:
            print(f"❌ [GET-ALL-SESSIONS] Error: {e}")
            return False, {}
    
    def is_profile_logged_in(self, profile_name: str) -> bool:
        """
        Check if profile has TikTok session (is logged in)
        
        Args:
            profile_name: Profile name
        
        Returns:
            True if profile has valid session, False otherwise
        """
        try:
            # Check config first
            if self.config.has_section('TIKTOK_SESSIONS') and self.config.has_option('TIKTOK_SESSIONS', profile_name):
                return True
            
            # Check profile directory
            profile_path = os.path.join(self.profiles_dir, profile_name)
            session_file = os.path.join(profile_path, 'tiktok_session.json')
            
            if os.path.exists(session_file):
                # Verify file is valid JSON
                try:
                    with open(session_file, 'r', encoding='utf-8') as f:
                        session_data = json.load(f)
                    # Check if session has required data
                    if session_data and isinstance(session_data, dict):
                        return True
                except:
                    pass
            
            return False
            
        except Exception as e:
            print(f"⚠️ [IS-LOGGED-IN] Error checking {profile_name}: {e}")
            return False
    
    # ============================================================
    # EXTENSION MANAGEMENT
    # ============================================================
    
    def ensure_extension_installed(self, profile_name: str, extension_id: str = "pfnededegaaopdmhkdmcofjmoldfiped") -> bool:
        """
        Ensure extension is installed for profile
        
        Note: Playwright không cần extensions như Selenium.
        Method này giữ lại để compatibility với code cũ.
        
        Args:
            profile_name: Profile name
            extension_id: Extension ID (ignored in Playwright)
        
        Returns:
            True (always, for compatibility)
        """
        try:
            print(f"ℹ️ [ENSURE-EXTENSION] Playwright không cần extension cho {profile_name}")
            print(f"ℹ️ [ENSURE-EXTENSION] Proxy auth được xử lý tự động bởi Playwright")
            return True
            
        except Exception as e:
            print(f"❌ [ENSURE-EXTENSION] Error: {e}")
            return False
    
    def check_extension_installed(self, profile_name: str, extension_id: str = "pfnededegaaopdmhkdmcofjmoldfiped") -> bool:
        """
        Check if extension is installed
        
        Note: Playwright không cần extensions.
        Method này giữ lại để compatibility.
        
        Args:
            profile_name: Profile name
            extension_id: Extension ID (ignored)
        
        Returns:
            True (always, for compatibility)
        """
        return True
    
    def install_extension_from_directory(self, profile_name: str, extension_dir: Optional[str] = None) -> Tuple[bool, str]:
        """
        Install extension from directory
        
        Note: Playwright không cần extensions.
        Method này giữ lại để compatibility.
        
        Args:
            profile_name: Profile name
            extension_dir: Extension directory (ignored)
        
        Returns:
            (True, "Not needed for Playwright")
        """
        print(f"ℹ️ [INSTALL-EXTENSION] Playwright không cần extension installation")
        return True, "Not needed for Playwright"

    
    # ============================================================
    # USER AGENT & HARDWARE
    # ============================================================
    
    def _generate_user_agent(self, profile_type: str, browser_version: Optional[str] = None) -> str:
        """Generate user agent string"""
        return generate_user_agent(self, profile_type, browser_version)
    
    def _generate_random_mac(self) -> str:
        """Generate random MAC address"""
        return generate_random_mac()
    
    # ============================================================
    # STEALTH CONFIG MANAGEMENT
    # ============================================================
    
    def get_stealth_configs_list(self) -> List[str]:
        """Get list of saved stealth configurations"""
        return get_stealth_configs_list(self)
    
    def load_stealth_config(self, config_name: str) -> Tuple[bool, Any]:
        """Load stealth configuration"""
        return load_stealth_config(self, config_name)
    
    def save_stealth_config(self, config_name: str, config_data: Dict) -> Tuple[bool, str]:
        """Save stealth configuration"""
        return save_stealth_config(self, config_name, config_data)
    
    def delete_stealth_config(self, config_name: str) -> Tuple[bool, str]:
        """Delete stealth configuration"""
        return delete_stealth_config(self, config_name)
    
    # ============================================================
    # EXTENSION MANAGEMENT (DELEGATED TO TILES)
    # ============================================================
    
    def install_extension_from_crx(self, profile_name: str, crx_path: str) -> Tuple[bool, str]:
        """Install extension from CRX file"""
        return install_extension_from_crx(self, profile_name, crx_path)
    
    def install_extension_for_all_profiles(self, extension_id: str = "", extension_name: Optional[str] = None) -> Tuple[int, List]:
        """Install extension for all profiles"""
        return install_extension_for_all_profiles(self, extension_id, extension_name)
    
    def install_extension_for_new_profiles(self, extension_id: str = "", extension_name: Optional[str] = None) -> Tuple[int, List]:
        """Install extension for new profiles"""
        return install_extension_for_new_profiles(self, extension_id, extension_name)
    
    # ============================================================
    # CLEANUP & HISTORY
    # ============================================================
    
    def clear_browsing_history(self, profile_names: List[str]) -> Tuple[bool, str]:
        """Clear browsing history for profiles"""
        return clear_browsing_history(self, profile_names)
    
    # ============================================================
    # LIVESTREAM AUTOMATION
    # ============================================================
    
    def run_livestream_profiles(
        self,
        profile_names: List[str],
        start_url: str,
        max_concurrency: int = 6,
        optimized_mode: bool = True,
        ultra_low_memory: bool = False
    ):
        """Run livestream automation for profiles"""
        return run_livestream_profiles(
            self,
            profile_names,
            start_url,
            max_concurrency,
            optimized_mode,
            ultra_low_memory
        )
    
    def run_livestream_advanced(
        self,
        profile_names: List[str],
        start_url: str,
        auto_out_minutes: int,
        replace_delay_seconds: int,
        max_viewers: int,
        hidden: bool,
        launch_delay: int,
        check_interval: int,
        max_retries: int,
        memory_optimization: bool,
        auto_cleanup: bool,
        show_stats: bool
    ):
        """Run advanced livestream automation"""
        return run_livestream_advanced(
            self,
            profile_names,
            start_url,
            auto_out_minutes,
            replace_delay_seconds,
            max_viewers,
            hidden,
            launch_delay,
            check_interval,
            max_retries,
            memory_optimization,
            auto_cleanup,
            show_stats
        )

    # ============================================================
    # OTP AUTO-FILL (PLAYWRIGHT VERSION)
    # ============================================================
    

    
    async def _input_verification_code(self, page, verification_code: str, username_has_warning_icon: bool = False, otp_tab_count: int = 17) -> bool:
        """
        Điền mã OTP - Sử dụng Playwright keyboard để Tab và điền code
        
        Args:
            page: Playwright page object
            verification_code: Mã OTP 6 số
            username_has_warning_icon: True nếu username có icon cảnh báo (cần Tab nhiều hơn)
            otp_tab_count: Số lần Tab để đến input OTP (default: 17)
        """
        try:
            print(f"[DEBUG] [OTP-AUTO] Đang điền mã OTP: {verification_code}")
            
            import time
            
            # Đợi 3 giây cho dialog xuất hiện
            print(f"[DEBUG] [OTP-AUTO] Đợi 3s cho dialog xuất hiện...")
            time.sleep(3)
            
            print(f"[DEBUG] [OTP-AUTO] Bắt đầu Tab {otp_tab_count} lần để đến input OTP...")
            print(f"[DEBUG] [OTP-AUTO] username_has_warning_icon = {username_has_warning_icon}")
            
            # Tab N lần bằng pyautogui (system-level keyboard)
            try:
                import pyautogui as pg
                pg.FAILSAFE = False
                
                # Tab N lần (default 17, có thể thay đổi tùy theo username_has_warning_icon)
                for i in range(otp_tab_count):
                    pg.press('tab')
                    time.sleep(0.1)  # 100ms giữa các Tab
                    print(f"[DEBUG] [OTP-AUTO] Tab {i+1}/17")
                
                print(f"[DEBUG] [OTP-AUTO] Đã Tab 17 lần, đợi 500ms...")
                time.sleep(0.5)
                
                print(f"[DEBUG] [OTP-AUTO] Bắt đầu điền code từng ký tự...")
                
                # Điền từng ký tự
                for i, char in enumerate(verification_code):
                    pg.press(char)
                    delay = 0.15 + (0.05 if i % 2 == 0 else 0)  # 150-200ms random
                    time.sleep(delay)
                    print(f"[DEBUG] [OTP-AUTO] Đã điền ký tự {i+1}/{len(verification_code)}: {char}")
                
                print(f"[DEBUG] [OTP-AUTO] Đã điền xong code: {verification_code}")
                
                # Đợi 3 giây như yêu cầu
                print(f"[DEBUG] [OTP-AUTO] Đợi 3s...")
                time.sleep(3)
                
                # Tab 1 lần
                print(f"[DEBUG] [OTP-AUTO] Nhấn Tab 1 lần...")
                pg.press('tab')
                time.sleep(0.5)
                
                # Thử tìm và click button submit trước
                print(f"[DEBUG] [OTP-AUTO] Thử tìm button submit...")
                try:
                    # Tìm button submit bằng JavaScript
                    submit_clicked = await page.evaluate("""
                        () => {
                            // Tìm button submit
                            const buttons = document.querySelectorAll('button, input[type="submit"]');
                            for (const btn of buttons) {
                                const text = (btn.textContent || btn.value || '').toLowerCase();
                                if (text.includes('submit') || text.includes('verify') || 
                                    text.includes('confirm') || text.includes('xác nhận') ||
                                    text.includes('tiếp tục') || text.includes('continue')) {
                                    btn.click();
                                    console.log('[OTP-AUTO-JS] Đã click button:', text);
                                    return true;
                                }
                            }
                            return false;
                        }
                    """)
                    
                    if submit_clicked:
                        print(f"[SUCCESS] [OTP-AUTO] Đã click button submit")
                        return True
                    else:
                        print(f"[DEBUG] [OTP-AUTO] Không tìm thấy button submit, thử nhấn Enter...")
                except Exception as e:
                    print(f"[DEBUG] [OTP-AUTO] Lỗi khi tìm button: {e}")
                
                # Nhấn Enter nhiều lần để đảm bảo
                print(f"[DEBUG] [OTP-AUTO] Nhấn Enter để submit...")
                for attempt in range(3):
                    pg.press('enter')
                    print(f"[DEBUG] [OTP-AUTO] Đã nhấn Enter lần {attempt + 1}/3")
                    time.sleep(0.2)
                
                print(f"[SUCCESS] [OTP-AUTO] Đã submit mã OTP bằng pyautogui")
                
                # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                # KIỂM TRA CAPTCHA SAU KHI NHẬP OTP (POLLING MODE)
                # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                print(f"[OTP-AUTO] Đợi 5s trước khi kiểm tra captcha...")
                time.sleep(5)
                
                try:
                    from core.livestream_captcha_debug import LivestreamCaptchaDebugger
                    
                    debugger = LivestreamCaptchaDebugger("otp_verification")
                    
                    # Polling: Check captcha multiple times over 20 seconds
                    max_checks = 4  # Check 4 times
                    check_interval = 3  # Every 3 seconds
                    has_captcha = False
                    captcha_type = None
                    
                    print(f"[OTP-AUTO] Bắt đầu kiểm tra captcha (polling {max_checks} lần, mỗi {check_interval}s)...")
                    
                    for check_num in range(1, max_checks + 1):
                        print(f"[OTP-AUTO] Kiểm tra captcha lần {check_num}/{max_checks}...")
                        has_captcha, captcha_type = await debugger.detect_captcha(page)
                        
                        if has_captcha:
                            print(f"[OTP-AUTO] ⚠️  Captcha phát hiện tại lần check {check_num}: {captcha_type}")
                            break
                        else:
                            print(f"[OTP-AUTO] Lần {check_num}: Chưa có captcha")
                            if check_num < max_checks:
                                time.sleep(check_interval)
                    
                    if has_captcha:
                        print(f"[OTP-AUTO] ⚠️  Captcha xuất hiện sau khi nhập OTP: {captcha_type}")
                        
                        # Ensure captcha visible
                        await debugger.ensure_captcha_visible(page)
                        
                        # Try auto-solve if solver available
                        try:
                            from core.tiktok_captcha_solver_playwright import TikTokCaptchaSolverPlaywright
                            from core.omocaptcha_client import OMOcaptchaClient
                            import configparser
                            
                            config = configparser.ConfigParser()
                            config.read('config.ini')
                            api_key = config.get('CAPTCHA', 'omocaptcha_api_key', fallback='')
                            
                            if api_key and api_key.strip():
                                print(f"[OTP-AUTO] Attempting auto-solve captcha...")
                                omocaptcha_client = OMOcaptchaClient(api_key=api_key.strip())
                                captcha_solver = TikTokCaptchaSolverPlaywright(omocaptcha_client)
                                
                                solution = await captcha_solver.solve_captcha(page, max_retries=10)
                                
                                if solution:
                                    print(f"[OTP-AUTO] ✅ Captcha auto-solved")
                                else:
                                    print(f"[OTP-AUTO] ⚠️  Captcha auto-solve failed")
                                    print(f"[OTP-AUTO] Waiting for manual solve (180s)...")
                                    resolved = await debugger.wait_for_captcha_resolved(page, timeout=180)
                                    if not resolved:
                                        print(f"[OTP-AUTO] ❌ Captcha not resolved after 180s")
                            else:
                                print(f"[OTP-AUTO] No captcha API key, waiting for manual solve...")
                                resolved = await debugger.wait_for_captcha_resolved(page, timeout=180)
                                if not resolved:
                                    print(f"[OTP-AUTO] ❌ Captcha not resolved after 180s")
                        except Exception as captcha_err:
                            print(f"[OTP-AUTO] ⚠️  Captcha handling error: {captcha_err}")
                            print(f"[OTP-AUTO] Waiting for manual solve...")
                            resolved = await debugger.wait_for_captcha_resolved(page, timeout=180)
                            if not resolved:
                                print(f"[OTP-AUTO] ❌ Captcha not resolved after 180s")
                    else:
                        print(f"[OTP-AUTO] ✅ No captcha after OTP")
                        
                except Exception as e:
                    print(f"[OTP-AUTO] ⚠️  Error checking captcha: {e}")
                
                return True
                
            except ImportError:
                print(f"[WARNING] [OTP-AUTO] pyautogui không có, thử dùng Playwright...")
                
                # Fallback: dùng Playwright evaluate để chạy JavaScript
                js_code = f"""
                    () => {{
                        console.log('[OTP-AUTO-JS] Tìm input OTP...');
                        
                        // Tìm input OTP
                        let input = document.activeElement;
                        if (!input || input.tagName !== 'INPUT') {{
                            input = document.querySelector('input.code-input') || 
                                    document.querySelector('input[type="tel"][maxlength="6"]') ||
                                    document.querySelector('input[placeholder*="code" i]');
                        }}
                        
                        if (!input) {{
                            console.log('[OTP-AUTO-JS] Không tìm thấy input');
                            return 'not_found';
                        }}
                        
                        console.log('[OTP-AUTO-JS] Tìm thấy input, focus và điền code...');
                        input.focus();
                        
                        // Điền code
                        input.value = '{verification_code}';
                        input.dispatchEvent(new Event('input', {{ bubbles: true }}));
                        input.dispatchEvent(new Event('change', {{ bubbles: true }}));
                        
                        console.log('[OTP-AUTO-JS] Đã điền code:', input.value);
                        return 'success';
                    }}
                """
                
                result = page.evaluate(js_code)
                
                if result == 'success':
                    print(f"[SUCCESS] [OTP-AUTO] Đã điền mã OTP bằng JavaScript")
                    
                    # Đợi 1-2 giây
                    import random
                    delay_before_enter = 1.0 + random.random()
                    print(f"[DEBUG] [OTP-AUTO] Đợi {delay_before_enter:.2f}s trước khi nhấn Enter...")
                    time.sleep(delay_before_enter)
                    
                    # Nhấn Enter bằng JavaScript
                    page.evaluate("""
                        () => {
                            const input = document.activeElement;
                            if (input) {
                                const enterEvent = new KeyboardEvent('keydown', {
                                    key: 'Enter',
                                    code: 'Enter',
                                    keyCode: 13,
                                    which: 13,
                                    bubbles: true
                                });
                                input.dispatchEvent(enterEvent);
                            }
                        }
                    """)
                    
                    print(f"[SUCCESS] [OTP-AUTO] Đã submit mã OTP")
                    
                    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                    # KIỂM TRA CAPTCHA SAU KHI NHẬP OTP (POLLING MODE - JavaScript fallback)
                    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                    print(f"[OTP-AUTO] Đợi 5s trước khi kiểm tra captcha...")
                    time.sleep(5)
                    
                    try:
                        from core.livestream_captcha_debug import LivestreamCaptchaDebugger
                        
                        debugger = LivestreamCaptchaDebugger("otp_verification")
                        
                        # Polling: Check captcha multiple times over 20 seconds
                        max_checks = 4  # Check 4 times
                        check_interval = 3  # Every 3 seconds
                        has_captcha = False
                        captcha_type = None
                        
                        print(f"[OTP-AUTO] Bắt đầu kiểm tra captcha (polling {max_checks} lần, mỗi {check_interval}s)...")
                        
                        for check_num in range(1, max_checks + 1):
                            print(f"[OTP-AUTO] Kiểm tra captcha lần {check_num}/{max_checks}...")
                            has_captcha, captcha_type = await debugger.detect_captcha(page)
                            
                            if has_captcha:
                                print(f"[OTP-AUTO] ⚠️  Captcha phát hiện tại lần check {check_num}: {captcha_type}")
                                break
                            else:
                                print(f"[OTP-AUTO] Lần {check_num}: Chưa có captcha")
                                if check_num < max_checks:
                                    time.sleep(check_interval)
                        
                        if has_captcha:
                            print(f"[OTP-AUTO] ⚠️  Captcha xuất hiện sau khi nhập OTP: {captcha_type}")
                            
                            # Ensure captcha visible
                            await debugger.ensure_captcha_visible(page)
                            
                            # Try auto-solve if solver available
                            try:
                                from core.tiktok_captcha_solver_playwright import TikTokCaptchaSolverPlaywright
                                from core.omocaptcha_client import OMOcaptchaClient
                                import configparser
                                
                                config = configparser.ConfigParser()
                                config.read('config.ini')
                                api_key = config.get('CAPTCHA', 'omocaptcha_api_key', fallback='')
                                
                                if api_key and api_key.strip():
                                    print(f"[OTP-AUTO] Attempting auto-solve captcha...")
                                    omocaptcha_client = OMOcaptchaClient(api_key=api_key.strip())
                                    captcha_solver = TikTokCaptchaSolverPlaywright(omocaptcha_client)
                                    
                                    solution = await captcha_solver.solve_captcha(page, max_retries=10)
                                    
                                    if solution:
                                        print(f"[OTP-AUTO] ✅ Captcha auto-solved")
                                    else:
                                        print(f"[OTP-AUTO] ⚠️  Captcha auto-solve failed")
                                        print(f"[OTP-AUTO] Waiting for manual solve (180s)...")
                                        resolved = await debugger.wait_for_captcha_resolved(page, timeout=180)
                                        if not resolved:
                                            print(f"[OTP-AUTO] ❌ Captcha not resolved after 180s")
                                else:
                                    print(f"[OTP-AUTO] No captcha API key, waiting for manual solve...")
                                    resolved = await debugger.wait_for_captcha_resolved(page, timeout=180)
                                    if not resolved:
                                        print(f"[OTP-AUTO] ❌ Captcha not resolved after 180s")
                            except Exception as captcha_err:
                                print(f"[OTP-AUTO] ⚠️  Captcha handling error: {captcha_err}")
                                print(f"[OTP-AUTO] Waiting for manual solve...")
                                resolved = await debugger.wait_for_captcha_resolved(page, timeout=180)
                                if not resolved:
                                    print(f"[OTP-AUTO] ❌ Captcha not resolved after 180s")
                        else:
                            print(f"[OTP-AUTO] ✅ No captcha after OTP")
                            
                    except Exception as e:
                        print(f"[OTP-AUTO] ⚠️  Error checking captcha: {e}")
                    
                    return True
                else:
                    print(f"[ERROR] [OTP-AUTO] Không tìm thấy input OTP")
                    return False
                
        except Exception as e:
            print(f"[ERROR] [OTP-AUTO] Lỗi: {e}")
            import traceback
            traceback.print_exc()
            return False
