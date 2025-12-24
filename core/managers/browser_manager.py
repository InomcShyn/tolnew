#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Browser Manager - Quản lý browsers với Playwright
Core replacement for chrome_manager.py
HỖ TRỢ EXTENSIONS qua persistent context
"""

import os
import asyncio
from typing import Optional, Dict, List
from pathlib import Path
from playwright.async_api import async_playwright, Browser, BrowserContext, Page, Playwright


class BrowserManager:
    """Quản lý browsers với Playwright - HỖ TRỢ EXTENSIONS"""
    
    def __init__(self, profile_manager, proxy_manager):
        self.profile_manager = profile_manager
        self.proxy_manager = proxy_manager
        self.playwright: Optional[Playwright] = None
        self.playwright_context_manager = None
        self.contexts: Dict[str, BrowserContext] = {}
        self.pages: Dict[str, Page] = {}
        self.extensions_dir = Path(os.getcwd()) / "extensions"
    
    async def start(self):
        """Khởi động Playwright"""
        try:
            if not self.playwright:
                print("[BROWSER] Initializing Playwright...")
                self.playwright_context_manager = async_playwright()
                self.playwright = await self.playwright_context_manager.__aenter__()
                print("[BROWSER] ✅ Playwright initialized successfully")
        except Exception as e:
            print(f"[ERROR] Failed to start Playwright: {e}")
            import traceback
            traceback.print_exc()
            self.playwright = None
            self.playwright_context_manager = None
    
    async def stop(self):
        """Dừng Playwright và đóng tất cả contexts"""
        # Close all contexts
        for context in list(self.contexts.values()):
            try:
                await context.close()
            except:
                pass
        
        self.contexts.clear()
        self.pages.clear()
        
        # Stop playwright
        if self.playwright_context_manager:
            try:
                await self.playwright_context_manager.__aexit__(None, None, None)
            except:
                pass
        
        self.playwright = None
        self.playwright_context_manager = None
    
    def _get_extension_paths(self, profile_name: str) -> List[str]:
        """
        Lấy danh sách extension paths cho profile
        
        Returns:
            List các đường dẫn đến extension folders (version folders)
        """
        extension_paths = []
        
        # 1. Tìm extensions trong workspace extensions/ folder
        # Format: ProxyAuth_{profile_name}, ProfileTitle_{profile_name}
        if self.extensions_dir.exists():
            for ext_dir in self.extensions_dir.iterdir():
                if ext_dir.is_dir():
                    # Check if extension belongs to this profile
                    if profile_name in ext_dir.name or ext_dir.name.startswith('Global_'):
                        manifest_path = ext_dir / "manifest.json"
                        if manifest_path.exists():
                            extension_paths.append(str(ext_dir))
                            print(f"[EXTENSION] Found workspace extension: {ext_dir.name}")
        
        # 2. ✅ FIX: Tìm extensions đã cài trong profile folder
        # Path: chrome_profiles/{profile_name}/Default/Extensions/{ext_id}/{version}/
        profile_path = self.profile_manager.get_profile_path(profile_name)
        if profile_path:
            profile_extensions_dir = profile_path / "Default" / "Extensions"
            if profile_extensions_dir.exists():
                # Duyệt qua từng extension ID
                for ext_id_dir in profile_extensions_dir.iterdir():
                    if ext_id_dir.is_dir():
                        # Duyệt qua từng version folder
                        for version_dir in ext_id_dir.iterdir():
                            if version_dir.is_dir():
                                manifest_path = version_dir / "manifest.json"
                                if manifest_path.exists():
                                    extension_paths.append(str(version_dir))
                                    print(f"[EXTENSION] Found profile extension: {ext_id_dir.name}/{version_dir.name}")
        
        return extension_paths
    
    def _create_proxy_auth_extension(self, profile_name: str, username: str, password: str) -> Optional[str]:
        """
        Tạo proxy auth extension cho profile
        
        Args:
            profile_name: Tên profile
            username: Proxy username
            password: Proxy password
        
        Returns:
            Đường dẫn đến extension folder hoặc None
        """
        try:
            import json
            import shutil
            
            # Tạo folder extensions nếu chưa có
            self.extensions_dir.mkdir(exist_ok=True)
            
            # Tạo folder cho extension này (unique per profile)
            ext_folder_name = f"ProxyAuth_{profile_name}"
            ext_dir = self.extensions_dir / ext_folder_name
            
            # Xóa extension cũ nếu có
            if ext_dir.exists():
                try:
                    shutil.rmtree(ext_dir)
                    print(f"[PROXY-AUTH] Removed old proxy auth extension: {ext_dir}")
                except Exception as e:
                    print(f"[WARNING] Could not remove old extension: {e}")
            
            # Tạo folder mới
            ext_dir.mkdir(exist_ok=True)
            
            # Tạo manifest.json
            manifest = {
                "manifest_version": 3,
                "name": "Proxy Auth Helper",
                "version": "1.0.0",
                "description": "Auto-fill proxy authentication",
                "permissions": [
                    "webRequest",
                    "webRequestAuthProvider"
                ],
                "host_permissions": [
                    "<all_urls>"
                ],
                "background": {
                    "service_worker": "background.js"
                }
            }
            
            manifest_path = ext_dir / "manifest.json"
            with open(manifest_path, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, indent=2, ensure_ascii=False)
            
            # Tạo background.js với credentials
            background_js = f"""
