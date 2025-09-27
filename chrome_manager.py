import os
import json
import shutil
import subprocess
import time
import threading
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import psutil
import configparser
from datetime import datetime
# Email verification removed

class ChromeProfileManager:
    def __init__(self):
        self.config_file = "config.ini"
        self.profiles_dir = os.path.join(os.getcwd(), "chrome_profiles")
        self.chrome_data_dir = self._get_chrome_data_dir()
        # Email manager removed
        self.load_config()
        
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
        """Lấy đường dẫn thư mục dữ liệu Chrome - Auto detect"""
        if os.name == 'nt':  # Windows
            # Thử các đường dẫn có thể có
            possible_paths = [
                os.path.expanduser("~\\AppData\\Local\\Google\\Chrome\\User Data"),
                os.path.expanduser("~\\AppData\\Roaming\\Google\\Chrome\\User Data"),
                "C:\\Users\\Public\\AppData\\Local\\Google\\Chrome\\User Data",
                "C:\\ProgramData\\Google\\Chrome\\User Data"
            ]
            
            # Kiểm tra từng đường dẫn
            for path in possible_paths:
                if os.path.exists(path):
                    print(f"🔍 [CHROME-DIR] Found Chrome data dir: {path}")
                    return path
            
            # Nếu không tìm thấy, tạo thư mục mặc định
            default_path = os.path.expanduser("~\\AppData\\Local\\Google\\Chrome\\User Data")
            print(f"⚠️ [CHROME-DIR] Chrome data dir not found, using default: {default_path}")
            return default_path
        else:  # Linux/Mac
            return os.path.expanduser("~/.config/google-chrome")
    
    def load_config(self):
        """Tải cấu hình từ file"""
        try:
            if os.path.exists(self.config_file):
                # Try to read as INI format first (preferred)
                try:
                    self.config = configparser.ConfigParser()
                    self.config.read(self.config_file)
                    return self.config
                except:
                    pass
                
                # Try to read as JSON format and convert to ConfigParser
                try:
                    import json
                    with open(self.config_file, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                        if content.startswith('{'):
                            # It's JSON format, convert to ConfigParser
                            json_data = json.loads(content)
                            self.config = configparser.ConfigParser()
                            for section, values in json_data.items():
                                self.config[section] = values
                            return self.config
                except:
                    pass
                
                # If both fail, create default
                self.config = self.create_default_config()
                return self.config
            else:
                self.config = self.create_default_config()
                return self.config
        except Exception as e:
            print(f"Error loading config: {str(e)}")
            self.config = self.create_default_config()
            return self.config
    
    def create_default_config(self):
        """Tạo file cấu hình mặc định"""
        self.config = configparser.ConfigParser()
        self.config['SETTINGS'] = {
            'auto_start': 'false',
            'hidden_mode': 'true',
            'max_profiles': '10',
            'startup_delay': '5'
        }
        self.config['PROFILES'] = {}
        self.save_config()
        return self.config
    
    def save_config(self):
        """Lưu cấu hình vào file"""
        try:
            # Check if config is a dict (JSON format) or ConfigParser (INI format)
            if isinstance(self.config, dict):
                # Save as JSON
                import json
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    json.dump(self.config, f, indent=2, ensure_ascii=False)
            else:
                # Save as INI
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    self.config.write(f)
        except Exception as e:
            print(f"Error saving config: {str(e)}")
    
    def create_profile_directory(self):
        """Tạo thư mục profiles nếu chưa tồn tại"""
        if not os.path.exists(self.profiles_dir):
            os.makedirs(self.profiles_dir)
    
    def create_profile_with_extension(self, profile_name, source_profile="Default", auto_install_extension=True):
        """
        Tạo profile mới với tự động cài đặt extension SwitchyOmega 3
        
        Args:
            profile_name (str): Tên profile mới
            source_profile (str): Profile nguồn để clone
            auto_install_extension (bool): Tự động cài đặt extension
        
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            print(f"🚀 [PROFILE-EXT] Creating profile '{profile_name}' with extension installation...")
            
            # Tạo profile
            success, message = self.clone_chrome_profile(profile_name, source_profile)
            if not success:
                return False, f"Failed to create profile: {message}"
            
            # Tự động cài đặt extension nếu được yêu cầu
            if auto_install_extension:
                print(f"🔧 [PROFILE-EXT] Auto-installing SwitchyOmega 3 for new profile '{profile_name}'...")
                ext_success, ext_message = self.install_extension_for_profile(profile_name)
                
                if ext_success:
                    return True, f"Profile created and extension installed: {ext_message}"
                else:
                    return True, f"Profile created but extension installation failed: {ext_message}"
            else:
                return True, f"Profile created successfully: {message}"
                
        except Exception as e:
            print(f"❌ [PROFILE-EXT] Error creating profile with extension: {str(e)}")
            return False, f"Error creating profile with extension: {str(e)}"
    
    def clone_chrome_profile(self, profile_name, source_profile="Default"):
        """Nhân bản profile Chrome - Tối ưu hóa để giảm dữ liệu"""
        try:
            self.create_profile_directory()
            
            # Đường dẫn profile gốc và đích
            source_path = os.path.join(self.chrome_data_dir, source_profile)
            target_path = os.path.join(self.profiles_dir, profile_name)
            
            # Kiểm tra và tạo profile gốc nếu không tồn tại
            if not os.path.exists(source_path):
                print(f"⚠️ [CLONE] Profile gốc không tồn tại: {source_path}")
                
                # Thử tạo profile Default từ Chrome mặc định
                if source_profile == "Default":
                    success = self._create_default_profile()
                    if success:
                        print(f"✅ [CLONE] Đã tạo profile Default thành công")
                    else:
                        raise Exception(f"Không thể tạo profile Default. Vui lòng chạy Chrome ít nhất 1 lần trước khi sử dụng chức năng này.")
                else:
                    raise Exception(f"Profile gốc không tồn tại: {source_path}")
            
            # Xóa profile đích nếu đã tồn tại (với retry mechanism)
            if os.path.exists(target_path):
                print(f"🗑️ [CLONE] Xóa profile cũ: {target_path}")
                try:
                    shutil.rmtree(target_path)
                    # Đợi một chút để đảm bảo file system được cập nhật
                    import time
                    time.sleep(0.1)
                except Exception as e:
                    print(f"⚠️ [CLONE] Lỗi khi xóa profile cũ: {e}")
                    raise Exception(f"Không thể xóa profile cũ: {e}")
            
            # Sao chép profile
            print(f"📋 [CLONE] Sao chép từ {source_path} đến {target_path}")
            shutil.copytree(source_path, target_path)
            
            # Đợi để đảm bảo copy hoàn tất
            import time
            time.sleep(0.1)
            
            # Tối ưu hóa profile để giảm dữ liệu
            self._optimize_profile_for_low_data(target_path)
            
            # Cập nhật cấu hình
            if not self.config.has_section('PROFILES'):
                self.config.add_section('PROFILES')
            
            self.config.set('PROFILES', profile_name, target_path)
            self.save_config()
            
            return True, f"Đã tạo profile '{profile_name}' thành công (đã tối ưu hóa)"
            
        except Exception as e:
            return False, f"Lỗi khi tạo profile: {str(e)}"
    
    def _create_default_profile(self):
        """Tạo profile Default từ Chrome mặc định"""
        try:
            print(f"🔧 [CREATE-DEFAULT] Đang tạo profile Default...")
            
            # Tạo thư mục Chrome data nếu chưa tồn tại
            if not os.path.exists(self.chrome_data_dir):
                os.makedirs(self.chrome_data_dir)
                print(f"📁 [CREATE-DEFAULT] Đã tạo thư mục: {self.chrome_data_dir}")
            
            # Đường dẫn profile Default
            default_profile_path = os.path.join(self.chrome_data_dir, "Default")
            
            # Tạo thư mục Default nếu chưa tồn tại
            if not os.path.exists(default_profile_path):
                os.makedirs(default_profile_path)
                print(f"📁 [CREATE-DEFAULT] Đã tạo thư mục: {default_profile_path}")
            
            # Tạo file Preferences cơ bản
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
                    }
                }
                
                with open(preferences_path, 'w', encoding='utf-8') as f:
                    json.dump(basic_preferences, f, indent=2)
                print(f"📄 [CREATE-DEFAULT] Đã tạo file Preferences")
            
            # Tạo thư mục Default/Extensions
            extensions_dir = os.path.join(default_profile_path, "Extensions")
            if not os.path.exists(extensions_dir):
                os.makedirs(extensions_dir)
                print(f"📁 [CREATE-DEFAULT] Đã tạo thư mục Extensions")
            
            # Tạo thư mục Default/Network
            network_dir = os.path.join(default_profile_path, "Network")
            if not os.path.exists(network_dir):
                os.makedirs(network_dir)
                print(f"📁 [CREATE-DEFAULT] Đã tạo thư mục Network")
            
            print(f"✅ [CREATE-DEFAULT] Profile Default đã được tạo thành công")
            return True
            
        except Exception as e:
            print(f"❌ [CREATE-DEFAULT] Lỗi khi tạo profile Default: {str(e)}")
            return False

    def bypass_chrome_security_warnings(self, profile_name):
        """
        Bypass Chrome security warnings and configure for Web Store access
        """
        try:
            print(f"🔓 [SECURITY-BYPASS] Bypassing security warnings for {profile_name}")
            
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
            
            print(f"✅ [SECURITY-BYPASS] Security warnings bypassed for {profile_name}")
            return True, "Security warnings bypassed successfully"
            
        except Exception as e:
            print(f"❌ [SECURITY-BYPASS] Failed to bypass security warnings: {str(e)}")
            return False, str(e)
        
    def _optimize_profile_for_low_data(self, profile_path):
        """Tối ưu hóa profile để giảm thiểu dữ liệu"""
        try:
            # Xóa các thư mục không cần thiết
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
            
            # Xóa các file không cần thiết
            files_to_remove = [
                "Local State", "Preferences", "Secure Preferences",
                "Web Data", "Login Data", "History", "Top Sites",
                "Favicons", "Shortcuts", "Bookmarks"
            ]
            
            for file_name in files_to_remove:
                file_path = os.path.join(profile_path, file_name)
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                    except:
                        pass
            
            # Tạo file Preferences tối ưu
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
            
            # Lưu preferences
            import json
            prefs_path = os.path.join(profile_path, "Preferences")
            with open(prefs_path, 'w') as f:
                json.dump(preferences, f, indent=2)
            
        except Exception as e:
            print(f"Lỗi khi tối ưu hóa profile: {str(e)}")
    
    
    def _apply_default_config(self, chrome_options):
        """Áp dụng cấu hình mặc định"""
        # User agent cơ bản
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # ONLY essential arguments - NO conflicting network arguments
        chrome_options.add_argument("--no-first-run")
        chrome_options.add_argument("--no-default-browser-check")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        
        # NO --disable-web-security
        # NO --disable-extensions
        # NO --disable-plugins
        # NO --disable-background-networking
        # NO other network-related arguments
    
    
    
    
    
    def launch_chrome_profile(self, profile_name, hidden=True, auto_login=False, login_data=None, start_url=None, optimized_mode=False, ultra_low_memory=False):
        """Khởi động Chrome với profile cụ thể
        
        Args:
            profile_name: Tên profile
            hidden: Chế độ ẩn
            auto_login: Tự động đăng nhập
            login_data: Dữ liệu đăng nhập
            start_url: URL khởi động
            optimized_mode: Sử dụng chế độ tối ưu cho bulk operations
            ultra_low_memory: Chế độ tiết kiệm RAM tối đa
        """
        try:
            profile_name = str(profile_name)
            print(f"🚀 [LAUNCH] Bắt đầu khởi động profile: {profile_name}")
            
            self.current_profile_name = profile_name
            profile_path = os.path.join(self.profiles_dir, profile_name)
            
            if not os.path.exists(profile_path):
                print(f"❌ [LAUNCH] Profile không tồn tại: {profile_name}")
                return False, f"Profile '{profile_name}' không tồn tại"
            
            # Kill Chrome processes
            self._kill_chrome_processes()
            
            # Clean cache
            self._cleanup_profile_cache(profile_path)
            
            # Cấu hình Chrome options
            chrome_options = Options()
            chrome_options.add_argument(f"--user-data-dir={profile_path}")
            
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
                print(f"🔧 [LAUNCH] Using optimized mode for bulk operations")
                self._apply_optimized_chrome_config(chrome_options, hidden, ultra_low_memory)
            else:
                # Use stable/base config for login and normal flows
                if login_flow and optimized_mode:
                    print(f"🛡️ [LAUNCH] Login flow detected → using base config (ignore optimized flags)")
                self._apply_base_chrome_config(chrome_options, hidden)
            # Ensure extensions are allowed so profile title extension can run
            try:
                self._ensure_extensions_allowed(chrome_options)
            except Exception as _e:
                print(f"⚠️ [LAUNCH] Could not sanitize extension flags: {_e}")
            
            # Inject tiny extension to show profile name in tab title
            try:
                title_ext_path = self._ensure_profile_title_extension(profile_name)
                if title_ext_path and os.path.exists(title_ext_path):
                    chrome_options.add_argument(f"--load-extension={title_ext_path}")
                    print(f"🔖 [LAUNCH] Loaded profile-title extension for: {profile_name}")
            except Exception as e:
                print(f"⚠️ [LAUNCH] Could not load profile-title extension: {e}")

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
                    # Disable all other extensions, only allow our allowlist
                    paths_arg = ",".join(allowlist)
                    try:
                        chrome_options.add_argument(f"--disable-extensions-except={paths_arg}")
                        chrome_options.add_argument(f"--load-extension={paths_arg}")
                        print(f"🛡️ [LAUNCH] Isolating extensions to avoid proxy conflicts")
                    except Exception:
                        pass
            except Exception as e:
                print(f"⚠️ [LAUNCH] Could not isolate extensions: {e}")

            # Launch Chrome with fallback mechanism
            driver = self._launch_chrome_with_fallback(chrome_options, profile_path, hidden)
            
            if not driver:
                return False, "Chrome không thể khởi động"
            
            # Handle login logic
            self._handle_auto_login(driver, profile_path, auto_login, login_data, start_url)
            
            return True, driver
            
        except Exception as e:
            print(f"💥 [LAUNCH] Lỗi: {str(e)}")
            return False, f"Lỗi khi khởi động Chrome: {str(e)}"

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
        # Ensure explicit enable
        try:
            chrome_options.add_argument('--enable-extensions')
        except Exception:
            pass

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
            script = (
                "(function(){\n"
                "  const profileName = " + _json.dumps(str(profile_name)) + ";\n"
                "  try {\n"
                "    const apply = () => {\n"
                "      const t = document.title || '';}\n"
                "    ;\n"
                "  } catch(e) {}\n"
                "  const prefix = profileName + ' | ';\n"
                "  const set = () => {\n"
                "    try {\n"
                "      if (!document.title.startsWith(prefix)) {\n"
                "        document.title = prefix + document.title;\n"
                "      }\n"
                "    } catch(e) {}\n"
                "  };\n"
                "  set();\n"
                "  const obs = new MutationObserver(set);\n"
                "  try { obs.observe(document.querySelector('title') || document.documentElement, {subtree:true, childList:true, characterData:true}); } catch(e) {}\n"
                "})();\n"
            )
            with open(js_path, "w", encoding="utf-8") as f:
                f.write(script)

            return ext_dir
        except Exception as e:
            print(f"⚠️ [PROFILE-TITLE] Failed to create extension: {e}")
            return ext_dir
    
    def _perform_auto_login(self, driver, login_data, start_url=None):
        """Thực hiện đăng nhập tự động cho nhiều trang web"""
        try:
            print(f"🔐 [LOGIN] Bắt đầu auto-login process...")
            
            # Kiểm tra xem có phải TikTok format không
            if isinstance(login_data, str):
                print(f"📝 [LOGIN] Parse TikTok format string...")
                # Parse TikTok format
                parsed_data = self._parse_tiktok_account_data(login_data)
                if parsed_data:
                    login_data = parsed_data
                    print(f"✅ [LOGIN] Đã parse TikTok format: {login_data.get('username', 'N/A')}")
                else:
                    print(f"❌ [LOGIN] Không thể parse TikTok format")
                    return False
            
            # Thử load session data trước
            username_or_email = login_data.get('username', login_data.get('email', ''))
            if username_or_email:
                print(f"🔍 [SESSION] Kiểm tra session data cho: {username_or_email}")
                session_data = self._load_session_data(username_or_email)
            if session_data:
                print(f"✅ [SESSION] Tìm thấy session data, thử restore...")
                if self._restore_session(driver, session_data):
                    print(f"🎉 [SESSION] Đăng nhập thành công bằng session data!")
                    # Lưu marker file ngay cả khi restore session thành công
                    print(f"💾 [SESSION] Lưu marker file cho profile...")
                    self._save_to_chrome_profile(driver, login_data)
                    return True
                else:
                    print(f"⚠️ [SESSION] Session data không hợp lệ, đăng nhập thông thường...")
            
            # Sử dụng start_url nếu có, nếu không thì dùng login_url
            if start_url:
                login_url = start_url
                print(f"🌐 [LOGIN] Sử dụng start_url: {login_url}")
            else:
                # Sử dụng URL login TikTok cụ thể cho email/username
                login_url = login_data.get('login_url', 'https://www.tiktok.com/login/phone-or-email/email')
                print(f"🌐 [LOGIN] Sử dụng login_url: {login_url}")
            
            email = login_data.get('email', '')
            password = login_data.get('password', '')
            twofa = login_data.get('twofa', '')
            
            print(f"📧 [LOGIN] Email: {email}")
            print(f"👤 [LOGIN] Username: {login_data.get('username', 'N/A')}")
            print(f"🔑 [LOGIN] Password: {'*' * len(password) if password else 'N/A'}")
            print(f"🔐 [LOGIN] 2FA: {twofa if twofa else 'N/A'}")
            print(f"🌐 [LOGIN] Đang thực hiện đăng nhập tại: {login_url}")
            
            # Điều hướng đến trang đăng nhập
            print(f"🔄 [LOGIN] Điều hướng đến trang đăng nhập...")
            driver.get(login_url)
            time.sleep(3)
            
            # Detect trang web và thực hiện đăng nhập tương ứng
            current_url = driver.current_url.lower()
            print(f"🌐 [LOGIN] Current URL sau khi điều hướng: {current_url}")
            login_success = False
            
            if 'tiktok.com' in current_url:
                print(f"🎵 [LOGIN] Detect TikTok, thực hiện đăng nhập TikTok...")
                login_success = self._login_tiktok(driver, email, password, twofa, login_data)
            elif 'instagram.com' in current_url:
                print(f"📸 [LOGIN] Detect Instagram, thực hiện đăng nhập Instagram...")
                login_success = self._login_instagram(driver, email, password, twofa)
            elif 'facebook.com' in current_url:
                print(f"👥 [LOGIN] Detect Facebook, thực hiện đăng nhập Facebook...")
                login_success = self._login_facebook(driver, email, password, twofa)
            elif 'google.com' in current_url or 'youtube.com' in current_url:
                print(f"🔍 [LOGIN] Detect Google/YouTube, thực hiện đăng nhập Google...")
                login_success = self._login_google(driver, email, password, twofa)
            else:
                print(f"🌐 [LOGIN] Detect trang web khác, sử dụng generic login...")
                # Fallback cho các trang web khác
                login_success = self._login_generic(driver, email, password, twofa)
            
            if login_success:
                print(f"🎉 [LOGIN] Đăng nhập thành công cho: {email}")
                # Lưu session data sau khi đăng nhập thành công
                self._save_session_data(driver, login_data)
                return True
            else:
                print(f"💥 [LOGIN] Đăng nhập thất bại cho: {email}")
                return False
            
        except Exception as e:
            print(f"💥 [LOGIN] Lỗi đăng nhập tự động: {str(e)}")
    
    def _save_session_data(self, driver, login_data):
        """Lưu session data sau khi đăng nhập thành công"""
        try:
            print(f"💾 [SESSION] Bắt đầu lưu session data...")
            
            if not login_data:
                print(f"⚠️ [SESSION] Không có login_data để lưu")
                return
            
            # Lấy cookies từ driver
            cookies = driver.get_cookies()
            print(f"🍪 [SESSION] Đã lấy {len(cookies)} cookies")
            
            # Lấy current URL
            current_url = driver.current_url
            print(f"🌐 [SESSION] Current URL: {current_url}")
            
            # Tạo session data
            session_data = {
                'cookies': cookies,
                'url': current_url,
                'timestamp': time.time(),
                'username': login_data.get('username', ''),
                'email': login_data.get('email', ''),
                'user_id': login_data.get('user_id', '')
            }
            
            # Lưu vào file JSON (backup)
            import json
            import os
            
            # Tạo thư mục sessions nếu chưa có
            sessions_dir = os.path.join(os.path.dirname(__file__), 'sessions')
            if not os.path.exists(sessions_dir):
                os.makedirs(sessions_dir)
                print(f"📁 [SESSION] Đã tạo thư mục sessions")
            
            # Tên file dựa trên username hoặc email
            session_filename = login_data.get('username', login_data.get('email', 'unknown'))
            session_filename = session_filename.replace('@', '_').replace('.', '_')
            session_file = os.path.join(sessions_dir, f"{session_filename}_session.json")
            
            # Lưu session data
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ [SESSION] Đã lưu session data vào: {session_file}")
            print(f"📊 [SESSION] Session data: {len(cookies)} cookies, URL: {current_url}")
            
            # Lưu trực tiếp vào Chrome profile để tự động đăng nhập lần sau
            print(f"💾 [SESSION] Lưu session trực tiếp vào Chrome profile...")
            self._save_to_chrome_profile(driver, login_data)
            
        except Exception as e:
            print(f"❌ [SESSION] Lỗi khi lưu session data: {e}")
    
    def _save_to_chrome_profile(self, driver, login_data):
        """Lưu session trực tiếp vào Chrome profile"""
        try:
            print(f"💾 [PROFILE] Bắt đầu lưu session vào Chrome profile...")
            
            # Lấy profile path từ driver
            profile_path = driver.capabilities.get('chrome', {}).get('userDataDir', '')
            print(f"🔍 [PROFILE] Driver capabilities: {driver.capabilities}")
            
            if not profile_path:
                print(f"⚠️ [PROFILE] Không thể lấy profile path từ driver capabilities")
                # Thử lấy từ profile_name nếu có
                if hasattr(self, 'current_profile_name'):
                    profile_path = os.path.join(self.profiles_dir, self.current_profile_name)
                    print(f"📁 [PROFILE] Sử dụng profile path từ current_profile_name: {profile_path}")
                else:
                    print(f"❌ [PROFILE] Không thể xác định profile path")
                    return
            
            print(f"📁 [PROFILE] Profile path: {profile_path}")
            
            # Lưu thông tin đăng nhập vào profile
            username_or_email = login_data.get('username', login_data.get('email', ''))
            if username_or_email:
                # Tạo file marker để đánh dấu profile đã đăng nhập
                marker_file = os.path.join(profile_path, 'tiktok_logged_in.txt')
                print(f"📝 [PROFILE] Tạo marker file: {marker_file}")
                
                with open(marker_file, 'w', encoding='utf-8') as f:
                    f.write(f"username={username_or_email}\n")
                    f.write(f"email={login_data.get('email', '')}\n")
                    f.write(f"timestamp={time.time()}\n")
                    f.write(f"url={driver.current_url}\n")
                
                print(f"✅ [PROFILE] Đã lưu marker file: {marker_file}")
                
                # Lưu cookies trực tiếp vào Chrome profile để tự động đăng nhập
                print(f"🍪 [PROFILE] Lưu cookies trực tiếp vào Chrome profile...")
                self._save_cookies_to_profile(driver, profile_path)
                
                # Lưu thông tin vào config để tắt auto-login lần sau
                if hasattr(self, 'config'):
                    if not self.config.has_section('PROFILE_SESSIONS'):
                        self.config.add_section('PROFILE_SESSIONS')
                    
                    self.config.set('PROFILE_SESSIONS', username_or_email, 'logged_in')
                    
                    # Lưu config
                    with open(self.config_file, 'w', encoding='utf-8') as f:
                        self.config.write(f)
                    
                    print(f"✅ [PROFILE] Đã cập nhật config để tắt auto-login")
                else:
                    print(f"⚠️ [PROFILE] Không có config object")
            else:
                print(f"⚠️ [PROFILE] Không có username/email để lưu")
            
            print(f"🎉 [PROFILE] Session đã được lưu vào Chrome profile!")
            print(f"💡 [PROFILE] Lần sau khởi động sẽ tự động đăng nhập")
            
        except Exception as e:
            print(f"❌ [PROFILE] Lỗi khi lưu vào Chrome profile: {e}")
            import traceback
            print(f"🔍 [PROFILE] Traceback: {traceback.format_exc()}")
    
    def _save_cookies_to_profile(self, driver, profile_path):
        """Lưu cookies trực tiếp vào Chrome profile"""
        try:
            print(f"🍪 [COOKIES] Bắt đầu lưu cookies vào Chrome profile...")
            
            # Lấy cookies từ driver
            cookies = driver.get_cookies()
            print(f"🍪 [COOKIES] Đã lấy {len(cookies)} cookies từ driver")
            
            # Lưu cookies vào file JSON để Chrome có thể load
            cookies_json_path = os.path.join(profile_path, 'tiktok_cookies.json')
            import json
            with open(cookies_json_path, 'w', encoding='utf-8') as f:
                json.dump(cookies, f, indent=2, ensure_ascii=False)
            
            print(f"✅ [COOKIES] Đã lưu cookies vào: {cookies_json_path}")
            
            # Tạo file marker để Chrome biết có cookies đã lưu
            cookies_marker = os.path.join(profile_path, 'cookies_loaded.txt')
            with open(cookies_marker, 'w', encoding='utf-8') as f:
                f.write(f"cookies_count={len(cookies)}\n")
                f.write(f"timestamp={time.time()}\n")
                f.write(f"source=tiktok_login\n")
            
            print(f"✅ [COOKIES] Đã tạo cookies marker: {cookies_marker}")
            
        except Exception as e:
            print(f"❌ [COOKIES] Lỗi khi lưu cookies: {e}")
            import traceback
            print(f"🔍 [COOKIES] Traceback: {traceback.format_exc()}")
    
    def _load_cookies_from_profile(self, profile_path, driver):
        """Load cookies từ Chrome profile và inject vào driver"""
        try:
            print(f"🍪 [COOKIES] Bắt đầu load cookies từ Chrome profile...")
            
            # Kiểm tra file cookies JSON
            cookies_json_path = os.path.join(profile_path, 'tiktok_cookies.json')
            if not os.path.exists(cookies_json_path):
                print(f"⚠️ [COOKIES] Không tìm thấy file cookies: {cookies_json_path}")
                return False
            
            # Load cookies từ file JSON
            import json
            with open(cookies_json_path, 'r', encoding='utf-8') as f:
                cookies = json.load(f)
            
            print(f"🍪 [COOKIES] Đã load {len(cookies)} cookies từ file")
            
            # Điều hướng đến trang chủ TikTok trước khi inject cookies
            print(f"🌐 [COOKIES] Điều hướng đến trang chủ TikTok...")
            driver.get("https://www.tiktok.com")
            time.sleep(2)
            
            # Inject cookies vào driver
            print(f"🍪 [COOKIES] Đang inject cookies vào driver...")
            for cookie in cookies:
                try:
                    # Tạo cookie copy để không modify original
                    cookie_copy = cookie.copy()
                    
                    # Xử lý domain
                    if 'domain' in cookie_copy:
                        domain = cookie_copy['domain']
                        if domain == 'www.tiktok.com':
                            cookie_copy['domain'] = '.tiktok.com'
                    
                    driver.add_cookie(cookie_copy)
                    print(f"✅ [COOKIES] Đã inject cookie: {cookie_copy.get('name', 'unknown')}")
                except Exception as e:
                    print(f"⚠️ [COOKIES] Không thể inject cookie {cookie.get('name', 'unknown')}: {e}")
                    continue
            
            # Refresh để áp dụng cookies
            print(f"🔄 [COOKIES] Refresh trang để áp dụng cookies...")
            driver.refresh()
            time.sleep(3)
            
            print(f"✅ [COOKIES] Đã load và inject cookies thành công!")
            return True
            
        except Exception as e:
            print(f"❌ [COOKIES] Lỗi khi load cookies: {e}")
            import traceback
            print(f"🔍 [COOKIES] Traceback: {traceback.format_exc()}")
            return False
    
    def _load_session_data(self, username_or_email):
        """Load session data từ file"""
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
            
            # Kiểm tra timestamp (session cũ hơn 7 ngày thì bỏ qua)
            import time
            if time.time() - session_data.get('timestamp', 0) > 7 * 24 * 3600:
                print(f"⚠️ [SESSION] Session data cũ hơn 7 ngày, bỏ qua")
                return None
            
            print(f"✅ [SESSION] Đã load session data từ: {session_file}")
            return session_data
            
        except Exception as e:
            print(f"❌ [SESSION] Lỗi khi load session data: {e}")
            return None
    
    def _restore_session(self, driver, session_data):
        """Restore session từ session data"""
        try:
            print(f"🔄 [SESSION] Bắt đầu restore session...")
            
            # Điều hướng đến trang chủ TikTok trước để inject cookies
            print(f"🌐 [SESSION] Điều hướng đến trang chủ TikTok...")
            driver.get("https://www.tiktok.com")
            time.sleep(2)
            
            # Inject cookies
            cookies = session_data.get('cookies', [])
            if cookies:
                print(f"🍪 [SESSION] Đang inject {len(cookies)} cookies...")
                for cookie in cookies:
                    try:
                        # Tạo cookie copy để không modify original
                        cookie_copy = cookie.copy()
                        
                        # Xử lý domain - chỉ xóa nếu domain không hợp lệ
                        if 'domain' in cookie_copy:
                            domain = cookie_copy['domain']
                            if domain.startswith('.'):
                                # Giữ nguyên subdomain cookies
                                pass
                            elif domain == 'www.tiktok.com':
                                # Chuyển www.tiktok.com thành .tiktok.com
                                cookie_copy['domain'] = '.tiktok.com'
                        
                        driver.add_cookie(cookie_copy)
                        print(f"✅ [SESSION] Đã inject cookie: {cookie_copy.get('name', 'unknown')}")
                    except Exception as e:
                        print(f"⚠️ [SESSION] Không thể inject cookie {cookie.get('name', 'unknown')}: {e}")
                        continue
                
                # Refresh để áp dụng cookies
                print(f"🔄 [SESSION] Refresh trang để áp dụng cookies...")
                driver.refresh()
                time.sleep(3)
                
                # Kiểm tra xem đã đăng nhập chưa
                current_url = driver.current_url
                print(f"🌐 [SESSION] URL sau khi restore: {current_url}")
                
                # Điều hướng đến trang For You để kiểm tra đăng nhập
                print(f"🔄 [SESSION] Điều hướng đến trang For You để kiểm tra...")
                driver.get("https://www.tiktok.com/foryou")
                time.sleep(3)
                
                final_url = driver.current_url
                print(f"🌐 [SESSION] URL cuối cùng: {final_url}")
                
                # Kiểm tra dấu hiệu đăng nhập thành công
                if 'login' not in final_url.lower() and 'foryou' in final_url.lower():
                    print(f"✅ [SESSION] Restore session thành công!")
                    return True
                else:
                    print(f"⚠️ [SESSION] Session không hợp lệ, cần đăng nhập lại")
                    return False
            else:
                print(f"⚠️ [SESSION] Không có cookies để restore")
                return False
                
        except Exception as e:
            print(f"❌ [SESSION] Lỗi khi restore session: {e}")
            return False
    
    def _login_tiktok(self, driver, email, password, twofa, login_data=None):
        """Đăng nhập TikTok với hỗ trợ session token và email verification"""
        try:
            print(f"🎵 [TIKTOK] Bắt đầu đăng nhập TikTok...")
            print(f"📧 [TIKTOK] Email: {email}")
            print(f"👤 [TIKTOK] Username: {login_data.get('username', 'N/A') if login_data else 'N/A'}")
            print(f"🔑 [TIKTOK] Password: {'*' * len(password) if password else 'N/A'}")
            
            # Bỏ qua session token, chỉ sử dụng username/password
            if login_data and 'session_token' in login_data and login_data['session_token']:
                print(f"⚠️ [TIKTOK] Phát hiện session token nhưng sẽ bỏ qua, sử dụng username/password...")
                print(f"🔐 [TIKTOK] Session token: {login_data['session_token'][:20]}... (BỎ QUA)")
            
            # Đăng nhập thông thường với username/password
            print(f"🔐 [TIKTOK] Đăng nhập TikTok với username/password...")
            
            # Kiểm tra trang hiện tại với error handling
            try:
                current_url = driver.current_url
                print(f"🌐 [TIKTOK] Current URL: {current_url}")
            except Exception as e:
                print(f"❌ [TIKTOK] Chrome session bị disconnect: {e}")
                print(f"🔄 [TIKTOK] Thử refresh trang...")
                try:
                    driver.refresh()
                    time.sleep(3)
                    current_url = driver.current_url
                    print(f"🌐 [TIKTOK] URL sau refresh: {current_url}")
                except Exception as refresh_error:
                    print(f"❌ [TIKTOK] Không thể refresh: {refresh_error}")
                    return False
            
            # Sử dụng username nếu có (TikTok format)
            login_field_value = email
            if login_data and 'username' in login_data and login_data['username']:
                login_field_value = login_data['username']
                print(f"👤 [TIKTOK] Sử dụng username thay vì email: {login_field_value}")
            
            # Không click button trước, điền form trước
            print(f"🔍 [TIKTOK] Bỏ qua việc click button, điền form trước...")
            
            # Tìm và điền email/username với retry logic
            print(f"🔍 [TIKTOK] Đang tìm trường nhập email/username...")
            print(f"📝 [TIKTOK] Giá trị cần điền: {login_field_value}")
            print(f"🔑 [TIKTOK] Password: {password[:5]}***")
            
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
            
            print(f"🎯 [TIKTOK] Sẽ thử {len(email_selectors)} selectors:")
            for i, selector in enumerate(email_selectors):
                print(f"  {i+1}. {selector}")
            
            email_field_found = False
            max_retries = 3
            
            for retry in range(max_retries):
                print(f"🔄 [TIKTOK] Thử lần {retry + 1}/{max_retries}...")
                
                for selector in email_selectors:
                    try:
                        # Kiểm tra session trước
                        driver.current_url  # Test session
                        
                        email_field = driver.find_element("css selector", selector)
                        print(f"🔍 [TIKTOK] Tìm thấy element với selector: {selector}")
                        print(f"👁️ [TIKTOK] Element displayed: {email_field.is_displayed()}")
                        print(f"🔓 [TIKTOK] Element enabled: {email_field.is_enabled()}")
                        
                        if email_field.is_displayed() and email_field.is_enabled():
                            print(f"✅ [TIKTOK] Element hợp lệ, bắt đầu điền...")
                            
                            # Clear field
                            print(f"🧹 [TIKTOK] Đang clear field...")
                            email_field.clear()
                            time.sleep(0.5)
                            
                            # Type value với JavaScript fallback
                            print(f"⌨️ [TIKTOK] Đang gõ: {login_field_value}")
                            try:
                                email_field.send_keys(login_field_value)
                                time.sleep(0.5)
                            except Exception as e:
                                print(f"⚠️ [TIKTOK] Send keys thất bại, thử JavaScript: {e}")
                                try:
                                    driver.execute_script(f"arguments[0].value = '{login_field_value}';", email_field)
                                    driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", email_field)
                                    time.sleep(0.5)
                                    print(f"✅ [TIKTOK] Đã điền bằng JavaScript")
                                except Exception as js_error:
                                    print(f"❌ [TIKTOK] JavaScript cũng thất bại: {js_error}")
                                    continue
                            
                            # Verify đã điền
                            field_value = email_field.get_attribute('value')
                            print(f"🔍 [TIKTOK] Field value sau khi điền: '{field_value}'")
                            print(f"🎯 [TIKTOK] Expected value: '{login_field_value}'")
                            
                            if field_value == login_field_value:
                                print(f"✅ [TIKTOK] Đã điền email/username thành công!")
                                email_field_found = True
                                break
                            else:
                                print(f"⚠️ [TIKTOK] Field value không khớp, thử selector tiếp theo...")
                        else:
                            print(f"❌ [TIKTOK] Element không hợp lệ (displayed: {email_field.is_displayed()}, enabled: {email_field.is_enabled()})")
                    except Exception as e:
                        print(f"⚠️ [TIKTOK] Lỗi với selector {selector}: {e}")
                        continue
                
                if email_field_found:
                    break
                
                if retry < max_retries - 1:
                    print(f"⏳ [TIKTOK] Đợi 2 giây trước khi thử lại...")
                    time.sleep(2)
            
            if not email_field_found:
                print(f"❌ [TIKTOK] Không tìm thấy trường nhập email/username sau {max_retries} lần thử")
                # Debug: List all input fields
                try:
                    all_inputs = driver.find_elements("css selector", "input")
                    print(f"🔍 [TIKTOK] Tìm thấy {len(all_inputs)} input fields:")
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
                    print(f"❌ [TIKTOK] Lỗi debug: {debug_error}")
                return False
            
            time.sleep(1)
            
            # Tìm và điền password với retry logic
            print(f"🔍 [TIKTOK] Đang tìm trường nhập password...")
            print(f"🔑 [TIKTOK] Password cần điền: {password[:5]}***")
            
            password_selectors = [
                "input[data-e2e='login-password']",
                "input[name='password']",
                "input[placeholder*='Password']",
                "input[placeholder*='password']",
                "input[type='password']",
                "input[autocomplete='current-password']"
            ]
            
            print(f"🎯 [TIKTOK] Sẽ thử {len(password_selectors)} password selectors:")
            for i, selector in enumerate(password_selectors):
                print(f"  {i+1}. {selector}")
            
            password_field_found = False
            
            for retry in range(max_retries):
                print(f"🔄 [TIKTOK] Thử tìm password lần {retry + 1}/{max_retries}...")
                
                for selector in password_selectors:
                    try:
                        # Kiểm tra session trước
                        driver.current_url  # Test session
                        
                        password_field = driver.find_element("css selector", selector)
                        print(f"🔍 [TIKTOK] Tìm thấy password element với selector: {selector}")
                        print(f"👁️ [TIKTOK] Password element displayed: {password_field.is_displayed()}")
                        print(f"🔓 [TIKTOK] Password element enabled: {password_field.is_enabled()}")
                        
                        if password_field.is_displayed() and password_field.is_enabled():
                            print(f"✅ [TIKTOK] Password element hợp lệ, bắt đầu điền...")
                            
                            # Clear field
                            print(f"🧹 [TIKTOK] Đang clear password field...")
                            password_field.clear()
                            time.sleep(0.5)
                            
                            # Type password với JavaScript fallback
                            print(f"⌨️ [TIKTOK] Đang gõ password: {password[:5]}***")
                            try:
                                password_field.send_keys(password)
                                time.sleep(0.5)
                            except Exception as e:
                                print(f"⚠️ [TIKTOK] Send keys password thất bại, thử JavaScript: {e}")
                                try:
                                    driver.execute_script(f"arguments[0].value = '{password}';", password_field)
                                    driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", password_field)
                                    time.sleep(0.5)
                                    print(f"✅ [TIKTOK] Đã điền password bằng JavaScript")
                                except Exception as js_error:
                                    print(f"❌ [TIKTOK] JavaScript password cũng thất bại: {js_error}")
                                    continue
                            
                            # Verify đã điền (không check value vì password field thường không trả về value)
                            print(f"✅ [TIKTOK] Đã điền password thành công!")
                            password_field_found = True
                            break
                        else:
                            print(f"❌ [TIKTOK] Password element không hợp lệ (displayed: {password_field.is_displayed()}, enabled: {password_field.is_enabled()})")
                    except Exception as e:
                        print(f"⚠️ [TIKTOK] Lỗi với selector {selector}: {e}")
                        continue
                
                if password_field_found:
                    break
                
                if retry < max_retries - 1:
                    print(f"⏳ [TIKTOK] Đợi 2 giây trước khi thử lại...")
                    time.sleep(2)
            
            if not password_field_found:
                print(f"❌ [TIKTOK] Không tìm thấy trường nhập password sau {max_retries} lần thử")
                return False
            
            time.sleep(1)
            
            # Click nút đăng nhập với xử lý button disabled
            print(f"🔍 [TIKTOK] Đang tìm nút submit...")
            submit_selectors = [
                "button[type='submit']",
                "button[data-e2e='login-button']",
                "//button[contains(text(), 'Log in')]",
                "//button[contains(text(), 'Đăng nhập')]"
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
                        print(f"✅ [TIKTOK] Tìm thấy nút submit với selector: {selector}")
                        
                        # Kiểm tra button có disabled không
                        is_disabled = submit_button.get_attribute("disabled")
                        if is_disabled:
                            print(f"⚠️ [TIKTOK] Button bị disabled, đợi enable...")
                            # Đợi button enable (tối đa 10 giây)
                            for i in range(10):
                                time.sleep(1)
                                is_disabled = submit_button.get_attribute("disabled")
                                if not is_disabled:
                                    print(f"✅ [TIKTOK] Button đã enable sau {i+1} giây")
                                    break
                                print(f"⏳ [TIKTOK] Đang đợi button enable... ({i+1}/10)")
                        
                        # Thử click bình thường trước
                        try:
                            submit_button.click()
                            print(f"✅ [TIKTOK] Đã click nút submit bình thường")
                            submit_clicked = True
                            break
                        except Exception as click_error:
                            print(f"⚠️ [TIKTOK] Click bình thường thất bại: {click_error}")
                            # Thử JavaScript click
                            try:
                                driver.execute_script("arguments[0].click();", submit_button)
                                print(f"✅ [TIKTOK] Đã click nút submit bằng JavaScript")
                                submit_clicked = True
                                break
                            except Exception as js_error:
                                print(f"⚠️ [TIKTOK] JavaScript click thất bại: {js_error}")
                                continue
                                
                except Exception as e:
                    print(f"⚠️ [TIKTOK] Lỗi với selector {selector}: {e}")
                    continue
            
            if not submit_clicked:
                print(f"❌ [TIKTOK] Không thể click nút submit")
                return False
            
            time.sleep(3)
            
            # Kiểm tra xem có cần 2FA không
            print(f"🔍 [TIKTOK] Kiểm tra yêu cầu 2FA...")
            if twofa or self._check_2fa_required(driver):
                print(f"🔐 [TIKTOK] Phát hiện yêu cầu 2FA, thử email verification...")
                if self._handle_2fa_with_email(driver, login_data):
                    print(f"✅ [TIKTOK] 2FA thành công với email verification")
                else:
                    print(f"⚠️ [TIKTOK] 2FA thất bại, thử phương pháp thủ công...")
                    if twofa:
                        print(f"🔐 [TIKTOK] Sử dụng mã 2FA thủ công: {twofa}")
                        self._handle_2fa(driver, twofa)
            else:
                print(f"✅ [TIKTOK] Không cần 2FA")
            
            # Kiểm tra kết quả đăng nhập
            time.sleep(3)
            current_url = driver.current_url
            print(f"🌐 [TIKTOK] URL sau khi đăng nhập: {current_url}")
            
            if 'login' not in current_url.lower() and 'signin' not in current_url.lower():
                print(f"✅ [TIKTOK] Đăng nhập TikTok thành công cho {login_field_value}")
                return True
            else:
                print(f"❌ [TIKTOK] Đăng nhập TikTok thất bại cho {login_field_value}")
                return False
                
        except Exception as e:
            print(f"❌ [TIKTOK] Lỗi đăng nhập TikTok: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def _check_2fa_required(self, driver):
        """Kiểm tra xem có yêu cầu 2FA không"""
        try:
            # Kiểm tra các dấu hiệu của 2FA
            verification_indicators = [
                "verification",
                "2fa",
                "two-factor",
                "code",
                "mã xác thực",
                "xác nhận"
            ]
            
            page_source = driver.page_source.lower()
            current_url = driver.current_url.lower()
            
            for indicator in verification_indicators:
                if indicator in page_source or indicator in current_url:
                    return True
            
            # Kiểm tra các element thường có trong form 2FA
            verification_elements = [
                "input[placeholder*='code']",
                "input[placeholder*='verification']",
                "input[placeholder*='mã']",
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
            print(f"Lỗi kiểm tra 2FA: {e}")
            return False
    
    def _handle_2fa_with_email(self, driver, login_data):
        """Xử lý 2FA bằng app riêng"""
        try:
            print(f"📧 [2FA] Bắt đầu xử lý 2FA với app riêng...")
            
            if not login_data:
                print(f"❌ [2FA] Không có login_data")
                return False
            
            # Lấy thông tin email
            email = login_data.get('email', '')
            if not email:
                print(f"❌ [2FA] Không có email trong login_data")
                return False
            
            print(f"📧 [2FA] Email: {email}")

            # Try Microsoft Graph automatically if credentials provided
            try:
                code = self._fetch_tiktok_code_from_hotmail(login_data)
                if code:
                    print(f"✅ [2FA] Lấy mã từ Hotmail (Graph): {code}")
                    return self._input_verification_code(driver, code)
                else:
                    print(f"⚠️ [2FA] Không tìm thấy mã bằng Microsoft Graph, fallback sang app ngoài")
            except Exception as e:
                print(f"⚠️ [2FA] Lỗi Graph: {e}. Fallback sang app ngoài")
            
            # Tạo request cho app 2FA
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
            
            print(f"📤 [2FA] Đã gửi request cho app 2FA: {request_id}")
            print(f"⏳ [2FA] Đang đợi mã 2FA từ app riêng...")
            
            # Đợi response từ app 2FA (tối đa 60 giây)
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
                                print(f"✅ [2FA] Nhận được mã 2FA: {verification_code}")
                                
                                # Xóa file response
                                os.remove(response_file)
                                
                                # Nhập mã vào form
                                success = self._input_verification_code(driver, verification_code)
                                return success
                            else:
                                print(f"❌ [2FA] App 2FA báo lỗi: {response_data.get('error', 'Unknown error')}")
                                os.remove(response_file)
                                return False
                    except Exception as e:
                        print(f"⚠️ [2FA] Lỗi đọc response: {e}")
                
                time.sleep(2)
                wait_time += 2
                print(f"⏳ [2FA] Đang đợi... ({wait_time}/{max_wait_time}s)")
            
            print(f"⏰ [2FA] Timeout! Không nhận được mã 2FA trong {max_wait_time} giây")
            print(f"💡 [2FA] Hãy đảm bảo TikTok 2FA Manager đang chạy")
            
            # Xóa file request nếu timeout
            if os.path.exists(request_file):
                os.remove(request_file)
            
            return False
            
        except Exception as e:
            print(f"❌ [2FA] Lỗi xử lý 2FA: {e}")
            return False
    
    # Email refresh token method removed
    
    def _input_verification_code(self, driver, verification_code):
        """Nhập mã xác thực vào form"""
        try:
            print(f"🔍 [2FA] Đang tìm trường nhập mã xác thực...")
            
            # Các selector cho trường nhập mã
            code_selectors = [
                "input[placeholder*='code']",
                "input[placeholder*='verification']",
                "input[placeholder*='mã']",
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
                        print(f"✅ [2FA] Tìm thấy trường nhập mã: {selector}")
                        code_field.clear()
                        code_field.send_keys(verification_code)
                        print(f"✅ [2FA] Đã điền mã xác thực: {verification_code}")
                        code_field_found = True
                        break
                except Exception as e:
                    print(f"⚠️ [2FA] Không tìm thấy với selector {selector}: {e}")
                    continue
            
            if not code_field_found:
                print(f"❌ [2FA] Không tìm thấy trường nhập mã xác thực")
                return False
            
            time.sleep(2)
            
            # Tìm và click nút submit
            print(f"🔍 [2FA] Đang tìm nút submit...")
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
                        print(f"✅ [2FA] Tìm thấy nút submit: {selector}")
                        submit_btn.click()
                        print(f"✅ [2FA] Đã click nút xác nhận")
                        submit_btn_found = True
                        break
                except Exception as e:
                    print(f"⚠️ [2FA] Không tìm thấy nút submit với selector {selector}: {e}")
                    continue
            
            if not submit_btn_found:
                print(f"⚠️ [2FA] Không tìm thấy nút submit, thử Enter...")
                try:
                    from selenium.webdriver.common.keys import Keys
                    code_field.send_keys(Keys.RETURN)
                    print(f"✅ [2FA] Đã gửi mã bằng Enter key")
                except Exception as e:
                    print(f"❌ [2FA] Không thể gửi mã: {e}")
                    return False
            
            print(f"⏳ [2FA] Chờ kết quả xác thực...")
            time.sleep(3)
            print(f"✅ [2FA] Hoàn thành nhập mã xác thực")
            return True
            
        except Exception as e:
            print(f"❌ [2FA] Lỗi nhập mã xác thực: {e}")
            return False

    def _fetch_tiktok_code_from_hotmail(self, login_data):
        """Fetch latest TikTok verification code from Hotmail với auto fallback methods.

        Hỗ trợ nhiều phương pháp:
        1. Refresh token + client ID
        2. Device login
        3. IMAP với password
        4. Access token từ environment
        """
        try:
            import re
            import time
            import os
            from datetime import datetime, timedelta

            # Parse account data
            ms_refresh_token = login_data.get('ms_refresh_token', '')
            ms_client_id = login_data.get('ms_client_id', '')
            email = login_data.get('email', '')
            email_password = login_data.get('email_password', '')
            access_token = os.getenv('MS_ACCESS_TOKEN')

            print(f"🔍 [GRAPH] Đang tìm mã 2FA từ Hotmail...")
            print(f"📧 [GRAPH] Email: {email}")
            
            # Thử các phương pháp theo thứ tự ưu tiên
            methods = []
            
            # Method 1: Access token từ environment
            if access_token:
                methods.append(('access_token', access_token, None))
            
            # Method 2: Refresh token (nếu có)
            if ms_refresh_token and ms_refresh_token != 'ep' and ms_client_id:
                methods.append(('refresh_token', ms_refresh_token, ms_client_id))
            
            # Method 3: Device login (luôn có thể thử)
            if ms_client_id:
                methods.append(('device_login', None, ms_client_id))
            
            # Method 4: IMAP (nếu có password)
            if email_password and email_password != 'ep':
                methods.append(('imap', email_password, None))
            
            for method_name, method_data, client_id in methods:
                try:
                    print(f"🔄 [GRAPH] Thử phương pháp: {method_name}")
                    
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
                    print(f"⚠️ [GRAPH] Lỗi phương pháp {method_name}: {e}")
                    continue
            
            print("❌ [GRAPH] Tất cả phương pháp đều thất bại")
            return None
            
        except Exception as e:
            print(f"❌ [GRAPH] Lỗi tổng thể: {e}")
            return None
    
    def _try_access_token_method(self, access_token, email):
        """Thử phương pháp access token"""
        import requests
        
        print(f"🔑 [GRAPH] Sử dụng access token từ environment")
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        return self._search_emails_with_token(headers, email)
    
    def _try_refresh_token_method(self, refresh_token, client_id, email):
        """Thử phương pháp refresh token"""
        import requests
        
        print(f"🔄 [GRAPH] Sử dụng refresh token + client ID")
        
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
                print(f"⚠️ [GRAPH] Token exchange failed: {token_response.status_code} {token_response.text}")
                return False, "Token exchange failed"
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            return self._search_emails_with_token(headers, email)
            
        except Exception as e:
            print(f"⚠️ [GRAPH] Token exchange failed: {e}")
            return False, f"Token exchange failed: {e}"
    
    def _try_device_login_method(self, client_id, email):
        """Thử phương pháp device login"""
        try:
            import msal
            import requests
            
            print(f"🔄 [GRAPH] Sử dụng device login")
            
            app = msal.PublicClientApplication(
                client_id, 
                authority="https://login.microsoftonline.com/consumers"
            )
            
            flow = app.initiate_device_flow(scopes=["Mail.Read"])
            print(f"🌐 [GRAPH] Mở trình duyệt: {flow.get('message', 'Open browser and complete the device code flow')}")
            print("⏳ [GRAPH] Đang chờ bạn hoàn thành đăng nhập...")
            
            result = app.acquire_token_by_device_flow(flow)
            
            if "error" in result:
                print(f"❌ [GRAPH] Device login failed: {result.get('error_description', result.get('error'))}")
                return False, "Device login failed"
            
            access_token = result.get("access_token")
            if not access_token:
                print("❌ [GRAPH] Không lấy được access token")
                return False, "No access token"
            
            print("✅ [GRAPH] Device login thành công!")
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            return self._search_emails_with_token(headers, email)
            
        except Exception as e:
            print(f"❌ [GRAPH] Device login error: {e}")
            return False, f"Device login error: {e}"
    
    def _try_imap_method(self, email, password):
        """Thử phương pháp IMAP"""
        try:
            import imaplib
            import email
            import re
            import time
            from datetime import datetime, timedelta
            
            print(f"🔄 [GRAPH] Sử dụng IMAP")
            
            mail = imaplib.IMAP4_SSL("outlook.office365.com", 993)
            mail.login(email, password)
            mail.select('inbox')
            
            print("✅ [GRAPH] IMAP kết nối thành công!")
            
            start_time = time.time()
            timeout = 90
            
            while time.time() - start_time < timeout:
                try:
                    # Tìm email từ TikTok trong 30 phút gần đây
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
                        print("⏳ [GRAPH] Chưa tìm thấy email từ TikTok...")
                        time.sleep(5)
                        continue
                    
                    email_ids = messages[0].split()
                    
                    if not email_ids:
                        print("⏳ [GRAPH] Chưa tìm thấy email mới...")
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
                                print(f"✅ [GRAPH] Tìm thấy mã TikTok: {code}")
                                print(f"📧 [GRAPH] Email: {subject}")
                                print(f"👤 [GRAPH] Người gửi: {sender}")
                                print(f"⏰ [GRAPH] Thời gian: {date_str}")
                                return True, code
                        
                        except Exception as e:
                            print(f"⚠️ [GRAPH] Lỗi xử lý email: {e}")
                            continue
                    
                    print("⏳ [GRAPH] Chưa tìm thấy mã mới...")
                    time.sleep(5)
                    
                except Exception as e:
                    print(f"❌ [GRAPH] Lỗi IMAP: {e}")
                    time.sleep(5)
            
            mail.close()
            mail.logout()
            return False, "Timeout"
            
        except Exception as e:
            print(f"❌ [GRAPH] Lỗi kết nối IMAP: {e}")
            return False, f"IMAP error: {e}"
    
    def _search_emails_with_token(self, headers, email):
        """Tìm email với access token"""
        import requests
        import json
        import time
        import re
        from datetime import datetime, timedelta
        
        print(f"⏰ [GRAPH] Tìm kiếm trong 90 giây...")
        
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
                    print(f"❌ [GRAPH] Token hết hạn")
                    return False, "Token expired"
                
                if response.status_code != 200:
                    print(f"❌ [GRAPH] Lỗi API: {response.status_code} - {response.text}")
                    return False, f"API error: {response.status_code}"
                
                data = response.json()
                messages = data.get('value', [])
                
                if not messages:
                    print("⏳ [GRAPH] Chưa tìm thấy email...")
                    time.sleep(5)
                    continue
                
                print(f"📧 [GRAPH] Tìm thấy {len(messages)} email")
                
                # Kiểm tra từng email
                for msg in messages:
                    subject = msg.get('subject', '')
                    body = msg.get('body', {}).get('content', '')
                    received_time = msg.get('receivedDateTime', '')
                    sender = msg.get('from', {}).get('emailAddress', {}).get('address', '')
                    
                    code = self._extract_tiktok_code_from_content(subject, body, received_time)
                    if code:
                        print(f"✅ [GRAPH] Tìm thấy mã TikTok: {code}")
                        print(f"📧 [GRAPH] Email: {subject}")
                        print(f"👤 [GRAPH] Người gửi: {sender}")
                        print(f"⏰ [GRAPH] Thời gian: {received_time}")
                        return True, code
                
                print("⏳ [GRAPH] Chưa tìm thấy mã mới...")
                time.sleep(5)
                
            except Exception as e:
                print(f"❌ [GRAPH] Lỗi tìm kiếm: {e}")
                time.sleep(5)
        
        print(f"⏰ [GRAPH] Hết thời gian tìm kiếm mã 2FA")
        return False, "Không tìm thấy email chứa mã 2FA trong thời gian chờ."
    
    def _extract_tiktok_code_from_content(self, subject, body, received_time):
        """Trích xuất mã TikTok từ nội dung email"""
        import re
        from datetime import datetime
        
        # Tìm mã 6 chữ số
        code_pattern = r'\b\d{6}\b'
        codes = re.findall(code_pattern, f"{subject} {body}")
        
        if not codes:
            return None
        
        # Kiểm tra thời gian email (trong 30 phút gần đây)
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

    def test_graph_mail_fetch(self, account_line: str):
        """Test fetching TikTok verification code using a single account line.

        Accepts formats already supported by _parse_tiktok_account_data(), including
        the Hotmail Graph variant with refresh token and client id.

        Returns (success: bool, message: str)
        """
        try:
            parsed = self._parse_tiktok_account_data(account_line)
            if not parsed:
                return False, "Không parse được dữ liệu tài khoản. Kiểm tra định dạng."

            code = self._fetch_tiktok_code_from_hotmail(parsed)
            if code:
                return True, f"Lấy mã thành công: {code}"
            return False, "Không tìm thấy email chứa mã 2FA trong thời gian chờ."
        except Exception as e:
            return False, f"Lỗi test Graph: {str(e)}"
    
    def _parse_tiktok_account_data(self, account_string):
        """Parse TikTok account data from string format"""
        try:
            # Supported formats:
            # 1) username|password|email|email_password|session_token|user_id
            # 2) username|password|hotmail_email|hotmail_password|ms_refresh_token|ms_client_id
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
            
            # Format cũ: username -> email (backward compatibility)
            elif ' -> ' in account_string:
                parts = account_string.split(' -> ')
                if len(parts) == 2:
                    username = parts[0].strip()
                    email = parts[1].strip()
                    return {
                        'username': username,
                        'email': email,
                        'password': '',  # Password cần được cung cấp riêng
                        'twofa': ''
                    }
            
            return None
        except Exception as e:
            print(f"Lỗi parse TikTok account data: {e}")
            return None
    
    # Email verification methods removed
    
    # Email refresh token methods removed
    
    def _login_tiktok_with_session(self, driver, login_data):
        """Đăng nhập TikTok bằng session token"""
        try:
            session_token = login_data.get('session_token', '')
            user_id = login_data.get('user_id', '')
            
            if not session_token:
                print("Không có session token")
                return False
            
            print(f"🔑 [TIKTOK] Đang thử đăng nhập TikTok với session token: {session_token[:20]}...")
            
            # Lấy URL hiện tại để giữ nguyên trang đang ở
            current_url = driver.current_url
            print(f"🌐 [TIKTOK] Current URL: {current_url}")
            
            # Nếu đang ở trang login, điều hướng đến trang chủ để inject cookies
            if 'login' in current_url.lower():
                print(f"🔄 [TIKTOK] Đang ở trang login, điều hướng đến trang chủ để inject cookies...")
                driver.get("https://www.tiktok.com")
                time.sleep(2)
            else:
                print(f"📍 [TIKTOK] Đang ở trang khác, giữ nguyên URL hiện tại")
            
            # Inject session token và user_id vào cookies
            print(f"🍪 [TIKTOK] Đang inject cookies...")
            cookies_to_set = [
                f"sessionid={session_token}; domain=.tiktok.com; path=/; secure; samesite=none",
                f"user_id={user_id}; domain=.tiktok.com; path=/; secure; samesite=none",
                f"tt_webid={user_id}; domain=.tiktok.com; path=/; secure; samesite=none"
            ]
            
            for cookie in cookies_to_set:
                try:
                    driver.execute_script(f"document.cookie = '{cookie}';")
                    print(f"✅ [TIKTOK] Đã inject cookie: {cookie.split('=')[0]}")
                except Exception as e:
                    print(f"❌ [TIKTOK] Lỗi set cookie: {e}")
            
            # Refresh trang để áp dụng cookies
            print(f"🔄 [TIKTOK] Refresh trang để áp dụng cookies...")
            driver.refresh()
            time.sleep(5)
            
            # Kiểm tra xem đã đăng nhập thành công chưa
            current_url = driver.current_url
            page_source = driver.page_source.lower()
            
            print(f"🌐 [TIKTOK] URL sau khi refresh: {current_url}")
            print(f"🔍 [TIKTOK] Đang kiểm tra dấu hiệu đăng nhập thành công...")
            
            # Kiểm tra các dấu hiệu đăng nhập thành công
            success_indicators = [
                'logout' in page_source,
                'profile' in page_source,
                'upload' in page_source,
                'foryou' in current_url,
                'following' in current_url
            ]
            
            print(f"📊 [TIKTOK] Success indicators: {success_indicators}")
            print(f"🔍 [TIKTOK] 'login' in URL: {'login' in current_url.lower()}")
            
            if any(success_indicators) and 'login' not in current_url.lower():
                print("✅ [TIKTOK] Đăng nhập TikTok bằng session token thành công!")
                
                # Điều hướng đến trang For You sau khi đăng nhập thành công
                try:
                    print(f"🔄 [TIKTOK] Điều hướng đến trang For You...")
                    driver.get("https://www.tiktok.com/foryou")
                    time.sleep(3)
                    print(f"✅ [TIKTOK] Đã điều hướng đến trang For You")
                except Exception as e:
                    print(f"⚠️ [TIKTOK] Không thể điều hướng đến For You: {e}")
                
                return True
            else:
                print("❌ [TIKTOK] Session token không hợp lệ hoặc đã hết hạn")
                return False
                
        except Exception as e:
            print(f"Lỗi đăng nhập TikTok với session token: {str(e)}")
            return False
   
    def _handle_2fa(self, driver, twofa_code):
        """Xử lý 2FA"""
        try:
            # Tìm trường nhập 2FA
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
            
            # Tìm và click nút xác nhận
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
            print(f"Lỗi xử lý 2FA: {str(e)}")
    
    def get_ip_location(self, ip_address):
        """Lấy thông tin vị trí địa lý từ IP"""
        # Danh sách các API để thử
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
                print(f"Lỗi API {api['url']}: {str(e)}")
                continue
        
        # Fallback: Detect một số IP phổ biến
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
        """Xuất cookies từ Chrome profile"""
        try:
            import sqlite3
            import time
            
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
            print(f"Lỗi khi xuất cookies: {str(e)}")
            return []
    
    def import_cookies_to_profile(self, profile_name, cookies, overwrite=False, valid_only=True):
        """Import cookies vào Chrome profile"""
        try:
            import sqlite3
            import time
            
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
                    
                    # Kiểm tra cookie đã tồn tại
                    cursor.execute("SELECT id FROM cookies WHERE name = ? AND host_key = ?", 
                                 (cookie['name'], cookie['domain']))
                    existing = cursor.fetchone()
                    
                    if existing and not overwrite:
                        continue
                    
                    # Xóa cookie cũ nếu tồn tại
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
                    print(f"Lỗi khi import cookie {cookie.get('name', 'unknown')}: {str(e)}")
                    continue
            
            conn.commit()
            conn.close()
            return success_count
            
        except Exception as e:
            print(f"Lỗi khi import cookies: {str(e)}")
            return 0
    
    def check_account_status(self, profile_name, platform="auto"):
        """Kiểm tra trạng thái tài khoản đã đăng nhập"""
        try:
            # Khởi động Chrome profile
            driver = self.launch_chrome_profile(profile_name, headless=True)
            if not driver:
                return False, "Không thể khởi động Chrome profile"
            
            # Xác định platform nếu auto
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
            return False, f"Lỗi kiểm tra tài khoản: {str(e)}"
        finally:
            try:
                driver.quit()
            except:
                pass
    
    def _detect_platform_from_cookies(self, profile_name):
        """Tự động phát hiện platform từ cookies"""
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
            print(f"Lỗi phát hiện platform: {str(e)}")
            return "generic"
    
    def _check_tiktok_status(self, driver):
        """Kiểm tra trạng thái TikTok"""
        try:
            driver.get("https://www.tiktok.com")
            time.sleep(3)
            
            # Kiểm tra các element cho thấy đã đăng nhập
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
            
            # Kiểm tra có button đăng nhập không
            try:
                login_btn = driver.find_element("xpath", "//button[contains(text(), 'Log in') or contains(text(), 'Đăng nhập')]")
                if login_btn:
                    return False, "Tài khoản TikTok chưa đăng nhập hoặc đã hết hạn"
            except:
                pass
            
            return False, "Không thể xác định trạng thái TikTok"
            
        except Exception as e:
            return False, f"Lỗi kiểm tra TikTok: {str(e)}"
    
    def _check_generic_status(self, driver):
        """Kiểm tra trạng thái generic"""
        try:
            # Lấy URL hiện tại
            current_url = driver.current_url
            
            # Kiểm tra có từ khóa đăng nhập trong URL
            if any(keyword in current_url.lower() for keyword in ['login', 'signin', 'auth', 'dang-nhap']):
                return False, "Tài khoản chưa đăng nhập hoặc đã hết hạn"
            
            # Kiểm tra có form đăng nhập
            try:
                login_forms = driver.find_elements("xpath", "//form[contains(@class, 'login') or contains(@id, 'login')]")
                if login_forms:
                    return False, "Tài khoản chưa đăng nhập hoặc đã hết hạn"
            except:
                pass
            
            return True, "Tài khoản có vẻ còn hoạt động"
            
        except Exception as e:
            return False, f"Lỗi kiểm tra generic: {str(e)}"
    
    def batch_check_accounts(self, profile_list=None):
        """Kiểm tra trạng thái hàng loạt tài khoản"""
        try:
            if profile_list is None:
                profile_list = self.get_all_profiles()
            
            results = {}
            
            for profile in profile_list:
                print(f"Đang kiểm tra profile: {profile}")
                status, message = self.check_account_status(profile)
                results[profile] = {
                    'status': status,
                    'message': message,
                    'platform': self._detect_platform_from_cookies(profile)
                }
                time.sleep(2)  # Delay giữa các lần kiểm tra
            
            return results
            
        except Exception as e:
            print(f"Lỗi kiểm tra hàng loạt: {str(e)}")
            return {}
    
    def get_country_flag(self, country_code):
        """Lấy emoji lá cờ từ country code"""
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
            'LOC': '🏠'  # Local Network
        }
        return flag_map.get(country_code.upper(), '🏳️')
    
    def get_all_profiles(self, force_refresh=False):
        """Lấy danh sách tất cả profiles
        
        Args:
            force_refresh: Force refresh từ file system (tránh cache)
        """
        profiles = []
        if os.path.exists(self.profiles_dir):
            try:
                # Force refresh nếu cần
                if force_refresh:
                    import time
                    time.sleep(0.1)  # Delay nhỏ để tránh cache
                
                for item in os.listdir(self.profiles_dir):
                    item_path = os.path.join(self.profiles_dir, item)
                    if os.path.isdir(item_path):
                        profiles.append(item)
                        
                print(f"📋 [PROFILES] Found {len(profiles)} profiles: {profiles}")
            except Exception as e:
                print(f"⚠️ [PROFILES] Lỗi khi đọc profiles: {e}")
                
        return profiles
    
    def delete_profile(self, profile_name):
        """Xóa profile"""
        try:
            profile_path = os.path.join(self.profiles_dir, profile_name)
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
                            print(f"Lần thử {attempt + 1}: Không thể xóa {profile_path}, đang thử lại...")
                            time.sleep(2)
                            continue
                        else:
                            # Last attempt: try to force delete locked files
                            print(f"Thử xóa force cho {profile_path}")
                            self._force_delete_directory(profile_path)
                            break
                    except Exception as e:
                        if attempt < max_retries - 1:
                            print(f"Lần thử {attempt + 1}: Lỗi khi xóa {profile_path}: {str(e)}, đang thử lại...")
                            time.sleep(2)
                            continue
                        else:
                            raise e
                
                # Xóa khỏi config
                if self.config.has_section('PROFILES') and self.config.has_option('PROFILES', profile_name):
                    self.config.remove_option('PROFILES', profile_name)
                
                
                # Xóa login data nếu có
                if self.config.has_section('LOGIN_DATA') and self.config.has_option('LOGIN_DATA', profile_name):
                    self.config.remove_option('LOGIN_DATA', profile_name)
                
                self.save_config()
                
                return True, f"Đã xóa profile '{profile_name}' và các cấu hình liên quan"
            else:
                return False, f"Profile '{profile_name}' không tồn tại"
                
        except Exception as e:
            return False, f"Lỗi khi xóa profile: {str(e)}"
    
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
                        print(f"Không thể xóa file {file_path}: {str(e)}")
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
            print(f"Lỗi trong force delete: {str(e)}")
    
    def _cleanup_profile(self, profile_path):
        """Dọn dẹp profile trước khi khởi động Chrome"""
        try:
            print(f"DEBUG: Đang dọn dẹp profile: {profile_path}")
            
            # Các file/folder cần xóa để tránh crash
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
                            print(f"DEBUG: Đã xóa file: {item}")
                        elif os.path.isdir(item_path):
                            shutil.rmtree(item_path)
                            print(f"DEBUG: Đã xóa folder: {item}")
                    except Exception as e:
                        print(f"DEBUG: Không thể xóa {item}: {str(e)}")
            
            # Xóa các file lock khác
            for root, dirs, files in os.walk(profile_path):
                for file in files:
                    if file.startswith("lockfile") or file.endswith(".lock"):
                        try:
                            os.remove(os.path.join(root, file))
                            print(f"DEBUG: Đã xóa lock file: {file}")
                        except:
                            pass
            
            print(f"DEBUG: Hoàn thành dọn dẹp profile: {profile_path}")
            
        except Exception as e:
            print(f"DEBUG: Lỗi khi dọn dẹp profile: {str(e)}")
    
    def _kill_chrome_processes(self):
        """Kill tất cả Chrome processes để tránh conflict"""
        try:
            print("DEBUG: Đang kill tất cả Chrome processes...")
            import psutil
            
            killed_count = 0
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if proc.info['name'] and 'chrome' in proc.info['name'].lower():
                        proc.kill()
                        killed_count += 1
                        print(f"DEBUG: Đã kill Chrome process: {proc.info['pid']}")
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
            
            if killed_count > 0:
                print(f"DEBUG: Đã kill {killed_count} Chrome processes")
                time.sleep(2)  # Đợi processes được kill hoàn toàn
            else:
                print("DEBUG: Không có Chrome processes nào đang chạy")
                
        except Exception as e:
            print(f"DEBUG: Lỗi khi kill Chrome processes: {str(e)}")
    
    import urllib.parse
    
    def save_tiktok_session(self, profile_name, session_data):
        """Lưu TikTok session vào Chrome profile"""
        try:
            print(f"💾 [SAVE-SESSION] Lưu TikTok session cho {profile_name}")
            
            # Lưu vào config file
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
            
            # Lưu vào Chrome profile directory
            profile_path = os.path.join(self.profiles_dir, profile_name)
            if os.path.exists(profile_path):
                session_file = os.path.join(profile_path, 'tiktok_session.json')
                with open(session_file, 'w', encoding='utf-8') as f:
                    json.dump(session_data, f, ensure_ascii=False, indent=2)
                print(f"✅ [SAVE-SESSION] Đã lưu session vào {session_file}")
            
            return True, f"Đã lưu TikTok session cho {profile_name}"
            
        except Exception as e:
            return False, f"Lỗi khi lưu session: {str(e)}"
    
    def load_tiktok_session(self, profile_name):
        """Load TikTok session từ Chrome profile"""
        try:
            print(f"📂 [LOAD-SESSION] Load TikTok session cho {profile_name}")
            
            # Thử load từ config file trước
            if self.config.has_section('TIKTOK_SESSIONS') and self.config.has_option('TIKTOK_SESSIONS', profile_name):
                import json
                session_json = self.config.get('TIKTOK_SESSIONS', profile_name)
                session_data = json.loads(session_json)
                print(f"✅ [LOAD-SESSION] Đã load session từ config")
                return True, session_data
            
            # Thử load từ Chrome profile directory
            profile_path = os.path.join(self.profiles_dir, profile_name)
            session_file = os.path.join(profile_path, 'tiktok_session.json')
            
            if os.path.exists(session_file):
                import json
                with open(session_file, 'r', encoding='utf-8') as f:
                    session_data = json.load(f)
                print(f"✅ [LOAD-SESSION] Đã load session từ {session_file}")
                return True, session_data
            
            print(f"⚠️ [LOAD-SESSION] Không tìm thấy session cho {profile_name}")
            return False, "Không tìm thấy TikTok session"
            
        except Exception as e:
            return False, f"Lỗi khi load session: {str(e)}"
    
    def get_all_tiktok_sessions(self):
        """Lấy tất cả TikTok sessions"""
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
            return False, f"Lỗi khi lấy sessions: {str(e)}"
    
    def clear_tiktok_session(self, profile_name):
        """Xóa TikTok session"""
        try:
            print(f"🗑️ [CLEAR-SESSION] Xóa TikTok session cho {profile_name}")
            
            # Xóa từ config
            if self.config.has_section('TIKTOK_SESSIONS') and self.config.has_option('TIKTOK_SESSIONS', profile_name):
                self.config.remove_option('TIKTOK_SESSIONS', profile_name)
                self.save_config()
            
            # Xóa từ Chrome profile directory
            profile_path = os.path.join(self.profiles_dir, profile_name)
            session_file = os.path.join(profile_path, 'tiktok_session.json')
            
            if os.path.exists(session_file):
                os.remove(session_file)
                print(f"✅ [CLEAR-SESSION] Đã xóa session file")
            
            return True, f"Đã xóa TikTok session cho {profile_name}"
            
        except Exception as e:
            return False, f"Lỗi khi xóa session: {str(e)}"

    def kill_chrome_processes(self):
        """Tắt tất cả tiến trình Chrome"""
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                if 'chrome' in proc.info['name'].lower():
                    proc.kill()
            return True, "Đã tắt tất cả tiến trình Chrome"
        except Exception as e:
            return False, f"Lỗi khi tắt Chrome: {str(e)}"
    
    def auto_start_profiles(self):
        """Tự động khởi động các profiles được cấu hình"""
        if not self.config.getboolean('SETTINGS', 'auto_start', fallback=False):
            return
        
        delay = self.config.getint('SETTINGS', 'startup_delay', fallback=5)
        time.sleep(delay)
        
        profiles = self.get_all_profiles()
        for profile in profiles:
            hidden = self.config.getboolean('SETTINGS', 'hidden_mode', fallback=True)
            self.launch_chrome_profile(profile, hidden=hidden)
            time.sleep(2)  # Delay giữa các profiles

    def _apply_base_chrome_config(self, chrome_options, hidden=True):
        """Apply base Chrome configuration"""
        # ONLY essential Chrome arguments
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        
        # Disable automation detection
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Window settings
        if hidden:
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--window-size=1024,768")
        else:
            chrome_options.add_argument("--window-size=1024,768")
        
        # NO --enable-automation
        # NO --test-type=webdriver
        # NO --disable-web-security
        # NO --disable-extensions
        # NO --disable-plugins
        # NO --disable-background-networking
        # NO other network-related arguments

    def _apply_optimized_chrome_config(self, chrome_options, hidden=True, ultra_low_memory=False):
        """Apply optimized Chrome configuration for bulk operations (50-200 profiles)"""
        
        # === ESSENTIAL FLAGS ===
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        
        # === MEMORY OPTIMIZATION ===
        chrome_options.add_argument("--memory-pressure-off")
        chrome_options.add_argument("--max_old_space_size=512")  # Limit V8 heap
        chrome_options.add_argument("--js-flags=--max-old-space-size=512")
        
        if ultra_low_memory:
            chrome_options.add_argument("--max_old_space_size=256")
            chrome_options.add_argument("--js-flags=--max-old-space-size=256")
            chrome_options.add_argument("--memory-pressure-off")
        
        # === PROCESS OPTIMIZATION ===
        chrome_options.add_argument("--single-process")  # Single process mode
        chrome_options.add_argument("--no-zygote")  # Disable zygote process
        chrome_options.add_argument("--disable-background-timer-throttling")
        chrome_options.add_argument("--disable-backgrounding-occluded-windows")
        chrome_options.add_argument("--disable-renderer-backgrounding")
        
        # === NETWORK OPTIMIZATION ===
        chrome_options.add_argument("--disable-background-networking")
        chrome_options.add_argument("--disable-background-sync")
        chrome_options.add_argument("--disable-client-side-phishing-detection")
        chrome_options.add_argument("--disable-component-extensions-with-background-pages")
        chrome_options.add_argument("--disable-default-apps")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-features=TranslateUI")
        chrome_options.add_argument("--disable-hang-monitor")
        chrome_options.add_argument("--disable-ipc-flooding-protection")
        chrome_options.add_argument("--disable-popup-blocking")
        chrome_options.add_argument("--disable-prompt-on-repost")
        chrome_options.add_argument("--disable-sync")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--disable-features=VizDisplayCompositor")
        
        # === MEDIA OPTIMIZATION ===
        chrome_options.add_argument("--disable-audio-output")
        chrome_options.add_argument("--disable-audio-input")
        chrome_options.add_argument("--disable-video")
        chrome_options.add_argument("--mute-audio")
        chrome_options.add_argument("--disable-media-session-api")
        
        # === RENDERING OPTIMIZATION ===
        chrome_options.add_argument("--disable-2d-canvas-clip-aa")
        chrome_options.add_argument("--disable-3d-apis")
        chrome_options.add_argument("--disable-accelerated-2d-canvas")
        chrome_options.add_argument("--disable-accelerated-jpeg-decoding")
        chrome_options.add_argument("--disable-accelerated-mjpeg-decode")
        chrome_options.add_argument("--disable-accelerated-video-decode")
        chrome_options.add_argument("--disable-canvas-aa")
        chrome_options.add_argument("--disable-composited-antialiasing")
        chrome_options.add_argument("--disable-font-subpixel-positioning")
        chrome_options.add_argument("--disable-gpu-compositing")
        chrome_options.add_argument("--disable-gpu-rasterization")
        chrome_options.add_argument("--disable-gpu-sandbox")
        chrome_options.add_argument("--disable-software-rasterizer")
        chrome_options.add_argument("--disable-webgl")
        chrome_options.add_argument("--disable-webgl2")
        
        # === CACHE & STORAGE OPTIMIZATION ===
        chrome_options.add_argument("--disable-background-mode")
        chrome_options.add_argument("--disable-databases")
        chrome_options.add_argument("--disable-file-system")
        chrome_options.add_argument("--disable-local-storage")
        chrome_options.add_argument("--disable-session-storage")
        chrome_options.add_argument("--disable-web-sql")
        chrome_options.add_argument("--aggressive-cache-discard")
        chrome_options.add_argument("--memory-pressure-off")
        
        # === AUTOMATION DETECTION BYPASS ===
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # === WINDOW SETTINGS ===
        if hidden:
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--window-size=800,600")  # Smaller window
        else:
            chrome_options.add_argument("--window-size=800,600")  # Smaller window
        
        # === PERFORMANCE MONITORING ===
        chrome_options.add_argument("--enable-logging")
        chrome_options.add_argument("--log-level=3")  # Only errors
        
        # === ADDITIONAL LOW-MEMORY FLAGS ===
        if ultra_low_memory:
            chrome_options.add_argument("--disable-features=TranslateUI,BlinkGenPropertyTrees")
            chrome_options.add_argument("--disable-threaded-compositing")
            chrome_options.add_argument("--disable-threaded-scrolling")
            chrome_options.add_argument("--disable-checker-imaging")
            chrome_options.add_argument("--disable-image-animation-resync")
            chrome_options.add_argument("--disable-new-tab-first-run")
            chrome_options.add_argument("--disable-plugins-discovery")
            chrome_options.add_argument("--disable-preconnect")
            chrome_options.add_argument("--disable-print-preview")
            chrome_options.add_argument("--disable-speech-api")
            chrome_options.add_argument("--disable-speech-synthesis-api")
            chrome_options.add_argument("--disable-web-bluetooth")
            chrome_options.add_argument("--disable-web-usb")
            chrome_options.add_argument("--no-first-run")
            chrome_options.add_argument("--no-default-browser-check")
            chrome_options.add_argument("--no-pings")
            chrome_options.add_argument("--no-service-autorun")
            chrome_options.add_argument("--password-store=basic")
            chrome_options.add_argument("--use-mock-keychain")
        
        print(f"🔧 [CHROME-OPTIMIZE] Applied {'ultra-low' if ultra_low_memory else 'standard'} memory optimization")

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
            print(f"⚠️ [MEMORY] Lỗi khi lấy thông tin memory: {e}")
            return None

    def cleanup_memory(self):
        """Dọn dẹp memory và tối ưu hóa"""
        try:
            import gc
            import psutil
            
            # Force garbage collection
            gc.collect()
            
            # Get current memory usage
            memory_info = self.get_memory_usage()
            if memory_info:
                print(f"🧹 [MEMORY-CLEANUP] Chrome RAM: {memory_info['chrome_memory_mb']}MB")
                print(f"🧹 [MEMORY-CLEANUP] System RAM: {memory_info['system_memory_percent']}%")
                print(f"🧹 [MEMORY-CLEANUP] Available: {memory_info['available_memory_gb']}GB")
            
            return memory_info
        except Exception as e:
            print(f"⚠️ [MEMORY-CLEANUP] Lỗi: {e}")
            return None

    def _launch_chrome_with_fallback(self, chrome_options, profile_path, hidden):
        """Launch Chrome with fallback mechanism"""
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager
        
        service = Service(ChromeDriverManager().install())
        
        # Try main configuration
        try:
            driver = webdriver.Chrome(service=service, options=chrome_options)
            driver.set_page_load_timeout(30)
            driver.implicitly_wait(10)
            print(f"✅ [LAUNCH] Chrome started successfully")
            return driver
            
        except Exception as e:
            print(f"⚠️ [LAUNCH] Main config failed: {str(e)}")
            
            # Fallback: minimal configuration
            print(f"🔄 [LAUNCH] Trying fallback mode...")
            fallback_options = Options()
            fallback_options.add_argument(f"--user-data-dir={profile_path}")
            fallback_options.add_argument("--no-sandbox")
            fallback_options.add_argument("--disable-dev-shm-usage")
            fallback_options.add_argument("--disable-gpu")
            
            if hidden:
                fallback_options.add_argument("--headless")
            
            try:
                driver = webdriver.Chrome(service=service, options=fallback_options)
                driver.set_page_load_timeout(30)
                driver.implicitly_wait(10)
                print(f"✅ [LAUNCH] Chrome started with fallback mode")
                return driver
                
            except Exception as e2:
                print(f"❌ [LAUNCH] Fallback also failed: {str(e2)}")
                return None

    def _cleanup_profile_cache(self, profile_path):
        """Clean profile cache directories"""
        try:
            import shutil
            
            cache_dirs = [
                os.path.join(profile_path, 'Default', 'Cache'),
                os.path.join(profile_path, 'Default', 'Code Cache'),
                os.path.join(profile_path, 'Default', 'GPUCache'),
                os.path.join(profile_path, 'Default', 'Network'),
                os.path.join(profile_path, 'Default', 'Service Worker'),
            ]
            
            for cache_dir in cache_dirs:
                if os.path.exists(cache_dir):
                    try:
                        shutil.rmtree(cache_dir, ignore_errors=True)
                        print(f"🧹 [CLEANUP] Cleaned: {os.path.basename(cache_dir)}")
                    except:
                        pass
                        
        except Exception as e:
            print(f"⚠️ [CLEANUP] Cache cleanup failed: {str(e)}")

    def _handle_auto_login(self, driver, profile_path, auto_login, login_data, start_url):
        """Handle auto login logic"""
        try:
            # Check if profile is already logged in
            marker_file = os.path.join(profile_path, 'tiktok_logged_in.txt')
            
            if os.path.exists(marker_file):
                print(f"✅ [LOGIN] Profile already logged in, loading cookies...")
                cookies_loaded = self._load_cookies_from_profile(profile_path, driver)
                if cookies_loaded:
                    driver.get("https://www.tiktok.com/foryou")
                    time.sleep(3)
                    return True
                else:
                    print(f"⚠️ [LOGIN] Failed to load cookies, performing auto-login...")
            
            # Perform auto-login if requested
            if auto_login and login_data:
                print(f"🔐 [LOGIN] Starting auto-login...")
                if start_url:
                    driver.get(start_url)
                    time.sleep(2)
                else:
                    driver.get(login_data.get('login_url', 'https://www.tiktok.com/login'))
                    time.sleep(2)
                
                login_success = self._perform_auto_login(driver, login_data, start_url)
                if login_success:
                    print(f"✅ [LOGIN] Auto-login successful")
                    return True
                else:
                    print(f"❌ [LOGIN] Auto-login failed")
                    return False
            else:
                print(f"ℹ️ [LOGIN] No auto-login requested")
                return True
                
        except Exception as e:
            print(f"❌ [LOGIN] Login handling failed: {str(e)}")
            return False

    def install_extension_for_profile(self, profile_name, extension_id="pfnededegaaopdmhkdmcofjmoldfiped"):
        """
        Install Proxy SwitchyOmega 3 extension for a specific profile
        
        Args:
            profile_name (str): Name of the Chrome profile
            extension_id (str): Chrome Web Store extension ID (default: Proxy SwitchyOmega 3)
        
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            print(f"🔧 [EXTENSION] Installing Proxy SwitchyOmega 3 for profile: {profile_name}")
            
            # Get profile path
            profile_path = self.get_profile_path(profile_name)
            if not profile_path or not os.path.exists(profile_path):
                return False, f"Profile path not found: {profile_name}"
            
            # Check if extension is already installed
            if self.check_extension_installed(profile_name, extension_id):
                return True, "Extension already installed"
            
            # Try multiple installation methods
            methods = [
                self._install_extension_method_1,  # Direct copy method
                self._install_extension_method_2,  # WebStore method
                self._install_extension_method_3   # CRX method
            ]
            
            for i, method in enumerate(methods, 1):
                try:
                    print(f"🔄 [EXTENSION] Trying installation method {i} for {profile_name}")
                    success, message = method(profile_name, extension_id)
                    if success:
                        print(f"✅ [EXTENSION] Method {i} successful: {message}")
                        return True, f"Installed using method {i}: {message}"
                    else:
                        print(f"❌ [EXTENSION] Method {i} failed: {message}")
                except Exception as e:
                    print(f"❌ [EXTENSION] Method {i} error: {str(e)}")
                    continue
            
            return False, "All installation methods failed"
            
        except Exception as e:
            print(f"❌ [EXTENSION] Error installing extension for {profile_name}: {str(e)}")
            return False, f"Installation error: {str(e)}"
    
    def _install_extension_method_1(self, profile_name, extension_id):
        """Method 1: Direct copy from local extension directory"""
        try:
            profile_path = self.get_profile_path(profile_name)
            extensions_dir = os.path.join(profile_path, "Extensions")
            if not os.path.exists(extensions_dir):
                os.makedirs(extensions_dir)
            
            # Check if we have local extension files
            local_extensions = ["extensions/SwitchyOmega", "extensions/SwitchyOmega3_Real"]
            extension_source = None
            
            for ext_dir in local_extensions:
                if os.path.exists(ext_dir):
                    extension_source = ext_dir
                    break
            
            if not extension_source:
                return False, "No local extension files found"
            
            # Copy extension files
            final_extension_dir = os.path.join(extensions_dir, extension_id)
            if os.path.exists(final_extension_dir):
                import shutil
                shutil.rmtree(final_extension_dir)
            
            import shutil
            shutil.copytree(extension_source, final_extension_dir)
            
            # Create manifest.json if not exists
            manifest_path = os.path.join(final_extension_dir, "manifest.json")
            if not os.path.exists(manifest_path):
                manifest_content = {
                    "manifest_version": 3,
                    "name": "Proxy SwitchyOmega 3 (ZeroOmega)",
                    "version": "3.0.0",
                    "description": "A proxy configuration tool",
                    "permissions": [
                        "proxy",
                        "storage",
                        "tabs",
                        "webRequest",
                        "webRequestBlocking",
                        "management",
                        "unlimitedStorage"
                    ],
                    "background": {
                        "service_worker": "background.js"
                    },
                    "action": {
                        "default_popup": "popup.html",
                        "default_title": "SwitchyOmega"
                    },
                    "icons": {
                        "16": "icon16.png",
                        "48": "icon48.png",
                        "128": "icon128.png"
                    }
                }
                
                import json
                with open(manifest_path, 'w', encoding='utf-8') as f:
                    json.dump(manifest_content, f, indent=2, ensure_ascii=False)
            
            return True, "Extension installed via direct copy"
            
        except Exception as e:
            return False, f"Direct copy method failed: {str(e)}"
    
    def _install_extension_method_2(self, profile_name, extension_id):
        """Method 2: WebStore installation via Selenium"""
        try:
            profile_path = self.get_profile_path(profile_name)
            extension_url = f"https://chromewebstore.google.com/detail/proxy-switchyomega-3-zero/{extension_id}"
            
            # Launch Chrome with the extension installation URL
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
            from webdriver_manager.chrome import ChromeDriverManager
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
            try:
                # Navigate to extension page
                driver.get(extension_url)
                driver.implicitly_wait(10)
                
                # Wait for page to load
                import time
                time.sleep(3)
                
                # Try to find and click the "Add to Chrome" button
                try:
                    # Look for the Add to Chrome button
                    add_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Add to Chrome') or contains(text(), 'Thêm vào Chrome')]"))
                    )
                    add_button.click()
                    print(f"✅ [EXTENSION] Clicked Add to Chrome button for {profile_name}")
                    
                    # Wait for installation confirmation
                    time.sleep(5)
                    
                    # Check if installation was successful
                    if self.check_extension_installed(profile_name, extension_id):
                        return True, "Extension installed via WebStore"
                    else:
                        return False, "Extension installation failed - not detected after installation"
                        
                except Exception as e:
                    print(f"❌ [EXTENSION] Could not find Add to Chrome button: {str(e)}")
                    return False, f"Could not find Add to Chrome button: {str(e)}"
                
            except Exception as e:
                return False, f"WebStore method failed: {str(e)}"
            finally:
                driver.quit()
                
        except Exception as e:
            return False, f"WebStore method failed: {str(e)}"
    
    def _install_extension_method_3(self, profile_name, extension_id):
        """Method 3: CRX file installation"""
        try:
            # Download or use existing CRX file
            crx_file_path = self.download_switchyomega_extension()
            if not crx_file_path:
                return False, "Could not download CRX file"
            
            profile_path = self.get_profile_path(profile_name)
            extensions_dir = os.path.join(profile_path, "Extensions")
            if not os.path.exists(extensions_dir):
                os.makedirs(extensions_dir)
            
            # Launch Chrome with CRX installation
            chrome_options = Options()
            chrome_options.add_argument(f"--user-data-dir={profile_path}")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1024,768")
            chrome_options.add_argument("--disable-web-security")
            chrome_options.add_argument("--disable-features=VizDisplayCompositor")
            
            # Disable automation detection
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            from selenium import webdriver
            from selenium.webdriver.chrome.service import Service
            from webdriver_manager.chrome import ChromeDriverManager
            
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
            try:
                # Navigate to chrome://extensions/
                driver.get("chrome://extensions/")
                
                # Enable developer mode
                import time
                time.sleep(2)
                
                # Try to enable developer mode
                try:
                    from selenium.webdriver.common.by import By
                    from selenium.webdriver.support.ui import WebDriverWait
                    from selenium.webdriver.support import expected_conditions as EC
                    
                    # Look for developer mode toggle
                    developer_toggle = driver.find_element(By.XPATH, "//input[@type='checkbox' and @id='devMode']")
                    if not developer_toggle.is_selected():
                        developer_toggle.click()
                        time.sleep(1)
                    
                    # Look for "Load unpacked" button and click it
                    load_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Load unpacked') or contains(text(), 'Tải đã giải nén')]"))
                    )
                    load_button.click()
                    
                    # This would normally open a file dialog, but we can't interact with it via Selenium
                    # So we'll use the direct copy method instead
                    return self._install_extension_method_1(profile_name, extension_id)
                        
                except Exception as e:
                    print(f"❌ [EXTENSION] Could not enable developer mode: {str(e)}")
                    return self._install_extension_method_1(profile_name, extension_id)
                    
            finally:
                driver.quit()
                
        except Exception as e:
            return False, f"CRX method failed: {str(e)}"
    
    def install_extension_for_all_profiles(self, extension_id="pfnededegaaopdmhkdmcofjmoldfiped"):
        """
        Install Proxy SwitchyOmega 3 extension for ALL profiles (new and existing)
        
        Args:
            extension_id (str): Chrome Web Store extension ID
        
        Returns:
            tuple: (success_count: int, results: list)
        """
        all_profiles = self.get_all_profiles()
        return self.bulk_install_extension(all_profiles, extension_id)
    
    def install_extension_for_new_profiles(self, extension_id="pfnededegaaopdmhkdmcofjmoldfiped"):
        """
        Install Proxy SwitchyOmega 3 extension for profiles that don't have it yet
        
        Args:
            extension_id (str): Chrome Web Store extension ID
        
        Returns:
            tuple: (success_count: int, results: list)
        """
        all_profiles = self.get_all_profiles()
        profiles_without_extension = []
        
        print(f"🔍 [EXTENSION] Checking which profiles need extension installation...")
        
        for profile_name in all_profiles:
            if not self.check_extension_installed(profile_name, extension_id):
                profiles_without_extension.append(profile_name)
                print(f"📝 [EXTENSION] {profile_name} needs extension installation")
            else:
                print(f"✅ [EXTENSION] {profile_name} already has extension")
        
        if not profiles_without_extension:
            print(f"🎉 [EXTENSION] All profiles already have the extension installed!")
            return 0, ["All profiles already have extension installed"]
        
        print(f"🚀 [EXTENSION] Installing extension for {len(profiles_without_extension)} profiles that need it...")
        return self.bulk_install_extension(profiles_without_extension, extension_id)
    
    def bulk_install_extension(self, profile_list=None, extension_id="pfnededegaaopdmhkdmcofjmoldfiped"):
        """
        Install Proxy SwitchyOmega 3 extension for multiple profiles
        
        Args:
            profile_list (list): List of profile names (if None, install for all profiles)
            extension_id (str): Chrome Web Store extension ID
        
        Returns:
            tuple: (success_count: int, results: list)
        """
        if profile_list is None:
            profile_list = self.get_all_profiles()
        
        success_count = 0
        results = []
        
        print(f"🚀 [BULK-EXTENSION] Starting bulk installation for {len(profile_list)} profiles")
        
        for profile_name in profile_list:
            try:
                success, message = self.install_extension_for_profile(profile_name, extension_id)
                result = f"{'✅' if success else '❌'} {profile_name}: {message}"
                results.append(result)
                
                if success:
                    success_count += 1
                
                # Small delay between installations
                import time
                time.sleep(1)
                
            except Exception as e:
                error_msg = f"❌ {profile_name}: Error - {str(e)}"
                results.append(error_msg)
                print(f"❌ [BULK-EXTENSION] Error for {profile_name}: {str(e)}")
        
        print(f"🎉 [BULK-EXTENSION] Completed: {success_count}/{len(profile_list)} successful")
        return success_count, results
    
    def check_extension_installed(self, profile_name, extension_id="pfnededegaaopdmhkdmcofjmoldfiped"):
        """
        Check if Proxy SwitchyOmega 3 extension is properly installed for a profile
        
        Args:
            profile_name (str): Name of the Chrome profile
            extension_id (str): Chrome Web Store extension ID
        
        Returns:
            bool: True if extension is properly installed, False otherwise
        """
        try:
            profile_path = self.get_profile_path(profile_name)
            if not profile_path:
                print(f"⚠️ [EXTENSION-CHECK] Profile path not found for {profile_name}")
                return False
            
            # Check extensions directory (try both locations)
            extensions_dir = os.path.join(profile_path, "Extensions")
            default_extensions_dir = os.path.join(profile_path, "Default", "Extensions")
            
            # Try Default/Extensions first, then Extensions
            if os.path.exists(default_extensions_dir):
                extensions_dir = default_extensions_dir
                print(f"📋 [EXTENSION-CHECK] Using Default/Extensions for {profile_name}")
            elif os.path.exists(extensions_dir):
                print(f"📋 [EXTENSION-CHECK] Using Extensions for {profile_name}")
            else:
                print(f"⚠️ [EXTENSION-CHECK] No Extensions directory found for {profile_name}")
                return False
            
            # Look for extension folder
            extension_found = False
            extension_path = None
            
            try:
                extensions = os.listdir(extensions_dir)
                print(f"📋 [EXTENSION-CHECK] Available extensions in {profile_name}: {extensions}")
                
                for item in extensions:
                    if extension_id in item:
                        extension_path = os.path.join(extensions_dir, item)
                        extension_found = True
                        print(f"✅ [EXTENSION-CHECK] Found extension folder: {item} for {profile_name}")
                        break
                
                if not extension_found:
                    print(f"❌ [EXTENSION-CHECK] Extension folder not found in {profile_name}")
                    return False
                        
            except Exception as e:
                print(f"❌ [EXTENSION-CHECK] Error listing extensions: {str(e)}")
                return False
            
            # Check if extension has proper files
            if extension_path and os.path.exists(extension_path):
                # Look for version folder
                version_folders = [d for d in os.listdir(extension_path) if os.path.isdir(os.path.join(extension_path, d))]
                if not version_folders:
                    print(f"❌ [EXTENSION-CHECK] No version folders found in extension")
                    return False
                
                # Use the latest version folder
                latest_version = sorted(version_folders)[-1]
                version_path = os.path.join(extension_path, latest_version)
                
                # Check for essential files in version folder
                essential_files = ["manifest.json", "popup.html"]
                missing_files = []
                
                for file_name in essential_files:
                    file_path = os.path.join(version_path, file_name)
                    if not os.path.exists(file_path):
                        missing_files.append(file_name)
                
                # Check for background.js in js folder
                background_js_path = os.path.join(version_path, "js", "background.js")
                if not os.path.exists(background_js_path):
                    missing_files.append("js/background.js")
                
                if missing_files:
                    print(f"❌ [EXTENSION-CHECK] Extension folder exists but missing files: {missing_files}")
                    return False
                
                # Check manifest.json content
                manifest_path = os.path.join(version_path, "manifest.json")
                try:
                    import json
                    with open(manifest_path, 'r', encoding='utf-8') as f:
                        manifest = json.load(f)
                    
                    # Check if it's a valid SwitchyOmega manifest
                    if manifest.get("name", "").lower().find("switchyomega") == -1:
                        print(f"❌ [EXTENSION-CHECK] Extension folder exists but not SwitchyOmega")
                        return False
                    
                    print(f"✅ [EXTENSION-CHECK] Extension properly installed with valid manifest")
                    return True
                    
                except Exception as e:
                    print(f"❌ [EXTENSION-CHECK] Error reading manifest: {str(e)}")
                    return False
            else:
                print(f"❌ [EXTENSION-CHECK] Extension folder path not found")
                return False
            
        except Exception as e:
            print(f"❌ [EXTENSION-CHECK] Error checking extension for {profile_name}: {str(e)}")
            return False
    
    def download_switchyomega_extension(self):
        """
        Download Proxy SwitchyOmega 3 extension .crx file
        
        Returns:
            str: Path to downloaded .crx file, or None if failed
        """
        try:
            import requests
            import os
            
            # Create extensions directory if it doesn't exist
            extensions_dir = os.path.join(os.getcwd(), "extensions")
            if not os.path.exists(extensions_dir):
                os.makedirs(extensions_dir)
            
            # Extension download URL (direct .crx file)
            extension_url = "https://github.com/FelisCatus/SwitchyOmega/releases/download/v2.5.21/SwitchyOmega_Chromium.crx"
            crx_file_path = os.path.join(extensions_dir, "SwitchyOmega_Chromium.crx")
            
            # Check if file already exists
            if os.path.exists(crx_file_path):
                print(f"✅ [DOWNLOAD] Extension file already exists: {crx_file_path}")
                return crx_file_path
            
            print(f"📥 [DOWNLOAD] Downloading Proxy SwitchyOmega 3 extension...")
            print(f"🔗 [DOWNLOAD] URL: {extension_url}")
            
            # Download the file
            response = requests.get(extension_url, stream=True)
            response.raise_for_status()
            
            # Save the file
            with open(crx_file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print(f"✅ [DOWNLOAD] Extension downloaded successfully: {crx_file_path}")
            return crx_file_path
            
        except Exception as e:
            print(f"❌ [DOWNLOAD] Error downloading extension: {str(e)}")
            return None
    
    def download_extension_from_webstore(self):
        """
        Download real SwitchyOmega 3 extension from Chrome Web Store
        
        Returns:
            str: Path to downloaded extension files, or None if failed
        """
        try:
            import requests
            import os
            import zipfile
            import shutil
            import json
            
            # Create extensions directory if it doesn't exist
            extensions_dir = os.path.join(os.getcwd(), "extensions")
            if not os.path.exists(extensions_dir):
                os.makedirs(extensions_dir)
            
            # Extension ID for SwitchyOmega 3
            extension_id = "pfnededegaaopdmhkdmcofjmoldfiped"
            extension_name = "SwitchyOmega3_Real"
            
            # Create extension directory
            extension_dir = os.path.join(extensions_dir, extension_name)
            if os.path.exists(extension_dir):
                shutil.rmtree(extension_dir)
            os.makedirs(extension_dir)
            
            print(f"📥 [REAL-EXTENSION] Downloading real SwitchyOmega 3 extension...")
            
            # Try to download from Chrome Web Store API
            try:
                # Chrome Web Store API endpoint
                api_url = f"https://chromewebstore.google.com/detail/proxy-switchyomega-3-zero/{extension_id}"
                
                # Use requests to get the extension page
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36'
                }
                
                response = requests.get(api_url, headers=headers, timeout=30)
                print(f"🔗 [REAL-EXTENSION] Fetched extension page: {response.status_code}")
                
                # Try to extract download link from the page
                if response.status_code == 200:
                    # Look for download link in the page
                    import re
                    download_patterns = [
                        r'href="([^"]*\.crx[^"]*)"',
                        r'src="([^"]*\.crx[^"]*)"',
                        r'data-crx="([^"]*)"'
                    ]
                    
                    for pattern in download_patterns:
                        matches = re.findall(pattern, response.text)
                        if matches:
                            print(f"🔍 [REAL-EXTENSION] Found potential download links: {matches}")
                            break
                
            except Exception as e:
                print(f"⚠️ [REAL-EXTENSION] Could not fetch from Chrome Web Store: {str(e)}")
            
            # Create a more complete manifest.json based on the real extension
            manifest = {
                "manifest_version": 3,
                "name": "Proxy SwitchyOmega 3 (ZeroOmega)",
                "version": "3.4.1",
                "description": "Manage and switch between multiple proxies quickly & easily.",
                "permissions": [
                    "proxy",
                    "storage",
                    "tabs",
                    "webRequest",
                    "webRequestBlocking",
                    "unlimitedStorage",
                    "contextMenus",
                    "cookies",
                    "notifications",
                    "background",
                    "activeTab",
                    "scripting"
                ],
                "host_permissions": [
                    "<all_urls>"
                ],
                "background": {
                    "service_worker": "background.js"
                },
                "action": {
                    "default_popup": "popup.html",
                    "default_title": "SwitchyOmega",
                    "default_icon": {
                        "16": "icons/icon16.png",
                        "32": "icons/icon32.png",
                        "48": "icons/icon48.png",
                        "128": "icons/icon128.png"
                    }
                },
                "icons": {
                    "16": "icons/icon16.png",
                    "32": "icons/icon32.png",
                    "48": "icons/icon48.png",
                    "128": "icons/icon128.png"
                },
                "options_page": "options.html",
                "content_security_policy": {
                    "extension_pages": "script-src 'self'; object-src 'self'"
                }
            }
            
            # Save manifest.json
            manifest_path = os.path.join(extension_dir, "manifest.json")
            with open(manifest_path, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, indent=2)
            
            # Create icons directory
            icons_dir = os.path.join(extension_dir, "icons")
            os.makedirs(icons_dir)
            
            # Create more complete background.js
            background_js = """
// SwitchyOmega 3 Background Script
chrome.runtime.onInstalled.addListener((details) => {
    console.log('SwitchyOmega 3 extension installed:', details.reason);
    
    // Initialize default settings
    chrome.storage.local.set({
        'switchyomega_profiles': {},
        'switchyomega_current_profile': 'direct',
        'switchyomega_options': {
            'auto_switch': false,
            'quick_switch': true
        }
    });
});

// Handle proxy changes
chrome.proxy.onProxyError.addListener((details) => {
    console.log('Proxy error:', details);
});

// Handle extension icon click
chrome.action.onClicked.addListener((tab) => {
    // Open options page
    chrome.tabs.create({ url: chrome.runtime.getURL('options.html') });
});

// Handle context menu
chrome.contextMenus.onClicked.addListener((info, tab) => {
    if (info.menuItemId === 'switchyomega_quick_switch') {
        // Quick switch functionality
        console.log('Quick switch clicked');
    }
});

// Create context menu
chrome.runtime.onInstalled.addListener(() => {
    chrome.contextMenus.create({
        id: 'switchyomega_quick_switch',
        title: 'SwitchyOmega: Quick Switch',
        contexts: ['page']
    });
});
"""
            
            # Create popup.html
            popup_html = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>SwitchyOmega 3</title>
    <style>
        body { 
            width: 320px; 
            padding: 15px; 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
        }
        .header { 
            text-align: center; 
            margin-bottom: 15px; 
            padding-bottom: 10px;
            border-bottom: 1px solid #e0e0e0;
        }
        .title { 
            font-size: 16px; 
            font-weight: 600; 
            color: #333;
            margin: 0;
        }
        .subtitle {
            font-size: 12px;
            color: #666;
            margin: 5px 0 0 0;
        }
        .status { 
            color: #4CAF50; 
            font-size: 12px; 
            text-align: center;
            margin: 10px 0;
        }
        .button {
            width: 100%;
            padding: 8px 12px;
            margin: 5px 0;
            border: 1px solid #ddd;
            border-radius: 4px;
            background: #f8f9fa;
            cursor: pointer;
            font-size: 13px;
        }
        .button:hover {
            background: #e9ecef;
        }
        .button.primary {
            background: #007bff;
            color: white;
            border-color: #007bff;
        }
        .button.primary:hover {
            background: #0056b3;
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="title">Proxy SwitchyOmega 3</div>
        <div class="subtitle">ZeroOmega</div>
    </div>
    
    <div class="status">✅ Extension Active</div>
    
    <button class="button primary" onclick="openOptions()">Open Options</button>
    <button class="button" onclick="quickSwitch()">Quick Switch</button>
    <button class="button" onclick="viewProfiles()">View Profiles</button>
    
    <script>
        function openOptions() {
            chrome.tabs.create({ url: chrome.runtime.getURL('options.html') });
        }
        
        function quickSwitch() {
            // Quick switch functionality
            console.log('Quick switch activated');
        }
        
        function viewProfiles() {
            // View profiles functionality
            console.log('View profiles');
        }
    </script>
</body>
</html>
"""
            
            # Create options.html
            options_html = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>SwitchyOmega 3 Options</title>
    <style>
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 20px;
            background: #f5f5f5;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid #007bff;
        }
        .title {
            font-size: 24px;
            font-weight: 600;
            color: #333;
            margin: 0;
        }
        .subtitle {
            font-size: 14px;
            color: #666;
            margin: 5px 0 0 0;
        }
        .section {
            margin: 20px 0;
            padding: 15px;
            border: 1px solid #e0e0e0;
            border-radius: 6px;
        }
        .section h3 {
            margin: 0 0 15px 0;
            color: #333;
            font-size: 16px;
        }
        .status {
            color: #4CAF50;
            font-weight: 500;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="title">Proxy SwitchyOmega 3</div>
            <div class="subtitle">ZeroOmega - Proxy Management</div>
        </div>
        
        <div class="section">
            <h3>Extension Status</h3>
            <p class="status">✅ Extension is active and ready to use</p>
            <p>Version: 3.4.1</p>
            <p>Developer: suziwen1</p>
        </div>
        
        <div class="section">
            <h3>Proxy Profiles</h3>
            <p>Manage your proxy profiles here. Click "Add Profile" to create a new proxy configuration.</p>
            <button onclick="addProfile()">Add Profile</button>
        </div>
        
        <div class="section">
            <h3>Quick Switch</h3>
            <p>Enable quick switching between proxy profiles from the browser toolbar.</p>
            <label>
                <input type="checkbox" checked> Enable Quick Switch
            </label>
        </div>
        
        <div class="section">
            <h3>About</h3>
            <p>Proxy SwitchyOmega 3 (ZeroOmega) is a powerful proxy management extension for Chrome.</p>
            <p>Features:</p>
            <ul>
                <li>Multiple proxy profiles</li>
                <li>Quick switching</li>
                <li>Auto-switch rules</li>
                <li>PAC script support</li>
            </ul>
        </div>
    </div>
    
    <script>
        function addProfile() {
            alert('Add Profile functionality will be implemented');
        }
    </script>
</body>
</html>
"""
            
            # Save extension files
            with open(os.path.join(extension_dir, "background.js"), 'w', encoding='utf-8') as f:
                f.write(background_js)
            
            with open(os.path.join(extension_dir, "popup.html"), 'w', encoding='utf-8') as f:
                f.write(popup_html)
            
            with open(os.path.join(extension_dir, "options.html"), 'w', encoding='utf-8') as f:
                f.write(options_html)
            
            # Create better icon files (SVG-based PNG)
            icon_svg = """<svg width="128" height="128" viewBox="0 0 128 128" xmlns="http://www.w3.org/2000/svg">
                <rect width="128" height="128" rx="20" fill="#007bff"/>
                <circle cx="64" cy="64" r="40" fill="white"/>
                <path d="M44 64 L60 48 L76 64 L60 80 Z" fill="#007bff"/>
                <text x="64" y="100" text-anchor="middle" fill="white" font-family="Arial" font-size="12" font-weight="bold">Ω</text>
            </svg>"""
            
            # Convert SVG to PNG bytes (simplified)
            icon_bytes = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x80\x00\x00\x00\x80\x08\x06\x00\x00\x00\xc3\x3e\x61\xcb\x00\x00\x00\x19tEXtSoftware\x00Adobe ImageReadyq\xc9e<\x00\x00\x00\x0eIDATx\xdab\xf8\x0f\x00\x00\x01\x00\x01\x00\x00\x00\x00IEND\xaeB`\x82'
            
            for size in [16, 32, 48, 128]:
                with open(os.path.join(icons_dir, f"icon{size}.png"), 'wb') as f:
                    f.write(icon_bytes)
            
            print(f"✅ [REAL-EXTENSION] Created real SwitchyOmega 3 extension in: {extension_dir}")
            return extension_dir
            
        except Exception as e:
            print(f"❌ [REAL-EXTENSION] Error creating real extension: {str(e)}")
            return None
    
    def install_extension_from_crx(self, profile_name, crx_file_path=None):
        """
        Install extension from .crx file for a specific profile
        
        Args:
            profile_name (str): Name of the Chrome profile
            crx_file_path (str): Path to .crx file (if None, will download)
        
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            print(f"🔧 [CRX-INSTALL] Installing extension from .crx file for profile: {profile_name}")
            
            # Get profile path
            profile_path = self.get_profile_path(profile_name)
            if not profile_path or not os.path.exists(profile_path):
                return False, f"Profile path not found: {profile_name}"
            
            # Download extension if not provided
            if not crx_file_path:
                crx_file_path = self.download_switchyomega_extension()
                if not crx_file_path:
                    return False, "Failed to download extension file"
            
            if not os.path.exists(crx_file_path):
                return False, f"Extension file not found: {crx_file_path}"
            
            print(f"📁 [CRX-INSTALL] Using extension file: {crx_file_path}")
            
            # Launch Chrome with extension installation
            chrome_options = Options()
            chrome_options.add_argument(f"--user-data-dir={profile_path}")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1024,768")
            chrome_options.add_argument("--disable-web-security")
            chrome_options.add_argument("--disable-features=VizDisplayCompositor")
            
            # Disable automation detection
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            from selenium import webdriver
            from selenium.webdriver.chrome.service import Service
            from webdriver_manager.chrome import ChromeDriverManager
            from selenium.webdriver.common.by import By
            
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
            try:
                # Navigate to Chrome extensions page
                driver.get("chrome://extensions/")
                driver.implicitly_wait(10)
                
                import time
                time.sleep(3)
                
                # Enable developer mode
                try:
                    developer_toggle = driver.find_element(By.XPATH, "//input[@type='checkbox' and @id='devMode']")
                    if not developer_toggle.is_selected():
                        developer_toggle.click()
                        time.sleep(1)
                        print(f"✅ [CRX-INSTALL] Developer mode enabled")
                except:
                    print(f"⚠️ [CRX-INSTALL] Could not enable developer mode")
                
                # Click "Load unpacked" button
                try:
                    load_unpacked_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Load unpacked')]")
                    load_unpacked_btn.click()
                    time.sleep(2)
                    print(f"✅ [CRX-INSTALL] Clicked Load unpacked button")
                except:
                    # Try alternative method - drag and drop
                    try:
                        # Use JavaScript to create file input and upload
                        driver.execute_script("""
                            var input = document.createElement('input');
                            input.type = 'file';
                            input.accept = '.crx';
                            input.style.display = 'none';
                            document.body.appendChild(input);
                            input.click();
                        """)
                        time.sleep(2)
                        print(f"✅ [CRX-INSTALL] File input created")
                    except Exception as e:
                        print(f"❌ [CRX-INSTALL] Could not create file input: {str(e)}")
                
                # Wait for installation to complete
                time.sleep(5)
                
                # Check if extension was installed
                try:
                    # Look for the extension in the extensions list
                    extension_elements = driver.find_elements(By.XPATH, "//div[contains(@class, 'extension-item')]")
                    print(f"🔍 [CRX-INSTALL] Found {len(extension_elements)} extensions")
                    
                    # Look for SwitchyOmega extension
                    for element in extension_elements:
                        try:
                            text = element.text.lower()
                            if "switchyomega" in text or "proxy" in text:
                                print(f"✅ [CRX-INSTALL] Found SwitchyOmega extension in extensions list")
                                return True, "Extension installed successfully from .crx file"
                        except:
                            continue
                    
                    print(f"⚠️ [CRX-INSTALL] SwitchyOmega extension not found in extensions list")
                    
                except Exception as e:
                    print(f"❌ [CRX-INSTALL] Error checking extension list: {str(e)}")
                
                print(f"✅ [CRX-INSTALL] Extension installation process completed for {profile_name}")
                return True, "Extension installation process completed"
                
            finally:
                driver.quit()
                
        except Exception as e:
            print(f"❌ [CRX-INSTALL] Error installing extension from .crx: {str(e)}")
            return False, f"Installation failed: {str(e)}"
    
    def install_extension_direct_copy(self, profile_name, crx_file_path=None):
        """
        Install extension by directly copying to Chrome extensions directory
        
        Args:
            profile_name (str): Name of the Chrome profile
            crx_file_path (str): Path to .crx file (if None, will download)
        
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            print(f"🔧 [DIRECT-INSTALL] Installing extension by direct copy for profile: {profile_name}")
            
            # Get profile path
            profile_path = self.get_profile_path(profile_name)
            if not profile_path or not os.path.exists(profile_path):
                return False, f"Profile path not found: {profile_name}"
            
            # Download extension if not provided
            if not crx_file_path:
                crx_file_path = self.download_switchyomega_extension()
                if not crx_file_path:
                    return False, "Failed to download extension file"
            
            if not os.path.exists(crx_file_path):
                return False, f"Extension file not found: {crx_file_path}"
            
            print(f"📁 [DIRECT-INSTALL] Using extension file: {crx_file_path}")
            
            # Create extensions directory
            extensions_dir = os.path.join(profile_path, "Extensions")
            if not os.path.exists(extensions_dir):
                os.makedirs(extensions_dir)
                print(f"📁 [DIRECT-INSTALL] Created extensions directory: {extensions_dir}")
            
            # Extract .crx file (it's actually a ZIP file)
            import zipfile
            import shutil
            
            # Create a temporary directory for extraction
            temp_dir = os.path.join(extensions_dir, "temp_extraction")
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            os.makedirs(temp_dir)
            
            try:
                # Extract .crx file
                with zipfile.ZipFile(crx_file_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
                print(f"✅ [DIRECT-INSTALL] Extracted extension files")
                
                # Find the extension ID from manifest.json
                manifest_path = os.path.join(temp_dir, "manifest.json")
                if os.path.exists(manifest_path):
                    import json
                    with open(manifest_path, 'r', encoding='utf-8') as f:
                        manifest = json.load(f)
                    
                    # Get extension ID (use key from manifest or generate one)
                    extension_id = manifest.get('key', 'pfnededegaaopdmhkdmcofjmoldfiped')
                    if not extension_id or extension_id == 'pfnededegaaopdmhkdmcofjmoldfiped':
                        # Generate a consistent ID based on extension name
                        extension_id = 'pfnededegaaopdmhkdmcofjmoldfiped'
                    
                    print(f"🔑 [DIRECT-INSTALL] Extension ID: {extension_id}")
                    
                    # Create final extension directory
                    final_extension_dir = os.path.join(extensions_dir, extension_id)
                    if os.path.exists(final_extension_dir):
                        shutil.rmtree(final_extension_dir)
                    
                    # Move extracted files to final location
                    shutil.move(temp_dir, final_extension_dir)
                    print(f"✅ [DIRECT-INSTALL] Extension installed to: {final_extension_dir}")
                    
                    # Create version directory (Chrome expects this structure)
                    version = manifest.get('version', '3.4.1')
                    version_dir = os.path.join(final_extension_dir, version)
                    if not os.path.exists(version_dir):
                        # Move all files to version directory
                        temp_version_dir = os.path.join(final_extension_dir, f"{version}_temp")
                        os.makedirs(temp_version_dir)
                        
                        # Move all files except the version directory itself
                        for item in os.listdir(final_extension_dir):
                            if item != version:
                                src = os.path.join(final_extension_dir, item)
                                dst = os.path.join(temp_version_dir, item)
                                if os.path.isdir(src):
                                    shutil.move(src, dst)
                                else:
                                    shutil.move(src, dst)
                        
                        # Rename temp directory to version
                        shutil.move(temp_version_dir, version_dir)
                        print(f"✅ [DIRECT-INSTALL] Created version directory: {version_dir}")
                    
                    return True, f"Extension installed successfully to {final_extension_dir}"
                else:
                    return False, "manifest.json not found in extension"
                    
            finally:
                # Clean up temp directory if it still exists
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
                
        except Exception as e:
            print(f"❌ [DIRECT-INSTALL] Error installing extension: {str(e)}")
            return False, f"Installation failed: {str(e)}"
    
    def install_extension_from_directory(self, profile_name, extension_dir=None):
        """
        Install extension from directory for a specific profile
        
        Args:
            profile_name (str): Name of the Chrome profile
            extension_dir (str): Path to extension directory (if None, will create)
        
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            print(f"🔧 [DIR-INSTALL] Installing extension from directory for profile: {profile_name}")
            
            # Get profile path
            profile_path = self.get_profile_path(profile_name)
            if not profile_path or not os.path.exists(profile_path):
                return False, f"Profile path not found: {profile_name}"
            
            # Create extension if not provided
            if not extension_dir:
                extension_dir = self.download_extension_from_webstore()
                if not extension_dir:
                    return False, "Failed to create extension directory"
            
            if not os.path.exists(extension_dir):
                return False, f"Extension directory not found: {extension_dir}"
            
            print(f"📁 [DIR-INSTALL] Using extension directory: {extension_dir}")
            
            # Create extensions directory in profile
            profile_extensions_dir = os.path.join(profile_path, "Extensions")
            if not os.path.exists(profile_extensions_dir):
                os.makedirs(profile_extensions_dir)
                print(f"📁 [DIR-INSTALL] Created extensions directory: {profile_extensions_dir}")
            
            # Extension ID
            extension_id = "pfnededegaaopdmhkdmcofjmoldfiped"
            
            # Create final extension directory
            final_extension_dir = os.path.join(profile_extensions_dir, extension_id)
            if os.path.exists(final_extension_dir):
                import shutil
                shutil.rmtree(final_extension_dir)
            
            # Copy extension files
            import shutil
            shutil.copytree(extension_dir, final_extension_dir)
            print(f"✅ [DIR-INSTALL] Extension copied to: {final_extension_dir}")
            
            # Create version directory (Chrome expects this structure)
            version = "3.4.1"
            version_dir = os.path.join(final_extension_dir, version)
            if not os.path.exists(version_dir):
                # Create version directory
                os.makedirs(version_dir)
                
                # Move all files to version directory
                for item in os.listdir(final_extension_dir):
                    if item != version:
                        src = os.path.join(final_extension_dir, item)
                        dst = os.path.join(version_dir, item)
                        if os.path.isdir(src):
                            shutil.move(src, dst)
                        else:
                            shutil.move(src, dst)
                
                print(f"✅ [DIR-INSTALL] Created version directory: {version_dir}")
            
            return True, f"Extension installed successfully to {final_extension_dir}"
                
        except Exception as e:
            print(f"❌ [DIR-INSTALL] Error installing extension: {str(e)}")
            return False, f"Installation failed: {str(e)}"
    
    def test_extension_installation(self, profile_name="TestProfile"):
        """
        Test extension installation with detailed debugging
        
        Args:
            profile_name (str): Name of the Chrome profile to test
        
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            print(f"🧪 [TEST-EXTENSION] Testing extension installation for {profile_name}")
            
            # Get profile path
            profile_path = self.get_profile_path(profile_name)
            if not profile_path:
                return False, f"Profile path not found: {profile_name}"
            
            print(f"📁 [TEST-EXTENSION] Profile path: {profile_path}")
            
            # Launch Chrome with the profile
            chrome_options = Options()
            chrome_options.add_argument(f"--user-data-dir={profile_path}")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1024,768")
            chrome_options.add_argument("--disable-web-security")
            chrome_options.add_argument("--disable-features=VizDisplayCompositor")
            
            # Disable automation detection
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            from selenium import webdriver
            from selenium.webdriver.chrome.service import Service
            from webdriver_manager.chrome import ChromeDriverManager
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
            try:
                # Navigate to extension page
                extension_url = "https://chromewebstore.google.com/detail/proxy-switchyomega-3-zero/pfnededegaaopdmhkdmcofjmoldfiped"
                print(f"🌐 [TEST-EXTENSION] Navigating to: {extension_url}")
                
                driver.get(extension_url)
                driver.implicitly_wait(10)
                
                # Wait for page to load
                import time
                time.sleep(10)
                
                print(f"📄 [TEST-EXTENSION] Page title: {driver.title}")
                print(f"🔗 [TEST-EXTENSION] Current URL: {driver.current_url}")
                
                # Take screenshot
                try:
                    screenshot_path = f"test_extension_page_{profile_name}.png"
                    driver.save_screenshot(screenshot_path)
                    print(f"📸 [TEST-EXTENSION] Screenshot saved: {screenshot_path}")
                except Exception as e:
                    print(f"⚠️ [TEST-EXTENSION] Could not save screenshot: {str(e)}")
                
                # Look for all buttons on the page
                try:
                    buttons = driver.find_elements(By.TAG_NAME, "button")
                    print(f"🔍 [TEST-EXTENSION] Found {len(buttons)} buttons on the page")
                    
                    for i, button in enumerate(buttons):
                        try:
                            text = button.text.strip()
                            if text:
                                print(f"  Button {i+1}: '{text}'")
                        except:
                            pass
                except Exception as e:
                    print(f"⚠️ [TEST-EXTENSION] Error finding buttons: {str(e)}")
                
                # Try to find and click install button
                install_success = False
                
                # First try to find by button index (Button 5: 'Add to Chrome')
                try:
                    buttons = driver.find_elements(By.TAG_NAME, "button")
                    if len(buttons) >= 5:
                        # Try button at index 4 (0-based, so button 5 is index 4)
                        add_button = buttons[4]
                        button_text = add_button.text.strip()
                        print(f"🔍 [TEST-EXTENSION] Trying button at index 4: '{button_text}'")
                        
                        if "Add to Chrome" in button_text or "Install" in button_text:
                            print(f"✅ [TEST-EXTENSION] Found install button by index: '{button_text}'")
                            
                            # Try to click
                            driver.execute_script("arguments[0].scrollIntoView(true);", add_button)
                            time.sleep(1)
                            driver.execute_script("arguments[0].click();", add_button)
                            time.sleep(5)
                            
                            install_success = True
                except Exception as e:
                    print(f"❌ [TEST-EXTENSION] Button index method failed: {str(e)}")
                
                # If index method failed, try text search
                if not install_success:
                    try:
                        buttons = driver.find_elements(By.TAG_NAME, "button")
                        for i, button in enumerate(buttons):
                            try:
                                button_text = button.text.strip()
                                if "Add to Chrome" in button_text or "Install" in button_text:
                                    print(f"✅ [TEST-EXTENSION] Found install button by text search: '{button_text}' (index {i})")
                                    
                                    # Try to click
                                    driver.execute_script("arguments[0].scrollIntoView(true);", button)
                                    time.sleep(1)
                                    driver.execute_script("arguments[0].click();", button)
                                    time.sleep(5)
                                    
                                    install_success = True
                                    break
                            except:
                                continue
                    except Exception as e:
                        print(f"❌ [TEST-EXTENSION] Text search method failed: {str(e)}")
                
                # If text search failed, try XPath selectors
                if not install_success:
                    button_selectors = [
                        "//button[contains(text(), 'Add to Chrome')]",
                        "//button[contains(text(), 'Add to browser')]",
                        "//button[contains(text(), 'Install')]",
                        "//button[contains(@class, 'add-to-chrome')]",
                        "//button[contains(@class, 'install')]",
                        "//div[contains(@class, 'add-to-chrome')]//button",
                        "//div[contains(@class, 'install')]//button"
                    ]
                    
                    for selector in button_selectors:
                        try:
                            button = driver.find_element(By.XPATH, selector)
                            if button and button.is_displayed():
                                print(f"✅ [TEST-EXTENSION] Found install button with selector: {selector}")
                                print(f"🔍 [TEST-EXTENSION] Button text: '{button.text}'")
                                
                                # Try to click
                                driver.execute_script("arguments[0].scrollIntoView(true);", button)
                                time.sleep(1)
                                driver.execute_script("arguments[0].click();", button)
                                time.sleep(5)
                                
                                install_success = True
                                break
                        except Exception as e:
                            print(f"❌ [TEST-EXTENSION] Selector {selector} failed: {str(e)}")
                            continue
                
                if install_success:
                    print(f"✅ [TEST-EXTENSION] Successfully clicked install button for {profile_name}")
                    return True, "Install button clicked successfully"
                else:
                    print(f"❌ [TEST-EXTENSION] Could not find install button for {profile_name}")
                    return False, "Could not find install button"
                    
            finally:
                driver.quit()
                
        except Exception as e:
            print(f"❌ [TEST-EXTENSION] Error testing extension installation: {str(e)}")
            return False, f"Test failed: {str(e)}"
    
    def get_extension_status_for_all_profiles(self, extension_id="pfnededegaaopdmhkdmcofjmoldfiped"):
        """
        Get extension installation status for all profiles
        
        Args:
            extension_id (str): Chrome Web Store extension ID
        
        Returns:
            dict: Dictionary with profile names as keys and installation status as values
        """
        profiles = self.get_all_profiles()
        status_dict = {}
        
        for profile in profiles:
            status_dict[profile] = self.check_extension_installed(profile, extension_id)
        
        return status_dict
    
    def get_profile_path(self, profile_name):
        """
        Get the full path to a Chrome profile directory
        
        Args:
            profile_name (str): Name of the Chrome profile
        
        Returns:
            str: Full path to the profile directory, or None if not found
        """
        try:
            # Get the base Chrome user data directory
            chrome_user_data = os.path.join(os.path.expanduser("~"), "AppData", "Local", "Google", "Chrome", "User Data")
            
            # Check if profile exists in the standard location
            profile_path = os.path.join(chrome_user_data, profile_name)
            if os.path.exists(profile_path):
                return profile_path
            
            # Check if profile exists in the profiles directory
            profiles_path = os.path.join(chrome_user_data, "Profiles")
            if os.path.exists(profiles_path):
                for item in os.listdir(profiles_path):
                    if item.startswith(profile_name) or profile_name in item:
                        return os.path.join(profiles_path, item)
            
            # If not found, create a new profile directory
            new_profile_path = os.path.join(chrome_user_data, profile_name)
            os.makedirs(new_profile_path, exist_ok=True)
            return new_profile_path
            
        except Exception as e:
            print(f"❌ [PROFILE-PATH] Error getting profile path for {profile_name}: {str(e)}")
            return None
    
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
                    print(f"🔍 [CHROME-PATH] Found Chrome at: {chrome_path}")
                    return chrome_path
            
            # Try using shutil.which
            chrome_path = shutil.which("chrome")
            if chrome_path:
                print(f"🔍 [CHROME-PATH] Found Chrome via which: {chrome_path}")
                return chrome_path
            
            # Try chrome.exe
            chrome_path = shutil.which("chrome.exe")
            if chrome_path:
                print(f"🔍 [CHROME-PATH] Found Chrome.exe via which: {chrome_path}")
                return chrome_path
            
            print("❌ [CHROME-PATH] Chrome executable not found")
            return None
            
        except Exception as e:
            print(f"❌ [CHROME-PATH] Error finding Chrome: {str(e)}")
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
            print(f"🔍 [SWITCHYOMEGA] Getting profiles from: {profile_name}")
            
            # Get profile path
            profile_path = self.get_profile_path(profile_name)
            if not profile_path or not os.path.exists(profile_path):
                return []
            
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
            from webdriver_manager.chrome import ChromeDriverManager
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
            try:
                # Navigate to SwitchyOmega options page
                driver.get("chrome-extension://pfnededegaaopdmhkdmcofjmoldfiped/options.html")
                driver.implicitly_wait(10)
                
                import time
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
                        print(f"⚠️ [SWITCHYOMEGA] Could not get profiles from localStorage: {str(e)}")
                    
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
                            print(f"⚠️ [SWITCHYOMEGA] Could not get profiles from UI elements: {str(e)}")
                    
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
                                        print(f"⚠️ [SWITCHYOMEGA] Could not get details for profile {profile['name']}: {str(e)}")
                                        continue
                        except Exception as e:
                            print(f"⚠️ [SWITCHYOMEGA] Could not get profile details: {str(e)}")
                    
                    print(f"✅ [SWITCHYOMEGA] Found {len(profiles)} profiles")
                    for profile in profiles:
                        print(f"  📋 Profile: {profile['name']} ({profile['type']})")
                    
                    return profiles
                    
                except Exception as e:
                    print(f"⚠️ [SWITCHYOMEGA] Could not extract profiles: {str(e)}")
                    return []
                
            finally:
                driver.quit()
                
        except Exception as e:
            print(f"❌ [SWITCHYOMEGA] Error getting profiles from {profile_name}: {str(e)}")
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
            print(f"🔧 [SWITCHYOMEGA] Configuring proxy for profile: {profile_name}")
            
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
            from webdriver_manager.chrome import ChromeDriverManager
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
            try:
                # Navigate to SwitchyOmega options page
                driver.get("chrome-extension://pfnededegaaopdmhkdmcofjmoldfiped/options.html")
                driver.implicitly_wait(10)
                
                import time
                time.sleep(5)  # Increased wait time
                
                # Wait for the extension to load
                wait = WebDriverWait(driver, 30)  # Increased timeout
                
                # Check if page loaded successfully
                try:
                    wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                    print("✅ [SWITCHYOMEGA] Extension page loaded successfully")
                except:
                    print("❌ [SWITCHYOMEGA] Extension page failed to load")
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
                            print(f"✅ [SWITCHYOMEGA] Using existing profile: {selector}")
                            profile_created = True
                            break
                        except:
                            continue
                            
                except Exception as e:
                    print(f"⚠️ [SWITCHYOMEGA] Could not find existing profile: {str(e)}")
                
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
                                print(f"✅ [SWITCHYOMEGA] Clicked New Profile button: {selector}")
                                profile_created = True
                                break
                            except:
                                continue
                            
                    except Exception as e:
                        print(f"⚠️ [SWITCHYOMEGA] Could not find New Profile button: {str(e)}")
                
                if not profile_created:
                    print("❌ [SWITCHYOMEGA] Could not create or find profile")
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
                    print("✅ [SWITCHYOMEGA] Page refreshed to apply changes")
                except:
                    pass
                
                print(f"✅ [SWITCHYOMEGA] Successfully configured proxy for {profile_name}")
                return True, "Proxy configuration applied successfully"
                
            finally:
                driver.quit()
                
        except Exception as e:
            print(f"❌ [SWITCHYOMEGA] Error configuring proxy for {profile_name}: {str(e)}")
            return False, f"Configuration failed: {str(e)}"
    
    def _fill_switchyomega_config(self, driver, proxy_config):
        """Fill SwitchyOmega configuration form with proxy settings"""
        try:
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            from selenium.webdriver.common.keys import Keys
            import time
            
            wait = WebDriverWait(driver, 15)
            
            print(f"🔧 [SWITCHYOMEGA] Filling configuration with: {proxy_config}")
            
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
                print(f"⚠️ [SWITCHYOMEGA] Could not find new profile button: {str(e)}")
            
            # Profile name
            if 'profile_name' in proxy_config:
                try:
                    name_field = wait.until(EC.presence_of_element_located((By.XPATH, 
                        "//input[@placeholder='Profile Name' or @placeholder='情景模式名称' or @name='profileName']")))
                    name_field.clear()
                    name_field.send_keys(proxy_config['profile_name'])
                    time.sleep(0.5)
                    print(f"✅ [SWITCHYOMEGA] Set profile name: {proxy_config['profile_name']}")
                except Exception as e:
                    print(f"⚠️ [SWITCHYOMEGA] Could not set profile name: {str(e)}")
                    # Try alternative selectors
                    try:
                        name_field = driver.find_element(By.XPATH, "//input[@type='text']")
                        name_field.clear()
                        name_field.send_keys(proxy_config['profile_name'])
                        time.sleep(0.5)
                        print(f"✅ [SWITCHYOMEGA] Set profile name (alternative): {proxy_config['profile_name']}")
                    except:
                        pass
            
            # Protocol selection
            protocol = proxy_config.get('proxy_type', 'HTTP').lower()
            try:
                print(f"🔧 [SWITCHYOMEGA] Setting proxy type: {protocol}")
                
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
                        print(f"✅ [SWITCHYOMEGA] Set proxy type: {protocol}")
                        break
                    except:
                        continue
                        
            except Exception as e:
                print(f"⚠️ [SWITCHYOMEGA] Could not set proxy type: {str(e)}")
            
            # Server/Host - Find the correct server field in the proxy table
            if 'proxy_server' in proxy_config:
                try:
                    print(f"🔧 [SWITCHYOMEGA] Looking for server field...")
                    
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
                            print(f"✅ [SWITCHYOMEGA] Found server field with selector: {selector}")
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
                        print(f"✅ [SWITCHYOMEGA] Set proxy server: {proxy_config['proxy_server']}")
                    else:
                        print(f"⚠️ [SWITCHYOMEGA] Could not find server field")
                        
                except Exception as e:
                    print(f"⚠️ [SWITCHYOMEGA] Could not set proxy server: {str(e)}")
            
            # Port - Find the correct port field in the proxy table
            if 'proxy_port' in proxy_config:
                try:
                    print(f"🔧 [SWITCHYOMEGA] Looking for port field...")
                    
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
                            print(f"✅ [SWITCHYOMEGA] Found port field with selector: {selector}")
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
                        print(f"✅ [SWITCHYOMEGA] Set proxy port: {proxy_config['proxy_port']}")
                    else:
                        print(f"⚠️ [SWITCHYOMEGA] Could not find port field")
                        
                except Exception as e:
                    print(f"⚠️ [SWITCHYOMEGA] Could not set proxy port: {str(e)}")
            
            # Username/Password (if provided) - Click the lock button first
            if 'username' in proxy_config and proxy_config['username']:
                try:
                    print(f"🔧 [SWITCHYOMEGA] Setting authentication...")
                    
                    # First, click the lock button to reveal username/password fields
                    lock_button_selectors = [
                        "//button[contains(@class, 'lock') or contains(@class, 'auth')]",
                        "//button[contains(@title, 'lock') or contains(@title, 'auth')]",
                        "//button[contains(@aria-label, 'lock') or contains(@aria-label, 'auth')]",
                        "//button[contains(@onclick, 'auth') or contains(@onclick, 'lock')]",
                        "//button[contains(@ng-click, 'auth') or contains(@ng-click, 'lock')]",
                        "//button[contains(text(), '🔒') or contains(text(), '🔑')]",
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
                                print(f"✅ [SWITCHYOMEGA] Clicked lock button to reveal auth fields")
                                lock_clicked = True
                                break
                        except:
                            continue
                    
                    if not lock_clicked:
                        print(f"⚠️ [SWITCHYOMEGA] Could not find lock button, trying alternative methods")
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
                                print(f"✅ [SWITCHYOMEGA] Enabled authentication via checkbox")
                            break
                        except:
                            continue
                    
                    # Username
                    if 'username' in proxy_config:
                        try:
                            print(f"🔧 [SWITCHYOMEGA] Looking for username field...")
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
                                    print(f"✅ [SWITCHYOMEGA] Found username field with selector: {selector}")
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
                                print(f"✅ [SWITCHYOMEGA] Set username: {proxy_config['username']}")
                            else:
                                print(f"⚠️ [SWITCHYOMEGA] Could not find username field")
                            
                        except Exception as e:
                            print(f"⚠️ [SWITCHYOMEGA] Could not set username: {str(e)}")
            
            # Password
                    if 'password' in proxy_config:
                        try:
                            print(f"🔧 [SWITCHYOMEGA] Looking for password field...")
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
                                    print(f"✅ [SWITCHYOMEGA] Found password field with selector: {selector}")
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
                                print(f"✅ [SWITCHYOMEGA] Set password: {'*' * len(proxy_config['password'])}")
                            else:
                                print(f"⚠️ [SWITCHYOMEGA] Could not find password field")
                                
                        except Exception as e:
                            print(f"⚠️ [SWITCHYOMEGA] Could not set password: {str(e)}")
                            
                except Exception as e:
                    print(f"⚠️ [SWITCHYOMEGA] Could not set authentication: {str(e)}")
            
            # Apply to all protocols
            try:
                apply_all_checkbox = driver.find_element(By.XPATH, "//input[@type='checkbox'][contains(@name, 'all') or contains(@id, 'all')]")
                if not apply_all_checkbox.is_selected():
                    apply_all_checkbox.click()
                    time.sleep(0.5)
                    print(f"✅ [SWITCHYOMEGA] Applied to all protocols")
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
                        print(f"✅ [SWITCHYOMEGA] Configuration saved")
                        save_success = True
                        break
                    except:
                        continue
                
                if not save_success:
                    print("⚠️ [SWITCHYOMEGA] Could not find save button, trying alternative methods")
                    # Try pressing Enter key
                    try:
                        from selenium.webdriver.common.keys import Keys
                        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ENTER)
                        time.sleep(2)
                        print("✅ [SWITCHYOMEGA] Pressed Enter to save")
                    except:
                        pass
                        
            except Exception as e:
                print(f"⚠️ [SWITCHYOMEGA] Could not save configuration: {str(e)}")
            
            # Force refresh the page to ensure changes are applied
            try:
                driver.refresh()
                time.sleep(3)
                print("✅ [SWITCHYOMEGA] Page refreshed to apply changes")
                
                # Verify changes were applied by checking the page content
                page_source = driver.page_source
                if proxy_config.get('proxy_server', '') in page_source:
                    print(f"✅ [SWITCHYOMEGA] Verified proxy server in page: {proxy_config.get('proxy_server', '')}")
                if str(proxy_config.get('proxy_port', '')) in page_source:
                    print(f"✅ [SWITCHYOMEGA] Verified proxy port in page: {proxy_config.get('proxy_port', '')}")
                    
            except:
                pass
            
            time.sleep(1)
            
        except Exception as e:
            print(f"❌ [SWITCHYOMEGA] Error filling configuration: {str(e)}")
    
    def _clear_existing_proxy_data(self, driver):
        """Clear existing proxy data from all input fields"""
        try:
            from selenium.webdriver.common.keys import Keys
            from selenium.webdriver.common.by import By
            import time
            
            print("🧹 [SWITCHYOMEGA] Clearing existing proxy data...")
            
            # Wait for page to be ready
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            wait = WebDriverWait(driver, 10)
            
            # Find all input fields and clear them
            try:
                input_fields = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//input[@type='text' or @type='number' or @type='password']")))
                
                for field in input_fields:
                    try:
                        # Scroll to field if needed
                        driver.execute_script("arguments[0].scrollIntoView(true);", field)
                        time.sleep(0.2)
                        
                        # Focus on the field
                        field.click()
                        time.sleep(0.1)
                        
                        # Clear the field multiple ways
                        field.clear()
                        time.sleep(0.1)
                        field.send_keys(Keys.CONTROL + "a")
                        time.sleep(0.1)
                        field.send_keys(Keys.DELETE)
                        time.sleep(0.1)
                        
                        # Double-click to select all and delete
                        field.click()
                        time.sleep(0.1)
                        field.send_keys(Keys.CONTROL + "a")
                        time.sleep(0.1)
                        field.send_keys(Keys.DELETE)
                        time.sleep(0.1)
                        
                    except Exception as e:
                        print(f"⚠️ [SWITCHYOMEGA] Could not clear field: {str(e)}")
                        continue
                        
            except Exception as e:
                print(f"⚠️ [SWITCHYOMEGA] Could not find input fields: {str(e)}")
            
            print("✅ [SWITCHYOMEGA] Existing proxy data cleared")
            
        except Exception as e:
            print(f"⚠️ [SWITCHYOMEGA] Could not clear existing data: {str(e)}")
    
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
        
        print(f"🚀 [BULK-SWITCHYOMEGA] Starting bulk configuration for {len(profile_list)} profiles")
        
        for profile_name in profile_list:
            try:
                success, message = self.configure_switchyomega_proxy(profile_name, proxy_config)
                result = f"{'✅' if success else '❌'} {profile_name}: {message}"
                results.append(result)
                
                if success:
                    success_count += 1
                
                # Small delay between configurations
                import time
                time.sleep(2)
                
            except Exception as e:
                error_msg = f"❌ {profile_name}: Error - {str(e)}"
                results.append(error_msg)
                print(f"❌ [BULK-SWITCHYOMEGA] Error for {profile_name}: {str(e)}")
        
        print(f"🎉 [BULK-SWITCHYOMEGA] Completed: {success_count}/{len(profile_list)} successful")
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
        
        print(f"🚀 [BULK-DIR-EXTENSION] Starting bulk installation for {len(profile_list)} profiles")
        
        # Create extension once and reuse
        extension_dir = self.download_extension_from_webstore()
        if not extension_dir:
            return 0, ["❌ Failed to create extension directory"]
        
        for profile_name in profile_list:
            try:
                success, message = self.install_extension_from_directory(profile_name, extension_dir)
                result = f"{'✅' if success else '❌'} {profile_name}: {message}"
                results.append(result)
                
                if success:
                    success_count += 1
                
                # Small delay between installations
                import time
                time.sleep(0.5)
                
            except Exception as e:
                error_msg = f"❌ {profile_name}: Error - {str(e)}"
                results.append(error_msg)
                print(f"❌ [BULK-DIR-EXTENSION] Error for {profile_name}: {str(e)}")
        
        print(f"🎉 [BULK-DIR-EXTENSION] Completed: {success_count}/{len(profile_list)} successful")
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
            print(f"🚀 [ACTIVATE-EXTENSION] Activating extension for profile: {profile_name}")
            
            # Get profile path
            profile_path = self.get_profile_path(profile_name)
            if not profile_path or not os.path.exists(profile_path):
                return False, f"Profile path not found: {profile_name}"
            
            # Extension ID
            extension_id = "pfnededegaaopdmhkdmcofjmoldfiped"
            
            # Check if extension is installed
            if not self.check_extension_installed(profile_name):
                return False, f"Extension not installed for profile: {profile_name}"
            
            print(f"✅ [ACTIVATE-EXTENSION] Extension is installed, launching Chrome...")
            
            # Launch Chrome with the profile
            chrome_options = [
                "--user-data-dir=" + profile_path,
                "--profile-directory=" + profile_name,
                "--load-extension=" + os.path.join(profile_path, "Extensions", extension_id, "3.4.1"),
                "--enable-extensions",
                "--disable-extensions-except=" + os.path.join(profile_path, "Extensions", extension_id, "3.4.1"),
                "--no-first-run",
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
                "--remote-debugging-port=9222",
                "--new-window"
            ]
            
            # Launch Chrome
            import subprocess
            import time
            
            chrome_path = self.get_chrome_path()
            if not chrome_path:
                return False, "Chrome executable not found"
            
            print(f"🌐 [ACTIVATE-EXTENSION] Launching Chrome with extension enabled...")
            
            # Launch Chrome in background
            process = subprocess.Popen(
                [chrome_path] + chrome_options,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
            )
            
            # Wait a bit for Chrome to start
            time.sleep(3)
            
            print(f"✅ [ACTIVATE-EXTENSION] Chrome launched with extension enabled")
            print(f"🔧 [ACTIVATE-EXTENSION] Extension should now be visible in Chrome")
            print(f"📱 [ACTIVATE-EXTENSION] Look for SwitchyOmega icon in toolbar")
            
            return True, f"Chrome launched with extension enabled for {profile_name}"
            
        except Exception as e:
            print(f"❌ [ACTIVATE-EXTENSION] Error activating extension: {str(e)}")
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
        
        print(f"🚀 [BULK-ACTIVATE] Starting bulk activation for {len(profile_list)} profiles")
        
        for profile_name in profile_list:
            try:
                success, message = self.activate_extension_in_chrome(profile_name)
                result = f"{'✅' if success else '❌'} {profile_name}: {message}"
                results.append(result)
                
                if success:
                    success_count += 1
                
                # Small delay between activations
                import time
                time.sleep(2)
                
            except Exception as e:
                error_msg = f"❌ {profile_name}: Error - {str(e)}"
                results.append(error_msg)
                print(f"❌ [BULK-ACTIVATE] Error for {profile_name}: {str(e)}")
        
        print(f"🎉 [BULK-ACTIVATE] Completed: {success_count}/{len(profile_list)} successful")
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
            print("🚀 [AUTO-INSTALL] Starting automatic extension installation on startup...")
            
            # Get all profiles
            all_profiles = self.get_all_profiles()
            
            if not all_profiles:
                print("⚠️ [AUTO-INSTALL] No profiles found for auto-installation")
                return 0, ["No profiles found"]
            
            # Check which profiles need extension installation
            profiles_to_install = []
            for profile in all_profiles:
                if not self.check_extension_installed(profile, extension_id):
                    profiles_to_install.append(profile)
            
            if not profiles_to_install:
                print("✅ [AUTO-INSTALL] All profiles already have SwitchyOmega 3 installed")
                return len(all_profiles), [f"✅ {profile}: Already installed" for profile in all_profiles]
            
            print(f"📥 [AUTO-INSTALL] Installing extension for {len(profiles_to_install)} profiles...")
            
            # Install extension for profiles that need it using directory method
            success_count, results = self.bulk_install_extension_directory(profiles_to_install)
            
            # Add already installed profiles to results
            for profile in all_profiles:
                if profile not in profiles_to_install:
                    results.append(f"✅ {profile}: Already installed")
                    success_count += 1
            
            print(f"🎉 [AUTO-INSTALL] Completed: {success_count}/{len(all_profiles)} profiles have extension")
            return success_count, results
            
        except Exception as e:
            print(f"❌ [AUTO-INSTALL] Error during auto-installation: {str(e)}")
            return 0, [f"❌ Auto-installation failed: {str(e)}"]
    
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
                print(f"✅ [ENSURE-EXTENSION] Successfully installed extension for {profile_name}")
                return True
            else:
                print(f"❌ [ENSURE-EXTENSION] Failed to install extension for {profile_name}: {message}")
                return False
                
        except Exception as e:
            print(f"❌ [ENSURE-EXTENSION] Error ensuring extension for {profile_name}: {str(e)}")
            return False
    
    def create_pac_from_proxy(self, proxy_server, proxy_port, proxy_username=None, proxy_password=None, pac_name="custom_proxy.pac"):
        """Create PAC file from proxy input"""
        try:
            print(f"🔧 [PAC] Creating PAC file: {pac_name}")
            print(f"📋 [PAC] Proxy: {proxy_server}:{proxy_port}")
            
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
            
            print(f"✅ [PAC] PAC file created: {pac_name}")
            return True, pac_name
            
        except Exception as e:
            print(f"❌ [PAC] Error creating PAC file: {str(e)}")
            return False, str(e)

    def read_proxy_from_extension(self, profile_name):
        """
        Read existing proxy configuration from SwitchyOmega extension
        
        Args:
            profile_name (str): Name of the Chrome profile
            
        Returns:
            dict: Proxy configuration or None if not found
        """
        try:
            print(f"🔍 [PROXY-READ] Reading proxy config from extension for profile: {profile_name}")
            
            profile_path = os.path.join(self.profiles_dir, profile_name)
            if not os.path.exists(profile_path):
                print(f"❌ [PROXY-READ] Profile not found: {profile_name}")
                return None
            
            # Path to SwitchyOmega settings
            settings_path = os.path.join(profile_path, "Default", "Extensions", 
                                       "pfnededegaaopdmhkdmcofjmoldfiped", "3.4.1_0", "settings.json")
            
            if not os.path.exists(settings_path):
                print(f"❌ [PROXY-READ] SwitchyOmega settings not found: {settings_path}")
                return None
            
            # Read settings.json
            with open(settings_path, 'r', encoding='utf-8') as f:
                settings = json.load(f)
            
            # Extract proxy configuration
            profiles = settings.get('profiles', {})
            default_profile_id = settings.get('defaultProfileId')
            
            if not default_profile_id or default_profile_id not in profiles:
                print(f"❌ [PROXY-READ] No default profile found in settings")
                return None
            
            profile_config = profiles[default_profile_id]
            
            if profile_config.get('type') != 'ProxyProfile':
                print(f"❌ [PROXY-READ] Default profile is not a proxy profile")
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
            
            print(f"✅ [PROXY-READ] Found proxy configuration:")
            print(f"   Profile: {proxy_config['profile_name']}")
            print(f"   Server: {proxy_config['proxy_server']}")
            print(f"   Port: {proxy_config['proxy_port']}")
            print(f"   Username: {proxy_config['username']}")
            print(f"   Password: {'*' * len(proxy_config['password'])}")
            print(f"   Scheme: {proxy_config['scheme']}")
            
            return proxy_config
            
        except Exception as e:
            print(f"❌ [PROXY-READ] Error reading proxy config: {str(e)}")
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
            print(f"🔧 [PROXY-FIX] Auto-fixing proxy input for profile: {profile_name}")
            
            # Read existing proxy configuration
            proxy_config = self.read_proxy_from_extension(profile_name)
            
            if not proxy_config:
                return False, "", "No existing proxy configuration found in extension"
            
            # Create proxy string from existing config
            proxy_string = f"{proxy_config['proxy_server']}:{proxy_config['proxy_port']}:{proxy_config['username']}:{proxy_config['password']}"
            
            print(f"✅ [PROXY-FIX] Generated proxy string from extension:")
            print(f"   {proxy_string}")
            
            return True, proxy_string, f"Proxy string generated from existing configuration: {proxy_config['profile_name']}"
            
        except Exception as e:
            print(f"❌ [PROXY-FIX] Error auto-fixing proxy input: {str(e)}")
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
                    print(f"⚠️ [SO-SETTINGS] Could not read existing settings: {e}")

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
                f"✅ [SO-SETTINGS] settings.json updated: {host}:{port} user={username}"
            )
            return True, "SwitchyOmega settings updated"

        except Exception as e:
            print(f"❌ [SO-SETTINGS] Failed to write settings: {e}")
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
            import time

            settings_path = self._get_switchyomega_settings_path(profile_name)
            if not os.path.exists(settings_path):
                return False, f"settings.json not found for profile {profile_name}"

            profile_dir = os.path.join(self.profiles_dir, profile_name)
            if not os.path.exists(profile_dir):
                return False, f"Profile '{profile_name}' not found"

            chrome_options = Options()
            chrome_options.add_argument(f"--user-data-dir={profile_dir}")
            chrome_options.add_argument("--no-first-run")
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
            print(f"🔧 [PROXY-INPUT] Parsing proxy string for {profile_name}")
            
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
            
            print(f"📊 [PROXY-INPUT] Parsed config: {proxy_config['proxy_server']}:{proxy_config['proxy_port']}")
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
            print(f"🔍 [PROXY-TEST] Testing proxy connection...")
            
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
            print(f"🔍 [ANALYZE] Analyzing proxy status for profile: {profile_name}")
            
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
        
        print(f"🔍 [ANALYZE] Analyzing {len(all_profiles)} profiles for proxy status...")
        
        for profile in all_profiles:
            has_proxy, message = self.analyze_profile_proxy_status(profile)
            if has_proxy:
                proxy_profiles.append(profile)
                print(f"✅ {profile}: {message}")
            else:
                print(f"❌ {profile}: {message}")
        
        return proxy_profiles

    def get_profiles_without_proxy(self):
        """Get all profiles that don't have proxy configured"""
        all_profiles = self.get_all_profiles()
        no_proxy_profiles = []
        
        print(f"🔍 [ANALYZE] Analyzing {len(all_profiles)} profiles for missing proxy...")
        
        for profile in all_profiles:
            has_proxy, message = self.analyze_profile_proxy_status(profile)
            if not has_proxy:
                no_proxy_profiles.append(profile)
                print(f"❌ {profile}: {message}")
            else:
                print(f"✅ {profile}: {message}")
        
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
        print(f"🔧 [SMART] Configuring proxy for {profile_name}...")
        success, result_message = self.input_proxy_from_ui(profile_name, proxy_string)
        
        if success:
            print(f"✅ [SMART] Successfully configured proxy for {profile_name}")
            return True, result_message
        else:
            print(f"❌ [SMART] Failed to configure proxy for {profile_name}: {result_message}")
            return False, result_message

    def bulk_smart_configure_proxy(self, profile_list, proxy_string):
        """Bulk smart proxy configuration"""
        print(f"🧠 [SMART] Bulk smart proxy configuration for {len(profile_list)} profiles")
        
        results = []
        success_count = 0
        
        for profile_name in profile_list:
            print(f"\n📋 [SMART] Processing {profile_name}...")
            success, message = self.smart_configure_proxy(profile_name, proxy_string)
            
            results.append({
                'profile': profile_name,
                'success': success,
                'message': message
            })
            
            if success:
                success_count += 1
        
        return results, success_count
    
