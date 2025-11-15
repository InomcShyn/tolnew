import os
import json
import shutil
import time

# === OMOcaptcha Extension Management ===
# Tách logic xử lý OMOcaptcha extension và API key ra khỏi GUI

def get_omocaptcha_extension_id(manager):
    """
    Lấy OMOcaptcha extension ID từ override/config hoặc dùng default.
    
    Args:
        manager: ChromeProfileManager instance
    
    Returns:
        str: Extension ID
    """
    try:
        if hasattr(manager, "_get_omocaptcha_extension_id_override"):
            ext_id = (manager._get_omocaptcha_extension_id_override() or '').strip()
            if ext_id:
                return ext_id
    except Exception:
        pass
    
    # Default known OMOcaptcha extension ID
    return 'dfjghhjachoacpgpkmbpdlpppeagojhe'


def get_omocaptcha_extension_path(manager, profile_name):
    """
    Lấy đường dẫn đầy đủ đến OMOcaptcha extension trong profile.
    Dùng để thêm vào --load-extension flag khi launch Chrome.
    
    Args:
        manager: ChromeProfileManager instance
        profile_name: Tên profile
    
    Returns:
        str or None: Đường dẫn đến extension version folder, hoặc None nếu không tìm thấy
    """
    try:
        extension_id = get_omocaptcha_extension_id(manager)
        profile_path = manager.get_profile_path(profile_name)
        
        if not profile_path or not os.path.exists(profile_path):
            return None
        
        # Đường dẫn đến extension: Default/Extensions/{extension_id}/
        ext_base_dir = os.path.join(profile_path, "Default", "Extensions", extension_id)
        
        if not os.path.exists(ext_base_dir):
            return None
        
        # Tìm version folder (ví dụ: 1.3.1_0)
        try:
            versions = [d for d in os.listdir(ext_base_dir) 
                       if os.path.isdir(os.path.join(ext_base_dir, d))]
            
            if not versions:
                return None
            
            # Lấy version mới nhất (sort theo tên)
            versions.sort(reverse=True)
            version_dir = os.path.join(ext_base_dir, versions[0])
            
            # Kiểm tra manifest.json có tồn tại không
            manifest_path = os.path.join(version_dir, "manifest.json")
            if os.path.exists(manifest_path):
                return version_dir
            
        except Exception:
            pass
        
        return None
        
    except Exception:
        return None


