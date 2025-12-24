#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
User Agent Generator - Intelligent UA System (UPGRADED)
- Random user agents for browser
- Persistent UA per profile (save to profile/useragent.txt)
- Auto rotation when blocked by TikTok
- Login awareness (random during login, persistent during view)
- Block detection and auto-healing
- Validation and info extraction

UPGRADED: December 9, 2025
- Added persistence (save/load from file)
- Added block detection
- Added auto rotation
- Added validation
- Expanded UA pool (30+ UAs)
"""

import random
import re
import os
import time
from pathlib import Path
from typing import Optional, Tuple, Dict


def get_user_agent_for_chrome_version(chrome_version: str) -> str:
    """
    Generate user agent matching specific Chrome version
    
    Args:
        chrome_version: Chrome version (e.g., "119.0.6045.124")
    
    Returns:
        User agent string matching the Chrome version
    """
    # Extract major version (e.g., "119" from "119.0.6045.124")
    major_version = chrome_version.split('.')[0]
    
    # Use full version for UA (e.g., "119.0.0.0")
    ua_chrome_version = f"{major_version}.0.0.0"
    
    # Random Windows version
    windows_versions = [
        'Windows NT 10.0; Win64; x64',  # Windows 10/11
        'Windows NT 10.0; WOW64',       # Windows 10 32-bit on 64-bit
    ]
    windows_version = random.choice(windows_versions)
    
    # WebKit version (standard)
    webkit_version = '537.36'
    
    # Build user agent
    user_agent = (
        f'Mozilla/5.0 ({windows_version}) '
        f'AppleWebKit/{webkit_version} (KHTML, like Gecko) '
        f'Chrome/{ua_chrome_version} Safari/{webkit_version}'
    )
    
    return user_agent


def get_random_user_agent() -> str:
    """
    Generate random user agent string
    
    Returns:
        Random user agent string with varying Chrome versions
    """
    # Chrome versions (recent stable versions)
    chrome_versions = [
        '120.0.0.0',
        '121.0.0.0',
        '122.0.0.0',
        '123.0.0.0',
        '124.0.0.0',
        '125.0.0.0',
        '126.0.0.0',
        '127.0.0.0',
        '128.0.0.0',
        '129.0.0.0',
        '130.0.0.0',
        '131.0.0.0',
    ]
    
    # Windows versions
    windows_versions = [
        'Windows NT 10.0; Win64; x64',  # Windows 10/11
        'Windows NT 10.0; WOW64',       # Windows 10 32-bit on 64-bit
    ]
    
    # WebKit versions (recent)
    webkit_versions = [
        '537.36',
        '538.36',
        '539.36',
    ]
    
    # Random selections
    chrome_version = random.choice(chrome_versions)
    windows_version = random.choice(windows_versions)
    webkit_version = random.choice(webkit_versions)
    
    # Build user agent
    user_agent = (
        f'Mozilla/5.0 ({windows_version}) '
        f'AppleWebKit/{webkit_version} (KHTML, like Gecko) '
        f'Chrome/{chrome_version} Safari/{webkit_version}'
    )
    
    return user_agent


def get_user_agent_for_profile(profile_name: str) -> str:
    """
    Get consistent user agent for a profile
    Uses profile name as seed for consistency
    
    Args:
        profile_name: Profile name to generate consistent UA
        
    Returns:
        User agent string (same for same profile)
    """
    # Use profile name as seed for consistency
    seed = sum(ord(c) for c in profile_name)
    random.seed(seed)
    
    ua = get_random_user_agent()
    
    # Reset random seed
    random.seed()
    
    return ua


# ============================================================
# EXPANDED USER AGENTS POOL (Desktop Chrome - for LOGIN)
# UPGRADED: 30+ UAs, Chrome 118-135 (future-proof)
# ============================================================
USER_AGENTS_POOL = [
    # Windows 10/11 - Chrome 118-135
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36',
    
    # macOS - Chrome 120-135
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36',
    
    # Linux - Chrome 120-135
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
]


if __name__ == "__main__":
    # Test
    print("Random User Agents:")
    for i in range(5):
        print(f"{i+1}. {get_random_user_agent()}")
    
    print("\nConsistent User Agents (same profile):")
    for i in range(3):
        print(f"Profile 'test': {get_user_agent_for_profile('test')}")
    
    print("\nDifferent profiles:")
    for profile in ['P-001', 'P-002', 'P-003']:
        print(f"{profile}: {get_user_agent_for_profile(profile)}")



# ============================================================
# PERSISTENCE FUNCTIONS (NEW - UPGRADED)
# ============================================================

def get_ua_file_path(profile_path: str) -> Path:
    """
    Get path to useragent.txt file
    
    Args:
        profile_path: Path to profile directory
    
    Returns:
        Path to useragent.txt
    """
    if isinstance(profile_path, str):
        profile_path = Path(profile_path)
    
    return profile_path / 'useragent.txt'


def load_saved_ua(profile_path: str) -> Optional[str]:
    """
    Load saved UA from profile/useragent.txt
    
    Args:
        profile_path: Path to profile directory
    
    Returns:
        Saved UA string or None if not found
    """
    try:
        ua_file = get_ua_file_path(profile_path)
        
        if ua_file.exists():
            with open(ua_file, 'r', encoding='utf-8') as f:
                ua = f.read().strip()
            
            if ua:
                print(f"[UA] ✅ Loaded saved UA: {ua[:60]}...")
                return ua
        
        print(f"[UA] No saved UA found")
        return None
        
    except Exception as e:
        print(f"[UA] ⚠️ Error loading UA: {e}")
        return None


def save_ua_to_profile(profile_path: str, ua: str) -> bool:
    """
    Save UA to profile/useragent.txt
    
    Args:
        profile_path: Path to profile directory
        ua: User agent string to save
    
    Returns:
        True if saved successfully
    """
    try:
        ua_file = get_ua_file_path(profile_path)
        
        # Ensure profile directory exists
        ua_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(ua_file, 'w', encoding='utf-8') as f:
            f.write(ua)
        
        print(f"[UA] ✅ Saved UA: {ua[:60]}...")
        return True
        
    except Exception as e:
        print(f"[UA] ❌ Error saving UA: {e}")
        return False


# ============================================================
# BLOCK DETECTION (NEW - UPGRADED)
# ============================================================

def detect_ua_block(response_body: str = "", status_code: int = 200) -> bool:
    """
    Detect if TikTok blocked the request due to UA
    
    Args:
        response_body: HTML response body
        status_code: HTTP status code
    
    Returns:
        True if UA is blocked
    """
    try:
        # Check status code
        if status_code in [403, 429, 503]:
            print(f"[UA] ⚠️ Blocked status code: {status_code}")
            return True
        
        # Check response body for block indicators
        if not response_body:
            return False
        
        block_indicators = [
            'captcha',
            'access denied',
            'blocked',
            'forbidden',
            'verify you are human',
            'unusual activity',
            'suspicious activity',
            'bot detected',
            'automation detected',
            'too many requests',
            'rate limit',
        ]
        
        response_lower = response_body.lower()
        
        for indicator in block_indicators:
            if indicator in response_lower:
                print(f"[UA] ⚠️ Detected block indicator: {indicator}")
                return True
        
        return False
        
    except Exception as e:
        print(f"[UA] Error detecting block: {e}")
        return False


def rotate_ua_if_blocked(
    profile_path: str,
    response_body: str = "",
    status_code: int = 200,
    force_rotate: bool = False
) -> Tuple[bool, Optional[str]]:
    """
    Rotate UA if blocked by TikTok
    
    Args:
        profile_path: Path to profile directory
        response_body: HTML response body to check
        status_code: HTTP status code
        force_rotate: Force rotation even if not blocked
    
    Returns:
        (rotated: bool, new_ua: str or None)
    """
    try:
        # Check if blocked
        is_blocked = force_rotate or detect_ua_block(response_body, status_code)
        
        if not is_blocked:
            print(f"[UA] No block detected, keeping current UA")
            return False, None
        
        # Generate new UA
        new_ua = get_random_user_agent()
        
        # Save new UA
        if save_ua_to_profile(profile_path, new_ua):
            print(f"[UA] ✅ UA rotated successfully")
            return True, new_ua
        else:
            print(f"[UA] ❌ Failed to save new UA")
            return False, None
        
    except Exception as e:
        print(f"[UA] Error rotating UA: {e}")
        return False, None


# ============================================================
# SMART UA MANAGEMENT (NEW - UPGRADED)
# ============================================================

def get_or_create_ua_for_profile(profile_path: str, force_new: bool = False, chrome_version: Optional[str] = None) -> str:
    """
    Get saved UA or create new one (LOGIN AWARE)
    
    During LOGIN: Generate random UA
    After LOGIN: Use saved UA (persistent)
    
    Args:
        profile_path: Path to profile directory
        force_new: Force create new UA (for rotation)
        chrome_version: Chrome version to match (e.g., "119.0.6045.124")
                       If provided, generates UA matching this version
    
    Returns:
        UA string
    """
    try:
        # Try load saved UA (unless force_new)
        if not force_new:
            saved_ua = load_saved_ua(profile_path)
            if saved_ua:
                # If chrome_version provided, check if UA matches
                if chrome_version:
                    ua_info = get_ua_info(saved_ua)
                    saved_major = ua_info.get('chrome_version', '').split('.')[0] if ua_info.get('chrome_version') else None
                    target_major = chrome_version.split('.')[0]
                    
                    # If major version matches, use saved UA
                    if saved_major == target_major:
                        return saved_ua
                    else:
                        # Version mismatch, generate new UA matching chrome_version
                        print(f"[UA] Version mismatch (saved: {saved_major}, target: {target_major}), generating new UA")
                        force_new = True
                else:
                    return saved_ua
        
        # Generate new UA
        if chrome_version:
            # Generate UA matching Chrome version
            new_ua = get_user_agent_for_chrome_version(chrome_version)
            print(f"[UA] Generated UA matching Chrome {chrome_version}")
        else:
            # Generate random UA
            new_ua = get_random_user_agent()
        
        # Save it
        save_ua_to_profile(profile_path, new_ua)
        
        return new_ua
        
    except Exception as e:
        print(f"[UA] Error getting/creating UA: {e}")
        # Fallback
        if chrome_version:
            return get_user_agent_for_chrome_version(chrome_version)
        else:
            return get_random_user_agent()


# ============================================================
# VALIDATION & INFO EXTRACTION (NEW - UPGRADED)
# ============================================================

def validate_ua(ua: str) -> bool:
    """
    Validate UA string format
    
    Args:
        ua: User agent string
    
    Returns:
        True if valid
    """
    try:
        # Check basic format
        if not ua or len(ua) < 50:
            return False
        
        # Check contains Chrome
        if 'Chrome/' not in ua:
            return False
        
        # Check contains AppleWebKit
        if 'AppleWebKit/' not in ua:
            return False
        
        return True
        
    except Exception as e:
        print(f"[UA] Error validating UA: {e}")
        return False


def get_ua_info(ua: str) -> Dict:
    """
    Extract info from UA string
    
    Args:
        ua: User agent string
    
    Returns:
        Dict with UA info
    """
    try:
        info = {
            'ua': ua,
            'chrome_version': None,
            'os': None,
            'platform': None,
        }
        
        # Extract Chrome version
        chrome_match = re.search(r'Chrome/([\d.]+)', ua)
        if chrome_match:
            info['chrome_version'] = chrome_match.group(1)
        
        # Extract OS
        if 'Windows' in ua:
            info['os'] = 'Windows'
            info['platform'] = 'Win64'
        elif 'Macintosh' in ua:
            info['os'] = 'macOS'
            info['platform'] = 'Mac'
        elif 'Linux' in ua:
            info['os'] = 'Linux'
            info['platform'] = 'Linux'
        
        return info
        
    except Exception as e:
        print(f"[UA] Error extracting UA info: {e}")
        return {'ua': ua}


def print_ua_summary(profile_path: str):
    """
    Print UA summary for profile
    
    Args:
        profile_path: Path to profile directory
    """
    try:
        ua = load_saved_ua(profile_path)
        
        if not ua:
            print(f"[UA] No UA saved for profile")
            return
        
        info = get_ua_info(ua)
        
        print(f"\n{'='*70}")
        print(f"UA SUMMARY")
        print(f"{'='*70}")
        print(f"Profile: {Path(profile_path).name}")
        print(f"UA: {ua}")
        print(f"Chrome Version: {info.get('chrome_version', 'Unknown')}")
        print(f"OS: {info.get('os', 'Unknown')}")
        print(f"Platform: {info.get('platform', 'Unknown')}")
        print(f"{'='*70}\n")
        
    except Exception as e:
        print(f"[UA] Error printing summary: {e}")


# ============================================================
# MIGRATION HELPER (NEW - UPGRADED)
# ============================================================

def migrate_profile_to_persistent_ua(profile_path: str, profile_name: str) -> bool:
    """
    Migrate profile from seed-based UA to persistent UA
    
    Args:
        profile_path: Path to profile directory
        profile_name: Profile name (for seed-based UA)
    
    Returns:
        True if migrated successfully
    """
    try:
        # Check if already has saved UA
        if load_saved_ua(profile_path):
            print(f"[UA] Profile already has saved UA")
            return True
        
        # Generate UA using old seed-based method
        old_ua = get_user_agent_for_profile(profile_name)
        
        # Save it
        if save_ua_to_profile(profile_path, old_ua):
            print(f"[UA] ✅ Migrated profile to persistent UA")
            return True
        else:
            print(f"[UA] ❌ Failed to migrate profile")
            return False
        
    except Exception as e:
        print(f"[UA] Error migrating profile: {e}")
        return False


# ============================================================
# BACKWARD COMPATIBILITY (KEEP EXISTING FUNCTIONS)
# ============================================================

# get_random_user_agent() - ALREADY EXISTS ABOVE
# get_user_agent_for_profile() - ALREADY EXISTS ABOVE
# USER_AGENTS_POOL - ALREADY EXISTS ABOVE

# These functions are kept for backward compatibility
# New code should use get_or_create_ua_for_profile() instead
