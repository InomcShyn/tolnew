import os
import time
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

# === Extension management functions (moved from chrome_manager.py) ===
# Refactored to support ANY extension, not just SwitchyOmega

def _get_extension_display_name(extension_id, extension_name=None):
    """Get display name for extension - use extension_name if provided, otherwise use extension_id"""
    if extension_name:
        return extension_name
    # Default fallback for backward compatibility
    if extension_id == "pfnededegaaopdmhkdmcofjmoldfiped":
        return "Proxy SwitchyOmega 3"
    return f"Extension {extension_id[:8]}..."


def _ensure_local_extension_directory(extension_name):
    """Auto-create local extension directory if it doesn't exist"""
    if not extension_name:
        return None
    extensions_base = os.path.join(os.getcwd(), "extensions")
    if not os.path.exists(extensions_base):
        os.makedirs(extensions_base)
    extension_dir = os.path.join(extensions_base, extension_name)
    if not os.path.exists(extension_dir):
        os.makedirs(extension_dir)
        print(f"[CREATE] [EXTENSION] Created local extension directory: {extension_dir}")
    return extension_dir


def install_extension_for_profile(manager, profile_name, extension_id="pfnededegaaopdmhkdmcofjmoldfiped", extension_name=None):
    """
    Install extension for a specific profile.
    
    Args:
        manager: ChromeProfileManager instance
        profile_name: Name of the Chrome profile
        extension_id: Chrome extension ID (default: SwitchyOmega 3)
        extension_name: Optional display name for the extension (used for local directory)
    
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        display_name = _get_extension_display_name(extension_id, extension_name)
        print(f"[TOOL] [EXTENSION] Installing {display_name} (ID: {extension_id}) for profile: {profile_name}")
        
        profile_path = manager.get_profile_path(profile_name)
        if not profile_path or not os.path.exists(profile_path):
            return False, f"Profile path not found: {profile_name}"
        
        if check_extension_installed(manager, profile_name, extension_id):
            return True, f"{display_name} already installed"
        
        # Auto-create local directory if extension_name provided
        if extension_name:
            _ensure_local_extension_directory(extension_name)
        
        methods = [
            lambda m, p, eid: _install_extension_method_1(m, p, eid, extension_name),
            lambda m, p, eid: _install_extension_method_2(m, p, eid, extension_name),
            lambda m, p, eid: _install_extension_method_3(m, p, eid, extension_name),
        ]
        for i, method in enumerate(methods, 1):
            try:
                print(f"[REFRESH] [EXTENSION] Trying installation method {i} for {profile_name}")
                success, message = method(manager, profile_name, extension_id)
                if success:
                    print(f"[SUCCESS] [EXTENSION] Method {i} successful: {message}")
                    return True, f"Installed using method {i}: {message}"
                else:
                    print(f"[ERROR] [EXTENSION] Method {i} failed: {message}")
            except Exception as e:
                print(f"[ERROR] [EXTENSION] Method {i} error: {str(e)}")
                continue
        return False, "All installation methods failed"
    except Exception as e:
        print(f"[ERROR] [EXTENSION] Error installing extension for {profile_name}: {str(e)}")
        return False, f"Installation error: {str(e)}"


def _install_extension_method_1(manager, profile_name, extension_id, extension_name=None):
    """Method 1: Direct copy from local directory"""
    try:
        profile_path = manager.get_profile_path(profile_name)
        extensions_dir = os.path.join(profile_path, "Default", "Extensions")
        if not os.path.exists(extensions_dir):
            os.makedirs(extensions_dir)
        
        # Try to find local extension directory
        local_extensions = []
        if extension_name:
            local_extensions.append(f"extensions/{extension_name}")
        # Backward compatibility: try SwitchyOmega paths
        if extension_id == "pfnededegaaopdmhkdmcofjmoldfiped":
            local_extensions.extend(["extensions/SwitchyOmega", "extensions/SwitchyOmega3_Real"])
        
        extension_source = None
        for ext_dir in local_extensions:
            if os.path.exists(ext_dir):
                extension_source = ext_dir
                break
        
        if not extension_source:
            return False, f"No local extension files found in extensions/{extension_name or extension_id}"
        
        final_extension_dir = os.path.join(extensions_dir, extension_id)
        if os.path.exists(final_extension_dir):
            import shutil
            shutil.rmtree(final_extension_dir)
        
        import shutil
        shutil.copytree(extension_source, final_extension_dir)
        
        # Verify manifest exists
        manifest_path = os.path.join(final_extension_dir, "manifest.json")
        if not os.path.exists(manifest_path):
            # Only create default manifest if it's SwitchyOmega (backward compatibility)
            if extension_id == "pfnededegaaopdmhkdmcofjmoldfiped":
                import json
                manifest_content = {
                    "manifest_version": 3,
                    "name": "Proxy SwitchyOmega 3 (ZeroOmega)",
                    "version": "3.0.0",
                    "description": "A proxy configuration tool",
                    "permissions": [
                        "proxy","storage","tabs","webRequest","webRequestBlocking","management","unlimitedStorage"
                    ],
                    "background": {"service_worker": "background.js"},
                    "action": {"default_popup": "popup.html","default_title": "SwitchyOmega"},
                    "icons": {"16": "icon16.png","48": "icon48.png","128": "icon128.png"}
                }
                with open(manifest_path, 'w', encoding='utf-8') as f:
                    json.dump(manifest_content, f, indent=2, ensure_ascii=False)
            else:
                return False, "Extension copied but manifest.json not found"
        
        display_name = _get_extension_display_name(extension_id, extension_name)
        return True, f"{display_name} installed via direct copy"
    except Exception as e:
        return False, f"Direct copy method failed: {str(e)}"


def _install_extension_method_2(manager, profile_name, extension_id, extension_name=None):
    """Method 2: Install from Chrome WebStore via automation"""
    try:
        profile_path = manager.get_profile_path(profile_name)
        # Generic WebStore URL format
        extension_url = f"https://chromewebstore.google.com/detail/{extension_id}"
        chrome_options = Options()
        manager._apply_custom_chrome_binary(chrome_options, profile_path)
        chrome_options.add_argument(f"--user-data-dir={profile_path}")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1024,768")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        desired_version = ''
        try:
            settings_probe = os.path.join(profile_path, 'profile_settings.json')
            if os.path.exists(settings_probe):
                import json as _json
                with open(settings_probe, 'r', encoding='utf-8') as sf:
                    _ps = _json.load(sf)
                    desired_version = ((_ps.get('software') or {}).get('browser_version') or '').strip()
        except Exception:
            pass
        driver_path = manager._ensure_cft_chromedriver(desired_version)
        if driver_path and os.path.exists(driver_path):
            service = Service(executable_path=driver_path)
            driver = webdriver.Chrome(service=service, options=chrome_options)
        else:
            driver = webdriver.Chrome(options=chrome_options)
        try:
            driver.get(extension_url)
            driver.implicitly_wait(10)
            time.sleep(3)
            try:
                add_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Add to Chrome') or contains(text(), 'Thêm ando Chrome')]"))
                )
                add_button.click()
                display_name = _get_extension_display_name(extension_id, extension_name)
                print(f"[SUCCESS] [EXTENSION] Clicked Add to Chrome button for {profile_name}")
                time.sleep(5)
                if check_extension_installed(manager, profile_name, extension_id):
                    return True, f"{display_name} installed via WebStore"
                else:
                    return False, f"{display_name} installation failed - not detected after installation"
            except Exception as e:
                print(f"[ERROR] [EXTENSION] Could not find Add to Chrome button: {str(e)}")
                return False, f"Could not find Add to Chrome button: {str(e)}"
        except Exception as e:
            return False, f"WebStore method failed: {str(e)}"
        finally:
            driver.quit()
    except Exception as e:
        return False, f"WebStore method failed: {str(e)}"


def _install_extension_method_3(manager, profile_name, extension_id, extension_name=None):
    """Method 3: Download CRX and load unpacked"""
    try:
        # Try to download extension CRX (generic or SwitchyOmega-specific)
        crx_file_path = _download_extension_crx(manager, extension_id, extension_name)
        if not crx_file_path:
            return False, "Could not download CRX file"
        profile_path = manager.get_profile_path(profile_name)
        extensions_dir = os.path.join(profile_path, "Extensions")
        if not os.path.exists(extensions_dir):
            os.makedirs(extensions_dir)
        chrome_options = Options()
        manager._apply_custom_chrome_binary(chrome_options, profile_path)
        chrome_options.add_argument(f"--user-data-dir={profile_path}")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1024,768")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--disable-features=VizDisplayCompositor")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        from selenium import webdriver
        desired_version = ''
        try:
            settings_probe = os.path.join(profile_path, 'profile_settings.json')
            if os.path.exists(settings_probe):
                import json as _json
                with open(settings_probe, 'r', encoding='utf-8') as sf:
                    _ps = _json.load(sf)
                    desired_version = ((_ps.get('software') or {}).get('browser_version') or '').strip()
        except Exception:
            pass
        driver_path = manager._ensure_cft_chromedriver(desired_version)
        if driver_path and os.path.exists(driver_path):
            service = Service(executable_path=driver_path)
            driver = webdriver.Chrome(service=service, options=chrome_options)
        else:
            driver = webdriver.Chrome(options=chrome_options)
        try:
            driver.get("chrome://extensions/")
            time.sleep(2)
            try:
                from selenium.webdriver.common.by import By
                from selenium.webdriver.support.ui import WebDriverWait
                from selenium.webdriver.support import expected_conditions as EC
                developer_toggle = driver.find_element(By.XPATH, "//input[@type='checkbox' and @id='devMode']")
                if not developer_toggle.is_selected():
                    developer_toggle.click()
                    time.sleep(1)
                load_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Load unpacked') or contains(text(), 'Tải done giải nén')]"))
                )
                load_button.click()
                return _install_extension_method_1(manager, profile_name, extension_id, extension_name)
            except Exception as e:
                print(f"[ERROR] [EXTENSION] Could not enable developer mode: {str(e)}")
                return _install_extension_method_1(manager, profile_name, extension_id, extension_name)
        finally:
            driver.quit()
    except Exception as e:
        return False, f"CRX method failed: {str(e)}"


def install_extension_for_all_profiles(manager, extension_id="pfnededegaaopdmhkdmcofjmoldfiped", extension_name=None):
    """Install extension for all profiles"""
    all_profiles = manager.get_all_profiles()
    return bulk_install_extension(manager, all_profiles, extension_id, extension_name)


def install_extension_for_new_profiles(manager, extension_id="pfnededegaaopdmhkdmcofjmoldfiped", extension_name=None):
    """Install extension only for profiles that don't have it"""
    all_profiles = manager.get_all_profiles()
    profiles_without_extension = []
    display_name = _get_extension_display_name(extension_id, extension_name)
    print(f"[DEBUG] [EXTENSION] Checking which profiles need {display_name} installation...")
    for profile_name in all_profiles:
        if not check_extension_installed(manager, profile_name, extension_id):
            profiles_without_extension.append(profile_name)
            print(f"[INPUT] [EXTENSION] {profile_name} needs {display_name} installation")
        else:
            print(f"[SUCCESS] [EXTENSION] {profile_name} already has {display_name}")
    if not profiles_without_extension:
        print(f"[SUCCESS] [EXTENSION] All profiles already have {display_name} installed!")
        return 0, [f"All profiles already have {display_name} installed"]
    print(f"[PROFILE] [EXTENSION] Installing {display_name} for {len(profiles_without_extension)} profiles that need it...")
    return bulk_install_extension(manager, profiles_without_extension, extension_id, extension_name)