def install_omocaptcha_extension_local(manager, profile_name, extension_id=None, force=False, api_key=None):
    """
    Cài đặt OMOcaptcha extension bằng cách copy từ thư mục local.
    Không sử dụng Selenium để tránh xung đột với Chrome đang chạy.
    
    Args:
        manager: ChromeProfileManager instance
        profile_name: Tên profile cần cài extension
        extension_id: Extension ID (nếu None sẽ tự động lấy)
        force: Bỏ qua kiểm tra Chrome đang chạy (dùng cho bulk run)
        api_key: API key để inject ngay sau khi copy (optional)
    
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        if extension_id is None:
            extension_id = get_omocaptcha_extension_id(manager)
        
        profile_path = manager.get_profile_path(profile_name)
        if not profile_path or not os.path.exists(profile_path):
            return False, f"Profile path not found: {profile_name}"
        
        # Kiểm tra Chrome có đang chạy không (trừ khi force=True)
        if not force:
            devtools_flag = os.path.join(profile_path, 'DevToolsActivePort')
            if os.path.exists(devtools_flag):
                return False, "Chrome đang chạy với profile này. Vui lòng đóng Chrome trước khi cài extension."
        
        # Tìm thư mục extension local (sử dụng đường dẫn tuyệt đối)
        # Thử nhiều cách để tìm workspace root
        workspace_root = None
        
        # Cách 1: Lấy từ __file__ (đáng tin cậy nhất)
        try:
            current_file = os.path.abspath(__file__)
            # core/tiles/tile_omocaptcha.py -> workspace root
            workspace_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))
        except:
            pass
        
        # Cách 2: Fallback về os.getcwd()
        if not workspace_root or not os.path.exists(workspace_root):
            workspace_root = os.getcwd()
        
        # Cách 3: Thử tìm từ các thư mục cha
        if not os.path.exists(os.path.join(workspace_root, "extensions")):
            # Thử 1 level lên
            parent_dir = os.path.dirname(workspace_root)
            if os.path.exists(os.path.join(parent_dir, "extensions")):
                workspace_root = parent_dir
        
        local_ext_paths = [
            os.path.join(workspace_root, "extensions", "OMOcaptcha"),
            os.path.join(workspace_root, "extensions", extension_id),
            os.path.join(workspace_root, "extensions", "omocaptcha"),
        ]
        
        # Tìm extension source
        local_ext_source = None
        for ext_path in local_ext_paths:
            manifest_path = os.path.join(ext_path, "manifest.json")
            if os.path.exists(ext_path) and os.path.isdir(ext_path) and os.path.exists(manifest_path):
                local_ext_source = ext_path
                break
        
        if not local_ext_source:
            return False, f"Không tìm thấy extension OMOcaptcha trong thư mục extensions/"
        
        # Đích: Default/Extensions/{extension_id}/
        # Đảm bảo thư mục Default tồn tại
        default_dir = os.path.join(profile_path, "Default")
        if not os.path.exists(default_dir):
            try:
                os.makedirs(default_dir, exist_ok=True)
            except Exception as e:
                return False, f"Không thể tạo thư mục Default: {str(e)}"
        
        extensions_base_dir = os.path.join(profile_path, "Default", "Extensions")
        if not os.path.exists(extensions_base_dir):
            try:
                os.makedirs(extensions_base_dir, exist_ok=True)
            except Exception as e:
                return False, f"Không thể tạo thư mục Extensions: {str(e)}"
        
        target_ext_dir = os.path.join(extensions_base_dir, extension_id)
        
        # Xóa extension cũ nếu có
        if os.path.exists(target_ext_dir):
            try:
                shutil.rmtree(target_ext_dir)
            except Exception as e:
                return False, f"Không thể xóa extension cũ: {str(e)}"
        
        # Copy extension
        try:
            if not os.path.exists(local_ext_source):
                return False, f"Thư mục extension nguồn không tồn tại: {local_ext_source}"
            shutil.copytree(local_ext_source, target_ext_dir)
        except Exception as e:
            return False, f"Lỗi khi cài đặt extension: {str(e)}"
        
        # Đọc manifest để lấy version
        manifest_path = os.path.join(target_ext_dir, "manifest.json")
        if not os.path.exists(manifest_path):
            return False, "Extension đã copy nhưng không có manifest.json"
        
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
            version = manifest.get('version', '1.0.0')
        except Exception:
            version = '1.0.0'
        
        # Chrome yêu cầu cấu trúc {ext_id}/{version}/ cho extension
        # Kiểm tra xem extension đã có version folder chưa
        version_dir = os.path.join(target_ext_dir, f"{version}_0")
        
        # Nếu manifest.json ở root của target_ext_dir, cần di chuyển vào version folder
        main_manifest = os.path.join(target_ext_dir, "manifest.json")
        if os.path.exists(main_manifest) and not os.path.exists(version_dir):
            # Tạo version folder và di chuyển tất cả file vào đó
            try:
                os.makedirs(version_dir, exist_ok=True)
                # Di chuyển tất cả file và folder vào version_dir (trừ version folder nếu đã có)
                items_to_move = []
                for item in os.listdir(target_ext_dir):
                    if item == f"{version}_0":  # Bỏ qua nếu đã có version folder
                        continue
                    items_to_move.append(item)
                
                for item in items_to_move:
                    src = os.path.join(target_ext_dir, item)
                    dst = os.path.join(version_dir, item)
                    if os.path.isdir(src):
                        if os.path.exists(dst):
                            shutil.rmtree(dst)
                        shutil.copytree(src, dst)
                        # Xóa source sau khi copy thành công
                        shutil.rmtree(src)
                    else:
                        shutil.copy2(src, dst)
                        # Xóa source sau khi copy thành công
                        os.remove(src)
            except Exception as e:
                return False, f"Lỗi khi tạo thư mục version: {str(e)}"
        
        # Đảm bảo cấu trúc đúng: chỉ có version folder ở root, không có file/folder thừa
        # Xóa các file/folder không cần thiết ở root (như _metadata, README.md, etc.)
        if os.path.exists(target_ext_dir):
            items_to_remove = []
            for item in os.listdir(target_ext_dir):
                # Chỉ giữ lại version folder
                if item != f"{version}_0":
                    items_to_remove.append(item)
            
            for item in items_to_remove:
                item_path = os.path.join(target_ext_dir, item)
                try:
                    if os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                    else:
                        os.remove(item_path)
                except Exception as e:
                    # Log warning nhưng không fail nếu không xóa được
                    print(f"[WARNING] Không thể xóa {item_path}: {str(e)}")
        
        # Inject API key vào configs.json ngay sau khi copy extension
        # Đảm bảo extension đọc API key đúng khi load lần đầu
        if api_key and api_key.strip():
            try:
                configs_path = os.path.join(version_dir, "configs.json")
                if os.path.exists(configs_path):
                    with open(configs_path, 'r', encoding='utf-8') as f:
                        configs = json.load(f)
                    
                    configs['api_key'] = api_key.strip()
                    
                    with open(configs_path, 'w', encoding='utf-8') as f:
                        json.dump(configs, f, indent=2, ensure_ascii=False)
            except Exception:
                pass
        
        # Cập nhật Preferences để Chrome nhận diện extension
        try:
            prefs_path = os.path.join(profile_path, "Default", "Preferences")
            if os.path.exists(prefs_path):
                with open(prefs_path, 'r', encoding='utf-8') as f:
                    prefs = json.load(f)
                
                if 'extensions' not in prefs:
                    prefs['extensions'] = {}
                if 'settings' not in prefs['extensions']:
                    prefs['extensions']['settings'] = {}
                
                # Thêm extension vào settings nếu chưa có hoặc cập nhật nếu đã có
                current_time_us = str(int(time.time() * 10000000))
                
                # Đọc permissions từ manifest
                manifest_permissions = manifest.get('permissions', [])
                host_permissions = manifest.get('host_permissions', [])
                
                # Tạo granted_permissions và active_permissions từ manifest
                granted_perms = {
                    "api": manifest_permissions.copy(),
                    "explicit_host": host_permissions.copy() if isinstance(host_permissions, list) else [],
                    "manifest_permissions": [],
                    "scriptable_host": []
                }
                
                # Thêm scriptable_host từ content_scripts
                content_scripts = manifest.get('content_scripts', [])
                scriptable_hosts = set()
                for script in content_scripts:
                    matches = script.get('matches', [])
                    scriptable_hosts.update(matches)
                granted_perms["scriptable_host"] = list(scriptable_hosts)
                
                # Đảm bảo active_permissions giống granted_permissions
                active_perms = {
                    "api": granted_perms["api"].copy(),
                    "explicit_host": granted_perms["explicit_host"].copy(),
                    "manifest_permissions": [],
                    "scriptable_host": granted_perms["scriptable_host"].copy()
                }
                
                if extension_id not in prefs['extensions']['settings']:
                    prefs['extensions']['settings'][extension_id] = {
                        "creation_flags": 9,
                        "first_install_time": current_time_us,
                        "last_update_time": current_time_us,
                        "location": 1,
                        "disable_reasons": [],  # Extension được enable
                        "granted_permissions": granted_perms,
                        "active_permissions": active_perms,
                        "withholding_permissions": False,  # Không giữ lại permissions
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
                        "preferences": {},
                        "regular_only_preferences": {},
                        "serviceworkerevents": [],
                        "manifest": manifest,
                        "path": f"{extension_id}\\{version}_0"  # Đúng format với _0
                    }
                else:
                    # Cập nhật extension đã có - đảm bảo enable và permissions đúng
                    ext_settings = prefs['extensions']['settings'][extension_id]
                    ext_settings["disable_reasons"] = []  # Enable extension
                    ext_settings["withholding_permissions"] = False  # Grant permissions
                    ext_settings["granted_permissions"] = granted_perms
                    ext_settings["active_permissions"] = active_perms
                    ext_settings["last_update_time"] = current_time_us
                    ext_settings["path"] = f"{extension_id}\\{version}_0"
                    if "manifest" not in ext_settings:
                        ext_settings["manifest"] = manifest
                
                # Lưu Preferences
                with open(prefs_path, 'w', encoding='utf-8') as f:
                    json.dump(prefs, f, indent=2, ensure_ascii=False)
                
                return True, f"Extension đã được cài đặt và cập nhật Preferences (version {version})"
            else:
                return True, f"Extension đã được copy (version {version}), nhưng không tìm thấy Preferences để cập nhật"
        except Exception as e:
            return True, f"Extension đã được copy (version {version}), nhưng lỗi khi cập nhật Preferences: {str(e)}"
    
    except Exception as e:
        return False, f"Lỗi khi cài đặt extension: {str(e)}"


def set_omocaptcha_api_key_for_profile(manager, profile_name, api_key, extension_id=None, force=False):
    """
    Lưu OMOcaptcha API key vào extension configs.json cho profile.
    Extension đọc API key từ file configs.json trong extension folder.
    
    Args:
        manager: ChromeProfileManager instance
        profile_name: Tên profile
        api_key: OMOcaptcha API key
        extension_id: Extension ID (nếu None sẽ tự động lấy)
        force: Bỏ qua kiểm tra Chrome đang chạy (dùng cho bulk run)
    
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        if not api_key or not api_key.strip():
            return False, "API key không được để trống"
        
        if extension_id is None:
            extension_id = get_omocaptcha_extension_id(manager)
        
        profile_path = manager.get_profile_path(profile_name)
        if not profile_path or not os.path.exists(profile_path):
            return False, f"Profile path not found: {profile_name}"
        
        # Kiểm tra Chrome có đang chạy không (trừ khi force=True)
        if not force:
            devtools_flag = os.path.join(profile_path, 'DevToolsActivePort')
            if os.path.exists(devtools_flag):
                return False, "Chrome đang chạy với profile này. Vui lòng đóng Chrome trước khi lưu API key."
        
        # Tìm extension folder
        ext_base_dir = os.path.join(profile_path, "Default", "Extensions", extension_id)
        
        if not os.path.exists(ext_base_dir):
            return False, f"Extension chưa được cài đặt trong profile"
        
        # Tìm version folder
        try:
            versions = [d for d in os.listdir(ext_base_dir) 
                       if os.path.isdir(os.path.join(ext_base_dir, d))]
            
            if not versions:
                return False, "Không tìm thấy version folder của extension"
            
            # Lấy version mới nhất
            versions.sort(reverse=True)
            version_dir = os.path.join(ext_base_dir, versions[0])
            
            # Đường dẫn đến configs.json
            configs_path = os.path.join(version_dir, "configs.json")
            
            if not os.path.exists(configs_path):
                return False, f"Không tìm thấy configs.json trong extension"
            
            # Đọc configs.json
            with open(configs_path, 'r', encoding='utf-8') as f:
                configs = json.load(f)
            
            # Update API key
            configs['api_key'] = api_key.strip()
            
            # Lưu lại configs.json
            with open(configs_path, 'w', encoding='utf-8') as f:
                json.dump(configs, f, indent=2, ensure_ascii=False)
            
            # Xóa chrome.storage để extension đọc lại configs.json khi Chrome khởi động
            try:
                storage_path = os.path.join(profile_path, "Default", "Local Extension Settings", extension_id)
                if os.path.exists(storage_path):
                    shutil.rmtree(storage_path)
            except Exception:
                pass
            
            return True, f"Đã lưu API key vào configs.json (version {versions[0]})"
            
        except Exception as e:
            return False, f"Lỗi khi update configs.json: {str(e)}"
    
    except Exception as e:
        return False, f"Lỗi khi lưu API key: {str(e)}"


