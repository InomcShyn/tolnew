#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🛡️ BROWSER MANAGER STEALTH 2025 - TIKTOK ANTI-DETECTION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Wrapper cho browser_manager.py với full TikTok 2025 anti-detection:

✅ Anti-detect Headless → Stealth-Headful
✅ Remove dangerous Chrome flags
✅ Full anti-automation patches
✅ Anti blank page recovery
✅ Configurable window sizes
✅ Mobile mode support
✅ UA preservation
✅ RAM optimization
✅ Livestream mode

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import asyncio
from typing import Optional
from pathlib import Path

from .browser_manager import BrowserManager
from ..playwright_stealth_2025 import (
    should_use_headless,
    get_safe_chrome_args,
    clean_chrome_args,
    inject_stealth_script,
    parse_window_size,
    apply_mobile_mode,
    handle_blank_page,
    should_preserve_ua,
    WINDOW_SIZES,
)


class BrowserManagerStealth2025(BrowserManager):
    """
    Browser Manager với TikTok 2025 Anti-Detection
    
    Extends BrowserManager với stealth features
    """
    
    async def launch_profile_stealth(
        self,
        profile_name: str,
        url: Optional[str] = None,
        window_size: str = "360x640",
        mobile_mode: bool = False,
        force_headless: bool = False,
        ultra_low_ram: bool = True,
        **kwargs
    ):
        """
        Launch profile với TikTok 2025 stealth mode
        
        Args:
            profile_name: Profile name
            url: URL to navigate
            window_size: Window size (e.g. "360x640", "mobile_medium", "1x1")
            mobile_mode: Enable mobile mode
            force_headless: Force headless (not recommended for TikTok)
            ultra_low_ram: Enable ultra low RAM mode (150-200MB)
            **kwargs: Additional Playwright options
        
        Returns:
            Page object or None
        """
        try:
            print(f"[STEALTH-2025] Launching {profile_name} with anti-detection...")
            
            # ═══════════════════════════════════════════════════════════════
            # 1. DETERMINE HEADLESS MODE
            # ═══════════════════════════════════════════════════════════════
            is_livestream = bool(url and '/live' in url)
            use_headless = should_use_headless(url, force_headless)
            
            # Livestream MUST be visible
            if is_livestream and use_headless:
                print("[STEALTH-2025] ⚠️  Livestream detected, forcing visible mode")
                use_headless = False
                # Use minimal window for RAM optimization
                if window_size not in ['1x1', 'minimal']:
                    window_size = '1x1'
                    print("[STEALTH-2025] Using minimal window (1x1) for RAM optimization")
            
            # ═══════════════════════════════════════════════════════════════
            # 2. GET SAFE CHROME ARGS
            # ═══════════════════════════════════════════════════════════════
            safe_args = get_safe_chrome_args(
                is_livestream=is_livestream,
                window_size=window_size,
                ultra_low_ram=ultra_low_ram
            )
            
            # Clean any existing args from kwargs
            if 'args' in kwargs:
                kwargs['args'] = clean_chrome_args(kwargs['args'])
                # Merge with safe args
                kwargs['args'].extend(safe_args)
            else:
                kwargs['args'] = safe_args
            
            # ═══════════════════════════════════════════════════════════════
            # 3. CHECK UA PRESERVATION
            # ═══════════════════════════════════════════════════════════════
            profile_path = self.profile_manager.get_profile_path(profile_name)
            preserve_ua, existing_ua = should_preserve_ua(profile_path)
            
            if preserve_ua and existing_ua:
                # Add UA to args
                kwargs['args'].append(f'--user-agent={existing_ua}')
                print(f"[STEALTH-2025] ✅ Preserved UA from profile")
            elif mobile_mode:
                # Will apply mobile UA after launch
                print(f"[STEALTH-2025] Mobile mode: Will apply random mobile UA")
            
            # ═══════════════════════════════════════════════════════════════
            # 4. USE PROFILE'S CHROME WITH SAFE FLAGS
            # ═══════════════════════════════════════════════════════════════
            # STRATEGY: Allow GPM Browser or Chrome for Testing to be used
            # BUT override flags with safe flags via _stealth_mode
            print("[STEALTH-2025] 🔧 Using profile's Chrome with safe flags...")
            
            # CRITICAL: Mark that we're using stealth mode
            # This prevents browser_manager from adding bad flags
            kwargs['_stealth_mode'] = True
            print("[STEALTH-2025] Set _stealth_mode=True - safe flags will override defaults")
            
            # Call parent launch_profile
            # It will find GPM Browser or Chrome for Testing based on profile version
            # But our safe flags will override the bad flags
            page = await self.launch_profile(
                profile_name=profile_name,
                url=None,  # Don't navigate yet
                headless=use_headless,
                ultra_low_cpu=False,  # We handle RAM optimization in safe_args
                **kwargs
            )
            
            if not page:
                print(f"[STEALTH-2025] ❌ Failed to launch {profile_name}")
                return None
            
            # ═══════════════════════════════════════════════════════════════
            # 5. INJECT STEALTH SCRIPT
            # ═══════════════════════════════════════════════════════════════
            await inject_stealth_script(page)
            
            # ═══════════════════════════════════════════════════════════════
            # 6. APPLY MOBILE MODE (if requested)
            # ═══════════════════════════════════════════════════════════════
            if mobile_mode:
                width, height = parse_window_size(window_size)
                await apply_mobile_mode(page, width, height, existing_ua)
            
            # ═══════════════════════════════════════════════════════════════
            # 7. NAVIGATE TO URL
            # ═══════════════════════════════════════════════════════════════
            if url:
                print(f"[STEALTH-2025] Navigating to {url}...")
                
                try:
                    await page.goto(url, wait_until='domcontentloaded', timeout=30000)
                    await asyncio.sleep(2)
                    
                    # Check for blank page
                    if page.url == "about:blank":
                        print("[STEALTH-2025] ⚠️  Blank page detected, attempting recovery...")
                        recovered = await handle_blank_page(page, url)
                        
                        if not recovered:
                            print("[STEALTH-2025] ❌ Failed to recover from blank page")
                            if use_headless:
                                print("[STEALTH-2025] 💡 Try again with force_headless=False")
                            return None
                    
                    print(f"[STEALTH-2025] ✅ Navigation complete: {page.url}")
                    
                except Exception as e:
                    print(f"[STEALTH-2025] ❌ Navigation error: {e}")
                    
                    # Try recovery
                    print("[STEALTH-2025] Attempting recovery...")
                    recovered = await handle_blank_page(page, url)
                    
                    if not recovered:
                        return None
            
            # ═══════════════════════════════════════════════════════════════
            # 8. LIVESTREAM SETUP (if needed)
            # ═══════════════════════════════════════════════════════════════
            if is_livestream:
                print(f"[STEALTH-2025] 🎥 Setting up livestream mode...")
                
                try:
                    from livestream_utils import (
                        wait_for_websocket_liveroom,
                        wait_for_video_with_fallback,
                        start_engagement_loop,
                        run_livestream_debug
                    )
                    
                    # Wait for page to load
                    await asyncio.sleep(3)
                    
                    # Check WebSocket
                    ws_found = await wait_for_websocket_liveroom(page, timeout=15000)
                    
                    if not ws_found:
                        print(f"[STEALTH-2025] ⚠️  WebSocket not found, reloading...")
                        await page.reload(wait_until='domcontentloaded')
                        await asyncio.sleep(3)
                        
                        ws_found = await wait_for_websocket_liveroom(page, timeout=10000)
                        
                        if not ws_found:
                            print(f"[STEALTH-2025] ❌ WebSocket still not found")
                            print(f"[STEALTH-2025] ⚠️  Views may not be counted!")
                    
                    # Wait for video
                    video_found = await wait_for_video_with_fallback(page, timeout=15000)
                    
                    if video_found:
                        # Start engagement
                        await start_engagement_loop(page)
                        
                        # Debug info
                        debug_result = await run_livestream_debug(page)
                        print(f"[STEALTH-2025] WebGL: {debug_result.get('webglVendor')}")
                        print(f"[STEALTH-2025] Video: {debug_result.get('canPlay')}")
                        print(f"[STEALTH-2025] WebSocket: {debug_result.get('wsExists')}")
                        
                        print(f"[STEALTH-2025] ✅ Livestream setup complete")
                    else:
                        print(f"[STEALTH-2025] ⚠️  Video not found - views may not count")
                
                except Exception as e:
                    print(f"[STEALTH-2025] ⚠️  Livestream setup error: {e}")
            
            print(f"[STEALTH-2025] ✅ {profile_name} launched successfully")
            return page
            
        except Exception as e:
            print(f"[STEALTH-2025] ❌ Error launching {profile_name}: {e}")
            import traceback
            traceback.print_exc()
            return None