def bulk_install_extension(manager, profile_list=None, extension_id="pfnededegaaopdmhkdmcofjmoldfiped", extension_name=None):
    """Bulk install extension for multiple profiles"""
    if profile_list is None:
        profile_list = manager.get_all_profiles()
    success_count = 0
    results = []
    display_name = _get_extension_display_name(extension_id, extension_name)
    print(f"[PROFILE] [BULK-EXTENSION] Starting bulk installation of {display_name} for {len(profile_list)} profiles")
    for profile_name in profile_list:
        try:
            success, message = install_extension_for_profile(manager, profile_name, extension_id, extension_name)
            result = f"{'[SUCCESS]' if success else '[ERROR]'} {profile_name}: {message}"
            results.append(result)
            if success:
                success_count += 1
            time.sleep(1)
        except Exception as e:
            error_msg = f"[ERROR] {profile_name}: Error - {str(e)}"
            results.append(error_msg)
            print(f"[ERROR] [BULK-EXTENSION] Error for {profile_name}: {str(e)}")
    print(f"[SUCCESS] [BULK-EXTENSION] Completed: {success_count}/{len(profile_list)} successful for {display_name}")
    return success_count, results


def check_extension_installed(manager, profile_name, extension_id="pfnededegaaopdmhkdmcofjmoldfiped"):
    try:
        profile_path = manager.get_profile_path(profile_name)
        if not profile_path:
            print(f"[WARNING] [EXTENSION-CHECK] Profile path not found for {profile_name}")
            return False
        extensions_dir = os.path.join(profile_path, "Extensions")
        default_extensions_dir = os.path.join(profile_path, "Default", "Extensions")
        if os.path.exists(default_extensions_dir):
            extensions_dir = default_extensions_dir
            print(f"[CREATE] [EXTENSION-CHECK] Using Default/Extensions for {profile_name}")
        elif os.path.exists(extensions_dir):
            print(f"[CREATE] [EXTENSION-CHECK] Using Extensions for {profile_name}")
        else:
            print(f"[WARNING] [EXTENSION-CHECK] No Extensions directory found for {profile_name}")
            return False
        extension_found = False
        extension_path = None
        try:
            extensions = os.listdir(extensions_dir)
            print(f"[CREATE] [EXTENSION-CHECK] Available extensions in {profile_name}: {extensions}")
            for item in extensions:
                if extension_id in item:
                    extension_path = os.path.join(extensions_dir, item)
                    extension_found = True
                    print(f"[SUCCESS] [EXTENSION-CHECK] Found extension folder: {item} for {profile_name}")
                    break
            if not extension_found:
                print(f"[ERROR] [EXTENSION-CHECK] Extension folder not found in {profile_name}")
                return False
        except Exception as e:
            print(f"[ERROR] [EXTENSION-CHECK] Error listing extensions: {str(e)}")
            return False
        if extension_path and os.path.exists(extension_path):
            version_folders = [d for d in os.listdir(extension_path) if os.path.isdir(os.path.join(extension_path, d))]
            if not version_folders:
                print(f"[ERROR] [EXTENSION-CHECK] No version folders found in extension")
                return False
            latest_version = sorted(version_folders)[-1]
            version_path = os.path.join(extension_path, latest_version)
            
            # Check for manifest.json (required for all extensions)
            manifest_path = os.path.join(version_path, "manifest.json")
            if not os.path.exists(manifest_path):
                print(f"[ERROR] [EXTENSION-CHECK] Extension folder exists but manifest.json not found")
                return False
            
            try:
                import json
                with open(manifest_path, 'r', encoding='utf-8') as f:
                    manifest = json.load(f)
                # Check if manifest is valid
                manifest_name = manifest.get("name", "")
                manifest_version = manifest.get("manifest_version", 2)
                
                if not manifest_name:
                    print(f"[ERROR] [EXTENSION-CHECK] Extension manifest has no name")
                    return False
                
                # Verify extension ID matches (if present in manifest)
                manifest_app_id = manifest.get("key", "") or manifest.get("id", "")
                if manifest_app_id and extension_id not in manifest_app_id:
                    # Allow if manifest has key/id different (some extensions use key)
                    pass
                
                print(f"[SUCCESS] [EXTENSION-CHECK] Extension properly installed with valid manifest: {manifest_name} (v{manifest_version})")
                return True
            except Exception as e:
                print(f"[ERROR] [EXTENSION-CHECK] Error reading manifest: {str(e)}")
                return False
        else:
            print(f"[ERROR] [EXTENSION-CHECK] Extension folder path not found")
            return False
    except Exception as e:
        print(f"[ERROR] [EXTENSION-CHECK] Error checking extension for {profile_name}: {str(e)}")
        return False