def test_omocaptcha_setup(manager, profile_name, api_key, auto_install=True, extension_id=None):
    """
    Test cài đặt OMOcaptcha extension và lưu API key.
    
    Args:
        manager: ChromeProfileManager instance
        profile_name: Tên profile để test
        api_key: OMOcaptcha API key (có thể để trống nếu chỉ test cài extension)
        auto_install: Có tự động cài extension không
        extension_id: Extension ID (nếu None sẽ tự động lấy)
    
    Returns:
        dict: {
            'success': bool,
            'messages': list[str],
            'install_result': tuple or None,
            'key_result': tuple or None
        }
    """
    result = {
        'success': True,
        'messages': [],
        'install_result': None,
        'key_result': None
    }
    
    try:
        if extension_id is None:
            extension_id = get_omocaptcha_extension_id(manager)
        
        result['messages'].append(f"Profile: {profile_name}")
        result['messages'].append(f"Extension ID: {extension_id}")
        
        # Bước 1: Kiểm tra extension đã được cài chưa
        from core.tiles.tile_extension_management import check_extension_installed
        extension_already_installed = check_extension_installed(manager, profile_name, extension_id)
        if extension_already_installed:
            result['messages'].append(f"✅ Extension đã được cài đặt trước đó")
        else:
            result['messages'].append(f"ℹ️ Extension chưa được cài đặt")
        
        # Bước 2: Cài extension nếu được yêu cầu
        if auto_install:
            if extension_already_installed:
                result['messages'].append("ℹ️ Extension đã có, sẽ cài đặt lại để đảm bảo đúng cấu trúc")
            
            # Truyền api_key để inject ngay khi cài extension
            install_ok, install_msg = install_omocaptcha_extension_local(
                manager, profile_name, extension_id, force=False, api_key=api_key
            )
            result['install_result'] = (install_ok, install_msg)
            if install_ok:
                result['messages'].append(f"✅ Cài extension: {install_msg}")
                
                # Verify extension sau khi cài
                verify_installed = check_extension_installed(manager, profile_name, extension_id)
                if verify_installed:
                    result['messages'].append(f"✅ Xác nhận: Extension đã được cài đặt và Chrome nhận diện")
                else:
                    result['messages'].append(f"⚠️ Cảnh báo: Extension đã copy nhưng Chrome chưa nhận diện (có thể cần khởi động lại Chrome)")
            else:
                result['messages'].append(f"⚠️ Cài extension: {install_msg}")
                result['success'] = False
        else:
            result['messages'].append("ℹ️ Bỏ qua bước cài extension (vui lòng bật auto_install nếu muốn cài).")
        
        # Bước 3: Lưu API key nếu có
        if api_key and api_key.strip():
            key_ok, key_msg = set_omocaptcha_api_key_for_profile(manager, profile_name, api_key.strip(), extension_id)
            result['key_result'] = (key_ok, key_msg)
            if key_ok:
                result['messages'].append(f"✅ Lưu API key: {key_msg}")
            else:
                result['messages'].append(f"⚠️ Lưu API key: {key_msg}")
                if not key_ok:
                    result['success'] = False
        else:
            result['messages'].append("ℹ️ Chưa nhập API key nên bỏ qua bước lưu key.")
        
        # Tóm tắt kết quả
        if result['success']:
            result['messages'].append("")
            result['messages'].append("✅ Tất cả các bước đã hoàn thành thành công!")
        else:
            result['messages'].append("")
            result['messages'].append("⚠️ Có một số bước chưa thành công. Vui lòng kiểm tra lại.")
        
        return result
    
    except Exception as e:
        result['success'] = False
        result['messages'].append(f"❌ Lỗi: {str(e)}")
        return result


