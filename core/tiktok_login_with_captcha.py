#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TikTok Login với Auto Captcha Solver
Tích hợp captcha solver vào quá trình login
"""

import asyncio
import logging
from typing import Optional, Tuple, Dict, Any

logger = logging.getLogger(__name__)


class TikTokLoginWithCaptcha:
    """
    Wrapper để login TikTok với auto captcha solving
    
    Usage:
        login_handler = TikTokLoginWithCaptcha(captcha_solver)
        success, page = await login_handler.login_with_auto_captcha(
            page, username, password
        )
    """
    
    def __init__(self, captcha_solver=None):
        """
        Args:
            captcha_solver: TikTokCaptchaSolver instance (optional)
        """
        self.captcha_solver = captcha_solver
        self.logger = logger
    
    async def wait_for_login_complete(
        self,
        page,
        timeout: int = 60,
        check_interval: float = 2.0
    ) -> Tuple[bool, str]:
        """
        Chờ login hoàn tất, tự động giải captcha nếu xuất hiện
        
        Args:
            page: Playwright page
            timeout: Timeout tổng (seconds)
            check_interval: Khoảng thời gian check (seconds)
            
        Returns:
            Tuple (success, current_url)
        """
        self.logger.info("[LOGIN-CAPTCHA] Waiting for login to complete...")
        
        start_time = asyncio.get_event_loop().time()
        check_count = 0
        
        while True:
            elapsed = asyncio.get_event_loop().time() - start_time
            if elapsed > timeout:
                self.logger.warning(f"[LOGIN-CAPTCHA] Timeout after {timeout}s")
                return False, page.url
            
            check_count += 1
            self.logger.debug(f"[LOGIN-CAPTCHA] Check #{check_count} (elapsed: {elapsed:.1f}s)")
            
            try:
                current_url = page.url
                
                # Check if login successful (not on login page anymore)
                if '/login' not in current_url:
                    self.logger.info(f"[LOGIN-CAPTCHA] ✅ Login successful! URL: {current_url}")
                    return True, current_url
                
                # Check for captcha
                if self.captcha_solver:
                    captcha_type = await self.captcha_solver.detect_captcha(page)
                    
                    if captcha_type:
                        self.logger.info(f"[LOGIN-CAPTCHA] 🎯 Captcha detected during login: {captcha_type}")
                        
                        # Solve captcha
                        solution = await self.captcha_solver.solve_captcha(
                            page,
                            captcha_type,
                            max_retries=3
                        )
                        
                        if solution:
                            self.logger.info("[LOGIN-CAPTCHA] ✅ Captcha solved, continuing login...")
                            # Wait a bit for page to process
                            await asyncio.sleep(2)
                        else:
                            self.logger.error("[LOGIN-CAPTCHA] ❌ Failed to solve captcha")
                            return False, current_url
                
                # Wait before next check
                await asyncio.sleep(check_interval)
                
            except Exception as e:
                self.logger.error(f"[LOGIN-CAPTCHA] Error: {e}")
                await asyncio.sleep(check_interval)
        
        return False, page.url
    
    async def fill_and_submit_login(
        self,
        page,
        username: str,
        password: str,
        auto_solve_captcha: bool = True
    ) -> Tuple[bool, str]:
        """
        Fill login form và submit, tự động xử lý captcha
        
        Args:
            page: Playwright page
            username: Username hoặc email
            password: Password
            auto_solve_captcha: Tự động giải captcha
            
        Returns:
            Tuple (success, message)
        """
        try:
            self.logger.info(f"[LOGIN-CAPTCHA] Filling login form for: {username}")
            
            # Wait for login form
            await page.wait_for_selector('input[name="username"]', timeout=10000)
            
            # Fill username
            await page.fill('input[name="username"]', username)
            self.logger.debug("[LOGIN-CAPTCHA] Username filled")
            
            await asyncio.sleep(0.5)
            
            # Fill password
            await page.fill('input[type="password"]', password)
            self.logger.debug("[LOGIN-CAPTCHA] Password filled")
            
            await asyncio.sleep(0.5)
            
            # Click login button
            login_button = await page.query_selector('button[type="submit"]')
            if login_button:
                await login_button.click()
                self.logger.info("[LOGIN-CAPTCHA] Login button clicked")
            else:
                self.logger.warning("[LOGIN-CAPTCHA] Login button not found, trying Enter key")
                await page.press('input[type="password"]', 'Enter')
            
            # Wait for response
            await asyncio.sleep(2)
            
            # Check for captcha immediately after submit
            if auto_solve_captcha and self.captcha_solver:
                self.logger.info("[LOGIN-CAPTCHA] Checking for captcha after submit...")
                
                captcha_type = await self.captcha_solver.detect_captcha(page)
                
                if captcha_type:
                    self.logger.info(f"[LOGIN-CAPTCHA] 🎯 Captcha appeared: {captcha_type}")
                    
                    solution = await self.captcha_solver.solve_captcha(
                        page,
                        captcha_type,
                        max_retries=3
                    )
                    
                    if not solution:
                        return False, "Failed to solve captcha"
                    
                    self.logger.info("[LOGIN-CAPTCHA] ✅ Captcha solved")
                    await asyncio.sleep(2)
            
            # Wait for login to complete
            success, final_url = await self.wait_for_login_complete(page, timeout=60)
            
            if success:
                return True, f"Login successful: {final_url}"
            else:
                return False, f"Login failed or timeout: {final_url}"
            
        except Exception as e:
            self.logger.error(f"[LOGIN-CAPTCHA] Error: {e}")
            return False, str(e)
    
    async def monitor_and_solve_captcha_during_action(
        self,
        page,
        action_func,
        timeout: int = 30
    ) -> Tuple[bool, Any]:
        """
        Monitor captcha trong khi thực hiện action
        
        Args:
            page: Playwright page
            action_func: Async function to execute
            timeout: Timeout (seconds)
            
        Returns:
            Tuple (success, result)
        """
        try:
            # Start monitoring task
            async def monitor_captcha():
                while True:
                    if self.captcha_solver:
                        captcha_type = await self.captcha_solver.detect_captcha(page)
                        if captcha_type:
                            self.logger.info(f"[MONITOR] Captcha detected: {captcha_type}")
                            await self.captcha_solver.solve_captcha(page, captcha_type)
                    await asyncio.sleep(2)
            
            # Run action and monitoring concurrently
            monitor_task = asyncio.create_task(monitor_captcha())
            action_task = asyncio.create_task(action_func())
            
            # Wait for action to complete
            done, pending = await asyncio.wait(
                [action_task],
                timeout=timeout
            )
            
            # Cancel monitoring
            monitor_task.cancel()
            
            if action_task in done:
                result = action_task.result()
                return True, result
            else:
                return False, "Timeout"
            
        except Exception as e:
            self.logger.error(f"[MONITOR] Error: {e}")
            return False, str(e)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

async def login_tiktok_with_captcha_handling(
    page,
    username: str,
    password: str,
    captcha_solver=None
) -> Tuple[bool, str]:
    """
    Helper function: Login TikTok với auto captcha handling
    
    Args:
        page: Playwright page
        username: Username hoặc email
        password: Password
        captcha_solver: TikTokCaptchaSolver instance
        
    Returns:
        Tuple (success, message)
    """
    handler = TikTokLoginWithCaptcha(captcha_solver)
    return await handler.fill_and_submit_login(page, username, password)


async def wait_for_page_ready_with_captcha(
    page,
    captcha_solver=None,
    timeout: int = 30
) -> bool:
    """
    Helper function: Chờ page ready, tự động giải captcha nếu có
    
    Args:
        page: Playwright page
        captcha_solver: TikTokCaptchaSolver instance
        timeout: Timeout (seconds)
        
    Returns:
        True nếu page ready
    """
    if not captcha_solver:
        await asyncio.sleep(2)
        return True
    
    return await captcha_solver.wait_and_solve_captcha(page, timeout=timeout)