def _download_extension_crx(manager, extension_id, extension_name=None):
    """
    Download extension CRX file (generic or SwitchyOmega-specific).
    Currently only supports SwitchyOmega from GitHub.
    For other extensions, users should provide local CRX file.
    """
    try:
        import requests
        extensions_dir = os.path.join(os.getcwd(), "extensions")
        if not os.path.exists(extensions_dir):
            os.makedirs(extensions_dir)
        
        # SwitchyOmega-specific download
        if extension_id == "pfnededegaaopdmhkdmcofjmoldfiped":
            extension_url = "https://github.com/FelisCatus/SwitchyOmega/releases/download/v2.5.21/SwitchyOmega_Chromium.crx"
            crx_file_path = os.path.join(extensions_dir, "SwitchyOmega_Chromium.crx")
            display_name = _get_extension_display_name(extension_id, extension_name)
        else:
            # Generic: try to find CRX file in extensions/{extension_name}/ or extensions/
            if extension_name:
                crx_file_path = os.path.join(extensions_dir, extension_name, f"{extension_name}.crx")
                if not os.path.exists(crx_file_path):
                    # Try alternative location
                    crx_file_path = os.path.join(extensions_dir, f"{extension_name}.crx")
            else:
                crx_file_path = os.path.join(extensions_dir, f"{extension_id}.crx")
            
            if os.path.exists(crx_file_path):
                print(f"[SUCCESS] [DOWNLOAD] Extension file already exists: {crx_file_path}")
                return crx_file_path
            else:
                print(f"[WARNING] [DOWNLOAD] CRX file not found locally: {crx_file_path}")
                print(f"[INFO] [DOWNLOAD] Please provide CRX file manually or use WebStore method")
                return None
        
        if os.path.exists(crx_file_path):
            print(f"[SUCCESS] [DOWNLOAD] Extension file already exists: {crx_file_path}")
            return crx_file_path
        
        display_name = _get_extension_display_name(extension_id, extension_name)
        print(f"📥 [DOWNLOAD] Downloading {display_name} extension...")
        print(f"🔗 [DOWNLOAD] URL: {extension_url}")
        response = requests.get(extension_url, stream=True)
        response.raise_for_status()
        with open(crx_file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"[SUCCESS] [DOWNLOAD] Extension downloaded successfully: {crx_file_path}")
        return crx_file_path
    except Exception as e:
        print(f"[ERROR] [DOWNLOAD] Error downloading extension: {str(e)}")
        return None


