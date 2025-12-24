#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mobile Mode for TikTok Livestream
Android Chrome emulation with anti-detection
"""

import random

# Android User-Agents (Chrome 119-122, Android 9-14)
ANDROID_USER_AGENTS = [
    "Mozilla/5.0 (Linux; Android 13; SM-G973N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 12; SM-A505F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 11; SM-M307F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; Redmi Note 8 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; Pixel 4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 12; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 11; Redmi Note 9 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; SM-A525F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 12; Pixel 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36"
]

# Viewport sizes (mobile devices)
INPUT_VIEWPORT_LIST = [
    (360, 640),   # Samsung Galaxy S8
    (375, 667),   # iPhone 8
    (414, 896),   # iPhone 11
    (393, 851),   # Pixel 5
    (412, 915),   # Samsung Galaxy S21
    (390, 844),   # iPhone 13
    (360, 780),   # Samsung A52
    (384, 854),   # Redmi Note 8
    (412, 892),   # Pixel 6
    (428, 926)    # iPhone 13 Pro Max
]

# Languages
LANGUAGES = [
    ["vi-VN", "vi", "en-US", "en"],
    ["en-US", "en"],
    ["en-GB", "en"],
    ["vi-VN", "vi"],
    ["en-US", "en", "vi-VN", "vi"]
]


def get_mobile_config(viewport_index: int = None):
    """
    Get mobile configuration for TikTok livestream
    
    Args:
        viewport_index: Index to select viewport (None = random)
    
    Returns:
        dict: Mobile configuration
    """
    # Random viewport
    if viewport_index is None or viewport_index < 0 or viewport_index >= len(INPUT_VIEWPORT_LIST):
        viewport_index = random.randint(0, len(INPUT_VIEWPORT_LIST) - 1)
    
    width, height = INPUT_VIEWPORT_LIST[viewport_index]
    
    # Random user agent
    user_agent = random.choice(ANDROID_USER_AGENTS)
    
    # Random device scale factor (2.0 - 3.0)
    device_scale_factor = round(random.uniform(2.0, 3.0), 2)
    
    # Random languages
    languages = random.choice(LANGUAGES)
    
    # Random touch points (5-10)
    max_touch_points = random.randint(5, 10)
    
    config = {
        'viewport': {
            'width': width,
            'height': height
        },
        'user_agent': user_agent,
        'device_scale_factor': device_scale_factor,
        'is_mobile': True,
        'has_touch': True,
        'languages': languages,
        'max_touch_points': max_touch_points,
        'accept_language': languages[0] if languages else 'en-US'
    }
    
    print(f"[MOBILE-CONFIG] Viewport: {width}x{height}")
    print(f"[MOBILE-CONFIG] Scale: {device_scale_factor}x")
    print(f"[MOBILE-CONFIG] UA: {user_agent[:60]}...")
    print(f"[MOBILE-CONFIG] Touch points: {max_touch_points}")
    
    return config


async def apply_mobile_config(page, config):
    """
    Apply mobile configuration to page
    Override navigator properties for mobile emulation
    
    Args:
        page: Playwright page
        config: Mobile config from get_mobile_config()
    """
    try:
        # Override navigator.maxTouchPoints
        await page.add_init_script(f"""
            Object.defineProperty(navigator, 'maxTouchPoints', {{
                get: () => {config['max_touch_points']}
            }});
        """)
        
        # Override navigator.platform
        await page.add_init_script("""
            Object.defineProperty(navigator, 'platform', {
                get: () => 'Linux armv8l'
            });
        """)
        
        # Override screen properties
        await page.add_init_script(f"""
            Object.defineProperty(screen, 'width', {{
                get: () => {config['viewport']['width']}
            }});
            Object.defineProperty(screen, 'height', {{
                get: () => {config['viewport']['height']}
            }});
            Object.defineProperty(screen, 'availWidth', {{
                get: () => {config['viewport']['width']}
            }});
            Object.defineProperty(screen, 'availHeight', {{
                get: () => {config['viewport']['height']}
            }});
        """)
        
        # Override touch events
        await page.add_init_script("""
            // Enable touch events
            window.ontouchstart = null;
            document.ontouchstart = null;
            
            // Touch event constructor
            if (!window.TouchEvent) {
                window.TouchEvent = class TouchEvent extends UIEvent {
                    constructor(type, eventInitDict) {
                        super(type, eventInitDict);
                    }
                };
            }
        """)
        
        print(f"[MOBILE-CONFIG] Applied mobile overrides")
        
    except Exception as e:
        print(f"[MOBILE-CONFIG] Error applying config: {e}")


def get_mobile_chrome_args():
    """
    Get Chrome args for mobile mode
    
    Returns:
        list: Chrome arguments
    """
    return [
        '--disable-blink-features=AutomationControlled',
        '--disable-features=IsolateOrigins,site-per-process',
        '--disable-infobars',
        '--window-position=0,0',
        '--ignore-certificate-errors',
        '--ignore-certificate-errors-spki-list',
        '--disable-popup-blocking',
        '--disable-save-password-bubble',
        '--disable-translate',
        '--disable-background-networking',
        '--disable-default-apps',
        '--disable-hang-monitor',
        '--disable-prompt-on-repost',
        '--disable-domain-reliability',
        '--disable-component-update',
        '--disable-client-side-phishing-detection',
        '--disable-breakpad',
        '--metrics-recording-only',
        '--no-pings'
    ]
