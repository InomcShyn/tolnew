#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chrome Flags Tile - Anti-detection flags for Playwright
Extracted from chrome_manager.py
"""


def get_antidetect_chrome_flags() -> list:
    """
    Lấy danh sách Chrome flags for antidetect
    
    Chỉ giữ flags cần thiết nhất như GPM Login để:
    - Ẩn automation detection
    - Tối ưu performance
    - Tương thích với anti-detect browsers
    
    Returns:
        List of Chrome command line flags
    """
    return [
        # Core anti-detection
        "--disable-blink-features=AutomationControlled",
        
        # ✅ FIX: Allow extension installation from outside Chrome Web Store
        "--enable-easy-off-store-extension-install",
        "--disable-component-extensions-with-background-pages",
        "--disable-features=ExtensionInstallVerification,InfiniteSessionRestore,SessionRestore,AudioServiceOutOfProcess",
        
        # Basic settings
        "--no-default-browser-check",
        "--password-store=basic",
        "--no-first-run",
        
        # Disable restore pages popup (multiple flags for complete disable)
        "--disable-session-crashed-bubble",
        "--disable-infobars",
        "--hide-crash-restore-bubble",
        "--restore-last-session=0",
        "--disable-restore-session-state",
        "--disable-restore-background-contents",
        
        # Disable unnecessary features (performance)
        "--disable-background-networking",
        "--disable-background-timer-throttling",
        "--disable-backgrounding-occluded-windows",
        "--disable-breakpad",
        "--disable-client-side-phishing-detection",
        "--disable-component-update",
        "--disable-default-apps",
        "--disable-dev-shm-usage",
        "--disable-domain-reliability",
        "--disable-hang-monitor",
        "--disable-ipc-flooding-protection",
        "--disable-notifications",
        "--disable-offer-store-unmasked-wallet-cards",
        "--disable-popup-blocking",
        "--disable-print-preview",
        "--disable-prompt-on-repost",
        "--disable-renderer-backgrounding",
        "--disable-setuid-sandbox",
        "--disable-speech-api",
        "--disable-sync",
        "--hide-scrollbars",
        "--ignore-gpu-blacklist",
        "--metrics-recording-only",
        "--mute-audio",
        "--no-first-run",
        "--no-pings",
        "--no-sandbox",
        "--no-zygote",
        "--safebrowsing-disable-auto-update",
    ]


def get_gpm_style_flags() -> list:
    """
    GPM-style flags - Minimal và clean như GPM Browser thực tế
    Dựa trên command line của GPM Browser:
    --user-data-dir --lang --password-store=basic --gpm-disable-machine-id 
    --user-agent --no-default-browser-check --load-extension 
    --gpm-use-pref-tracking-config-before-v137 --flag-switches-begin 
    --flag-switches-end --origin-trial-disabled-features
    
    Returns:
        List of Chrome command line flags (GPM style - MINIMAL)
    """
    return [
        # Core anti-detection (QUAN TRỌNG - ẩn automation)
        "--disable-blink-features=AutomationControlled",
        
        # Basic settings (giống GPM)
        "--no-default-browser-check",
        "--password-store=basic",
        
        # ✅ FIX: Allow extension installation (QUAN TRỌNG!)
        # GPM không có flag này vì GPM dùng signed extensions
        # Nhưng chúng ta cần nó để cài extensions từ Chrome Web Store
        "--disable-features=ExtensionInstallVerification",
        
        # Flag switches (giống GPM)
        "--flag-switches-begin",
        "--flag-switches-end",
    ]


def get_minimal_antidetect_flags() -> list:
    """
    Minimal flags - chỉ những flags quan trọng nhất
    Dùng khi cần performance tối đa
    
    Returns:
        List of essential Chrome flags
    """
    return [
        "--disable-blink-features=AutomationControlled",
        "--no-default-browser-check",
        "--password-store=basic",
        "--no-sandbox",
        "--disable-dev-shm-usage",
    ]


def get_gpm_compatible_flags() -> list:
    """
    Flags tương thích với GPM Browser
    Giống như GPM Login sử dụng
    
    Returns:
        List of GPM-compatible Chrome flags
    """
    return [
        "--disable-blink-features=AutomationControlled",
        "--no-default-browser-check",
        "--password-store=basic",
        "--disable-background-networking",
        "--disable-client-side-phishing-detection",
        "--disable-default-apps",
        "--disable-dev-shm-usage",
        "--disable-hang-monitor",
        "--disable-popup-blocking",
        "--disable-prompt-on-repost",
        "--disable-sync",
        "--no-first-run",
        "--no-sandbox",
    ]


def get_stealth_flags() -> list:
    """
    Stealth flags - tối đa hóa anti-detection
    Dùng khi cần stealth cao nhất
    
    Returns:
        List of stealth Chrome flags
    """
    return [
        # Anti-detection core
        "--disable-blink-features=AutomationControlled",
        
        # Hide automation
        "--disable-automation",
        "--disable-infobars",
        
        # Basic
        "--no-default-browser-check",
        "--password-store=basic",
        
        # Disable tracking
        "--disable-background-networking",
        "--disable-background-timer-throttling",
        "--disable-backgrounding-occluded-windows",
        "--disable-breakpad",
        "--disable-client-side-phishing-detection",
        "--disable-component-update",
        "--disable-default-apps",
        "--disable-dev-shm-usage",
        "--disable-domain-reliability",
        "--disable-features=AudioServiceOutOfProcess,IsolateOrigins,site-per-process",
        "--disable-hang-monitor",
        "--disable-ipc-flooding-protection",
        "--disable-notifications",
        "--disable-offer-store-unmasked-wallet-cards",
        "--disable-popup-blocking",
        "--disable-print-preview",
        "--disable-prompt-on-repost",
        "--disable-renderer-backgrounding",
        "--disable-setuid-sandbox",
        "--disable-speech-api",
        "--disable-sync",
        # ❌ REMOVED: "--disable-web-security" (gây ra "Not Secure" warning)
        "--hide-scrollbars",
        
        # SSL/HTTPS bypass (chỉ giữ flags cần thiết, không gây warning)
        # ❌ REMOVED: "--test-type" (gây ra security warning)
        "--ignore-certificate-errors",
        "--ignore-certificate-errors-spki-list",
        # ❌ REMOVED: "--ignore-ssl-errors" (trùng với ignore-certificate-errors)
        "--allow-insecure-localhost",
        # ❌ REMOVED: "--allow-running-insecure-content" (gây ra warning)
        # ❌ REMOVED: "--disable-features=IsolateOrigins,site-per-process" (gây ra warning)
        # ❌ REMOVED: "--disable-site-isolation-trials" (gây ra warning)
        
        "--ignore-gpu-blacklist",
        "--metrics-recording-only",
        "--mute-audio",
        "--no-first-run",
        "--no-pings",
        "--no-sandbox",
        "--no-zygote",
        "--safebrowsing-disable-auto-update",
        
        # WebRTC
        "--force-webrtc-ip-handling-policy=default_public_interface_only",
        "--enforce-webrtc-ip-permission-check",
    ]


def get_flags_for_profile(profile_settings: dict = None, mode: str = "gpm_style") -> list:
    """
    Get Chrome flags based on profile settings and mode
    
    Args:
        profile_settings: Profile settings dict (optional)
        mode: Flag mode - "minimal", "balanced", "gpm", "gpm_style", "stealth"
    
    Returns:
        List of Chrome flags
    """
    # Check profile settings for custom flags
    if profile_settings:
        custom_flags = profile_settings.get('chrome_flags')
        if custom_flags:
            return custom_flags
        
        # Check for stealth mode
        if profile_settings.get('stealth_mode'):
            mode = "stealth"
    
    # Return flags based on mode
    if mode == "minimal":
        return get_minimal_antidetect_flags()
    elif mode == "gpm":
        return get_gpm_compatible_flags()
    elif mode == "gpm_style":
        return get_gpm_style_flags()
    elif mode == "stealth":
        return get_stealth_flags()
    elif mode == "balanced":
        return get_antidetect_chrome_flags()
    else:  # default to gpm_style
        return get_gpm_style_flags()


def merge_flags(base_flags: list, additional_flags: list) -> list:
    """
    Merge two flag lists, removing duplicates
    
    Args:
        base_flags: Base flags list
        additional_flags: Additional flags to add
    
    Returns:
        Merged list without duplicates
    """
    # Use dict to preserve order and remove duplicates
    merged = {}
    for flag in base_flags + additional_flags:
        # Extract flag name (before =)
        flag_name = flag.split('=')[0]
        merged[flag_name] = flag
    
    return list(merged.values())
