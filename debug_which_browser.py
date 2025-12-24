#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug: Which Browser Is Being Used?
Trace xem launch_livestream_tiktok.py đang dùng Playwright hay GPM Browser
"""

import sys
import os

# Monkey patch để trace
original_launch = None

def trace_browser_launch():
    """Patch BrowserManager để trace browser path"""
    
    # Patch Playwright launch
    try:
        from playwright.async_api import async_playwright
        
        print("[TRACE] Patching Playwright to trace browser path...")
        
        # We'll trace at the context level
        import asyncio
        
        async def test_playwright():
            async with async_playwright() as p:
                print(f"[TRACE] Playwright chromium executable:")
                print(f"  {p.chromium.executable_path if hasattr(p.chromium, 'executable_path') else 'N/A'}")
                
                # Check if it's GPM or Playwright
                if hasattr(p.chromium, 'executable_path'):
                    exe_path = str(p.chromium.executable_path)
                    if 'GPMLogin' in exe_path or 'gpm_browser' in exe_path:
                        print(f"  ❌ TYPE: GPM Browser (WRONG!)")
                    elif 'ms-playwright' in exe_path:
                        print(f"  ✅ TYPE: Playwright Chromium (CORRECT!)")
                    else:
                        print(f"  ⚠️  TYPE: Unknown")
        
        asyncio.run(test_playwright())
        
    except Exception as e:
        print(f"[TRACE] Error: {e}")

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🔍 DEBUG: Which Browser Is Being Used?")
    print("="*70)
    
    trace_browser_launch()
    
    print("\n" + "="*70)
    print("Now checking BrowserManager configuration...")
    print("="*70)
    
    # Check BrowserManager
    try:
        from core.managers.browser_manager import BrowserManager
        from core.managers.profile_manager import ProfileManager
        from core.managers.proxy_manager import ProxyManager
        
        pm = ProfileManager()
        prm = ProxyManager(pm)
        bm = BrowserManager(pm, prm)
        
        print(f"[CHECK] BrowserManager class: {bm.__class__.__name__}")
        print(f"[CHECK] Has playwright attr: {hasattr(bm, 'playwright')}")
        
        # Check if there's any GPM-related config
        if hasattr(bm, 'config'):
            print(f"[CHECK] Has config: Yes")
            try:
                import configparser
                if isinstance(bm.config, configparser.ConfigParser):
                    gpm_path = bm.config.get('chrome', 'gpm_browser_path', fallback='')
                    if gpm_path:
                        print(f"[CHECK] GPM browser path in config: {gpm_path}")
                        print(f"  ⚠️  This may override Playwright!")
                    else:
                        print(f"[CHECK] No GPM browser path in config")
            except:
                pass
        
    except Exception as e:
        print(f"[CHECK] Error: {e}")
    
    print("\n" + "="*70)
    print("Checking BrowserManagerStealth2025...")
    print("="*70)
    
    try:
        from core.managers.browser_manager_stealth_2025 import BrowserManagerStealth2025
        
        pm = ProfileManager()
        prm = ProxyManager(pm)
        bms = BrowserManagerStealth2025(pm, prm)
        
        print(f"[CHECK] BrowserManagerStealth2025 class: {bms.__class__.__name__}")
        print(f"[CHECK] Parent class: {bms.__class__.__bases__}")
        print(f"[CHECK] Has playwright attr: {hasattr(bms, 'playwright')}")
        
        # Check method resolution order
        print(f"[CHECK] Method Resolution Order:")
        for cls in bms.__class__.__mro__:
            print(f"  - {cls.__name__}")
        
    except Exception as e:
        print(f"[CHECK] Error: {e}")
    
    print("\n" + "="*70)
    print("CONCLUSION")
    print("="*70)
    print("If Playwright chromium path shows GPM Browser:")
    print("  → Playwright is configured to use GPM Browser")
    print("  → Need to reconfigure Playwright")
    print("")
    print("If Playwright chromium path shows ms-playwright:")
    print("  → Playwright is configured correctly")
    print("  → But launch_livestream_tiktok.py may be using wrong manager")
    print("="*70)
