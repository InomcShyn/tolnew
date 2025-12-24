#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mobile Mode - Playwright Chrome Mobile Emulation
Ultra low RAM configuration for mobile viewport
"""

import random
from playwright.async_api import async_playwright

# Mobile User-Agents (Android devices)
UAs = [
    "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 12; SM-S906N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 11; Redmi Note 8 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 12; M2102J20SG) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; Pixel 6a) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 11; SM-A515F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 12; Redmi Note 11) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 11; Mi 11 Lite) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Mobile Safari/537.36"
]

# Low RAM viewport sizes
SIZES = [
    (360, 640),
    (320, 480),
    (480, 800),
    (240, 320),
    (200, 300),
    (200, 400),
    (200, 200),
    (180, 240),
    (160, 240),
    (150, 150)
]


async def init_mobile_chrome(context_path: str, size_index: int):
    """
    Initialize Chrome in mobile mode with ultra low RAM configuration
    
    Args:
        context_path: Path to Chrome profile/context
        size_index: Index to select viewport size from SIZES list
    
    Returns:
        Tuple (browser_context, page)
    """
    # Validate and select size
    if size_index < 0 or size_index >= len(SIZES):
        size_index = 0  # Fallback to first size
    
    width, height = SIZES[size_index]
    
    # Random User-Agent
    ua_selected = random.choice(UAs)
    
    # Ultra low RAM flags
    args = [
        f"--window-size={width},{height}",
        "--force-device-scale-factor=1",
        "--high-dpi-support=0",
        "--disable-renderer-backgrounding",
        "--disable-background-timer-throttling",
        "--disable-backgrounding-occluded-windows",
        "--disable-dev-shm-usage",
        "--disable-gpu",
        "--no-sandbox",
        "--disable-setuid-sandbox",
        "--disable-web-security",
        "--disable-features=IsolateOrigins,site-per-process",
        "--disable-blink-features=AutomationControlled",
        "--disable-infobars",
        "--disable-notifications",
        "--disable-popup-blocking",
        "--disable-save-password-bubble",
        "--disable-translate",
        "--disable-sync",
        "--disable-background-networking",
        "--disable-default-apps",
        "--disable-extensions",
        "--disable-component-extensions-with-background-pages",
        "--mute-audio",
        "--no-first-run",
        "--no-default-browser-check",
        "--disable-hang-monitor",
        "--disable-prompt-on-repost",
        "--disable-domain-reliability",
        "--disable-component-update",
        "--disable-client-side-phishing-detection",
        "--disable-breakpad",
        "--metrics-recording-only",
        "--no-pings"
    ]
    
    # Launch Playwright
    playwright = await async_playwright().start()
    
    # Launch persistent context with mobile emulation
    browser = await playwright.chromium.launch_persistent_context(
        context_path,
        headless=False,
        args=args,
        user_agent=ua_selected,
        viewport={
            'width': width,
            'height': height
        },
        device_scale_factor=2.75,
        is_mobile=True,
        has_touch=True,
        ignore_https_errors=True,
        java_script_enabled=True,
        bypass_csp=True,
        locale='en-US',
        timezone_id='America/New_York'
    )
    
    # Get or create page
    if len(browser.pages) > 0:
        page = browser.pages[0]
    else:
        page = await browser.new_page()
    
    print(f"[OK] Chrome Mobile Mode | Size {width}x{height} | UA: {ua_selected}")
    
    return browser, page
