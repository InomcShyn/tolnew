"""
⚠️ DEPRECATED: This file is deprecated and will be removed in future versions.
Use core.utils.user_agent instead for all user agent operations.

Migration Guide:
- OLD: from core.tiles.tile_user_agent import generate_user_agent
- NEW: from core.utils.user_agent import get_user_agent_for_profile

The new module provides:
- Persistent UA (saved to profile/useragent.txt)
- Block detection and auto-rotation
- Login awareness
- Expanded UA pool (30+ UAs)
- Validation and info extraction
"""

import warnings
import random

# Issue deprecation warning
warnings.warn(
    "tile_user_agent is deprecated. Use core.utils.user_agent instead.",
    DeprecationWarning,
    stacklevel=2
)


def generate_user_agent(manager, profile_type, browser_version=None):
    """Generate user agent string for profile"""
    if browser_version:
        major_version = browser_version.split('.')[0]
        return f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{major_version}.0.0.0 Safari/537.36"
    if profile_type in ("work", "cong_viec"):
        chrome_versions = [
            "120.0.6099.109",
            "120.0.6099.129",
            "121.0.6167.85",
            "121.0.6167.140",
        ]
        chrome_version = random.choice(chrome_versions)
        return f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_version} Safari/537.36"
    return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.109 Safari/537.36"


def generate_random_mac():
    """Generate random MAC address"""
    mac = [
        0x00, 0x16, 0x3e,  # VMware OUI
        random.randint(0x00, 0x7f),
        random.randint(0x00, 0xff),
        random.randint(0x00, 0xff)
    ]
    return ':'.join(map(lambda x: "%02x" % x, mac))