// Proxy credentials
const PROXY_USERNAME = "{username}";
const PROXY_PASSWORD = "{password}";

// Listen for auth requests
chrome.webRequest.onAuthRequired.addListener(
    function(details, callbackFn) {{
        console.log('[PROXY-AUTH] Authentication required for:', details.url);
        
        // Return credentials
        callbackFn({{
            authCredentials: {{
                username: PROXY_USERNAME,
                password: PROXY_PASSWORD
            }}
        }});
    }},
    {{ urls: ["<all_urls>"] }},
    ['asyncBlocking']
);

console.log('[PROXY-AUTH] Extension loaded. Username:', PROXY_USERNAME);
"""
            
            background_path = ext_dir / "background.js"
            with open(background_path, 'w', encoding='utf-8') as f:
                f.write(background_js)
            
            print(f"[PROXY-AUTH] ✅ Created proxy auth extension: {ext_dir}")
            print(f"[PROXY-AUTH]    Username: {username}")
            print(f"[PROXY-AUTH]    Password: {'*' * len(password)}")
            
            return str(ext_dir)
            
        except Exception as e:
            print(f"[ERROR] Failed to create proxy auth extension: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    async def launch_profile(
        self,
        profile_name: str,
        url: Optional[str] = None,
        headless: bool = False,
        minimize: bool = False,
        ultra_low_cpu: bool = False,
        **kwargs
    ) -> Optional[Page]:
        """
        Launch một profile với EXTENSION SUPPORT
        
        Args:
            profile_name: Tên profile
            url: URL để mở
            headless: Chế độ headless (LƯU Ý: extensions chỉ hoạt động khi headless=False)
            minimize: Minimize window xuống taskbar (chỉ khi headless=False)
            ultra_low_cpu: Chế độ ultra low CPU
            **kwargs: Các options khác cho Playwright
        
        Returns:
            Page object hoặc None nếu thất bại
        """
        try:
            # ✅ FIX: Kill any existing Chrome processes using this profile
            # This prevents "Opening in existing browser session" error
            profile_path = self.profile_manager.get_profile_path(profile_name)
            if profile_path and profile_path.exists():
                try:
                    import subprocess
                    import time
                    
                    # Get profile path string for matching
                    profile_path_str = str(profile_path).replace('/', '\\')
                    
                    # Find Chrome processes using this profile
                    print(f"[BROWSER] Checking for existing Chrome processes using {profile_name}...")
                    
                    # Use WMIC to find Chrome processes with this user-data-dir
                    try:
                        result = subprocess.run(
                            ['wmic', 'process', 'where', f"name='chrome.exe'", 'get', 'ProcessId,CommandLine'],
                            capture_output=True,
                            text=True,
                            timeout=5
                        )
                        
                        if result.returncode == 0:
                            lines = result.stdout.strip().split('\n')
                            pids_to_kill = []
                            
                            for line in lines[1:]:  # Skip header
                                if profile_path_str in line:
                                    # Extract PID (last number in line)
                                    parts = line.strip().split()
                                    if parts:
                                        try:
                                            pid = int(parts[-1])
                                            pids_to_kill.append(pid)
                                        except:
                                            pass
                            
                            # Kill found processes
                            if pids_to_kill:
                                print(f"[BROWSER] Found {len(pids_to_kill)} Chrome processes to kill: {pids_to_kill}")
                                for pid in pids_to_kill:
                                    try:
                                        subprocess.run(['taskkill', '/F', '/PID', str(pid)], 
                                                     capture_output=True, timeout=3)
                                        print(f"[BROWSER] Killed Chrome process {pid}")
                                    except:
                                        pass
                                
                                # Wait for processes to fully terminate
                                print(f"[BROWSER] Waiting for processes to terminate...")
                                time.sleep(2)
                                print(f"[BROWSER] ✅ Cleanup complete")
                            else:
                                print(f"[BROWSER] No existing Chrome processes found for this profile")
                    
                    except Exception as e:
                        print(f"[WARNING] Could not check for existing Chrome processes: {e}")
                
                except Exception as e:
                    print(f"[WARNING] Error during Chrome process cleanup: {e}")
            
            # Ensure playwright is started
            if not self.playwright or not hasattr(self.playwright, 'chromium'):
                print("[BROWSER] Starting Playwright...")
                await self.start()
            
            # Double check playwright is initialized
            if not self.playwright:
                print("[ERROR] Failed to initialize Playwright")
                return None
            
            # Verify playwright connection is alive
            try:
                # Test if chromium is accessible
                _ = self.playwright.chromium
            except Exception as e:
                print(f"[ERROR] Playwright connection is broken: {e}")
                print("[BROWSER] Restarting Playwright...")
                await self.stop()
                await self.start()
                
                if not self.playwright:
                    print("[ERROR] Failed to restart Playwright")
                    return None
            
            profile_path = self.profile_manager.get_profile_path(profile_name)
            
            if not profile_path.exists():
                print(f"Profile not found: {profile_name}")
                return None
            
            # Disable restore pages and SSL warnings (prevent popup)
            try:
                import json
                import shutil
                
                # 1. DON'T Delete Session files - this breaks TikTok login!
                # Deleting Sessions/Session Storage will log out users from TikTok
                # and cause ERR_HTTP_RESPONSE_CODE_FAILURE
                # session_files = [
                #     profile_path / 'Default' / 'Sessions',
                #     profile_path / 'Default' / 'Session Storage',
                #     profile_path / 'Sessions',
                #     profile_path / 'Session Storage',
                # ]
                # for session_path in session_files:
                #     if session_path.exists():
                #         try:
                #             if session_path.is_dir():
                #                 shutil.rmtree(session_path)
                #             else:
                #                 session_path.unlink()
                #             print(f"[BROWSER] Deleted session: {session_path.name}")
                #         except:
                #             pass
                print(f"[BROWSER] Keeping sessions (preserves TikTok login)")
                
                # 2. Modify Preferences
                prefs_path = profile_path / 'Default' / 'Preferences'
                if prefs_path.exists():
                    with open(prefs_path, 'r', encoding='utf-8') as f:
                        prefs = json.load(f)
                    
                    # Disable restore pages
                    if 'profile' not in prefs:
                        prefs['profile'] = {}
                    prefs['profile']['exit_type'] = 'Normal'
                    prefs['profile']['exited_cleanly'] = True
                    
                    # Disable SSL warnings
                    if 'ssl' not in prefs:
                        prefs['ssl'] = {}
                    prefs['ssl']['rev_checking_enabled'] = False
                    
                    # Save preferences
                    with open(prefs_path, 'w', encoding='utf-8') as f:
                        json.dump(prefs, f, ensure_ascii=False, indent=2)
                    
                    print(f"[BROWSER] ✅ Disabled restore pages & SSL warnings")
            except Exception as e:
                print(f"[WARNING] Could not modify profile: {e}")
            
            # Check if stealth mode is enabled (skip default flags)
            _stealth_mode = kwargs.get('_stealth_mode', False)
            
            # Build launch args with anti-detection flags
            if not _stealth_mode:
                from core.tiles.tile_chrome_flags import get_flags_for_profile
                
                # Load profile settings to determine flag mode
                try:
                    import json
                    settings_path = profile_path / 'profile_settings.json'
                    profile_settings = {}
                    if settings_path.exists():
                        with open(settings_path, 'r', encoding='utf-8') as f:
                            profile_settings = json.load(f)
                except:
                    profile_settings = {}
                
                # Get appropriate flags (minimal, balanced, gpm, gpm_style, or stealth)
                # Default to gpm_style for clean command line like GPM Browser
                flag_mode = profile_settings.get('flag_mode', 'gpm_style')
                args = get_flags_for_profile(profile_settings, flag_mode)
            else:
                # Stealth mode: Use flags from kwargs['args']
                args = kwargs.get('args', [])
                
                # CRITICAL: Remove bad flags that Playwright might add
                bad_flags = [
                    '--single-process',
                    '--disk-cache-dir=/dev/null',
                ]
                bad_flag_prefixes = [
                    '--js-flags',  # Remove ALL js-flags, we'll add our own
                ]
                
                # Filter out bad flags
                cleaned_args = []
                for arg in args:
                    is_bad = False
                    # Check exact match
                    if arg in bad_flags:
                        is_bad = True
                        print(f"[STEALTH] Removed bad flag: {arg}")
                    # Check prefix match
                    for prefix in bad_flag_prefixes:
                        if arg.startswith(prefix):
                            is_bad = True
                            print(f"[STEALTH] Removed bad flag: {arg}")
                            break
                    
                    if not is_bad:
                        cleaned_args.append(arg)
                
                args = cleaned_args
                print(f"[STEALTH] Using {len(args)} cleaned flags")
            
            # Add user-agent from profile settings (GPM style) - skip in stealth mode
            if not _stealth_mode:
                try:
                    user_agent = None
                    if profile_settings.get('software', {}).get('user_agent'):
                        user_agent = profile_settings['software']['user_agent']
                    elif profile_settings.get('user_agent'):
                        user_agent = profile_settings['user_agent']
                    
                    if user_agent:
                        args.append(f'--user-agent={user_agent}')
                        print(f"[BROWSER] Using custom User-Agent: {user_agent[:50]}...")
                except Exception as e:
                    print(f"[WARNING] Could not set user-agent: {e}")
                
                # Add language from profile settings (GPM style)
                try:
                    language = None
                    if profile_settings.get('software', {}).get('language'):
                        language = profile_settings['software']['language']
                    elif profile_settings.get('language'):
                        language = profile_settings['language']
                    
                    if language:
                        # Extract language code (vi from vi-VN)
                        lang_code = language.split('-')[0] if '-' in language else language
                        args.append(f'--lang={lang_code}')
                        print(f"[BROWSER] Using language: {lang_code}")
                except Exception as e:
                    print(f"[WARNING] Could not set language: {e}")
            
            # Pop stealth mode flag (already checked above)
            _stealth_mode = kwargs.pop('_stealth_mode', False)
            
            if _stealth_mode:
                print(f"[BROWSER] ✅ Stealth mode: Using custom flags from stealth manager")
            else:
                # ALWAYS disable audio for all profiles (TikTok livestream)
                args.extend([
                    # Mute all audio
                    '--mute-audio',
                    # Disable audio output completely
                    '--autoplay-policy=user-gesture-required',
                    # Block audio rendering
                    '--disable-audio-output',
                    # Disable WebAudio API
                    '--disable-webaudio',
                ])
                print(f"[BROWSER] ✅ Audio completely disabled")
            
            # ULTRA LOW RAM mode - target 150-200MB per profile
            # AGGRESSIVE optimization for maximum profile density
            if not _stealth_mode:
                args.extend([
                # GPU (must have - saves 200MB)
                '--disable-gpu',
                '--disable-software-rasterizer',
                '--disable-accelerated-2d-canvas',
                '--disable-gpu-compositing',
                '--disable-gpu-rasterization',
                
                # Process limits (critical - saves 50-100MB)
                '--renderer-process-limit=1',
                '--max-gum-fps=5',  # Limit frame rate
                
                # Cache (saves 30-50MB) - AGGRESSIVE
                '--disk-cache-size=1',
                '--media-cache-size=1',
                '--aggressive-cache-discard',
                '--disable-application-cache',
                
                # Memory management (saves 50-80MB)
                '--disable-dev-shm-usage',
                '--disable-background-networking',
                '--disable-background-timer-throttling',
                '--disable-backgrounding-occluded-windows',
                '--disable-breakpad',
                '--disable-component-update',
                '--disable-domain-reliability',
                '--disable-features=AudioServiceOutOfProcess,IsolateOrigins,site-per-process',
                '--disable-hang-monitor',
                '--disable-ipc-flooding-protection',
                '--disable-popup-blocking',
                '--disable-prompt-on-repost',
                '--disable-renderer-backgrounding',
                '--disable-sync',
                '--disable-translate',
                '--metrics-recording-only',
                '--no-first-run',
                '--no-pings',
                '--safebrowsing-disable-auto-update',
                
                # Rendering (saves 20-40MB) - AGGRESSIVE
                '--disable-smooth-scrolling',
                '--disable-threaded-animation',
                '--disable-threaded-scrolling',
                '--num-raster-threads=1',
                '--disable-partial-raster',
                '--disable-skia-runtime-opts',
                
                # ✅ HARD LIMIT: 200MB RAM per Chrome process
                # JavaScript heap limit (main memory consumer) - AGGRESSIVE
                '--js-flags=--max-old-space-size=80',      # 80MB JS heap (reduced from 150MB)
                '--js-flags=--max-semi-space-size=1',      # Minimize semi-space
                '--js-flags=--max-heap-size=120',          # 120MB total heap limit (reduced from 200MB)
                '--js-flags=--optimize-for-size',          # Optimize for size not speed
                '--js-flags=--always-compact',             # Always compact memory
                '--js-flags=--gc-interval=100',            # Frequent garbage collection
                
                # Additional memory limits - AGGRESSIVE
                '--max-old-space-size=80',                 # V8 old space limit
                '--memory-pressure-off',                   # Disable memory pressure warnings
                
                # Image/Media optimization (saves 10-30MB)
                '--disable-image-animation-resync',
                '--disable-webgl',
                '--disable-webgl2',
                
                # Network optimization (saves 5-10MB)
                '--disable-features=NetworkService',
                '--disable-features=NetworkServiceInProcess',
                ])
                print(f"[BROWSER] ✅ ULTRA LOW RAM mode enabled (target: 150-200MB per profile)")
            
            # Low resource mode (additional optimizations)
            if ultra_low_cpu and not _stealth_mode:
                args.extend([
                    # Additional resource saving
                    '--num-raster-threads=1',  # Limit raster threads
                    
                    # Limit processes
                    '--renderer-process-limit=2',  # Allow 2 renderers for video
                    
                    # Memory optimization
                    '--disk-cache-size=1',
                    '--media-cache-size=1',
                    '--aggressive-cache-discard',
                ])
                print(f"[BROWSER] ✅ Low resource mode enabled (GPU kept for video)")
            
            # EXTENSION SUPPORT: Load extensions (cả khi ultra_low_cpu=True)
            # Get all extension paths FIRST
            extension_paths = self._get_extension_paths(profile_name)
            
            # Get proxy config để tạo proxy auth extension nếu cần
            proxy_string = self.proxy_manager.get_profile_proxy(profile_name)
            print(f"[DEBUG] [PROXY] Proxy string for {profile_name}: {proxy_string}")
            
            if proxy_string:
                proxy_dict = self.proxy_manager.parse_proxy_string(proxy_string)
                print(f"[DEBUG] [PROXY] Parsed proxy: {proxy_dict}")
                
                # Nếu proxy có username/password, tạo proxy auth extension
                if proxy_dict.get('username'):
                    print(f"[DEBUG] [PROXY] Creating proxy auth extension...")
                    ext_path = self._create_proxy_auth_extension(
                        profile_name,
                        proxy_dict['username'],
                        proxy_dict.get('password', '')
                    )
                    if ext_path:
                        # ADD proxy auth extension to extension_paths
                        extension_paths.append(ext_path)
                        print(f"[EXTENSION] ✅ Added proxy auth extension to load list")
                    else:
                        print(f"[ERROR] Failed to create proxy auth extension")
                else:
                    print(f"[DEBUG] [PROXY] No username in proxy, skipping auth extension")
            
            if extension_paths:
                # LƯU Ý: Extensions chỉ hoạt động khi headless=False
                if headless:
                    print("[WARNING] Extensions không hoạt động trong headless mode!")
                    print("[WARNING] Chuyển sang headed mode để sử dụng extensions...")
                    headless = False
                
                # Load extensions
                extensions_arg = ','.join(extension_paths)
                args.append(f'--disable-extensions-except={extensions_arg}')
                args.append(f'--load-extension={extensions_arg}')
                print(f"[EXTENSION] Loading {len(extension_paths)} extensions for {profile_name}")
            
            # Get proxy config - SET VIA CHROME ARGS (like GPM does)
            # Không dùng Playwright proxy config vì không hoạt động tốt
            proxy_config = None  # Không dùng Playwright proxy
            proxy_string = self.proxy_manager.get_profile_proxy(profile_name)
            
            # Check if proxy is valid (not empty, not "no proxy", etc.)
            if proxy_string and proxy_string.lower() not in ['', 'none', 'null', 'no proxy', 'no', 'remove']:
                proxy_dict = self.proxy_manager.parse_proxy_string(proxy_string)
                
                # Check if proxy was parsed successfully
                if proxy_dict and 'protocol' in proxy_dict and 'server' in proxy_dict and 'port' in proxy_dict:
                    # Set proxy via Chrome args (GPM style)
                    proxy_server = f"{proxy_dict['protocol']}://{proxy_dict['server']}:{proxy_dict['port']}"
                    args.append(f'--proxy-server={proxy_server}')
                    print(f"[PROXY] Set proxy via Chrome args: {proxy_server}")
                    
                    if proxy_dict.get('username'):
                        print(f"[PROXY] Proxy auth will be handled by extension: {proxy_dict['username']}")
                else:
                    print(f"[WARNING] Invalid proxy format: {proxy_string}")
                    print(f"[INFO] Profile will launch without proxy")
            else:
                if proxy_string:
                    print(f"[INFO] No proxy configured (value: {proxy_string})")
                else:
                    print(f"[INFO] No proxy configured for {profile_name}")
            
            # Get Chrome executable path for specific version
            # Uses full logic from tile_chrome_binary: GPM, env, config, Chrome for Testing
            executable_path = None
            desired_version = ''
            
            try:
                # Load profile settings to get browser version
                import json
                settings_path = profile_path / 'profile_settings.json'
                if settings_path.exists():
                    with open(settings_path, 'r', encoding='utf-8') as f:
                        settings = json.load(f)
                    
                    # Get version from settings (check multiple possible field names)
                    # Priority: chrome_version (top-level) > browser_version > software.chrome_version > software.browser_version
                    desired_version = (
                        settings.get('chrome_version') or  # HIGHEST PRIORITY
                        settings.get('browser_version') or 
                        settings.get('software', {}).get('chrome_version') or
                        settings.get('software', {}).get('browser_version')
                    )
                
                # Also check Last Version file (for compatibility)
                if not desired_version:
                    last_version_file = profile_path / 'Last Version'
                    if last_version_file.exists():
                        try:
                            with open(last_version_file, 'r', encoding='utf-8') as f:
                                desired_version = f.read().strip()
                            print(f"[BROWSER] Version from 'Last Version' file: {desired_version}")
                        except:
                            pass
                
                if not desired_version:
                    print(f"[BROWSER] ⚠️  No Chrome version specified in profile settings")
                    print(f"[BROWSER] Will use system Chrome (if available)")
                
                if desired_version:
                    print(f"[BROWSER] Profile requests Chrome version: {desired_version}")
                    
                    # Use full logic from tile_chrome_binary
                    from core.tiles.tile_chrome_binary import (
                        gpm_chrome_path_for_version,
                        resolve_chrome_binary_path,
                        ensure_cft_chrome_binary
                    )
                    
                    # Get custom GPM browser path from config
                    gpm_config_path = None
                    try:
                        if hasattr(self.profile_manager, 'manager'):
                            mgr = self.profile_manager.manager
                            if hasattr(mgr, 'config'):
                                import configparser
                                if isinstance(mgr.config, configparser.ConfigParser):
                                    gpm_config_path = mgr.config.get('chrome', 'gpm_browser_path', fallback='').strip()
                    except:
                        pass
                    
                    # Priority 1: GPM Browser (if installed and has chrome.exe)
                    from core.tiles.tile_chrome_binary import gpm_chrome_path_for_version
                    gpm_path = gpm_chrome_path_for_version(desired_version, gpm_config_path)
                    
                    if gpm_path:
                        gpm_exists = os.path.exists(gpm_path)
                        print(f"[DEBUG] GPM path: {gpm_path}")
                        print(f"[DEBUG] GPM chrome.exe exists: {gpm_exists}")
                        
                        if gpm_exists:
                            executable_path = gpm_path
                            print(f"[BROWSER] ✅ Using GPM Chrome: {gpm_path}")
                        else:
                            # Check if folder exists but chrome.exe missing
                            gpm_folder = os.path.dirname(gpm_path)
                            if os.path.exists(gpm_folder):
                                print(f"[WARNING] GPM folder exists but chrome.exe missing: {gpm_folder}")
                                print(f"[WARNING] Please download Chrome {desired_version} in GPM Browser")
                            else:
                                print(f"[INFO] GPM Chrome {desired_version} not installed")
                    
                    # Priority 2: Environment variable or config
                    if not executable_path:
                        # Pass manager instance for config access
                        manager_instance = self.profile_manager
                        if hasattr(manager_instance, 'manager'):
                            manager_instance = manager_instance.manager
                        
                        binary = resolve_chrome_binary_path(manager_instance, desired_version)
                        if binary and os.path.exists(binary):
                            executable_path = binary
                            print(f"[BROWSER] Using configured Chrome: {binary}")
                    
                    # Priority 3: Chrome for Testing (download if needed)
                    if not executable_path:
                        chrome_exe = ensure_cft_chrome_binary(desired_version)
                        if chrome_exe and os.path.exists(chrome_exe):
                            executable_path = chrome_exe
                            print(f"[BROWSER] Using Chrome for Testing: {chrome_exe}")
                    
                    # Priority 4: System Chrome (fallback)
                    if not executable_path:
                        print(f"[WARNING] Chrome {desired_version} not available")
                        print(f"[INFO] Searching for system Chrome...")
                        
                        # Try common Chrome installation paths
                        system_chrome_paths = [
                            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                            os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
                            os.path.expandvars(r"%PROGRAMFILES%\Google\Chrome\Application\chrome.exe"),
                            os.path.expandvars(r"%PROGRAMFILES(X86)%\Google\Chrome\Application\chrome.exe"),
                        ]
                        
                        for chrome_path in system_chrome_paths:
                            if os.path.exists(chrome_path):
                                executable_path = chrome_path
                                print(f"[BROWSER] ✅ Using system Chrome: {chrome_path}")
                                break
                        
                        if not executable_path:
                            print(f"[ERROR] No Chrome found! Please:")
                            print(f"  1. Download Chrome {desired_version} in GPM Browser")
                            print(f"  2. Or install Google Chrome")
                            print(f"  3. Or set gpm_browser_path in config.ini")
                            raise Exception(f"Chrome {desired_version} not found and no system Chrome available")
                        else:
                            # Warn about version mismatch
                            print(f"[WARNING] Using system Chrome instead of Chrome {desired_version}")
                            print(f"[WARNING] This may cause issues with extensions and proxy auth")
                            print(f"[WARNING] Recommend: Download Chrome {desired_version} in GPM Browser")
                    
                    # Save Last Version and Last Browser for tracking
                    if executable_path:
                        try:
                            with open(profile_path / 'Last Version', 'w', encoding='utf-8') as f:
                                f.write(desired_version)
                            with open(profile_path / 'Last Browser', 'w', encoding='utf-8') as f:
                                f.write(executable_path)
                        except:
                            pass
                            
            except Exception as e:
                print(f"[WARNING] Could not resolve Chrome binary: {e}")
                import traceback
                traceback.print_exc()
                
                # Fallback to system Chrome if version check failed
                if not executable_path:
                    print(f"[BROWSER] Attempting fallback to system Chrome...")
                    system_chrome_paths = [
                        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
                    ]
                    
                    for chrome_path in system_chrome_paths:
                        if os.path.exists(chrome_path):
                            executable_path = chrome_path
                            print(f"[BROWSER] ✅ Using system Chrome (fallback): {chrome_path}")
                            break
                    
                    if not executable_path:
                        print(f"[ERROR] No Chrome binary found - cannot launch profile")
                        print(f"[ERROR] Please install Google Chrome or configure gpm_browser_path")
            
            # Extract autofill params before launching (not part of Playwright API)
            auto_login = kwargs.pop('auto_login', False)
            login_data = kwargs.pop('login_data', None)
            
            # ✅ FIX: Remove Playwright's default automation flags
            # Playwright tự động thêm NHIỀU flags mặc định
            # Chúng ta cần dùng ignore_default_args để loại bỏ chúng
            
            # List of Playwright's default args to ignore (keep only what we need)
            ignore_default_args = [
                '--enable-automation',  # ❌ Gây "installation is not enabled"
                '--disable-extensions',  # ❌ CHẶN TẤT CẢ EXTENSIONS!
                '--disable-component-extensions-with-background-pages',  # Chúng ta tự thêm
                '--disable-background-networking',  # Chúng ta tự thêm nếu cần
                '--disable-background-timer-throttling',
                '--disable-backgrounding-occluded-windows',
                '--disable-back-forward-cache',
                '--disable-breakpad',
                '--disable-client-side-phishing-detection',
                '--disable-component-update',
                '--disable-default-apps',
                '--disable-dev-shm-usage',
                '--disable-hang-monitor',
                '--disable-ipc-flooding-protection',
                '--disable-popup-blocking',
                '--disable-prompt-on-repost',
                '--disable-renderer-backgrounding',
                '--disable-sync',
                '--force-color-profile=srgb',
                '--metrics-recording-only',
                '--no-first-run',
                '--use-mock-keychain',
                '--no-service-autorun',
                '--export-tagged-pdf',
                '--disable-search-engine-choice-screen',
            ]
            
            # CRITICAL: In stealth mode, also ignore bad flags that break TikTok
            if _stealth_mode:
                ignore_default_args.extend([
                    '--single-process',  # Breaks AudioContext
                    '--disk-cache-dir=/dev/null',  # Breaks session
                ])
                print(f"[STEALTH] Ignoring bad Playwright defaults")
            
            # Launch persistent context
            launch_options = {
                'user_data_dir': str(profile_path),
                'headless': headless,
                'args': args,
                'ignore_default_args': ignore_default_args,  # ✅ Loại bỏ Playwright's default flags
                'proxy': proxy_config,
                'viewport': {'width': 1920, 'height': 1080},
                'ignore_https_errors': True,
                'java_script_enabled': not ultra_low_cpu,
            }
            
            # Add executable_path if specific version requested
            if executable_path:
                launch_options['executable_path'] = executable_path
            
            # Merge with remaining kwargs (only valid Playwright options)
            launch_options.update(kwargs)
            
            context = await self.playwright.chromium.launch_persistent_context(**launch_options)
            
            # Store context
            self.contexts[profile_name] = context
            
            # Get or create page (don't close old tabs to avoid errors)
            if len(context.pages) > 0:
                # Use first existing page and navigate to URL
                page = context.pages[0]
                print(f"[BROWSER] Using existing page (current: {page.url})")
            else:
                # No pages exist, create new one
                print(f"[BROWSER] Creating new page...")
                page = await context.new_page()
                print(f"[BROWSER] ✅ New page created")
            
            self.pages[profile_name] = page
            
            # Wait for extensions to initialize (especially proxy auth extension)
            if extension_paths:
                # Longer delay if using system Chrome (version mismatch)
                delay = 5 if executable_path and 'Program Files' in executable_path else 3
                print(f"[BROWSER] Waiting {delay}s for extensions to initialize...")
                await asyncio.sleep(delay)
                print(f"[BROWSER] ✅ Extensions ready")
            
            # Navigate to URL if provided
            if url:
                # Check if using system Chrome (may need extra retries for proxy)
                using_system_chrome = executable_path and 'Program Files' in executable_path
                max_retries = 3 if using_system_chrome else 2
                
                for attempt in range(max_retries):
                    try:
                        if attempt > 0:
                            wait_time = 3 * attempt  # 3s, 6s
                            print(f"[BROWSER] Waiting {wait_time}s for proxy auth extension...")
                            await asyncio.sleep(wait_time)
                        
                        current_url = page.url
                        print(f"[BROWSER] Navigating from {current_url} to {url}... (attempt {attempt + 1}/{max_retries})")
                        await page.goto(url, wait_until='domcontentloaded', timeout=30000)
                        print(f"[BROWSER] ✅ Navigation complete")
                        break  # Success, exit retry loop
                        
                    except Exception as e:
                        error_msg = str(e)
                        if 'ERR_INVALID_AUTH_CREDENTIALS' in error_msg or 'ERR_PROXY' in error_msg:
                            if attempt < max_retries - 1:
                                print(f"[WARNING] Proxy auth failed, retrying... ({attempt + 1}/{max_retries})")
                                continue
                            else:
                                print(f"[ERROR] Proxy auth failed after {max_retries} attempts")
                                print(f"[ERROR] This usually happens when:")
                                print(f"  1. Proxy credentials are incorrect")
                                print(f"  2. Chrome version mismatch (using system Chrome instead of GPM Chrome)")
                                print(f"  3. Proxy auth extension not loaded properly")
                                print(f"[SOLUTION] Download Chrome {desired_version} in GPM Browser for best compatibility")
                                raise
                        else:
                            print(f"[ERROR] Navigation failed: {e}")
                            if attempt < max_retries - 1:
                                print(f"[BROWSER] Retrying with different strategy...")
                            else:
                                print(f"[ERROR] All navigation attempts failed")
                                raise
            
            # Inject JavaScript to disable audio at page level
            try:
                await page.add_init_script("""
                    // Disable all audio/video playback
                    Object.defineProperty(HTMLMediaElement.prototype, 'volume', {
                        set: function() {},
                        get: function() { return 0; }
                    });
                    
                    Object.defineProperty(HTMLMediaElement.prototype, 'muted', {
                        set: function() {},
                        get: function() { return true; }
                    });
                    
                    // Override play() to mute first
                    const originalPlay = HTMLMediaElement.prototype.play;
                    HTMLMediaElement.prototype.play = function() {
                        this.muted = true;
                        this.volume = 0;
                        return originalPlay.apply(this, arguments);
                    };
                    
                    // Disable Web Audio API
                    if (window.AudioContext) {
                        window.AudioContext = function() {};
                    }
                    if (window.webkitAudioContext) {
                        window.webkitAudioContext = function() {};
                    }
                """)
                print(f"[BROWSER] ✅ Audio disabled via JavaScript injection")
            except Exception as e:
                print(f"[WARNING] Could not inject audio disable script: {e}")
            
            # Perform autofill if login_data provided
            if auto_login and login_data:
                print(f"[AUTOFILL] Auto-login requested, performing keyboard autofill...")
                try:
                    from ..tiles.tile_autofill import perform_keyboard_autofill_async
                    
                    # Get username_has_warning_icon setting from login_data
                    username_has_warning_icon = login_data.get('username_has_warning_icon', False)
                    
                    # Perform autofill synchronously (wait for it to complete)
                    await perform_keyboard_autofill_async(page, login_data, delay=5.0, username_has_warning_icon=username_has_warning_icon)
                    
                except Exception as autofill_err:
                    print(f"[WARNING] [AUTOFILL] Failed: {autofill_err}")
                    import traceback
                    traceback.print_exc()
            
            # Minimize window if requested (chỉ khi headless=False)
            if minimize and not headless:
                print(f"[BROWSER] Minimizing window for {profile_name}...")
                
                # Wait a bit for window to fully render
                await asyncio.sleep(0.5)
                
                minimized = False
                
                # Method 1: Try CDP (Chrome DevTools Protocol)
                try:
                    cdp_session = await context.new_cdp_session(page)
                    
                    # Get window ID
                    window_info = await cdp_session.send('Browser.getWindowForTarget')
                    window_id = window_info['windowId']
                    
                    # Minimize window
                    await cdp_session.send('Browser.setWindowBounds', {
                        'windowId': window_id,
                        'bounds': {'windowState': 'minimized'}
                    })
                    
                    print(f"[BROWSER] ✅ Window minimized via CDP")
                    minimized = True
                    
                except Exception as e:
                    print(f"[WARNING] CDP minimize failed: {e}")
                
                # Method 2: Fallback to pyautogui if CDP failed
                if not minimized:
                    try:
                        import pyautogui as pg
                        import time
                        
                        # Wait a bit more
                        time.sleep(0.3)
                        
                        # Windows: Win+Down minimizes active window
                        pg.hotkey('win', 'down')
                        
                        print(f"[BROWSER] ✅ Window minimized via pyautogui")
                        minimized = True
                        
                    except Exception as e:
                        print(f"[WARNING] pyautogui minimize failed: {e}")
                
                # Method 3: Last resort - use win32gui (Windows only)
                if not minimized:
                    try:
                        import win32gui
                        import win32con
                        import time
                        
                        time.sleep(0.3)
                        
                        # Find Chrome window by title (contains profile name or URL)
                        def find_chrome_window(hwnd, windows):
                            if win32gui.IsWindowVisible(hwnd):
                                title = win32gui.GetWindowText(hwnd)
                                if 'Chrome' in title or 'Google' in title:
                                    windows.append(hwnd)
                        
                        windows = []
                        win32gui.EnumWindows(find_chrome_window, windows)
                        
                        # Minimize the most recent Chrome window (last in list)
                        if windows:
                            hwnd = windows[-1]
                            win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
                            print(f"[BROWSER] ✅ Window minimized via win32gui")
                            minimized = True
                        
                    except Exception as e:
                        print(f"[WARNING] win32gui minimize failed: {e}")
                
                if not minimized:
                    print(f"[ERROR] All minimize methods failed!")
            
            return page
            
        except Exception as e:
            print(f"Error launching {profile_name}: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    async def close_profile(self, profile_name: str):
        """Đóng một profile"""
        if profile_name in self.contexts:
            try:
                await self.contexts[profile_name].close()
            except:
                pass
            del self.contexts[profile_name]
        
        if profile_name in self.pages:
            del self.pages[profile_name]
    
    async def close_all_profiles(self):
        """Đóng tất cả profiles"""
        for profile_name in list(self.contexts.keys()):
            await self.close_profile(profile_name)
    
    def get_page(self, profile_name: str) -> Optional[Page]:
        """Lấy Page object của profile"""
        return self.pages.get(profile_name)
    
    def get_context(self, profile_name: str) -> Optional[BrowserContext]:
        """Lấy BrowserContext của profile"""
        return self.contexts.get(profile_name)
    
    def is_profile_running(self, profile_name: str) -> bool:
        """Kiểm tra profile có đang chạy không"""
        return profile_name in self.contexts
    
    def get_running_profiles(self) -> List[str]:
        """Lấy danh sách profiles đang chạy"""
        return list(self.contexts.keys())
    
    async def execute_script(self, profile_name: str, script: str) -> any:
        """Execute JavaScript trong profile"""
        page = self.get_page(profile_name)
        if page:
            return await page.evaluate(script)
        return None
    
    async def screenshot(self, profile_name: str, path: str):
        """Chụp screenshot của profile"""
        page = self.get_page(profile_name)
        if page:
            await page.screenshot(path=path)
    
    async def get_cookies(self, profile_name: str) -> List[Dict]:
        """Lấy cookies của profile"""
        context = self.get_context(profile_name)
        if context:
            return await context.cookies()
        return []
    
    async def set_cookies(self, profile_name: str, cookies: List[Dict]):
        """Set cookies cho profile"""
        context = self.get_context(profile_name)
        if context:
            await context.add_cookies(cookies)