# === Modern Extension Management (GUI-based) ===

def load_extensions_from_profile_path(profile_path):
    """
    Load extensions from a Chrome profile path.
    Wrapper for ChromeExtensionManager.load_extensions_from_profile()
    
    Args:
        profile_path (str): Full path to Chrome profile folder
    
    Returns:
        list: List of extension dicts
    """
    try:
        from core.chrome_manager import ChromeExtensionManager
        ext_mgr = ChromeExtensionManager()
        return ext_mgr.load_extensions_from_profile(profile_path)
    except Exception as e:
        print(f"[ERROR] [TILE-EXT] Error loading extensions: {e}")
        import traceback
        traceback.print_exc()
        return []


def list_chrome_profiles_from_user_data(user_data_path):
    """
    List all Chrome profiles in User Data directory.
    Wrapper for ChromeExtensionManager.list_available_profiles()
    
    Args:
        user_data_path (str): Path to Chrome User Data folder
    
    Returns:
        list: List of profile dicts
    """
    try:
        from core.chrome_manager import ChromeExtensionManager
        ext_mgr = ChromeExtensionManager()
        return ext_mgr.list_available_profiles(user_data_path)
    except Exception as e:
        print(f"[ERROR] [TILE-EXT] Error listing profiles: {e}")
        import traceback
        traceback.print_exc()
        return []


