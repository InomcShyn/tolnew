import os
import json
import time

def set_profile_proxy(manager, profile_name, proxy_string):
    """Set proxy for a profile - Lưu vào profile_settings.json VÀ Chrome Preferences (không qua extension)"""
    try:
        profile_path = os.path.join(manager.profiles_dir, profile_name)
        settings_path = os.path.join(profile_path, 'profile_settings.json')
        data = {}
        if os.path.exists(settings_path):
            with open(settings_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        # Set proxy
        data.setdefault('network', {})['proxy'] = proxy_string
        # Save settings
        with open(settings_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"[PROXY] [PROFILE-SETTINGS] Saved proxy to profile_settings.json for {profile_name}")
        
        # ✅ Set proxy trực tiếp vào Chrome Preferences (không qua extension)
        if proxy_string and proxy_string.lower() != 'null':
            try:
                set_proxy_to_chrome_preferences(manager, profile_name, proxy_string)
                print(f"[PROXY] [CHROME-PREFS] Set proxy to Chrome Preferences for {profile_name}")
            except Exception as e:
                print(f"[WARNING] [PROXY] Could not set proxy to Chrome Preferences: {e}")
        
        print(f"[BULK-CREATE] Set proxy for {profile_name}: {proxy_string[:50] if proxy_string else 'null'}...")
    except Exception as e:
        print(f"[WARNING] [BULK-CREATE] Could not set proxy for {profile_name}: {e}")


def set_proxy_to_chrome_preferences(manager, profile_name, proxy_string):
    """Set proxy trực tiếp vào Chrome Preferences file (không qua extension)"""
    try:
        profile_path = os.path.join(manager.profiles_dir, profile_name)
        prefs_path = os.path.join(profile_path, 'Default', 'Preferences')
        
        if not os.path.exists(profile_path):
            raise Exception(f"Profile path not found: {profile_path}")
        
        # Parse proxy string: http://server:port:user:pass hoặc socks5://server:port:user:pass
        if not proxy_string or proxy_string.lower() == 'null':
            # Xóa proxy
            proxy_mode = 'system'
            proxy_config = {}
        else:
            # Parse proxy string
            if '://' in proxy_string:
                parts = proxy_string.split('://', 1)
                scheme = parts[0].lower()  # http hoặc socks5
                rest = parts[1]
            else:
                scheme = 'http'
                rest = proxy_string
            
            # Parse server:port:user:pass
            rest_parts = rest.split(':')
            server = rest_parts[0]
            port = rest_parts[1] if len(rest_parts) > 1 else '8080'
            username = rest_parts[2] if len(rest_parts) > 2 else ''
            password = rest_parts[3] if len(rest_parts) > 3 else ''
            
            # Set proxy mode
            proxy_mode = 'fixed_servers'
            proxy_config = {
                'mode': 'fixed_servers',
                'server': f"{scheme}://{server}:{port}",
            }
            
            # Nếu có username/password, cần lưu riêng (Chrome không lưu auth trong proxy server string)
            if username and password:
                # Chrome lưu auth trong separate field hoặc dùng trong URL
                # Format: scheme://username:password@server:port
                proxy_config['server'] = f"{scheme}://{username}:{password}@{server}:{port}"
        
        # Đọc Preferences hiện tại
        prefs_data = {}
        if os.path.exists(prefs_path):
            try:
                with open(prefs_path, 'r', encoding='utf-8') as f:
                    prefs_data = json.load(f)
            except Exception:
                prefs_data = {}
        
        # Set proxy vào Preferences
        if 'profile' not in prefs_data:
            prefs_data['profile'] = {}
        
        if 'content_settings' not in prefs_data:
            prefs_data['content_settings'] = {}
        
        # Chrome lưu proxy trong profile.proxy_config
        if proxy_string and proxy_string.lower() != 'null':
            prefs_data['profile']['proxy_config'] = {
                'mode': proxy_mode,
                'server': proxy_config.get('server', ''),
            }
        else:
            # Xóa proxy - set về system
            if 'proxy_config' in prefs_data.get('profile', {}):
                prefs_data['profile']['proxy_config'] = {
                    'mode': 'system',
                    'server': '',
                }
        
        # Lưu Preferences
        prefs_dir = os.path.dirname(prefs_path)
        if not os.path.exists(prefs_dir):
            os.makedirs(prefs_dir, exist_ok=True)
        
        with open(prefs_path, 'w', encoding='utf-8') as f:
            json.dump(prefs_data, f, ensure_ascii=False, indent=2)
        
        print(f"[PROXY] [CHROME-PREFS] Successfully set proxy in Chrome Preferences")
        return True
        
    except Exception as e:
        print(f"[ERROR] [PROXY] [CHROME-PREFS] Failed to set proxy in Chrome Preferences: {e}")
        return False


def get_proxy_from_profile_settings(manager, profile_name):
    """Đọc proxy từ profile_settings.json"""
    try:
        profile_path = os.path.join(manager.profiles_dir, profile_name)
        settings_path = os.path.join(profile_path, 'profile_settings.json')
        
        if not os.path.exists(settings_path):
            return None
        
        with open(settings_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        proxy = data.get('network', {}).get('proxy')
        if proxy and proxy.lower() != 'null':
            return proxy
        
        return None
    except Exception as e:
        print(f"[WARNING] [PROXY] Could not read proxy from profile_settings.json: {e}")
        return None


def get_switchyomega_settings_path(manager, profile_name):
    """Return absolute path to SwitchyOmega settings.json for a profile."""
    profile_path = os.path.join(manager.profiles_dir, profile_name)
    settings_path = os.path.join(
        profile_path,
        "Default",
        "Extensions",
        "pfnededegaaopdmhkdmcofjmoldfiped",
        "3.4.1_0",
        "settings.json",
    )
    return settings_path


def apply_proxy_via_settings(manager, profile_name, proxy_config):
    """
    Apply proxy by writing SwitchyOmega settings.json directly (no Chrome launch).

    proxy_config keys: proxy_server, proxy_port, username(optional), password(optional), scheme(optional)
    """
    try:
        print(f"💾 [SO-SETTINGS] Writing settings.json for profile: {profile_name}")

        settings_path = get_switchyomega_settings_path(manager, profile_name)
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


def apply_proxy_via_settings_string(manager, profile_name, proxy_string):
    """Parse proxy string and call apply_proxy_via_settings.
    Also saves proxy to profile_settings.json for consistency."""
    try:
        parts = proxy_string.strip().split(":")
        if len(parts) < 2:
            return False, "Invalid proxy format. Use server:port[:username:password]"
        
        # Build proxy string for profile_settings.json (format: http://server:port:username:password)
        scheme = "http"
        server = parts[0].strip()
        port = parts[1].strip()
        username = parts[2].strip() if len(parts) > 2 else ""
        password = parts[3].strip() if len(parts) > 3 else ""
        
        # Format for profile_settings.json
        if username and password:
            proxy_for_settings = f"{scheme}://{server}:{port}:{username}:{password}"
        else:
            proxy_for_settings = f"{scheme}://{server}:{port}"
        
        # Save to profile_settings.json
        try:
            set_profile_proxy(manager, profile_name, proxy_for_settings)
            print(f"[PROXY] [PROFILE-SETTINGS] Saved proxy to profile_settings.json for {profile_name}")
        except Exception as e:
            print(f"[WARNING] [PROXY] Could not save to profile_settings.json: {e}")
        
        # Apply to SwitchyOmega settings.json
        proxy_config = {
            "proxy_server": server,
            "proxy_port": int(port),
            "username": username,
            "password": password,
            "scheme": scheme,
        }
        return apply_proxy_via_settings(manager, profile_name, proxy_config)
    except Exception as e:
        return False, f"Failed to parse/apply: {e}"


def bulk_apply_proxy_map_via_settings(manager, profile_to_proxy_map):
    """Apply many proxies to many profiles by editing settings.json files directly.

    profile_to_proxy_map: dict { profile_name: proxy_string }
    Returns (results: list of {profile, success, message}, success_count)
    """
    results = []
    success_count = 0
    for profile_name, proxy_string in profile_to_proxy_map.items():
        try:
            ok, msg = apply_proxy_via_settings_string(manager, profile_name, proxy_string)
            results.append({"profile": profile_name, "success": ok, "message": msg})
            if ok:
                success_count += 1
        except Exception as e:
            results.append({"profile": profile_name, "success": False, "message": str(e)})
    return results, success_count


def force_import_settings_into_extension(manager, profile_name):
    """Open SwitchyOmega options for the given profile and import our settings.json via UI.

    This ensures the extension's Local Extension Settings storage reflects the settings file we wrote.
    """
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC

        settings_path = get_switchyomega_settings_path(manager, profile_name)
        if not os.path.exists(settings_path):
            return False, f"settings.json not found for profile {profile_name}"

        profile_dir = os.path.join(manager.profiles_dir, profile_name)
        if not os.path.exists(profile_dir):
            return False, f"Profile '{profile_name}' not found"

        chrome_options = Options()
        chrome_options.add_argument(f"--user-data-dir={profile_dir}")
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


def input_proxy_from_ui(manager, profile_name, proxy_string):
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
        return manager.configure_switchyomega_proxy(profile_name, proxy_config)
        
    except ValueError as e:
        return False, f"Invalid port number: {str(e)}"
    except Exception as e:
        return False, f"Error parsing proxy: {str(e)}"


def bulk_input_proxy_from_ui(manager, profile_list, proxy_string):
    """
    Apply proxy configuration to multiple profiles
    """
    results = []
    success_count = 0
    
    for profile_name in profile_list:
        try:
            success, message = input_proxy_from_ui(manager, profile_name, proxy_string)
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


def test_proxy_connection(manager, proxy_string):
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


def analyze_profile_proxy_status(manager, profile_name):
    """Analyze if a profile has proxy configured"""
    try:
        print(f"[DEBUG] [ANALYZE] Analyzing proxy status for profile: {profile_name}")
        
        profile_path = manager.get_profile_path(profile_name)
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


def get_profiles_with_proxy(manager):
    """Get all profiles that have proxy configured"""
    all_profiles = manager.get_all_profiles()
    proxy_profiles = []
    
    print(f"[DEBUG] [ANALYZE] Analyzing {len(all_profiles)} profiles for proxy status...")
    
    for profile in all_profiles:
        has_proxy, message = analyze_profile_proxy_status(manager, profile)
        if has_proxy:
            proxy_profiles.append(profile)
            print(f"[SUCCESS] {profile}: {message}")
        else:
            print(f"[ERROR] {profile}: {message}")
    
    return proxy_profiles


def get_profiles_without_proxy(manager):
    """Get all profiles that don't have proxy configured"""
    all_profiles = manager.get_all_profiles()
    no_proxy_profiles = []
    
    print(f"[DEBUG] [ANALYZE] Analyzing {len(all_profiles)} profiles for missing proxy...")
    
    for profile in all_profiles:
        has_proxy, message = analyze_profile_proxy_status(manager, profile)
        if not has_proxy:
            no_proxy_profiles.append(profile)
            print(f"[ERROR] {profile}: {message}")
        else:
            print(f"[SUCCESS] {profile}: {message}")
    
    return no_proxy_profiles


def smart_configure_proxy(manager, profile_name, proxy_string):
    """Smart proxy configuration - check if profile needs proxy setup"""
    print(f"🧠 [SMART] Smart proxy configuration for {profile_name}")
    
    # Check current status
    has_proxy, message = analyze_profile_proxy_status(manager, profile_name)
    
    if has_proxy:
        print(f"ℹ️ [SMART] Profile {profile_name} already has proxy configured: {message}")
        return True, f"Proxy already configured: {message}"
    
    # Configure proxy
    print(f"[TOOL] [SMART] Configuring proxy for {profile_name}...")
    success, result_message = input_proxy_from_ui(manager, profile_name, proxy_string)
    
    if success:
        print(f"[SUCCESS] [SMART] Successfully configured proxy for {profile_name}")
        return True, result_message
    else:
        print(f"[ERROR] [SMART] Failed to configure proxy for {profile_name}: {result_message}")
        return False, result_message


def bulk_smart_configure_proxy(manager, profile_list, proxy_string):
    """Bulk smart proxy configuration"""
    print(f"🧠 [SMART] Bulk smart proxy configuration for {len(profile_list)} profiles")
    
    results = []
    success_count = 0
    
    for profile_name in profile_list:
        print(f"\n[CREATE] [SMART] Processing {profile_name}...")
        success, message = smart_configure_proxy(manager, profile_name, proxy_string)
        
        results.append({
            'profile': profile_name,
            'success': success,
            'message': message
        })
        
        if success:
            success_count += 1
    
    return results, success_count