# ═══════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

async def launch_profile_stealth(
    browser_manager: BrowserManager,
    profile_name: str,
    url: Optional[str] = None,
    window_size: str = "360x640",
    mobile_mode: bool = False,
    force_headless: bool = False,
    ultra_low_ram: bool = True,
    **kwargs
):
    """
    Helper function: Launch profile with stealth mode
    
    Args:
        browser_manager: BrowserManager instance
        profile_name: Profile name
        url: URL to navigate
        window_size: Window size (e.g. "360x640", "mobile_medium", "1x1")
        mobile_mode: Enable mobile mode
        force_headless: Force headless (not recommended for TikTok)
        ultra_low_ram: Enable ultra low RAM mode (150-200MB)
        **kwargs: Additional Playwright options
    
    Returns:
        Page object or None
    """
    # Upgrade to stealth manager
    stealth_manager = BrowserManagerStealth2025(
        browser_manager.profile_manager,
        browser_manager.proxy_manager
    )
    
    # Copy state
    stealth_manager.playwright = browser_manager.playwright
    stealth_manager.playwright_context_manager = browser_manager.playwright_context_manager
    stealth_manager.contexts = browser_manager.contexts
    stealth_manager.pages = browser_manager.pages
    
    # Launch with stealth
    return await stealth_manager.launch_profile_stealth(
        profile_name=profile_name,
        url=url,
        window_size=window_size,
        mobile_mode=mobile_mode,
        force_headless=force_headless,
        ultra_low_ram=ultra_low_ram,
        **kwargs
    )


__all__ = [
    'BrowserManagerStealth2025',
    'launch_profile_stealth',
]