def setup_omocaptcha_for_bulk_run(manager, profile_name, api_key, auto_install=True, extension_id=None):
    """
    Thiết lập OMOcaptcha cho một profile trong bulk run.
    Tương tự test_omocaptcha_setup nhưng tối ưu cho bulk run (ít log hơn).
    
    QUAN TRỌNG: Function này được gọi TRƯỚC KHI mở Chrome, nên không cần force=True
    
    Args:
        manager: ChromeProfileManager instance
        profile_name: Tên profile
        api_key: OMOcaptcha API key
        auto_install: Có tự động cài extension không
        extension_id: Extension ID (nếu None sẽ tự động lấy)
    
    Returns:
        tuple: (install_success: bool, key_success: bool, messages: list)
    """
    install_success = False
    key_success = False
    messages = []
    
    try:
        if extension_id is None:
            extension_id = get_omocaptcha_extension_id(manager)
        
        # Đảm bảo Chrome đã đóng hoàn toàn trước khi cài extension
        profile_path = manager.get_profile_path(profile_name)
        if profile_path:
            devtools_flag = os.path.join(profile_path, 'DevToolsActivePort')
            if os.path.exists(devtools_flag):
                try:
                    os.remove(devtools_flag)
                    time.sleep(0.3)  # Đợi một chút để đảm bảo file đã bị xóa
                except Exception:
                    pass
        
        # Cài extension nếu được yêu cầu (truyền api_key để inject ngay)
        if auto_install and api_key:
            install_ok, install_msg = install_omocaptcha_extension_local(
                manager, profile_name, extension_id, force=False, api_key=api_key
            )
            install_success = install_ok
            if not install_ok:
                messages.append(f"⚠️ Cài extension: {install_msg}")
        
        # Lưu API key
        if api_key and api_key.strip():
            key_ok, key_msg = set_omocaptcha_api_key_for_profile(manager, profile_name, api_key.strip(), extension_id)
            key_success = key_ok
            if not key_ok:
                messages.append(f"⚠️ Lưu API key: {key_msg}")
        
        return install_success, key_success, messages
    
    except Exception as e:
        messages.append(f"❌ Lỗi: {str(e)}")
        return False, False, messages

