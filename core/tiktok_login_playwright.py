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


# ============================================================================
# HELPER FUNCTIONS - Login Status Verification
# ============================================================================

def is_login_success_url(url: str) -> bool:
    """
    Check xem URL có phải là login success không
    
    CRITICAL: Phải check URL chuyển từ /login sang /foryou hoặc homepage
    để đảm bảo login thành công thật sự
    
    Args:
        url: Current page URL
    
    Returns:
        True nếu login success, False nếu không
    """
    # Normalize URL
    url = url.lower().rstrip('/')
    
    # CRITICAL: Nếu vẫn ở /login thì chưa success
    if '/login' in url:
        return False
    
    # Check các URL patterns cho login success
    success_patterns = [
        '/foryou',      # For You page (main feed)
        '/following',   # Following page
        '/@',           # Profile page
        '/explore',     # Explore page
        '/live',        # Live page
    ]
    
    # Check nếu URL chứa 1 trong các patterns success
    for pattern in success_patterns:
        if pattern in url:
            return True
    
    # Hoặc nếu là homepage (không có path cụ thể)
    if url in ['https://www.tiktok.com', 'https://tiktok.com', 'http://www.tiktok.com', 'http://tiktok.com']:
        return True
    
    # Nếu không match pattern nào thì coi như chưa success
    return False


async def verify_login_status(page) -> Tuple[bool, str]:
    """
    Verify login status bằng cách check URL
    
    Returns:
        (is_logged_in, current_url)
    """
    try:
        current_url = page.url
        is_logged_in = is_login_success_url(current_url)
        return is_logged_in, current_url
    except Exception as e:
        logger.error(f"[VERIFY-LOGIN] Error: {e}")
        return False, str(e)


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
        """
        Wait for login to complete
        
        IMPROVED: Check URL chuyển từ /login sang /foryou hoặc homepage
        để đảm bảo login thành công thật sự
        """
        self.logger.info("[LOGIN-PW] Waiting for login to complete...")
        
        start_time = asyncio.get_event_loop().time()
        
        while True:
            elapsed = asyncio.get_event_loop().time() - start_time
            if elapsed > timeout:
                self.logger.warning(f"[LOGIN-PW] Timeout after {timeout}s")
                return False, page.url
            
            try:
                current_url = page.url
                
                # IMPROVED: Sử dụng helper function để check login success
                is_logged_in = is_login_success_url(current_url)
                
                if is_logged_in:
                    self.logger.info(f"[LOGIN-PW] ✅ Login successful! Redirected to: {current_url}")
                    return True, current_url
                
                # Log current status
                if '/login' in current_url:
                    self.logger.debug(f"[LOGIN-PW] Still on login page... ({elapsed:.1f}s)")
                else:
                    self.logger.warning(f"[LOGIN-PW] ⚠️  Not on login page but not on success page either: {current_url}")
                
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
