#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mode Profiles - Set width/height for Chrome profiles
Lưu và load cấu hình width/height cho từng profile
"""

import os
import json
from typing import Optional, Tuple, Dict

# Default config file
CONFIG_FILE = "profile_modes.json"


def load_profile_modes() -> Dict[str, Dict[str, int]]:
    """
    Load profile modes từ file JSON
    
    Returns:
        Dict với format: {
            "profile_name": {"width": 360, "height": 640, "size_index": 0},
            ...
        }
    """
    if not os.path.exists(CONFIG_FILE):
        return {}
    
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"[ERROR] Cannot load {CONFIG_FILE}: {e}")
        return {}


def save_profile_modes(modes: Dict[str, Dict[str, int]]) -> bool:
    """
    Save profile modes vào file JSON
    
    Args:
        modes: Dict với format như load_profile_modes()
    
    Returns:
        True nếu save thành công
    """
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(modes, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"[ERROR] Cannot save {CONFIG_FILE}: {e}")
        return False


def set_profile_mode(profile_name: str, width: int, height: int, size_index: int = 0) -> bool:
    """
    Set width/height cho một profile
    
    Args:
        profile_name: Tên profile
        width: Chiều rộng viewport
        height: Chiều cao viewport
        size_index: Index của size trong SIZES list (optional)
    
    Returns:
        True nếu set thành công
    """
    modes = load_profile_modes()
    
    modes[profile_name] = {
        "width": width,
        "height": height,
        "size_index": size_index
    }
    
    success = save_profile_modes(modes)
    
    if success:
        print(f"[OK] Set mode for {profile_name}: {width}x{height} (index: {size_index})")
    
    return success


def get_profile_mode(profile_name: str) -> Optional[Tuple[int, int, int]]:
    """
    Get width/height cho một profile
    
    Args:
        profile_name: Tên profile
    
    Returns:
        Tuple (width, height, size_index) hoặc None nếu không có config
    """
    modes = load_profile_modes()
    
    if profile_name not in modes:
        return None
    
    mode = modes[profile_name]
    return (mode.get("width", 360), mode.get("height", 640), mode.get("size_index", 0))


def delete_profile_mode(profile_name: str) -> bool:
    """
    Xóa config cho một profile
    
    Args:
        profile_name: Tên profile
    
    Returns:
        True nếu xóa thành công
    """
    modes = load_profile_modes()
    
    if profile_name in modes:
        del modes[profile_name]
        success = save_profile_modes(modes)
        
        if success:
            print(f"[OK] Deleted mode for {profile_name}")
        
        return success
    
    return False


def list_profile_modes() -> Dict[str, Dict[str, int]]:
    """
    List tất cả profile modes
    
    Returns:
        Dict với format như load_profile_modes()
    """
    return load_profile_modes()


def set_bulk_profile_modes(profiles: list, width: int, height: int, size_index: int = 0) -> int:
    """
    Set width/height cho nhiều profiles cùng lúc
    
    Args:
        profiles: List tên profiles
        width: Chiều rộng viewport
        height: Chiều cao viewport
        size_index: Index của size trong SIZES list
    
    Returns:
        Số lượng profiles đã set thành công
    """
    modes = load_profile_modes()
    
    count = 0
    for profile_name in profiles:
        modes[profile_name] = {
            "width": width,
            "height": height,
            "size_index": size_index
        }
        count += 1
    
    if save_profile_modes(modes):
        print(f"[OK] Set mode for {count} profiles: {width}x{height} (index: {size_index})")
        return count
    
    return 0


def get_profile_size_index(profile_name: str, default: int = 0) -> int:
    """
    Get size_index cho một profile (để dùng với mobile_mode.py)
    
    Args:
        profile_name: Tên profile
        default: Giá trị mặc định nếu không có config
    
    Returns:
        size_index (int)
    """
    mode = get_profile_mode(profile_name)
    
    if mode is None:
        return default
    
    return mode[2]  # Return size_index


# ============================================================
# CLI USAGE (nếu chạy trực tiếp)
# ============================================================

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python mode_profiles.py set <profile_name> <width> <height> [size_index]")
        print("  python mode_profiles.py get <profile_name>")
        print("  python mode_profiles.py delete <profile_name>")
        print("  python mode_profiles.py list")
        print("\nExamples:")
        print("  python mode_profiles.py set profile001 360 640 0")
        print("  python mode_profiles.py get profile001")
        print("  python mode_profiles.py list")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "set":
        if len(sys.argv) < 5:
            print("Error: Missing arguments for 'set'")
            print("Usage: python mode_profiles.py set <profile_name> <width> <height> [size_index]")
            sys.exit(1)
        
        profile_name = sys.argv[2]
        width = int(sys.argv[3])
        height = int(sys.argv[4])
        size_index = int(sys.argv[5]) if len(sys.argv) > 5 else 0
        
        set_profile_mode(profile_name, width, height, size_index)
    
    elif command == "get":
        if len(sys.argv) < 3:
            print("Error: Missing profile_name")
            print("Usage: python mode_profiles.py get <profile_name>")
            sys.exit(1)
        
        profile_name = sys.argv[2]
        mode = get_profile_mode(profile_name)
        
        if mode:
            print(f"Profile: {profile_name}")
            print(f"  Width: {mode[0]}")
            print(f"  Height: {mode[1]}")
            print(f"  Size Index: {mode[2]}")
        else:
            print(f"No config found for {profile_name}")
    
    elif command == "delete":
        if len(sys.argv) < 3:
            print("Error: Missing profile_name")
            print("Usage: python mode_profiles.py delete <profile_name>")
            sys.exit(1)
        
        profile_name = sys.argv[2]
        delete_profile_mode(profile_name)
    
    elif command == "list":
        modes = list_profile_modes()
        
        if not modes:
            print("No profile modes configured")
        else:
            print(f"Total profiles: {len(modes)}\n")
            for profile_name, mode in modes.items():
                print(f"{profile_name}:")
                print(f"  {mode['width']}x{mode['height']} (index: {mode.get('size_index', 0)})")
    
    else:
        print(f"Unknown command: {command}")
        print("Available commands: set, get, delete, list")
        sys.exit(1)
