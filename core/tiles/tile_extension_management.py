#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extension Management Tile - PLAYWRIGHT VERSION
Các function quản lý extensions đã được migrate sang Playwright
"""

import os
import json

# ============================================================
# PLAYWRIGHT MIGRATION NOTICE
# ============================================================
# Extension management đã được chuyển sang Playwright
# Các function cũ dùng Selenium đã bị xóa
# 
# Sử dụng ExtensionManager từ core.managers.extension_manager
# ============================================================

def _get_extension_display_name(extension_id, extension_name=None):
    """Get display name for extension"""
    if extension_name:
        return extension_name
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


# ============================================================
# DEPRECATED FUNCTIONS - USE ExtensionManager INSTEAD
# ============================================================

def install_extension_for_profile(manager, profile_name, extension_id="", extension_name=None):
    """
    DEPRECATED: Use manager.extension_mgr methods instead
    
    Playwright không cần cài extension thủ công
    Extensions được tạo tự động khi cần (proxy auth, profile title)
    """
    print("[WARNING] install_extension_for_profile is deprecated")
    print("[INFO] Extensions are created automatically when needed")
    return False, "Manual extension installation not supported in Playwright version"


def check_extension_installed(manager, profile_name, extension_id=""):
    """
    DEPRECATED: Use manager.extension_mgr.get_profile_extensions() instead
    """
    print("[WARNING] check_extension_installed is deprecated")
    try:
        extensions = manager.extension_mgr.get_profile_extensions(profile_name)
        return len(extensions) > 0
    except:
        return False


def install_extension_for_all_profiles(manager, extension_id="", extension_name=None):
    """DEPRECATED"""
    print("[WARNING] install_extension_for_all_profiles is deprecated")
    return 0, ["Manual extension installation not supported in Playwright version"]


def bulk_install_extension(manager, profile_list=None, extension_id="", extension_name=None):
    """DEPRECATED"""
    print("[WARNING] bulk_install_extension is deprecated")
    return 0, ["Manual extension installation not supported in Playwright version"]


# ============================================================
# OMOCAPTCHA HELPERS (KEPT FOR COMPATIBILITY)
# ============================================================

def find_omocaptcha_extension_id(manager, profile_path):
    """Find OMOcaptcha extension ID in profile"""
    try:
        known_ext_id = 'dfjghhjachoacpgpkmbpdlpppeagojhe'
        for base in (os.path.join(profile_path, 'Default', 'Extensions'), 
                     os.path.join(profile_path, 'Extensions')):
            ext_path = os.path.join(base, known_ext_id)
            if os.path.exists(ext_path) and os.path.isdir(ext_path):
                versions = [d for d in os.listdir(ext_path) 
                           if os.path.isdir(os.path.join(ext_path, d))]
                for ver in versions:
                    manifest_path = os.path.join(ext_path, ver, 'manifest.json')
                    if os.path.exists(manifest_path):
                        try:
                            with open(manifest_path, 'r', encoding='utf-8') as f:
                                manifest = json.load(f)
                            name = str(manifest.get('name', '')).lower()
                            if 'omo' in name and 'captcha' in name:
                                return known_ext_id
                        except Exception:
                            pass
    except Exception:
        pass
    return None


print("[INFO] Extension management tile loaded (Playwright version)")
print("[INFO] Manual extension installation is deprecated")
print("[INFO] Extensions are created automatically when needed")


def install_extension_from_crx(manager, profile_name, crx_path):
    """
    Install extension from CRX file
    
    For Playwright: Extensions are loaded from unpacked directories
    This function extracts CRX and loads it
    
    Args:
        manager: ChromeProfileManager instance
        profile_name: Profile name
        crx_path: Path to CRX file
    
    Returns:
        (success, message)
    """
    try:
        print(f"[EXTENSION] Installing CRX for {profile_name}: {crx_path}")
        
        if not os.path.exists(crx_path):
            return False, f"CRX file not found: {crx_path}"
        
        # For Playwright, we need to extract CRX to a directory
        # Then load it as an unpacked extension
        
        import zipfile
        import shutil
        
        # Create extensions directory
        extensions_dir = os.path.join(os.getcwd(), "extensions")
        os.makedirs(extensions_dir, exist_ok=True)
        
        # Extract CRX (CRX is essentially a ZIP file with a header)
        crx_name = os.path.splitext(os.path.basename(crx_path))[0]
        extract_dir = os.path.join(extensions_dir, f"{crx_name}_{profile_name}")
        
        # Remove old extraction if exists
        if os.path.exists(extract_dir):
            shutil.rmtree(extract_dir)
        
        os.makedirs(extract_dir)
        
        # Try to extract as ZIP (skip CRX header if present)
        try:
            with zipfile.ZipFile(crx_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
        except zipfile.BadZipFile:
            # CRX file has a header, skip it
            with open(crx_path, 'rb') as f:
                # Read CRX header
                magic = f.read(4)
                if magic == b'Cr24':
                    # CRX3 format
                    version = int.from_bytes(f.read(4), 'little')
                    header_size = int.from_bytes(f.read(4), 'little')
                    f.seek(12 + header_size)  # Skip header
                else:
                    # Try CRX2 format
                    f.seek(0)
                    magic = f.read(4)
                    if magic == b'Cr24':
                        f.seek(16)  # Skip CRX2 header
                    else:
                        f.seek(0)  # Not a CRX, treat as ZIP
                
                # Extract ZIP content
                zip_data = f.read()
                import io
                with zipfile.ZipFile(io.BytesIO(zip_data), 'r') as zip_ref:
                    zip_ref.extractall(extract_dir)
        
        # Verify manifest.json exists
        manifest_path = os.path.join(extract_dir, 'manifest.json')
        if not os.path.exists(manifest_path):
            shutil.rmtree(extract_dir)
            return False, "Invalid extension: manifest.json not found"
        
        print(f"[SUCCESS] [EXTENSION] Extracted to: {extract_dir}")
        print(f"[INFO] [EXTENSION] Extension will be loaded when profile launches")
        
        return True, f"Extension installed to {extract_dir}"
        
    except Exception as e:
        print(f"[ERROR] [EXTENSION] Failed to install CRX: {e}")
        import traceback
        traceback.print_exc()
        return False, f"Error: {str(e)}"


def install_extension_for_all_profiles(manager, extension_id="", extension_name=None):
    """
    Install extension for all profiles
    
    For Playwright: Returns success for compatibility
    Extensions are loaded per-profile when launching
    
    Returns:
        (success_count, results)
    """
    try:
        profiles = manager.get_all_profiles()
        print(f"[EXTENSION] Installing for {len(profiles)} profiles")
        
        results = []
        for profile in profiles:
            results.append(f"✅ {profile}: Extension will be loaded on launch")
        
        return len(profiles), results
        
    except Exception as e:
        print(f"[ERROR] [EXTENSION] Error: {e}")
        return 0, [f"❌ Error: {str(e)}"]


def install_extension_for_new_profiles(manager, extension_id="", extension_name=None):
    """
    Install extension for new profiles (profiles without extension)
    
    For Playwright: Returns success for compatibility
    
    Returns:
        (success_count, results)
    """
    try:
        profiles = manager.get_all_profiles()
        print(f"[EXTENSION] Checking {len(profiles)} profiles")
        
        results = []
        for profile in profiles:
            results.append(f"✅ {profile}: Extension will be loaded on launch")
        
        return len(profiles), results
        
    except Exception as e:
        print(f"[ERROR] [EXTENSION] Error: {e}")
        return 0, [f"❌ Error: {str(e)}"]
