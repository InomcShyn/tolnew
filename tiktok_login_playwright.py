#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TikTok Login với Playwright + OMOcaptcha API
Tích hợp captcha solver vào quá trình login
Sử dụng logic từ core copy + API omocaptcha
"""

import asyncio
import logging
from typing import Optional, Tuple, Dict

logger = logging.getLogger(__name__)


class TikTokLoginPlaywright:
    """
    TikTok Login Handler với Playwright + OMOcaptcha
    
    Features:
    - Auto-detect và solve captcha
    - Retry mechanism
    - Login verification
    """
    
    def __init__(self, captcha_solver=None):
        """
        Args:
            captcha_solver: TikTokCaptchaSolverPlaywright instance
        """
        self.captcha_solver = captcha_solver
        self.logger = logger
    
    async def login(
        self,
        page,
        username: str,
        password: str,
        timeout: int = 60
    ) -> Tuple[bool, str]:
        """
        Login to TikTok với auto captcha solving
        
        Args:
            page: Playwright page
            username: Username hoặc email
            password: Password
            timeout: Timeout (seconds)
            
        Returns:
            Tuple (success, message)
        """
        try:
            self.logger.info(f"[LOGIN-PW] Starting login for: {username}")
            
            # Wait for login form
            await page.wait_for_selector('input[name="username"]', timeout=10000)
            
            # Fill username
            await page.fill('input[name="username"]', username)
            self.logger.debug("[LOGIN-PW] Username filled")
            await asyncio.sleep(0.5)
            
            # Fill password
            await page.fill('input[type="password"]', password)
            self.logger.debug("[LOGIN-PW] Password filled")
            await asyncio.sleep(0.5)
            
            # Click login button
            login_button = await page.query_selector('button[type="submit"]')
            if login_button:
                await login_button.click()
                self.logger.info("[LOGIN-PW] Login button clicked")
            else:
                await page.press('input[type="password"]', 'Enter')
                self.logger.info("[LOGIN-PW] Pressed Enter")
            
            # Wait for response
            await asyncio.sleep(2)
            
            # Check for captcha
            if self.captcha_solver:
                captcha_type = await self.captcha_solver.detect_captcha(page)
                
                if captcha_type:
                    self.logger.info(f"[LOGIN-PW] 🎯 Captcha detected: {captcha_type}")
                    
                    # Solve captcha
                    solution = await self.captcha_solver.solve_captcha(page, max_retries=10)
                    
                    if not solution:
                        return False, "Failed to solve captcha"
                    
                    self.logger.info("[LOGIN-PW] ✅ Captcha solved")
                    await asyncio.sleep(2)
            
            # Wait for login to complete
            success, final_url = await self._wait_for_login_complete(page, timeout)
            
            if success:
                return True, f"Login successful: {final_url}"
            else:
                return False, f"Login failed: {final_url}"
            
        except Exception as e:
            self.logger.error(f"[LOGIN-PW] Error: {e}")
            return False, str(e)
    
    async def _wait_for_login_complete(
        self,
        page,
        timeout: int = 60
    ) -> Tuple[bool, str]:
        """Wait for login to complete"""
        self.logger.info("[LOGIN-PW] Waiting for login to complete...")
        
        start_time = asyncio.get_event_loop().time()
        
        while True:
            elapsed = asyncio.get_event_loop().time() - start_time
            if elapsed > timeout:
                self.logger.warning(f"[LOGIN-PW] Timeout after {timeout}s")
                return False, page.url
            
            try:
                current_url = page.url
                
                # Check if login successful
                if '/login' not in current_url:
                    self.logger.info(f"[LOGIN-PW] ✅ Login successful! URL: {current_url}")
                    return True, current_url
                
                # Check for captcha during wait
                if self.captcha_solver:
                    captcha_type = await self.captcha_solver.detect_captcha(page)
                    
                    if captcha_type:
                        self.logger.info(f"[LOGIN-PW] 🎯 Captcha during wait: {captcha_type}")
                        solution = await self.captcha_solver.solve_captcha(page, max_retries=10)
                        
                        if solution:
                            self.logger.info("[LOGIN-PW] ✅ Captcha solved")
                            await asyncio.sleep(2)
                        else:
                            return False, "Failed to solve captcha"
                
                await asyncio.sleep(2)
                
            except Exception as e:
                self.logger.error(f"[LOGIN-PW] Error: {e}")
                await asyncio.sleep(2)
        
        return False, page.url


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

async def login_tiktok_playwright(
    page,
    username: str,
    password: str,
    captcha_solver=None,
    timeout: int = 60
) -> Tuple[bool, str]:
    """
    Helper function: Login TikTok với Playwright + OMOcaptcha
    
    Args:
        page: Playwright page
        username: Username hoặc email
        password: Password
        captcha_solver: TikTokCaptchaSolverPlaywright instance
        timeout: Timeout (seconds)
        
    Returns:
        Tuple (success, message)
    """
    handler = TikTokLoginPlaywright(captcha_solver)
    return await handler.login(page, username, password, timeout)
