#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TikTok Captcha Solver - Playwright + OMOcaptcha API
Kết hợp logic Playwright từ core copy với API omocaptcha
Giải quyết lỗi "maximum" của TikTok bằng cách sử dụng API trực tiếp

Features:
- Playwright backend (từ core copy)
- OMOcaptcha API integration (từ core/omocaptcha_client.py)
- Retry với exponential backoff
- Debug logging chi tiết
- Artifact saving
"""

import asyncio
import base64
import logging
import os
import time
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Tuple, Any
import traceback

logger = logging.getLogger(__name__)


class TikTokCaptchaSolverPlaywright:
    """
    TikTok Captcha Solver với Playwright + OMOcaptcha API
    
    Kết hợp:
    - Playwright page handling (từ core copy)
    - OMOcaptcha API (từ core/omocaptcha_client.py)
    
    Supported types:
    - Rotate (xoay ảnh)
    - Select Object (chọn 2 điểm)
    - 3D Select Object (chọn 2 điểm 3D)
    - Slider (kéo slider)
    """
    
    # TikTok captcha selectors
    CAPTCHA_SELECTORS = {
        'container': [
            '.TUXModal.captcha-verify-container',
            'div.captcha-verify-container',
            '#captcha-verify-container-main-page',
            '[class*="captcha"]',
            '[id*="captcha"]',
            '.secsdk-captcha-container',
        ],
        'image': [
            'img[alt="Captcha"]',
            'img[src^="data:image/webp;base64"]',
            'img[src^="data:image/"]',
            '.captcha-verify-container img',
            '.TUXModal img',
            'img[class*="captcha"]',
            'canvas[class*="captcha"]',
        ],
        'slider': [
            'button#captcha_slide_button',
            'button.secsdk-captcha-drag-icon',
            'div[draggable="true"]',
            '[class*="secsdk-captcha-drag"]',
            'button[class*="slider"]',
        ],
        'rotate': [
            '[class*="captcha-rotate"]',
            '[class*="rotate-captcha"]',
        ],
    }
    
    def __init__(self, omocaptcha_client, debug_level: str = "INFO", 
                 artifacts_dir: str = "logs/captcha_playwright",
                 rate_limit_delay: float = 1.0):
        """
        Args:
            omocaptcha_client: Instance of OMOcaptchaClient
            debug_level: Logging level (DEBUG/INFO/WARN/ERROR)
            artifacts_dir: Directory to save debug artifacts
            rate_limit_delay: Minimum delay between API calls (seconds)
        """
        self.client = omocaptcha_client
        self.logger = logger
        self.debug_level = debug_level
        self.artifacts_dir = Path(artifacts_dir)
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)
        self.rate_limit_delay = rate_limit_delay
        self.last_api_call = 0
        
        # Configure logging
        if debug_level == "DEBUG":
            self.logger.setLevel(logging.DEBUG)
        elif debug_level == "INFO":
            self.logger.setLevel(logging.INFO)
        
        self.logger.info(f"[CAPTCHA-PW] Initialized with Playwright + OMOcaptcha API")
        self.logger.info(f"[CAPTCHA-PW] Artifacts: {self.artifacts_dir}")
    
    async def _enforce_rate_limit(self):
        """Enforce rate limiting between API calls"""
        elapsed = time.time() - self.last_api_call
        if elapsed < self.rate_limit_delay:
            wait_time = self.rate_limit_delay - elapsed
            self.logger.debug(f"[RATE_LIMIT] Waiting {wait_time:.2f}s")
            await asyncio.sleep(wait_time)
        self.last_api_call = time.time()
    
    async def _save_artifact(self, artifact_type: str, data: Any, extension: str = "txt"):
        """Save debug artifact"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            filename = f"{artifact_type}_{timestamp}.{extension}"
            filepath = self.artifacts_dir / filename
            
            if extension == "json":
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            elif extension == "png":
                with open(filepath, 'wb') as f:
                    f.write(data)
            else:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(str(data))
            
            self.logger.debug(f"[ARTIFACT] Saved to {filepath}")
            return str(filepath)
        except Exception as e:
            self.logger.error(f"[ARTIFACT] Failed: {e}")
            return None
    
    async def detect_captcha(self, page) -> Optional[str]:
        """
        Detect captcha type
        
        Args:
            page: Playwright page object
            
        Returns:
            Captcha type (rotate/select/3d/slider) or None
        """
        self.logger.debug("[DETECT] Checking for captcha...")
        
        try:
            # Check for container
            for selector in self.CAPTCHA_SELECTORS['container']:
                element = await page.query_selector(selector)
                if element:
                    is_visible = await element.is_visible()
                    if is_visible:
                        self.logger.info(f"[DETECT] ✅ Found: {selector}")
                        return await self._detect_captcha_type(page, element)
            
            return None
            
        except Exception as e:
            self.logger.error(f"[DETECT] Error: {e}")
            return None
    
    async def _detect_captcha_type(self, page, container) -> Optional[str]:
        """Detect specific captcha type"""
        try:
            # Check for rotate (includes "fit the puzzle" which is also rotate type)
            for selector in self.CAPTCHA_SELECTORS['rotate']:
                rotate = await page.query_selector(selector)
                if rotate and await rotate.is_visible():
                    self.logger.info("[DETECT] Type: ROTATE")
                    return "rotate"
            
            # Check for slider
            for selector in self.CAPTCHA_SELECTORS['slider']:
                slider = await page.query_selector(selector)
                if slider and await slider.is_visible():
                    self.logger.info("[DETECT] Type: SLIDER")
                    return "slider"
            
            # Default to slider (most common)
            self.logger.info("[DETECT] Type: SLIDER (default)")
            return "slider"
            
        except Exception as e:
            self.logger.error(f"[DETECT] Type error: {e}")
            return None
    
    async def capture_captcha_image(self, page, captcha_type: str) -> Optional[Tuple[str, int, int]]:
        """
        Capture captcha image
        
        Returns:
            Tuple (base64_image, width, height) or None
        """
        self.logger.debug("[CAPTURE] Starting...")
        
        try:
            # Find image element
            image_element = None
            found_selector = None
            
            for selector in self.CAPTCHA_SELECTORS['image']:
                element = await page.query_selector(selector)
                if element and await element.is_visible():
                    image_element = element
                    found_selector = selector
                    break
            
            # Try container if no image found
            if not image_element:
                for selector in self.CAPTCHA_SELECTORS['container']:
                    element = await page.query_selector(selector)
                    if element and await element.is_visible():
                        image_element = element
                        found_selector = f"container: {selector}"
                        break
            
            if not image_element:
                self.logger.error("[CAPTURE] ❌ No image found")
                # Save page screenshot for debug
                screenshot = await page.screenshot()
                await self._save_artifact("no_image", screenshot, "png")
                return None
            
            self.logger.info(f"[CAPTURE] Found: {found_selector}")
            
            # Get dimensions
            box = await image_element.bounding_box()
            if not box:
                self.logger.error("[CAPTURE] ❌ No bounding box")
                return None
            
            width = int(box['width'])
            height = int(box['height'])
            
            # Capture screenshot
            screenshot = await image_element.screenshot()
            image_base64 = base64.b64encode(screenshot).decode('utf-8')
            
            self.logger.info(f"[CAPTURE] ✅ {len(image_base64)} bytes, {width}x{height}px")
            
            # Save artifact
            await self._save_artifact("captcha_image", screenshot, "png")
            
            return (image_base64, width, height)
            
        except Exception as e:
            self.logger.error(f"[CAPTURE] Error: {e}")
            self.logger.debug(traceback.format_exc())
            return None
    
    async def solve_captcha(self, page, captcha_type: str = None, max_retries: int = 10) -> Optional[Dict]:
        """
        Solve captcha using OMOcaptcha API
        
        Args:
            page: Playwright page
            captcha_type: Captcha type (auto-detect if None)
            max_retries: Max retry attempts
            
        Returns:
            Solution dict or None
        """
        self.logger.info(f"[SOLVE] Starting (max_retries={max_retries})...")
        
        for attempt in range(max_retries):
            try:
                self.logger.info(f"[SOLVE] ═══ Attempt {attempt + 1}/{max_retries} ═══")
                
                # Exponential backoff
                if attempt > 0:
                    delay = 2 ** (attempt - 1)
                    self.logger.info(f"[SOLVE] Waiting {delay:.1f}s...")
                    await asyncio.sleep(delay)
                
                # Auto-detect type if not provided
                if not captcha_type:
                    captcha_type = await self.detect_captcha(page)
                    if not captcha_type:
                        self.logger.error("[SOLVE] ❌ No captcha detected")
                        continue
                
                # Capture image
                capture_result = await self.capture_captcha_image(page, captcha_type)
                if not capture_result:
                    self.logger.error("[SOLVE] ❌ Failed to capture")
                    continue
                
                image_base64, width, height = capture_result
                
                # Enforce rate limit
                await self._enforce_rate_limit()
                
                # Call OMOcaptcha API
                self.logger.info(f"[SOLVE] Calling API for {captcha_type}...")
                api_start = time.time()
                
                solution = self.client.solve_captcha_auto(
                    captcha_type,
                    image_base64,
                    width=width,
                    height=height
                )
                
                api_duration = time.time() - api_start
                self.logger.info(f"[SOLVE] API completed in {api_duration:.2f}s")
                
                if not solution:
                    self.logger.error("[SOLVE] ❌ No solution from API")
                    # Refresh captcha for next attempt
                    if attempt < max_retries - 1:
                        await self._refresh_captcha(page)
                    continue
                
                self.logger.info(f"[SOLVE] ✅ Solution: {solution}")
                
                # Save solution artifact
                await self._save_artifact("solution", {
                    "attempt": attempt + 1,
                    "captcha_type": captcha_type,
                    "solution": solution,
                    "api_duration": api_duration
                }, "json")
                
                # Apply solution
                self.logger.info("[SOLVE] Applying solution...")
                success = await self._apply_solution(page, captcha_type, solution)
                
                if success:
                    self.logger.info("[SOLVE] ✅ Applied")
                    
                    # Verify
                    await asyncio.sleep(2)
                    still_there = await self.detect_captcha(page)
                    
                    if not still_there:
                        self.logger.info("[SOLVE] ✅✅✅ SOLVED! ✅✅✅")
                        return solution
                    else:
                        self.logger.warning("[SOLVE] ⚠️ Still present")
                        # Refresh for next attempt
                        if attempt < max_retries - 1:
                            await self._refresh_captcha(page)
                else:
                    self.logger.error("[SOLVE] ❌ Failed to apply")
                    if attempt < max_retries - 1:
                        await self._refresh_captcha(page)
                
            except Exception as e:
                self.logger.error(f"[SOLVE] ❌ Exception: {e}")
                self.logger.debug(traceback.format_exc())
                
                # Save error artifact
                await self._save_artifact("error", {
                    "attempt": attempt + 1,
                    "error": str(e),
                    "traceback": traceback.format_exc()
                }, "json")
        
        self.logger.error(f"[SOLVE] ❌❌❌ FAILED after {max_retries} attempts ❌❌❌")
        return None
    
    async def _refresh_captcha(self, page) -> bool:
        """Refresh captcha to get new one"""
        try:
            self.logger.info("[REFRESH] Refreshing captcha...")
            
            # Find refresh button
            refresh_selectors = [
                'svg[fill="currentColor"]',
                'button:has(svg)',
                'div:has(svg[viewBox="0 0 72 72"])',
                'button[class*="refresh"]',
                '.secsdk-captcha-refresh',
            ]
            
            for selector in refresh_selectors:
                btn = await page.query_selector(selector)
                if btn:
                    try:
                        await btn.click(force=True, timeout=5000)
                        await asyncio.sleep(2)
                        self.logger.info("[REFRESH] ✅ Refreshed")
                        return True
                    except:
                        continue
            
            self.logger.warning("[REFRESH] ⚠️ Button not found")
            return False
            
        except Exception as e:
            self.logger.error(f"[REFRESH] Error: {e}")
            return False
    
    async def _apply_solution(self, page, captcha_type: str, solution) -> bool:
        """Apply solution to captcha"""
        self.logger.info(f"[APPLY] Type: {captcha_type}")
        
        try:
            if captcha_type == "rotate":
                return await self._apply_rotate(page, solution)
            elif captcha_type in ["select", "3d"]:
                return await self._apply_select(page, solution)
            elif captcha_type == "slider":
                return await self._apply_slider(page, solution)
            else:
                self.logger.error(f"[APPLY] Unknown type: {captcha_type}")
                return False
                
        except Exception as e:
            self.logger.error(f"[APPLY] Error: {e}")
            self.logger.debug(traceback.format_exc())
            return False
    
    async def _apply_rotate(self, page, solution) -> bool:
        """Apply rotate solution"""
        try:
            rotate_degree = solution if isinstance(solution, (int, float)) else solution.get('rotate', 0)
            self.logger.info(f"[APPLY-ROTATE] Rotating {rotate_degree}°...")
            
            # Find draggable element
            slider = await page.query_selector('div[draggable="true"]')
            if not slider:
                self.logger.error("[APPLY-ROTATE] ❌ No draggable element")
                return False
            
            box = await slider.bounding_box()
            if not box:
                return False
            
            # Calculate drag distance
            # TikTok rotate: 360° = track width (usually ~284px)
            track_width = 284  # Typical TikTok track width
            target_x = (1 - rotate_degree / 360) * track_width
            
            self.logger.info(f"[APPLY-ROTATE] Dragging to {target_x}px...")
            
            # Perform drag
            start_x = box['x'] + box['width'] / 2
            start_y = box['y'] + box['height'] / 2
            
            await page.mouse.move(start_x, start_y)
            await asyncio.sleep(0.1)
            await page.mouse.down()
            await asyncio.sleep(0.1)
            
            # Smooth drag with steps
            steps = 30
            for i in range(steps + 1):
                progress = i / steps
                current_x = start_x + (target_x * progress)
                await page.mouse.move(current_x, start_y)
                await asyncio.sleep(0.02)
            
            await asyncio.sleep(0.1)
            await page.mouse.up()
            
            self.logger.info("[APPLY-ROTATE] ✅ Drag completed")
            return True
            
        except Exception as e:
            self.logger.error(f"[APPLY-ROTATE] Error: {e}")
            return False
    
    async def _apply_select(self, page, solution) -> bool:
        """Apply select solution"""
        try:
            pointA, pointB = solution
            self.logger.info(f"[APPLY-SELECT] Points: A({pointA['x']}, {pointA['y']}), B({pointB['x']}, {pointB['y']})")
            
            # Find image element
            image_element = None
            for selector in self.CAPTCHA_SELECTORS['image']:
                element = await page.query_selector(selector)
                if element and await element.is_visible():
                    image_element = element
                    break
            
            if not image_element:
                self.logger.error("[APPLY-SELECT] ❌ No image element")
                return False
            
            box = await image_element.bounding_box()
            if not box:
                return False
            
            # Calculate absolute coordinates
            abs_x_a = box['x'] + pointA['x']
            abs_y_a = box['y'] + pointA['y']
            abs_x_b = box['x'] + pointB['x']
            abs_y_b = box['y'] + pointB['y']
            
            # Click points
            await page.mouse.click(abs_x_a, abs_y_a)
            await asyncio.sleep(0.5)
            await page.mouse.click(abs_x_b, abs_y_b)
            
            self.logger.info("[APPLY-SELECT] ✅ Clicked points")
            return True
            
        except Exception as e:
            self.logger.error(f"[APPLY-SELECT] Error: {e}")
            return False
    
    async def _apply_slider(self, page, solution) -> bool:
        """Apply slider solution"""
        try:
            end_x = solution.get('end', {}).get('x', 0) if isinstance(solution, dict) else solution
            self.logger.info(f"[APPLY-SLIDER] Sliding to {end_x}px...")
            
            # Find slider button
            slider = await page.query_selector('button#captcha_slide_button, button.secsdk-captcha-drag-icon, div[draggable="true"]')
            if not slider:
                self.logger.error("[APPLY-SLIDER] ❌ No slider button")
                return False
            
            box = await slider.bounding_box()
            if not box:
                return False
            
            start_x = box['x'] + box['width'] / 2
            start_y = box['y'] + box['height'] / 2
            
            # Drag
            await page.mouse.move(start_x, start_y)
            await asyncio.sleep(0.1)
            await page.mouse.down()
            await asyncio.sleep(0.1)
            
            # Smooth drag
            steps = 30
            for i in range(steps + 1):
                progress = i / steps
                current_x = start_x + (end_x * progress)
                await page.mouse.move(current_x, start_y)
                await asyncio.sleep(0.02)
            
            await asyncio.sleep(0.1)
            await page.mouse.up()
            
            self.logger.info("[APPLY-SLIDER] ✅ Drag completed")
            return True
            
        except Exception as e:
            self.logger.error(f"[APPLY-SLIDER] Error: {e}")
            return False


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

async def solve_tiktok_captcha_playwright(page, omocaptcha_client, max_retries: int = 10) -> bool:
    """
    Helper function: Solve TikTok captcha with Playwright + OMOcaptcha
    
    Args:
        page: Playwright page
        omocaptcha_client: OMOcaptchaClient instance
        max_retries: Max retry attempts
        
    Returns:
        True if solved successfully
    """
    solver = TikTokCaptchaSolverPlaywright(omocaptcha_client)
    solution = await solver.solve_captcha(page, max_retries=max_retries)
    return solution is not None
