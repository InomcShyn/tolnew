import os
import json
import time
from core.utils.proxy_utils import fix_duplicate_protocol, parse_proxy_string

def set_profile_proxy(manager, profile_name, proxy_string):
    """Set proxy for a profile - Lưu vào profile_settings.json VÀ tạo proxy auth extension"""
    try:
        # Fix duplicate protocol first
        proxy_string = fix_duplicate_protocol(proxy_string)
        
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
        
        # ❌ KHÔNG TỰ ĐỘNG TẠO PROXY AUTH EXTENSION
        # Proxy authentication sẽ được xử lý bởi CDP (Chrome DevTools Protocol)
        # hoặc user tự tạo extension nếu cần
        
        print(f"[BULK-CREATE] Set proxy for {profile_name}: {proxy_string[:50] if proxy_string else 'null'}...")
    except Exception as e:
        print(f"[WARNING] [BULK-CREATE] Could not set proxy for {profile_name}: {e}")


def set_proxy_to_chrome_preferences(manager, profile_name, proxy_string):
    """
    Set proxy trực tiếp vào Chrome Preferences file.
    
    ⚠️ LƯU Ý: Chrome KHÔNG hỗ trợ credentials trong Preferences.
    Credentials sẽ được xử lý bởi proxy auth extension (tạo trong set_profile_proxy).
    """
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
            
            # ⚠️ QUAN TRỌNG: Chrome KHÔNG hỗ trợ credentials trong Preferences
            # Chỉ lưu server:port, credentials được xử lý bởi extension
            proxy_config = {
                'mode': 'fixed_servers',
                'server': f"{scheme}://{server}:{port}",  # KHÔNG bao gồm username:password
            }
            
            # Note: Username/password sẽ được xử lý bởi proxy auth extension
            # Extension được tạo trong set_profile_proxy() và load khi launch Chrome
        
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


def force_import_settings_into_extension(manager, profile_name):
    """
    DEPRECATED: Selenium-based function removed
    
    Playwright version không cần import settings thủ công
    Proxy được apply trực tiếp qua Playwright API
    """
    print("[WARNING] force_import_settings_into_extension is deprecated")
    print("[INFO] Proxy is applied directly via Playwright API")
    print("[INFO] No need to import settings into extension")
    
    return False, "Function deprecated in Playwright version"


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
