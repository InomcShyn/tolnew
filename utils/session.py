#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Session utilities - Cache và session management
Converted from core/tiles/tile_session_management.py
"""

import os
import shutil
from pathlib import Path
from typing import Optional


def clear_profile_name_cache(profile_path: Path):
    """Clear profile name cache"""
    try:
        # Clear Preferences cache
        prefs_file = profile_path / "Default" / "Preferences"
        if prefs_file.exists():
            import json
            with open(prefs_file, 'r', encoding='utf-8') as f:
                prefs = json.load(f)
            
            # Clear profile name
            if 'profile' in prefs:
                prefs['profile'].pop('name', None)
            
            with open(prefs_file, 'w', encoding='utf-8') as f:
                json.dump(prefs, f, indent=2)
    except Exception as e:
        print(f"Error clearing profile name cache: {e}")


def clear_proxy_credentials_cache(profile_path: Path):
    """Clear proxy credentials cache"""
    try:
        # Clear Login Data
        login_data = profile_path / "Default" / "Login Data"
        if login_data.exists():
            os.remove(login_data)
        
        # Clear Network cache
        network_cache = profile_path / "Default" / "Network"
        if network_cache.exists():
            shutil.rmtree(network_cache, ignore_errors=True)
    except Exception as e:
        print(f"Error clearing proxy credentials: {e}")


def clear_browsing_data(profile_path: Path, clear_history: bool = True, clear_cache: bool = False):
    """
    Clear browsing data
    
    Args:
        profile_path: Path to profile
        clear_history: Clear history
        clear_cache: Clear cache
    """
    try:
        default_path = profile_path / "Default"
        
        if clear_history:
            # Clear History
            history_file = default_path / "History"
            if history_file.exists():
                os.remove(history_file)
            
            # Clear History-journal
            history_journal = default_path / "History-journal"
            if history_journal.exists():
                os.remove(history_journal)
        
        if clear_cache:
            # Clear Cache
            cache_dir = default_path / "Cache"
            if cache_dir.exists():
                shutil.rmtree(cache_dir, ignore_errors=True)
            
            # Clear Code Cache
            code_cache = default_path / "Code Cache"
            if code_cache.exists():
                shutil.rmtree(code_cache, ignore_errors=True)
    
    except Exception as e:
        print(f"Error clearing browsing data: {e}")
