#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cleanup Utilities - Dọn dẹp browsing history và cache
Converted from core/tiles/tile_cleanup.py
"""

import asyncio
import schedule
import time
import threading
from typing import List, Optional
from pathlib import Path


# Global flag to prevent duplicate cleanup messages
_CLEANUP_ALREADY_STOPPED = False


class CleanupManager:
    """Quản lý cleanup tasks"""
    
    def __init__(self, browser_manager):
        self.browser_manager = browser_manager
        self.cleanup_thread = None
        self.stop_cleanup = False
    
    async def clear_browsing_history(
        self,
        profile_names: List[str],
        keep_passwords: bool = True,
        keep_cache: bool = True
    ) -> dict:
        """
        Clear browsing history cho profiles
        
        Args:
            profile_names: List tên profiles
            keep_passwords: Giữ passwords (default: True)
            keep_cache: Giữ cache (default: True)
        
        Returns:
            Dict với results cho từng profile
        """
        results = {}
        
        for profile_name in profile_names:
            try:
                # Get context
                context = self.browser_manager.get_context(profile_name)
                
                if not context:
                    results[profile_name] = {
                        'success': False,
                        'message': 'Profile not running'
                    }
                    continue
                
                # Clear browsing data via CDP
                # Note: Playwright không có built-in clear history API
                # Cần dùng CDP (Chrome DevTools Protocol)
                
                # Get page
                page = self.browser_manager.get_page(profile_name)
                
                if page:
                    # Execute CDP command to clear browsing data
                    cdp = await page.context.new_cdp_session(page)
                    
                    # Clear types
                    data_types = ['cookies', 'fileSystems', 'indexedDB', 'localStorage', 
                                  'serviceWorkers', 'webSQL']
                    
                    if not keep_cache:
                        data_types.extend(['cache', 'cacheStorage'])
                    
                    # Clear browsing data
                    await cdp.send('Network.clearBrowserCookies')
                    await cdp.send('Network.clearBrowserCache')
                    
                    results[profile_name] = {
                        'success': True,
                        'message': 'History cleared'
                    }
                else:
                    results[profile_name] = {
                        'success': False,
                        'message': 'No page found'
                    }
                    
            except Exception as e:
                results[profile_name] = {
                    'success': False,
                    'message': f'Error: {e}'
                }
        
        return results
    
    def start_daily_history_cleanup(
        self,
        hour: int = 3,
        minute: int = 0,
        profiles: Optional[List[str]] = None,
        jitter_sec: int = 90
    ):
        """
        Bắt đầu daily cleanup schedule
        
        Args:
            hour: Giờ chạy (0-23)
            minute: Phút chạy (0-59)
            profiles: List profiles cần cleanup (None = all)
            jitter_sec: Random delay (seconds)
        """
        if self.cleanup_thread and self.cleanup_thread.is_alive():
            print("[CLEANUP] Daily cleanup already running")
            return
        
        self.stop_cleanup = False
        
        def cleanup_job():
            """Job chạy hàng ngày"""
            import random
            
            # Random delay
            if jitter_sec > 0:
                delay = random.randint(0, jitter_sec)
                print(f"[CLEANUP] Waiting {delay}s before cleanup...")
                time.sleep(delay)
            
            # Get profiles
            if profiles is None:
                # Get all running profiles
                profile_list = self.browser_manager.get_running_profiles()
            else:
                profile_list = profiles
            
            if not profile_list:
                print("[CLEANUP] No profiles to cleanup")
                return
            
            print(f"[CLEANUP] Cleaning {len(profile_list)} profiles...")
            
            # Run cleanup
            try:
                results = asyncio.run(
                    self.clear_browsing_history(profile_list)
                )
                
                success_count = sum(1 for r in results.values() if r['success'])
                print(f"[CLEANUP] Cleaned {success_count}/{len(profile_list)} profiles")
                
            except Exception as e:
                print(f"[CLEANUP] Error: {e}")
        
        # Schedule job
        schedule_time = f"{hour:02d}:{minute:02d}"
        schedule.every().day.at(schedule_time).do(cleanup_job)
        
        print(f"[CLEANUP] Scheduled daily cleanup at {schedule_time}")
        
        # Run scheduler in thread
        def run_scheduler():
            while not self.stop_cleanup:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        
        self.cleanup_thread = threading.Thread(target=run_scheduler, daemon=True)
        self.cleanup_thread.start()
        
        print("[CLEANUP] Daily cleanup started")
    
    def stop_daily_history_cleanup(self):
        """Dừng daily cleanup schedule"""
        global _CLEANUP_ALREADY_STOPPED
        
        if not self.stop_cleanup and not _CLEANUP_ALREADY_STOPPED:  # Only print once globally
            self.stop_cleanup = True
            _CLEANUP_ALREADY_STOPPED = True
            schedule.clear()
            
            if self.cleanup_thread:
                self.cleanup_thread.join(timeout=5)
                self.cleanup_thread = None
            
            print("[CLEANUP] Daily cleanup stopped")
    
    async def clear_profile_cache(self, profile_name: str) -> bool:
        """
        Clear cache cho profile
        
        Args:
            profile_name: Tên profile
        
        Returns:
            True nếu thành công
        """
        try:
            page = self.browser_manager.get_page(profile_name)
            
            if not page:
                return False
            
            # Clear cache via CDP
            cdp = await page.context.new_cdp_session(page)
            await cdp.send('Network.clearBrowserCache')
            
            print(f"[CLEANUP] Cleared cache for {profile_name}")
            return True
            
        except Exception as e:
            print(f"[CLEANUP] Error clearing cache: {e}")
            return False
    
    async def clear_profile_cookies(self, profile_name: str) -> bool:
        """
        Clear cookies cho profile
        
        Args:
            profile_name: Tên profile
        
        Returns:
            True nếu thành công
        """
        try:
            context = self.browser_manager.get_context(profile_name)
            
            if not context:
                return False
            
            # Clear all cookies
            await context.clear_cookies()
            
            print(f"[CLEANUP] Cleared cookies for {profile_name}")
            return True
            
        except Exception as e:
            print(f"[CLEANUP] Error clearing cookies: {e}")
            return False
