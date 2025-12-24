"""
Launch Live Ultra Compliant - TikTok 2025 Strict Compliance
============================================================

GOAL:
- RAM: 180-220MB per Chrome profile
- View eligibility: MAINTAINED (theo baseline đã đo)
- No bot detection
- No fake interaction

PHASES:
1. Bootstrap: Launch Chrome với flags tối thiểu
2. Natural Entry: Profile page → LIVE badge click
3. Trust Window: Wait for trust establishment (8-15s)
4. Stabilized Idle: Let browser self-manage resources

COMPLIANCE:
- NO headless
- NO single-process
- NO mute-audio / disable-audio
- NO window-size < 360x640
- NO fake metrics / spoofing
- Natural user activation via DOM click
"""

import sys
import os
import asyncio
import time
import threading
from pathlib import Path
from datetime import datetime

sys.path.insert(0, os.getcwd())

from core.chrome_manager import ChromeProfileManager
from core.managers.profile_manager import ProfileManager
from chrome_ram_optimizer_safe import ChromeRAMOptimizerSafe


# ============================================================================
# CHROME FLAGS - FINAL APPROVED SET
# ============================================================================

class TikTokCompliantFlags:
    """
    Chrome flags được phép sử dụng cho TikTok LIVE
    Mỗi flag có giải thích rõ ràng
    """
    
    APPROVED_FLAGS = [
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # BASIC SETUP (Required for automation)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        '--no-default-browser-check',  # Skip default browser prompt
        '--password-store=basic',  # Use basic password store
        '--unsafely-disable-devtools-self-xss-warnings',  # Allow DevTools usage
        '--edge-skip-compat-layer-relaunch',  # Skip Edge compat check
        '--no-sandbox',  # Required for some environments
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # STEALTH (Hide automation signals)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        '--disable-blink-features=AutomationControlled',  # Hide automation
        '--exclude-switches=enable-automation',  # Remove automation flag
        '--disable-infobars',  # Hide "Chrome is being controlled" infobar
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # MEMORY OPTIMIZATION (Critical for 180-220MB target)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        '--renderer-process-limit=2',  # Limit renderer processes to 2
        '--disk-cache-size=1',  # Minimal disk cache (1 byte = disabled)
        '--media-cache-size=1',  # Minimal media cache (1 byte = disabled)
        '--js-flags=--max-old-space-size=96',  # Limit JS heap to 96MB
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # LOCALE & LANGUAGE
        # ━━━━━━━