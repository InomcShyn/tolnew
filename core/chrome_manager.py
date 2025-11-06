import os
import json
import shutil
import subprocess
import time
import threading
import requests
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager  # Not used, let Selenium Manager handle it
import psutil
import configparser
from datetime import datetime
try:
    from core.tiles.tile_profile_management import create_profile_directory as _tile_create_profile_directory, create_profile_with_extension as _tile_create_profile_with_extension, create_profiles_bulk as _tile_create_profiles_bulk, clone_chrome_profile as _tile_clone_chrome_profile
    from core.tiles.tile_extension_management import install_extension_for_profile as _tile_install_extension_for_profile, install_extension_for_all_profiles as _tile_install_extension_for_all_profiles, install_extension_for_new_profiles as _tile_install_extension_for_new_profiles, bulk_install_extension as _tile_bulk_install_extension, check_extension_installed as _tile_check_extension_installed
    from core.tiles.tile_config_management import load_config as _tile_load_config, create_default_config as _tile_create_default_config, save_config as _tile_save_config
    from core.tiles.tile_logging import append_app_log as _tile_append_app_log, get_chrome_log_path as _tile_get_chrome_log_path, read_chrome_log as _tile_read_chrome_log
    from core.tiles.tile_chrome_binary import resolve_chrome_binary_path as _tile_resolve_chrome_binary_path, gpm_chrome_path_for_version as _tile_gpm_chrome_path_for_version, ensure_cft_chrome_binary as _tile_ensure_cft_chrome_binary, ensure_cft_chromedriver as _tile_ensure_cft_chromedriver, apply_custom_chrome_binary as _tile_apply_custom_chrome_binary
    from core.tiles.tile_proxy_management import set_profile_proxy as _tile_set_profile_proxy
    from core.tiles.tile_session_management import clear_profile_name_cache as _tile_clear_profile_name_cache, clear_existing_proxy_data as _tile_clear_existing_proxy_data
    from core.tiles.tile_automation import launch_chrome_profile as _tile_launch_chrome_profile
    from core.tiles.tile_livestream import run_livestream_profiles as _tile_run_livestream_profiles
    from core.tiles.tile_livestream import run_livestream_advanced as _tile_run_livestream_advanced
    from core.tiles.tile_cleanup import clear_browsing_history as _tile_clear_browsing_history
    from core.tiles.tile_livestream import run_livestream_advanced as _tile_run_livestream_advanced
    from core.tiles.tile_gpm_setting import load_gpm_setting as _tile_load_gpm_setting
    from core.tiles.tile_user_agent import generate_user_agent as _tile_generate_user_agent
    from core.tiles.tile_profile_path import get_profile_path as _tile_get_profile_path
except Exception:
    try:
        from .tiles.tile_profile_management import create_profile_directory as _tile_create_profile_directory, create_profile_with_extension as _tile_create_profile_with_extension, create_profiles_bulk as _tile_create_profiles_bulk, clone_chrome_profile as _tile_clone_chrome_profile
        from .tiles.tile_extension_management import install_extension_for_profile as _tile_install_extension_for_profile, install_extension_for_all_profiles as _tile_install_extension_for_all_profiles, install_extension_for_new_profiles as _tile_install_extension_for_new_profiles, bulk_install_extension as _tile_bulk_install_extension, check_extension_installed as _tile_check_extension_installed
        from .tiles.tile_config_management import load_config as _tile_load_config, create_default_config as _tile_create_default_config, save_config as _tile_save_config
        from .tiles.tile_logging import append_app_log as _tile_append_app_log, get_chrome_log_path as _tile_get_chrome_log_path, read_chrome_log as _tile_read_chrome_log
        from .tiles.tile_chrome_binary import resolve_chrome_binary_path as _tile_resolve_chrome_binary_path, gpm_chrome_path_for_version as _tile_gpm_chrome_path_for_version, ensure_cft_chrome_binary as _tile_ensure_cft_chrome_binary, ensure_cft_chromedriver as _tile_ensure_cft_chromedriver, apply_custom_chrome_binary as _tile_apply_custom_chrome_binary
        from .tiles.tile_proxy_management import set_profile_proxy as _tile_set_profile_proxy
        from .tiles.tile_session_management import clear_profile_name_cache as _tile_clear_profile_name_cache, clear_existing_proxy_data as _tile_clear_existing_proxy_data
        from .tiles.tile_automation import launch_chrome_profile as _tile_launch_chrome_profile
        from .tiles.tile_livestream import run_livestream_profiles as _tile_run_livestream_profiles
        from .tiles.tile_livestream import run_livestream_advanced as _tile_run_livestream_advanced
        from .tiles.tile_cleanup import clear_browsing_history as _tile_clear_browsing_history
        from .tiles.tile_livestream import run_livestream_advanced as _tile_run_livestream_advanced
        from .tiles.tile_gpm_setting import load_gpm_setting as _tile_load_gpm_setting
        from .tiles.tile_user_agent import generate_user_agent as _tile_generate_user_agent
        from .tiles.tile_profile_path import get_profile_path as _tile_get_profile_path
    except Exception:
        import sys as _sys, os as _os
        _core_dir = _os.path.dirname(__file__)
        _project_root = _os.path.abspath(_os.path.join(_core_dir, '..'))
        if _project_root not in _sys.path:
            _sys.path.insert(0, _project_root)
        from core.tiles.tile_profile_management import create_profile_directory as _tile_create_profile_directory, create_profile_with_extension as _tile_create_profile_with_extension, create_profiles_bulk as _tile_create_profiles_bulk, clone_chrome_profile as _tile_clone_chrome_profile
        from core.tiles.tile_extension_management import install_extension_for_profile as _tile_install_extension_for_profile, install_extension_for_all_profiles as _tile_install_extension_for_all_profiles, install_extension_for_new_profiles as _tile_install_extension_for_new_profiles, bulk_install_extension as _tile_bulk_install_extension, check_extension_installed as _tile_check_extension_installed
        from core.tiles.tile_config_management import load_config as _tile_load_config, create_default_config as _tile_create_default_config, save_config as _tile_save_config
        from core.tiles.tile_logging import append_app_log as _tile_append_app_log, get_chrome_log_path as _tile_get_chrome_log_path, read_chrome_log as _tile_read_chrome_log
        from core.tiles.tile_chrome_binary import resolve_chrome_binary_path as _tile_resolve_chrome_binary_path, gpm_chrome_path_for_version as _tile_gpm_chrome_path_for_version, ensure_cft_chrome_binary as _tile_ensure_cft_chrome_binary, ensure_cft_chromedriver as _tile_ensure_cft_chromedriver, apply_custom_chrome_binary as _tile_apply_custom_chrome_binary
        from core.tiles.tile_proxy_management import set_profile_proxy as _tile_set_profile_proxy
        from core.tiles.tile_session_management import clear_profile_name_cache as _tile_clear_profile_name_cache, clear_existing_proxy_data as _tile_clear_existing_proxy_data
        from core.tiles.tile_automation import launch_chrome_profile as _tile_launch_chrome_profile
        from core.tiles.tile_livestream import run_livestream_profiles as _tile_run_livestream_profiles
        from core.tiles.tile_livestream import run_livestream_advanced as _tile_run_livestream_advanced
        from core.tiles.tile_cleanup import clear_browsing_history as _tile_clear_browsing_history
        from core.tiles.tile_livestream import run_livestream_advanced as _tile_run_livestream_advanced
        from core.tiles.tile_gpm_setting import load_gpm_setting as _tile_load_gpm_setting
        from core.tiles.tile_user_agent import generate_user_agent as _tile_generate_user_agent
        from core.tiles.tile_profile_path import get_profile_path as _tile_get_profile_path
# Email verification removed

# Import captcha solver
try:
    from .captcha_solver import TikTokCaptchaSolver
    CAPTCHA_SOLVER_AVAILABLE = True
except ImportError:
    try:
        from captcha_solver import TikTokCaptchaSolver
        CAPTCHA_SOLVER_AVAILABLE = True
    except ImportError:
        CAPTCHA_SOLVER_AVAILABLE = False
        print("[CAPTCHA] Captcha solver not available")

# Import native OMOcaptcha solver (no WebDriver needed)
try:
    from .native_omocaptcha_solver import NativeOMOcaptchaSolver
    NATIVE_CAPTCHA_SOLVER_AVAILABLE = True
except ImportError:
    try:
        from native_omocaptcha_solver import NativeOMOcaptchaSolver
        NATIVE_CAPTCHA_SOLVER_AVAILABLE = True
    except ImportError:
        NATIVE_CAPTCHA_SOLVER_AVAILABLE = False
        print("[CAPTCHA] Native captcha solver not available")

# Import GPM flags configuration
gpm_config = None
GPM_FLAGS_AVAILABLE = False

def load_gpm_config():
    global gpm_config, GPM_FLAGS_AVAILABLE
    try:
        import json
        config_path = os.path.join(os.getcwd(), 'config', 'gpm_config.json')
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                gpm_config = json.load(f)
            GPM_FLAGS_AVAILABLE = True
            print("[GPM-FLAGS] GPM flags config loaded successfully")
        else:
            print(f"[GPM-FLAGS] GPM config file not found: {config_path}")
    except Exception as e:
        print(f"[GPM-FLAGS] GPM flags config not available: {e}")

# Load GPM config
load_gpm_config()

class ChromeProfileManager:
    def __init__(self):
        self.config_file = "config.ini"
        self.profiles_dir = os.path.join(os.getcwd(), "chrome_profiles")
        self.chrome_data_dir = self._get_chrome_data_dir()
        # Initialize default to avoid AttributeError before loading
        self.gpm_defaults = {}
        # Read config.ini if exists
        try:
            self.config = configparser.ConfigParser()
            if os.path.exists(self.config_file):
                self.config.read(self.config_file, encoding='utf-8')
        except Exception:
            self.config = configparser.ConfigParser()

    def _get_omocaptcha_api_key_from_config(self):
        try:
            if hasattr(self, 'config') and self.config is not None:
                if self.config.has_section('CAPTCHA'):
                    key = (self.config.get('CAPTCHA', 'omocaptcha_api_key', fallback='') or '').strip()
                    if key and key.lower() not in ('your_api_key_here', 'your_omocaptcha_api_key_here'):
                        return key
        except Exception:
            pass
        # Fallback: read config.ini directly
        try:
            cfg = configparser.ConfigParser()
            cfg.read('config.ini', encoding='utf-8')
            key = (cfg.get('CAPTCHA', 'omocaptcha_api_key', fallback='') or '').strip()
            if key and key.lower() not in ('your_api_key_here', 'your_omocaptcha_api_key_here'):
                return key
        except Exception:
            pass
        return ''

    def _get_omocaptcha_extension_id_override(self):
        # Read override from config/env to pin exact extension id
        try:
            if hasattr(self, 'config') and self.config is not None and self.config.has_section('CAPTCHA'):
                ext_id = (self.config.get('CAPTCHA', 'omocaptcha_extension_id', fallback='') or '').strip()
                if ext_id:
                    return ext_id
        except Exception:
            pass
        try:
            ext_id = (os.environ.get('OMO_EXTENSION_ID') or '').strip()
            if ext_id:
                return ext_id
        except Exception:
            pass
        return ''

    def _find_omocaptcha_extension_id(self, profile_path):
        try:
            override = self._get_omocaptcha_extension_id_override()
            if override:
                # If override is provided, prefer it (even if folders not present yet)
                return override
            import json as _json
            # Look in Extensions folders first
            for base in (os.path.join(profile_path, 'Default', 'Extensions'), os.path.join(profile_path, 'Extensions')):
                if os.path.exists(base):
                    for ext_id in os.listdir(base):
                        ext_path = os.path.join(base, ext_id)
                        if not os.path.isdir(ext_path):
                            continue
                        versions = [d for d in os.listdir(ext_path) if os.path.isdir(os.path.join(ext_path, d))]
                        for ver in versions:
                            manifest_path = os.path.join(ext_path, ver, 'manifest.json')
                            if os.path.exists(manifest_path):
                                try:
                                    with open(manifest_path, 'r', encoding='utf-8') as f:
                                        manifest = _json.load(f)
                                    name = str(manifest.get('name', '')).lower()
                                    if 'omo' in name and 'captcha' in name:
                                        return ext_id
                                except Exception:
                                    pass
            # Try Preferences fallback
            for prefs_name in (os.path.join(profile_path, 'Default', 'Preferences'), os.path.join(profile_path, 'Preferences')):
                if os.path.exists(prefs_name):
                    try:
                        with open(prefs_name, 'r', encoding='utf-8') as f:
                            prefs = _json.load(f)
                        settings = prefs.get('extensions', {}).get('settings', {})
                        for ext_id, data in settings.items():
                            m = data.get('manifest', {})
                            name = str(m.get('name', '')).lower()
                            if 'omo' in name and 'captcha' in name:
                                return ext_id
                    except Exception:
                        pass
        except Exception:
            pass
        return None

    def _inject_omocaptcha_key_via_driver(self, driver, profile_path, ext_id=None):
        try:
            api_key = self._get_omocaptcha_api_key_from_config()
            if not api_key:
                return False
            ext_id = ext_id or self._find_omocaptcha_extension_id(profile_path)
            if not ext_id:
                print('[WARNING] [OMO] Extension ID not found; cannot inject key via CDP')
                return False
            # Try common entry pages of the extension
            for page in ('index.html','options.html','home.html','settings.html','popup.html'):
                try:
                    url = f"chrome-extension://{ext_id}/{page}"
                    driver.get(url)
                    time.sleep(1.5)
                    break
                except Exception:
                    continue
            try:
                # Populate both local and sync storage to maximize compatibility
                driver.execute_script(
                    "chrome.storage.local.set({apiKey: arguments[0], api_key: arguments[0], omocaptcha_api_key: arguments[0]});"
                    "chrome.storage.sync && chrome.storage.sync.set({apiKey: arguments[0], api_key: arguments[0], omocaptcha_api_key: arguments[0]});",
                    api_key
                )
                print('[SUCCESS] [OMO] Injected API key into chrome.storage (local/sync) via extension page')
                return True
            except Exception as e:
                try:
                    # Fallback: localStorage
                    driver.execute_script("localStorage.setItem('apiKey', arguments[0]); localStorage.setItem('omocaptcha_api_key', arguments[0]); localStorage.setItem('api_key', arguments[0]);", api_key)
                    print('[SUCCESS] [OMO] Injected API key into localStorage (fallback)')
                    return True
                except Exception as ee:
                    print(f"[ERROR] [OMO] Injection via driver failed: {ee}")
            return False
        except Exception as e:
            print(f"[ERROR] [OMO] Unexpected error injecting key: {e}")
            return False

    # Profile
    def create_profile_directory(self): return _tile_create_profile_directory(self)
    def create_profile_with_extension(self, profile_name, source_profile="Default", auto_install_extension=True): return _tile_create_profile_with_extension(self, profile_name, source_profile, auto_install_extension)
    def create_profiles_bulk(self, base_name, quantity, version, use_random_format, proxy_list, use_random_hardware, use_random_ua=False): return _tile_create_profiles_bulk(self, base_name, quantity, version, use_random_format, proxy_list, use_random_hardware, use_random_ua)
    def clone_chrome_profile(self, profile_name, source_profile="Default", profile_type="work"): return _tile_clone_chrome_profile(self, profile_name, source_profile, profile_type)

    # Extension
    def install_extension(self, extension_id: str, extension_name: str = None, profile_name: str = None):
        """
        Cài đặt extension theo extension_id.
        
        Args:
            extension_id (str): Chrome extension ID (bắt buộc)
            extension_name (str, optional): Tên hiển thị của extension (dùng cho thư mục local)
            profile_name (str, optional): Tên profile để cài đặt
                - Nếu None → cài cho tất cả profiles
                - Nếu có giá trị → chỉ cài cho profile đó
        
        Returns:
            - Nếu profile_name=None: tuple (success_count: int, results: list)
            - Nếu có profile_name: tuple (success: bool, message: str)
        
        Examples:
            # Cài cho tất cả profiles
            manager.install_extension("pfnededegaaopdmhkdmcofjmoldfiped", "SwitchyOmega")
            
            # Cài cho một profile cụ thể
            manager.install_extension("abc123...", "MyExtension", profile_name="P-123-456")
        """
        if not extension_id or not extension_id.strip():
            if profile_name:
                return False, "extension_id is required"
            else:
                return 0, ["[ERROR] extension_id is required"]
        
        if profile_name:
            # Cài cho một profile cụ thể
            return _tile_install_extension_for_profile(self, profile_name, extension_id, extension_name)
        else:
            # Cài cho tất cả profiles
            return _tile_install_extension_for_all_profiles(self, extension_id, extension_name)
    
    def install_extension_for_profile(self, profile_name, extension_id="pfnededegaaopdmhkdmcofjmoldfiped", extension_name=None): 
        return _tile_install_extension_for_profile(self, profile_name, extension_id, extension_name)
    
    def install_extension_for_all_profiles(self, extension_id="pfnededegaaopdmhkdmcofjmoldfiped", extension_name=None): 
        return _tile_install_extension_for_all_profiles(self, extension_id, extension_name)
    
    def install_extension_for_new_profiles(self, extension_id="pfnededegaaopdmhkdmcofjmoldfiped", extension_name=None): 
        return _tile_install_extension_for_new_profiles(self, extension_id, extension_name)
    
    def bulk_install_extension(self, profile_list=None, extension_id="pfnededegaaopdmhkdmcofjmoldfiped", extension_name=None): 
        return _tile_bulk_install_extension(self, profile_list, extension_id, extension_name)
    
    def check_extension_installed(self, profile_name, extension_id="pfnededegaaopdmhkdmcofjmoldfiped"): 
        return _tile_check_extension_installed(self, profile_name, extension_id)

    # Config
    def load_config(self): return _tile_load_config(self)
    def create_default_config(self): return _tile_create_default_config(self)
    def save_config(self): return _tile_save_config(self)

    # Logging
    def _append_app_log(self, profile_path, message): return _tile_append_app_log(self, profile_path, message)
    def get_chrome_log_path(self, profile_name): return _tile_get_chrome_log_path(self, profile_name)
    def read_chrome_log(self, profile_name, tail_lines=200): return _tile_read_chrome_log(self, profile_name, tail_lines)

    # Chrome binary
    def _resolve_chrome_binary_path(self, desired_version=''): return _tile_resolve_chrome_binary_path(self, desired_version)
    def _gpm_chrome_path_for_version(self, version): return _tile_gpm_chrome_path_for_version(version)
    def _ensure_cft_chrome_binary(self, desired_version): return _tile_ensure_cft_chrome_binary(desired_version)
    def _ensure_cft_chromedriver(self, desired_version): return _tile_ensure_cft_chromedriver(desired_version)
    def _apply_custom_chrome_binary(self, chrome_options, profile_path, desired_version=''): return _tile_apply_custom_chrome_binary(self, chrome_options, profile_path, desired_version)

    # Proxy
    def _set_profile_proxy(self, profile_name, proxy_string): return _tile_set_profile_proxy(self, profile_name, proxy_string)

    # Session/cookie
    def _clear_profile_name_cache(self, profile_path): return _tile_clear_profile_name_cache(self, profile_path)
    def _clear_existing_proxy_data(self, driver): return _tile_clear_existing_proxy_data(self, driver)

    # Automation
    def run_livestream_profiles(self, profile_names, start_url, max_concurrency=6, optimized_mode=True, ultra_low_memory=False):
        return _tile_run_livestream_profiles(self, profile_names, start_url, max_concurrency, optimized_mode, ultra_low_memory)    

    # Advanced livestream (backend for UI advanced tab)
    def run_livestream_advanced(self, profile_names, start_url,
                                auto_out_minutes, replace_delay_seconds, max_viewers, hidden,
                                launch_delay, check_interval, max_retries,
                                memory_optimization, auto_cleanup, show_stats):
        return _tile_run_livestream_advanced(
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
            show_stats,
        )

    # Cleanup: clear browsing history only (keep passwords/cache)
    def clear_browsing_history(self, profile_names):
        return _tile_clear_browsing_history(self, profile_names)

    def run_livestream_advanced(self, profile_names, start_url,
                                auto_out_minutes, replace_delay_seconds, max_viewers, hidden,
                                launch_delay, check_interval, max_retries,
                                memory_optimization, auto_cleanup, show_stats):
        return _tile_run_livestream_advanced(
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
            show_stats,
        )
    def _load_gpm_setting(self): return _tile_load_gpm_setting(self)
    def _generate_user_agent(self, profile_type, browser_version=None): return _tile_generate_user_agent(self, profile_type, browser_version)
    def get_profile_path(self, profile_name): return _tile_get_profile_path(self, profile_name)
    # === Stealth feature stubs (disabled) ===
    # Some UI screens reference stealth config helpers. To avoid runtime errors
    # and effectively disable stealth, provide safe no-op implementations.
    def get_stealth_configs_list(self):
        """Return empty list to indicate no stealth configs available."""
        return []

    def load_stealth_config(self, profile_name):
        """No-op loader for stealth; returns (False, {})."""
        return False, {}

    def save_stealth_config(self, name, config):
        """No-op saver for stealth; indicates feature is disabled."""
        return False, "Stealth feature disabled"

    def _get_chrome_data_dir(self):
        """Get Chrome data directory path - Use separate directory to avoid conflicts"""
        if os.name == 'nt':  # Windows
            # Use separate directory in tool folder to avoid conflicts with personal Chrome
            tool_chrome_dir = os.path.join(os.getcwd(), "chrome_data")
            print(f"[CHROME-DIR] Using isolated Chrome data dir: {tool_chrome_dir}")
            return tool_chrome_dir
        else:  # Linux/Mac
            tool_chrome_dir = os.path.join(os.getcwd(), "chrome_data")
            print(f"[CHROME-DIR] Using isolated Chrome data dir: {tool_chrome_dir}")
            return tool_chrome_dir

    def _build_user_agent_metadata(self, user_agent: str) -> dict:
        """Sinh userAgentMetadata (UA-CH) tương thích with UA đầu ando.
        Website hiện đại dựa ando UA-CH nên cần đồng bộ major version and fullVersion.
        """
        try:
            import re
            # Mặc định for Windows desktop
            platform = "Windows"
            platform_version = "10.0.0"
            bitness = "64"
            mobile = False
            architecture = "x86"
            model = ""

            # Parse major and full version from UA "Chrome/x.y.z.w"
            m = re.search(r"Chrome/(\d+)(?:\.(\d+)\.(\d+)\.(\d+))?", user_agent)
            major = m.group(1) if m else "120"
            full = None
            if m and m.group(2):
                full = f"{m.group(1)}.{m.group(2)}.{m.group(3)}.{m.group(4)}"
            else:
                # Nếu UA không have đủ 4 phần, chuẩn hóa về major.0.0.0
                full = f"{major}.0.0.0"

            # Brands tiêu chuẩn (tránh brand lạ)
            brands = [
                {"brand": "Chromium", "version": major},
                {"brand": "Google Chrome", "version": major},
                {"brand": "Not.A/Brand", "version": "99"},
            ]
            full_list = [
                {"brand": "Chromium", "version": full},
                {"brand": "Google Chrome", "version": full},
                {"brand": "Not.A/Brand", "version": "99.0.0.0"},
            ]

            return {
                "brands": brands,
                "fullVersion": full,
                "fullVersionList": full_list,
                "platform": platform,
                "platformVersion": platform_version,
                "architecture": architecture,
                "model": model,
                "mobile": mobile,
                "bitness": bitness,
            }
        except Exception:
            return {}

    def _get_antidetect_chrome_flags(self):
        """Lấy danh sách Chrome flags for antidetect - Chỉ giữ flags cần thiết nhất như GPM Login"""
        # Chỉ giữ lại the flags cần thiết nhất như GPM Login
        return [
            # Chỉ the flags cần thiết nhất
            "--disable-blink-features=AutomationControlled",
            "--no-default-browser-check",
            "--password-store=basic"
        ]

    def _get_antidetect_chrome_preferences(self, profile_type):
        """Lấy Chrome preferences for antidetect"""
        import random
        
        prefs = {
            "profile": {
                "default_content_setting_values": {
                    "notifications": 2,
                    "geolocation": 2,
                    "media_stream": 2
                },
                "content_settings": {
                    "exceptions": {
                        "notifications": {
                            "*": {"setting": 2}
                        }
                    }
                },
                "content_settings": {
                    "pattern_pairs": {
                        "https://*,*": {
                            "notifications": 2,
                            "geolocation": 2,
                            "media_stream": 2
                        }
                    }
                },
                "managed_default_content_settings": {
                    "notifications": 2,
                    "geolocation": 2,
                    "media_stream": 2
                }
            },
            "gcm": {
                "product_category_for_subtypes": "",
                "wake_from_idle": False
            },
            "invalidations": {
                "service_enabled": False
            },
            "webrtc": {
                "ip_handling_policy": "default_public_interface_only",
                "multiple_routes_enabled": False,
                "nonproxied_udp_enabled": False
            },
            "intl": {
                "accept_languages": "en-US,en,vi-VN,vi" if profile_type == "cong_viec" else "en-US,en,en-GB",
                "selected_languages": ["en-US", "vi-VN"] if profile_type == "cong_viec" else ["en-US", "en-GB"]
            },
            "browser": {
                "check_default_browser": False,
                "show_home_button": False
            },
            "safebrowsing": {
                "enabled": False,
                "scout_reporting_enabled_when_deprecated": False
            },
            "distribution": {
                "skip_first_run_ui": True,
                "import_bookmarks": False,
                "import_history": False,
                "import_search_engine": False
            },
            "first_run_tabs": [],
            "homepage": "",
            "homepage_is_newtabpage": True,
            "session": {
                "restore_on_startup": 1,
                "startup_urls": []
            },
            "default_search_provider_data": {
                "template_url_data": []
            },
            "profile": {
                "password_manager_enabled": False,
                "safebrowsing": {
                    "enabled": False
                }
            }
        }
        
        return prefs

    def _apply_stealth_evasion(self, driver, profile_path):
        """Áp dụng stealth evasion to tránh detect automation"""
        try:
            # Đọc antidetect settings
            settings_path = os.path.join(profile_path, 'profile_settings.json')
            if not os.path.exists(settings_path):
                return
            
            import json
            with open(settings_path, 'r', encoding='utf-8') as f:
                settings = json.load(f)
            
            antidetect = settings.get('antidetect', {})
            if not antidetect.get('enabled', False):
                return
            
            # CDP script to ẩn webdriver and spoof the thuộc tính - Cải thiện to tránh unusual traffic
            stealth_script = r"""
            // Ẩn webdriver hoàn toàn
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
            
            // Xóa automation indicators
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
            
            // Spoof plugins with plugins thật
            Object.defineProperty(navigator, 'plugins', {
                get: () => [
                    {name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer'},
                    {name: 'Chrome PDF Viewer', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai'},
                    {name: 'Native Client', filename: 'internal-nacl-plugin'}
                ],
            });
            
            // Spoof languages theo profile type
            const languages = /*#__PURE__*/ (function(){ return \"\"\" + json.dumps(['en-US', 'en']) + \"\"\"; })();
            Object.defineProperty(navigator, 'languages', {
                get: () => languages,
            });
            
            // Spoof chrome object hoàn chỉnh
            window.chrome = {
                runtime: {
                    onConnect: undefined,
                    onMessage: undefined,
                },
                loadTimes: function() {
                    return {
                        requestTime: performance.now(),
                        startLoadTime: performance.now(),
                        commitLoadTime: performance.now(),
                        finishDocumentLoadTime: performance.now(),
                        finishLoadTime: performance.now(),
                        firstPaintTime: performance.now(),
                        firstPaintAfterLoadTime: 0,
                        navigationType: 'navigate'
                    };
                },
                csi: function() {
                    return {
                        pageT: performance.now(),
                        startE: performance.now(),
                        tran: 15
                    };
                },
                app: {
                    isInstalled: false,
                    InstallState: {
                        DISABLED: 'disabled',
                        INSTALLED: 'installed',
                        NOT_INSTALLED: 'not_installed'
                    },
                    RunningState: {
                        CANNOT_RUN: 'cannot_run',
                        READY_TO_RUN: 'ready_to_run',
                        RUNNING: 'running'
                    }
                }
            };
            
            // Fix permissions.query
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
            
            // Mask WebGL
            const getParameter = WebGLRenderingContext.prototype.getParameter;
            WebGLRenderingContext.prototype.getParameter = function(parameter) {
                if (parameter === 37445) {
                    return 'Intel Inc.';
                }
                if (parameter === 37446) {
                    return 'Intel Iris OpenGL Engine';
                }
                return getParameter(parameter);
            };
            
            // Add Canvas noise
            const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
            HTMLCanvasElement.prototype.toDataURL = function() {
                const context = this.getContext('2d');
                const imageData = context.getImageData(0, 0, this.width, this.height);
                for (let i = 0; i < imageData.data.length; i += 4) {
                    imageData.data[i] = imageData.data[i] ^ Math.floor(Math.random() * 255);
                }
                context.putImageData(imageData, 0, 0);
                return originalToDataURL.apply(this, arguments);
            };
            
            // Spoof screen properties
            Object.defineProperty(screen, 'availHeight', {
                get: () => 1040,
            });
            Object.defineProperty(screen, 'availWidth', {
                get: () => 1920,
            });
            Object.defineProperty(screen, 'colorDepth', {
                get: () => 24,
            });
            Object.defineProperty(screen, 'height', {
                get: () => 1080,
            });
            Object.defineProperty(screen, 'width', {
                get: () => 1920,
            });
            
            // Spoof timezone
            const originalDateToString = Date.prototype.toString;
            Date.prototype.toString = function() {
                return originalDateToString.call(this).replace(/GMT[+-]\d{4}/, 'GMT+0700');
            };
            """
            
            # Execute stealth script
            driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': stealth_script
            })
            
            print(f"[SUCCESS] [STEALTH] Done áp dụng stealth evasion for profile")
            
        except Exception as e:
            print(f"[WARNING] [STEALTH] Error áp dụng stealth evasion: {e}")

    def _randomize_profile_fingerprint(self, profile_path: str) -> None:
        """Random hóa the định danh cục bộ in profile to tránh trùng lặp.

        Lưu ý: Chrome không for phép thay đổi MAC thật of hệ thống. Mục tiêu ở đây là:
        - Tạo `Local State` mới with client_id/metrics_client_id khác nhau giữa the profiles
        - Random hóa the seed liên quan đến variations/metrics
        - Điều chỉnh Preferences to hạn chế lộ IP cục bộ qua WebRTC (giảm fingerprint)
        """
        import uuid, base64, os, json

        # Đường dẫn tệp in thư mục user-data-dir of profile tùy chỉnh
        local_state_path = os.path.join(profile_path, "Local State")
        preferences_path = os.path.join(profile_path, "Preferences")

        # 1) Tạo/ghi Local State with client_id and variations seed ngẫu nhiên
        local_state = {}
        try:
            if os.path.exists(local_state_path):
                with open(local_state_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:
                        local_state = json.loads(content)
        except Exception:
            local_state = {}

        # Tạo the giá trị ngẫu nhiên
        new_client_id = str(uuid.uuid4())
        new_variations_seed = base64.b64encode(os.urandom(16)).decode('ascii')

        # user_experience_metrics.client_id
        uxm = local_state.get("user_experience_metrics", {})
        uxm["client_id"] = new_client_id
        local_state["user_experience_metrics"] = uxm

        # metrics.reporting_enabled have thể to nguyên, chỉ đổi id
        metrics = local_state.get("metrics", {})
        metrics["client_id"] = new_client_id
        local_state["metrics"] = metrics

        # variations seed
        variations = local_state.get("variations", {})
        variations["seed"] = new_variations_seed
        variations.pop("seed_signature", None)  # bỏ signature cũ if have
        local_state["variations"] = variations

        # Ghi Local State
        with open(local_state_path, 'w', encoding='utf-8') as f:
            json.dump(local_state, f, ensure_ascii=False, indent=2)

        # 2) Chỉnh Preferences to hạn chế WebRTC lộ IP cục bộ
        prefs = {}
        try:
            if os.path.exists(preferences_path):
                with open(preferences_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:
                        prefs = json.loads(content)
        except Exception:
            prefs = {}

        webrtc = prefs.get("webrtc", {})
        # Chính sách: chỉ dùng public interface, tắt many route, tắt UDP ngoài proxy
        webrtc["ip_handling_policy"] = "default_public_interface_only"
        webrtc["multiple_routes"] = False
        webrtc["non_proxied_udp"] = False
        prefs["webrtc"] = webrtc

        # Đảm bảo profile name không bị trùng lặp/rối (optional)
        profile_block = prefs.get("profile", {})
        # No đổi name ở đây; chỉ đảm bảo have khóa
        prefs["profile"] = profile_block

        with open(preferences_path, 'w', encoding='utf-8') as f:
            json.dump(prefs, f, ensure_ascii=False, indent=2)
    
    def _create_default_profile(self):
        """Tạo profile Default hoàn toàn mới - No clone from Chrome cá nhân"""
        try:
            print(f"[TOOL] [CREATE-DEFAULT] Đang create profile Default hoàn toàn mới...")
            
            # Tạo thư mục Chrome data if chưa tồn tại
            if not os.path.exists(self.chrome_data_dir):
                os.makedirs(self.chrome_data_dir)
                print(f"📁 [CREATE-DEFAULT] Done create thư mục: {self.chrome_data_dir}")
            
            # Đường dẫn profile Default
            default_profile_path = os.path.join(self.chrome_data_dir, "Default")
            
            # Tạo thư mục Default if chưa tồn tại
            if not os.path.exists(default_profile_path):
                os.makedirs(default_profile_path)
                print(f"📁 [CREATE-DEFAULT] Done create thư mục: {default_profile_path}")
            
            # Tạo file Preferences cơ bản with anti-detection
            preferences_path = os.path.join(default_profile_path, "Preferences")
            if not os.path.exists(preferences_path):
                basic_preferences = {
                    "profile": {
                        "name": "Default",
                        "avatar_icon": "chrome://theme/IDR_PROFILE_AVATAR_0"
                    },
                    "browser": {
                        "show_home_button": False
                    },
                    "bookmark_bar": {
                        "show_on_all_tabs": False
                    },
                    # Anti-detection preferences
                    "google": {},
                    "signin": {"allowed": False},
                    "gcm": {
                        "product_category_for_subtypes": "",
                        "wake_from_idle": False
                    },
                    "safebrowsing": {
                        "enabled": False,
                        "scout_reporting_enabled_when_deprecated": False
                    },
                    "intl": {
                        "accept_languages": "en-US,en;q=0.9"
                    },
                    "notifications": {
                        "default_content_setting": 2
                    }
                }
                
                with open(preferences_path, 'w', encoding='utf-8') as f:
                    json.dump(basic_preferences, f, indent=2)
                print(f"📄 [CREATE-DEFAULT] Done create file Preferences")
            
            # Tạo file Local State to hoàn toàn độc lập
            local_state_path = os.path.join(self.chrome_data_dir, "Local State")
            if not os.path.exists(local_state_path):
                import uuid
                local_state = {
                    "profile": {
                        "info_cache": {
                            "Default": {
                                "name": "Default",
                                "user_name": "",
                                "is_using_default_name": True,
                                "is_using_default_avatar": True,
                                "avatar_icon": "chrome://theme/IDR_PROFILE_AVATAR_0"
                            }
                        }
                    },
                    "browser": {
                        "enabled_labs_experiments": []
                    },
                    "google": {},
                    "gcm": {
                        "product_category_for_subtypes": "",
                        "wake_from_idle": False
                    }
                }
                
                with open(local_state_path, 'w', encoding='utf-8') as f:
                    json.dump(local_state, f, indent=2)
                print(f"📄 [CREATE-DEFAULT] Done create file Local State")
            
            # Tạo thư mục Default/Extensions
            extensions_dir = os.path.join(default_profile_path, "Extensions")
            if not os.path.exists(extensions_dir):
                os.makedirs(extensions_dir)
                print(f"📁 [CREATE-DEFAULT] Done create thư mục Extensions")
            
            print(f"[SUCCESS] [CREATE-DEFAULT] Profile Default done get create thành công")
            return True
            
        except Exception as e:
            print(f"[ERROR] [CREATE-DEFAULT] Error when create profile Default: {str(e)}")
            return False
    
    def _create_fresh_template(self, template_name):
        """Tạo fresh template mới with randomization to tránh spam detection"""
        try:
            print(f"[TOOL] [FRESH-TEMPLATE] Đang create fresh template: {template_name}")
            
            # Tạo thư mục Chrome data if chưa tồn tại
            if not os.path.exists(self.chrome_data_dir):
                os.makedirs(self.chrome_data_dir)
            
            # Đường dẫn template
            template_path = os.path.join(self.chrome_data_dir, template_name)
            
            # Tạo thư mục template
            if not os.path.exists(template_path):
                os.makedirs(template_path)
                print(f"📁 [FRESH-TEMPLATE] Done create thư mục: {template_path}")
            
            # Tạo Preferences with randomization
            preferences_path = os.path.join(template_path, "Preferences")
            import random
            import uuid
            
            # Randomize the giá trị to tránh pattern detection
            random_values = {
                "profile_id": str(uuid.uuid4()),
                "avatar_icon": f"chrome://theme/IDR_PROFILE_AVATAR_{random.randint(0, 26)}",
                "hardware_concurrency": random.choice([2, 4, 6, 8, 10, 12]),
                "device_memory": random.choice([4, 8, 12, 16, 24, 32]),
                "webgl_vendor": random.choice(['Google Inc.', 'NVIDIA Corporation', 'AMD', 'Intel Inc.', 'Microsoft Corporation']),
                "webgl_renderer": random.choice([
                    # NVIDIA Graphics
                    'ANGLE (NVIDIA, NVIDIA GeForce RTX 3080 Ti Direct3D11 vs_5_0 ps_5_0, D3D11)',
                    'ANGLE (NVIDIA, NVIDIA GeForce GTX 1060 Direct3D11 vs_5_0 ps_5_0, D3D11)',
                    'ANGLE (NVIDIA, NVIDIA GeForce RTX 3060 Direct3D11 vs_5_0 ps_5_0, D3D11)',
                    # Intel Graphics - UHD Series
                    'ANGLE (Intel, Intel(R) UHD Graphics 620 (0x00005917) Direct3D11 vs_5_0 ps_5_0, D3D11)',
                    'ANGLE (Intel, Intel(R) UHD Graphics 630 (0x00005917) Direct3D11 vs_5_0 ps_5_0, D3D11)',
                    'ANGLE (Intel, Intel(R) UHD Graphics 620 Direct3D11 vs_5_0 ps_5_0, D3D11)',
                    'ANGLE (Intel, Intel(R) UHD Graphics 630 Direct3D11 vs_5_0 ps_5_0, D3D11)',
                    # Intel Graphics - HD Series
                    'ANGLE (Intel, Intel(R) HD Graphics 530 Direct3D11 vs_5_0 ps_5_0, D3D11)',
                    'ANGLE (Intel, Intel(R) HD Graphics 520 Direct3D11 vs_5_0 ps_5_0, D3D11)',
                    'ANGLE (Intel, Intel(R) HD Graphics 4600 Direct3D11 vs_5_0 ps_5_0, D3D11)',
                    'ANGLE (Intel, Intel(R) HD Graphics 4000 Direct3D9Ex vs_3_0 ps_3_0, igdumdim64.dll-10.18.10.3345)',
                    # Intel Graphics - Iris Series
                    'ANGLE (Intel, Intel(R) Iris(R) Xe Graphics Direct3D11 vs_5_0 ps_5_0, D3D11)',
                    'ANGLE (Intel, Intel(R) HD Graphics Family Direct3D11 vs_5_0 ps_5_0, D3D11)',
                    # AMD Graphics
                    'ANGLE (AMD, AMD Radeon RX 580 Direct3D11 vs_5_0 ps_5_0, D3D11)',
                    'ANGLE (AMD, AMD Radeon RX 6600 Direct3D11 vs_5_0 ps_5_0, D3D11)'
                ]),
                "timezone": random.choice([
                    'America/New_York', 'America/Los_Angeles', 'America/Chicago', 'America/Denver',
                    'Europe/London', 'Europe/Paris', 'Europe/Berlin', 'Europe/Rome',
                    'Asia/Tokyo', 'Asia/Shanghai', 'Asia/Seoul', 'Asia/Singapore'
                ]),
                "language": random.choice([
                    'en-US', 'en-GB', 'en-CA', 'en-AU', 'de-DE', 'fr-FR', 'es-ES', 'it-IT'
                ])
            }
            
            fresh_preferences = {
                "profile": {
                    "name": template_name,
                    "avatar_icon": random_values["avatar_icon"]
                },
                "browser": {
                    "show_home_button": False
                },
                "bookmark_bar": {
                    "show_on_all_tabs": False
                },
                # Anti-detection preferences with randomization
                "google": {},
                "signin": {"allowed": False},
                "gcm": {
                    "product_category_for_subtypes": "",
                    "wake_from_idle": False
                },
                "safebrowsing": {
                    "enabled": False,
                    "scout_reporting_enabled_when_deprecated": False
                },
                "intl": {
                    "accept_languages": f"{random_values['language']},en;q=0.9"
                },
                "notifications": {
                    "default_content_setting": 2
                },
                # Thêm randomization for hardware
                "hardware_acceleration": {
                    "enabled": random.choice([True, False])
                }
            }
            
            with open(preferences_path, 'w', encoding='utf-8') as f:
                json.dump(fresh_preferences, f, indent=2)
            print(f"📄 [FRESH-TEMPLATE] Done create file Preferences with randomization")
            
            # Tạo Local State with randomization
            local_state_path = os.path.join(self.chrome_data_dir, "Local State")
            if not os.path.exists(local_state_path):
                local_state = {
                    "profile": {
                        "info_cache": {
                            template_name: {
                                "name": template_name,
                                "user_name": "",
                                "is_using_default_name": True,
                                "is_using_default_avatar": True,
                                "avatar_icon": random_values["avatar_icon"]
                            }
                        }
                    },
                    "browser": {
                        "enabled_labs_experiments": []
                    },
                    "google": {},
                    "gcm": {
                        "product_category_for_subtypes": "",
                        "wake_from_idle": False
                    }
                }
                
                with open(local_state_path, 'w', encoding='utf-8') as f:
                    json.dump(local_state, f, indent=2)
                print(f"📄 [FRESH-TEMPLATE] Done create file Local State")
            
            # Tạo thư mục Extensions
            extensions_dir = os.path.join(template_path, "Extensions")
            if not os.path.exists(extensions_dir):
                os.makedirs(extensions_dir)
            
            print(f"[SUCCESS] [FRESH-TEMPLATE] Done create fresh template thành công: {template_name}")
            return True
            
        except Exception as e:
            print(f"[ERROR] [FRESH-TEMPLATE] Error create fresh template: {e}")
            return False

    def bypass_chrome_security_warnings(self, profile_name):
        """
        Bypass Chrome security warnings and configure for Web Store access
        """
        try:
            print(f"[ENABLED] [SECURITY-BYPASS] Bypassing security warnings for {profile_name}")
            
            profile_path = os.path.join(self.profiles_dir, profile_name)
            if not os.path.exists(profile_path):
                return False, f"Profile {profile_name} not found"
            
            # Create security bypass preferences
            preferences_path = os.path.join(profile_path, "Default", "Preferences")
            
            # Load existing preferences or create new
            if os.path.exists(preferences_path):
                try:
                    with open(preferences_path, 'r', encoding='utf-8') as f:
                        preferences = json.load(f)
                except:
                    preferences = {}
            else:
                preferences = {}
            
            # Security bypass settings
            if "profile" not in preferences:
                preferences["profile"] = {}
            
            if "content_settings" not in preferences["profile"]:
                preferences["profile"]["content_settings"] = {}
            
            if "exceptions" not in preferences["profile"]["content_settings"]:
                preferences["profile"]["content_settings"]["exceptions"] = {}
            
            # Disable security warnings
            security_exceptions = {
                "chrome.google.com": {"setting": 1},
                "*.google.com": {"setting": 1},
                "*.googleapis.com": {"setting": 1},
                "*.gstatic.com": {"setting": 1}
            }
            
            preferences["profile"]["content_settings"]["exceptions"]["mixed_content"] = security_exceptions
            preferences["profile"]["content_settings"]["exceptions"]["insecure_content"] = security_exceptions
            
            # Disable safe browsing
            preferences["safebrowsing"] = {
                "enabled": False,
                "enhanced": False,
                "reporting_enabled": False
            }
            
            # Disable security warnings
            preferences["security_state"] = {
                "show_secure_connection_icon": False,
                "show_dangerous_connection_icon": False
            }
            
            # Save preferences
            with open(preferences_path, 'w', encoding='utf-8') as f:
                json.dump(preferences, f, indent=2)
            
            print(f"[SUCCESS] [SECURITY-BYPASS] Security warnings bypassed for {profile_name}")
            return True, "Security warnings bypassed successfully"
            
        except Exception as e:
            print(f"[ERROR] [SECURITY-BYPASS] Failed to bypass security warnings: {str(e)}")
            return False, str(e)
        
    def _random_user_agent(self) -> str:
        """Sinh User-Agent ngẫu nhiên nhưng hợp lý for Windows 10 x64, Chrome stable.
        Nguồn UA dựa trên the phiên bản Chrome phổ biến, xoay vòng minor to đa dạng hóa.
        """
        import random as _rand
        # Các dải version Chrome phổ biến gần đây (optimize for anti-bot, không quá cũ)
        major_versions = [131, 132, 133, 134, 135, 136, 137, 138, 139]
        major = _rand.forice(major_versions)
        minor = _rand.randint(0, 0)
        build = _rand.randint(8000, 9999)
        patch = _rand.randint(50, 199)
        chrome_ver = f"{major}.{minor}.{build}.{patch}"
        # WebKit giữ ổn định to phù hợp Chrome
        webkit = "537.36"
        # Một số biến thể Platform
        platforms = [
            "Windows NT 10.0; Win64; x64",
            "Windows NT 10.0; Win64; x64; rv:109.0",
        ]
        platform = _rand.forice(platforms)
        # Một ít biến thể trình duyệt Chrome/Edg dựa trên Chromium
        if _rand.random() < 0.15:
            # Edge Chromium (giúp phân phối dấu vết tự nhiên hơn)
            edg_major = major
            edg_build = _rand.randint(100, 999)
            edg_patch = _rand.randint(10, 199)
            return (
                f"Mozilla/5.0 ({platform}) AppleWebKit/{webkit} (KHTML, like Gecko) "
                f"Chrome/{chrome_ver} Safari/{webkit} Edg/{edg_major}.0.{edg_build}.{edg_patch}"
            )
        # Chrome chuẩn
        return (
            f"Mozilla/5.0 ({platform}) AppleWebKit/{webkit} (KHTML, like Gecko) "
            f"Chrome/{chrome_ver} Safari/{webkit}"
        )

    def _user_agent_pool(self) -> list:
        """Trả về 4-5 UA chất lượng cao to xoay vòng ổn định (Windows 10 x64)."""
        return [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
            # Edge Chromium biến thể nhẹ (tăng đa dạng)
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.1025.67",
        ]
        
    def _optimize_profile_for_low_data(self, profile_path):
        """Tối ưu hóa profile to giảm thiểu dữ liệu"""
        try:
            # Xóa the thư mục không cần thiết
            folders_to_remove = [
                "Cache", "Code Cache", "GPUCache", "ShaderCache",
                "Network Action Predictor", "TransportSecurity",
                "Local State", "Crashpad", "Crash Reports"
            ]
            
            for folder in folders_to_remove:
                folder_path = os.path.join(profile_path, folder)
                if os.path.exists(folder_path):
                    try:
                        shutil.rmtree(folder_path)
                    except:
                        pass
            
            # Xóa the file không cần thiết cả ở root and in Default/
            files_to_remove = [
                # root-level
                "Local State", "Preferences", "Secure Preferences",
                "Web Data", "Login Data", "History", "Top Sites",
                "Favicons", "Shortcuts", "Bookmarks", "Visited Links",
                "Cookies", "Cookies-journal", "AutofillStrikeDatabase",
                # Default-level (đường dẫn sẽ process riêng bên dưới)
            ]
            for file_name in files_to_remove:
                # root
                root_file = os.path.join(profile_path, file_name)
                if os.path.exists(root_file):
                    try:
                        os.remove(root_file)
                    except:
                        pass
                # Default/
                default_file = os.path.join(profile_path, 'Default', file_name)
                if os.path.exists(default_file):
                    try:
                        os.remove(default_file)
                    except:
                        pass

            # Xóa biến thể SQLite (shm/wal) for the DB lịch sử/cookies/autofill
            sqlite_variants = [
                'History', 'Cookies', 'Web Data', 'Login Data', 'AutofillStrikeDatabase',
                'Visited Links', 'Top Sites'
            ]
            for base in sqlite_variants:
                for ext in ("-shm", "-wal"):
                    for prefix in (profile_path, os.path.join(profile_path, 'Default')):
                        p = os.path.join(prefix, base + ext)
                        if os.path.exists(p):
                            try:
                                os.remove(p)
                            except:
                                pass
            
            # Tạo file Preferences optimize
            preferences = {
                "profile": {
                    "content_settings": {
                        "exceptions": {
                            "images": {"*": {"setting": 2}},
                            "javascript": {"*": {"setting": 2}},
                            "plugins": {"*": {"setting": 2}},
                            "popups": {"*": {"setting": 2}},
                            "geolocation": {"*": {"setting": 2}},
                            "notifications": {"*": {"setting": 2}},
                            "media_stream": {"*": {"setting": 2}}
                        }
                    },
                    "default_content_setting_values": {
                        "images": 2,
                        "javascript": 2,
                        "plugins": 2,
                        "popups": 2,
                        "geolocation": 2,
                        "notifications": 2,
                        "media_stream": 2,
                        "automatic_downloads": 2
                    }
                },
                "browser": {
                    "check_default_browser": False,
                    "show_home_button": False,
                    "show_bookmark_bar": False
                },
                "privacy_sandbox": {
                    "ad_measurement_enabled": False,
                    "fledge_enabled": False,
                    "topics_enabled": False
                },
                "translate": {
                    "enabled": False
                },
                "sync": {
                    "suppress_start": True
                }
            }
            
            # KHÔNG ghi Preferences ở root; to Chrome tự create in Default sau when launch
            
        except Exception as e:
            print(f"Error when optimize hóa profile: {str(e)}")
    
    
    def _detect_locale_from_ip(self) -> dict:
        """Phát hiện timezone and languages theo IP công cộng (best-effort)."""
        try:
            import requests as _rq
            # ipapi.co đủ nhanh and đơn giản
            r = _rq.get('https://ipapi.co/json/', timeout=5)
            if r.status_code == 200:
                data = r.json()
                tz = data.get('timezone') or 'UTC'
                country_code = (data.get('country_code') or '').upper()
                # Chọn languages hợp lý theo country
                lang_map = {
                    'VN': ['vi-VN', 'vi'],
                    'US': ['en-US', 'en'],
                    'GB': ['en-GB', 'en'],
                    'DE': ['de-DE', 'de'],
                    'FR': ['fr-FR', 'fr'],
                    'JP': ['ja-JP', 'ja']
                }
                languages = lang_map.get(country_code, ['en-US', 'en'])
                return {'timezone': tz, 'languages': languages, 'country': country_code}
        except Exception:
            pass
        return {'timezone': 'UTC', 'languages': ['en-US', 'en'], 'country': 'US'}
    
    def _apply_default_config(self, chrome_options):
        """Áp dụng cấu hình mặc định from gpm_config.json - Chỉ giữ flags cần thiết nhất như GPM Login"""
        # Sử dụng gpm_config.json to optimize hóa command line
        if gpm_config and gpm_config.get('profile_settings', {}).get('software', {}).get('minimal_flags', False):
            print(f"[GPM-CONFIG] Using minimal flags from gpm_config.json")
            
            # Lấy user-agent and language from gpm_config
            software_settings = gpm_config.get('profile_settings', {}).get('software', {})
            user_agent = software_settings.get('user_agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36')
            language = software_settings.get('language', 'vi-VN')
            
            # Chỉ thêm the flags cần thiết nhất from gpm_config
            essential_flags = [
                '--gpm-disable-machine-id',
                '--gpm-use-pref-tracking-config-before-v137',
                '--no-default-browser-check',
                '--password-store=basic',
                f'--user-agent="{user_agent}"',
                f'--lang={language.split("-")[0]}',  # Chỉ lấy 'vi' from 'vi-VN'
                '--load-extension="C:\\GPM-profile\\dx7rwzL1Rf-10102025\\Default\\GPMSoft\\Extensions\\clipboard-ext"',
                '--flag-switches-begin',
                '--flag-switches-end'
            ]
            
            # Thêm essential flags
            for flag in essential_flags:
                chrome_options.add_argument(flag)
                
            print(f"[GPM-CONFIG] Added {len(essential_flags)} essential flags")
            print(f"[GPM-CONFIG] User-Agent: {user_agent}")
            print(f"[GPM-CONFIG] Language: {language}")
        else:
            print(f"[GPM-CONFIG] Using default config - will remove unnecessary flags")
        
        # Log command line to debug
        try:
            args = getattr(chrome_options, '_arguments', []) or []
            cmd_line = ' '.join([str(arg) for arg in args if arg])
            print(f"[DEBUG] Command line length: {len(cmd_line)} characters")
            if len(cmd_line) > 500:  # Nếu command line quá dài
                print(f"[DEBUG] Command line too long: {len(cmd_line)} chars")
                print(f"[DEBUG] First 200 chars: {cmd_line[:200]}...")
            else:
                print(f"[DEBUG] Command line: {cmd_line}")
        except Exception as e:
            print(f"[DEBUG] Could not log command line: {e}")

        # Always enforce password manager OFF at default config layer as well
        try:
            prefs = {
                "credentials_enable_service": False,
                "profile.password_manager_enabled": False,
                "autofill.profile_enabled": False,
                "autofill.credit_card_enabled": False,
                "credentials_enable_autosignin": False
            }
            chrome_options.add_experimental_option("prefs", prefs)
            chrome_options.add_argument("--disable-features=PasswordManagerOnboarding,AutofillServerCommunication,AutofillEnableAccountWalletStorage,AutoSignIn,PasswordImport")
            chrome_options.add_argument("--disable-save-password-bubble")
            print("[PRIVACY] [DEFAULT] Password manager and auto sign-in disabled")
        except Exception as _perr:
            print(f"[WARNING] [DEFAULT] Could not enforce privacy prefs: {_perr}")
    
    def _remove_automation_flags(self, chrome_options):
        """Loại bỏ automation flags to tránh detection"""
        try:
            # Lấy danh sách arguments
            args_attr = None
            if hasattr(chrome_options, 'arguments'):
                args_attr = 'arguments'
            elif hasattr(chrome_options, '_arguments'):
                args_attr = '_arguments'
            
            if args_attr:
                args = list(getattr(chrome_options, args_attr) or [])
                print(f"[FLAG-REMOVAL] Before removal: {len(args)} flags")
                print(f"[FLAG-REMOVAL] Original args: {[str(a) for a in args[:5]]}...")
                # Chỉ giữ lại the flags cần thiết như GPM Login
                essential_flags = [
                    '--user-data-dir=',
                    '--lang=',
                    '--password-store=basic',
                    '--gpm-disable-machine-id',
                    '--user-agent=',
                    '--no-default-browser-check',
                    '--load-extension=',
                    '--gpm-use-pref-tracking-config-before-v137',
                    '--flag-switches-begin',
                    '--flag-switches-end'
                ]
                
                # Loại bỏ all flags không cần thiết
                bad_prefixes = (
                    # Tất cả flags không cần thiết from command line hiện tại
                    '--allow-pre-commit-input',
                    '--disable-background-networking',
                    '--disable-backgrounding-occluded-windows',
                    '--disable-client-side-phishing-detection',
                    '--disable-default-apps',
                    '--disable-hang-monitor',
                    '--disable-popup-blocking',
                    '--disable-prompt-on-repost',
                    '--disable-sync',
                    '--enable-logging',
                    '--log-level=',
                    '--no-first-run',
                    '--no-service-autorun',
                    '--remote-debugging-port=',
                    '--test-type=',
                    '--use-mock-keychain',
                    '--lang=en-US',  # Chỉ giữ --lang=vi
                    # Automation detection flags
                    '--test-type=webdriver', '--enable-automation',
                    '--disable-extensions-except=', '--accept-lang=',
                    '--disable-background-', '--disable-client-side-', '--disable-component-',
                    '--disable-device-', '--disable-dns-', '--disable-domain-',
                    '--disable-ipv6', '--disable-notifications', '--disable-permissions-',
                    '--disable-popup-', '--disable-prompt-', '--disable-quic',
                    '--disable-renderer-', '--disable-sync', '--disable-usb',
                    '--enable-extensions', '--enable-gpu', '--enable-logging',
                    '--enable-webgl', '--force-webrtc-', '--host-resolver-rules=',
                    '--ignore-gpu-', '--log-file=', '--log-level=', '--profile-directory=',
                    '--remote-debugging-port=', '--use-angle=', '--use-gl=',
                    '--use-mock-keychain', '--v=', '--vmodule=', '--window-size=',
                    '--allow-pre-commit-input', '--disable-default-apps', '--disable-hang-monitor',
                    '--disable-popup-blocking', '--disable-prompt-on-repost', '--disable-sync',
                    '--enable-logging', '--homepage=', '--log-level=',
                    '--new-tab', '--no-first-run', '--no-pings', '--no-sandbox',
                    '--no-service-autorun', '--restore-last-session=', '--safebrowsing-disable-auto-update',
                    '--test-type=webdriver', '--use-mock-keychain'
                )
                
                filtered = []
                for a in args:
                    txt = str(a or '')
                    # Chỉ giữ lại the flags cần thiết như GPM Login
                    if any(txt.startswith(flag) for flag in essential_flags):
                        filtered.append(a)
                    elif any(txt.startswith(p) for p in bad_prefixes):
                        continue
                    else:
                        # Giữ lại the flags khác if không nằm in danh sách loại bỏ
                        filtered.append(a)
                
                # Loại bỏ duplicate and cập nhật
                seen = set()
                dedup = []
                for a in filtered:
                    if a in seen:
                        continue
                    seen.add(a)
                    dedup.append(a)
                
                # Cập nhật arguments bằng theh thay thế trực tiếp
                if len(dedup) != len(args):
                    # Thay thế arguments
                    chrome_options._arguments = dedup
                    removed_count = len(args) - len(dedup)
                    print(f"[FLAG-REMOVAL] Removed {removed_count} automation flags")
                    print(f"[FLAG-REMOVAL] After removal: {len(dedup)} flags")
                    print(f"[FLAG-REMOVAL] Remaining args: {[str(a) for a in dedup[:5]]}...")
                
        except Exception as e:
            print(f"[FLAG-REMOVAL] Error removing flags: {e}")
    
    def _enforce_chrome_policies(self) -> None:
        """Thiết lập Chrome Enterprise Policies ở HKCU để cưỡng chế tắt Password Manager/AutoSignIn.
        Không cần quyền admin (HKCU). Áp dụng cho mọi phiên bản launch (native/WebDriver).
        """
        try:
            import winreg
            policy_paths = [
                r"Software\Policies\Google\Chrome",
                r"Software\Policies\Chromium"
            ]
            for policy_path in policy_paths:
                for root in (winreg.HKEY_CURRENT_USER,):
                    try:
                        key = winreg.CreateKeyEx(root, policy_path, 0, winreg.KEY_SET_VALUE)
                        # 0 = disabled/false
                        winreg.SetValueEx(key, "PasswordManagerEnabled", 0, winreg.REG_DWORD, 0)
                        winreg.SetValueEx(key, "CredentialsEnableService", 0, winreg.REG_DWORD, 0)
                        winreg.SetValueEx(key, "AutoSignInAllowed", 0, winreg.REG_DWORD, 0)
                        winreg.SetValueEx(key, "AutofillAddressEnabled", 0, winreg.REG_DWORD, 0)
                        winreg.SetValueEx(key, "AutofillCreditCardEnabled", 0, winreg.REG_DWORD, 0)
                        winreg.SetValueEx(key, "PasswordLeakDetectionEnabled", 0, winreg.REG_DWORD, 0)
                        winreg.CloseKey(key)
                        print(f"[POLICY] Applied policies at HKCU\\{policy_path}")
                    except Exception as _hkcu_err:
                        print(f"[POLICY] Could not write HKCU policies at {policy_path}: {_hkcu_err}")
        except Exception as _e:
            print(f"[POLICY] Policy enforcement failed: {_e}")

    def _prelaunch_hardening(self, profile_path: str, language: str = None) -> None:
        """Harden profile prefs and local state to reduce Google beacons and automation signals.
        - Writes Default/Preferences: intl.accept_languages, signin, google, gcm, safebrowsing
        - Scrubs Local State 'google' block to avoid GCM registrations
        """
        try:
            import json as _json
            os.makedirs(os.path.join(profile_path, 'Default'), exist_ok=True)

            # 1) Update Preferences for all profile directories (Default, Profile 1, Profile 2, ...)
            profile_dirs = []
            root = os.path.join(profile_path)
            try:
                for name in os.listdir(root):
                    if name.lower() == 'default' or name.lower().startswith('profile'):
                        profile_dirs.append(os.path.join(root, name))
            except Exception:
                profile_dirs = [os.path.join(profile_path, 'Default')]

            for prof_dir in profile_dirs:
                prefs_path = os.path.join(prof_dir, 'Preferences')
                prefs_obj = None
                if os.path.exists(prefs_path):
                    try:
                        with open(prefs_path, 'r', encoding='utf-8') as pf:
                            content = pf.read().strip()
                            prefs_obj = _json.loads(content) if content else {}
                    except Exception:
                        prefs_obj = {}
                else:
                    prefs_obj = {}

                if isinstance(prefs_obj, dict):
                    if language:
                        intl = prefs_obj.get('intl', {})
                        intl['accept_languages'] = language
                        prefs_obj['intl'] = intl

                    # Disable Google signin, GCM beacons, and SafeBrowsing reporting
                    prefs_obj['google'] = {}
                    prefs_obj['signin'] = {"allowed": False}
                    gcm = prefs_obj.get('gcm', {})
                    gcm['product_category_for_subtypes'] = ""
                    gcm['wake_from_idle'] = False
                    prefs_obj['gcm'] = gcm
                    sb = prefs_obj.get('safebrowsing', {})
                    sb['enabled'] = False
                    sb['scout_reporting_enabled_when_deprecated'] = False
                    prefs_obj['safebrowsing'] = sb

                    # Disable Autofill & form data
                    autofill = prefs_obj.get('autofill', {})
                    autofill['enabled'] = False
                    autofill['profile_enabled'] = False
                    autofill['credit_card_enabled'] = False
                    prefs_obj['autofill'] = autofill

                    # Ensure minimal search config and disable omnibox
                    search_block = prefs_obj.get('search', {})
                    search_block['engine_forice'] = {"made_by_user": True}
                    prefs_obj['search'] = search_block
                    omnibox = prefs_obj.get('omnibox', {})
                    omnibox['suggestion_enabled'] = False
                    omnibox['suppress_suggestions'] = True
                    prefs_obj['omnibox'] = omnibox

                    # Reduce client hints / hints to Google domains
                    prefs_obj.setdefault('privacy_sandbox', {})
                    ch = prefs_obj.get('client_hints', {})
                    ch['enabled'] = False
                    prefs_obj['client_hints'] = ch

                    session_block = prefs_obj.get('session', {})
                    session_block['restore_on_startup'] = 1
                    session_block['startup_urls'] = []
                    prefs_obj['session'] = session_block

                    profile_block = prefs_obj.get('profile', {})
                    profile_block['exit_type'] = 'Normal'
                    profile_block['password_manager_enabled'] = False
                    prefs_obj['profile'] = profile_block

                    # Disable credentials services & autosignin
                    prefs_obj['credentials_enable_service'] = False
                    prefs_obj['credentials_enable_autosignin'] = False

                    try:
                        with open(prefs_path, 'w', encoding='utf-8') as pfw:
                            _json.dump(prefs_obj, pfw, ensure_ascii=False, indent=2)
                        print(f"[PRIVACY] [HARDEN] Preferences updated in: {prefs_path}")
                    except Exception as _pw:
                        print(f"[WARNING] [HARDEN] Could not write {prefs_path}: {_pw}")

            # 2) Update Local State: drop 'google' block to avoid background registrations
            local_state_path = os.path.join(profile_path, 'Local State')
            if os.path.exists(local_state_path):
                try:
                    with open(local_state_path, 'r', encoding='utf-8') as lf:
                        ls_content = lf.read().strip()
                        if ls_content:
                            ls = _json.loads(ls_content)
                        else:
                            ls = {}
                except Exception:
                    ls = {}

                if 'google' in ls:
                    try:
                        del ls['google']
                    except Exception:
                        pass
                # Remove GCM/invalidations blocks if present to stop background registrations
                for _k in ('gcm', 'invalidation', 'invalidations'):
                    if _k in ls:
                        try:
                            del ls[_k]
                        except Exception:
                            pass

                with open(local_state_path, 'w', encoding='utf-8') as lfw:
                    _json.dump(ls, lfw, ensure_ascii=False)

            # Xóa artefacts phiên to không còn gì to khôi phục
            try:
                import glob, shutil as _shutil
                default_dir = os.path.join(profile_path, 'Default')
                sessions_dir = os.path.join(default_dir, 'Sessions')
                if os.path.isdir(sessions_dir):
                    _shutil.rmtree(sessions_dir, ignore_errors=True)
                remove_patterns = [
                    'Current Session', 'Current Tabs', 'Last Session', 'Last Tabs',
                    'Sessions*', 'Tabs_*', 'Session_*'
                ]
                for pat in remove_patterns:
                    for fp in glob.glob(os.path.join(default_dir, pat)):
                        try:
                            if os.path.isdir(fp):
                                _shutil.rmtree(fp, ignore_errors=True)
                            else:
                                os.remove(fp)
                        except Exception:
                            pass
            except Exception:
                pass
        except Exception as _e:
            print(f"[WARNING] [HARDEN] No thể harden prefs/local state: {_e}")
    
    def launch_chrome_profile(self, profile_name, hidden=True, auto_login=False, login_data=None, start_url=None, optimized_mode=False, ultra_low_memory=False):
        """Khởi động Chrome with profile cụ thể
        
        Args:
            profile_name: Tên profile
            hidden: Chế độ ẩn
            auto_login: Tự động login
            login_data: Dữ liệu login
            start_url: URL start
            optimized_mode: Sử dụng chế độ optimize for bulk operations
            ultra_low_memory: Chế độ tiết kiệm RAM tối đa
        """
        try:
            profile_name = str(profile_name)
            print(f"[LAUNCH] Starting profile: {profile_name}")
            
            self.current_profile_name = profile_name
            profile_path = os.path.join(self.profiles_dir, profile_name)
            # Dọn nested dir trùng tên if have trước when mở
            try:
                self._dedupe_nested_profile_dir(profile_path)
            except Exception:
                pass
            
            if not os.path.exists(profile_path):
                print(f"[ERROR] [LAUNCH] Profile không tồn tại: {profile_name}")
                return False, f"Profile '{profile_name}' không tồn tại"
            
            # Kill Chrome processes - SKIP when launching concurrent livestream to avoid killing other profiles
            # Only kill if not in concurrent mode (avoid killing other launching profiles)
            try:
                # Skip kill for livestream-like launches (start_url provided and not auto_login)
                skip_kill = bool(start_url and start_url.strip() and not auto_login)
                # But if this profile is already in use (lock/DevToolsActivePort), force kill to free it
                try:
                    _running_marker = os.path.join(profile_path, 'DevToolsActivePort')
                    _has_lock = any(name.startswith('Singleton') for name in os.listdir(profile_path) if os.path.isfile(os.path.join(profile_path, name)))
                except Exception:
                    _running_marker = None
                    _has_lock = False
                if skip_kill and ((_running_marker and os.path.exists(_running_marker)) or _has_lock):
                    print("[LAUNCH] Profile appears in-use; overriding skip and killing Chrome for this profile")
                    skip_kill = False
                if not skip_kill:
                    self._kill_chrome_processes()
                else:
                    print(f"[LIVESTREAM] [CONCURRENT] Skipping kill_chrome_processes to allow concurrent launches")
            except Exception:
                print("[WARNING] [LAUNCH] kill_chrome_processes failed; continuing")
            # Cleanup leftover lock/marker files that prevent launching
            try:
                for _fname in ('DevToolsActivePort','SingletonLock','SingletonCookie','SingletonSocket','RunningChromeVersion'):
                    for _base in (profile_path, os.path.join(profile_path, 'Default')):
                        _fpath = os.path.join(_base, _fname)
                        if os.path.exists(_fpath):
                            try:
                                os.remove(_fpath)
                                print(f"[LAUNCH] Removed leftover file: {_fpath}")
                            except Exception:
                                pass
            except Exception:
                pass
            
            # Do not clean cache in any mode (user requested to preserve all data)
            
            # Xóa cache profile cũ to Chrome nhận diện tên mới
            self._clear_profile_name_cache(profile_path)

            # Pre-harden prefs & local state before starting Chrome
            try:
                # Try to align language with software.language if possible
                _lang_hint = None
                try:
                    _settings_probe = os.path.join(profile_path, 'profile_settings.json')
                    if os.path.exists(_settings_probe):
                        import json as _json
                        with open(_settings_probe, 'r', encoding='utf-8') as sf:
                            _ps = _json.load(sf)
                            _lang_hint = (_ps.get('software') or {}).get('language')
                except Exception:
                    pass
                self._prelaunch_hardening(profile_path, _lang_hint)
                # Enforce enterprise policies (HKCU) to guarantee settings even on fresh profiles
                self._enforce_chrome_policies()
            except Exception as _e:
                print(f"[WARNING] [LAUNCH] Hardening trước when start thất bại: {_e}")
            
            # Đọc cấu hình profile tuỳ chỉnh (if have)
            custom_settings = {}
            try:
                settings_path = os.path.join(profile_path, 'profile_settings.json')
                if os.path.exists(settings_path):
                    import json as _json
                    with open(settings_path, 'r', encoding='utf-8') as f:
                        custom_settings = _json.load(f)
            except Exception as _e:
                print(f"[WARNING] [LAUNCH] No read get profile_settings.json: {_e}")
            
            # Cấu hình Chrome options
            chrome_options = Options()
            
            # Áp dụng cấu hình mặc định with flags tối thiểu
            self._apply_default_config(chrome_options)
            
            # Áp dụng Chrome binary tùy chỉnh: ENV/INI or tự tải CfT theo version mong muốn from settings
            desired_version = ''
            try:
                # Ưu tiên software.browser_version, sau đó browser_version (top-level)
                desired_version = (sw.get('browser_version') or '').strip()
                if not desired_version:
                    # Fallback: read from top-level browser_version
                    try:
                        settings_file = os.path.join(profile_path, 'profile_settings.json')
                        if os.path.exists(settings_file):
                            import json as _json
                            with open(settings_file, 'r', encoding='utf-8') as sf:
                                data = _json.load(sf)
                                desired_version = (data.get('browser_version') or '').strip()
                    except Exception:
                        pass
            except Exception:
                desired_version = ''
            self._apply_custom_chrome_binary(chrome_options, profile_path, desired_version)
            chrome_options.add_argument(f"--user-data-dir={profile_path}")
            
            # Thêm user-agent from profile settings
            try:
                if 'sw' in locals() and sw.get('user_agent'):
                    ua = sw.get('user_agent')
                    chrome_options.add_argument(f"--user-agent={ua}")
                    print(f"[NETWORK] [LAUNCH] Using custom User-Agent: {ua[:50]}...")
                elif custom_settings.get('software', {}).get('user_agent'):
                    ua = custom_settings['software']['user_agent']
                    chrome_options.add_argument(f"--user-agent={ua}")
                    print(f"[NETWORK] [LAUNCH] Using profile User-Agent: {ua[:50]}...")
            except Exception as e:
                print(f"[WARNING] [LAUNCH] Could not set User-Agent: {e}")
            
            # Thêm language from profile settings
            try:
                if 'sw' in locals() and sw.get('language'):
                    lang = sw.get('language')
                    chrome_options.add_argument(f"--lang={lang}")
                    print(f"[NETWORK] [LAUNCH] Using language: {lang}")
            except Exception as e:
                print(f"[WARNING] [LAUNCH] Could not set language: {e}")
            # Chỉ giữ lại the flags cần thiết như GPM Login
            # Disable automation detection
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            # Chỉ giữ lại the flags cần thiết nhất như GPM Login
            # Tắt Password Manager & Auto Sign-in tuyệt đối
            try:
                prefs = {
                    "credentials_enable_service": False,
                    "profile.password_manager_enabled": False,
                    "autofill.profile_enabled": False,
                    "autofill.credit_card_enabled": False,
                    "credentials_enable_autosignin": False
                }
                chrome_options.add_experimental_option("prefs", prefs)
                chrome_options.add_argument("--disable-features=PasswordManagerOnboarding,AutofillServerCommunication,AutofillEnableAccountWalletStorage,AutoSignIn,PasswordImport")
                chrome_options.add_argument("--disable-save-password-bubble")
                print("[PRIVACY] [LAUNCH] Disabled password manager and auto sign-in")
            except Exception as _prefs_err:
                print(f"[WARNING] [LAUNCH] Could not apply password manager prefs: {_prefs_err}")
            
            # Sử dụng --profile-directory to hiển thị profile name tùy chỉnh
            # Lấy display name from settings or sử dụng profile name
            # profile_info = custom_settings.get('profile_info', {})
            # profile_display_name = profile_info.get('display_name', profile_name)
            # chrome_options.add_argument(f"--profile-directory={profile_display_name}")
            
            # Áp dụng antidetect flags - Chỉ giữ flags cần thiết nhất
            # Hidden: với livestream (có start_url và không auto_login), tránh headless để đảm bảo view được tính
            try:
                if hidden:
                    is_livestream_like = bool(start_url and start_url.strip() and not auto_login)
                    if is_livestream_like:
                        # Stealth-hidden: cửa sổ thật, nhỏ, đặt ngoài màn hình + chống throttling/occlusion
                        chrome_options.add_argument("--window-size=480,360")
                        chrome_options.add_argument("--window-position=-2000,0")
                        # Giữ render khi bị occluded/minimized
                        chrome_options.add_argument("--disable-background-timer-throttling")
                        chrome_options.add_argument("--disable-backgrounding-occluded-windows")
                        chrome_options.add_argument("--disable-renderer-backgrounding")
                        chrome_options.add_argument("--disable-features=CalculateNativeWinOcclusion,TabHoverCards")
                        # Tối ưu RAM/CPU an toàn cho livestream
                        chrome_options.add_argument("--renderer-process-limit=4")
                        chrome_options.add_argument("--disable-site-isolation-trials")
                        chrome_options.add_argument("--enable-low-end-device-mode")
                        chrome_options.add_argument("--autoplay-policy=no-user-gesture-required")
                        # Dùng ANGLE D3D11 ổn định GPU trên Windows
                        chrome_options.add_argument("--use-angle=d3d11")
                        print("[DISPLAY] [LAUNCH] Stealth-hidden window (no headless) for livestream")
                    if not is_livestream_like:
                        # Không phải livestream: dùng headless thật để tiết kiệm tài nguyên
                        chrome_options.add_argument("--headless=new")
                        chrome_options.add_argument("--window-size=1366,768")
                        chrome_options.add_argument("--window-position=-2000,0")
                        print("[DISPLAY] [LAUNCH] Headless mode enabled (hidden)")
            except Exception as _herr:
                print(f"[WARNING] [LAUNCH] Could not set hidden/headless flags: {_herr}")
            # antidetect = custom_settings.get('antidetect', {})
            # if antidetect.get('enabled', False):
            #     chrome_flags = custom_settings.get('chrome_flags', [])
            #     for flag in chrome_flags:
            #         chrome_options.add_argument(flag)
            
            # Áp dụng one số tùy chọn Software from custom_settings
            sw = custom_settings.get('software', {})
            # Kết hợp with gpm_defaults if profile không ghi đè
            if isinstance(self.gpm_defaults, dict):
                sw.setdefault('user_agent', self.gpm_defaults.get('user_agent'))
                sw.setdefault('language', self.gpm_defaults.get('language'))
                sw.setdefault('webrtc_policy', self.gpm_defaults.get('webrtc_policy'))
                sw.setdefault('raw_proxy', self.gpm_defaults.get('raw_proxy'))

            # Chọn User-Agent
            auto_ua = os.environ.get('AUTO_UA', '1').lower() in ('1','true','yes')
            use_pool = os.environ.get('UA_POOL', '1').lower() in ('1','true','yes')
            ua_cfg = (sw.get('user_agent') or '').strip()
            ua_source = 'profile'
            if auto_ua:
                if use_pool:
                    pool = self._user_agent_pool()
                    try:
                        import random as _rand
                        ua = _rand.forice(pool)
                    except Exception:
                        ua = pool[0]
                    ua_source = 'pool'
                else:
                    ua = self._random_user_agent()
                    ua_source = 'random'
            else:
                ua = ua_cfg
                ua_source = 'profile'
            if ua:
                chrome_options.add_argument(f"--user-agent={ua}")
            # Auto-detect locale if bật env AUTO_LOCALE or if trống
            auto_locale = os.environ.get('AUTO_LOCALE', '1').lower() in ('1','true','yes')
            detected_locale = None
            if auto_locale or not (sw.get('language') or '').strip():
                detected_locale = self._detect_locale_from_ip()
            lang = (sw.get('language') or '').strip() or ((detected_locale or {}).get('languages', ['vi'])[0])
            if lang:
                chrome_options.add_argument(f"--lang={lang}")
                # Ghi ando Preferences: intl.accept_languages
                try:
                    prefs_path = os.path.join(profile_path, 'Default', 'Preferences')
                    prefs_obj = {}
                    if os.path.exists(prefs_path):
                        import json as _json
                        with open(prefs_path, 'r', encoding='utf-8') as pf:
                            content = pf.read().strip()
                            if content:
                                prefs_obj = _json.loads(content)
                    # Set languages
                    intl = prefs_obj.get('intl', {})
                    intl['accept_languages'] = lang
                    prefs_obj['intl'] = intl
                    # Đặt DuckDuckGo làm search engine mặc định to tránh Google CAPTCHA when gõ from thanh địa chỉ
                    dse = {
                        "enabled": True,
                        "name": "DuckDuckGo",
                        "keyword": "duckduckgo.com",
                        "search_url": "https://duckduckgo.com/?q={searchTerms}",
                        "suggest_url": "",
                        "favicon_url": "https://duckduckgo.com/favicon.ico",
                        "id": 0
                    }
                    prefs_obj['default_search_provider'] = dse
                    prefs_obj['default_search_provider_data'] = {"template_url_data": dse}
                    # Đánh dấu done chọn search engine
                    se_forice = prefs_obj.get('search', {})
                    se_forice['engine_forice'] = {"made_by_user": True}
                    prefs_obj['search'] = se_forice
                    with open(prefs_path, 'w', encoding='utf-8') as pfw:
                        import json as _json
                        _json.dump(prefs_obj, pfw, ensure_ascii=False, indent=2)
                except Exception as _e:
                    print(f"[WARNING] [LAUNCH] No ghi get intl.accept_languages: {_e}")

            # Đồng bộ Accept-Language and UA qua CDP càng sớm càng tốt
            try:
                # Sẽ gọi sau when driver sẵn: Network.setUserAgentOverride + ExtraHTTPHeaders
                self._pending_lang_header = lang
            except Exception:
                pass
            # webrtc_policy = (sw.get('webrtc_policy') or '').strip()
            # if webrtc_policy:
            #     chrome_options.add_argument(f"--force-webrtc-ip-handling-policy={webrtc_policy}")
            #     # Đồng bộ thêm ando Preferences.webrtc
            #     try:
            #         prefs_path = os.path.join(profile_path, 'Default', 'Preferences')
            #         prefs_obj = {}
            #         if os.path.exists(prefs_path):
            #             import json as _json
            #             with open(prefs_path, 'r', encoding='utf-8') as pf:
            #                 content = pf.read().strip()
            #                 if content:
            #                     prefs_obj = _json.loads(content)
            #         webrtc = prefs_obj.get('webrtc', {})
            #         if webrtc_policy == 'default_public_interface_only':
            #             webrtc['ip_handling_policy'] = 'default_public_interface_only'
            #             webrtc['multiple_routes'] = False
            #             webrtc['non_proxied_udp'] = False
            #         elif webrtc_policy == 'disable_non_proxied_udp':
            #             webrtc['ip_handling_policy'] = 'disable_non_proxied_udp'
            #             webrtc['multiple_routes'] = False
            #             webrtc['non_proxied_udp'] = False
            #         else:
            #             webrtc['ip_handling_policy'] = 'default'
            #         prefs_obj['webrtc'] = webrtc
            #         with open(prefs_path, 'w', encoding='utf-8') as pfw:
            #             import json as _json
            #             _json.dump(prefs_obj, pfw, ensure_ascii=False, indent=2)
            #     except Exception as _e:
            #         print(f"[WARNING] [LAUNCH] No ghi get webrtc prefs: {_e}")
            # Hardware (tham số chủ yếu save trữ; have mục tiêu mở rộng in tương lai)
            # Hiện tại chúng ta không thể thay đổi MAC thật; giá trị get save to hiển thị.

            # No mở trang have thể kích hoạt captcha ngay when start
            # Tránh mở google.com, chrome://welcome, or the URL search ngay lập tức
            # Chỉ thêm flags cần thiết nhất
            # chrome_options.add_argument("--homepage=about:blank")
            # chrome_options.add_argument("--restore-last-session=false")
            # chrome_options.add_argument("--new-tab")

            # Áp dụng proxy from sw.raw_proxy (if have, dạng user:pass@host:port or host:port)
            raw_proxy = (sw.get('raw_proxy') or '').strip()
            if raw_proxy:
                try:
                    # Hỗ trợ cả socks5/http: prefix if người dùng fill
                    if '://' in raw_proxy:
                        proxy_url = raw_proxy
                    else:
                        # Mặc định http
                        proxy_url = f"http://{raw_proxy}"
                    chrome_options.add_argument(f"--proxy-server={proxy_url}")
                    print(f"[NETWORK] [PROXY] Done áp dụng proxy: {proxy_url}")
                except Exception as _pe:
                    print(f"[WARNING] [PROXY] No áp dụng get proxy: {_pe}")
            
            # Decide configuration based on login flow
            def _is_login_like_url(url: str) -> bool:
                try:
                    if not url:
                        return False
                    lu = url.lower()
                    return ('/login' in lu) or ('tiktok.com/login' in lu)
                except Exception:
                    return False

            login_flow = bool(auto_login) or _is_login_like_url(start_url)

            if optimized_mode and not login_flow:
                print(f"[TOOL] [LAUNCH] Using optimized mode for bulk operations")
                self._apply_optimized_chrome_config(chrome_options, hidden, ultra_low_memory)
            else:
                # Use stable/base config for login and normal flows
                if login_flow and optimized_mode:
                    print(f"[SECURITY] [LAUNCH] Login flow detected → using base config (ignore optimized flags)")
            self._apply_base_chrome_config(chrome_options, hidden)
            # Loại bỏ --no-sandbox to tránh cảnh báo and tăng ổn định
            try:
                self._remove_unsafe_sandbox_flag(chrome_options)
            except Exception:
                pass
            # Ensure extensions are allowed so profile title extension can run
            try:
                self._ensure_extensions_allowed(chrome_options)
            except Exception as _e:
                print(f"[WARNING] [LAUNCH] Could not sanitize extension flags: {_e}")
            
            # Inject tiny extension to show profile name in tab title
            try:
                title_ext_path = self._ensure_profile_title_extension(profile_name)
                if title_ext_path and os.path.exists(title_ext_path):
                    chrome_options.add_argument(f"--load-extension={title_ext_path}")
                    print(f"[EXTENSION] [LAUNCH] Loaded profile-title extension for: {profile_name}")
            except Exception as e:
                print(f"[WARNING] [LAUNCH] Could not load profile-title extension: {e}")

            # Ensure SwitchyOmega has proxy control priority by isolating extensions
            try:
                extension_id = "pfnededegaaopdmhkdmcofjmoldfiped"
                so_base = os.path.join(profile_path, "Default", "Extensions", extension_id)
                so_version_dir = None
                if os.path.exists(so_base):
                    try:
                        versions = [d for d in os.listdir(so_base) if os.path.isdir(os.path.join(so_base, d))]
                        if versions:
                            versions.sort()
                            so_version_dir = os.path.join(so_base, versions[-1])
                    except Exception:
                        so_version_dir = None

                # Build allowlist of extensions (SwitchyOmega + title extension)
                allowlist = []
                if so_version_dir and os.path.exists(so_version_dir):
                    allowlist.append(so_version_dir)
                if title_ext_path and os.path.exists(title_ext_path):
                    allowlist.append(title_ext_path)

                if allowlist:
                    # Load extensions like GPM Login (cleaner approach)
                    paths_arg = ",".join(allowlist)
                    try:
                        # Chỉ load extension, không disable others (giống GPM)
                        chrome_options.add_argument(f"--load-extension={paths_arg}")
                        print(f"[SECURITY] [LAUNCH] Loading extensions like GPM Login")
                    except Exception:
                        pass
            except Exception as e:
                print(f"[WARNING] [LAUNCH] Could not isolate extensions: {e}")
            
            # Launch Chrome with fallback mechanism
            # Xóa cache đồ họa to tránh save vết GPU giữa the lần chạy
            try:
                self._purge_graphics_caches(profile_path)
            except Exception:
                pass
            # Ghi log cấu hình HW/SW trước when launch (ghi rõ nguồn UA)
            try:
                # Đọc hardware from profile_settings.json (if have)
                hw_cpu = hw_mem = hw_vendor = hw_renderer = None
                try:
                    import json as _json
                    with open(os.path.join(profile_path, 'profile_settings.json'), 'r', encoding='utf-8') as _psf:
                        _ps = _json.load(_psf)
                        _hw = _ps.get('hardware') or {}
                        hw_cpu = _hw.get('cpu_cores')
                        hw_mem = _hw.get('device_memory')
                        hw_vendor = _hw.get('webgl_vendor')
                        hw_renderer = _hw.get('webgl_renderer')
                except Exception:
                    pass
                # Lấy software from sw hiện tại
                sw_webrtc = (sw.get('webrtc_policy') or '').strip()
                sw_proxy = (sw.get('raw_proxy') or '').strip()
                self._append_app_log(
                    profile_path,
                    f"Launching Chrome with configured options | UA({ua_source})={ua or 'N/A'} | LANG={lang or 'N/A'} | WErtc={sw_webrtc or 'default'} | PROXY={'set' if sw_proxy else 'none'} | HW(cpu={hw_cpu or 'unk'}, mem={hw_mem or 'unk'}, glVendor={hw_vendor or 'rand'}, glRenderer={hw_renderer or 'rand'})"
                )
            except Exception:
                self._append_app_log(profile_path, "Launching Chrome with configured options")
            # In đường dẫn log to người dùng tiện mở
            try:
                log_path = self.get_chrome_log_path(profile_name)
                print(f"[INPUT] [LOG] Chrome log: {log_path}")
            except Exception:
                pass
            # Trước when launch: sử dụng function fix_chrome_command to optimize hóa command line
            try:
                # Import fix function
                import sys
                import os as os_module
                sys.path.append(os_module.path.dirname(os_module.path.dirname(__file__)))
                from fix_chrome_command import fix_chrome_command, create_rules_from_gpm_config
                
                # Tạo command line hiện tại
                args_attr = None
                if hasattr(chrome_options, 'arguments'):
                    args_attr = 'arguments'
                elif hasattr(chrome_options, '_arguments'):
                    args_attr = '_arguments'
                
                if args_attr:
                    args = list(getattr(chrome_options, args_attr) or [])
                    current_command = 'chrome.exe ' + ' '.join([str(arg) for arg in args])
                    print(f"[COMMAND-FIX] Original command: {len(args)} flags")
                    print(f"[COMMAND-FIX] Original command length: {len(current_command)} characters")
                    
                    # Tạo rules from GPM config và giữ nguyên profile_path để không mất session
                    rules = create_rules_from_gpm_config(gpm_config)
                    rules['user_data_dir'] = profile_path
                    rules.pop('extension_path', None)
                    
                    # Fix command line
                    fixed_command = fix_chrome_command(current_command, rules)
                    print(f"[COMMAND-FIX] Fixed command: {fixed_command}")
                    
                    if not fixed_command.startswith('ERROR:'):
                        # Parse fixed command and cập nhật chrome_options
                        import shlex
                        fixed_parts = shlex.split(fixed_command)
                        if len(fixed_parts) > 1:
                            fixed_args = fixed_parts[1:]  # Bỏ executable path
                            chrome_options._arguments = fixed_args
                            print(f"[COMMAND-FIX] Applied fixed command line: {len(fixed_args)} flags")
                            print(f"[COMMAND-FIX] Removed {len(args) - len(fixed_args)} unnecessary flags")
                    else:
                        print(f"[COMMAND-FIX] Error: {fixed_command}")
                
            except Exception as e:
                print(f"[COMMAND-FIX] Error fixing command line: {str(e)}")

            # Nếu mở hiển thị (Starting), KHÔNG dùng WebDriver để tránh ChromeDriver tự chèn --remote-debugging-port=0
            if hidden is False:
                print(f"[DEBUG] [LAUNCH] Using native launch (visible mode) - keyboard-only autofill available")
                try:
                    ok = self._launch_chrome_native_fixed(chrome_options, profile_path, start_url)
                    if ok:
                        # If native visible and auto_login requested, perform keystroke-based autofill
                        try:
                            if auto_login and login_data:
                                print(f"[AUTOLOGIN] Native autofill requested - using keyboard-only method")
                                import threading as _threading
                                def _do_native_autofill():
                                    try:
                                        import time as _time
                                        import pyautogui as _pg
                                        
                                        # Disable failsafe to prevent accidental stops
                                        _pg.FAILSAFE = False
                                        
                                        # Wait for Chrome to load
                                        _time.sleep(5)
                                        
                                        # Get login data
                                        username = login_data.get('username', login_data.get('email', ''))
                                        password = login_data.get('password', '')
                                        
                                        if username and password:
                                            print(f"[AUTOLOGIN] Starting keyboard-only autofill...")
                                            
                                            # Method 1: Use Tab navigation (no mouse movement)
                                            try:
                                                # First, press Tab a few times to skip logo/header elements
                                                print(f"[AUTOLOGIN] Skipping logo/header elements...")
                                                for i in range(3):
                                                    _pg.press('tab')
                                                    _time.sleep(0.3)
                                                
                                                # Press Tab to focus first field (email/username)
                                                _pg.press('tab')
                                                _time.sleep(0.5)
                                                print(f"[AUTOLOGIN] Focused on username field")
                                                
                                                # Clear and type username
                                                _pg.hotkey('ctrl', 'a')
                                                _time.sleep(0.2)
                                                _pg.typewrite(username, interval=0.05)
                                                _time.sleep(0.5)
                                                print(f"[AUTOLOGIN] Typed username")
                                                
                                                # Press Tab to go to password field
                                                _pg.press('tab')
                                                _time.sleep(0.5)
                                                print(f"[AUTOLOGIN] Focused on password field")
                                                
                                                # Clear and type password
                                                _pg.hotkey('ctrl', 'a')
                                                _time.sleep(0.2)
                                                _pg.typewrite(password, interval=0.05)
                                                _time.sleep(0.5)
                                                print(f"[AUTOLOGIN] Typed password")
                                                
                                                # Press Enter to submit
                                                _pg.press('enter')
                                                print(f"[AUTOLOGIN] Keyboard-only autofill completed")
                                                
                                                # Wait for captcha to appear (10-15 seconds)
                                                print(f"[CAPTCHA] Waiting for captcha to appear...")
                                                _time.sleep(12)  # Wait for captcha loading
                                                
                                                # Try to solve captcha automatically
                                                try:
                                                    print(f"[CAPTCHA] Attempting to solve captcha...")
                                                    
                                                    # Take screenshot to detect captcha
                                                    import pyautogui as _pg2
                                                    screenshot = _pg2.screenshot()
                                                    
                                                    # Try to solve captcha with native OMOcaptcha solver (no WebDriver needed)
                                                    if NATIVE_CAPTCHA_SOLVER_AVAILABLE:
                                                        print(f"[CAPTCHA] [NATIVE-OMO] Attempting to solve captcha with OMOcaptcha...")
                                                        try:
                                                            # Load API key from config
                                                            if hasattr(self, 'config') and self.config.has_section('CAPTCHA'):
                                                                api_key = self.config.get('CAPTCHA', 'omocaptcha_api_key', fallback=None)
                                                                if api_key and api_key != 'YOUR_OMOCAPTCHA_API_KEY_HERE':
                                                                    print(f"[CAPTCHA] [NATIVE-OMO] Initializing native solver...")
                                                                    solver = NativeOMOcaptchaSolver(api_key)
                                                                    success = solver.solve_captcha()
                                                                    if success:
                                                                        print(f"[SUCCESS] [CAPTCHA] [NATIVE-OMO] Captcha solved!")
                                                                        _time.sleep(2)
                                                                    else:
                                                                        print(f"[WARNING] [CAPTCHA] [NATIVE-OMO] Failed to solve captcha")
                                                                else:
                                                                    print(f"[WARNING] [CAPTCHA] [NATIVE-OMO] No valid API key")
                                                            else:
                                                                print(f"[WARNING] [CAPTCHA] [NATIVE-OMO] No [CAPTCHA] section in config")
                                                        except Exception as solver_err:
                                                            print(f"[ERROR] [CAPTCHA] [NATIVE-OMO] Error: {solver_err}")
                                                            import traceback
                                                            print(f"Traceback: {traceback.format_exc()}")
                                                    else:
                                                        print(f"[INFO] [CAPTCHA] Native OMOcaptcha solver not available")
                                                        print(f"[INFO] [CAPTCHA] Manual solving required")
                                                    
                                                except Exception as captcha_err:
                                                    print(f"[CAPTCHA] Auto-solve failed: {captcha_err}")
                                                
                                            except Exception as tab_err:
                                                print(f"[AUTOLOGIN] Tab navigation failed: {tab_err}")
                                                
                                                # Method 2: Use Ctrl+V with clipboard (backup)
                                                try:
                                                    import pyperclip as _pc
                                                    
                                                    # Focus first field and paste username
                                                    _pg.hotkey('ctrl', 'a')
                                                    _pc.copy(username)
                                                    _pg.hotkey('ctrl', 'v')
                                                    _time.sleep(0.5)
                                                    
                                                    # Tab to password field
                                                    _pg.press('tab')
                                                    _time.sleep(0.5)
                                                    
                                                    # Paste password
                                                    _pg.hotkey('ctrl', 'a')
                                                    _pc.copy(password)
                                                    _pg.hotkey('ctrl', 'v')
                                                    _time.sleep(0.5)
                                                    
                                                    # Submit
                                                    _pg.press('enter')
                                                    print(f"[AUTOLOGIN] Clipboard autofill completed")
                                                    
                                                except Exception as clip_err:
                                                    print(f"[AUTOLOGIN] Clipboard method failed: {clip_err}")
                                        
                                    except Exception as _eaf:
                                        print(f"[AUTOLOGIN] Native autofill error: {_eaf}")
                                
                                _threading.Thread(target=_do_native_autofill, daemon=True).start()
                            else:
                                print(f"[INFO] [LAUNCH] No autofill requested for native launch")
                        except Exception as _af_err:
                            print(f"[AUTOLOGIN] Could not start native autofill: {_af_err}")
                        return True, "Chrome started (native)"
                    else:
                        print("[ERROR] [LAUNCH] Native visible start failed; not falling back to WebDriver to avoid remote-debugging-port")
                        return False, "Native start failed (visible). Please retry or check Chrome path."
                except Exception as _ne:
                    print(f"[ERROR] [LAUNCH] Native start failed: {_ne}")
                    return False, "Native start exception (visible)."

            print(f"[DEBUG] [LAUNCH] Using WebDriver launch (hidden mode) - autofill available")

            driver = self._launch_chrome_with_fallback(chrome_options, profile_path, hidden)
            
            if not driver:
                self._append_app_log(profile_path, "Chrome failed to start")
                return False, "Chrome không thể start"
            
            # Áp dụng stealth to giảm bị detect bot
            try:
                self._apply_stealth_driver(driver, lang, profile_path)
                # Áp dụng antidetect settings from profile
                self._apply_stealth_evasion(driver, profile_path)
                # Đồng bộ UA/Accept-Language qua CDP to thống nhất mọi request
                try:
                    driver.execute_cdp_cmd('Network.enable', {})
                    # Nếu have UA cấu hình (ví dụ bạn muốn 139.0.7258.139), ưu tiên dùng nó; if trống then fallback Browser.getVersion
                    ua_to_apply = (ua or '').strip()
                    if not ua_to_apply:
                        try:
                            ver = driver.execute_cdp_cmd('Browser.getVersion', {}) or {}
                            ua_str = (ver.get('userAgent') or '').strip()
                            if ua_str:
                                ua_to_apply = ua_str
                        except Exception:
                            ua_to_apply = ''
                    if ua_to_apply:
                        # UA-CH metadata đồng bộ with UA
                        metadata = self._build_user_agent_metadata(ua_to_apply)
                        cmd = {
                            'userAgent': ua_to_apply,
                            'acceptLanguage': (lang or 'en-US')
                        }
                        if metadata:
                            cmd['userAgentMetadata'] = metadata
                        driver.execute_cdp_cmd('Network.setUserAgentOverride', cmd)
                        # Lưu UA done áp dụng ngược ando profile_settings.json to lần sau GUI hiển thị đúng
                        try:
                            import json as _json
                            settings_file = os.path.join(profile_path, 'profile_settings.json')
                            data = {}
                            if os.path.exists(settings_file):
                                with open(settings_file, 'r', encoding='utf-8') as sf:
                                    data = _json.load(sf) or {}
                            sw_block = data.get('software') or {}
                            sw_block['user_agent'] = ua_to_apply
                            # Cập nhật cả "browser_version" to GUI đồng bộ combobox
                            try:
                                import re as _re
                                m = _re.search(r"Chrome/(\d+[^\s]*)", ua_to_apply)
                                if m:
                                    data['browser_version'] = m.group(1)
                            except Exception:
                                pass
                            data['software'] = sw_block
                            with open(settings_file, 'w', encoding='utf-8') as sfw:
                                _json.dump(data, sfw, ensure_ascii=False, indent=2)
                        except Exception:
                            pass
                    # Luôn set Accept-Language header
                    driver.execute_cdp_cmd('Network.setExtraHTTPHeaders', {
                        'headers': {
                            'Accept-Language': (lang or 'en-US')
                        }
                    })
                except Exception as _cdp:
                    print(f"[WARNING] [LAUNCH] No đồng bộ UA/headers qua CDP: {_cdp}")
                # Áp dụng timezone theo IP if have
                try:
                    detected_locale = getattr(self, '_last_detected_locale', None)
                except Exception:
                    detected_locale = None
                try:
                    if not detected_locale:
                        detected_locale = self._detect_locale_from_ip()
                        self._last_detected_locale = detected_locale
                except Exception:
                    detected_locale = None
                try:
                    if detected_locale and detected_locale.get('timezone'):
                        driver.execute_cdp_cmd('Emulation.setTimezoneOverride', {
                            'timezoneId': detected_locale['timezone']
                        })
                        self._append_app_log(profile_path, f"Timezone override: {detected_locale['timezone']}")
                except Exception as _tz:
                    print(f"[WARNING] [LAUNCH] No set timezone qua CDP: {_tz}")
                # Chặn tạm thời truy cập *.google.* in giai đoạn warmup to tránh gọi nền
                try:
                    driver.execute_cdp_cmd('Network.enable', {})
                    driver.execute_cdp_cmd('Network.setBlockedURLs', { 'urls': [
                        '*://*.google.com/*',
                        '*://*.gstatic.com/*',
                        '*://clientservices.googleapis.com/*',
                        '*://clients4.google.com/*',
                        '*://clients6.google.com/*',
                        '*://safebrowsing.googleapis.com/*',
                        '*://play.googleapis.com/*',
                        '*://firebaseinstallations.googleapis.com/*',
                        '*://fcm.googleapis.com/*',
                        '*://gcm.googleapis.com/*',
                        '*://mtalk.google.com/*',
                        '*://invalidation.googleapis.com/*',
                        '*://invalidations.googleapis.com/*',
                        '*://push.googleapis.com/*',
                        '*://www.google.com/gen_204*',
                        '*://ssl.gstatic.com/gb/*',
                        '*://clients*.google.com/*',
                        '*://clients*.googleusercontent.com/*',
                        '*://www.google.com/sorry/*'
                    ] })
                except Exception:
                    pass
                # Humanizer: cuộn/di chuột nhẹ ngay sau load
                try:
                    humanizer = r"""
                    (function(){
                      if (window.__humanized__) return; window.__humanized__=true;
                      function r(a,b){return Math.floor(Math.random()*(b-a+1))+a}
                      function s(){let t=r(200,1000), st=r(10,40), i=0; let iv=setInterval(()=>{window.scrollBy(0,st); i+=st; if(i>=t) clearInterval(iv)}, r(50,120))}
                      function m(){let x=r(10,200), y=r(10,150); let ev=new MouseEvent('mousemove',{clientX:x, clientY:y, bubbles:true}); document.dispatchEvent(ev)}
                      setTimeout(s, r(800,2000)); setTimeout(m, r(1200,2500));
                    })();
                    """
                    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', { 'source': humanizer })
                except Exception:
                    pass

                # Warm-up delay to tránh rate-limit/captcha ngay sau start
                try:
                    delay_ms = random.randint(7000, 12000)
                    print(f"[WAITING] [WARMUP] Chờ {delay_ms}ms trước when thao tác find kiếm...")
                    self._append_app_log(profile_path, f"Warmup delay: {delay_ms}ms")
                    time.sleep(delay_ms/1000.0)
                except Exception:
                    pass
                # Gỡ chặn sau warmup, giữ chặn GCM/invalidations endpoints + beacon bot
                try:
                    driver.execute_cdp_cmd('Network.setBlockedURLs', { 'urls': [
                        '*://clientservices.googleapis.com/*',
                        '*://clients4.google.com/*',
                        '*://clients6.google.com/*',
                        '*://safebrowsing.googleapis.com/*',
                        '*://firebaseinstallations.googleapis.com/*',
                        '*://fcm.googleapis.com/*',
                        '*://gcm.googleapis.com/*',
                        '*://mtalk.google.com/*',
                        '*://invalidation.googleapis.com/*',
                        '*://invalidations.googleapis.com/*',
                        '*://push.googleapis.com/*',
                        '*://www.google.com/gen_204*',
                        '*://ssl.gstatic.com/gb/*',
                        '*://clients*.google.com/*',
                        '*://clients*.googleusercontent.com/*',
                        '*://www.google.com/sorry/*'
                    ] })
                except Exception:
                    pass

                # Thêm script to chặn Google search and chuyển hướng
                try:
                    redirect_script = """
                    // Chặn Google search and chuyển hướng
                    const originalOpen = window.open;
                    const originalAssign = window.location.assign;
                    const originalReplace = window.location.replace;
                // Đồng bộ navigator.language/navigator.languages with Accept-Language done đặt
                try {
                  const lang = (navigator.language || 'en-US');
                  Object.defineProperty(navigator, 'language', { get: () => lang });
                  const langs = (navigator.languages && navigator.languages.length) ? navigator.languages : [lang.split(',')[0]];
                  Object.defineProperty(navigator, 'languages', { get: () => langs });
                } catch(e) {}
                    
                    function redirectGoogleSearch(url) {
                        if (url.includes('google.com/search')) {
                            const urlObj = new URL(url);
                            const query = urlObj.searchParams.get('q');
                            if (query) {
                                const searchEngines = [
                                    `https://duckduckgo.com/?q=${encodeURIComponent(query)}`,
                                    `https://www.bing.com/search?q=${encodeURIComponent(query)}`,
                                    `https://search.yahoo.com/search?p=${encodeURIComponent(query)}`,
                                    `https://www.startpage.com/sp/search?query=${encodeURIComponent(query)}`,
                                    `https://searx.be/search?q=${encodeURIComponent(query)}`
                                ];
                                const randomEngine = searchEngines[Math.floor(Math.random() * searchEngines.length)];
                                console.log('[REFRESH] [SEARCH] Chuyển from Google sang:', randomEngine);
                                return randomEngine;
                            }
                        }
                        return url;
                    }
                    
                    window.open = function(url, ...args) {
                        const newUrl = redirectGoogleSearch(url);
                        return originalOpen.call(this, newUrl, ...args);
                    };
                    
                    window.location.assign = function(url) {
                        const newUrl = redirectGoogleSearch(url);
                        return originalAssign.call(this, newUrl);
                    };
                    
                    window.location.replace = function(url) {
                        const newUrl = redirectGoogleSearch(url);
                        return originalReplace.call(this, newUrl);
                    };
                    
                    // Chặn form submit đến Google
                    document.addEventListener('submit', function(e) {
                        const form = e.target;
                        const action = form.action;
                        if (action && action.includes('google.com/search')) {
                            e.preventDefault();
                            const query = form.querySelector('input[name="q"]')?.value;
                            if (query) {
                                const searchEngines = [
                                    `https://duckduckgo.com/?q=${encodeURIComponent(query)}`,
                                    `https://www.bing.com/search?q=${encodeURIComponent(query)}`,
                                    `https://search.yahoo.com/search?p=${encodeURIComponent(query)}`,
                                    `https://www.startpage.com/sp/search?query=${encodeURIComponent(query)}`,
                                    `https://searx.be/search?q=${encodeURIComponent(query)}`
                                ];
                                const randomEngine = searchEngines[Math.floor(Math.random() * searchEngines.length)];
                                console.log('[REFRESH] [SEARCH] Chuyển form from Google sang:', randomEngine);
                                window.location.href = randomEngine;
                            }
                        }
                    });
                    """
                    driver.execute_script(redirect_script)
                except Exception:
                    pass

                # Vô hiệu client hints/UA-CH and thống nhất Accept-Language qua headers CDP
                try:
                    hdrs = {
                        'Accept-Language': lang or 'en-US,en;q=0.9',
                        'Sec-CH-UA-Platform': None,
                        'Sec-CH-UA-Platform-Version': None,
                        'Sec-CH-UA': None,
                        'Sec-CH-UA-Arch': None,
                        'Sec-CH-UA-Bitness': None,
                        'Sec-CH-UA-Full-Version-List': None,
                        'Sec-CH-UA-Model': None
                    }
                    driver.execute_cdp_cmd('Network.setExtraHTTPHeaders', { 'headers': {k:v for k,v in hdrs.items() if v is not None} })
                except Exception:
                    pass
            except Exception as _se:
                print(f"[WARNING] [STEALTH] No thể áp dụng stealth: {_se}")

            # Handle login logic and Startup URL from cấu hình if have
            # Ưu tiên: tham số start_url > software.startup_url
            startup_url = start_url
            if not startup_url:
                su = (sw.get('startup_url') or '').strip()
                if su:
                    startup_url = su
            # Tránh mở Google Search trực tiếp (dễ captcha). Chuyển sang search engine khác.
            safe_start_url = startup_url
            try:
                if startup_url and 'google.com/search' in startup_url.lower():
                    from urllib.parse import urlparse, parse_qs, urlencode
                    import random
                    parsed = urlparse(startup_url)
                    q = parse_qs(parsed.query).get('q', [''])[0]
                    if q:
                        # Chọn ngẫu nhiên search engine to tránh detection
                        search_engines = [
                            f"https://duckduckgo.com/?{urlencode({'q': q})}",
                            f"https://www.bing.com/search?{urlencode({'q': q})}",
                            f"https://search.yahoo.com/search?{urlencode({'p': q})}",
                            f"https://www.startpage.com/sp/search?{urlencode({'query': q})}",
                            f"https://searx.be/search?{urlencode({'q': q})}"
                        ]
                        safe_start_url = random.choice(search_engines)
                        print(f"[REFRESH] [SEARCH] Chuyển from Google sang {safe_start_url.split('//')[1].split('/')[0]}: {q}")
                    else:
                        safe_start_url = "about:blank"
            except Exception:
                safe_start_url = startup_url or "about:blank"
            print(f"[DEBUG] [AUTOLOGIN] Calling _handle_auto_login...")
            print(f"[DEBUG] [AUTOLOGIN] auto_login={auto_login}, login_data={bool(login_data)}")
            self._handle_auto_login(driver, profile_path, auto_login, login_data, safe_start_url)
            
            # Ghi fingerprint cơ bản ando app log to chẩn đoán
            try:
                # Lặp lại HW/SW sau when launch to đối chiếu
                sw_webrtc = (sw.get('webrtc_policy') or '').strip()
                sw_proxy = (sw.get('raw_proxy') or '').strip()
                self._append_app_log(
                    profile_path,
                    f"Chrome launched successfully | PROFILE={profile_name} | UA={ua or 'N/A'} | LANG={lang or 'N/A'} | WEbrtc={sw_webrtc or 'default'} | PROXY={'set' if sw_proxy else 'none'}"
                )
            except Exception:
                self._append_app_log(profile_path, "Chrome launched successfully")
            
            # Cập nhật Last Browser and Last Version sau when launch thành công
            try:
                # Lấy browser version from settings
                browser_version = ''
                try:
                    settings_file = os.path.join(profile_path, 'profile_settings.json')
                    if os.path.exists(settings_file):
                        import json as _json
                        with open(settings_file, 'r', encoding='utf-8') as sf:
                            data = _json.load(sf)
                            browser_version = (data.get('software', {}).get('browser_version') or '').strip()
                except Exception:
                    pass
                
                if browser_version:
                    # Cập nhật Last Browser file -> ghi full path GPM if have
                    last_browser_path = os.path.join(profile_path, 'Last Browser')
                    gpm_exe = self._gpm_chrome_path_for_version(browser_version)
                    try:
                        if gpm_exe and os.path.exists(gpm_exe):
                            with open(last_browser_path, 'w', encoding='utf-8') as f:
                                f.write(gpm_exe)
                        else:
                            with open(last_browser_path, 'w', encoding='utf-8') as f:
                                f.write(f"browser_chromium_core_{browser_version.split('.')[0]}")
                    except Exception:
                        with open(last_browser_path, 'w', encoding='utf-8') as f:
                            f.write(f"browser_chromium_core_{browser_version.split('.')[0]}")
                    
                    # Cập nhật Last Version file
                    last_version_path = os.path.join(profile_path, 'Last Version')
                    with open(last_version_path, 'w', encoding='utf-8') as f:
                        f.write(browser_version)
                    
                    self._append_app_log(profile_path, f"Updated Last Browser: browser_chromium_core_{browser_version.split('.')[0]}, Last Version: {browser_version}")
            except Exception as e:
                self._append_app_log(profile_path, f"Failed to update Last Browser/Version: {e}")
            
            # Tuỳ chọn: tự động tail log if bật biến môi trường
            try:
                import os as _os
                if _os.environ.get('SHOW_CHROME_LOG_ON_LAUNCH', '').lower() in ('1','true','yes'):
                    tail = self.read_chrome_log(profile_name, tail_lines=120)
                    print("\n===== chrome.log (tail) =====\n" + tail + "\n============================\n")
            except Exception:
                pass
            return True, driver
            
        except Exception as e:
            print(f"[ERROR] [LAUNCH] Error: {str(e)}")
            try:
                self._append_app_log(profile_path, f"Launch error: {str(e)}")
            except Exception:
                pass
            return False, f"Error when start Chrome: {str(e)}"

    def _apply_stealth_driver(self, driver, lang: str = 'en-US', profile_path: str = None):
        """Tiêm the script stealth to giảm detect tự động hóa.
        - Ẩn navigator.webdriver
        - Thêm navigator.plugins & navigator.languages
        - Thêm window.chrome
        - Bẻ permissions for notifications (tránh lỗi ChromeDriver)
        - Che one số fingerprint cơ bản: WebGL vendor/renderer, canvas noise nhẹ
        """
        try:
            script = r"""
Object.defineProperty(navigator, 'webdriver', { get: () => undefined });

// window.chrome placeholder
if (!window.chrome) {
  Object.defineProperty(window, 'chrome', { value: { runtime: {} } });
}

// languages
try {
  Object.defineProperty(navigator, 'languages', { get: () => ['""" + (lang or 'en-US') + r"""', 'en'] });
} catch(e) {}

// plugins
try {
  Object.defineProperty(navigator, 'plugins', { get: () => [1,2,3,4,5] });
} catch(e) {}

// permissions
const origQuery = window.navigator.permissions && window.navigator.permissions.query;
if (origQuery) {
  window.navigator.permissions.query = (parameters) => (
    parameters && parameters.name === 'notifications' ?
      Promise.resolve({ state: Notification.permission }) : origQuery(parameters)
  );
}

// WebGL vendor/renderer spoof with randomization
try {
  const getParameter = WebGLRenderingContext.prototype.getParameter;
  const vendors = ['Google Inc.', 'NVIDIA Corporation', 'AMD', 'Intel Inc.', 'Microsoft Corporation'];
  const renderers = [
    'ANGLE (Intel(R) HD Graphics 620 Direct3D11 vs_5_0 ps_5_0)',
    'ANGLE (NVIDIA GeForce GTX 1060 Direct3D11 vs_5_0 ps_5_0)',
    'ANGLE (AMD Radeon RX 580 Direct3D11 vs_5_0 ps_5_0)',
    'ANGLE (Intel(R) UHD Graphics 630 Direct3D11 vs_5_0 ps_5_0)',
    'ANGLE (Microsoft Basic Render Driver Direct3D11 vs_5_0 ps_5_0)'
  ];
  const randomVendor = vendors[Math.floor(Math.random() * vendors.length)];
  const randomRenderer = renderers[Math.floor(Math.random() * renderers.length)];
  
  WebGLRenderingContext.prototype.getParameter = function(parameter){
    if (parameter === 37445) return randomVendor; // UNMASKED_VENDOR_WEBGL
    if (parameter === 37446) return randomRenderer; // UNMASKED_RENDERER_WEBGL
    return getParameter.apply(this, arguments);
  };
} catch(e) {}

// Thêm randomization for hardware concurrency and device memory
try {
  Object.defineProperty(navigator, 'hardwareConcurrency', { 
    get: () => Math.floor(Math.random() * 8) + 2 
  });
} catch(e) {}

try {
  Object.defineProperty(navigator, 'deviceMemory', { 
    get: () => Math.pow(2, Math.floor(Math.random() * 4) + 2) 
  });
} catch(e) {}

// Spoof screen properties with randomization
try {
  const screenSizes = [
    {w: 1920, h: 1080, aw: 1920, ah: 1040},
    {w: 1366, h: 768, aw: 1366, ah: 728},
    {w: 1440, h: 900, aw: 1440, ah: 860},
    {w: 1536, h: 864, aw: 1536, ah: 824},
    {w: 1600, h: 900, aw: 1600, ah: 860}
  ];
  const randomScreen = screenSizes[Math.floor(Math.random() * screenSizes.length)];
  
  Object.defineProperty(screen, 'availWidth', { get: () => randomScreen.aw });
  Object.defineProperty(screen, 'availHeight', { get: () => randomScreen.ah });
  Object.defineProperty(screen, 'width', { get: () => randomScreen.w });
  Object.defineProperty(screen, 'height', { get: () => randomScreen.h });
  Object.defineProperty(screen, 'colorDepth', { get: () => 24 });
  Object.defineProperty(screen, 'pixelDepth', { get: () => 24 });
} catch(e) {}

// Spoof timezone
try {
  const timezones = [
    'America/New_York', 'America/Los_Angeles', 'America/Chicago', 'America/Denver',
    'Europe/London', 'Europe/Paris', 'Europe/Berlin', 'Europe/Rome',
    'Asia/Tokyo', 'Asia/Shanghai', 'Asia/Seoul', 'Asia/Singapore',
    'Australia/Sydney', 'Australia/Melbourne', 'Canada/Toronto', 'Canada/Vancouver'
  ];
  const randomTz = timezones[Math.floor(Math.random() * timezones.length)];
  
  Object.defineProperty(Intl.DateTimeFormat.prototype, 'resolvedOptions', {
    value: function() {
      const original = Intl.DateTimeFormat.prototype.resolvedOptions.call(this);
      return { ...original, timeZone: randomTz };
    }
  });
} catch(e) {}

// Spoof language with randomization
try {
  const languages = [
    ['en-US', 'en'],
    ['en-GB', 'en'],
    ['en-CA', 'en'],
    ['en-AU', 'en'],
    ['de-DE', 'de'],
    ['fr-FR', 'fr'],
    ['es-ES', 'es'],
    ['it-IT', 'it'],
    ['pt-BR', 'pt'],
    ['ja-JP', 'ja'],
    ['ko-KR', 'ko'],
    ['zh-CN', 'zh'],
    ['zh-TW', 'zh']
  ];
  const randomLang = languages[Math.floor(Math.random() * languages.length)];
  
  Object.defineProperty(navigator, 'language', { get: () => randomLang[0] });
  Object.defineProperty(navigator, 'languages', { get: () => randomLang });
} catch(e) {}

// Canvas noise nhẹ
try {
  const toDataURL = HTMLCanvasElement.prototype.toDataURL;
  HTMLCanvasElement.prototype.toDataURL = function(){
    const ctx = this.getContext('2d');
    if (ctx) {
      const w = Math.min(10, this.width||0), h = Math.min(10, this.height||0);
      if (w && h) {
        const imgData = ctx.getImageData(0,0,w,h);
        for (let i=0; i<imgData.data.length; i+=7) imgData.data[i] ^= 0x11;
        ctx.putImageData(imgData,0,0);
      }
    }
    return toDataURL.apply(this, arguments);
  };
} catch(e) {}
            """
            driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', { 'source': script })
        except Exception as e:
            print(f"[WARNING] [STEALTH] Error when addScriptOnNewDocument: {e}")

        # Inject script to ẩn hoàn toàn webdriver property
        try:
            webdriver_hide_script = """
            // Ẩn hoàn toàn webdriver property
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
            
            // Ẩn automation indicators
                delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
                delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
                delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
            
            // Ẩn selenium indicators
            delete window.$cdc_asdjflasutopfhvcZLmcfl_;
            delete window.$chrome_asyncScriptInfo;
            delete window.__$webdriverAsyncExecutor;
            
            // Ẩn automation extension
            if (window.chrome && window.chrome.runtime && window.chrome.runtime.onConnect) {
                delete window.chrome.runtime.onConnect;
            }
            
            // Override getParameter to ẩn automation
            const getParameter = WebGLRenderingContext.prototype.getParameter;
            WebGLRenderingContext.prototype.getParameter = function(parameter) {
                if (parameter === 37445) {
                    return 'Intel Inc.';
                }
                if (parameter === 37446) {
                    return 'Intel(R) HD Graphics 620';
                }
                return getParameter.call(this, parameter);
            };
            
            // Ẩn automation in console
            const originalLog = console.log;
            console.log = function(...args) {
                if (args.some(arg => typeof arg === 'string' && arg.includes('webdriver'))) {
                    return;
                }
                return originalLog.apply(this, args);
            };
            """
            driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', { 'source': webdriver_hide_script })
        except Exception as e:
            print(f"[WARNING] [STEALTH] Error when inject webdriver hide script: {e}")

        # Inject randomized hardware fingerprints (WebGL vendor/renderer, CPU cores, deviceMemory)
        try:
            hw = {}
            if profile_path:
                try:
                    import json as _json
                    with open(os.path.join(profile_path, 'profile_settings.json'), 'r', encoding='utf-8') as sf:
                        ps = _json.load(sf)
                        hw = (ps.get('hardware') or {})
                except Exception:
                    hw = {}

            import random as _rand
            cpu_cores = int(str(hw.get('cpu_cores') or 0) or 0) or _rand.forice([4, 6, 8, 12])
            device_memory = int(str(hw.get('device_memory') or 0) or 0) or _rand.forice([8, 16, 32])
            webgl_vendor = (hw.get('webgl_vendor') or '').strip()
            webgl_renderer = (hw.get('webgl_renderer') or '').strip()
            if not webgl_vendor or not webgl_renderer:
                pairs = [
                    # NVIDIA Graphics
                    ("Google Inc. (NVIDIA)", "ANGLE (NVIDIA, NVIDIA GeForce RTX 3080 Ti Direct3D11 vs_5_0 ps_5_0, D3D11)"),
                    ("Google Inc. (NVIDIA)", "ANGLE (NVIDIA, NVIDIA GeForce GTX 1060 Direct3D11 vs_5_0 ps_5_0, D3D11)"),
                    ("Google Inc. (NVIDIA)", "ANGLE (NVIDIA, NVIDIA GeForce RTX 3060 Direct3D11 vs_5_0 ps_5_0, D3D11)"),
                    # Intel Graphics - UHD Series
                    ("Google Inc. (Intel)", "ANGLE (Intel, Intel(R) UHD Graphics 620 (0x00005917) Direct3D11 vs_5_0 ps_5_0, D3D11)"),
                    ("Google Inc. (Intel)", "ANGLE (Intel, Intel(R) UHD Graphics 630 (0x00005917) Direct3D11 vs_5_0 ps_5_0, D3D11)"),
                    ("Google Inc. (Intel)", "ANGLE (Intel, Intel(R) UHD Graphics 620 Direct3D11 vs_5_0 ps_5_0, D3D11)"),
                    ("Google Inc. (Intel)", "ANGLE (Intel, Intel(R) UHD Graphics 630 Direct3D11 vs_5_0 ps_5_0, D3D11)"),
                    # Intel Graphics - HD Series
                    ("Google Inc. (Intel)", "ANGLE (Intel, Intel(R) HD Graphics 530 Direct3D11 vs_5_0 ps_5_0, D3D11)"),
                    ("Google Inc. (Intel)", "ANGLE (Intel, Intel(R) HD Graphics 520 Direct3D11 vs_5_0 ps_5_0, D3D11)"),
                    ("Google Inc. (Intel)", "ANGLE (Intel, Intel(R) HD Graphics 4600 Direct3D11 vs_5_0 ps_5_0, D3D11)"),
                    ("Google Inc. (Intel)", "ANGLE (Intel, Intel(R) HD Graphics 4000 Direct3D9Ex vs_3_0 ps_3_0, igdumdim64.dll-10.18.10.3345)"),
                    # Intel Graphics - Iris Series
                    ("Google Inc. (Intel)", "ANGLE (Intel, Intel(R) Iris(R) Xe Graphics Direct3D11 vs_5_0 ps_5_0, D3D11)"),
                    ("Google Inc. (Intel)", "ANGLE (Intel, Intel(R) HD Graphics Family Direct3D11 vs_5_0 ps_5_0, D3D11)"),
                    # AMD Graphics
                    ("Google Inc. (AMD)", "ANGLE (AMD, AMD Radeon RX 580 Direct3D11 vs_5_0 ps_5_0, D3D11)"),
                    ("Google Inc. (AMD)", "ANGLE (AMD, AMD Radeon RX 6600 Direct3D11 vs_5_0 ps_5_0, D3D11)"),
                ]
                webgl_vendor, webgl_renderer = _rand.forice(pairs)

            hw_script = f"""
            try {{
              Object.defineProperty(navigator, 'hardwareConcurrency', {{ get: () => {cpu_cores} }});
            }} catch(e) {{}}
            try {{
              Object.defineProperty(navigator, 'deviceMemory', {{ get: () => {device_memory} }});
            }} catch(e) {{}}
            try {{
              const getParameterProxy = WebGLRenderingContext.prototype.getParameter;
              WebGLRenderingContext.prototype.getParameter = function(parameter) {{
                const UNMASKED_VENDOR_WEBGL = 0x9245; // ext.UNMASKED_VENDOR_WEBGL
                const UNMASKED_RENDERER_WEBGL = 0x9246; // ext.UNMASKED_RENDERER_WEBGL
                if (parameter === UNMASKED_VENDOR_WEBGL) return '{webgl_vendor}';
                if (parameter === UNMASKED_RENDERER_WEBGL) return '{webgl_renderer}';
                return getParameterProxy.apply(this, [parameter]);
              }};
              if (window.WebGL2RenderingContext && WebGL2RenderingContext.prototype.getParameter) {{
                const getParameterProxy2 = WebGL2RenderingContext.prototype.getParameter;
                WebGL2RenderingContext.prototype.getParameter = function(parameter) {{
                  const UNMASKED_VENDOR_WEBGL = 0x9245;
                  const UNMASKED_RENDERER_WEBGL = 0x9246;
                  if (parameter === UNMASKED_VENDOR_WEBGL) return '{webgl_vendor}';
                  if (parameter === UNMASKED_RENDERER_WEBGL) return '{webgl_renderer}';
                  return getParameterProxy2.apply(this, [parameter]);
                }};
              }}
            }} catch(e) {{}}
            """
            driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', { 'source': hw_script })
        except Exception as e:
            print(f"[WARNING] [STEALTH] Error when inject hardware spoof: {e}")

    def _ensure_extensions_allowed(self, chrome_options: "Options") -> None:
        """Remove flags that disable extensions and add enable flag.

        Some optimized modes add '--disable-extensions'. We need extensions for
        our tiny title prefix extension and for any user extensions.
        """
        args_attr = None
        # Selenium Options keeps args on 'arguments' (public) or '_arguments' (internal)
        if hasattr(chrome_options, 'arguments'):
            args_attr = 'arguments'
        elif hasattr(chrome_options, '_arguments'):
            args_attr = '_arguments'
        if not args_attr:
            return
        args = getattr(chrome_options, args_attr, []) or []
        filtered = []
        for a in list(args):
            la = a.lower()
            if la.startswith('--disable-extensions'):
                continue
            filtered.append(a)
        # Update args
        if args_attr:
            # set back the filtered list
            try:
                setattr(chrome_options, args_attr, filtered)
            except Exception:
                pass
        # Ensure explicit enable - Chỉ thêm flags cần thiết nhất
        # try:
        #     chrome_options.add_argument('--enable-extensions')
        # except Exception:
        #     pass

    def _ensure_profile_title_extension(self, profile_name: str) -> str:
        """Create a minimal MV3 extension that prefixes document.title with the profile name.

        The extension is generated in a deterministic folder under ./extensions/ProfileTitle_<sanitized>.
        Returns absolute extension directory path.
        """
        import re
        base_dir = os.path.join(os.getcwd(), "extensions")
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)
        safe_name = re.sub(r"[^A-Za-z0-9_\-]", "_", str(profile_name))
        ext_dir = os.path.join(base_dir, f"ProfileTitle_{safe_name}")
        assets_dir = ext_dir
        try:
            if not os.path.exists(assets_dir):
                os.makedirs(assets_dir)
            # manifest.json (MV3)
            manifest_path = os.path.join(assets_dir, "manifest.json")
            manifest = {
                "manifest_version": 3,
                "name": f"ProfileTitle: {profile_name}",
                "version": "1.0.0",
                "description": "Prefix page title with profile name for easy identification.",
                "content_scripts": [
                    {
                        "matches": ["<all_urls>"],
                        "js": ["profile_title.js"],
                        "run_at": "document_end"
                    }
                ],
                "permissions": []
            }
            import json as _json
            with open(manifest_path, "w", encoding="utf-8") as f:
                _json.dump(manifest, f, ensure_ascii=False, indent=2)

            # content script with inlined profile name
            js_path = os.path.join(assets_dir, "profile_title.js")
            # Sử dụng profile name thực tế
            display_name = profile_name
            
            script = (
                "(function(){\n"
                "  const profileName = " + _json.dumps(str(profile_name)) + ";\n"
                "  const displayName = " + _json.dumps(display_name) + ";\n"
                "  const prefix = '[' + displayName + '] ';\n"
                "  \n"
                "  // Function to update title\n"
                "  const updateTitle = () => {\n"
                "    try {\n"
                "      const currentTitle = document.title || '';\n"
                "      if (!currentTitle.startsWith(prefix)) {\n"
                "        document.title = prefix + currentTitle;\n"
                "      }\n"
                "    } catch(e) {}\n"
                "  };\n"
                "  \n"
                "  // Function to update Google search bar\n"
                "  const updateGoogleSearch = () => {\n"
                "    try {\n"
                "      const searchInputs = document.querySelectorAll('input[name=\"q\"], input[aria-label*=\"Search\"], input[placeholder*=\"Search\"], input[placeholder*=\"Tìm\"]');\n"
                "      searchInputs.forEach(input => {\n"
                "        if (input.placeholder && !input.placeholder.includes(displayName)) {\n"
                "          input.placeholder = displayName + ' | ' + input.placeholder;\n"
                "        }\n"
                "      });\n"
                "    } catch(e) {}\n"
                "  };\n"
                "  \n"
                "  // Function to add profile indicator to page\n"
                "  const addProfileIndicator = () => {\n"
                "    try {\n"
                "      // Remove existing indicator\n"
                "      const existing = document.getElementById('gpm-profile-indicator');\n"
                "      if (existing) existing.remove();\n"
                "      \n"
                "      // Create new indicator\n"
                "      const indicator = document.createElement('div');\n"
                "      indicator.id = 'gpm-profile-indicator';\n"
                "      indicator.style.cssText = 'position:fixed;top:20px;right:20px;background:linear-gradient(45deg, #4285f4, #34a853);color:white;padding:8px 15px;border-radius:8px;font-family:Arial,sans-serif;font-size:14px;font-weight:bold;z-index:999999;box-shadow:0 4px 12px rgba(0,0,0,0.3);border:2px solid #fff;';\n"
                "      indicator.textContent = '[TOOL] ' + displayName;\n"
                "      document.body.appendChild(indicator);\n"
                "      \n"
                "      // Add animation\n"
                "      indicator.style.animation = 'slideIn 0.5s ease-out';\n"
                "      const style = document.createElement('style');\n"
                "      style.textContent = '@keyframes slideIn { from { transform: translateX(100%); opacity: 0; } to { transform: translateX(0); opacity: 1; } }';\n"
                "      document.head.appendChild(style);\n"
                "    } catch(e) {}\n"
                "  };\n"
                "  \n"
                "  // Function to update page content\n"
                "  const updatePageContent = () => {\n"
                "    updateTitle();\n"
                "    updateGoogleSearch();\n"
                "    addProfileIndicator();\n"
                "  };\n"
                "  \n"
                "  // Initial setup\n"
                "  updatePageContent();\n"
                "  \n"
                "  // Wait for page load then update\n"
                "  if (document.readyState === 'loading') {\n"
                "    document.addEventListener('DOMContentLoaded', () => {\n"
                "      setTimeout(updatePageContent, 500);\n"
                "      setTimeout(updatePageContent, 2000);\n"
                "    });\n"
                "  } else {\n"
                "    setTimeout(updatePageContent, 500);\n"
                "    setTimeout(updatePageContent, 2000);\n"
                "  }\n"
                "  \n"
                "  // Monitor all changes\n"
                "  const observer = new MutationObserver(() => {\n"
                "    setTimeout(updatePageContent, 100);\n"
                "  });\n"
                "  \n"
                "  try {\n"
                "    observer.observe(document.documentElement, {childList:true, subtree:true, characterData:true});\n"
                "  } catch(e) {}\n"
                "  \n"
                "  // Also monitor window events\n"
                "  window.addEventListener('load', () => {\n"
                "    setTimeout(updatePageContent, 1000);\n"
                "  });\n"
                "  \n"
                "  // Periodic update every 5 seconds\n"
                "  setInterval(updatePageContent, 5000);\n"
                "})();\n"
            )
            with open(js_path, "w", encoding="utf-8") as f:
                f.write(script)

            return ext_dir
        except Exception as e:
            print(f"[WARNING] [PROFILE-TITLE] Failed to create extension: {e}")
            return ext_dir

    def _remove_unsafe_sandbox_flag(self, chrome_options: "Options") -> None:
        """Loại bỏ cờ --no-sandbox khỏi danh sách arguments if have."""
        try:
            args_attr = None
            if hasattr(chrome_options, 'arguments'):
                args_attr = 'arguments'
            elif hasattr(chrome_options, '_arguments'):
                args_attr = '_arguments'
            if not args_attr:
                return
            args = getattr(chrome_options, args_attr, []) or []
            filtered = [a for a in list(args) if a.strip().lower() != '--no-sandbox']
            setattr(chrome_options, args_attr, filtered)
        except Exception:
            pass
    
    def diagnose_profile(self, profile_name: str, test_query: str = "tiktok", warmup_seconds: int = 8):
        """Chẩn đoán profile: thu thập log trình duyệt, check IPv4/IPv6, try truy cập Google.
        Tạo báo cáo JSON tại ./diagnostics/<profile>_<timestamp>.json
        """
        try:
            os.makedirs("diagnostics", exist_ok=True)
            profile_name = str(profile_name)
            profile_path = os.path.join(self.profiles_dir, profile_name)
            if not os.path.exists(profile_path):
                return False, f"Profile '{profile_name}' không tồn tại"

            # Kill chrome trước when chẩn đoán
            try:
                self._kill_chrome_processes()
            except Exception:
                pass

            chrome_options = Options()
            chrome_options.add_argument(f"--user-data-dir={profile_path}")
            # Removed to match GPM command format and avoid automation fingerprints
            # chrome_options.add_argument("--no-first-run")
            chrome_options.add_argument("--no-default-browser-check")
            chrome_options.add_argument("--disable-ipv6")
            chrome_options.add_argument("--disable-quic")
            chrome_options.add_argument("--disable-dns-prefetch")
            chrome_options.add_argument("--no-pings")
            chrome_options.add_argument("--disable-notifications")
            chrome_options.add_argument("--disable-features=UseGCMChannel,PushMessaging,NotificationTriggers,UseDnsHttpsSvcb,InvalidationService,InvalidationServiceInvalidationHandler,BackgroundSync,BackgroundFetch")
            # Bật logging
            try:
                chrome_options.set_capability('goog:loggingPrefs', { 'performance': 'ALL', 'browser': 'ALL' })
            except Exception:
                pass

            # Tối ưu hóa command line bằng function fix
            try:
                from fix_chrome_command import fix_chrome_command, create_rules_from_gpm_config
                
                # Tạo command line hiện tại
                args_attr = None
                if hasattr(chrome_options, 'arguments'):
                    args_attr = 'arguments'
                elif hasattr(chrome_options, '_arguments'):
                    args_attr = '_arguments'
                
                if args_attr:
                    args = list(getattr(chrome_options, args_attr) or [])
                    # Chủ động gỡ 3 cờ autobot trước khi fix lần cuối
                    args = [a for a in args if not (
                        a.startswith('--log-level') or
                        a == '--no-first-run' or
                        a.startswith('--remote-debugging-port')
                    )]
                    current_command = 'chrome.exe ' + ' '.join([str(arg) for arg in args])
                    
                    # Tạo rules từ GPM config
                    rules = create_rules_from_gpm_config(gpm_config)
                    rules['user_data_dir'] = profile_path
                    
                    # Fix command line
                    fixed_command = fix_chrome_command(current_command, rules)
                    
                    if not fixed_command.startswith('ERROR:'):
                        # Parse fixed command và cập nhật chrome_options
                        import shlex
                        fixed_parts = shlex.split(fixed_command)
                        if len(fixed_parts) > 1:
                            fixed_args = fixed_parts[1:]  # Bỏ executable path
                            chrome_options._arguments = fixed_args
                            print(f"[COMMAND-FIX] Fixed diagnose command line: {len(fixed_args)} flags")
                else:
                    print(f"[COMMAND-FIX] Error fixing diagnose command line: {str(e)}")
                    
            except Exception as e:
                print(f"[COMMAND-FIX] Error fixing diagnose command line: {str(e)}")

            driver = self._launch_chrome_with_fallback(chrome_options, profile_path, hidden=True)
            if not driver:
                return False, "Chrome không thể start (diagnostics)"

            report = {
                'profile': profile_name,
                'started_at': datetime.utcnow().isoformat() + 'Z',
                'ipv4': None,
                'ipv6': None,
                'google_search_url': None,
                'google_sorry_detected': False,
                'browser_log_counts': {},
                'gcm_indicators': {
                    'deprecated_endpoint': 0,
                    'quota_exceeded': 0
                }
            }

            # IPv4/IPv6 leak checks
            def _fetch_text(url: str, timeout_sec: int = 12):
                try:
                    driver.get(url)
                    time.sleep(0.6)
                    return (driver.find_element('tag name', 'body').text or '').strip()
                except Exception:
                    return None

            report['ipv4'] = _fetch_text('https://ipv4.icanhazip.com')
            report['ipv6'] = _fetch_text('https://ipv6.icanhazip.com')

            # Warmup
            try:
                time.sleep(max(0, int(warmup_seconds)))
            except Exception:
                pass

            # Probe search engine (thay vì Google to tránh captcha)
            try:
                from urllib.parse import urlencode
                import random
                q = urlencode({'q': test_query})
                # Sử dụng DuckDuckGo thay vì Google to tránh captcha
                url = f"https://duckduckgo.com/?{q}"
                driver.get(url)
                time.sleep(1.5)
                cur = driver.current_url
                report['google_search_url'] = cur  # Giữ tên field to tương thích
                if 'duckduckgo.com' in (cur or '').lower():
                    report['google_sorry_detected'] = False  # DuckDuckGo không have captcha
            except Exception:
                pass

            # Collect logs
            def _safe_get_log(kind: str):
                try:
                    return driver.get_log(kind)
                except Exception:
                    return []

            browser_logs = _safe_get_log('browser')
            perf_logs = _safe_get_log('performance')
            report['browser_log_counts'] = {
                'browser': len(browser_logs),
                'performance': len(perf_logs)
            }
            # Scan quick indicators
            def _scan(lines):
                dep = 0
                quota = 0
                for it in lines:
                    try:
                        msg = it.get('message') or it.get('text') or ''
                    except Exception:
                        msg = str(it)
                    ml = (msg or '').lower()
                    if 'deprecated_endpoint' in ml:
                        dep += 1
                    if 'quota_exceeded' in ml:
                        quota += 1
                return dep, quota
            d1, q1 = _scan(browser_logs)
            d2, q2 = _scan(perf_logs)
            report['gcm_indicators']['deprecated_endpoint'] = d1 + d2
            report['gcm_indicators']['quota_exceeded'] = q1 + q2

            # Persist report
            ts = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
            out_path = os.path.join('diagnostics', f"{profile_name}_{ts}.json")
            try:
                with open(out_path, 'w', encoding='utf-8') as f:
                    json.dump(report, f, ensure_ascii=False, indent=2)
            except Exception as e:
                print(f"[WARNING] [DIAG] No thể save báo cáo: {e}")

            try:
                driver.quit()
            except Exception:
                pass

            return True, out_path
        except Exception as e:
            return False, f"Error chẩn đoán: {e}"

    def prune_profile_to_gpm_baseline(self, profile_name: str):
        """Xoá file/thư mục thừa to optimize profile giống baseline of GPM.
        Giữ lại the marker quan trọng and cấu hình cần thiết.
        """
        try:
            profile_name = str(profile_name)
            profile_path = os.path.join(self.profiles_dir, profile_name)
            if not os.path.exists(profile_path):
                return False, f"Profile '{profile_name}' không tồn tại"

            # Danh sách file cần giữ (if tồn tại)
            keep_files = {
                os.path.join(profile_path, 'Local State'),
                os.path.join(profile_path, 'First Run'),
                os.path.join(profile_path, 'Last Version'),
                os.path.join(profile_path, 'Last Browser'),
                os.path.join(profile_path, 'Variations'),
                os.path.join(profile_path, 'first_party_sets.db'),
                os.path.join(profile_path, 'first_party_sets.db-journal'),
            }
            # Thư mục cần giữ
            keep_dirs = {
                os.path.join(profile_path, 'Default'),
                os.path.join(profile_path, 'GPMSoft'),
                os.path.join(profile_path, 'GPMBrowserExtenions'),
                os.path.join(profile_path, 'Safe Browsing'),
                os.path.join(profile_path, 'SSLErrorAssistant'),
            }
            # Các thư mục rác/cached nên xoá if have
            remove_dirs = [
                'Accounts','AmountExtractionHeuristicRegexes','AutofillStates','AutofillStrikeDatabase','blob_storage',
                'BrowserMetrics','BudgetDatabase','CertificateRevocation','chrome_cart_db','ClientCertificates',
                'Collaboration','commerce_subscription_db','component_crx_cache','Crashpad','DataSharing',
                'DawnGraphiteCache','DawnWebGPUCache','Discount Service','DNR Extension Rules','Download Service',
                'Extension Rules','Extension Scripts','Extension State','Extensions','Feature Engagement Tracker',
                'GraphiteDawnCache','GrShaderCache','GCM Store','IndexedDB','JumpListIconsMostVisited',
                'JumpListIconsRecentClosed','Local Extension Settings','Local Storage','MediaFoundationWidevineCdm',
                'Network','optimization_guide_hint_cache_store','OptimizationHints','OriginTrials','parcel_tracking_db',
                'PersistentOriginTrials','Platform Notifications','Policy','PrivacySandboxAttestationsPreloaded',
                'ProbabilisticRevealTokenRegistry','Search Logos','segmentation_platform','Segmentation Platform',
                'Service Worker','Session Storage','Sessions','ShaderCache','shared_proto_db','Shared Dictionary',
                'Site Characteristics Database','Storage','Subresource Filter','Sync Data','Sync Extension Settings',
                'TrustTokenKeyCommitments','VideoDecodeStats','WasmTtsEngine','Web Applications','WebStorage',
                'webrtc_event_logs','ZxcvbnData'
            ]
            # Các file rác nên xoá if have
            remove_files = [
                'chrome_debug.log','DevToolsActivePort','CrashpadMetrics-active.pma','LOG','LOG.old',
                'Network Action Predictor','Network Action Predictor-journal','Top Sites','Top Sites-journal',
                'History','History-journal','Favicons','Favicons-journal','Shortcuts','Shortcuts-journal',
                'Google Profile.ico','Google Profile Picture.png','DownloadMetadata','passkey_enclave_state',
                'Login Data','Login Data-journal','Login Data For Account','Login Data For Account-journal',
                'Account Web Data','Account Web Data-journal','BrowsingTopicsState','BrowsingTopicsState-journal',
                'BrowsingTopicsSiteData','BrowsingTopicsSiteData-journal','DIPS','DIPS-journal','trusted_vault.pb'
            ]

            # Xoá thư mục rác
            for d in remove_dirs:
                p = os.path.join(profile_path, d)
                if os.path.isdir(p) and p not in keep_dirs:
                    try:
                        shutil.rmtree(p, ignore_errors=True)
                        # print(f"[CLEANUP] Removed dir: {p}")
                    except Exception:
                        pass

            # Xoá file rác
            for f in remove_files:
                p = os.path.join(profile_path, f)
                if os.path.exists(p) and p not in keep_files:
                    try:
                        os.remove(p)
                        # print(f"[CLEANUP] Removed file: {p}")
                    except Exception:
                        pass

            # No create thêm cấu trúc GPM phụ to giữ tối giản như GPM (chỉ Default/)

            return True, f"Done optimize profile '{profile_name}' về baseline GPM"
        except Exception as e:
            return False, f"Error when optimize profile: {e}"
    
    def _perform_auto_login(self, driver, login_data, start_url=None):
        """Thực hiện login tự động for many trang web"""
        try:
            print(f"[SECURITY] [LOGIN] Bắt đầu auto-login process...")
            
            # Kiểm tra xem have phải string format không (TikTok/Standard)
            if isinstance(login_data, str):
                print(f"[INPUT] [LOGIN] Parse string format (username|password)...")
                # Parse TikTok/Standard format
                parsed_data = self._parse_tiktok_account_data(login_data)
                if parsed_data:
                    login_data = parsed_data
                    print(f"[SUCCESS] [LOGIN] Done parse format: {login_data.get('username', 'N/A')}")
                else:
                    print(f"[ERROR] [LOGIN] No thể parse string format")
                    return False
            
            # Kiểm tra và giải captcha nếu có
            if CAPTCHA_SOLVER_AVAILABLE:
                try:
                    print(f"🔍 [CAPTCHA] [STEP 1/5] Kiểm tra captcha...")
                    
                    # Load OMOcaptcha API key từ config
                    omocaptcha_api_key = None
                    try:
                        if hasattr(self, 'config') and self.config.has_section('CAPTCHA'):
                            omocaptcha_api_key = self.config.get('CAPTCHA', 'omocaptcha_api_key', fallback=None)
                            if omocaptcha_api_key and omocaptcha_api_key != 'YOUR_OMOCAPTCHA_API_KEY_HERE':
                                print(f"🔑 [CAPTCHA] [STEP 2/5] API Key loaded: {omocaptcha_api_key[:20]}...{omocaptcha_api_key[-10:]}")
                                print(f"✅ [CAPTCHA] [OMO] Sử dụng OMOcaptcha API để giải captcha")
                            else:
                                print(f"⚠️ [CAPTCHA] [OMO] API key chưa được cấu hình hoặc là placeholder")
                                print(f"⚠️ [CAPTCHA] Cần thêm API key hợp lệ vào config.ini")
                                return False
                    except Exception as config_err:
                        print(f"❌ [CAPTCHA] [STEP 2/5] Lỗi load config: {config_err}")
                        import traceback
                        print(f"Traceback: {traceback.format_exc()}")
                    
                    if not omocaptcha_api_key:
                        print(f"❌ [CAPTCHA] Không có API key, skip captcha solving")
                        return False
                    
                    # Khởi tạo captcha solver với OMOcaptcha API key
                    print(f"🔧 [CAPTCHA] [STEP 3/5] Khởi tạo captcha solver...")
                    captcha_solver = TikTokCaptchaSolver(driver, omocaptcha_api_key=omocaptcha_api_key)
                    
                    print(f"🎯 [CAPTCHA] [STEP 4/5] Bắt đầu giải captcha...")
                    success = captcha_solver.solve_captcha()
                    
                    print(f"🎯 [CAPTCHA] [STEP 5/5] Kết quả: {'✅ THÀNH CÔNG' if success else '❌ THẤT BẠI'}")
                    if success:
                        print(f"[SUCCESS] [CAPTCHA] Đã giải captcha thành công!")
                    else:
                        print(f"[INFO] [CAPTCHA] Không phát hiện captcha hoặc đã được giải")
                    
                    return success
                except Exception as e:
                    print(f"❌ [CAPTCHA] Lỗi khi giải captcha: {e}")
                    import traceback
                    print(f"Traceback: {traceback.format_exc()}")
            else:
                print(f"[INFO] [CAPTCHA] Captcha solver không khả dụng (CAPTCHA_SOLVER_AVAILABLE=False)")
            
            # Thử load session data trước
            username_or_email = login_data.get('username', login_data.get('email', ''))
            if username_or_email:
                print(f"[DEBUG] [SESSION] Kiểm tra session data for: {username_or_email}")
                session_data = self._load_session_data(username_or_email)
            if session_data:
                print(f"[SUCCESS] [SESSION] Tìm found session data, try restore...")
                if self._restore_session(driver, session_data):
                    print(f"[SUCCESS] [SESSION] Đăng input thành công bằng session data!")
                    # Lưu marker file ngay cả when restore session thành công
                    print(f"💾 [SESSION] Lưu marker file for profile...")
                    self._save_to_chrome_profile(driver, login_data)
                    return True
                else:
                    print(f"[WARNING] [SESSION] Session data không hợp lệ, login thông thường...")
            
            # Sử dụng start_url if have, if không then dùng login_url
            if start_url:
                login_url = start_url
                print(f"[NETWORK] [LOGIN] Sử dụng start_url: {login_url}")
            else:
                # Sử dụng URL login TikTok cụ thể for email/username
                login_url = login_data.get('login_url', 'https://www.tiktok.com/login/phone-or-email/email')
                print(f"[NETWORK] [LOGIN] Sử dụng login_url: {login_url}")
            
            username = login_data.get('username', '')
            email = login_data.get('email', username)  # Sử dụng username làm email if không have email
            password = login_data.get('password', '')
            twofa = login_data.get('twofa', '')
            
            print(f"👤 [LOGIN] Username: {username}")
            print(f"[EMAIL] [LOGIN] Email: {email}")
            print(f"[PASSWORD] [LOGIN] Password: {'*' * len(password) if password else 'N/A'}")
            print(f"[SECURITY] [LOGIN] 2FA: {twofa if twofa else 'N/A'}")
            print(f"[NETWORK] [LOGIN] Đang execute login tại: {login_url}")
            
            # Điều hướng đến trang login
            print(f"[REFRESH] [LOGIN] Điều hướng đến trang login...")
            driver.get(login_url)
            time.sleep(3)
            
            # Detect trang web and execute login tương ứng
            current_url = driver.current_url.lower()
            print(f"[NETWORK] [LOGIN] Current URL sau when điều hướng: {current_url}")
            login_success = False
            
            if 'tiktok.com' in current_url:
                print(f"[MUSIC] [LOGIN] Detect TikTok, execute login TikTok...")
                login_success = self._login_tiktok(driver, email, password, twofa, login_data)
            elif 'instagram.com' in current_url:
                print(f"📸 [LOGIN] Detect Instagram, execute login Instagram...")
                login_success = self._login_instagram(driver, email, password, twofa)
            elif 'facebook.com' in current_url:
                print(f"👥 [LOGIN] Detect Facebook, execute login Facebook...")
                login_success = self._login_facebook(driver, email, password, twofa)
            elif 'google.com' in current_url or 'youtube.com' in current_url:
                print(f"[DEBUG] [LOGIN] Detect Google/YouTube, execute login Google...")
                login_success = self._login_google(driver, email, password, twofa)
            else:
                print(f"[NETWORK] [LOGIN] Detect trang web khác, sử dụng generic login...")
                # Fallback for the trang web khác
                login_success = self._login_generic(driver, email, password, twofa)
            
            if login_success:
                print(f"[SUCCESS] [LOGIN] Đăng input thành công for: {username}")
                # Lưu session data sau when login thành công
                self._save_session_data(driver, login_data)
                # Lưu ando Chrome profile to tự động login lần sau
                self._save_to_chrome_profile(driver, login_data)
                return True
            else:
                print(f"[ERROR] [LOGIN] Đăng input thất bại for: {username}")
                return False
            
        except Exception as e:
            print(f"[ERROR] [LOGIN] Error login tự động: {str(e)}")
    
    def _save_session_data(self, driver, login_data):
        """Lưu session data sau when login thành công"""
        try:
            print(f"💾 [SESSION] Bắt đầu save session data...")
            
            if not login_data:
                print(f"[WARNING] [SESSION] No have login_data to save")
                return
            
            # Lấy cookies from driver
            cookies = driver.get_cookies()
            print(f"🍪 [SESSION] Done lấy {len(cookies)} cookies")
            
            # Lấy current URL
            current_url = driver.current_url
            print(f"[NETWORK] [SESSION] Current URL: {current_url}")
            
            # Tạo session data
            session_data = {
                'cookies': cookies,
                'url': current_url,
                'timestamp': time.time(),
                'username': login_data.get('username', ''),
                'email': login_data.get('email', ''),
                'user_id': login_data.get('user_id', '')
            }
            
            # Lưu ando file JSON (backup)
            import json
            import os
            
            # Tạo thư mục sessions if chưa have
            sessions_dir = os.path.join(os.path.dirname(__file__), 'sessions')
            if not os.path.exists(sessions_dir):
                os.makedirs(sessions_dir)
                print(f"📁 [SESSION] Done create thư mục sessions")
            
            # Tên file dựa trên username or email
            session_filename = login_data.get('username', login_data.get('email', 'unknown'))
            session_filename = session_filename.replace('@', '_').replace('.', '_')
            session_file = os.path.join(sessions_dir, f"{session_filename}_session.json")
            
            # Lưu session data
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)
            
            print(f"[SUCCESS] [SESSION] Done save session data ando: {session_file}")
            print(f"[STATS] [SESSION] Session data: {len(cookies)} cookies, URL: {current_url}")
            
            # Lưu trực tiếp ando Chrome profile to tự động login lần sau
            print(f"💾 [SESSION] Lưu session trực tiếp ando Chrome profile...")
            self._save_to_chrome_profile(driver, login_data)
            
        except Exception as e:
            print(f"[ERROR] [SESSION] Error when save session data: {e}")
    
    def _save_to_chrome_profile(self, driver, login_data):
        """Lưu session trực tiếp ando Chrome profile"""
        try:
            print(f"💾 [PROFILE] Bắt đầu save session ando Chrome profile...")
            
            # Lấy profile path from driver
            profile_path = driver.capabilities.get('chrome', {}).get('userDataDir', '')
            print(f"[DEBUG] [PROFILE] Driver capabilities: {driver.capabilities}")
            
            if not profile_path:
                print(f"[WARNING] [PROFILE] No thể lấy profile path from driver capabilities")
                # Thử lấy from profile_name if have
                if hasattr(self, 'current_profile_name'):
                    profile_path = os.path.join(self.profiles_dir, self.current_profile_name)
                    print(f"📁 [PROFILE] Sử dụng profile path from current_profile_name: {profile_path}")
                else:
                    print(f"[ERROR] [PROFILE] No thể xác định profile path")
                    return
            
            print(f"📁 [PROFILE] Profile path: {profile_path}")
            
            # Lưu thông tin login ando profile
            username_or_email = login_data.get('username', login_data.get('email', ''))
            if username_or_email:
                # Tạo file marker to đánh dấu profile done login
                marker_file = os.path.join(profile_path, 'tiktok_logged_in.txt')
                print(f"[INPUT] [PROFILE] Tạo marker file: {marker_file}")
                
                with open(marker_file, 'w', encoding='utf-8') as f:
                    f.write(f"username={username_or_email}\n")
                    f.write(f"email={login_data.get('email', '')}\n")
                    f.write(f"timestamp={time.time()}\n")
                    f.write(f"url={driver.current_url}\n")
                
                print(f"[SUCCESS] [PROFILE] Done save marker file: {marker_file}")
                
                # Lưu cookies trực tiếp ando Chrome profile to tự động login
                print(f"🍪 [PROFILE] Lưu cookies trực tiếp ando Chrome profile...")
                self._save_cookies_to_profile(driver, profile_path)
                
                # Lưu thông tin ando config to tắt auto-login lần sau
                if hasattr(self, 'config'):
                    if not self.config.has_section('PROFILE_SESSIONS'):
                        self.config.add_section('PROFILE_SESSIONS')
                    
                    self.config.set('PROFILE_SESSIONS', username_or_email, 'logged_in')
                    
                    # Lưu config
                    with open(self.config_file, 'w', encoding='utf-8') as f:
                        self.config.write(f)
                    
                    print(f"[SUCCESS] [PROFILE] Done cập nhật config to tắt auto-login")
                else:
                    print(f"[WARNING] [PROFILE] No have config object")
            else:
                print(f"[WARNING] [PROFILE] No have username/email to save")
            
            print(f"[SUCCESS] [PROFILE] Session done get save ando Chrome profile!")
            print(f"[INFO] [PROFILE] Lần sau start sẽ tự động login")
            
        except Exception as e:
            print(f"[ERROR] [PROFILE] Error when save ando Chrome profile: {e}")
            import traceback
            print(f"[DEBUG] [PROFILE] Traceback: {traceback.format_exc()}")
    
    def _save_cookies_to_profile(self, driver, profile_path):
        """Lưu cookies trực tiếp ando Chrome profile"""
        try:
            print(f"🍪 [COOKIES] Bắt đầu save cookies ando Chrome profile...")
            
            # Lấy cookies from driver
            cookies = driver.get_cookies()
            print(f"🍪 [COOKIES] Done lấy {len(cookies)} cookies from driver")
            
            # Lưu cookies ando file JSON to Chrome have thể load
            cookies_json_path = os.path.join(profile_path, 'tiktok_cookies.json')
            import json
            with open(cookies_json_path, 'w', encoding='utf-8') as f:
                json.dump(cookies, f, indent=2, ensure_ascii=False)
            
            print(f"[SUCCESS] [COOKIES] Done save cookies ando: {cookies_json_path}")
            
            # Tạo file marker to Chrome biết have cookies done save
            cookies_marker = os.path.join(profile_path, 'cookies_loaded.txt')
            with open(cookies_marker, 'w', encoding='utf-8') as f:
                f.write(f"cookies_count={len(cookies)}\n")
                f.write(f"timestamp={time.time()}\n")
                f.write(f"source=tiktok_login\n")
            
            print(f"[SUCCESS] [COOKIES] Done create cookies marker: {cookies_marker}")
            
        except Exception as e:
            print(f"[ERROR] [COOKIES] Error when save cookies: {e}")
            import traceback
            print(f"[DEBUG] [COOKIES] Traceback: {traceback.format_exc()}")
    
    def _load_cookies_from_profile(self, profile_path, driver):
        """Load cookies from Chrome profile and inject ando driver"""
        try:
            print(f"🍪 [COOKIES] Bắt đầu load cookies from Chrome profile...")
            
            # Kiểm tra file cookies JSON
            cookies_json_path = os.path.join(profile_path, 'tiktok_cookies.json')
            if not os.path.exists(cookies_json_path):
                print(f"[WARNING] [COOKIES] No find found file cookies: {cookies_json_path}")
                return False
            
            # Load cookies from file JSON
            import json
            with open(cookies_json_path, 'r', encoding='utf-8') as f:
                cookies = json.load(f)
            
            print(f"🍪 [COOKIES] Done load {len(cookies)} cookies from file")
            
            # Điều hướng đến trang chủ TikTok trước when inject cookies
            print(f"[NETWORK] [COOKIES] Điều hướng đến trang chủ TikTok...")
            driver.get("https://www.tiktok.com")
            time.sleep(2)
            
            # Inject cookies ando driver
            print(f"🍪 [COOKIES] Đang inject cookies ando driver...")
            for cookie in cookies:
                try:
                    # Tạo cookie copy to không modify original
                    cookie_copy = cookie.copy()
                    
                    # Xử lý domain
                    if 'domain' in cookie_copy:
                        domain = cookie_copy['domain']
                        if domain == 'www.tiktok.com':
                            cookie_copy['domain'] = '.tiktok.com'
                    
                    driver.add_cookie(cookie_copy)
                    print(f"[SUCCESS] [COOKIES] Done inject cookie: {cookie_copy.get('name', 'unknown')}")
                except Exception as e:
                    print(f"[WARNING] [COOKIES] No thể inject cookie {cookie.get('name', 'unknown')}: {e}")
                    continue
            
            # Refresh to áp dụng cookies
            print(f"[REFRESH] [COOKIES] Refresh trang to áp dụng cookies...")
            driver.refresh()
            time.sleep(3)
            
            print(f"[SUCCESS] [COOKIES] Done load and inject cookies thành công!")
            return True
            
        except Exception as e:
            print(f"[ERROR] [COOKIES] Error when load cookies: {e}")
            import traceback
            print(f"[DEBUG] [COOKIES] Traceback: {traceback.format_exc()}")
            return False
    
    def _load_session_data(self, username_or_email):
        """Load session data from file"""
        try:
            import json
            import os
            
            sessions_dir = os.path.join(os.path.dirname(__file__), 'sessions')
            if not os.path.exists(sessions_dir):
                return None
            
            # Tìm file session
            session_filename = username_or_email.replace('@', '_').replace('.', '_')
            session_file = os.path.join(sessions_dir, f"{session_filename}_session.json")
            
            if not os.path.exists(session_file):
                return None
            
            # Load session data
            with open(session_file, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
            
            # Kiểm tra timestamp (session cũ hơn 7 ngày then bỏ qua)
            if time.time() - session_data.get('timestamp', 0) > 7 * 24 * 3600:
                print(f"[WARNING] [SESSION] Session data cũ hơn 7 ngày, bỏ qua")
                return None
            
            print(f"[SUCCESS] [SESSION] Done load session data from: {session_file}")
            return session_data
            
        except Exception as e:
            print(f"[ERROR] [SESSION] Error when load session data: {e}")
            return None
    
    def _restore_session(self, driver, session_data):
        """Restore session from session data"""
        try:
            print(f"[REFRESH] [SESSION] Bắt đầu restore session...")
            
            # Điều hướng đến trang chủ TikTok trước to inject cookies
            print(f"[NETWORK] [SESSION] Điều hướng đến trang chủ TikTok...")
            driver.get("https://www.tiktok.com")
            time.sleep(2)
            
            # Inject cookies
            cookies = session_data.get('cookies', [])
            if cookies:
                print(f"🍪 [SESSION] Đang inject {len(cookies)} cookies...")
                for cookie in cookies:
                    try:
                        # Tạo cookie copy to không modify original
                        cookie_copy = cookie.copy()
                        
                        # Xử lý domain - chỉ delete if domain không hợp lệ
                        if 'domain' in cookie_copy:
                            domain = cookie_copy['domain']
                            if domain.startswith('.'):
                                # Giữ nguyên subdomain cookies
                                pass
                            elif domain == 'www.tiktok.com':
                                # Chuyển www.tiktok.com thành .tiktok.com
                                cookie_copy['domain'] = '.tiktok.com'
                        
                        driver.add_cookie(cookie_copy)
                        print(f"[SUCCESS] [SESSION] Done inject cookie: {cookie_copy.get('name', 'unknown')}")
                    except Exception as e:
                        print(f"[WARNING] [SESSION] No thể inject cookie {cookie.get('name', 'unknown')}: {e}")
                        continue
                
                # Refresh to áp dụng cookies
                print(f"[REFRESH] [SESSION] Refresh trang to áp dụng cookies...")
                driver.refresh()
                time.sleep(3)
                
                # Kiểm tra xem done login chưa
                current_url = driver.current_url
                print(f"[NETWORK] [SESSION] URL sau when restore: {current_url}")
                
                # Điều hướng đến trang For You to check login
                print(f"[REFRESH] [SESSION] Điều hướng đến trang For You to check...")
                driver.get("https://www.tiktok.com/foryou")
                time.sleep(3)
                
                final_url = driver.current_url
                print(f"[NETWORK] [SESSION] URL cuối cùng: {final_url}")
                
                # Kiểm tra dấu hiệu login thành công
                if 'login' not in final_url.lower() and 'foryou' in final_url.lower():
                    print(f"[SUCCESS] [SESSION] Restore session thành công!")
                    return True
                else:
                    print(f"[WARNING] [SESSION] Session không hợp lệ, cần login lại")
                    return False
            else:
                print(f"[WARNING] [SESSION] No have cookies to restore")
                return False
                
        except Exception as e:
            print(f"[ERROR] [SESSION] Error when restore session: {e}")
            return False
    
    def _login_tiktok(self, driver, email, password, twofa, login_data=None):
        """Đăng input TikTok with hỗ trợ session token and email verification"""
        try:
            print(f"[MUSIC] [TIKTOK] Bắt đầu login TikTok...")
            print(f"[EMAIL] [TIKTOK] Email: {email}")
            print(f"👤 [TIKTOK] Username: {login_data.get('username', 'N/A') if login_data else 'N/A'}")
            print(f"[PASSWORD] [TIKTOK] Password: {'*' * len(password) if password else 'N/A'}")
            
            # Bỏ qua session token, chỉ sử dụng username/password
            if login_data and 'session_token' in login_data and login_data['session_token']:
                print(f"[WARNING] [TIKTOK] Phát hiện session token nhưng sẽ bỏ qua, sử dụng username/password...")
                print(f"[SECURITY] [TIKTOK] Session token: {login_data['session_token'][:20]}... (BỎ QUA)")
            
            # Đăng input thông thường with username/password
            print(f"[SECURITY] [TIKTOK] Đăng input TikTok with username/password...")
            
            # Kiểm tra trang hiện tại with error handling
            try:
                current_url = driver.current_url
                print(f"[NETWORK] [TIKTOK] Current URL: {current_url}")
            except Exception as e:
                print(f"[ERROR] [TIKTOK] Chrome session bị disconnect: {e}")
                print(f"[REFRESH] [TIKTOK] Thử refresh trang...")
                try:
                    driver.refresh()
                    time.sleep(3)
                    current_url = driver.current_url
                    print(f"[NETWORK] [TIKTOK] URL sau refresh: {current_url}")
                except Exception as refresh_error:
                    print(f"[ERROR] [TIKTOK] No thể refresh: {refresh_error}")
                    return False
            
            # Sử dụng username if have (TikTok format)
            login_field_value = email
            if login_data and 'username' in login_data and login_data['username']:
                login_field_value = login_data['username']
                print(f"👤 [TIKTOK] Sử dụng username thay vì email: {login_field_value}")
            
            # No click button trước, fill form trước
            print(f"[DEBUG] [TIKTOK] Bỏ qua việc click button, fill form trước...")
            
            # Tìm and fill email/username with retry logic
            print(f"[DEBUG] [TIKTOK] Đang find trường input email/username...")
            print(f"[INPUT] [TIKTOK] Giá trị cần fill: {login_field_value}")
            print(f"[PASSWORD] [TIKTOK] Password: {password[:5]}***")
            
            # Ensure window is focused before finding elements
            try:
                driver.switch_to.window(driver.current_window_handle)
                print("[SUCCESS] [FOCUS] Window focused before fill")
            except Exception as focus_err:
                print(f"[WARNING] [FOCUS] Could not focus: {focus_err}")
            
            email_selectors = [
                "input[data-e2e='login-username']",
                "input[name='username']",
                "input[placeholder*='Email or username']",
                "input[placeholder*='email']",
                "input[placeholder*='username']",
                "input[type='email']",
                "input[type='text']",
                "input[autocomplete='username']"
            ]
            
            print(f"[TARGET] [TIKTOK] Sẽ try {len(email_selectors)} selectors:")
            for i, selector in enumerate(email_selectors):
                print(f"  {i+1}. {selector}")
            
            email_field_found = False
            max_retries = 3
            
            for retry in range(max_retries):
                print(f"[REFRESH] [TIKTOK] Thử lần {retry + 1}/{max_retries}...")
                
                for selector in email_selectors:
                    try:
                        # Kiểm tra session trước
                        driver.current_url  # Test session
                        
                        email_field = driver.find_element("css selector", selector)
                        print(f"[DEBUG] [TIKTOK] Tìm found email element with selector: {selector}")
                        print(f"[VISIBLE] [TIKTOK] Email element displayed: {email_field.is_displayed()}")
                        print(f"[ENABLED] [TIKTOK] Email element enabled: {email_field.is_enabled()}")
                        print(f"[LOCATION] [TIKTOK] Email element location: {email_field.location}")
                        print(f"[SIZE] [TIKTOK] Email element size: {email_field.size}")
                        
                        if email_field.is_displayed() and email_field.is_enabled():
                            print(f"[SUCCESS] [TIKTOK] Email element hợp lệ, start fill...")
                            
                            # Wait for element to be interactable
                            try:
                                from selenium.webdriver.support.ui import WebDriverWait
                                from selenium.webdriver.support import expected_conditions as EC
                                
                                wait = WebDriverWait(driver, 5)
                                wait.until(EC.element_to_be_clickable(email_field))
                                print(f"[SUCCESS] [TIKTOK] Element is clickable")
                            except Exception as wait_err:
                                print(f"[WARNING] [TIKTOK] Wait failed: {wait_err}")
                            
                            # Fill value using JavaScript with detailed logging - NO mouse movement
                            try:
                                print(f"⌨️ [TIKTOK] Đang fill value bằng JavaScript (không di chuyển chuột)")
                                print(f"[DEBUG] [TIKTOK] Target value: '{login_field_value}'")
                                print(f"[DEBUG] [TIKTOK] Element tag: {email_field.tag_name}")
                                print(f"[DEBUG] [TIKTOK] Element type: {email_field.get_attribute('type')}")
                                print(f"[DEBUG] [TIKTOK] Element placeholder: {email_field.get_attribute('placeholder')}")
                                
                                # Check initial value
                                initial_value = email_field.get_attribute('value')
                                print(f"[DEBUG] [TIKTOK] Initial field value: '{initial_value}'")
                                
                                # Method 1: Direct value setting with events
                                print(f"[STEP 1] [TIKTOK] Clearing field...")
                                driver.execute_script("arguments[0].value = '';", email_field)  # Clear
                                time.sleep(0.1)
                                
                                print(f"[STEP 2] [TIKTOK] Setting value...")
                                driver.execute_script(f"arguments[0].value = '{login_field_value}';", email_field)  # Fill
                                time.sleep(0.1)
                                
                                print(f"[STEP 3] [TIKTOK] Triggering input event...")
                                driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", email_field)
                                time.sleep(0.1)
                                
                                print(f"[STEP 4] [TIKTOK] Triggering change event...")
                                driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", email_field)
                                time.sleep(0.1)
                                
                                print(f"[STEP 5] [TIKTOK] Triggering blur event...")
                                driver.execute_script("arguments[0].dispatchEvent(new Event('blur', { bubbles: true }));", email_field)
                                time.sleep(0.2)
                                
                                # Check value after Method 1
                                value_after_method1 = email_field.get_attribute('value')
                                print(f"[DEBUG] [TIKTOK] Value after Method 1: '{value_after_method1}'")
                                
                                # Method 2: Focus and set value (backup)
                                print(f"[STEP 6] [TIKTOK] Method 2: Focus element...")
                                driver.execute_script("arguments[0].focus();", email_field)
                                time.sleep(0.1)
                                
                                print(f"[STEP 7] [TIKTOK] Method 2: Select all text...")
                                driver.execute_script("arguments[0].select();", email_field)
                                time.sleep(0.1)
                                
                                print(f"[STEP 8] [TIKTOK] Method 2: Set value again...")
                                driver.execute_script(f"arguments[0].value = '{login_field_value}';", email_field)
                                time.sleep(0.1)
                                
                                print(f"[STEP 9] [TIKTOK] Method 2: Trigger input event...")
                                driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", email_field)
                                time.sleep(0.2)
                                
                                # Final check
                                final_value = email_field.get_attribute('value')
                                print(f"[DEBUG] [TIKTOK] Final field value: '{final_value}'")
                                print(f"[SUCCESS] [TIKTOK] Done fill value - NO mouse movement")
                            except Exception as js_err:
                                print(f"[ERROR] [TIKTOK] JavaScript fill failed: {js_err}")
                                # Fallback: Try Selenium send_keys without clicking
                                try:
                                    print(f"🔄 [TIKTOK] Fallback: Using Selenium send_keys")
                                    driver.execute_script("arguments[0].focus();", email_field)
                                    driver.execute_script("arguments[0].select();", email_field)
                                    email_field.send_keys(login_field_value)
                                    time.sleep(0.3)
                                    print(f"[SUCCESS] [TIKTOK] Fallback send_keys successful")
                                except Exception as fallback_err:
                                    print(f"[ERROR] [TIKTOK] Fallback also failed: {fallback_err}")
                                    continue
                            
                            # Verify done fill
                            field_value = email_field.get_attribute('value')
                            print(f"[DEBUG] [TIKTOK] Field value sau when fill: '{field_value}'")
                            print(f"[TARGET] [TIKTOK] Expected value: '{login_field_value}'")
                            
                            if field_value == login_field_value:
                                print(f"[SUCCESS] [TIKTOK] Done fill email/username thành công!")
                                email_field_found = True
                                break
                            else:
                                print(f"[WARNING] [TIKTOK] Field value không khớp, try selector tiếp theo...")
                        else:
                            print(f"[ERROR] [TIKTOK] Element không hợp lệ (displayed: {email_field.is_displayed()}, enabled: {email_field.is_enabled()})")
                    except Exception as e:
                        print(f"[WARNING] [TIKTOK] Error with selector {selector}: {e}")
                        continue
                
                if email_field_found:
                    break
                
                if retry < max_retries - 1:
                    print(f"[WAITING] [TIKTOK] Đợi 2 giây trước when try lại...")
                    time.sleep(2)
            
            if not email_field_found:
                print(f"[ERROR] [TIKTOK] No find found trường input email/username sau {max_retries} lần try")
                # Debug: List all input fields
                try:
                    all_inputs = driver.find_elements("css selector", "input")
                    print(f"[DEBUG] [TIKTOK] Tìm found {len(all_inputs)} input fields:")
                    for i, inp in enumerate(all_inputs):
                        try:
                            placeholder = inp.get_attribute('placeholder') or ''
                            name = inp.get_attribute('name') or ''
                            input_type = inp.get_attribute('type') or ''
                            data_e2e = inp.get_attribute('data-e2e') or ''
                            print(f"  Input {i}: placeholder='{placeholder}', name='{name}', type='{input_type}', data-e2e='{data_e2e}'")
                        except:
                            pass
                except Exception as debug_error:
                    print(f"[ERROR] [TIKTOK] Error debug: {debug_error}")
                return False
            
            time.sleep(1)
            
            # Tìm and fill password with retry logic
            print(f"[DEBUG] [TIKTOK] Đang find trường input password...")
            print(f"[PASSWORD] [TIKTOK] Password cần fill: {password[:5]}***")
            
            password_selectors = [
                "input[data-e2e='login-password']",
                "input[name='password']",
                "input[placeholder*='Password']",
                "input[placeholder*='password']",
                "input[type='password']",
                "input[autocomplete='current-password']"
            ]
            
            print(f"[TARGET] [TIKTOK] Sẽ try {len(password_selectors)} password selectors:")
            for i, selector in enumerate(password_selectors):
                print(f"  {i+1}. {selector}")
            
            password_field_found = False
            
            for retry in range(max_retries):
                print(f"[REFRESH] [TIKTOK] Thử find password lần {retry + 1}/{max_retries}...")
                
                for selector in password_selectors:
                    try:
                        # Kiểm tra session trước
                        driver.current_url  # Test session
                        
                        password_field = driver.find_element("css selector", selector)
                        print(f"[DEBUG] [TIKTOK] Tìm found password element with selector: {selector}")
                        print(f"[VISIBLE] [TIKTOK] Password element displayed: {password_field.is_displayed()}")
                        print(f"[ENABLED] [TIKTOK] Password element enabled: {password_field.is_enabled()}")
                        print(f"[LOCATION] [TIKTOK] Password element location: {password_field.location}")
                        print(f"[SIZE] [TIKTOK] Password element size: {password_field.size}")
                        
                        if password_field.is_displayed() and password_field.is_enabled():
                            print(f"[SUCCESS] [TIKTOK] Password element hợp lệ, start fill...")
                            
                            # Wait for element to be interactable
                            try:
                                from selenium.webdriver.support.ui import WebDriverWait
                                from selenium.webdriver.support import expected_conditions as EC
                                
                                wait = WebDriverWait(driver, 5)
                                wait.until(EC.element_to_be_clickable(password_field))
                                print(f"[SUCCESS] [TIKTOK] Password field is clickable")
                            except Exception as wait_err:
                                print(f"[WARNING] [TIKTOK] Wait failed: {wait_err}")
                            
                            # Fill password using JavaScript with detailed logging - NO mouse movement
                            try:
                                print(f"⌨️ [TIKTOK] Đang fill password bằng JavaScript (không di chuyển chuột)")
                                print(f"[DEBUG] [TIKTOK] Target password: '{password[:3]}***'")
                                print(f"[DEBUG] [TIKTOK] Element tag: {password_field.tag_name}")
                                print(f"[DEBUG] [TIKTOK] Element type: {password_field.get_attribute('type')}")
                                print(f"[DEBUG] [TIKTOK] Element placeholder: {password_field.get_attribute('placeholder')}")
                                
                                # Check initial value
                                initial_value = password_field.get_attribute('value')
                                print(f"[DEBUG] [TIKTOK] Initial password value: '{initial_value}'")
                                
                                # Method 1: Direct value setting with events
                                print(f"[STEP 1] [TIKTOK] Clearing password field...")
                                driver.execute_script("arguments[0].value = '';", password_field)  # Clear
                                time.sleep(0.1)
                                
                                print(f"[STEP 2] [TIKTOK] Setting password value...")
                                driver.execute_script(f"arguments[0].value = '{password}';", password_field)  # Fill
                                time.sleep(0.1)
                                
                                print(f"[STEP 3] [TIKTOK] Triggering input event...")
                                driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", password_field)
                                time.sleep(0.1)
                                
                                print(f"[STEP 4] [TIKTOK] Triggering change event...")
                                driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", password_field)
                                time.sleep(0.1)
                                
                                print(f"[STEP 5] [TIKTOK] Triggering blur event...")
                                driver.execute_script("arguments[0].dispatchEvent(new Event('blur', { bubbles: true }));", password_field)
                                time.sleep(0.2)
                                
                                # Check value after Method 1
                                value_after_method1 = password_field.get_attribute('value')
                                print(f"[DEBUG] [TIKTOK] Password value after Method 1: '{value_after_method1}'")
                                
                                # Method 2: Focus and set value (backup)
                                print(f"[STEP 6] [TIKTOK] Method 2: Focus password element...")
                                driver.execute_script("arguments[0].focus();", password_field)
                                time.sleep(0.1)
                                
                                print(f"[STEP 7] [TIKTOK] Method 2: Select all text...")
                                driver.execute_script("arguments[0].select();", password_field)
                                time.sleep(0.1)
                                
                                print(f"[STEP 8] [TIKTOK] Method 2: Set password value again...")
                                driver.execute_script(f"arguments[0].value = '{password}';", password_field)
                                time.sleep(0.1)
                                
                                print(f"[STEP 9] [TIKTOK] Method 2: Trigger input event...")
                                driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", password_field)
                                time.sleep(0.2)
                                
                                # Final check
                                final_value = password_field.get_attribute('value')
                                print(f"[DEBUG] [TIKTOK] Final password value: '{final_value}'")
                                print(f"[SUCCESS] [TIKTOK] Done fill password - NO mouse movement")
                            except Exception as js_err:
                                print(f"[ERROR] [TIKTOK] JavaScript password fill failed: {js_err}")
                                # Fallback: Try Selenium send_keys without clicking
                                try:
                                    print(f"🔄 [TIKTOK] Fallback: Using Selenium send_keys for password")
                                    driver.execute_script("arguments[0].focus();", password_field)
                                    driver.execute_script("arguments[0].select();", password_field)
                                    password_field.send_keys(password)
                                    time.sleep(0.3)
                                    print(f"[SUCCESS] [TIKTOK] Fallback password send_keys successful")
                                except Exception as fallback_err:
                                    print(f"[ERROR] [TIKTOK] Password fallback also failed: {fallback_err}")
                                    continue
                            
                            # Verify done fill (không check value vì password field thường không trả về value)
                            print(f"[SUCCESS] [TIKTOK] Done fill password thành công!")
                            password_field_found = True
                            break
                        else:
                            print(f"[ERROR] [TIKTOK] Password element không hợp lệ (displayed: {password_field.is_displayed()}, enabled: {password_field.is_enabled()})")
                    except Exception as e:
                        print(f"[WARNING] [TIKTOK] Error with selector {selector}: {e}")
                        continue
                
                if password_field_found:
                    break
                
                if retry < max_retries - 1:
                    print(f"[WAITING] [TIKTOK] Đợi 2 giây trước when try lại...")
                    time.sleep(2)
            
            if not password_field_found:
                print(f"[ERROR] [TIKTOK] No find found trường input password sau {max_retries} lần try")
                return False
            
            time.sleep(1)
            
            # Click nút login with process button disabled
            print(f"[DEBUG] [TIKTOK] Đang find nút submit...")
            submit_selectors = [
                "button[type='submit']",
                "button[data-e2e='login-button']",
                "//button[contains(text(), 'Log in')]",
                "//button[contains(text(), 'Đăng input')]"
            ]
            
            submit_clicked = False
            for selector in submit_selectors:
                try:
                    if selector.startswith("//"):
                        submit_buttons = driver.find_elements("xpath", selector)
                    else:
                        submit_buttons = driver.find_elements("css selector", selector)
                    
                    if submit_buttons:
                        submit_button = submit_buttons[0]
                        print(f"[SUCCESS] [TIKTOK] Tìm found nút submit with selector: {selector}")
                        print(f"[DEBUG] [TIKTOK] Found {len(submit_buttons)} submit buttons")
                        print(f"[VISIBLE] [TIKTOK] Submit button displayed: {submit_button.is_displayed()}")
                        print(f"[ENABLED] [TIKTOK] Submit button enabled: {submit_button.is_enabled()}")
                        print(f"[LOCATION] [TIKTOK] Submit button location: {submit_button.location}")
                        print(f"[SIZE] [TIKTOK] Submit button size: {submit_button.size}")
                        
                        # Kiểm tra button have disabled không
                        is_disabled = submit_button.get_attribute("disabled")
                        if is_disabled:
                            print(f"[WARNING] [TIKTOK] Button bị disabled, đợi enable...")
                            # Đợi button enable (tối đa 10 giây)
                            for i in range(10):
                                time.sleep(1)
                                is_disabled = submit_button.get_attribute("disabled")
                                if not is_disabled:
                                    print(f"[SUCCESS] [TIKTOK] Button done enable sau {i+1} giây")
                                    break
                                print(f"[WAITING] [TIKTOK] Đang đợi button enable... ({i+1}/10)")
                        
                        # Get button location for logging
                        try:
                            location = submit_button.location
                            size = submit_button.size
                            center_x = location['x'] + size['width'] / 2
                            center_y = location['y'] + size['height'] / 2
                            print(f"[DEBUG] [TIKTOK] Button center at ({center_x}, {center_y})")
                        except Exception as loc_err:
                            print(f"[WARNING] [TIKTOK] Could not get button location: {loc_err}")
                        
                        # Thử click bình thường trước
                        # Submit using JavaScript with detailed logging - NO mouse movement
                        try:
                            print(f"[DEBUG] [TIKTOK] Submit button tag: {submit_button.tag_name}")
                            print(f"[DEBUG] [TIKTOK] Submit button type: {submit_button.get_attribute('type')}")
                            print(f"[DEBUG] [TIKTOK] Submit button text: '{submit_button.text}'")
                            print(f"[DEBUG] [TIKTOK] Submit button enabled: {submit_button.is_enabled()}")
                            print(f"[DEBUG] [TIKTOK] Submit button displayed: {submit_button.is_displayed()}")
                            
                            # Method 1: JavaScript click
                            print(f"[STEP 1] [TIKTOK] JavaScript click submit button...")
                            driver.execute_script("arguments[0].click();", submit_button)
                            print(f"[SUCCESS] [TIKTOK] Done submit bằng JavaScript - NO mouse movement")
                            submit_clicked = True
                            break
                        except Exception as js_error:
                            print(f"[WARNING] [TIKTOK] JavaScript submit failed: {js_error}")
                            # Method 2: Focus and press Enter
                            try:
                                print(f"[STEP 2] [TIKTOK] Focus submit button...")
                                driver.execute_script("arguments[0].focus();", submit_button)
                                time.sleep(0.1)
                                
                                print(f"[STEP 3] [TIKTOK] Triggering Enter key down...")
                                driver.execute_script("arguments[0].dispatchEvent(new KeyboardEvent('keydown', {key: 'Enter', keyCode: 13}));", submit_button)
                                time.sleep(0.1)
                                
                                print(f"[STEP 4] [TIKTOK] Triggering Enter key up...")
                                driver.execute_script("arguments[0].dispatchEvent(new KeyboardEvent('keyup', {key: 'Enter', keyCode: 13}));", submit_button)
                                time.sleep(0.1)
                                
                                print(f"[SUCCESS] [TIKTOK] Done submit bằng Enter key - NO mouse movement")
                                submit_clicked = True
                                break
                            except Exception as enter_error:
                                print(f"[ERROR] [TIKTOK] Enter key submit also failed: {enter_error}")
                                continue
                                
                except Exception as e:
                    print(f"[WARNING] [TIKTOK] Error with selector {selector}: {e}")
                    continue
            
            if not submit_clicked:
                print(f"[ERROR] [TIKTOK] No thể click nút submit")
                return False
            
            # Wait longer to check result and ensure form is submitted
            print(f"[WAITING] [TIKTOK] Waiting 5 seconds to check login result...")
            time.sleep(5)
            
            # Kiểm tra xem have cần 2FA không
            print(f"[DEBUG] [TIKTOK] Kiểm tra request 2FA...")
            if twofa or self._check_2fa_required(driver):
                print(f"[SECURITY] [TIKTOK] Phát hiện request 2FA, try email verification...")
                if self._handle_2fa_with_email(driver, login_data):
                    print(f"[SUCCESS] [TIKTOK] 2FA thành công with email verification")
                else:
                    print(f"[WARNING] [TIKTOK] 2FA thất bại, try phương pháp thủ công...")
                    if twofa:
                        print(f"[SECURITY] [TIKTOK] Sử dụng code 2FA thủ công: {twofa}")
                        self._handle_2fa(driver, twofa)
            else:
                print(f"[SUCCESS] [TIKTOK] No cần 2FA")
            
            # Kiểm tra kết quả login
            time.sleep(3)
            current_url = driver.current_url
            print(f"[NETWORK] [TIKTOK] URL sau when login: {current_url}")

            # Nhận diện thông báo 'Maximum number of attempts reached' and the biến thể
            try:
                error_texts = []
                candidates = driver.find_elements("css selector", "div, span, p, h1, h2")
                for el in candidates[:200]:
                    try:
                        txt = (el.text or "").strip()
                        if txt:
                            error_texts.append(txt)
                    except Exception:
                        pass
                joined = "\n".join(error_texts).lower()
                if ("maximum number of attempts reached" in joined) or ("too many attempts" in joined) or ("try again later" in joined):
                    print("⛔ [TIKTOK] Phát hiện giới hạn số lần try login: Maximum number of attempts reached / Too many attempts / Try again later")
                    # Trả về False to caller have thể execute backoff/đổi IP/proxy and try lại sau
                    return False
            except Exception as _e:
                print(f"[WARNING] [TIKTOK] Error when dò thông báo lỗi: {_e}")
            
            if 'login' not in current_url.lower() and 'signin' not in current_url.lower():
                print(f"[SUCCESS] [TIKTOK] Đăng input TikTok thành công for {login_field_value}")
                return True
            else:
                print(f"[ERROR] [TIKTOK] Đăng input TikTok thất bại for {login_field_value}")
                return False
                
        except Exception as e:
            print(f"[ERROR] [TIKTOK] Error login TikTok: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def _check_2fa_required(self, driver):
        """Kiểm tra xem have request 2FA không"""
        try:
            # Kiểm tra the dấu hiệu of 2FA
            verification_indicators = [
                "verification",
                "2fa",
                "two-factor",
                "code",
                "code verify",
                "xác nhận"
            ]
            
            page_source = driver.page_source.lower()
            current_url = driver.current_url.lower()
            
            for indicator in verification_indicators:
                if indicator in page_source or indicator in current_url:
                    return True
            
            # Kiểm tra the element thường have in form 2FA
            verification_elements = [
                "input[placeholder*='code']",
                "input[placeholder*='verification']",
                "input[placeholder*='code']",
                "input[name*='code']",
                "input[name*='verification']"
            ]
            
            for selector in verification_elements:
                try:
                    element = driver.find_element("css selector", selector)
                    if element.is_displayed():
                        return True
                except:
                    continue
            
            return False
            
        except Exception as e:
            print(f"Error check 2FA: {e}")
            return False
    
    def _handle_2fa_with_email(self, driver, login_data):
        """Xử lý 2FA bằng app riêng"""
        try:
            print(f"[EMAIL] [2FA] Bắt đầu process 2FA with app riêng...")
            
            if not login_data:
                print(f"[ERROR] [2FA] No have login_data")
                return False
            
            # Lấy thông tin email
            email = login_data.get('email', '')
            if not email:
                print(f"[ERROR] [2FA] No have email in login_data")
                return False
            
            print(f"[EMAIL] [2FA] Email: {email}")

            # Try Microsoft Graph automatically if credentials provided
            try:
                code = self._fetch_tiktok_code_from_hotmail(login_data)
                if code:
                    print(f"[SUCCESS] [2FA] Lấy code from Hotmail (Graph): {code}")
                    return self._input_verification_code(driver, code)
                else:
                    print(f"[WARNING] [2FA] No find found code bằng Microsoft Graph, fallback sang app ngoài")
            except Exception as e:
                print(f"[WARNING] [2FA] Error Graph: {e}. Fallback sang app ngoài")
            
            # Tạo request for app 2FA
            request_id = f"2fa_{int(time.time())}"
            request_data = {
                'request_id': request_id,
                'email': email,
                'timestamp': datetime.now().isoformat(),
                'status': 'waiting'
            }
            
            # Ghi file request
            comm_dir = "2fa_communication"
            os.makedirs(comm_dir, exist_ok=True)
            request_file = os.path.join(comm_dir, "2fa_request.json")
            response_file = os.path.join(comm_dir, "2fa_response.json")
            
            with open(request_file, 'w', encoding='utf-8') as f:
                json.dump(request_data, f, indent=2, ensure_ascii=False)
            
            print(f"📤 [2FA] Done gửi request for app 2FA: {request_id}")
            print(f"[WAITING] [2FA] Đang đợi code 2FA from app riêng...")
            
            # Đợi response from app 2FA (tối đa 60 giây)
            max_wait_time = 60
            wait_time = 0
            
            while wait_time < max_wait_time:
                if os.path.exists(response_file):
                    try:
                        with open(response_file, 'r', encoding='utf-8') as f:
                            response_data = json.load(f)
                        
                        if response_data.get('request_id') == request_id:
                            verification_code = response_data.get('verification_code', '')
                            status = response_data.get('status', '')
                            
                            if status == 'success' and verification_code:
                                print(f"[SUCCESS] [2FA] Nhận get code 2FA: {verification_code}")
                                
                                # Xóa file response
                                os.remove(response_file)
                                
                                # Nhập code ando form
                                success = self._input_verification_code(driver, verification_code)
                                return success
                            else:
                                print(f"[ERROR] [2FA] App 2FA báo lỗi: {response_data.get('error', 'Unknown error')}")
                                os.remove(response_file)
                                return False
                    except Exception as e:
                        print(f"[WARNING] [2FA] Error read response: {e}")
                
                time.sleep(2)
                wait_time += 2
                print(f"[WAITING] [2FA] Đang đợi... ({wait_time}/{max_wait_time}s)")
            
            print(f"[TIME] [2FA] Timeout! No nhận get code 2FA in {max_wait_time} giây")
            print(f"[INFO] [2FA] Hãy đảm bảo TikTok 2FA Manager doing chạy")
            
            # Xóa file request if timeout
            if os.path.exists(request_file):
                os.remove(request_file)
            
            return False
            
        except Exception as e:
            print(f"[ERROR] [2FA] Error process 2FA: {e}")
            return False
    
    # Email refresh token method removed
    
    def _input_verification_code(self, driver, verification_code):
        """Nhập code verify ando form"""
        try:
            print(f"[DEBUG] [2FA] Đang find trường input code verify...")
            
            # Các selector for trường input code
            code_selectors = [
                "input[placeholder*='code']",
                "input[placeholder*='verification']",
                "input[placeholder*='code']",
                "input[name*='code']",
                "input[name*='verification']",
                "input[type='text']",
                "input[data-e2e='verification-code']",
                "input[autocomplete='one-time-code']"
            ]
            
            code_field_found = False
            for selector in code_selectors:
                try:
                    code_field = driver.find_element("css selector", selector)
                    if code_field.is_displayed():
                        print(f"[SUCCESS] [2FA] Tìm found trường input code: {selector}")
                        code_field.clear()
                        code_field.send_keys(verification_code)
                        print(f"[SUCCESS] [2FA] Done fill code verify: {verification_code}")
                        code_field_found = True
                        break
                except Exception as e:
                    print(f"[WARNING] [2FA] No find found with selector {selector}: {e}")
                    continue
            
            if not code_field_found:
                print(f"[ERROR] [2FA] No find found trường input code verify")
                return False
            
            time.sleep(2)
            
            # Tìm and click nút submit
            print(f"[DEBUG] [2FA] Đang find nút submit...")
            submit_selectors = [
                "button[type='submit']",
                "button[data-e2e='verification-submit']",
                "//button[contains(text(), 'Verify')]",
                "//button[contains(text(), 'Xác nhận')]",
                "//button[contains(text(), 'Submit')]",
                "//button[contains(text(), 'Continue')]"
            ]
            
            submit_btn_found = False
            for selector in submit_selectors:
                try:
                    if selector.startswith("//"):
                        submit_btn = driver.find_element("xpath", selector)
                    else:
                        submit_btn = driver.find_element("css selector", selector)
                    
                    if submit_btn.is_displayed():
                        print(f"[SUCCESS] [2FA] Tìm found nút submit: {selector}")
                        submit_btn.click()
                        print(f"[SUCCESS] [2FA] Done click nút xác nhận")
                        submit_btn_found = True
                        break
                except Exception as e:
                    print(f"[WARNING] [2FA] No find found nút submit with selector {selector}: {e}")
                    continue
            
            if not submit_btn_found:
                print(f"[WARNING] [2FA] No find found nút submit, try Enter...")
                try:
                    from selenium.webdriver.common.keys import Keys
                    code_field.send_keys(Keys.RETURN)
                    print(f"[SUCCESS] [2FA] Done gửi code bằng Enter key")
                except Exception as e:
                    print(f"[ERROR] [2FA] No thể gửi code: {e}")
                    return False
            
            print(f"[WAITING] [2FA] Chờ kết quả verify...")
            time.sleep(3)
            print(f"[SUCCESS] [2FA] Hoàn thành input code verify")
            return True
            
        except Exception as e:
            print(f"[ERROR] [2FA] Error input code verify: {e}")
            return False

    def _fetch_tiktok_code_from_hotmail(self, login_data):
        """Fetch latest TikTok verification code from Hotmail with auto fallback methods.

        Hỗ trợ many phương pháp:
        1. Refresh token + client ID
        2. Device login
        3. IMAP with password
        4. Access token from environment
        """
        try:
            import re
            import os
            from datetime import datetime, timedelta

            # Parse account data
            ms_refresh_token = login_data.get('ms_refresh_token', '')
            ms_client_id = login_data.get('ms_client_id', '')
            email = login_data.get('email', '')
            email_password = login_data.get('email_password', '')
            access_token = os.getenv('MS_ACCESS_TOKEN')

            print(f"[DEBUG] [GRAPH] Đang find code 2FA from Hotmail...")
            print(f"[EMAIL] [GRAPH] Email: {email}")
            
            # Thử the phương pháp theo thứ tự ưu tiên
            methods = []
            
            # Method 1: Access token from environment
            if access_token:
                methods.append(('access_token', access_token, None))
            
            # Method 2: Refresh token (if have)
            if ms_refresh_token and ms_refresh_token != 'ep' and ms_client_id:
                methods.append(('refresh_token', ms_refresh_token, ms_client_id))
            
            # Method 3: Device login (luôn have thể try)
            if ms_client_id:
                methods.append(('device_login', None, ms_client_id))
            
            # Method 4: IMAP (if have password)
            if email_password and email_password != 'ep':
                methods.append(('imap', email_password, None))
            
            for method_name, method_data, client_id in methods:
                try:
                    print(f"[REFRESH] [GRAPH] Thử phương pháp: {method_name}")
                    
                    if method_name == 'access_token':
                        success, result = self._try_access_token_method(method_data, email)
                    elif method_name == 'refresh_token':
                        success, result = self._try_refresh_token_method(method_data, client_id, email)
                    elif method_name == 'device_login':
                        success, result = self._try_device_login_method(client_id, email)
                    elif method_name == 'imap':
                        success, result = self._try_imap_method(email, method_data)
                    
                    if success:
                        return result
                    
                except Exception as e:
                    print(f"[WARNING] [GRAPH] Error phương pháp {method_name}: {e}")
                    continue
            
            print("[ERROR] [GRAPH] Tất cả phương pháp đều thất bại")
            return None
            
        except Exception as e:
            print(f"[ERROR] [GRAPH] Error tổng thể: {e}")
            return None
    
    def _try_access_token_method(self, access_token, email):
        """Thử phương pháp access token"""
        import requests
        
        print(f"[PASSWORD] [GRAPH] Sử dụng access token from environment")
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        return self._search_emails_with_token(headers, email)
    
    def _try_refresh_token_method(self, refresh_token, client_id, email):
        """Thử phương pháp refresh token"""
        import requests
        
        print(f"[REFRESH] [GRAPH] Sử dụng refresh token + client ID")
        
        # Refresh access token
        token_url = "https://login.microsoftonline.com/consumers/oauth2/v2.0/token"
        token_data = {
            'client_id': client_id,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token',
            'scope': 'Mail.Read'
        }
        
        try:
            token_response = requests.post(token_url, data=token_data)
            token_response.raise_for_status()
            token_result = token_response.json()
            access_token = token_result.get('access_token')
            
            if not access_token:
                print(f"[WARNING] [GRAPH] Token exchange failed: {token_response.status_code} {token_response.text}")
                return False, "Token exchange failed"
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            return self._search_emails_with_token(headers, email)
            
        except Exception as e:
            print(f"[WARNING] [GRAPH] Token exchange failed: {e}")
            return False, f"Token exchange failed: {e}"
    
    def _try_device_login_method(self, client_id, email):
        """Thử phương pháp device login"""
        try:
            import msal
            import requests
            
            print(f"[REFRESH] [GRAPH] Sử dụng device login")
            
            app = msal.PublicClientApplication(
                client_id, 
                authority="https://login.microsoftonline.com/consumers"
            )
            
            flow = app.initiate_device_flow(scopes=["Mail.Read"])
            print(f"[NETWORK] [GRAPH] Mở trình duyệt: {flow.get('message', 'Open browser and complete the device code flow')}")
            print("[WAITING] [GRAPH] Đang chờ bạn hoàn thành login...")
            
            result = app.acquire_token_by_device_flow(flow)
            
            if "error" in result:
                print(f"[ERROR] [GRAPH] Device login failed: {result.get('error_description', result.get('error'))}")
                return False, "Device login failed"
            
            access_token = result.get("access_token")
            if not access_token:
                print("[ERROR] [GRAPH] No lấy get access token")
                return False, "No access token"
            
            print("[SUCCESS] [GRAPH] Device login thành công!")
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            return self._search_emails_with_token(headers, email)
            
        except Exception as e:
            print(f"[ERROR] [GRAPH] Device login error: {e}")
            return False, f"Device login error: {e}"
    
    def _try_imap_method(self, email, password):
        """Thử phương pháp IMAP"""
        try:
            import imaplib
            import email
            import re
            from datetime import datetime, timedelta
            
            print(f"[REFRESH] [GRAPH] Sử dụng IMAP")
            
            mail = imaplib.IMAP4_SSL("outlook.office365.com", 993)
            mail.login(email, password)
            mail.select('inbox')
            
            print("[SUCCESS] [GRAPH] IMAP kết nối thành công!")
            
            start_time = time.time()
            timeout = 90
            
            while time.time() - start_time < timeout:
                try:
                    # Tìm email from TikTok in 30 phút gần đây
                    since_date = (datetime.now() - timedelta(minutes=30)).strftime("%d-%b-%Y")
                    
                    search_criteria = [
                        'FROM', 'tiktok.com',
                        'OR', 'FROM', 'no-reply@account.tiktok.com',
                        'OR', 'SUBJECT', 'TikTok',
                        'OR', 'SUBJECT', 'verification',
                        'OR', 'SUBJECT', 'code',
                        'SINCE', since_date
                    ]
                    
                    status, messages = mail.search(None, *search_criteria)
                    
                    if status != 'OK':
                        print("[WAITING] [GRAPH] Chưa find found email from TikTok...")
                        time.sleep(5)
                        continue
                    
                    email_ids = messages[0].split()
                    
                    if not email_ids:
                        print("[WAITING] [GRAPH] Chưa find found email mới...")
                        time.sleep(5)
                        continue
                    
                    # Kiểm tra email mới nhất
                    for email_id in reversed(email_ids[-20:]):
                        try:
                            status, msg_data = mail.fetch(email_id, '(RFC822)')
                            
                            if status != 'OK':
                                continue
                            
                            email_body = msg_data[0][1]
                            email_message = email.message_from_bytes(email_body)
                            
                            subject = email_message.get('Subject', '')
                            sender = email_message.get('From', '')
                            date_str = email_message.get('Date', '')
                            
                            # Lấy nội dung email
                            body = ""
                            if email_message.is_multipart():
                                for part in email_message.walk():
                                    if part.get_content_type() == "text/plain":
                                        body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                                        break
                            else:
                                body = email_message.get_payload(decode=True).decode('utf-8', errors='ignore')
                            
                            code = self._extract_tiktok_code_from_content(subject, body, date_str)
                            if code:
                                print(f"[SUCCESS] [GRAPH] Tìm found code TikTok: {code}")
                                print(f"[EMAIL] [GRAPH] Email: {subject}")
                                print(f"👤 [GRAPH] Người gửi: {sender}")
                                print(f"[TIME] [GRAPH] Thời gian: {date_str}")
                                return True, code
                        
                        except Exception as e:
                            print(f"[WARNING] [GRAPH] Error process email: {e}")
                            continue
                    
                    print("[WAITING] [GRAPH] Chưa find found code mới...")
                    time.sleep(5)
                    
                except Exception as e:
                    print(f"[ERROR] [GRAPH] Error IMAP: {e}")
                    time.sleep(5)
            
            mail.close()
            mail.logout()
            return False, "Timeout"
            
        except Exception as e:
            print(f"[ERROR] [GRAPH] Error kết nối IMAP: {e}")
            return False, f"IMAP error: {e}"
    
    def _search_emails_with_token(self, headers, email):
        """Tìm email with access token"""
        import requests
        import json
        import re
        from datetime import datetime, timedelta
        
        print(f"[TIME] [GRAPH] Tìm kiếm in 90 giây...")
        
        start_time = time.time()
        timeout = 90
        
        while time.time() - start_time < timeout:
            try:
                # Tìm email gần đây
                url = f"https://graph.microsoft.com/v1.0/me/messages"
                params = {
                    '$top': 30,
                    '$orderby': 'receivedDateTime desc'
                }
                
                response = requests.get(url, headers=headers, params=params, timeout=10)
                
                if response.status_code == 401:
                    print(f"[ERROR] [GRAPH] Token hết hạn")
                    return False, "Token expired"
                
                if response.status_code != 200:
                    print(f"[ERROR] [GRAPH] Error API: {response.status_code} - {response.text}")
                    return False, f"API error: {response.status_code}"
                
                data = response.json()
                messages = data.get('value', [])
                
                if not messages:
                    print("[WAITING] [GRAPH] Chưa find found email...")
                    time.sleep(5)
                    continue
                
                print(f"[EMAIL] [GRAPH] Tìm found {len(messages)} email")
                
                # Kiểm tra fromng email
                for msg in messages:
                    subject = msg.get('subject', '')
                    body = msg.get('body', {}).get('content', '')
                    received_time = msg.get('receivedDateTime', '')
                    sender = msg.get('from', {}).get('emailAddress', {}).get('address', '')
                    
                    code = self._extract_tiktok_code_from_content(subject, body, received_time)
                    if code:
                        print(f"[SUCCESS] [GRAPH] Tìm found code TikTok: {code}")
                        print(f"[EMAIL] [GRAPH] Email: {subject}")
                        print(f"👤 [GRAPH] Người gửi: {sender}")
                        print(f"[TIME] [GRAPH] Thời gian: {received_time}")
                        return True, code
                
                print("[WAITING] [GRAPH] Chưa find found code mới...")
                time.sleep(5)
                
            except Exception as e:
                print(f"[ERROR] [GRAPH] Error find kiếm: {e}")
                time.sleep(5)
        
        print(f"[TIME] [GRAPH] Hết thời gian find kiếm code 2FA")
        return False, "No find found email chứa code 2FA in thời gian chờ."
    
    def _extract_tiktok_code_from_content(self, subject, body, received_time):
        """Trích xuất code TikTok from nội dung email"""
        import re
        from datetime import datetime
        
        # Tìm code 6 chữ số
        code_pattern = r'\b\d{6}\b'
        codes = re.findall(code_pattern, f"{subject} {body}")
        
        if not codes:
            return None
        
        # Kiểm tra thời gian email (in 30 phút gần đây)
        try:
            if received_time:
                if 'T' in received_time:  # ISO format
                    received_dt = datetime.fromisoformat(received_time.replace('Z', '+00:00'))
                    now = datetime.now(received_dt.tzinfo)
                else:  # IMAP format
                    import email.utils
                    received_dt = email.utils.parsedate_to_datetime(received_time)
                    now = datetime.now(received_dt.tzinfo)
                
                time_diff = (now - received_dt).total_seconds()
                
                if time_diff <= 1800:  # 30 phút
                    return codes[0]
        except:
            pass
        
        return None
    
    def ultimate_auto_2fa_handler(self, email, password=None, refresh_token=None, client_id="9e5f94bc-e8a4-4e73-b8be-63364c29d753"):
        """Ultimate Auto 2FA Handler - Xử lý tự động hoàn toàn"""
        print(f"[PROFILE] [ULTIMATE] Bắt đầu process tự động TikTok 2FA for: {email}")
        print(f"[TIME] [ULTIMATE] Thời gian start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # Thử the phương pháp theo thứ tự ưu tiên
        methods = []
        
        # Method 1: Refresh token (if have)
        if refresh_token and refresh_token != 'ep':
            methods.append(('refresh_token', refresh_token, client_id))
        
        # Method 2: Device login (luôn have thể try)
        if client_id:
            methods.append(('device_login', None, client_id))
        
        # Method 3: IMAP (if have password)
        if password and password != 'ep':
            methods.append(('imap', password, None))
        
        for method_name, method_data, client_id in methods:
            try:
                print(f"[REFRESH] [ULTIMATE] Thử phương pháp: {method_name}")
                
                if method_name == 'refresh_token':
                    success, result = self._try_refresh_token_method(method_data, client_id, email)
                elif method_name == 'device_login':
                    success, result = self._try_device_login_method(client_id, email)
                elif method_name == 'imap':
                    success, result = self._try_imap_method(email, method_data)
                
                if success:
                    print(f"[SUCCESS] [ULTIMATE] THÀNH CÔNG! Mã TikTok: {result}")
                    return True, result
                
            except Exception as e:
                print(f"[WARNING] [ULTIMATE] Error phương pháp {method_name}: {e}")
                continue
        
        print("[ERROR] [ULTIMATE] Tất cả phương pháp đều thất bại")
        return False, "Tất cả phương pháp đều thất bại"
    
    def continuous_monitor_2fa(self, email, password=None, refresh_token=None, client_id="9e5f94bc-e8a4-4e73-b8be-63364c29d753", duration=300, interval=30):
        """Continuous Monitor 2FA - Monitor liên tục"""
        print(f"[DEBUG] [MONITOR] Bắt đầu monitor TikTok 2FA for: {email}")
        print(f"[TIME] [MONITOR] Thời gian monitor: {duration} giây")
        print(f"[REFRESH] [MONITOR] Khoảng thời gian check: {interval} giây")
        print(f"[TIME] [MONITOR] Thời gian start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        found_codes = set()
        start_time = time.time()
        
        while time.time() - start_time < duration:
            try:
                print(f"[DEBUG] [MONITOR] Kiểm tra code mới... {datetime.now().strftime('%H:%M:%S')}")
                
                # Thử lấy code
                success, result = self.ultimate_auto_2fa_handler(email, password, refresh_token, client_id)
                
                if success and result not in found_codes:
                    found_codes.add(result)
                    print(f"[SUCCESS] [MONITOR] Tìm found code TikTok mới: {result}")
                    print(f"[TIME] [MONITOR] Thời gian: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    return True, result
                
                print("[WAITING] [MONITOR] Chưa have code mới")
                time.sleep(interval)
                
            except KeyboardInterrupt:
                print("⏹️ [MONITOR] Dừng monitor...")
                break
            except Exception as e:
                print(f"[ERROR] [MONITOR] Error monitor: {e}")
                time.sleep(interval)
        
        print("[TIME] [MONITOR] Kết thúc monitor")
        return False, "Monitor timeout"

    def test_graph_mail_fetch(self, account_line: str):
        """Test fetching TikTok verification code using a single account line.

        Accepts formats already supported by _parse_tiktok_account_data(), including
        the Hotmail Graph variant with refresh token and client id.

        Returns (success: bool, message: str)
        """
        try:
            parsed = self._parse_tiktok_account_data(account_line)
            if not parsed:
                return False, "No parse get dữ liệu tài khoản. Kiểm tra định dạng."

            # Sử dụng ultimate handler
            email = parsed.get('email', '')
            password = parsed.get('email_password', '')
            refresh_token = parsed.get('ms_refresh_token', '')
            client_id = parsed.get('ms_client_id', '9e5f94bc-e8a4-4e73-b8be-63364c29d753')
            
            success, result = self.ultimate_auto_2fa_handler(email, password, refresh_token, client_id)
            
            if success:
                return True, f"Lấy code thành công: {result}"
            else:
                return False, f"No find found code 2FA: {result}"
                
        except Exception as e:
            return False, f"Error test Graph: {str(e)}"
    
    def _parse_tiktok_account_data(self, account_string):
        """Parse TikTok account data from string format - hỗ trợ username|password"""
        try:
            # Supported formats:
            # 1) username|password (Standard format - đơn giản)
            # 2) username|password|email|email_password|session_token|user_id (TikTok Format)
            # 3) username|password|hotmail_email|hotmail_password|ms_refresh_token|ms_client_id (Microsoft Format)
            if '|' in account_string:
                parts = account_string.split('|')
                if len(parts) >= 6 and '@' in parts[2] and '-' in parts[5]:
                    # Hotmail (Microsoft) 2FA flow using Graph refresh token + client_id
                    username = parts[0].strip()
                    password = parts[1].strip()
                    email = parts[2].strip()
                    email_password = parts[3].strip()
                    ms_refresh_token = parts[4].strip()
                    ms_client_id = parts[5].strip()
                    
                    return {
                        'username': username,
                        'email': email,
                        'password': password,
                        'email_password': email_password,
                        'ms_refresh_token': ms_refresh_token,
                        'ms_client_id': ms_client_id,
                        'twofa': ''
                    }
                if len(parts) >= 3:
                    username = parts[0].strip()
                    password = parts[1].strip()
                    email = parts[2].strip()
                    email_password = parts[3].strip() if len(parts) > 3 else ''
                    session_token = parts[4].strip() if len(parts) > 4 else ''
                    user_id = parts[5].strip() if len(parts) > 5 else ''
                    
                    return {
                        'username': username,
                        'email': email,
                        'password': password,
                        'email_password': email_password,
                        'session_token': session_token,
                        'user_id': user_id,
                        'twofa': ''
                    }
                elif len(parts) >= 2:
                    # Format đơn giản: username|password (Standard format)
                    username = parts[0].strip()
                    password = parts[1].strip()
                    return {
                        'username': username,
                        'password': password,
                        'email': username,  # Sử dụng username làm email
                        'twofa': ''
                    }
            
            # Format cũ: username -> email (backward compatibility)
            elif ' -> ' in account_string:
                parts = account_string.split(' -> ')
                if len(parts) == 2:
                    username = parts[0].strip()
                    email = parts[1].strip()
                    return {
                        'username': username,
                        'email': email,
                        'password': '',  # Password cần get cung cấp riêng
                        'twofa': ''
                    }
            
            return None
        except Exception as e:
            print(f"Error parse TikTok account data: {e}")
            return None
    
    # Email verification methods removed
    
    # Email refresh token methods removed
    
    def _login_tiktok_with_session(self, driver, login_data):
        """Đăng input TikTok bằng session token"""
        try:
            session_token = login_data.get('session_token', '')
            user_id = login_data.get('user_id', '')
            
            if not session_token:
                print("No have session token")
                return False
            
            print(f"[PASSWORD] [TIKTOK] Đang try login TikTok with session token: {session_token[:20]}...")
            
            # Lấy URL hiện tại to giữ nguyên trang doing ở
            current_url = driver.current_url
            print(f"[NETWORK] [TIKTOK] Current URL: {current_url}")
            
            # Nếu doing ở trang login, điều hướng đến trang chủ to inject cookies
            if 'login' in current_url.lower():
                print(f"[REFRESH] [TIKTOK] Đang ở trang login, điều hướng đến trang chủ to inject cookies...")
                driver.get("https://www.tiktok.com")
                time.sleep(2)
            else:
                print(f"📍 [TIKTOK] Đang ở trang khác, giữ nguyên URL hiện tại")
            
            # Inject session token and user_id ando cookies
            print(f"🍪 [TIKTOK] Đang inject cookies...")
            cookies_to_set = [
                f"sessionid={session_token}; domain=.tiktok.com; path=/; secure; samesite=none",
                f"user_id={user_id}; domain=.tiktok.com; path=/; secure; samesite=none",
                f"tt_webid={user_id}; domain=.tiktok.com; path=/; secure; samesite=none"
            ]
            
            for cookie in cookies_to_set:
                try:
                    driver.execute_script(f"document.cookie = '{cookie}';")
                    print(f"[SUCCESS] [TIKTOK] Done inject cookie: {cookie.split('=')[0]}")
                except Exception as e:
                    print(f"[ERROR] [TIKTOK] Error set cookie: {e}")
            
            # Refresh trang to áp dụng cookies
            print(f"[REFRESH] [TIKTOK] Refresh trang to áp dụng cookies...")
            driver.refresh()
            time.sleep(5)
            
            # Kiểm tra xem done login thành công chưa
            current_url = driver.current_url
            page_source = driver.page_source.lower()
            
            print(f"[NETWORK] [TIKTOK] URL sau when refresh: {current_url}")
            print(f"[DEBUG] [TIKTOK] Đang check dấu hiệu login thành công...")
            
            # Kiểm tra the dấu hiệu login thành công
            success_indicators = [
                'logout' in page_source,
                'profile' in page_source,
                'upload' in page_source,
                'foryou' in current_url,
                'following' in current_url
            ]
            
            print(f"[STATS] [TIKTOK] Success indicators: {success_indicators}")
            print(f"[DEBUG] [TIKTOK] 'login' in URL: {'login' in current_url.lower()}")
            
            if any(success_indicators) and 'login' not in current_url.lower():
                print("[SUCCESS] [TIKTOK] Đăng input TikTok bằng session token thành công!")
                
                # Điều hướng đến trang For You sau when login thành công
                try:
                    print(f"[REFRESH] [TIKTOK] Điều hướng đến trang For You...")
                    driver.get("https://www.tiktok.com/foryou")
                    time.sleep(3)
                    print(f"[SUCCESS] [TIKTOK] Done điều hướng đến trang For You")
                except Exception as e:
                    print(f"[WARNING] [TIKTOK] No thể điều hướng đến For You: {e}")
                
                return True
            else:
                print("[ERROR] [TIKTOK] Session token không hợp lệ or done hết hạn")
                return False
                
        except Exception as e:
            print(f"Error login TikTok with session token: {str(e)}")
            return False
   
    def _handle_2fa(self, driver, twofa_code):
        """Xử lý 2FA"""
        try:
            # Tìm trường input 2FA
            twofa_selectors = [
                "input[name*='code']",
                "input[name*='verification']",
                "input[name*='2fa']",
                "input[placeholder*='code']",
                "input[placeholder*='verification']",
                "input[type='text']"
            ]
            
            for selector in twofa_selectors:
                try:
                    twofa_field = driver.find_element("css selector", selector)
                    twofa_field.clear()
                    twofa_field.send_keys(twofa_code)
                    break
                except:
                    continue
            
            time.sleep(1)
            
            # Tìm and click nút xác nhận
            confirm_selectors = [
                "button[type='submit']",
                "button:contains('Verify')",
                "button:contains('Confirm')",
                "button:contains('Xác nhận')"
            ]
            
            for selector in confirm_selectors:
                try:
                    confirm_button = driver.find_element("css selector", selector)
                    confirm_button.click()
                    break
                except:
                    continue
            
            time.sleep(3)
            
        except Exception as e:
            print(f"Error process 2FA: {str(e)}")
    
    def get_ip_location(self, ip_address):
        """Lấy thông tin vị trí địa lý from IP"""
        # Danh sách the API to try
        apis = [
            {
                'url': f"http://ip-api.com/json/{ip_address}",
                'parse': lambda data: {
                    'country': data.get('country', 'Unknown'),
                    'country_code': data.get('countryCode', 'XX'),
                    'city': data.get('city', 'Unknown'),
                    'region': data.get('regionName', 'Unknown')
                }
            },
            {
                'url': f"https://ipapi.co/{ip_address}/json/",
                'parse': lambda data: {
                    'country': data.get('country_name', 'Unknown'),
                    'country_code': data.get('country_code', 'XX'),
                    'city': data.get('city', 'Unknown'),
                    'region': data.get('region', 'Unknown')
                }
            },
            {
                'url': f"http://ipinfo.io/{ip_address}/json",
                'parse': lambda data: {
                    'country': data.get('country', 'Unknown'),
                    'country_code': data.get('country_code', 'XX'),
                    'city': data.get('city', 'Unknown'),
                    'region': data.get('region', 'Unknown')
                }
            }
        ]
        
        for api in apis:
            try:
                response = requests.get(api['url'], timeout=3)
                if response.status_code == 200:
                    data = response.json()
                    result = api['parse'](data)
                    if result['country'] != 'Unknown':
                        return result
            except Exception as e:
                print(f"Error API {api['url']}: {str(e)}")
                continue
        
        # Fallback: Detect one số IP phổ biến
        common_ips = {
            '8.8.8.8': {'country': 'United States', 'country_code': 'US', 'city': 'Mountain View', 'region': 'California'},
            '8.8.4.4': {'country': 'United States', 'country_code': 'US', 'city': 'Mountain View', 'region': 'California'},
            '1.1.1.1': {'country': 'United States', 'country_code': 'US', 'city': 'San Francisco', 'region': 'California'},
            '1.0.0.1': {'country': 'United States', 'country_code': 'US', 'city': 'San Francisco', 'region': 'California'},
            '208.67.222.222': {'country': 'United States', 'country_code': 'US', 'city': 'San Francisco', 'region': 'California'},
            '208.67.220.220': {'country': 'United States', 'country_code': 'US', 'city': 'San Francisco', 'region': 'California'},
        }
        
        if ip_address in common_ips:
            return common_ips[ip_address]
        
        # Fallback: Detect theo IP range
        try:
            ip_parts = ip_address.split('.')
            if len(ip_parts) == 4:
                first_octet = int(ip_parts[0])
                if first_octet == 8:  # Google IPs
                    return {'country': 'United States', 'country_code': 'US', 'city': 'Mountain View', 'region': 'California'}
                elif first_octet == 1:  # Cloudflare IPs
                    return {'country': 'United States', 'country_code': 'US', 'city': 'San Francisco', 'region': 'California'}
                elif first_octet == 208:  # OpenDNS IPs
                    return {'country': 'United States', 'country_code': 'US', 'city': 'San Francisco', 'region': 'California'}
                elif first_octet >= 192 and first_octet <= 223:  # Private IPs
                    return {'country': 'Local Network', 'country_code': 'LOC', 'city': 'Local', 'region': 'Private'}
        except:
            pass
        
        return {
            'country': 'Unknown',
            'country_code': 'XX',
            'city': 'Unknown',
            'region': 'Unknown'
        }
    
    def export_cookies_from_profile(self, profile_name, domain_filter="", valid_only=True):
        """Xuất cookies from Chrome profile"""
        try:
            import sqlite3
            
            profile_path = os.path.join(self.profiles_dir, profile_name)
            cookies_db = os.path.join(profile_path, "Default", "Cookies")
            
            if not os.path.exists(cookies_db):
                return []
            
            # Kết nối database cookies
            conn = sqlite3.connect(cookies_db)
            cursor = conn.cursor()
            
            # Query cookies
            if domain_filter:
                query = """
                SELECT name, value, host_key, path, expires_utc, is_secure, is_httponly, 
                       samesite, creation_utc, last_access_utc, last_update_utc
                FROM cookies 
                WHERE host_key LIKE ?
                """
                cursor.execute(query, (f"%{domain_filter}%",))
            else:
                query = """
                SELECT name, value, host_key, path, expires_utc, is_secure, is_httponly, 
                       samesite, creation_utc, last_access_utc, last_update_utc
                FROM cookies
                """
                cursor.execute(query)
            
            cookies = []
            current_time = time.time()
            
            for row in cursor.fetchall():
                name, value, host_key, path, expires_utc, is_secure, is_httponly, samesite, creation_utc, last_access_utc, last_update_utc = row
                
                # Chuyển đổi thời gian Chrome (microseconds since 1601) sang Unix timestamp
                if expires_utc > 0:
                    expiration_date = (expires_utc / 1000000) - 11644473600
                else:
                    expiration_date = None
                
                # Kiểm tra cookies còn hiệu lực
                if valid_only and expiration_date and expiration_date < current_time:
                    continue
                
                # Chuyển đổi samesite
                samesite_map = {0: "no_restriction", 1: "lax", 2: "strict"}
                samesite_value = samesite_map.get(samesite, "unspecified")
                
                cookie = {
                    "name": name,
                    "value": value,
                    "domain": host_key,
                    "path": path or "/",
                    "secure": bool(is_secure),
                    "httpOnly": bool(is_httponly),
                    "sameSite": samesite_value,
                    "session": expiration_date is None,
                    "expirationDate": expiration_date
                }
                
                cookies.append(cookie)
            
            conn.close()
            return cookies
            
        except Exception as e:
            print(f"Error when xuất cookies: {str(e)}")
            return []
    
    def import_cookies_to_profile(self, profile_name, cookies, overwrite=False, valid_only=True):
        """Import cookies ando Chrome profile"""
        try:
            import sqlite3
            
            profile_path = os.path.join(self.profiles_dir, profile_name)
            cookies_db = os.path.join(profile_path, "Default", "Cookies")
            
            if not os.path.exists(cookies_db):
                return 0
            
            # Kết nối database cookies
            conn = sqlite3.connect(cookies_db)
            cursor = conn.cursor()
            
            success_count = 0
            current_time = time.time()
            
            for cookie in cookies:
                try:
                    # Kiểm tra cookies còn hiệu lực
                    if valid_only and cookie.get('expirationDate') and cookie.get('expirationDate') < current_time:
                        continue
                    
                    # Chuyển đổi thời gian Unix sang Chrome format
                    if cookie.get('expirationDate'):
                        expires_utc = int((cookie['expirationDate'] + 11644473600) * 1000000)
                    else:
                        expires_utc = 0
                    
                    # Chuyển đổi samesite
                    samesite_map = {"no_restriction": 0, "lax": 1, "strict": 2}
                    samesite_value = samesite_map.get(cookie.get('sameSite', 'unspecified'), 0)
                    
                    # Kiểm tra cookie done tồn tại
                    cursor.execute("SELECT id FROM cookies WHERE name = ? AND host_key = ?", 
                                 (cookie['name'], cookie['domain']))
                    existing = cursor.fetforne()
                    
                    if existing and not overwrite:
                        continue
                    
                    # Xóa cookie cũ if tồn tại
                    if existing:
                        cursor.execute("DELETE FROM cookies WHERE name = ? AND host_key = ?", 
                                     (cookie['name'], cookie['domain']))
                    
                    # Thêm cookie mới
                    cursor.execute("""
                        INSERT INTO cookies (name, value, host_key, path, expires_utc, is_secure, 
                                             is_httponly, samesite, creation_utc, last_access_utc, last_update_utc)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        cookie['name'],
                        cookie['value'],
                        cookie['domain'],
                        cookie.get('path', '/'),
                        expires_utc,
                        1 if cookie.get('secure', False) else 0,
                        1 if cookie.get('httpOnly', False) else 0,
                        samesite_value,
                        int(current_time * 1000000) + 11644473600000000,
                        int(current_time * 1000000) + 11644473600000000,
                        int(current_time * 1000000) + 11644473600000000
                    ))
                    
                    success_count += 1
                    
                except Exception as e:
                    print(f"Error when import cookie {cookie.get('name', 'unknown')}: {str(e)}")
                    continue
            
            conn.commit()
            conn.close()
            return success_count
            
        except Exception as e:
            print(f"Error when import cookies: {str(e)}")
            return 0
    
    def check_account_status(self, profile_name, platform="auto"):
        """Kiểm tra trạng thái tài khoản done login"""
        try:
            # Khởi động Chrome profile
            driver = self.launch_chrome_profile(profile_name, headless=True)
            if not driver:
                return False, "No thể start Chrome profile"
            
            # Xác định platform if auto
            if platform == "auto":
                platform = self._detect_platform_from_cookies(profile_name)
            
            # Kiểm tra trạng thái theo platform
            if platform == "tiktok":
                return self._check_tiktok_status(driver)
            elif platform == "instagram":
                return self._check_instagram_status(driver)
            elif platform == "facebook":
                return self._check_facebook_status(driver)
            elif platform == "google":
                return self._check_google_status(driver)
            else:
                return self._check_generic_status(driver)
                
        except Exception as e:
            return False, f"Error check tài khoản: {str(e)}"
        finally:
            try:
                driver.quit()
            except:
                pass
    
    def _detect_platform_from_cookies(self, profile_name):
        """Tự động detect platform from cookies"""
        try:
            cookies = self.export_cookies_from_profile(profile_name)
            
            # Kiểm tra domain cookies
            domains = [cookie.get('domain', '') for cookie in cookies]
            
            if any('tiktok.com' in domain for domain in domains):
                return "tiktok"
            elif any('instagram.com' in domain for domain in domains):
                return "instagram"
            elif any('facebook.com' in domain for domain in domains):
                return "facebook"
            elif any('google.com' in domain or 'youtube.com' in domain for domain in domains):
                return "google"
            else:
                return "generic"
                
        except Exception as e:
            print(f"Error detect platform: {str(e)}")
            return "generic"
    
    def _check_tiktok_status(self, driver):
        """Kiểm tra trạng thái TikTok"""
        try:
            driver.get("https://www.tiktok.com")
            time.sleep(3)
            
            # Kiểm tra the element for found done login
            login_indicators = [
                "//div[contains(@class, 'avatar')]",
                "//div[contains(@class, 'user-avatar')]",
                "//button[contains(@class, 'upload')]",
                "//div[contains(@class, 'profile')]"
            ]
            
            for indicator in login_indicators:
                try:
                    element = driver.find_element("xpath", indicator)
                    if element:
                        return True, "Tài khoản TikTok còn hoạt động"
                except:
                    continue
            
            # Kiểm tra have button login không
            try:
                login_btn = driver.find_element("xpath", "//button[contains(text(), 'Log in') or contains(text(), 'Đăng input')]")
                if login_btn:
                    return False, "Tài khoản TikTok chưa login or done hết hạn"
            except:
                pass
            
            return False, "No thể xác định trạng thái TikTok"
            
        except Exception as e:
            return False, f"Error check TikTok: {str(e)}"
    
    def _check_generic_status(self, driver):
        """Kiểm tra trạng thái generic"""
        try:
            # Lấy URL hiện tại
            current_url = driver.current_url
            
            # Kiểm tra have from khóa login in URL
            if any(keyword in current_url.lower() for keyword in ['login', 'signin', 'auth', 'dang-nhap']):
                return False, "Tài khoản chưa login or done hết hạn"
            
            # Kiểm tra have form login
            try:
                login_forms = driver.find_elements("xpath", "//form[contains(@class, 'login') or contains(@id, 'login')]")
                if login_forms:
                    return False, "Tài khoản chưa login or done hết hạn"
            except:
                pass
            
            return True, "Tài khoản have vẻ còn hoạt động"
            
        except Exception as e:
            return False, f"Error check generic: {str(e)}"
    
    def batch_check_accounts(self, profile_list=None):
        """Kiểm tra trạng thái hàng loạt tài khoản"""
        try:
            if profile_list is None:
                profile_list = self.get_all_profiles()
            
            results = {}
            
            for profile in profile_list:
                print(f"Đang check profile: {profile}")
                status, message = self.check_account_status(profile)
                results[profile] = {
                    'status': status,
                    'message': message,
                    'platform': self._detect_platform_from_cookies(profile)
                }
                time.sleep(2)  # Delay giữa the lần check
            
            return results
            
        except Exception as e:
            print(f"Error check hàng loạt: {str(e)}")
            return {}
    
    def get_country_flag(self, country_code):
        """Lấy emoji lá cờ from country code"""
        flag_map = {
            'AD': '🇦🇩', 'AE': '🇦🇪', 'AF': '🇦🇫', 'AG': '🇦🇬', 'AI': '🇦🇮', 'AL': '🇦🇱', 'AM': '🇦🇲', 'AO': '🇦🇴',
            'AQ': '🇦🇶', 'AR': '🇦🇷', 'AS': '🇦🇸', 'AT': '🇦🇹', 'AU': '🇦🇺', 'AW': '🇦🇼', 'AX': '🇦🇽', 'AZ': '🇦🇿',
            'BA': '🇧🇦', 'BB': '🇧🇧', 'BD': '🇧🇩', 'BE': '🇧🇪', 'BF': '🇧🇫', 'BG': '🇧🇬', 'BH': '🇧🇭', 'BI': '🇧🇮',
            'BJ': '🇧🇯', 'BL': '🇧🇱', 'BM': '🇧🇲', 'BN': '🇧🇳', 'BO': '🇧🇴', 'BQ': '🇧🇶', 'BR': '🇧🇷', 'BS': '🇧🇸',
            'BT': '🇧🇹', 'BV': '🇧🇻', 'BW': '🇧🇼', 'BY': '🇧🇾', 'BZ': '🇧🇿', 'CA': '🇨🇦', 'CC': '🇨🇨', 'CD': '🇨🇩',
            'CF': '🇨🇫', 'CG': '🇨🇬', 'CH': '🇨🇭', 'CI': '🇨🇮', 'CK': '🇨🇰', 'CL': '🇨🇱', 'CM': '🇨🇲', 'CN': '🇨🇳',
            'CO': '🇨🇴', 'CR': '🇨🇷', 'CU': '🇨🇺', 'CV': '🇨🇻', 'CW': '🇨🇼', 'CX': '🇨🇽', 'CY': '🇨🇾', 'CZ': '🇨🇿',
            'DE': '🇩🇪', 'DJ': '🇩🇯', 'DK': '🇩🇰', 'DM': '🇩🇲', 'DO': '🇩🇴', 'DZ': '🇩🇿', 'EC': '🇪🇨', 'EE': '🇪🇪',
            'EG': '🇪🇬', 'EH': '🇪🇭', 'ER': '🇪🇷', 'ES': '🇪🇸', 'ET': '🇪🇹', 'FI': '🇫🇮', 'FJ': '🇫🇯', 'FK': '🇫🇰',
            'FM': '🇫🇲', 'FO': '🇫🇴', 'FR': '🇫🇷', 'GA': '🇬🇦', 'GB': '🇬🇧', 'GD': '🇬🇩', 'GE': '🇬🇪', 'GF': '🇬🇫',
            'GG': '🇬🇬', 'GH': '🇬🇭', 'GI': '🇬🇮', 'GL': '🇬🇱', 'GM': '🇬🇲', 'GN': '🇬🇳', 'GP': '🇬🇵', 'GQ': '🇬🇶',
            'GR': '🇬🇷', 'GS': '🇬🇸', 'GT': '🇬🇹', 'GU': '🇬🇺', 'GW': '🇬🇼', 'GY': '🇬🇾', 'HK': '🇭🇰', 'HM': '🇭🇲',
            'HN': '🇭🇳', 'HR': '🇭🇷', 'HT': '🇭🇹', 'HU': '🇭🇺', 'ID': '🇮🇩', 'IE': '🇮🇪', 'IL': '🇮🇱', 'IM': '🇮🇲',
            'IN': '🇮🇳', 'IO': '🇮🇴', 'IQ': '🇮🇶', 'IR': '🇮🇷', 'IS': '🇮🇸', 'IT': '🇮🇹', 'JE': '🇯🇪', 'JM': '🇯🇲',
            'JO': '🇯🇴', 'JP': '🇯🇵', 'KE': '🇰🇪', 'KG': '🇰🇬', 'KH': '🇰🇭', 'KI': '🇰🇮', 'KM': '🇰🇲', 'KN': '🇰🇳',
            'KP': '🇰🇵', 'KR': '🇰🇷', 'KW': '🇰🇼', 'KY': '🇰🇾', 'KZ': '🇰🇿', 'LA': '🇱🇦', 'LB': '🇱🇧', 'LC': '🇱🇨',
            'LI': '🇱🇮', 'LK': '🇱🇰', 'LR': '🇱🇷', 'LS': '🇱🇸', 'LT': '🇱🇹', 'LU': '🇱🇺', 'LV': '🇱🇻', 'LY': '🇱🇾',
            'MA': '🇲🇦', 'MC': '🇲🇨', 'MD': '🇲🇩', 'ME': '🇲🇪', 'MF': '🇲🇫', 'MG': '🇲🇬', 'MH': '🇲🇭', 'MK': '🇲🇰',
            'ML': '🇲🇱', 'MM': '🇲🇲', 'MN': '🇲🇳', 'MO': '🇲🇴', 'MP': '🇲🇵', 'MQ': '🇲🇶', 'MR': '🇲🇷', 'MS': '🇲🇸',
            'MT': '🇲🇹', 'MU': '🇲🇺', 'MV': '🇲🇻', 'MW': '🇲🇼', 'MX': '🇲🇽', 'MY': '🇲🇾', 'MZ': '🇲🇿', 'NA': '🇳🇦',
            'NC': '🇳🇨', 'NE': '🇳🇪', 'NF': '🇳🇫', 'NG': '🇳🇬', 'NI': '🇳🇮', 'NL': '🇳🇱', 'NO': '🇳🇴', 'NP': '🇳🇵',
            'NR': '🇳🇷', 'NU': '🇳🇺', 'NZ': '🇳🇿', 'OM': '🇴🇲', 'PA': '🇵🇦', 'PE': '🇵🇪', 'PF': '🇵🇫', 'PG': '🇵🇬',
            'PH': '🇵🇭', 'PK': '🇵🇰', 'PL': '🇵🇱', 'PM': '🇵🇲', 'PN': '🇵🇳', 'PR': '🇵🇷', 'PS': '🇵🇸', 'PT': '🇵🇹',
            'PW': '🇵🇼', 'PY': '🇵🇾', 'QA': '🇶🇦', 'RE': '🇷🇪', 'RO': '🇷🇴', 'RS': '🇷🇸', 'RU': '🇷🇺', 'RW': '🇷🇼',
            'SA': '🇸🇦', 'SB': '🇸🇧', 'SC': '🇸🇨', 'SD': '🇸🇩', 'SE': '🇸🇪', 'SG': '🇸🇬', 'SH': '🇸🇭', 'SI': '🇸🇮',
            'SJ': '🇸🇯', 'SK': '🇸🇰', 'SL': '🇸🇱', 'SM': '🇸🇲', 'SN': '🇸🇳', 'SO': '🇸🇴', 'SR': '🇸🇷', 'SS': '🇸🇸',
            'ST': '🇸🇹', 'SV': '🇸🇻', 'SX': '🇸🇽', 'SY': '🇸🇾', 'SZ': '🇸🇿', 'TC': '🇹🇨', 'TD': '🇹🇩', 'TF': '🇹🇫',
            'TG': '🇹🇬', 'TH': '🇹🇭', 'TJ': '🇹🇯', 'TK': '🇹🇰', 'TL': '🇹🇱', 'TM': '🇹🇲', 'TN': '🇹🇳', 'TO': '🇹🇴',
            'TR': '🇹🇷', 'TT': '🇹🇹', 'TV': '🇹🇻', 'TW': '🇹🇼', 'TZ': '🇹🇿', 'UA': '🇺🇦', 'UG': '🇺🇬', 'UM': '🇺🇲',
            'US': '🇺🇸', 'UY': '🇺🇾', 'UZ': '🇺🇿', 'VA': '🇻🇦', 'VC': '🇻🇨', 'VE': '🇻🇪', 'VG': '🇻🇬', 'VI': '🇻🇮',
            'VN': '🇻🇳', 'VU': '🇻🇺', 'WF': '🇼🇫', 'WS': '🇼🇸', 'YE': '🇾🇪', 'YT': '🇾🇹', 'ZA': '🇿🇦', 'ZM': '🇿🇲',
            'ZW': '🇿🇼',
            'LOC': '[HOME]'  # Local Network
        }
        return flag_map.get(country_code.upper(), '[FLAG]')
    
    def get_all_profiles(self, force_refresh=False):
        """Lấy danh sách all profiles
        
        Args:
            force_refresh: Force refresh from file system (tránh cache)
        """
        profiles = []
        if os.path.exists(self.profiles_dir):
            try:
                # Force refresh if cần
                if force_refresh:
                    time.sleep(0.1)  # Delay nhỏ to tránh cache
                
                for item in os.listdir(self.profiles_dir):
                    item_path = os.path.join(self.profiles_dir, item)
                    if os.path.isdir(item_path):
                        profiles.append(item)
                
                print(f"[CREATE] [PROFILES] Found {len(profiles)} profiles: {profiles}")
            except Exception as e:
                print(f"[WARNING] [PROFILES] Error when read profiles: {e}")
                
        return profiles
    
    def delete_profile(self, profile_name):
        """Xóa profile"""
        try:
            profile_path = os.path.join(self.profiles_dir, profile_name)
            # Try load TikTok session to identify associated account for cleanup in bulk_run_data.json
            account_identifier = None
            try:
                success, session_data = self.load_tiktok_session(profile_name)
                if success and isinstance(session_data, dict):
                    account_identifier = (session_data.get('username') or session_data.get('email') or '').strip()
                    if not account_identifier:
                        account_identifier = None
            except Exception:
                account_identifier = None
            if os.path.exists(profile_path):
                # Try to delete with retry mechanism
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        # First try normal deletion
                        shutil.rmtree(profile_path)
                        break
                    except PermissionError as e:
                        if attempt < max_retries - 1:
                            print(f"Lần try {attempt + 1}: No thể delete {profile_path}, doing try lại...")
                            time.sleep(2)
                            continue
                        else:
                            # Last attempt: try to force delete locked files
                            print(f"Thử delete force for {profile_path}")
                            self._force_delete_directory(profile_path)
                            break
                    except Exception as e:
                        if attempt < max_retries - 1:
                            print(f"Lần try {attempt + 1}: Error when delete {profile_path}: {str(e)}, doing try lại...")
                            time.sleep(2)
                            continue
                        else:
                            raise e
                
                # Xóa khỏi config
                if self.config.has_section('PROFILES') and self.config.has_option('PROFILES', profile_name):
                    self.config.remove_option('PROFILES', profile_name)
                
                
                # Xóa login data if have
                if self.config.has_section('LOGIN_DATA') and self.config.has_option('LOGIN_DATA', profile_name):
                    self.config.remove_option('LOGIN_DATA', profile_name)
                
                # Option B: Also remove associated account from bulk_run_data.json
                try:
                    bulk_path = os.path.join(os.getcwd(), 'bulk_run_data.json')
                    if os.path.exists(bulk_path) and account_identifier:
                        import json as _json
                        with open(bulk_path, 'r', encoding='utf-8') as bf:
                            try:
                                bulk_data = _json.load(bf)
                            except Exception:
                                bulk_data = {}
                        accounts_field = bulk_data.get('accounts', '')
                        changed = False
                        if isinstance(accounts_field, str) and accounts_field:
                            # accounts may be newline or comma separated or single
                            raw_lines = [ln.strip() for ln in accounts_field.replace('\r','').split('\n') if ln.strip()]
                            new_lines = []
                            for ln in raw_lines:
                                # expected format: username|password
                                parts = ln.split('|')
                                user = parts[0].strip() if parts else ''
                                if account_identifier and user and user.lower() == account_identifier.lower():
                                    changed = True
                                    continue
                                new_lines.append(ln)
                            if changed:
                                bulk_data['accounts'] = ('\n'.join(new_lines)) if new_lines else ''
                        elif isinstance(accounts_field, list):
                            new_list = []
                            for entry in accounts_field:
                                try:
                                    parts = str(entry).split('|')
                                    user = parts[0].strip() if parts else ''
                                    if account_identifier and user and user.lower() == account_identifier.lower():
                                        changed = True
                                        continue
                                except Exception:
                                    pass
                                new_list.append(entry)
                            if changed:
                                bulk_data['accounts'] = new_list
                        if changed:
                            with open(bulk_path, 'w', encoding='utf-8') as bf:
                                _json.dump(bulk_data, bf, ensure_ascii=False, indent=2)
                            print(f"[BULK-DATA] Removed TikTok account '{account_identifier}' from bulk_run_data.json")
                except Exception as _bd_err:
                    print(f"[WARNING] [BULK-DATA] Could not update bulk_run_data.json: {_bd_err}")
                
                self.save_config()
                
                return True, f"Done delete profile '{profile_name}' and the cấu hình liên quan"
            else:
                return False, f"Profile '{profile_name}' không tồn tại"
                
        except Exception as e:
            return False, f"Error when delete profile: {str(e)}"
    
    def _force_delete_directory(self, directory_path):
        """Force delete directory by removing files one by one"""
        try:
            import stat
            for root, dirs, files in os.walk(directory_path, topdown=False):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        # Remove read-only attribute
                        os.chmod(file_path, stat.S_IWRITE)
                        os.remove(file_path)
                    except (OSError, PermissionError) as e:
                        print(f"No thể delete file {file_path}: {str(e)}")
                        # Try to rename and delete later
                        try:
                            temp_name = file_path + ".tmp"
                            os.rename(file_path, temp_name)
                            os.remove(temp_name)
                        except:
                            pass
                
                for dir in dirs:
                    dir_path = os.path.join(root, dir)
                    try:
                        os.rmdir(dir_path)
                    except (OSError, PermissionError):
                        pass
            
            # Finally try to remove the main directory
            try:
                os.rmdir(directory_path)
            except (OSError, PermissionError):
                pass
                
        except Exception as e:
            print(f"Error in force delete: {str(e)}")
    
    def _cleanup_profile(self, profile_path):
        """Dọn dẹp profile trước when start Chrome"""
        try:
            print(f"DEBUG: Đang dọn dẹp profile: {profile_path}")
            
            # Các file/folder cần delete to tránh crash
            cleanup_items = [
                "SingletonLock",
                "SingletonSocket", 
                "SingletonCookie",
                "lockfile",
                "chrome_shutdown_ms.txt",
                "CrashpadMetrics.pma",
                "Default/Network/Cookies",
                "Default/Network/Cookies-journal",
                "Default/Safe Browsing Network/Safe Browsing Cookies",
                "Default/Sessions/Tabs_*",
                "Default/Extension State/000003.log",
                "Default/Extension State/000004.log",
                "Default/Extension State/000005.log"
            ]
            
            for item in cleanup_items:
                item_path = os.path.join(profile_path, item)
                if os.path.exists(item_path):
                    try:
                        if os.path.isfile(item_path):
                            os.remove(item_path)
                            print(f"DEBUG: Done delete file: {item}")
                        elif os.path.isdir(item_path):
                            shutil.rmtree(item_path)
                            print(f"DEBUG: Done delete folder: {item}")
                    except Exception as e:
                        print(f"DEBUG: No thể delete {item}: {str(e)}")
            
            # Xóa the file lock khác
            for root, dirs, files in os.walk(profile_path):
                for file in files:
                    if file.startswith("lockfile") or file.endswith(".lock"):
                        try:
                            os.remove(os.path.join(root, file))
                            print(f"DEBUG: Done delete lock file: {file}")
                        except:
                            pass
            
            print(f"DEBUG: Hoàn thành dọn dẹp profile: {profile_path}")
            
        except Exception as e:
            print(f"DEBUG: Error when dọn dẹp profile: {str(e)}")
    
    def _kill_chrome_processes(self):
        """Kill all Chrome processes to tránh conflict"""
        try:
            print("DEBUG: Killing all Chrome processes...")
            import psutil
            
            killed_count = 0
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if proc.info['name'] and 'chrome' in proc.info['name'].lower():
                        proc.kill()
                        killed_count += 1
                        print(f"DEBUG: Killed Chrome process: {proc.info['pid']}")
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
            
            if killed_count > 0:
                print(f"DEBUG: Killed {killed_count} Chrome processes")
                time.sleep(2)  # Waiting for processes to be killed completely
            else:
                print("DEBUG: No Chrome processes running")
                
        except Exception as e:
            print(f"DEBUG: Error killing Chrome processes: {str(e)}")
    
    import urllib.parse
    
    def save_tiktok_session(self, profile_name, session_data):
        """Lưu TikTok session ando Chrome profile"""
        try:
            print(f"💾 [SAVE-SESSION] Lưu TikTok session for {profile_name}")
            
            # Lưu ando config file
            if not self.config.has_section('TIKTOK_SESSIONS'):
                self.config.add_section('TIKTOK_SESSIONS')
            
            # Thêm timestamp
            from datetime import datetime
            session_data['saved_at'] = datetime.now().isoformat()
            session_data['updated_at'] = datetime.now().isoformat()
            
            # Lưu session data
            import json
            session_json = json.dumps(session_data, ensure_ascii=False)
            self.config.set('TIKTOK_SESSIONS', profile_name, session_json)
            self.save_config()
            
            # Lưu ando Chrome profile directory
            profile_path = os.path.join(self.profiles_dir, profile_name)
            if os.path.exists(profile_path):
                session_file = os.path.join(profile_path, 'tiktok_session.json')
                with open(session_file, 'w', encoding='utf-8') as f:
                    json.dump(session_data, f, ensure_ascii=False, indent=2)
                print(f"[SUCCESS] [SAVE-SESSION] Done save session ando {session_file}")
                
                # Tạo marker file để đánh dấu profile đã đăng nhập
                marker_file = os.path.join(profile_path, 'tiktok_logged_in.txt')
                username_or_email = session_data.get('username', session_data.get('email', ''))
                with open(marker_file, 'w', encoding='utf-8') as f:
                    f.write(f"username={username_or_email}\n")
                    f.write(f"email={session_data.get('email', '')}\n")
                    f.write(f"timestamp={time.time()}\n")
                    f.write(f"url=https://www.tiktok.com\n")
                print(f"[SUCCESS] [SAVE-SESSION] Done save marker file: {marker_file}")
            
            return True, f"Done save TikTok session for {profile_name}"
            
        except Exception as e:
            return False, f"Error when save session: {str(e)}"
    
    def load_tiktok_session(self, profile_name):
        """Load TikTok session from Chrome profile"""
        try:
            print(f"📂 [LOAD-SESSION] Load TikTok session for {profile_name}")
            
            # Thử load from config file trước
            if self.config.has_section('TIKTOK_SESSIONS') and self.config.has_option('TIKTOK_SESSIONS', profile_name):
                import json
                session_json = self.config.get('TIKTOK_SESSIONS', profile_name)
                session_data = json.loads(session_json)
                print(f"[SUCCESS] [LOAD-SESSION] Done load session from config")
                return True, session_data
            
            # Thử load from Chrome profile directory
            profile_path = os.path.join(self.profiles_dir, profile_name)
            session_file = os.path.join(profile_path, 'tiktok_session.json')
            
            if os.path.exists(session_file):
                import json
                with open(session_file, 'r', encoding='utf-8') as f:
                    session_data = json.load(f)
                print(f"[SUCCESS] [LOAD-SESSION] Done load session from {session_file}")
                return True, session_data
            
            print(f"[WARNING] [LOAD-SESSION] No find found session for {profile_name}")
            return False, "No find found TikTok session"
            
        except Exception as e:
            return False, f"Error when load session: {str(e)}"
    
    def get_all_tiktok_sessions(self):
        """Lấy all TikTok sessions"""
        try:
            sessions = {}
            
            if self.config.has_section('TIKTOK_SESSIONS'):
                import json
                for profile_name in self.config.options('TIKTOK_SESSIONS'):
                    try:
                        session_json = self.config.get('TIKTOK_SESSIONS', profile_name)
                        session_data = json.loads(session_json)
                        sessions[profile_name] = session_data
                    except:
                        continue
            
            return True, sessions
            
        except Exception as e:
            return False, f"Error when lấy sessions: {str(e)}"
    
    def clear_tiktok_session(self, profile_name):
        """Xóa TikTok session"""
        try:
            print(f"[REMOVE] [CLEAR-SESSION] Xóa TikTok session for {profile_name}")
            
            # Xóa from config
            if self.config.has_section('TIKTOK_SESSIONS') and self.config.has_option('TIKTOK_SESSIONS', profile_name):
                self.config.remove_option('TIKTOK_SESSIONS', profile_name)
                self.save_config()
            
            # Xóa from Chrome profile directory
            profile_path = os.path.join(self.profiles_dir, profile_name)
            session_file = os.path.join(profile_path, 'tiktok_session.json')
            
            if os.path.exists(session_file):
                os.remove(session_file)
                print(f"[SUCCESS] [CLEAR-SESSION] Done delete session file")
            
            return True, f"Done delete TikTok session for {profile_name}"
            
        except Exception as e:
            return False, f"Error when delete session: {str(e)}"

    def kill_chrome_processes(self):
        """Tắt all tiến trình Chrome"""
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                if 'chrome' in proc.info['name'].lower():
                    proc.kill()
            return True, "Done tắt all tiến trình Chrome"
        except Exception as e:
            return False, f"Error when tắt Chrome: {str(e)}"
    
    def auto_start_profiles(self):
        """Tự động start the profiles get cấu hình"""
        if not self.config.getboolean('SETTINGS', 'auto_start', fallback=False):
            return
        
        delay = self.config.getint('SETTINGS', 'startup_delay', fallback=5)
        time.sleep(delay)
        
        profiles = self.get_all_profiles()
        for profile in profiles:
            hidden = self.config.getboolean('SETTINGS', 'hidden_mode', fallback=True)
            self.launch_chrome_profile(profile, hidden=hidden)
            time.sleep(2)  # Delay giữa the profiles

    def _apply_base_chrome_config(self, chrome_options, hidden=True):
        """Apply base Chrome configuration - Minimal flags like GPM Login"""
        # Chỉ giữ lại the flags cần thiết nhất như GPM Login
        # No thêm flags thừa to giảm độ dài command line
        
        # Disable automation detection
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Window settings - Chỉ thêm when cần thiết
        if hidden:
            chrome_options.add_argument("--headless")
        # No thêm window-size to giảm command line
        
        # Livestream/Media autoplay flags (always add for compatibility)
        chrome_options.add_argument("--autoplay-policy=no-user-gesture-required")
        try:
            chrome_options.add_argument("--use-fake-ui-for-media-stream")
        except Exception:
            pass  # Flag may not be supported in some Chrome versions

    def _apply_optimized_chrome_config(self, chrome_options, hidden=True, ultra_low_memory=False):
        """Apply optimized Chrome configuration - Minimal flags like GPM Login"""
        # Chỉ giữ lại the flags cần thiết nhất to giảm độ dài command line
        
        # === AUTOMATION DETECTION BYPASS ===
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # === WINDOW SETTINGS ===
        if hidden:
            chrome_options.add_argument("--headless")
        # No thêm window-size to giảm command line
        
        print(f"[TOOL] [CHROME-OPTIMIZE] Applied minimal flags configuration")

    def get_memory_usage(self):
        """Lấy thông tin sử dụng RAM of Chrome processes"""
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
            print(f"[WARNING] [MEMORY] Error when lấy thông tin memory: {e}")
            return None

    def cleanup_memory(self):
        """Dọn dẹp memory and optimize hóa"""
        try:
            import gc
            import psutil
            
            # Force garbage collection
            gc.collect()
            
            # Get current memory usage
            memory_info = self.get_memory_usage()
            if memory_info:
                print(f"[CLEANUP] [MEMORY-CLEANUP] Chrome RAM: {memory_info['chrome_memory_mb']}MB")
                print(f"[CLEANUP] [MEMORY-CLEANUP] System RAM: {memory_info['system_memory_percent']}%")
                print(f"[CLEANUP] [MEMORY-CLEANUP] Available: {memory_info['available_memory_gb']}GB")
            
            return memory_info
        except Exception as e:
            print(f"[WARNING] [MEMORY-CLEANUP] Error: {e}")
            return None

    def _launch_chrome_with_fallback(self, chrome_options, profile_path, hidden):
        """Launch Chrome with fallback mechanism"""
        from selenium import webdriver
        # Dùng Selenium Manager tự chọn chromedriver theo binary
        
        # Try main configuration
        try:
            # Chọn chromedriver khớp version
            desired_version = ''
            try:
                # read from settings in profile
                settings_probe = os.path.join(profile_path, 'profile_settings.json')
                if os.path.exists(settings_probe):
                    import json as _json
                    with open(settings_probe, 'r', encoding='utf-8') as sf:
                        _ps = _json.load(sf)
                        desired_version = ((_ps.get('software') or {}).get('browser_version') or '').strip()
            except Exception:
                pass
            # BẮT BUỘC: áp dụng Chrome binary đúng desired_version trước when create driver
            self._apply_custom_chrome_binary(chrome_options, profile_path, desired_version)
            
            # Loại bỏ automation flags to tránh detection
            self._remove_automation_flags(chrome_options)
            
            # Thêm excludeSwitches để loại bỏ automation flags từ Selenium
            chrome_options.add_experimental_option("excludeSwitches", [
                "enable-automation",
                "enable-logging",
                "disable-logging",
                "log-level",
                "disable-background-networking",
                "disable-backgrounding-occluded-windows",
                "disable-client-side-phishing-detection",
                "disable-default-apps",
                "disable-hang-monitor",
                "disable-popup-blocking",
                "disable-prompt-on-repost",
                "disable-sync",
                "no-service-autorun",
                "no-first-run",
                "password-store",
                "remote-debugging-port",
                "test-type",
                "use-mock-keychain",
                "allow-pre-commit-input"
            ])
            
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            
            # Tối ưu hóa command line bằng function fix
            try:
                from fix_chrome_command import fix_chrome_command, create_rules_from_gpm_config
                
                # Tạo command line hiện tại
                args_attr = None
                if hasattr(chrome_options, 'arguments'):
                    args_attr = 'arguments'
                elif hasattr(chrome_options, '_arguments'):
                    args_attr = '_arguments'
                
                if args_attr:
                    args = list(getattr(chrome_options, args_attr) or [])
                    current_command = 'chrome.exe ' + ' '.join([str(arg) for arg in args])
                    
                    # Tạo rules từ GPM config
                    rules = create_rules_from_gpm_config(gpm_config)
                    rules['user_data_dir'] = profile_path
                    
                    # Fix command line
                    fixed_command = fix_chrome_command(current_command, rules)
                    
                    if not fixed_command.startswith('ERROR:'):
                        # Parse fixed command và cập nhật chrome_options
                        import shlex
                        fixed_parts = shlex.split(fixed_command)
                        if len(fixed_parts) > 1:
                            fixed_args = fixed_parts[1:]  # Bỏ executable path
                            chrome_options._arguments = fixed_args
                            print(f"[COMMAND-FIX] Fixed fallback command line: {len(fixed_args)} flags")
                else:
                    print(f"[COMMAND-FIX] Error fixing fallback command line: {str(e)}")
                    
            except Exception as e:
                print(f"[COMMAND-FIX] Error fixing fallback command line: {str(e)}")
            
            driver_path = self._ensure_cft_chromedriver(desired_version)
            if driver_path and os.path.exists(driver_path):
                service = Service(executable_path=driver_path)
                driver = webdriver.Chrome(service=service, options=chrome_options)
            else:
                # Cố gắng tránh Selenium Manager tự lấy sai version: if không have driver, vẫn cố tải theo major
                driver_path = self._ensure_cft_chromedriver(desired_version or '0')
                if driver_path and os.path.exists(driver_path):
                    service = Service(executable_path=driver_path)
                    driver = webdriver.Chrome(service=service, options=chrome_options)
                else:
                    # Loại bỏ automation flags in fallback case
                    self._remove_automation_flags(chrome_options)
                    driver = webdriver.Chrome(options=chrome_options)
            driver.set_page_load_timeout(30)
            driver.implicitly_wait(10)
            
            # Fix window size and position to prevent click misalignment
            try:
                driver.set_window_size(1366, 768)
                print("[SUCCESS] [WINDOW] Set window size to 1366x768")
            except Exception as window_error:
                print(f"[WARNING] [WINDOW] Could not set window size: {window_error}")
            
            # Set window position to top-left corner (0, 0)
            try:
                driver.set_window_position(0, 0)
                print("[SUCCESS] [WINDOW] Set window position to (0, 0) - top-left corner")
            except Exception as position_error:
                print(f"[WARNING] [WINDOW] Could not set window position: {position_error}")
            
            # Lock virtual viewport to ensure consistent coordinates
            try:
                # Use CDP to set device metrics for consistent viewport
                device_metrics = {
                    'width': 1366,
                    'height': 768,
                    'deviceScaleFactor': 1.0,
                    'mobile': False
                }
                driver.execute_cdp_cmd('Emulation.setDeviceMetricsOverride', device_metrics)
                print("[SUCCESS] [VIEWPORT] Locked virtual viewport to 1366x768")
            except Exception as viewport_error:
                print(f"[WARNING] [VIEWPORT] Could not lock viewport: {viewport_error}")
            
            # Inject OMOcaptcha API key into extension storage (safe, no Preferences writes)
            try:
                self._inject_omocaptcha_key_via_driver(driver, profile_path)
            except Exception:
                pass
            
            # Ensure window is in focus
            try:
                driver.switch_to.window(driver.current_window_handle)
                print("[SUCCESS] [FOCUS] Window focused")
            except Exception as focus_error:
                print(f"[WARNING] [FOCUS] Could not focus window: {focus_error}")
            
            # Apply User-Agent override and GPM anti-detection script
            try:
                # 1. Override User-Agent qua CDP to tránh mismatch
                try:
                    driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                        'userAgent': driver.execute_script("return navigator.userAgent"),
                        'acceptLanguage': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7',
                        'platform': 'Win32'
                    })
                    print("[SUCCESS] [CDP] User-Agent override applied")
                except Exception as e:
                    print(f"[WARNING] [CDP] User-Agent override failed: {e}")
                
                # 2. Apply GPM anti-detection script
                if GPM_FLAGS_AVAILABLE:
                    antidetect_script = gpm_config.get_antidetect_script()
                    driver.execute_script(antidetect_script)
                    print("[SUCCESS] [GPM-ANTIDETECT] Applied GPM anti-detection script")
                else:
                    # Fallback basic anti-detection
                    basic_script = """
                    // Loại bỏ webdriver properties
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined,
                    });
                    
                    // Loại bỏ automation indicators
                    delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
                    delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
                    delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
                    
                    // Spoof plugins to tránh detection
                    Object.defineProperty(navigator, 'plugins', {
                        get: () => [1, 2, 3, 4, 5],
                    });
                    
                    // Spoof languages
                    Object.defineProperty(navigator, 'languages', {
                        get: () => ['vi-VN', 'vi', 'en-US', 'en'],
                    });
                    
                    // Spoof chrome object
                    window.chrome = {
                        runtime: {},
                        loadTimes: function() {},
                        csi: function() {},
                        app: {}
                    };
                    
                    // Loại bỏ automation flags
                    Object.defineProperty(navigator, 'permissions', {
                        get: () => ({
                            query: () => Promise.resolve({ state: 'granted' })
                        })
                    });
                    """
                    driver.execute_script(basic_script)
                    print("[SUCCESS] [ANTIDETECT] Applied basic anti-detection script")
            except Exception as e:
                print(f"[WARNING] [ANTIDETECT] Error applying anti-detection script: {e}")
            
            print(f"[SUCCESS] [LAUNCH] Chrome started successfully")
            return driver
            
        except Exception as e:
            print(f"[ERROR] [LAUNCH] Fallback failed: {str(e)}")
            return None

    def _launch_chrome_native_fixed(self, chrome_options, profile_path, start_url=None):
        """Launch Chrome natively (visible) without WebDriver to avoid remote-debugging-port flag.
        Keeps all other flags intact, removes only automation-related ones, and runs
        fix_chrome_command as the final normalization step.
        """
        import subprocess as _subprocess
        import shlex as _shlex
        try:
            # Resolve desired version from profile metadata
            desired_version = ''
            try:
                settings_probe = os.path.join(profile_path, 'profile_settings.json')
                if os.path.exists(settings_probe):
                    import json as _json
                    with open(settings_probe, 'r', encoding='utf-8') as sf:
                        _ps = _json.load(sf)
                        desired_version = ((_ps.get('software') or {}).get('browser_version') or '').strip()
                if not desired_version:
                    last_version_fp = os.path.join(profile_path, 'Last Version')
                    if os.path.exists(last_version_fp):
                        try:
                            with open(last_version_fp, 'r', encoding='utf-8') as lvf:
                                desired_version = lvf.read().strip()
                        except Exception:
                            pass
            except Exception:
                pass

            # Try to match Chrome binary to desired_version like fallback does
            chrome_path = ''
            try:
                gpm_candidate = self._gpm_chrome_path_for_version(desired_version)
                if gpm_candidate and os.path.exists(gpm_candidate):
                    chrome_path = gpm_candidate
            except Exception:
                pass
            if not chrome_path:
                try:
                    resolved = self._resolve_chrome_binary_path(desired_version)
                    if resolved:
                        chrome_path = resolved
                except Exception:
                    pass
            if not chrome_path and desired_version:
                try:
                    cft = self._ensure_cft_chrome_binary(desired_version)
                    if cft and os.path.exists(cft):
                        chrome_path = cft
                except Exception:
                    pass
            if not chrome_path:
                chrome_path = self.get_chrome_path()
            if not chrome_path:
                print("[ERROR] [NATIVE] Chrome executable not found")
                return False

            # Collect arguments from Options or a plain list
            if hasattr(chrome_options, 'arguments'):
                args = list(chrome_options.arguments or [])
            elif hasattr(chrome_options, '_arguments'):
                args = list(chrome_options._arguments or [])
            elif isinstance(chrome_options, (list, tuple)):
                args = list(chrome_options)
            else:
                args = []

            # Remove only the three problematic flags if present
            args = [a for a in args if not (
                str(a).startswith('--remote-debugging-port') or
                str(a) == '--no-first-run' or
                str(a).startswith('--log-level')
            )]

            # Final normalization via fix_chrome_command
            try:
                from fix_chrome_command import fix_chrome_command, create_rules_from_gpm_config, load_gpm_config
                # Ensure gpm_config is loaded in this scope
                try:
                    gpm_config_local = load_gpm_config()
                except Exception as _ge:
                    print(f"[COMMAND-FIX] Load gpm_config.json error: {_ge}")
                    gpm_config_local = None
                rules = create_rules_from_gpm_config(gpm_config_local)
                rules['user_data_dir'] = profile_path
                fixed = fix_chrome_command('chrome.exe ' + ' '.join([str(x) for x in args]), rules)
                parts = _shlex.split(fixed)
                if len(parts) > 1:
                    args = parts[1:]
            except Exception as _fe:
                print(f"[COMMAND-FIX] Native fix error: {_fe}")

            # Append start URL if provided (open desired page on launch)
            if start_url:
                try:
                    args = list(args) + [str(start_url)]
                except Exception:
                    pass

            # Launch visible Chrome natively
            _subprocess.Popen([chrome_path] + args,
                              stdout=_subprocess.DEVNULL,
                              stderr=_subprocess.DEVNULL,
                              creationflags=(_subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0))
            print("[SUCCESS] [NATIVE] Chrome started (visible) without remote-debugging-port")
            return True
        except Exception as _e:
            print(f"[ERROR] [NATIVE] Launch failed: {_e}")
            return False

    def _cleanup_profile_cache(self, profile_path):
        """Clean profile cache directories"""
        try:
            import shutil
            
            # Whitelist: only delete light-weight caches; preserve cookies and session data
            # IMPORTANT: Do NOT delete 'Network' because it contains Cookies DB
            SAFE_TO_DELETE = ['Cache', 'Code Cache', 'GPUCache']
            for folder in SAFE_TO_DELETE:
                folder_path = os.path.join(profile_path, 'Default', folder)
                if os.path.exists(folder_path):
                    try:
                        shutil.rmtree(folder_path, ignore_errors=True)
                        print(f"[CLEANUP] [CLEANUP] Cleaned: {folder}")
                    except Exception:
                        pass
                else:
                    print(f"[CLEANUP] [CLEANUP] Skipped: {folder} (not found)")
                        
        except Exception as e:
            print(f"[WARNING] [CLEANUP] Cache cleanup failed: {str(e)}")

    def _handle_auto_login(self, driver, profile_path, auto_login, login_data, start_url):
        """Handle auto login logic"""
        try:
            print(f"[DEBUG] [AUTOLOGIN] _handle_auto_login called")
            print(f"[DEBUG] [AUTOLOGIN] auto_login={auto_login}")
            print(f"[DEBUG] [AUTOLOGIN] login_data={login_data}")
            print(f"[DEBUG] [AUTOLOGIN] start_url={start_url}")
            
            # Check if profile is already logged in
            marker_file = os.path.join(profile_path, 'tiktok_logged_in.txt')
            
            if os.path.exists(marker_file):
                print(f"[SUCCESS] [LOGIN] Profile already logged in, loading cookies...")
                cookies_loaded = self._load_cookies_from_profile(profile_path, driver)
                if cookies_loaded:
                    # Navigate to TikTok to verify login
                    if start_url:
                        driver.get(start_url)
                    else:
                        driver.get("https://www.tiktok.com/foryou")
                    time.sleep(3)
                    
                    # Verify if still logged in
                    if self._verify_tiktok_login(driver):
                        print(f"[SUCCESS] [LOGIN] Successfully restored session from cookies!")
                        return True
                    else:
                        print(f"[WARNING] [LOGIN] Cookies expired, performing fresh login...")
                        # Remove expired marker
                        try:
                            os.remove(marker_file)
                        except:
                            pass
                else:
                    print(f"[WARNING] [LOGIN] Failed to load cookies, performing auto-login...")
            
            # Perform auto-login if requested
            if auto_login and login_data:
                print(f"[DEBUG] [AUTOLOGIN] Starting auto-login process...")
                if login_data:
                    print(f"[SECURITY] [LOGIN] Starting auto-login with provided data...")
                    if start_url:
                        print(f"[DEBUG] [AUTOLOGIN] Navigating to start_url: {start_url}")
                        driver.get(start_url)
                        time.sleep(2)
                    else:
                        login_url = login_data.get('login_url', 'https://www.tiktok.com/login')
                        print(f"[DEBUG] [AUTOLOGIN] Navigating to login_url: {login_url}")
                        driver.get(login_url)
                        time.sleep(2)
                    
                    print(f"[DEBUG] [AUTOLOGIN] Calling _perform_auto_login...")
                    login_success = self._perform_auto_login(driver, login_data, start_url)
                    if login_success:
                        print(f"[SUCCESS] [LOGIN] Auto-login successful")
                        return True
                    else:
                        print(f"[ERROR] [LOGIN] Auto-login failed")
                        return False
            else:
                print(f"[DEBUG] [AUTOLOGIN] No auto-login: auto_login={auto_login}, login_data={bool(login_data)}")
                return True
                
        except Exception as e:
            print(f"[ERROR] [LOGIN] Login handling failed: {str(e)}")
            return False

    def _verify_tiktok_login(self, driver):
        """Verify if user is logged in to TikTok"""
        try:
            current_url = driver.current_url.lower()
            print(f"[DEBUG] [VERIFY] Checking TikTok login status at: {current_url}")
            
            # Check if we're on TikTok domain
            if 'tiktok.com' not in current_url:
                print(f"[WARNING] [VERIFY] Not on TikTok domain")
                return False
            
            # Check for login indicators
            try:
                # Look for user avatar or profile elements
                avatar_selectors = [
                    '[data-e2e="nav-avatar"]',
                    '[data-e2e="user-avatar"]',
                    '.avatar',
                    '[class*="avatar"]',
                    '[class*="user"]'
                ]
                
                for selector in avatar_selectors:
                    try:
                        element = driver.find_element("css selector", selector)
                        if element and element.is_displayed():
                            print(f"[SUCCESS] [VERIFY] Found user avatar element: {selector}")
                            return True
                    except:
                        continue
                
                # Check for login button (if present, means not logged in)
                login_selectors = [
                    '[data-e2e="top-login-button"]',
                    'a[href*="/login"]',
                    'button[data-e2e*="login"]'
                ]
                
                for selector in login_selectors:
                    try:
                        element = driver.find_element("css selector", selector)
                        if element and element.is_displayed():
                            print(f"[ERROR] [VERIFY] Found login button, not logged in")
                            return False
                    except:
                        continue
                
                # Check page source for login indicators
                page_source = driver.page_source.lower()
                if 'login' in page_source and 'sign up' in page_source:
                    print(f"[ERROR] [VERIFY] Login page detected in source")
                    return False
                
                # If we reach here and no login elements found, assume logged in
                print(f"[SUCCESS] [VERIFY] No login elements found, assuming logged in")
                return True
                
            except Exception as e:
                print(f"[WARNING] [VERIFY] Error checking login status: {e}")
                return False
                
        except Exception as e:
            print(f"[ERROR] [VERIFY] Error verifying TikTok login: {e}")
            return False

    def is_profile_logged_in(self, profile_name):
        """Check if profile is logged in to TikTok"""
        try:
            profile_path = os.path.join(self.profiles_dir, profile_name)
            
            # Method 1: Check marker file
            marker_file = os.path.join(profile_path, 'tiktok_logged_in.txt')
            if os.path.exists(marker_file):
                # Check if marker file is recent (within 7 days)
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
                                    print(f"✅ [CHECK] {profile_name} - Logged in (marker file)")
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
                            print(f"✅ [CHECK] {profile_name} - Logged in (session data)")
                            return True
                        
                        # Check if has recent saved_at timestamp
                        saved_at = session_data.get('saved_at', '')
                        if saved_at:
                            try:
                                from datetime import datetime
                                dt = datetime.fromisoformat(saved_at)
                                current_time = datetime.now()
                                # Check if session is less than 7 days old
                                if (current_time - dt).days < 7:
                                    print(f"✅ [CHECK] {profile_name} - Logged in (recent session)")
                                    return True
                            except:
                                pass
                except:
                    pass
            
            # Method 3: Check if profile has TikTok cookies
            cookies_file = os.path.join(profile_path, 'Default', 'Cookies')
            if os.path.exists(cookies_file):
                try:
                    # Check if cookies file is recent (within 7 days)
                    import time
                    mod_time = os.path.getmtime(cookies_file)
                    current_time = time.time()
                    if current_time - mod_time < 7 * 24 * 3600:
                        print(f"✅ [CHECK] {profile_name} - Logged in (recent cookies)")
                        return True
                except:
                    pass
            
            print(f"❌ [CHECK] {profile_name} - Not logged in")
            return False
            
        except Exception as e:
            print(f"[ERROR] [CHECK] Error checking login status for {profile_name}: {e}")
            return False
    
    def get_chrome_path(self):
        """
        Get the path to Chrome executable
        
        Returns:
            str: Path to Chrome executable, or None if not found
        """
        try:
            import shutil
            
            # Common Chrome paths on Windows
            chrome_paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                r"C:\Users\{}\AppData\Local\Google\Chrome\Application\chrome.exe".format(os.getenv('USERNAME')),
                r"C:\Users\{}\AppData\Local\Google\Chrome\Application\chrome.exe".format(os.getenv('USER')),
            ]
            
            # Try to find Chrome
            for chrome_path in chrome_paths:
                if os.path.exists(chrome_path):
                    print(f"[DEBUG] [CHROME-PATH] Found Chrome at: {chrome_path}")
                    return chrome_path
            
            # Try using shutil.which
            chrome_path = shutil.which("chrome")
            if chrome_path:
                print(f"[DEBUG] [CHROME-PATH] Found Chrome via which: {chrome_path}")
                return chrome_path
            
            # Try chrome.exe
            chrome_path = shutil.which("chrome.exe")
            if chrome_path:
                print(f"[DEBUG] [CHROME-PATH] Found Chrome.exe via which: {chrome_path}")
                return chrome_path
            
            print("[ERROR] [CHROME-PATH] Chrome executable not found")
            return None
            
        except Exception as e:
            print(f"[ERROR] [CHROME-PATH] Error finding Chrome: {str(e)}")
            return None
    
    def get_switchyomega_profiles(self, profile_name):
        """
        Get all proxy profiles from SwitchyOmega extension
        
        Args:
            profile_name (str): Name of the Chrome profile
        
        Returns:
            list: List of proxy profiles with their configurations
        """
        try:
            print(f"[DEBUG] [SWITCHYOMEGA] Getting profiles from: {profile_name}")
            
            # Get profile path
            profile_path = self.get_profile_path(profile_name)
            if not profile_path or not os.path.exists(profile_path):
                return []
            
            # Launch Chrome with the profile
            chrome_options = Options()
            self._apply_custom_chrome_binary(chrome_options, profile_path)
            chrome_options.add_argument(f"--user-data-dir={profile_path}")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1024,768")
            
            # Disable automation detection
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Tối ưu hóa command line bằng function fix
            try:
                from fix_chrome_command import fix_chrome_command, create_rules_from_gpm_config
                
                # Tạo command line hiện tại
                args_attr = None
                if hasattr(chrome_options, 'arguments'):
                    args_attr = 'arguments'
                elif hasattr(chrome_options, '_arguments'):
                    args_attr = '_arguments'
                
                if args_attr:
                    args = list(getattr(chrome_options, args_attr) or [])
                    current_command = 'chrome.exe ' + ' '.join([str(arg) for arg in args])
                    
                    # Tạo rules từ GPM config
                    rules = create_rules_from_gpm_config(gpm_config)
                    rules['user_data_dir'] = profile_path
                    
                    # Fix command line
                    fixed_command = fix_chrome_command(current_command, rules)
                    
                    if not fixed_command.startswith('ERROR:'):
                        # Parse fixed command và cập nhật chrome_options
                        import shlex
                        fixed_parts = shlex.split(fixed_command)
                        if len(fixed_parts) > 1:
                            fixed_args = fixed_parts[1:]  # Bỏ executable path
                            chrome_options._arguments = fixed_args
                            print(f"[COMMAND-FIX] Fixed switchyomega command line: {len(fixed_args)} flags")
                else:
                    print(f"[COMMAND-FIX] Error fixing switchyomega command line: {str(e)}")
                    
            except Exception as e:
                print(f"[COMMAND-FIX] Error fixing switchyomega command line: {str(e)}")
            
            from selenium import webdriver
            from selenium.webdriver.chrome.service import Service
            # from webdriver_manager.chrome import ChromeDriverManager
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            driver = webdriver.Chrome(options=chrome_options)
            
            try:
                # Navigate to SwitchyOmega options page
                driver.get("chrome-extension://pfnededegaaopdmhkdmcofjmoldfiped/options.html")
                driver.implicitly_wait(10)
                
                time.sleep(3)
                
                profiles = []
                
                # Wait for the extension to load
                wait = WebDriverWait(driver, 20)
                
                try:
                    # Try multiple methods to get profiles
                    
                    # Method 1: Get from localStorage
                    try:
                        js_code = """
                        var profiles = [];
                        try {
                            // Try different localStorage keys
                            var keys = ['switchyomega_profiles', 'profiles', 'switchyomega_data', 'proxy_profiles'];
                            
                            for (var i = 0; i < keys.length; i++) {
                                var data = localStorage.getItem(keys[i]);
                                if (data) {
                                    try {
                                        var parsed = JSON.parse(data);
                                        if (typeof parsed === 'object') {
                                            for (var key in parsed) {
                                                if (parsed[key] && parsed[key].name) {
                                                    profiles.push({
                                                        name: parsed[key].name,
                                                        type: parsed[key].type || parsed[key].protocol || 'http',
                                                        server: parsed[key].host || parsed[key].server || '',
                                                        port: parsed[key].port || '',
                                                        username: parsed[key].username || parsed[key].user || '',
                                                        password: parsed[key].password || parsed[key].pass || ''
                                                    });
                                                }
                                            }
                                        }
                                    } catch(e) {
                                        console.log('Error parsing data for key', keys[i], e);
                                    }
                                }
                            }
                            
                            // Also try to get from chrome.storage
                            if (profiles.length === 0) {
                                try {
                                    var storageData = localStorage.getItem('chrome_storage');
                                    if (storageData) {
                                        var storage = JSON.parse(storageData);
                                        if (storage.profiles) {
                                            for (var key in storage.profiles) {
                                                if (storage.profiles[key] && storage.profiles[key].name) {
                                                    profiles.push({
                                                        name: storage.profiles[key].name,
                                                        type: storage.profiles[key].type || 'http',
                                                        server: storage.profiles[key].host || '',
                                                        port: storage.profiles[key].port || '',
                                                        username: storage.profiles[key].username || '',
                                                        password: storage.profiles[key].password || ''
                                                    });
                                                }
                                            }
                                        }
                                    }
                                } catch(e) {
                                    console.log('Error getting from chrome.storage:', e);
                                }
                            }
                            
                        } catch(e) {
                            console.log('Error getting profiles:', e);
                        }
                        return profiles;
                        """
                        
                        profiles = driver.execute_script(js_code)
                        if not profiles:
                            profiles = []
                            
                    except Exception as e:
                        print(f"[WARNING] [SWITCHYOMEGA] Could not get profiles from localStorage: {str(e)}")
                    
                    # Method 2: Look for profile elements in the UI
                    if not profiles:
                        try:
                            # Look for profile list in the sidebar
                            profile_elements = driver.find_elements(By.XPATH, "//div[contains(@class, 'profile') or contains(@id, 'profile')]//span[contains(text(), '')]")
                            
                            for element in profile_elements:
                                try:
                                    profile_name_text = element.text.strip()
                                    if profile_name_text and profile_name_text not in ['Direct', 'System Proxy', '自动切换', 'Auto Switch']:
                                        profiles.append({
                                            'name': profile_name_text,
                                            'type': 'http',
                                            'server': '',
                                            'port': '',
                                            'username': '',
                                            'password': ''
                                        })
                                except:
                                    continue
                        except Exception as e:
                            print(f"[WARNING] [SWITCHYOMEGA] Could not get profiles from UI elements: {str(e)}")
                    
                    # Method 3: Try to click on profiles to get details
                    if profiles:
                        try:
                            for i, profile in enumerate(profiles):
                                if not profile['server']:  # Only get details if we don't have them
                                    try:
                                        # Look for profile in the sidebar and click it
                                        profile_element = driver.find_element(By.XPATH, f"//span[contains(text(), '{profile['name']}')]")
                                        profile_element.click()
                                        time.sleep(1)
                                        
                                        # Try to get proxy details
                                        try:
                                            server_field = driver.find_element(By.XPATH, "//input[@placeholder='Server' or @placeholder='服务器' or @name='host']")
                                            profile['server'] = server_field.get_attribute('value') or ''
                                        except:
                                            pass
                                        
                                        try:
                                            port_field = driver.find_element(By.XPATH, "//input[@placeholder='Port' or @placeholder='端口' or @name='port']")
                                            profile['port'] = port_field.get_attribute('value') or ''
                                        except:
                                            pass
                                        
                                        try:
                                            username_field = driver.find_element(By.XPATH, "//input[@placeholder='Username' or @placeholder='用户名' or @name='username']")
                                            profile['username'] = username_field.get_attribute('value') or ''
                                        except:
                                            pass
                                        
                                        try:
                                            password_field = driver.find_element(By.XPATH, "//input[@placeholder='Password' or @placeholder='密码' or @name='password']")
                                            profile['password'] = password_field.get_attribute('value') or ''
                                        except:
                                            pass
                                        
                                    except Exception as e:
                                        print(f"[WARNING] [SWITCHYOMEGA] Could not get details for profile {profile['name']}: {str(e)}")
                                        continue
                        except Exception as e:
                            print(f"[WARNING] [SWITCHYOMEGA] Could not get profile details: {str(e)}")
                    
                    print(f"[SUCCESS] [SWITCHYOMEGA] Found {len(profiles)} profiles")
                    for profile in profiles:
                        print(f"  [CREATE] Profile: {profile['name']} ({profile['type']})")
                    
                    return profiles
                    
                except Exception as e:
                    print(f"[WARNING] [SWITCHYOMEGA] Could not extract profiles: {str(e)}")
                    return []
                
            finally:
                driver.quit()
                
        except Exception as e:
            print(f"[ERROR] [SWITCHYOMEGA] Error getting profiles from {profile_name}: {str(e)}")
            return []
    
    def configure_switchyomega_proxy(self, profile_name, proxy_config):
        """
        Configure SwitchyOmega 3 extension with proxy settings for a specific profile
        
        Args:
            profile_name (str): Name of the Chrome profile
            proxy_config (dict): Proxy configuration dictionary
        
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            print(f"[TOOL] [SWITCHYOMEGA] Configuring proxy for profile: {profile_name}")
            
            # Get profile path
            profile_path = self.get_profile_path(profile_name)
            if not profile_path or not os.path.exists(profile_path):
                return False, f"Profile path not found: {profile_name}"
            
            # Launch Chrome with the profile
            chrome_options = Options()
            chrome_options.add_argument(f"--user-data-dir={profile_path}")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1024,768")
            
            # Disable automation detection
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            from selenium import webdriver
            from selenium.webdriver.chrome.service import Service
            # from webdriver_manager.chrome import ChromeDriverManager
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            driver = webdriver.Chrome(options=chrome_options)
            
            try:
                # Navigate to SwitchyOmega options page
                driver.get("chrome-extension://pfnededegaaopdmhkdmcofjmoldfiped/options.html")
                driver.implicitly_wait(10)
                
                time.sleep(5)  # Increased wait time
                
                # Wait for the extension to load
                wait = WebDriverWait(driver, 30)  # Increased timeout
                
                # Check if page loaded successfully
                try:
                    wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                    print("[SUCCESS] [SWITCHYOMEGA] Extension page loaded successfully")
                except:
                    print("[ERROR] [SWITCHYOMEGA] Extension page failed to load")
                    return False, "Extension page failed to load"
                
                # Try to find existing profile first, then create new one if needed
                profile_created = False
                
                # Strategy 1: Look for existing profile to edit
                try:
                    existing_profile_selectors = [
                        "//li[contains(@class, 'profile') and contains(@class, 'active')]",
                        "//li[contains(@class, 'profile')]",
                        "//div[contains(@class, 'profile') and contains(@class, 'active')]",
                        "//div[contains(@class, 'profile')]",
                        "//div[contains(@class, 'item')]",
                        "//div[contains(@class, 'scenario')]",
                        "//tr[contains(@class, 'profile')]"
                    ]
                    
                    for selector in existing_profile_selectors:
                        try:
                            existing_profile = driver.find_element(By.XPATH, selector)
                            existing_profile.click()
                            time.sleep(2)
                            print(f"[SUCCESS] [SWITCHYOMEGA] Using existing profile: {selector}")
                            profile_created = True
                            break
                        except:
                            continue
                            
                except Exception as e:
                    print(f"[WARNING] [SWITCHYOMEGA] Could not find existing profile: {str(e)}")
                
                # Strategy 2: If no existing profile, try to create new one
                if not profile_created:
                    try:
                        new_profile_selectors = [
                        "//button[contains(text(), 'New Profile')]",
                        "//button[contains(text(), '新建情景模式')]",
                        "//button[contains(text(), 'Create Profile')]",
                        "//button[contains(text(), 'Add Profile')]",
                        "//button[contains(@class, 'new-profile')]",
                        "//button[contains(@class, 'create-profile')]",
                        "//button[contains(@class, 'add-profile')]"
                    ]
                    
                        for selector in new_profile_selectors:
                            try:
                                new_profile_btn = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                                new_profile_btn.click()
                                time.sleep(3)
                                print(f"[SUCCESS] [SWITCHYOMEGA] Clicked New Profile button: {selector}")
                                profile_created = True
                                break
                            except:
                                continue
                            
                    except Exception as e:
                        print(f"[WARNING] [SWITCHYOMEGA] Could not find New Profile button: {str(e)}")
                
                if not profile_created:
                    print("[ERROR] [SWITCHYOMEGA] Could not create or find profile")
                    return False, "Could not create or find profile"
                
                # Clear existing proxy data first
                self._clear_existing_proxy_data(driver)
                
                # Fill in proxy configuration
                self._fill_switchyomega_config(driver, proxy_config)
                
                # Save the configuration
                try:
                    save_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Save') or contains(text(), '保存')]")))
                    save_btn.click()
                    time.sleep(2)
                except:
                    # Try alternative save button selectors
                    try:
                        save_btn = driver.find_element(By.XPATH, "//button[@type='submit']")
                        save_btn.click()
                        time.sleep(2)
                    except:
                        pass
                
                # Force refresh to ensure changes are applied
                try:
                    driver.refresh()
                    time.sleep(3)
                    print("[SUCCESS] [SWITCHYOMEGA] Page refreshed to apply changes")
                except:
                    pass
                
                print(f"[SUCCESS] [SWITCHYOMEGA] Successfully configured proxy for {profile_name}")
                return True, "Proxy configuration applied successfully"
                
            finally:
                driver.quit()
                
        except Exception as e:
            print(f"[ERROR] [SWITCHYOMEGA] Error configuring proxy for {profile_name}: {str(e)}")
            return False, f"Configuration failed: {str(e)}"
    
    def _fill_switchyomega_config(self, driver, proxy_config):
        """Fill SwitchyOmega configuration form with proxy settings"""
        try:
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            from selenium.webdriver.common.keys import Keys
            
            wait = WebDriverWait(driver, 15)
            
            print(f"[TOOL] [SWITCHYOMEGA] Filling configuration with: {proxy_config}")
            
            # Wait for page to fully load
            time.sleep(3)
            
            # Navigate to proxy profile creation
            try:
                # Look for "New Profile" or "Create Profile" button
                new_profile_btn = wait.until(EC.element_to_be_clickable((By.XPATH, 
                    "//button[contains(text(), 'New Profile') or contains(text(), '新建情景模式') or contains(text(), 'Create Profile')]")))
                new_profile_btn.click()
                time.sleep(2)
                
                # Select "Proxy Profile" type
                try:
                    proxy_profile_btn = wait.until(EC.element_to_be_clickable((By.XPATH, 
                        "//button[contains(text(), 'Proxy Profile') or contains(text(), '代理情景模式')]")))
                    proxy_profile_btn.click()
                    time.sleep(2)
                except:
                    # Try alternative selector
                    try:
                        proxy_profile_btn = driver.find_element(By.XPATH, "//div[contains(text(), 'Proxy')]")
                        proxy_profile_btn.click()
                        time.sleep(2)
                    except:
                        pass
                        
            except Exception as e:
                print(f"[WARNING] [SWITCHYOMEGA] Could not find new profile button: {str(e)}")
            
            # Profile name
            if 'profile_name' in proxy_config:
                try:
                    name_field = wait.until(EC.presence_of_element_located((By.XPATH, 
                        "//input[@placeholder='Profile Name' or @placeholder='情景模式名称' or @name='profileName']")))
                    name_field.clear()
                    name_field.send_keys(proxy_config['profile_name'])
                    time.sleep(0.5)
                    print(f"[SUCCESS] [SWITCHYOMEGA] Set profile name: {proxy_config['profile_name']}")
                except Exception as e:
                    print(f"[WARNING] [SWITCHYOMEGA] Could not set profile name: {str(e)}")
                    # Try alternative selectors
                    try:
                        name_field = driver.find_element(By.XPATH, "//input[@type='text']")
                        name_field.clear()
                        name_field.send_keys(proxy_config['profile_name'])
                        time.sleep(0.5)
                        print(f"[SUCCESS] [SWITCHYOMEGA] Set profile name (alternative): {proxy_config['profile_name']}")
                    except:
                        pass
            
            # Protocol selection
            protocol = proxy_config.get('proxy_type', 'HTTP').lower()
            try:
                print(f"[TOOL] [SWITCHYOMEGA] Setting proxy type: {protocol}")
                
                # Try different selectors for proxy type
                type_selectors = [
                    f"//input[@type='radio' and (@value='{protocol}' or @value='{protocol.upper()}')]",
                    f"//select[@name='protocol']//option[@value='{protocol}']",
                    f"//button[contains(text(), '{protocol.upper()}')]"
                ]
                
                for selector in type_selectors:
                    try:
                        element = driver.find_element(By.XPATH, selector)
                        if element.tag_name == 'input':
                            element.click()
                        elif element.tag_name == 'option':
                            element.click()
                        elif element.tag_name == 'button':
                            element.click()
                        time.sleep(0.5)
                        print(f"[SUCCESS] [SWITCHYOMEGA] Set proxy type: {protocol}")
                        break
                    except:
                        continue
                        
            except Exception as e:
                print(f"[WARNING] [SWITCHYOMEGA] Could not set proxy type: {str(e)}")
            
            # Server/Host - Find the correct server field in the proxy table
            if 'proxy_server' in proxy_config:
                try:
                    print(f"[TOOL] [SWITCHYOMEGA] Looking for server field...")
                    
                    # Look for server field in the proxy table - should be the first input after "Server" column
                    server_selectors = [
                        "//td[contains(text(), 'Server') or contains(text(), '服务器')]/following-sibling::td//input",
                        "//th[contains(text(), 'Server') or contains(text(), '服务器')]/following-sibling::th//input",
                        "//input[@ng-model='proxyEditors[scheme].host']",
                        "//input[contains(@ng-model, 'host')]",
                        "//input[@placeholder='Server' or @placeholder='服务器']",
                        "//input[@name='host']"
                    ]
                    
                    server_field = None
                    for selector in server_selectors:
                        try:
                            server_field = driver.find_element(By.XPATH, selector)
                            print(f"[SUCCESS] [SWITCHYOMEGA] Found server field with selector: {selector}")
                            break
                        except:
                            continue
                    
                    if server_field:
                        # Scroll to field
                        driver.execute_script("arguments[0].scrollIntoView(true);", server_field)
                        time.sleep(0.5)
                        
                        # Clear and set server value
                        server_field.click()
                        time.sleep(0.3)
                        server_field.clear()
                        time.sleep(0.3)
                        server_field.send_keys(Keys.CONTROL + "a")
                        time.sleep(0.2)
                        server_field.send_keys(Keys.DELETE)
                        time.sleep(0.2)
                        server_field.send_keys(proxy_config['proxy_server'])
                        time.sleep(0.5)
                        print(f"[SUCCESS] [SWITCHYOMEGA] Set proxy server: {proxy_config['proxy_server']}")
                    else:
                        print(f"[WARNING] [SWITCHYOMEGA] Could not find server field")
                        
                except Exception as e:
                    print(f"[WARNING] [SWITCHYOMEGA] Could not set proxy server: {str(e)}")
            
            # Port - Find the correct port field in the proxy table
            if 'proxy_port' in proxy_config:
                try:
                    print(f"[TOOL] [SWITCHYOMEGA] Looking for port field...")
                    
                    # Look for port field in the proxy table - should be after server field
                    port_selectors = [
                        "//td[contains(text(), 'Port') or contains(text(), '端口')]/following-sibling::td//input",
                        "//th[contains(text(), 'Port') or contains(text(), '端口')]/following-sibling::th//input",
                        "//input[@ng-model='proxyEditors[scheme].port']",
                        "//input[contains(@ng-model, 'port')]",
                        "//input[@placeholder='Port' or @placeholder='端口']",
                        "//input[@name='port']",
                        "//input[@type='number']"
                    ]
                    
                    port_field = None
                    for selector in port_selectors:
                        try:
                            port_field = driver.find_element(By.XPATH, selector)
                            print(f"[SUCCESS] [SWITCHYOMEGA] Found port field with selector: {selector}")
                            break
                        except:
                            continue
                    
                    if port_field:
                        # Scroll to field
                        driver.execute_script("arguments[0].scrollIntoView(true);", port_field)
                        time.sleep(0.5)
                        
                        # Clear and set port value
                        port_field.click()
                        time.sleep(0.3)
                        port_field.clear()
                        time.sleep(0.3)
                        port_field.send_keys(Keys.CONTROL + "a")
                        time.sleep(0.2)
                        port_field.send_keys(Keys.DELETE)
                        time.sleep(0.2)
                        port_field.send_keys(str(proxy_config['proxy_port']))
                        time.sleep(0.5)
                        print(f"[SUCCESS] [SWITCHYOMEGA] Set proxy port: {proxy_config['proxy_port']}")
                    else:
                        print(f"[WARNING] [SWITCHYOMEGA] Could not find port field")
                        
                except Exception as e:
                    print(f"[WARNING] [SWITCHYOMEGA] Could not set proxy port: {str(e)}")
            
            # Username/Password (if provided) - Click the lock button first
            if 'username' in proxy_config and proxy_config['username']:
                try:
                    print(f"[TOOL] [SWITCHYOMEGA] Setting authentication...")
                    
                    # First, click the lock button to reveal username/password fields
                    lock_button_selectors = [
                        "//button[contains(@class, 'lock') or contains(@class, 'auth')]",
                        "//button[contains(@title, 'lock') or contains(@title, 'auth')]",
                        "//button[contains(@aria-label, 'lock') or contains(@aria-label, 'auth')]",
                        "//button[contains(@onclick, 'auth') or contains(@onclick, 'lock')]",
                        "//button[contains(@ng-click, 'auth') or contains(@ng-click, 'lock')]",
                        "//button[contains(text(), '🔒') or contains(text(), '[PASSWORD]')]",
                        "//button[@type='button' and contains(@class, 'btn')]",
                        "//button[contains(@class, 'btn') and not(contains(@class, 'btn-primary'))]"
                    ]
                    
                    lock_clicked = False
                    for selector in lock_button_selectors:
                        try:
                            lock_button = driver.find_element(By.XPATH, selector)
                            # Check if this button is near the port field
                            port_field = driver.find_element(By.XPATH, "//input[@ng-model='proxyEditors[scheme].port']")
                            if lock_button.is_displayed() and lock_button.is_enabled():
                                lock_button.click()
                                time.sleep(1)  # Wait for fields to appear
                                print(f"[SUCCESS] [SWITCHYOMEGA] Clicked lock button to reveal auth fields")
                                lock_clicked = True
                                break
                        except:
                            continue
                    
                    if not lock_clicked:
                        print(f"[WARNING] [SWITCHYOMEGA] Could not find lock button, trying alternative methods")
                        # Try to find authentication checkbox as fallback
                    auth_selectors = [
                        "//input[@type='checkbox' and contains(@id, 'auth')]",
                        "//input[@type='checkbox' and contains(@name, 'auth')]",
                        "//input[@type='checkbox' and contains(@class, 'auth')]"
                    ]
                    
                    for selector in auth_selectors:
                        try:
                            auth_checkbox = driver.find_element(By.XPATH, selector)
                            if not auth_checkbox.is_selected():
                                auth_checkbox.click()
                                time.sleep(0.5)
                                print(f"[SUCCESS] [SWITCHYOMEGA] Enabled authentication via checkbox")
                            break
                        except:
                            continue
                    
                    # Username
                    if 'username' in proxy_config:
                        try:
                            print(f"[TOOL] [SWITCHYOMEGA] Looking for username field...")
                            username_selectors = [
                                "//input[@ng-model='proxyEditors[scheme].username']",
                                "//input[contains(@ng-model, 'username')]",
                            "//input[@placeholder='Username' or @placeholder='用户名' or @name='username' or contains(@id, 'user')]",
                            "//input[@type='text' and contains(@placeholder, 'user')]",
                            "//input[contains(@class, 'username') or contains(@class, 'user')]"
                            ]
                            
                            username_field = None
                            for selector in username_selectors:
                                try:
                                    username_field = driver.find_element(By.XPATH, selector)
                                    print(f"[SUCCESS] [SWITCHYOMEGA] Found username field with selector: {selector}")
                                    break
                                except:
                                    continue
                            
                            if username_field:
                                # Scroll to field
                                driver.execute_script("arguments[0].scrollIntoView(true);", username_field)
                                time.sleep(0.5)
                                
                                # Clear and set username
                                username_field.click()
                                time.sleep(0.3)
                                username_field.clear()
                                time.sleep(0.3)
                                username_field.send_keys(Keys.CONTROL + "a")
                                time.sleep(0.2)
                                username_field.send_keys(Keys.DELETE)
                                time.sleep(0.2)
                                username_field.send_keys(proxy_config['username'])
                                time.sleep(0.5)
                                print(f"[SUCCESS] [SWITCHYOMEGA] Set username: {proxy_config['username']}")
                            else:
                                print(f"[WARNING] [SWITCHYOMEGA] Could not find username field")
                            
                        except Exception as e:
                            print(f"[WARNING] [SWITCHYOMEGA] Could not set username: {str(e)}")
            
            # Password
                    if 'password' in proxy_config:
                        try:
                            print(f"[TOOL] [SWITCHYOMEGA] Looking for password field...")
                            password_selectors = [
                                "//input[@ng-model='proxyEditors[scheme].password']",
                                "//input[contains(@ng-model, 'password')]",
                                "//input[@placeholder='Password' or @placeholder='密码' or @name='password' or contains(@id, 'pass')]",
                                "//input[@type='password']",
                                "//input[contains(@class, 'password') or contains(@class, 'pass')]"
                            ]
                            
                            password_field = None
                            for selector in password_selectors:
                                try:
                                    password_field = driver.find_element(By.XPATH, selector)
                                    print(f"[SUCCESS] [SWITCHYOMEGA] Found password field with selector: {selector}")
                                    break
                                except:
                                    continue
                            
                            if password_field:
                                # Scroll to field
                                driver.execute_script("arguments[0].scrollIntoView(true);", password_field)
                                time.sleep(0.5)
                                
                                # Clear and set password
                                password_field.click()
                                time.sleep(0.3)
                                password_field.clear()
                                time.sleep(0.3)
                                password_field.send_keys(Keys.CONTROL + "a")
                                time.sleep(0.2)
                                password_field.send_keys(Keys.DELETE)
                                time.sleep(0.2)
                                password_field.send_keys(proxy_config['password'])
                                time.sleep(0.5)
                                print(f"[SUCCESS] [SWITCHYOMEGA] Set password: {'*' * len(proxy_config['password'])}")
                            else:
                                print(f"[WARNING] [SWITCHYOMEGA] Could not find password field")
                                
                        except Exception as e:
                            print(f"[WARNING] [SWITCHYOMEGA] Could not set password: {str(e)}")
                            
                except Exception as e:
                    print(f"[WARNING] [SWITCHYOMEGA] Could not set authentication: {str(e)}")
            
            # Apply to all protocols
            try:
                apply_all_checkbox = driver.find_element(By.XPATH, "//input[@type='checkbox'][contains(@name, 'all') or contains(@id, 'all')]")
                if not apply_all_checkbox.is_selected():
                    apply_all_checkbox.click()
                    time.sleep(0.5)
                    print(f"[SUCCESS] [SWITCHYOMEGA] Applied to all protocols")
            except:
                pass
            
            # Save configuration
            try:
                save_selectors = [
                    "//button[contains(text(), 'Save') or contains(text(), '保存')]",
                    "//button[@type='submit']",
                    "//input[@type='submit']",
                    "//button[contains(@class, 'save')]",
                    "//button[contains(text(), 'Apply') or contains(text(), '应用')]",
                    "//button[contains(text(), 'OK') or contains(text(), '确定')]"
                ]
                
                save_success = False
                for selector in save_selectors:
                    try:
                        save_btn = driver.find_element(By.XPATH, selector)
                        save_btn.click()
                        time.sleep(2)
                        print(f"[SUCCESS] [SWITCHYOMEGA] Configuration saved")
                        save_success = True
                        break
                    except:
                        continue
                
                if not save_success:
                    print("[WARNING] [SWITCHYOMEGA] Could not find save button, trying alternative methods")
                    # Try pressing Enter key
                    try:
                        from selenium.webdriver.common.keys import Keys
                        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ENTER)
                        time.sleep(2)
                        print("[SUCCESS] [SWITCHYOMEGA] Pressed Enter to save")
                    except:
                        pass
                        
            except Exception as e:
                print(f"[WARNING] [SWITCHYOMEGA] Could not save configuration: {str(e)}")
            
            # Force refresh the page to ensure changes are applied
            try:
                driver.refresh()
                time.sleep(3)
                print("[SUCCESS] [SWITCHYOMEGA] Page refreshed to apply changes")
                
                # Verify changes were applied by checking the page content
                page_source = driver.page_source
                if proxy_config.get('proxy_server', '') in page_source:
                    print(f"[SUCCESS] [SWITCHYOMEGA] Verified proxy server in page: {proxy_config.get('proxy_server', '')}")
                if str(proxy_config.get('proxy_port', '')) in page_source:
                    print(f"[SUCCESS] [SWITCHYOMEGA] Verified proxy port in page: {proxy_config.get('proxy_port', '')}")
                    
            except:
                pass
            
            time.sleep(1)
            
        except Exception as e:
            print(f"[ERROR] [SWITCHYOMEGA] Error filling configuration: {str(e)}")
    
    
    def bulk_configure_switchyomega(self, profile_list, proxy_config):
        """
        Configure SwitchyOmega 3 for multiple profiles
        
        Args:
            profile_list (list): List of profile names
            proxy_config (dict): Proxy configuration dictionary
        
        Returns:
            tuple: (success_count: int, results: list)
        """
        success_count = 0
        results = []
        
        print(f"[PROFILE] [BULK-SWITCHYOMEGA] Starting bulk configuration for {len(profile_list)} profiles")
        
        for profile_name in profile_list:
            try:
                success, message = self.configure_switchyomega_proxy(profile_name, proxy_config)
                result = f"{'[SUCCESS]' if success else '[ERROR]'} {profile_name}: {message}"
                results.append(result)
                
                if success:
                    success_count += 1
                
                # Small delay between configurations
                time.sleep(2)
                
            except Exception as e:
                error_msg = f"[ERROR] {profile_name}: Error - {str(e)}"
                results.append(error_msg)
                print(f"[ERROR] [BULK-SWITCHYOMEGA] Error for {profile_name}: {str(e)}")
        
        print(f"[SUCCESS] [BULK-SWITCHYOMEGA] Completed: {success_count}/{len(profile_list)} successful")
        return success_count, results
    
    def bulk_install_extension_directory(self, profile_list=None):
        """
        Install extension for multiple profiles using directory method
        
        Args:
            profile_list (list): List of profile names (if None, install for all profiles)
        
        Returns:
            tuple: (success_count: int, results: list)
        """
        if profile_list is None:
            profile_list = self.get_all_profiles()
        
        success_count = 0
        results = []
        
        print(f"[PROFILE] [BULK-DIR-EXTENSION] Starting bulk installation for {len(profile_list)} profiles")
        
        # Create extension once and reuse
        extension_dir = self.download_extension_from_webstore()
        if not extension_dir:
            return 0, ["[ERROR] Failed to create extension directory"]
        
        for profile_name in profile_list:
            try:
                success, message = self.install_extension_from_directory(profile_name, extension_dir)
                result = f"{'[SUCCESS]' if success else '[ERROR]'} {profile_name}: {message}"
                results.append(result)
                
                if success:
                    success_count += 1
                
                # Small delay between installations
                time.sleep(0.5)
                
            except Exception as e:
                error_msg = f"[ERROR] {profile_name}: Error - {str(e)}"
                results.append(error_msg)
                print(f"[ERROR] [BULK-DIR-EXTENSION] Error for {profile_name}: {str(e)}")
        
        print(f"[SUCCESS] [BULK-DIR-EXTENSION] Completed: {success_count}/{len(profile_list)} successful")
        return success_count, results
    
    def activate_extension_in_chrome(self, profile_name):
        """
        Activate extension in Chrome by launching browser and enabling extension
        
        Args:
            profile_name (str): Name of the Chrome profile
        
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            print(f"[PROFILE] [ACTIVATE-EXTENSION] Activating extension for profile: {profile_name}")
            
            # Get profile path
            profile_path = self.get_profile_path(profile_name)
            if not profile_path or not os.path.exists(profile_path):
                return False, f"Profile path not found: {profile_name}"
            
            # Extension ID
            extension_id = "pfnededegaaopdmhkdmcofjmoldfiped"
            
            # Check if extension is installed
            if not self.check_extension_installed(profile_name):
                return False, f"Extension not installed for profile: {profile_name}"
            
            print(f"[SUCCESS] [ACTIVATE-EXTENSION] Extension is installed, launching Chrome...")
            
            # Launch Chrome with the profile
            # Lấy display name from settings
            display_name = profile_name
            try:
                settings_path = os.path.join(profile_path, 'profile_settings.json')
                if os.path.exists(settings_path):
                    import json
                    with open(settings_path, 'r', encoding='utf-8') as f:
                        settings = json.load(f)
                        profile_info = settings.get('profile_info', {})
                        display_name = profile_info.get('display_name', profile_name)
            except Exception:
                pass
                
            # Sử dụng function fix để tối ưu hóa command line
            chrome_options = [
                "--user-data-dir=" + profile_path,
                "--profile-directory=" + display_name,
                "--load-extension=" + os.path.join(profile_path, "Extensions", extension_id, "3.4.1"),
                "--enable-extensions",
                "--disable-extensions-except=" + os.path.join(profile_path, "Extensions", extension_id, "3.4.1"),
                # "--no-first-run",
                "--no-default-browser-check",
                "--disable-default-apps",
                "--disable-popup-blocking",
                "--disable-translate",
                "--disable-background-timer-throttling",
                "--disable-renderer-backgrounding",
                "--disable-backgrounding-occluded-windows",
                "--disable-client-side-phishing-detection",
                "--disable-sync",
                "--disable-background-networking",
                "--disable-web-security",
                "--allow-running-insecure-content",
                "--disable-features=TranslateUI",
                "--disable-ipc-flooding-protection",
                # "--remote-debugging-port=9222",
                "--new-window"
            ]
            
            # Tối ưu hóa command line bằng function fix
            try:
                from fix_chrome_command import fix_chrome_command, create_rules_from_gpm_config
                
                # Tạo command line hiện tại
                current_command = 'chrome.exe ' + ' '.join([str(arg) for arg in chrome_options])
                
                # Tạo rules từ GPM config
                rules = create_rules_from_gpm_config(gpm_config)
                rules['user_data_dir'] = profile_path
                rules['extension_path'] = os.path.join(profile_path, "Extensions", extension_id, "3.4.1")
                
                # Fix command line
                fixed_command = fix_chrome_command(current_command, rules)
                
                if not fixed_command.startswith('ERROR:'):
                    # Parse fixed command và cập nhật chrome_options
                    import shlex
                    fixed_parts = shlex.split(fixed_command)
                    if len(fixed_parts) > 1:
                        fixed_args = fixed_parts[1:]  # Bỏ executable path
                        chrome_options = fixed_args
                        print(f"[COMMAND-FIX] Fixed extension activation command line: {len(fixed_args)} flags")
                else:
                    print(f"[COMMAND-FIX] Error fixing extension command line: {fixed_command}")
                    
            except Exception as e:
                print(f"[COMMAND-FIX] Error fixing extension command line: {str(e)}")
            
            # Launch Chrome
            import subprocess
            
            chrome_path = self.get_chrome_path()
            if not chrome_path:
                return False, "Chrome executable not found"
            
            print(f"[NETWORK] [ACTIVATE-EXTENSION] Launching Chrome with extension enabled...")
            
            # Launch Chrome in background
            process = subprocess.Popen(
                [chrome_path] + chrome_options,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
            )
            
            # Wait a bit for Chrome to start
            time.sleep(3)
            
            print(f"[SUCCESS] [ACTIVATE-EXTENSION] Chrome launched with extension enabled")
            print(f"[TOOL] [ACTIVATE-EXTENSION] Extension should now be visible in Chrome")
            print(f"[TOOL] [ACTIVATE-EXTENSION] Look for SwitchyOmega icon in toolbar")
            
            return True, f"Chrome launched with extension enabled for {profile_name}"
            
        except Exception as e:
            print(f"[ERROR] [ACTIVATE-EXTENSION] Error activating extension: {str(e)}")
            return False, f"Activation failed: {str(e)}"
    
    def bulk_activate_extensions(self, profile_list=None):
        """
        Activate extensions for multiple profiles
        
        Args:
            profile_list (list): List of profile names (if None, activate for all profiles)
        
        Returns:
            tuple: (success_count: int, results: list)
        """
        if profile_list is None:
            profile_list = self.get_all_profiles()
        
        success_count = 0
        results = []
        
        print(f"[PROFILE] [BULK-ACTIVATE] Starting bulk activation for {len(profile_list)} profiles")
        
        for profile_name in profile_list:
            try:
                success, message = self.activate_extension_in_chrome(profile_name)
                result = f"{'[SUCCESS]' if success else '[ERROR]'} {profile_name}: {message}"
                results.append(result)
                
                if success:
                    success_count += 1
                
                # Small delay between activations
                time.sleep(2)
                
            except Exception as e:
                error_msg = f"[ERROR] {profile_name}: Error - {str(e)}"
                results.append(error_msg)
                print(f"[ERROR] [BULK-ACTIVATE] Error for {profile_name}: {str(e)}")
        
        print(f"[SUCCESS] [BULK-ACTIVATE] Completed: {success_count}/{len(profile_list)} successful")
        return success_count, results
    
    def auto_install_extension_on_startup(self, extension_id="pfnededegaaopdmhkdmcofjmoldfiped"):
        """
        Automatically install SwitchyOmega 3 extension for all profiles on startup
        
        Args:
            extension_id (str): Chrome Web Store extension ID
        
        Returns:
            tuple: (success_count: int, results: list)
        """
        try:
            print("[PROFILE] [AUTO-INSTALL] Starting automatic extension installation on startup...")
            
            # Get all profiles
            all_profiles = self.get_all_profiles()
            
            if not all_profiles:
                print("[WARNING] [AUTO-INSTALL] No profiles found for auto-installation")
                return 0, ["No profiles found"]
            
            # Check which profiles need extension installation
            profiles_to_install = []
            for profile in all_profiles:
                if not self.check_extension_installed(profile, extension_id):
                    profiles_to_install.append(profile)
            
            if not profiles_to_install:
                print("[SUCCESS] [AUTO-INSTALL] All profiles already have SwitchyOmega 3 installed")
                return len(all_profiles), [f"[SUCCESS] {profile}: Already installed" for profile in all_profiles]
            
            print(f"📥 [AUTO-INSTALL] Installing extension for {len(profiles_to_install)} profiles...")
            
            # Install extension for profiles that need it using directory method
            success_count, results = self.bulk_install_extension_directory(profiles_to_install)
            
            # Add already installed profiles to results
            for profile in all_profiles:
                if profile not in profiles_to_install:
                    results.append(f"[SUCCESS] {profile}: Already installed")
                    success_count += 1
            
            print(f"[SUCCESS] [AUTO-INSTALL] Completed: {success_count}/{len(all_profiles)} profiles have extension")
            return success_count, results
            
        except Exception as e:
            print(f"[ERROR] [AUTO-INSTALL] Error during auto-installation: {str(e)}")
            return 0, [f"[ERROR] Auto-installation failed: {str(e)}"]
    
    def ensure_extension_installed(self, profile_name, extension_id="pfnededegaaopdmhkdmcofjmoldfiped"):
        """
        Ensure SwitchyOmega 3 extension is installed for a specific profile
        If not installed, automatically install it
        
        Args:
            profile_name (str): Name of the Chrome profile
            extension_id (str): Chrome Web Store extension ID
        
        Returns:
            bool: True if extension is installed (or was successfully installed), False otherwise
        """
        try:
            # Check if extension is already installed
            if self.check_extension_installed(profile_name, extension_id):
                return True
            
            # If not installed, install it using directory method
            print(f"📥 [ENSURE-EXTENSION] Installing SwitchyOmega 3 for {profile_name}...")
            success, message = self.install_extension_from_directory(profile_name)
            
            if success:
                print(f"[SUCCESS] [ENSURE-EXTENSION] Successfully installed extension for {profile_name}")
                return True
            else:
                print(f"[ERROR] [ENSURE-EXTENSION] Failed to install extension for {profile_name}: {message}")
                return False
                
        except Exception as e:
            print(f"[ERROR] [ENSURE-EXTENSION] Error ensuring extension for {profile_name}: {str(e)}")
            return False
    
    def create_pac_from_proxy(self, proxy_server, proxy_port, proxy_username=None, proxy_password=None, pac_name="custom_proxy.pac"):
        """Create PAC file from proxy input"""
        try:
            print(f"[TOOL] [PAC] Creating PAC file: {pac_name}")
            print(f"[CREATE] [PAC] Proxy: {proxy_server}:{proxy_port}")
            
            # Create PAC content based on your working example
            pac_content = f'''var FindProxyForURL = function(init, profiles) {{
    return function(url, host) {{
        "use strict";
        var result = init, scheme = url.substr(0, url.indexOf(":"));
        do {{
            if (!profiles[result]) return result;
            result = profiles[result];
            if (typeof result === "function") result = result(url, host, scheme);
        }} while (typeof result !== "string" || result.charCodeAt(0) === 43);
        return result;
    }};
}}("+proxy", {{
    "+proxy": function(url, host, scheme) {{
        "use strict";
        if (/^127\\.0\\.0\\.1$/.test(host) || /^::1$/.test(host) || /^localhost$/.test(host)) return "DIRECT";
        return "PROXY {proxy_server}:{proxy_port}";
    }}
}});'''
            
            # Save PAC file
            with open(pac_name, 'w', encoding='utf-8') as f:
                f.write(pac_content)
            
            print(f"[SUCCESS] [PAC] PAC file created: {pac_name}")
            return True, pac_name
            
        except Exception as e:
            print(f"[ERROR] [PAC] Error creating PAC file: {str(e)}")
            return False, str(e)

    def _purge_graphics_caches(self, profile_path: str) -> None:
        """Xóa cache đồ họa to tránh save vết fingerprint GPU (GrShaderCache, GraphiteDawnCache)."""
        try:
            import shutil as _sh
            for folder in ("GrShaderCache", "GraphiteDawnCache", "GraphiteDawnCache", "GraphiteDawnCache", "GraphiteDawnCache"):
                p = os.path.join(profile_path, folder)
                if os.path.exists(p):
                    try:
                        _sh.rmtree(p)
                    except Exception:
                        # Thử delete file con if không delete get cả thư mục
                        try:
                            for root, dirs, files in os.walk(p):
                                for fn in files:
                                    try:
                                        os.remove(os.path.join(root, fn))
                                    except Exception:
                                        pass
                        except Exception:
                            pass
        except Exception:
            pass

    def read_proxy_from_extension(self, profile_name):
        """
        Read existing proxy configuration from SwitchyOmega extension
        
        Args:
            profile_name (str): Name of the Chrome profile
            
        Returns:
            dict: Proxy configuration or None if not found
        """
        try:
            print(f"[DEBUG] [PROXY-READ] Reading proxy config from extension for profile: {profile_name}")
            
            profile_path = os.path.join(self.profiles_dir, profile_name)
            if not os.path.exists(profile_path):
                print(f"[ERROR] [PROXY-READ] Profile not found: {profile_name}")
                return None
            
            # Path to SwitchyOmega settings
            settings_path = os.path.join(profile_path, "Default", "Extensions", 
                                       "pfnededegaaopdmhkdmcofjmoldfiped", "3.4.1_0", "settings.json")
            
            if not os.path.exists(settings_path):
                print(f"[ERROR] [PROXY-READ] SwitchyOmega settings not found: {settings_path}")
                return None
            
            # Read settings.json
            with open(settings_path, 'r', encoding='utf-8') as f:
                settings = json.load(f)
            
            # Extract proxy configuration
            profiles = settings.get('profiles', {})
            default_profile_id = settings.get('defaultProfileId')
            
            if not default_profile_id or default_profile_id not in profiles:
                print(f"[ERROR] [PROXY-READ] No default profile found in settings")
                return None
            
            profile_config = profiles[default_profile_id]
            
            if profile_config.get('type') != 'ProxyProfile':
                print(f"[ERROR] [PROXY-READ] Default profile is not a proxy profile")
                return None
            
            # Extract proxy details
            proxy_config = {
                'proxy_server': profile_config.get('host', ''),
                'proxy_port': profile_config.get('port', 0),
                'username': profile_config.get('username', ''),
                'password': profile_config.get('password', ''),
                'scheme': profile_config.get('scheme', 'http'),
                'profile_name': profile_config.get('name', 'Unknown')
            }
            
            print(f"[SUCCESS] [PROXY-READ] Found proxy configuration:")
            print(f"   Profile: {proxy_config['profile_name']}")
            print(f"   Server: {proxy_config['proxy_server']}")
            print(f"   Port: {proxy_config['proxy_port']}")
            print(f"   Username: {proxy_config['username']}")
            print(f"   Password: {'*' * len(proxy_config['password'])}")
            print(f"   Scheme: {proxy_config['scheme']}")
            
            return proxy_config
            
        except Exception as e:
            print(f"[ERROR] [PROXY-READ] Error reading proxy config: {str(e)}")
            return None

    def auto_fix_proxy_input(self, profile_name):
        """
        Automatically fix proxy input by reading from existing extension configuration
        
        Args:
            profile_name (str): Name of the Chrome profile
            
        Returns:
            tuple: (success: bool, proxy_string: str, message: str)
        """
        try:
            print(f"[TOOL] [PROXY-FIX] Auto-fixing proxy input for profile: {profile_name}")
            
            # Read existing proxy configuration
            proxy_config = self.read_proxy_from_extension(profile_name)
            
            if not proxy_config:
                return False, "", "No existing proxy configuration found in extension"
            
            # Create proxy string from existing config
            proxy_string = f"{proxy_config['proxy_server']}:{proxy_config['proxy_port']}:{proxy_config['username']}:{proxy_config['password']}"
            
            print(f"[SUCCESS] [PROXY-FIX] Generated proxy string from extension:")
            print(f"   {proxy_string}")
            
            return True, proxy_string, f"Proxy string generated from existing configuration: {proxy_config['profile_name']}"
            
        except Exception as e:
            print(f"[ERROR] [PROXY-FIX] Error auto-fixing proxy input: {str(e)}")
            return False, "", f"Error auto-fixing proxy input: {str(e)}"

    def _get_switchyomega_settings_path(self, profile_name):
        """Return absolute path to SwitchyOmega settings.json for a profile."""
        profile_path = os.path.join(self.profiles_dir, profile_name)
        settings_path = os.path.join(
            profile_path,
            "Default",
            "Extensions",
            "pfnededegaaopdmhkdmcofjmoldfiped",
            "3.4.1_0",
            "settings.json",
        )
        return settings_path

    def apply_proxy_via_settings(self, profile_name, proxy_config):
        """
        Apply proxy by writing SwitchyOmega settings.json directly (no Chrome launch).

        proxy_config keys: proxy_server, proxy_port, username(optional), password(optional), scheme(optional)
        """
        try:
            print(f"💾 [SO-SETTINGS] Writing settings.json for profile: {profile_name}")

            settings_path = self._get_switchyomega_settings_path(profile_name)
            settings_dir = os.path.dirname(settings_path)

            # Ensure directory exists
            if not os.path.exists(settings_dir):
                os.makedirs(settings_dir, exist_ok=True)

            # Load existing settings if exist, else create base
            settings = {
                "version": "3.0.0",
                "profiles": {},
                "rules": [],
                "defaultProfileId": "MyProxy",
            }
            if os.path.exists(settings_path):
                try:
                    with open(settings_path, "r", encoding="utf-8") as f:
                        existing = json.load(f)
                        if isinstance(existing, dict):
                            settings.update(existing)
                            if "profiles" not in settings:
                                settings["profiles"] = {}
                except Exception as e:
                    print(f"[WARNING] [SO-SETTINGS] Could not read existing settings: {e}")

            scheme = proxy_config.get("scheme", "http") or "http"
            host = proxy_config.get("proxy_server", "")
            port = int(proxy_config.get("proxy_port", 0) or 0)
            username = proxy_config.get("username") or ""
            password = proxy_config.get("password") or ""

            profile_id = "MyProxy"
            settings["profiles"][profile_id] = {
                "name": profile_id,
                "type": "ProxyProfile",
                "color": "#ff6b6b",
                "conditionType": "HostWildcardCondition",
                "condition": "*",
                "proxyType": scheme,
                "scheme": scheme,
                "host": host,
                "port": port,
                "username": username,
                "password": password,
                "bypassList": "",
                "pacUrl": "",
                "pacScript": "",
                "singleProxy": {
                    "scheme": scheme,
                    "host": host,
                    "port": port,
                    "username": username,
                    "password": password,
                },
            }

            # Ensure rule points to profile
            settings["defaultProfileId"] = profile_id
            settings["rules"] = [
                {"conditionType": "HostWildcardCondition", "condition": "*", "profileId": profile_id}
            ]

            with open(settings_path, "w", encoding="utf-8") as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)

            print(
                f"[SUCCESS] [SO-SETTINGS] settings.json updated: {host}:{port} user={username}"
            )
            return True, "SwitchyOmega settings updated"

        except Exception as e:
            print(f"[ERROR] [SO-SETTINGS] Failed to write settings: {e}")
            return False, f"Failed to write settings: {e}"

    def apply_proxy_via_settings_string(self, profile_name, proxy_string):
        """Parse proxy string and call apply_proxy_via_settings."""
        try:
            parts = proxy_string.strip().split(":")
            if len(parts) < 2:
                return False, "Invalid proxy format. Use server:port[:username:password]"
            proxy_config = {
                "proxy_server": parts[0].strip(),
                "proxy_port": int(parts[1].strip()),
                "username": parts[2].strip() if len(parts) > 2 else "",
                "password": parts[3].strip() if len(parts) > 3 else "",
                "scheme": "http",
            }
            return self.apply_proxy_via_settings(profile_name, proxy_config)
        except Exception as e:
            return False, f"Failed to parse/apply: {e}"

    def bulk_apply_proxy_map_via_settings(self, profile_to_proxy_map):
        """Apply many proxies to many profiles by editing settings.json files directly.

        profile_to_proxy_map: dict { profile_name: proxy_string }
        Returns (results: list of {profile, success, message}, success_count)
        """
        results = []
        success_count = 0
        for profile_name, proxy_string in profile_to_proxy_map.items():
            try:
                ok, msg = self.apply_proxy_via_settings_string(profile_name, proxy_string)
                results.append({"profile": profile_name, "success": ok, "message": msg})
                if ok:
                    success_count += 1
            except Exception as e:
                results.append({"profile": profile_name, "success": False, "message": str(e)})
        return results, success_count

    def force_import_settings_into_extension(self, profile_name):
        """Open SwitchyOmega options for the given profile and import our settings.json via UI.

        This ensures the extension's Local Extension Settings storage reflects the settings file we wrote.
        """
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC

            settings_path = self._get_switchyomega_settings_path(profile_name)
            if not os.path.exists(settings_path):
                return False, f"settings.json not found for profile {profile_name}"

            profile_dir = os.path.join(self.profiles_dir, profile_name)
            if not os.path.exists(profile_dir):
                return False, f"Profile '{profile_name}' not found"

            chrome_options = Options()
            chrome_options.add_argument(f"--user-data-dir={profile_dir}")
            # chrome_options.add_argument("--no-first-run")
            chrome_options.add_argument("--no-default-browser-check")
            chrome_options.add_argument("--disable-popup-blocking")

            driver = webdriver.Chrome(options=chrome_options)
            wait = WebDriverWait(driver, 20)

            # Read settings to get intended proxy values
            with open(settings_path, 'r', encoding='utf-8') as f:
                settings = json.load(f)
            prof = settings.get('profiles', {}).get('MyProxy') or next(iter(settings.get('profiles', {}).values()), {})
            host = str(prof.get('host', ''))
            port = str(prof.get('port', ''))
            username = str(prof.get('username', ''))
            password = str(prof.get('password', ''))

            # Go directly to the existing 'proxy' profile page
            driver.get("chrome-extension://pfnededegaaopdmhkdmcofjmoldfiped/options.html#!/profile/proxy")
            time.sleep(2)

            # Fill server and port
            try:
                server_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@ng-model='proxyEditors[scheme].host']")))
                port_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@ng-model='proxyEditors[scheme].port']")))
                server_input.clear(); server_input.send_keys(host)
                port_input.clear(); port_input.send_keys(port)
            except Exception:
                pass

            # Ensure Advanced panel is visible (to reveal auth/lock)
            try:
                adv_toggle = driver.find_element(By.XPATH, "//a[contains(@ng-click,'toggleAdvanced') or contains(.,'Show Advanced') or contains(.,'Advanced')]")
                if adv_toggle.is_displayed():
                    adv_toggle.click(); time.sleep(0.5)
            except Exception:
                pass

            # Click padlock to show auth fields (if username provided)
            try:
                if username:
                    lock_btn = driver.find_element(By.XPATH, "//button[contains(@class,'btn') and .//span[contains(@class,'glyphicon-lock')] or contains(@ng-click,'toggleAuth') or contains(@ng-click,'auth')]")
                    lock_btn.click(); time.sleep(0.8)
                    # Modal appears: fill username/password and save
                    try:
                        modal = wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class,'modal-dialog')]")))
                        user_modal = wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class,'modal-dialog')]//input[@type='text' or @type='email' or @name='username']")))
                        pass_modal = wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class,'modal-dialog')]//input[@type='password' or @name='password']")))
                        user_modal.clear(); user_modal.send_keys(username)
                        pass_modal.clear(); pass_modal.send_keys(password)
                        # Click Save changes inside modal
                        save_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class,'modal-dialog')]//button[contains(., 'Save changes') or contains(., 'Save')]")))
                        save_btn.click(); time.sleep(0.8)
                    except Exception:
                        pass
            except Exception:
                pass

            # Fill username/password if fields exist
            try:
                user_input = driver.find_element(By.XPATH, "//input[@ng-model='proxyEditors[scheme].username']")
                pass_input = driver.find_element(By.XPATH, "//input[@ng-model='proxyEditors[scheme].password']")
                user_input.clear(); user_input.send_keys(username)
                pass_input.clear(); pass_input.send_keys(password)
            except Exception:
                pass

            # Click Apply changes (left panel or bottom) and wait for success toast 'Options saved.'
            try:
                apply_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Apply changes') or contains(., 'Apply')] | //a[contains(., 'Apply changes')]")))
                apply_btn.click()
                # Wait for green success alert
                wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class,'alert-success') and contains(., 'Options saved')]")))
            except Exception:
                pass

            driver.quit()
            return True, "Settings imported into extension"

        except Exception as e:
            try:
                driver.quit()
            except Exception:
                pass
            return False, f"Failed to import into extension: {e}"

    def input_proxy_from_ui(self, profile_name, proxy_string):
        """
        Parse proxy string from UI and configure SwitchyOmega
        Format: server:port:username:password or server:port
        """
        try:
            print(f"[TOOL] [PROXY-INPUT] Parsing proxy string for {profile_name}")
            
            # Parse proxy string
            parts = proxy_string.strip().split(':')
            
            if len(parts) < 2:
                return False, "Invalid proxy format. Use: server:port:username:password"
            
            proxy_config = {
                'proxy_server': parts[0].strip(),
                'proxy_port': int(parts[1].strip()),
                'username': parts[2].strip() if len(parts) > 2 else None,
                'password': parts[3].strip() if len(parts) > 3 else None
            }
            
            print(f"[STATS] [PROXY-INPUT] Parsed config: {proxy_config['proxy_server']}:{proxy_config['proxy_port']}")
            if proxy_config['username']:
                print(f"👤 [PROXY-INPUT] Username: {proxy_config['username']}")
            
            # Configure SwitchyOmega
            return self.configure_switchyomega_proxy(profile_name, proxy_config)
            
        except ValueError as e:
            return False, f"Invalid port number: {str(e)}"
        except Exception as e:
            return False, f"Error parsing proxy: {str(e)}"

    def bulk_input_proxy_from_ui(self, profile_list, proxy_string):
        """
        Apply proxy configuration to multiple profiles
        """
        results = []
        success_count = 0
        
        for profile_name in profile_list:
            try:
                success, message = self.input_proxy_from_ui(profile_name, proxy_string)
                results.append({
                    'profile': profile_name,
                    'success': success,
                    'message': message
                })
                if success:
                    success_count += 1
            except Exception as e:
                results.append({
                    'profile': profile_name,
                    'success': False,
                    'message': f"Error: {str(e)}"
                })
        
        return results, success_count

    def test_proxy_connection(self, proxy_string):
        """
        Test proxy connection before applying
        """
        try:
            print(f"[DEBUG] [PROXY-TEST] Testing proxy connection...")
            
            # Parse proxy string
            parts = proxy_string.strip().split(':')
            
            if len(parts) < 2:
                return False, "Invalid proxy format. Use: server:port:username:password"
            
            proxy_server = parts[0].strip()
            proxy_port = int(parts[1].strip())
            proxy_username = parts[2].strip() if len(parts) > 2 else None
            proxy_password = parts[3].strip() if len(parts) > 3 else None
            
            # Test connection
            import requests
            import socket
            
            # Test basic connectivity
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            result = sock.connect_ex((proxy_server, proxy_port))
            sock.close()
            
            if result != 0:
                return False, f"Cannot connect to proxy {proxy_server}:{proxy_port}"
            
            # Test HTTP proxy
            proxies = {
                'http': f'http://{proxy_server}:{proxy_port}',
                'https': f'http://{proxy_server}:{proxy_port}'
            }
            
            if proxy_username and proxy_password:
                proxies['http'] = f'http://{proxy_username}:{proxy_password}@{proxy_server}:{proxy_port}'
                proxies['https'] = f'http://{proxy_username}:{proxy_password}@{proxy_server}:{proxy_port}'
            
            response = requests.get('http://httpbin.org/ip', proxies=proxies, timeout=10)
            
            if response.status_code == 200:
                ip_info = response.json()
                return True, f"Proxy working! Your IP: {ip_info.get('origin', 'Unknown')}"
            else:
                return False, f"Proxy test failed with status: {response.status_code}"
                
        except Exception as e:
            return False, f"Proxy test error: {str(e)}"

    def analyze_profile_proxy_status(self, profile_name):
        """Analyze if a profile has proxy configured"""
        try:
            print(f"[DEBUG] [ANALYZE] Analyzing proxy status for profile: {profile_name}")
            
            profile_path = self.get_profile_path(profile_name)
            if not profile_path or not os.path.exists(profile_path):
                return False, "Profile not found"
            
            extension_id = "pfnededegaaopdmhkdmcofjmoldfiped"
            
            # Check extension installation
            ext_path = os.path.join(profile_path, "Default", "Extensions", extension_id)
            if not os.path.exists(ext_path):
                return False, "SwitchyOmega extension not installed"
            
            # Check extension settings
            local_ext_path = os.path.join(profile_path, "Default", "Local Extension Settings", extension_id)
            if not os.path.exists(local_ext_path):
                return False, "Extension settings not found"
            
            # Check IndexedDB for proxy data
            indexeddb_path = os.path.join(profile_path, "Default", "IndexedDB")
            proxy_db_found = False
            
            if os.path.exists(indexeddb_path):
                for item in os.listdir(indexeddb_path):
                    if "chrome-extension" in item and extension_id in item:
                        proxy_db_found = True
                        break
            
            if not proxy_db_found:
                return False, "No proxy data found in IndexedDB"
            
            # Check Preferences for extension state
            prefs_file = os.path.join(profile_path, "Default", "Preferences")
            if os.path.exists(prefs_file):
                try:
                    with open(prefs_file, 'r', encoding='utf-8') as f:
                        prefs = json.load(f)
                    
                    # Check if extension is enabled
                    if 'extensions' in prefs:
                        ext_data = prefs['extensions']
                        
                        # Check if extension is in state
                        if 'state' in ext_data and extension_id in ext_data['state']:
                            ext_state = ext_data['state'][extension_id]
                            if ext_state.get('enabled', False):
                                return True, "Proxy configured and extension enabled"
                            else:
                                return False, "Extension disabled"
                        else:
                            # Extension not in state, but might be configured
                            # Check if extension is in install_signature
                            if 'install_signature' in ext_data and 'ids' in ext_data['install_signature']:
                                if extension_id in ext_data['install_signature']['ids']:
                                    return True, "Extension installed and configured"
                            
                            return False, "Extension not in state"
                    else:
                        return False, "No extensions section in preferences"
                except Exception as e:
                    return False, f"Error reading preferences: {str(e)}"
            
            return False, "Preferences file not found"
            
        except Exception as e:
            return False, f"Analysis error: {str(e)}"

    def get_profiles_with_proxy(self):
        """Get all profiles that have proxy configured"""
        all_profiles = self.get_all_profiles()
        proxy_profiles = []
        
        print(f"[DEBUG] [ANALYZE] Analyzing {len(all_profiles)} profiles for proxy status...")
        
        for profile in all_profiles:
            has_proxy, message = self.analyze_profile_proxy_status(profile)
            if has_proxy:
                proxy_profiles.append(profile)
                print(f"[SUCCESS] {profile}: {message}")
            else:
                print(f"[ERROR] {profile}: {message}")
        
        return proxy_profiles

    def get_profiles_without_proxy(self):
        """Get all profiles that don't have proxy configured"""
        all_profiles = self.get_all_profiles()
        no_proxy_profiles = []
        
        print(f"[DEBUG] [ANALYZE] Analyzing {len(all_profiles)} profiles for missing proxy...")
        
        for profile in all_profiles:
            has_proxy, message = self.analyze_profile_proxy_status(profile)
            if not has_proxy:
                no_proxy_profiles.append(profile)
                print(f"[ERROR] {profile}: {message}")
            else:
                print(f"[SUCCESS] {profile}: {message}")
        
        return no_proxy_profiles

    def smart_configure_proxy(self, profile_name, proxy_string):
        """Smart proxy configuration - check if profile needs proxy setup"""
        print(f"🧠 [SMART] Smart proxy configuration for {profile_name}")
        
        # Check current status
        has_proxy, message = self.analyze_profile_proxy_status(profile_name)
        
        if has_proxy:
            print(f"ℹ️ [SMART] Profile {profile_name} already has proxy configured: {message}")
            return True, f"Proxy already configured: {message}"
        
        # Configure proxy
        print(f"[TOOL] [SMART] Configuring proxy for {profile_name}...")
        success, result_message = self.input_proxy_from_ui(profile_name, proxy_string)
        
        if success:
            print(f"[SUCCESS] [SMART] Successfully configured proxy for {profile_name}")
            return True, result_message
        else:
            print(f"[ERROR] [SMART] Failed to configure proxy for {profile_name}: {result_message}")
            return False, result_message

    def bulk_smart_configure_proxy(self, profile_list, proxy_string):
        """Bulk smart proxy configuration"""
        print(f"🧠 [SMART] Bulk smart proxy configuration for {len(profile_list)} profiles")
        
        results = []
        success_count = 0
        
        for profile_name in profile_list:
            print(f"\n[CREATE] [SMART] Processing {profile_name}...")
            success, message = self.smart_configure_proxy(profile_name, proxy_string)
            
            results.append({
                'profile': profile_name,
                'success': success,
                'message': message
            })
            
            if success:
                success_count += 1
        
        return results, success_count
    
    def ultimate_auto_2fa_handler(self, email, password=None, refresh_token=None, client_id="9e5f94bc-e8a4-4e73-b8be-63364c29d753"):
        """Ultimate Auto 2FA Handler - Xử lý tự động hoàn toàn"""
        print(f"[PROFILE] [ULTIMATE] Bắt đầu process tự động TikTok 2FA for: {email}")
        print(f"[TIME] [ULTIMATE] Thời gian start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # Thử the phương pháp theo thứ tự ưu tiên
        methods = []
        
        # Method 1: Refresh token (if have)
        if refresh_token and refresh_token != 'ep':
            methods.append(('refresh_token', refresh_token, client_id))
        
        # Method 2: Device login (luôn have thể try)
        if client_id:
            methods.append(('device_login', None, client_id))
        
        # Method 3: IMAP (if have password)
        if password and password != 'ep':
            methods.append(('imap', password, None))
        
        for method_name, method_data, client_id in methods:
            try:
                print(f"[REFRESH] [ULTIMATE] Thử phương pháp: {method_name}")
                
                if method_name == 'refresh_token':
                    success, result = self._try_refresh_token_method(method_data, client_id, email)
                elif method_name == 'device_login':
                    success, result = self._try_device_login_method(client_id, email)
                elif method_name == 'imap':
                    success, result = self._try_imap_method(email, method_data)
                
                if success:
                    print(f"[SUCCESS] [ULTIMATE] THÀNH CÔNG! Mã TikTok: {result}")
                    return True, result
                
            except Exception as e:
                print(f"[WARNING] [ULTIMATE] Error phương pháp {method_name}: {e}")
                continue
        
        print("[ERROR] [ULTIMATE] Tất cả phương pháp đều thất bại")
        return False, "Tất cả phương pháp đều thất bại"
    
    def continuous_monitor_2fa(self, email, password=None, refresh_token=None, client_id="9e5f94bc-e8a4-4e73-b8be-63364c29d753", duration=300, interval=30):
        """Continuous Monitor 2FA - Monitor liên tục"""
        print(f"[DEBUG] [MONITOR] Bắt đầu monitor TikTok 2FA for: {email}")
        print(f"[TIME] [MONITOR] Thời gian monitor: {duration} giây")
        print(f"[REFRESH] [MONITOR] Khoảng thời gian check: {interval} giây")
        print(f"[TIME] [MONITOR] Thời gian start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        found_codes = set()
        start_time = time.time()
        
        while time.time() - start_time < duration:
            try:
                print(f"[DEBUG] [MONITOR] Kiểm tra code mới... {datetime.now().strftime('%H:%M:%S')}")
                
                # Thử lấy code
                success, result = self.ultimate_auto_2fa_handler(email, password, refresh_token, client_id)
                
                if success and result not in found_codes:
                    found_codes.add(result)
                    print(f"[SUCCESS] [MONITOR] Tìm found code TikTok mới: {result}")
                    print(f"[TIME] [MONITOR] Thời gian: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    return True, result
                
                print("[WAITING] [MONITOR] Chưa have code mới")
                time.sleep(interval)
                
            except KeyboardInterrupt:
                print("⏹️ [MONITOR] Dừng monitor...")
                break
            except Exception as e:
                print(f"[ERROR] [MONITOR] Error monitor: {e}")
                time.sleep(interval)
        
        print("[TIME] [MONITOR] Kết thúc monitor")
        return False, "Monitor timeout"

    def change_tiktok_password(self, profile_name, old_password, new_password):
        """Đổi mật khẩu TikTok for profile"""
        try:
            print(f"[SECURITY] [CHANGE-PASSWORD] Đổi mật khẩu TikTok for {profile_name}")
            
            # Lấy thông tin session hiện tại
            success, session_data = self.load_tiktok_session(profile_name)
            if not success:
                return False, "No thể load session data"
            
            # Lấy thông tin login
            email = session_data.get('email', '')
            if not email:
                return False, "No find found email in session"
            
            # Launch Chrome profile
            driver = self.launch_chrome_profile(profile_name, hidden=False, auto_login=False)
            if not driver:
                return False, "No thể launch Chrome profile"
            
            try:
                # Đi đến trang TikTok
                driver.get("https://www.tiktok.com/setting/account/password")
                time.sleep(3)
                
                # Kiểm tra xem done login chưa
                if "login" in driver.current_url.lower():
                    return False, "Profile chưa login TikTok"
                
                # Tìm and fill mật khẩu cũ
                old_pwd_input = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.NAME, "oldPassword"))
                )
                old_pwd_input.clear()
                old_pwd_input.send_keys(old_password)
                
                # Tìm and fill mật khẩu mới
                new_pwd_input = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.NAME, "newPassword"))
                )
                new_pwd_input.clear()
                new_pwd_input.send_keys(new_password)
                
                # Tìm and fill xác nhận mật khẩu mới
                confirm_pwd_input = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.NAME, "confirmPassword"))
                )
                confirm_pwd_input.clear()
                confirm_pwd_input.send_keys(new_password)
                
                # Tìm and click nút Submit
                submit_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
                )
                submit_button.click()
                
                # Chờ kết quả
                time.sleep(5)
                
                # Kiểm tra kết quả
                if "success" in driver.current_url.lower() or "password" not in driver.current_url.lower():
                    # Cập nhật session data with mật khẩu mới
                    session_data['password'] = new_password
                    session_data['updated_at'] = datetime.now().isoformat()
                    
                    # Lưu session data mới
                    self.save_tiktok_session(profile_name, session_data)
                    
                    return True, "Đổi mật khẩu thành công!"
                else:
                    return False, "Đổi mật khẩu thất bại. Vui lòng check mật khẩu cũ."
                    
            except Exception as e:
                return False, f"Error when đổi mật khẩu: {str(e)}"
            finally:
                driver.quit()
                
        except Exception as e:
            return False, f"Error hệ thống: {str(e)}"

    def get_microsoft_mx_and_emails(self, profile_name, microsoft_email, microsoft_password):
        """Lấy MX from Microsoft and lấy mail đổi password"""
        try:
            print(f"[EMAIL] [MICROSOFT-MX] Lấy MX from Microsoft for {profile_name}")
            
            # Lấy thông tin session hiện tại
            success, session_data = self.load_tiktok_session(profile_name)
            if not success:
                return False, "No thể load session data"
            
            # Sử dụng Microsoft Graph API to lấy emails
            import requests
            import json
            
            # Microsoft Graph API endpoint
            graph_url = "https://graph.microsoft.com/v1.0/me/messages"
            
            # Headers for Microsoft Graph API
            headers = {
                'Authorization': f'Bearer {self._get_microsoft_token(microsoft_email, microsoft_password)}',
                'Content-Type': 'application/json'
            }
            
            # Lấy emails liên quan đến TikTok
            params = {
                '$filter': "contains(subject,'TikTok') or contains(subject,'verification') or contains(subject,'code')",
                '$orderby': 'receivedDateTime desc',
                '$top': 10
            }
            
            response = requests.get(graph_url, headers=headers, params=params)
            
            if response.status_code == 200:
                emails = response.json().get('value', [])
                
                # Lưu emails ando session data
                session_data['microsoft_emails'] = emails
                session_data['microsoft_email'] = microsoft_email
                session_data['updated_at'] = datetime.now().isoformat()
                
                # Lưu session data
                self.save_tiktok_session(profile_name, session_data)
                
                return True, f"Done lấy get {len(emails)} emails from Microsoft"
            else:
                return False, f"Error when lấy emails: {response.status_code} - {response.text}"
                
        except Exception as e:
            return False, f"Error hệ thống: {str(e)}"

    def _get_microsoft_token(self, email, password):
        """Lấy Microsoft Graph API token"""
        try:
            import requests
            
            # Microsoft OAuth2 endpoint
            token_url = "https://login.microsoftonline.com/common/oauth2/v2.0/token"
            
            # Client ID for Microsoft Graph API
            client_id = "9e5f94bc-e8a4-4e73-b8be-63364c29d753"
            
            # Data for OAuth2
            data = {
                'client_id': client_id,
                'scope': 'https://graph.microsoft.com/.default',
                'grant_type': 'password',
                'username': email,
                'password': password
            }
            
            response = requests.post(token_url, data=data)
            
            if response.status_code == 200:
                token_data = response.json()
                return token_data.get('access_token')
            else:
                raise Exception(f"Error lấy token: {response.status_code} - {response.text}")
                
        except Exception as e:
            raise Exception(f"Error lấy Microsoft token: {str(e)}")


class ChromeExtensionManager:
    """
    Modern extension management system for Chrome profiles.
    Allows copying extensions from source profile to target profiles via GUI.
    """
    
    def __init__(self):
        """Initialize extension manager"""
        pass
    
    def load_extensions_from_profile(self, profile_path):
        """
        Load all extensions from a Chrome profile.
        
        Args:
            profile_path (str): Path to Chrome profile folder (e.g., "C:\\Users\\admin\\AppData\\Local\\Google\\Chrome\\User Data\\Profile 3")
        
        Returns:
            list: List of dicts with keys: {'id', 'name', 'version', 'path', 'enabled'}
        """
        extensions = []
        
        try:
            # Try Default/Extensions first (most common)
            extensions_dir = os.path.join(profile_path, "Default", "Extensions")
            if not os.path.exists(extensions_dir):
                # Try direct Extensions folder
                extensions_dir = os.path.join(profile_path, "Extensions")
                if not os.path.exists(extensions_dir):
                    print(f"[ERROR] [EXT-MGR] No Extensions folder found in: {profile_path}")
                    return []
            
            if not os.path.exists(extensions_dir):
                return []
            
            # Read Preferences to check enabled state
            preferences_path = os.path.join(profile_path, "Default", "Preferences")
            if not os.path.exists(preferences_path):
                preferences_path = os.path.join(profile_path, "Preferences")
            
            enabled_extensions = set()
            disabled_extensions = set()
            
            if os.path.exists(preferences_path):
                try:
                    with open(preferences_path, 'r', encoding='utf-8') as f:
                        prefs = json.load(f)
                        ext_settings = prefs.get('extensions', {}).get('settings', {})
                        for ext_id, ext_data in ext_settings.items():
                            state = ext_data.get('state', 0)
                            if state == 1:  # Enabled
                                enabled_extensions.add(ext_id)
                            elif state == 0:  # Disabled
                                disabled_extensions.add(ext_id)
                except Exception as e:
                    print(f"[WARNING] [EXT-MGR] Could not read Preferences: {e}")
            
            # Scan extension folders
            for item in os.listdir(extensions_dir):
                ext_folder = os.path.join(extensions_dir, item)
                if not os.path.isdir(ext_folder):
                    continue
                
                # Extension ID is the folder name
                extension_id = item
                
                # Find version folders
                version_folders = [d for d in os.listdir(ext_folder) 
                                  if os.path.isdir(os.path.join(ext_folder, d))]
                
                if not version_folders:
                    continue
                
                # Get latest version
                latest_version = sorted(version_folders)[-1]
                version_path = os.path.join(ext_folder, latest_version)
                
                # Read manifest.json
                manifest_path = os.path.join(version_path, "manifest.json")
                if not os.path.exists(manifest_path):
                    continue
                
                try:
                    with open(manifest_path, 'r', encoding='utf-8') as f:
                        manifest = json.load(f)
                        ext_name = manifest.get('name', extension_id)
                        ext_version = manifest.get('version', latest_version)
                        
                        # Determine enabled state
                        is_enabled = extension_id in enabled_extensions
                        if extension_id not in enabled_extensions and extension_id not in disabled_extensions:
                            is_enabled = True  # Default to enabled if not specified
                        
                        extensions.append({
                            'id': extension_id,
                            'name': ext_name,
                            'version': ext_version,
                            'path': ext_folder,  # Full path to extension folder
                            'version_path': version_path,  # Path to specific version
                            'enabled': is_enabled,
                            'manifest': manifest
                        })
                except Exception as e:
                    print(f"[WARNING] [EXT-MGR] Could not read manifest for {extension_id}: {e}")
                    continue
            
            print(f"[SUCCESS] [EXT-MGR] Loaded {len(extensions)} extensions from {profile_path}")
            return extensions
            
        except Exception as e:
            print(f"[ERROR] [EXT-MGR] Error loading extensions from {profile_path}: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def list_available_profiles(self, base_path):
        """
        List all Chrome profiles in User Data directory.
        
        Args:
            base_path (str): Path to Chrome User Data folder (e.g., "C:\\Users\\admin\\AppData\\Local\\Google\\Chrome\\User Data")
        
        Returns:
            list: List of dicts with keys: {'name', 'path', 'is_default'}
        """
        profiles = []
        
        try:
            if not os.path.exists(base_path):
                print(f"[ERROR] [EXT-MGR] User Data path does not exist: {base_path}")
                return []
            
            # Check Default profile
            default_path = os.path.join(base_path, "Default")
            if os.path.exists(default_path):
                profiles.append({
                    'name': 'Default',
                    'path': default_path,
                    'is_default': True
                })
            
            # Check numbered profiles (Profile 1, Profile 2, etc.)
            for item in os.listdir(base_path):
                item_path = os.path.join(base_path, item)
                if os.path.isdir(item_path) and item.startswith("Profile "):
                    profiles.append({
                        'name': item,
                        'path': item_path,
                        'is_default': False
                    })
            
            # Sort profiles: Default first, then numbered
            profiles.sort(key=lambda x: (not x['is_default'], x['name']))
            
            print(f"[SUCCESS] [EXT-MGR] Found {len(profiles)} profiles in {base_path}")
            return profiles
            
        except Exception as e:
            print(f"[ERROR] [EXT-MGR] Error listing profiles from {base_path}: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def install_extension_to_profiles(self, extension_id, source_profile_path, target_profile_paths):
        """
        Copy extension from source profile to target profiles and enable it.
        
        Args:
            extension_id (str): Extension ID
            source_profile_path (str): Source profile path
            target_profile_paths (list): List of target profile paths
        
        Returns:
            dict: {'success_count': int, 'failed_count': int, 'results': list}
        """
        results = []
        success_count = 0
        failed_count = 0
        
        try:
            # Find extension in source profile
            source_ext_dir = None
            extensions_dirs = [
                os.path.join(source_profile_path, "Default", "Extensions"),
                os.path.join(source_profile_path, "Extensions")
            ]
            
            print(f"[DEBUG] [EXT-MGR] Looking for extension {extension_id} in source: {source_profile_path}")
            for ext_dir in extensions_dirs:
                print(f"[DEBUG] [EXT-MGR] Checking directory: {ext_dir}")
                if os.path.exists(ext_dir):
                    print(f"[DEBUG] [EXT-MGR] Directory exists, listing: {os.listdir(ext_dir)[:5]}")
                ext_folder = os.path.join(ext_dir, extension_id)
                print(f"[DEBUG] [EXT-MGR] Checking extension folder: {ext_folder} -> {os.path.exists(ext_folder)}")
                if os.path.exists(ext_folder):
                    source_ext_dir = ext_folder
                    print(f"[DEBUG] [EXT-MGR] Found extension at: {source_ext_dir}")
                    break
            
            if not source_ext_dir:
                error_msg = f"Extension {extension_id} not found in source profile: {source_profile_path}"
                print(f"[ERROR] [EXT-MGR] {error_msg}")
                print(f"[DEBUG] [EXT-MGR] Checked directories: {extensions_dirs}")
                return {'success_count': 0, 'failed_count': len(target_profile_paths), 
                       'results': [{'profile': p, 'success': False, 'message': error_msg} 
                                   for p in target_profile_paths]}
            
            # Copy to each target profile
            for target_profile_path in target_profile_paths:
                try:
                    print(f"[DEBUG] [EXT-MGR] Processing target profile: {target_profile_path}")
                    print(f"[DEBUG] [EXT-MGR] Target profile exists: {os.path.exists(target_profile_path)}")
                    
                    # Ensure Default directory exists first
                    default_dir = os.path.join(target_profile_path, "Default")
                    if not os.path.exists(default_dir):
                        os.makedirs(default_dir)
                        print(f"[DEBUG] [EXT-MGR] Created Default directory: {default_dir}")
                    else:
                        print(f"[DEBUG] [EXT-MGR] Default directory already exists: {default_dir}")
                    
                    # Ensure Extensions directory exists
                    target_ext_dir = os.path.join(target_profile_path, "Default", "Extensions")
                    if not os.path.exists(target_ext_dir):
                        os.makedirs(target_ext_dir)
                        print(f"[DEBUG] [EXT-MGR] Created Extensions directory: {target_ext_dir}")
                    else:
                        print(f"[DEBUG] [EXT-MGR] Extensions directory already exists: {target_ext_dir}")
                    
                    target_ext_folder = os.path.join(target_ext_dir, extension_id)
                    print(f"[DEBUG] [EXT-MGR] Target extension folder: {target_ext_folder}")
                    
                    # Remove existing extension if present
                    if os.path.exists(target_ext_folder):
                        print(f"[DEBUG] [EXT-MGR] Removing existing extension folder: {target_ext_folder}")
                        shutil.rmtree(target_ext_folder)
                    
                    # Copy extension folder
                    print(f"[DEBUG] [EXT-MGR] Copying from {source_ext_dir} to {target_ext_folder}")
                    try:
                        # Remove target if exists
                        if os.path.exists(target_ext_folder):
                            shutil.rmtree(target_ext_folder)
                        
                        # Copy entire extension folder (including version folders)
                        shutil.copytree(source_ext_dir, target_ext_folder)
                        print(f"[SUCCESS] [EXT-MGR] Copied {extension_id} to {target_profile_path}")
                        
                        # Verify copy was successful
                        if not os.path.exists(target_ext_folder):
                            raise Exception(f"Extension folder was not copied successfully to {target_ext_folder}")
                        
                        # Count files to verify
                        source_count = sum(len(files) for _, _, files in os.walk(source_ext_dir))
                        target_count = sum(len(files) for _, _, files in os.walk(target_ext_folder))
                        print(f"[DEBUG] [EXT-MGR] Copy verification: Source files: {source_count}, Target files: {target_count}")
                        
                        if target_count == 0:
                            raise Exception(f"No files were copied to {target_ext_folder}")
                        if target_count < source_count * 0.9:  # Allow 10% difference for temp files
                            print(f"[WARNING] [EXT-MGR] File count mismatch: Expected ~{source_count}, got {target_count}")
                        
                    except Exception as copy_err:
                        error_msg = f"Failed to copy extension: {str(copy_err)}"
                        print(f"[ERROR] [EXT-MGR] {error_msg}")
                        raise Exception(error_msg)
                    
                    # Verify folder contents
                    copied_files = os.listdir(target_ext_folder)
                    print(f"[DEBUG] [EXT-MGR] Copied folder contains: {len(copied_files)} items")
                    print(f"[DEBUG] [EXT-MGR] Source folder contains: {len(os.listdir(source_ext_dir))} items")
                    
                    # Update Preferences to enable extension
                    print(f"[DEBUG] [EXT-MGR] Updating Preferences for {extension_id}...")
                    pref_result = self.update_preferences(target_profile_path, extension_id, None)
                    if not pref_result:
                        raise Exception(f"Failed to update Preferences for {extension_id}")
                    else:
                        print(f"[SUCCESS] [EXT-MGR] Preferences updated successfully for {extension_id}")
                    
                    # Final verification - CRITICAL CHECKS
                    pref_path = os.path.join(target_profile_path, "Default", "Preferences")
                    if not os.path.exists(pref_path):
                        pref_path = os.path.join(target_profile_path, "Preferences")
                    
                    if os.path.exists(pref_path):
                        with open(pref_path, 'r', encoding='utf-8') as pf:
                            pref_data = json.load(pf)
                            if extension_id not in pref_data.get('extensions', {}).get('settings', {}):
                                raise Exception(f"Extension {extension_id} NOT found in Preferences after update!")
                            
                            ext_data = pref_data['extensions']['settings'][extension_id]
                            # Chrome may not use 'state' field - check disable_reasons instead
                            disable_reasons = ext_data.get('disable_reasons', [])
                            has_state = 'state' in ext_data
                            ext_state = ext_data.get('state') if has_state else None
                            
                            print(f"[DEBUG] [EXT-MGR] Extension {extension_id} is in Preferences")
                            print(f"[DEBUG] [EXT-MGR] Has state field: {has_state}, State: {ext_state}")
                            print(f"[DEBUG] [EXT-MGR] Disable reasons: {disable_reasons}")
                            
                            # Ensure disable_reasons is empty (extension should be enabled)
                            if disable_reasons:
                                print(f"[WARNING] [EXT-MGR] Extension has disable_reasons: {disable_reasons}, clearing...")
                                ext_data['disable_reasons'] = []
                                with open(pref_path, 'w', encoding='utf-8') as pf:
                                    json.dump(pref_data, pf, indent=2, ensure_ascii=False)
                                print(f"[SUCCESS] [EXT-MGR] Cleared disable_reasons")
                            
                            # Verify required fields exist (match working profile structure)
                            required_fields = ['path', 'preferences', 'serviceworkerevents', 'manifest']
                            missing_fields = [f for f in required_fields if f not in ext_data]
                            if missing_fields:
                                print(f"[WARNING] [EXT-MGR] Missing fields: {missing_fields}, adding...")
                                if 'path' not in ext_data:
                                    # Find the extension path
                                    ext_dir = os.path.join(target_profile_path, "Default", "Extensions", extension_id)
                                    if os.path.exists(ext_dir):
                                        versions = [d for d in os.listdir(ext_dir) if os.path.isdir(os.path.join(ext_dir, d))]
                                        if versions:
                                            ext_data['path'] = f"{extension_id}\\{sorted(versions)[-1]}"
                                if 'preferences' not in ext_data:
                                    ext_data['preferences'] = {}
                                if 'regular_only_preferences' not in ext_data:
                                    ext_data['regular_only_preferences'] = {}
                                if 'serviceworkerevents' not in ext_data:
                                    ext_data['serviceworkerevents'] = []
                                with open(pref_path, 'w', encoding='utf-8') as pf:
                                    json.dump(pref_data, pf, indent=2, ensure_ascii=False)
                                print(f"[SUCCESS] [EXT-MGR] Added missing fields")
                            
                            # Final verification summary
                            print(f"[SUCCESS] [EXT-MGR] Installation verified:")
                            print(f"  - Extension folder: {target_ext_folder} ✓")
                            print(f"  - Preferences entry: {extension_id} ✓")
                            print(f"  - Path: {ext_data.get('path', 'N/A')} ✓")
                            print(f"  - Disable reasons: {ext_data.get('disable_reasons', [])} (empty = enabled) ✓")
                            print(f"  - Location: {ext_data.get('location', 'N/A')} ✓")
                            print(f"[NOTE] Please restart Chrome completely for extension to appear!")
                    else:
                        raise Exception(f"Preferences file not found: {pref_path}")
                    
                    # Verify extension folder still exists
                    if not os.path.exists(target_ext_folder):
                        raise Exception(f"Extension folder disappeared: {target_ext_folder}")
                    
                    # Double-check: Count version folders
                    version_folders = [d for d in os.listdir(target_ext_folder) 
                                     if os.path.isdir(os.path.join(target_ext_folder, d))]
                    if not version_folders:
                        raise Exception(f"No version folders found in extension: {target_ext_folder}")
                    print(f"[DEBUG] [EXT-MGR] Extension has {len(version_folders)} version folder(s): {version_folders}")
                    
                    # Final success message
                    final_state = ext_state if 'ext_state' in locals() else 1
                    results.append({
                        'profile': target_profile_path,
                        'success': True,
                        'message': f"Extension installed and enabled (state={final_state})"
                    })
                    success_count += 1
                    
                except Exception as e:
                    error_msg = f"Error installing to {target_profile_path}: {str(e)}"
                    print(f"[ERROR] [EXT-MGR] {error_msg}")
                    results.append({
                        'profile': target_profile_path,
                        'success': False,
                        'message': error_msg
                    })
                    failed_count += 1
            
            print(f"[SUCCESS] [EXT-MGR] Installation complete: {success_count} success, {failed_count} failed")
            return {'success_count': success_count, 'failed_count': failed_count, 'results': results}
            
        except Exception as e:
            error_msg = f"Error in install_extension_to_profiles: {str(e)}"
            print(f"[ERROR] [EXT-MGR] {error_msg}")
            import traceback
            traceback.print_exc()
            return {'success_count': 0, 'failed_count': len(target_profile_paths), 
                   'results': [{'profile': p, 'success': False, 'message': error_msg} 
                              for p in target_profile_paths]}
    
    def set_omocaptcha_api_key(self, profile_name, api_key, extension_id=None):
        """
        Set OMOcaptcha API key in extension storage for the profile.
        Tìm extension OMOcaptcha và lưu API key vào chrome.storage.local
        
        Args:
            profile_name (str): Profile name (not full path)
            api_key (str): OMOcaptcha API key
        """
        try:
            profile_path = self.get_profile_path(profile_name)
            if not os.path.exists(profile_path):
                print(f"[ERROR] [OMO] Profile path not found: {profile_path}")
                return False
            
            # Tìm extension ID của OMOcaptcha (ưu tiên override/config hoặc tham số)
            # Thường extension ID có thể tìm trong Default/Extensions hoặc Extensions folder
            ext_dirs = [
                os.path.join(profile_path, "Default", "Extensions"),
                os.path.join(profile_path, "Extensions")
            ]
            
            omocaptcha_extension_id = (extension_id or self._get_omocaptcha_extension_id_override() or None)
            if omocaptcha_extension_id:
                print(f"[DEBUG] [OMO] Using overridden extension ID: {omocaptcha_extension_id}")
            for ext_dir in ext_dirs:
                if os.path.exists(ext_dir):
                    for ext_id_folder in os.listdir(ext_dir):
                        ext_id_path = os.path.join(ext_dir, ext_id_folder)
                        if os.path.isdir(ext_id_path):
                            # Check manifest.json để tìm extension name có chứa "omo" hoặc "captcha"
                            version_folders = [d for d in os.listdir(ext_id_path) 
                                             if os.path.isdir(os.path.join(ext_id_path, d))]
                            for version_folder in version_folders:
                                manifest_path = os.path.join(ext_id_path, version_folder, "manifest.json")
                                if os.path.exists(manifest_path):
                                    try:
                                        import json
                                        with open(manifest_path, 'r', encoding='utf-8') as f:
                                            manifest = json.load(f)
                                            ext_name = manifest.get('name', '').lower()
                                            if 'omo' in ext_name or 'captcha' in ext_name:
                                                omocaptcha_extension_id = ext_id_folder
                                                print(f"[DEBUG] [OMO] Found OMOcaptcha extension: {omocaptcha_extension_id}")
                                                break
                                    except:
                                        pass
                            if omocaptcha_extension_id:
                                break
                if omocaptcha_extension_id:
                    break
            
            if not omocaptcha_extension_id:
                # Nếu không tìm thấy, thử tìm trong Preferences
                prefs_path = os.path.join(profile_path, "Default", "Preferences")
                if not os.path.exists(prefs_path):
                    prefs_path = os.path.join(profile_path, "Preferences")
                
                if os.path.exists(prefs_path):
                    with open(prefs_path, 'r', encoding='utf-8') as f:
                        prefs = json.load(f)
                        extensions = prefs.get('extensions', {}).get('settings', {})
                        for ext_id, ext_data in extensions.items():
                            manifest = ext_data.get('manifest', {})
                            ext_name = manifest.get('name', '').lower()
                            if 'omo' in ext_name or 'captcha' in ext_name:
                                omocaptcha_extension_id = ext_id
                                print(f"[DEBUG] [OMO] Found OMOcaptcha extension in Preferences: {omocaptcha_extension_id}")
                                break
            
            if not omocaptcha_extension_id:
                print(f"[WARNING] [OMO] Không tìm thấy extension OMOcaptcha trong profile {profile_name}")
                print(f"[INFO] [OMO] Vui lòng cài đặt extension OMOcaptcha trước")
                return False
            
            # Nếu Chrome đang chạy (DevToolsActivePort tồn tại), không chỉnh file để tránh hỏng Preferences
            devtools_flag = os.path.join(profile_path, 'DevToolsActivePort')
            if os.path.exists(devtools_flag):
                print(f"[WARNING] [OMO] Chrome is running for {profile_name}; skip writing settings. Retry after closing Chrome.")
                return False

            # Lưu API key vào Local Extension Settings
            # Chrome lưu extension storage trong: Default/Local Extension Settings/{extension_id}/
            local_ext_path = os.path.join(profile_path, "Default", "Local Extension Settings", omocaptcha_extension_id)
            os.makedirs(local_ext_path, exist_ok=True)
            
            # Chrome sử dụng LevelDB format, nhưng có thể lưu trực tiếp vào Preferences của extension
            # Hoặc sử dụng cách đơn giản hơn: inject vào localStorage khi launch
            
            # Cách 2: Lưu vào Preferences file của extension (nếu extension đọc từ đây)
            # Hoặc lưu vào file đơn giản mà extension có thể đọc
            
            # Cách tốt nhất: Inject API key vào chrome.storage.local khi launch browser
            # Lưu tạm vào file để inject sau
            api_key_file = os.path.join(local_ext_path, "api_key.txt")
            with open(api_key_file, 'w', encoding='utf-8') as f:
                f.write(api_key)
            
            # KHÔNG ghi Preferences nữa để tránh lỗi "Không thể đọc tuỳ chọn của bạn"
            print(f"[SUCCESS] [OMO] Đã lưu api_key.txt cho extension {omocaptcha_extension_id} tại profile {profile_name}")
            print(f"[INFO] [OMO] Key sẽ được inject vào chrome.storage.local sau khi khởi chạy Chrome")
            return True
            
        except Exception as e:
            print(f"[ERROR] [OMO] Error setting OMOcaptcha API key: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def update_preferences(self, profile_path, extension_id, extension_name=None):
        """
        Update Preferences file to enable extension.
        
        Args:
            profile_path (str): Profile path
            extension_id (str): Extension ID
            extension_name (str, optional): Extension name (if None, will try to read from manifest)
        """
        try:
            # Try Default/Preferences first
            preferences_path = os.path.join(profile_path, "Default", "Preferences")
            if not os.path.exists(preferences_path):
                preferences_path = os.path.join(profile_path, "Preferences")
            
            if not os.path.exists(preferences_path):
                print(f"[WARNING] [EXT-MGR] Preferences file not found: {preferences_path}")
                return False
            
            # Read current preferences
            with open(preferences_path, 'r', encoding='utf-8') as f:
                prefs = json.load(f)
            
            # Initialize extensions.settings if not exists
            if 'extensions' not in prefs:
                prefs['extensions'] = {}
            if 'settings' not in prefs['extensions']:
                prefs['extensions']['settings'] = {}
            
            # Define ext_dirs for later use
            ext_dirs = [
                os.path.join(profile_path, "Default", "Extensions", extension_id),
                os.path.join(profile_path, "Extensions", extension_id)
            ]
            
            # Get extension name from manifest if not provided
            if extension_name is None:
                for ext_dir in ext_dirs:
                    if os.path.exists(ext_dir):
                        version_folders = [d for d in os.listdir(ext_dir) 
                                          if os.path.isdir(os.path.join(ext_dir, d))]
                        if version_folders:
                            latest_version = sorted(version_folders)[-1]
                            manifest_path = os.path.join(ext_dir, latest_version, "manifest.json")
                            if os.path.exists(manifest_path):
                                try:
                                    with open(manifest_path, 'r', encoding='utf-8') as mf:
                                        manifest = json.load(mf)
                                        extension_name = manifest.get('name', extension_id)
                                except:
                                    extension_name = extension_id
                                break
                if extension_name is None:
                    extension_name = extension_id
            
            # Get extension version from manifest if available
            extension_version = "1.0"
            for ext_dir in ext_dirs:
                if os.path.exists(ext_dir):
                    version_folders = [d for d in os.listdir(ext_dir) 
                                      if os.path.isdir(os.path.join(ext_dir, d))]
                    if version_folders:
                        extension_version = sorted(version_folders)[-1]
                        break
            
            import time
            # Chrome uses microseconds timestamp format: "13406527510509987"
            # We'll use current time in microseconds
            current_time_us = str(int(time.time() * 10000000))  # Convert to microseconds-like format
            
            # Find the actual extension path (version folder)
            extension_path = None
            for ext_dir in ext_dirs:
                if os.path.exists(ext_dir):
                    version_folders = [d for d in os.listdir(ext_dir) 
                                      if os.path.isdir(os.path.join(ext_dir, d))]
                    if version_folders:
                        latest_version = sorted(version_folders)[-1]
                        extension_path = f"{extension_id}\\{latest_version}"
                        break
            
            # Initialize extension settings structure - match Chrome's actual format
            ext_settings = {
                "creation_flags": 9,  # 9 = installed by user, 1 = installed by default
                "first_install_time": current_time_us,
                "last_update_time": current_time_us,
                "location": 1,  # 1 = component/external, 2 = unpacked
                # Note: Chrome may not use 'state' field, so we don't include it initially
                "disable_reasons": [],
                "granted_permissions": {},
                "active_permissions": {
                    "api": [],
                    "explicit_host": [],
                    "manifest_permissions": [],
                    "scriptable_host": []
                },
                "withholding_permissions": False,
                "incognito_content_settings": [],
                "incognito_preferences": {},
                "content_settings": [],
                "commands": {},
                "account_extension_type": 0,
                "was_installed_by_default": False,
                "was_installed_by_custodian": False,
                "was_installed_by_oem": False,
                "was_installed_by_policy": False,
                "from_webstore": False,
                "keep_if_present": False,
                "app_launcher_ordinal": "n",
                "page_ordinal": "n",
                "needs_sync": True,
                # Additional fields found in working profiles
                "preferences": {},
                "regular_only_preferences": {},
                "serviceworkerevents": []
            }
            
            # Add path if we found the extension folder
            if extension_path:
                ext_settings["path"] = extension_path
            
            # Try to read actual manifest for better data
            actual_manifest_data = None
            for ext_dir in ext_dirs:
                if os.path.exists(ext_dir):
                    version_folders = [d for d in os.listdir(ext_dir) 
                                      if os.path.isdir(os.path.join(ext_dir, d))]
                    if version_folders:
                        latest_version = sorted(version_folders)[-1]
                        manifest_path = os.path.join(ext_dir, latest_version, "manifest.json")
                        if os.path.exists(manifest_path):
                            try:
                                with open(manifest_path, 'r', encoding='utf-8') as mf:
                                    actual_manifest_data = json.load(mf)
                            except:
                                pass
                            break
            
            # Update manifest info from actual manifest if available
            if actual_manifest_data:
                ext_settings['manifest'] = actual_manifest_data  # Store full manifest
                # Update permissions structure - match Chrome's format exactly
                if 'permissions' in actual_manifest_data:
                    perms = actual_manifest_data['permissions']
                    if isinstance(perms, list):
                        # Convert to Chrome's permission format
                        granted_perms = {
                            "api": [p for p in perms if not p.startswith('http://') and not p.startswith('https://') and not p.startswith('<') and not '/' in p],
                            "explicit_host": [p for p in perms if p.startswith('http://') or p.startswith('https://') or p.startswith('<') or '/' in p],
                            "manifest_permissions": [],
                            "scriptable_host": []
                        }
                        ext_settings['granted_permissions'] = granted_perms
                        ext_settings['active_permissions'] = granted_perms.copy()
                    elif isinstance(perms, dict):
                        ext_settings['granted_permissions'] = perms
                        ext_settings['active_permissions'] = perms.copy()
                # Handle host_permissions for Manifest V3
                if 'host_permissions' in actual_manifest_data:
                    host_perms = actual_manifest_data['host_permissions']
                    if isinstance(host_perms, list):
                        if isinstance(ext_settings['granted_permissions'], dict):
                            # Merge host permissions into explicit_host
                            existing_hosts = ext_settings['granted_permissions'].get('explicit_host', [])
                            ext_settings['granted_permissions']['explicit_host'] = list(set(existing_hosts + host_perms))
                            ext_settings['active_permissions']['explicit_host'] = ext_settings['granted_permissions']['explicit_host'].copy()
            else:
                # Fallback manifest
                ext_settings['manifest'] = {
                    "name": extension_name,
                    "version": extension_version,
                    "manifest_version": 2
                }
            
            # Add extension settings to Preferences
            prefs['extensions']['settings'][extension_id] = ext_settings
            
            # Also add to extensions.pending if needed (Chrome sometimes checks this)
            if 'pending' not in prefs.get('extensions', {}):
                prefs['extensions']['pending'] = {}
            # Remove from pending if exists (extension is now installed)
            if extension_id in prefs['extensions']['pending']:
                del prefs['extensions']['pending'][extension_id]
            
            # Ensure extensions.install_signature exists
            if 'install_signature' not in prefs.get('extensions', {}):
                prefs['extensions']['install_signature'] = {}
            
            # Ensure extensions.last_chrome_version exists (Chrome checks this)
            if 'last_chrome_version' not in prefs.get('extensions', {}):
                prefs['extensions']['last_chrome_version'] = ""
            
            # Ensure extensions.alerts exists
            if 'alerts' not in prefs.get('extensions', {}):
                prefs['extensions']['alerts'] = {}
            
            # Ensure extensions.chrome_url_overrides exists
            if 'chrome_url_overrides' not in prefs.get('extensions', {}):
                prefs['extensions']['chrome_url_overrides'] = {}
            
            # Write back to file (ensure proper JSON format)
            try:
                # Create backup
                backup_path = preferences_path + '.bak'
                if os.path.exists(preferences_path):
                    shutil.copy2(preferences_path, backup_path)
                
                # Write with proper formatting
                with open(preferences_path, 'w', encoding='utf-8') as f:
                    json.dump(prefs, f, indent=2, ensure_ascii=False)
                
                print(f"[DEBUG] [EXT-MGR] Preferences file written: {preferences_path}")
                
                # Verify write
                with open(preferences_path, 'r', encoding='utf-8') as f:
                    verify_prefs = json.load(f)
                    if extension_id in verify_prefs.get('extensions', {}).get('settings', {}):
                        print(f"[DEBUG] [EXT-MGR] Verification: Extension {extension_id} found in Preferences")
                    else:
                        print(f"[ERROR] [EXT-MGR] Verification FAILED: Extension {extension_id} NOT in Preferences!")
                        # Restore backup
                        if os.path.exists(backup_path):
                            shutil.copy2(backup_path, preferences_path)
                        return False
            except Exception as write_error:
                print(f"[ERROR] [EXT-MGR] Error writing Preferences: {write_error}")
                # Restore backup if exists
                backup_path = preferences_path + '.bak'
                if os.path.exists(backup_path):
                    shutil.copy2(backup_path, preferences_path)
                return False
            
            # Verify the extension was added to settings
            if extension_id in prefs.get('extensions', {}).get('settings', {}):
                ext_data = prefs['extensions']['settings'][extension_id]
                print(f"[SUCCESS] [EXT-MGR] Updated Preferences for {extension_id} in {profile_path}")
                print(f"[DEBUG] [EXT-MGR] Extension state: {ext_data.get('state')} (1=enabled, 0=disabled)")
                print(f"[DEBUG] [EXT-MGR] Extension path: {ext_data.get('path')}")
                return True
            else:
                print(f"[ERROR] [EXT-MGR] Extension {extension_id} was not added to Preferences!")
                return False
            
        except Exception as e:
            print(f"[ERROR] [EXT-MGR] Error updating Preferences: {e}")
            import traceback
            traceback.print_exc()
            return False
    