def install_extensions_to_profiles(extension_ids, source_profile_path, target_profile_paths):
    """
    Install multiple extensions to multiple profiles.
    
    Args:
        extension_ids (list): List of extension IDs to install
        source_profile_path (str): Source profile path
        target_profile_paths (list): List of target profile paths
    
    Returns:
        dict: {'success_count': int, 'failed_count': int, 'results': list}
    """
    try:
        from core.chrome_manager import ChromeExtensionManager
        ext_mgr = ChromeExtensionManager()
        
        total_success = 0
        total_failed = 0
        all_results = []
        
        for ext_id in extension_ids:
            result = ext_mgr.install_extension_to_profiles(
                ext_id, 
                source_profile_path, 
                target_profile_paths
            )
            
            total_success += result['success_count']
            total_failed += result['failed_count']
            all_results.append({
                'extension_id': ext_id,
                'result': result
            })
        
        print(f"[SUCCESS] [TILE-EXT] Total: {total_success} success, {total_failed} failed")
        return {
            'success_count': total_success,
            'failed_count': total_failed,
            'results': all_results
        }
        
    except Exception as e:
        print(f"[ERROR] [TILE-EXT] Error installing extensions: {e}")
        import traceback
        traceback.print_exc()
        return {
            'success_count': 0,
            'failed_count': len(extension_ids) * len(target_profile_paths),
            'results': []
        }
