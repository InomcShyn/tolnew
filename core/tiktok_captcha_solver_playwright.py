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
    
    async def _wait_for_captcha_images(self, page, timeout: int = 10) -> int:
        """
        Wait for captcha images to load
        
        Args:
            page: Playwright page
            timeout: Max wait time in seconds
            
        Returns:
            Number of visible images found
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            all_images = await page.query_selector_all('img[src^="data:image/"]')
            
            # Check if images are actually visible and have content
            visible_images = []
            for img in all_images:
                try:
                    if await img.is_visible():
                        box = await img.bounding_box()
                        if box and box['width'] > 100 and box['height'] > 100:
                            visible_images.append(img)
                except:
                    continue
            
            if len(visible_images) >= 2:
                self.logger.info(f"[WAIT] ✅ Found {len(visible_images)} visible images")
                return len(visible_images)
            
            self.logger.debug(f"[WAIT] Only {len(visible_images)} images, waiting...")
            await asyncio.sleep(0.5)
        
        self.logger.warning(f"[WAIT] ⚠️ Timeout after {timeout}s, found {len(visible_images)} images")
        return len(visible_images)
    
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
        """Detect specific captcha type - CHECK ROTATE FIRST (FIXED)"""
        try:
            # Get page HTML to check for keywords
            html = await page.content()
            
            # Count images for logging
            all_images = await page.query_selector_all('img[src^="data:image/"]')
            image_count = len(all_images)
            
            # Log image details for debugging
            self.logger.info(f"[DETECT] Found {image_count} captcha images")
            for i, img in enumerate(all_images):
                try:
                    box = await img.bounding_box()
                    if box:
                        self.logger.debug(f"[DETECT] Image {i+1}: {box['width']}x{box['height']}px")
                except:
                    pass
            
            # PRIORITY 1: Check for ROTATE elements FIRST (most accurate!)
            # This is the key fix - check rotate BEFORE button
            for selector in self.CAPTCHA_SELECTORS['rotate']:
                rotate = await page.query_selector(selector)
                if rotate and await rotate.is_visible():
                    self.logger.info(f"[DETECT] ✅ Type: ROTATE (element found: {selector})")
                    return "rotate"
            
            # PRIORITY 2: Check keywords for rotate
            rotate_specific_keywords = ['rotate', 'xoay', 'fit the puzzle']
            has_rotate_keyword = any(keyword.lower() in html.lower() for keyword in rotate_specific_keywords)
            
            if has_rotate_keyword:
                self.logger.info("[DETECT] ✅ Type: ROTATE (keyword found)")
                return "rotate"
            
            # PRIORITY 3: Check image count (2+ images = likely rotate)
            if image_count >= 2:
                self.logger.info(f"[DETECT] ✅ Type: ROTATE ({image_count} images found)")
                return "rotate"
            
            # PRIORITY 4: Check BUTTON TYPE for slider
            # Only check button if NOT rotate (to avoid false positives)
            slide_button = await page.query_selector('button#captcha_slide_button')
            if slide_button and await slide_button.is_visible():
                self.logger.info("[DETECT] ✅ Type: SLIDER (found button#captcha_slide_button)")
                return "slider"
            
            # Check for drag icon button (slider)
            drag_button = await page.query_selector('button.secsdk-captcha-drag-icon')
            if drag_button and await drag_button.is_visible():
                # Check if it's really a slider by looking at the button content
                button_html = await drag_button.inner_html()
                if 'arrow' in button_html.lower() or 'svg' in button_html.lower():
                    self.logger.info("[DETECT] ✅ Type: SLIDER (found drag button with arrow)")
                    return "slider"
            
            # PRIORITY 5: Check slider keywords
            slider_specific_keywords = ['slide', 'kéo', 'drag the slider', 'swipe']
            has_slider_keyword = any(keyword.lower() in html.lower() for keyword in slider_specific_keywords)
            
            if has_slider_keyword:
                self.logger.info("[DETECT] ✅ Type: SLIDER (keyword found)")
                return "slider"
            
            # PRIORITY 6: Check for draggable div (fallback)
            draggable = await page.query_selector('div[draggable="true"]')
            if draggable and await draggable.is_visible():
                # Default to slider if only 1 image
                if image_count == 1:
                    self.logger.info(f"[DETECT] ✅ Type: SLIDER (draggable + {image_count} image)")
                    return "slider"
                else:
                    # Should have been caught by image count check above
                    self.logger.warning(f"[DETECT] ⚠️ Type: ROTATE (fallback - draggable + {image_count} images)")
                    return "rotate"
            
            # Final fallback - default to slider
            self.logger.warning("[DETECT] ⚠️ Type: SLIDER (final fallback)")
            return "slider"
            
        except Exception as e:
            self.logger.error(f"[DETECT] Type error: {e}")
            return None
    
    async def capture_captcha_image(self, page, captcha_type: str) -> Optional[Tuple[str, int, int]]:
        """
        Capture captcha image with retry logic for image loading
        
        Returns:
            Tuple (base64_image, width, height) or None
        """
        self.logger.info("[CAPTURE] Starting...")
        
        try:
            # STEP 1: Wait for images to load (CRITICAL FIX)
            if captcha_type == "rotate":
                self.logger.info("[CAPTURE] Waiting for rotate captcha images to load...")
                image_count = await self._wait_for_captcha_images(page, timeout=10)
                
                if image_count < 2:
                    self.logger.error(f"[CAPTURE] ❌ Only {image_count} images found after waiting")
                    # Try to refresh captcha and wait again
                    self.logger.info("[CAPTURE] Attempting to refresh captcha...")
                    await self._refresh_captcha(page)
                    await asyncio.sleep(2)
                    image_count = await self._wait_for_captcha_images(page, timeout=5)
                    
                    if image_count < 2:
                        self.logger.error(f"[CAPTURE] ❌ Still only {image_count} images after refresh")
                        return None
            
            # STEP 2: Find ALL images
            all_images = await page.query_selector_all('img[src^="data:image/"]')
            self.logger.info(f"[CAPTURE] Found {len(all_images)} data:image elements")
            
            # Find image element - PRIORITIZE actual captcha image
            image_element = None
            found_selector = None
            
            # For ROTATE: Need to capture BOTH images (background + foreground)
            # For SLIDER: Need to capture the SINGLE puzzle image
            
            if captcha_type == "rotate" and len(all_images) >= 2:
                # Rotate captcha: Find the container that has both images
                self.logger.info("[CAPTURE] ROTATE type: Looking for container with 2 images...")
                
                # Try specific TikTok captcha container selectors first (PRIORITY)
                priority_selectors = [
                    '.captcha-verify-img-panel',  # TikTok specific
                    'div.cap-flex.cap-w-full',    # TikTok specific
                    '.secsdk-captcha-container',  # TikTok SDK
                ]
                
                for selector in priority_selectors:
                    container = await page.query_selector(selector)
                    if container and await container.is_visible():
                        # Verify container actually contains images
                        images_in_container = await container.query_selector_all('img[src^="data:image/"]')
                        if len(images_in_container) >= 2:
                            box = await container.bounding_box()
                            if box and 200 < box['width'] < 600 and 200 < box['height'] < 600:
                                image_element = container
                                found_selector = f"priority container: {selector}"
                                self.logger.info(f"[CAPTURE] ✅ Using {found_selector}: {box['width']}x{box['height']}px")
                                break
                
                # Fallback to generic container selectors
                if not image_element:
                    for selector in self.CAPTCHA_SELECTORS['container']:
                        container = await page.query_selector(selector)
                        if container and await container.is_visible():
                            box = await container.bounding_box()
                            if box and 200 < box['width'] < 600 and 200 < box['height'] < 600:
                                image_element = container
                                found_selector = f"container: {selector}"
                                self.logger.info(f"[CAPTURE] Using container for rotate: {box['width']}x{box['height']}px")
                                break
            else:
                # Slider or single image: Find the actual puzzle image
                self.logger.info("[CAPTURE] SLIDER type: Looking for puzzle image...")
                for selector in self.CAPTCHA_SELECTORS['image']:
                    element = await page.query_selector(selector)
                    if element and await element.is_visible():
                        box = await element.bounding_box()
                        # Slider puzzle image is usually 200-350px square
                        if box and 150 < box['width'] < 400 and 150 < box['height'] < 400:
                            image_element = element
                            found_selector = selector
                            self.logger.info(f"[CAPTURE] Found puzzle image: {selector} ({box['width']}x{box['height']}px)")
                            break
            
            # Fallback: Try any visible image
            if not image_element and len(all_images) > 0:
                self.logger.warning("[CAPTURE] Using fallback: first visible image")
                for img in all_images:
                    if await img.is_visible():
                        box = await img.bounding_box()
                        if box and box['width'] > 100 and box['height'] > 100:
                            image_element = img
                            found_selector = "fallback: first image"
                            self.logger.info(f"[CAPTURE] Fallback image: {box['width']}x{box['height']}px")
                            break
            
            # Last resort: Try container (AVOID THIS IF POSSIBLE)
            if not image_element:
                self.logger.warning("[CAPTURE] Last resort: trying container...")
                for selector in self.CAPTCHA_SELECTORS['container']:
                    element = await page.query_selector(selector)
                    if element and await element.is_visible():
                        box = await element.bounding_box()
                        if box and box['width'] > 200 and box['height'] > 200:
                            image_element = element
                            found_selector = f"last resort container: {selector}"
                            self.logger.warning(f"[CAPTURE] Using container: {box['width']}x{box['height']}px")
                            break
            
            if not image_element:
                self.logger.error("[CAPTURE] ❌ No image found")
                # Save page screenshot for debug
                screenshot = await page.screenshot()
                await self._save_artifact("no_image_full_page", screenshot, "png")
                return None
            
            self.logger.info(f"[CAPTURE] ✅ Selected: {found_selector}")
            
            # Get dimensions
            box = await image_element.bounding_box()
            if not box:
                self.logger.error("[CAPTURE] ❌ No bounding box")
                return None
            
            width = int(box['width'])
            height = int(box['height'])
            
            self.logger.info(f"[CAPTURE] Dimensions: {width}x{height}px")
            
            # Capture screenshot
            screenshot = await image_element.screenshot()
            image_base64 = base64.b64encode(screenshot).decode('utf-8')
            
            self.logger.info(f"[CAPTURE] ✅ Encoded: {len(image_base64)} bytes")
            
            # Save artifact with type in filename
            await self._save_artifact(f"captcha_{captcha_type}", screenshot, "png")
            
            return (image_base64, width, height)
            
        except Exception as e:
            self.logger.error(f"[CAPTURE] ❌ Error: {e}")
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
        """Apply rotate solution - CORRECT VERSION from core_copy"""
        try:
            # Extract rotate value from solution
            rotate_value = solution if isinstance(solution, (int, float)) else solution.get('rotate', 0)
            
            self.logger.info(f"[APPLY-ROTATE] Rotate value from API: {rotate_value} (0-1 range)")
            
            # Find draggable element
            slider = await page.query_selector('div[draggable="true"]')
            if not slider:
                self.logger.error("[APPLY-ROTATE] ❌ No draggable element")
                return False
            
            box = await slider.bounding_box()
            if not box:
                return False
            
            # Get current transform
            transform_value = await slider.evaluate('el => window.getComputedStyle(el).transform')
            current_translate_x = 0
            
            if transform_value and transform_value != 'none':
                import re
                match = re.search(r'matrix\([^,]+,\s*[^,]+,\s*[^,]+,\s*[^,]+,\s*([^,]+)', transform_value)
                if match:
                    current_translate_x = float(match.group(1))
            
            # Calculate drag distance using CORRECT formula from core_copy
            # METHOD 2: target_translateX = (1 - rotate) * usable_track_width
            track_width = 284  # Typical TikTok track width
            button_width = box['width']
            usable_track_width = track_width - button_width
            
            # CORRECT FORMULA (from core_copy)
            target_translate_x = (1 - rotate_value) * usable_track_width
            
            # Calculate absolute positions
            base_x = box['x']
            current_x = base_x + button_width / 2 + current_translate_x
            target_x = base_x + button_width / 2 + target_translate_x
            drag_distance = target_x - current_x
            
            self.logger.info(f"[APPLY-ROTATE] Track: {track_width}px, Button: {button_width}px")
            self.logger.info(f"[APPLY-ROTATE] Current translateX: {current_translate_x}px")
            self.logger.info(f"[APPLY-ROTATE] Target translateX: {target_translate_x:.2f}px")
            self.logger.info(f"[APPLY-ROTATE] Drag distance: {drag_distance:.2f}px")
            
            # Perform drag with human-like movement
            import random
            
            start_y = box['y'] + box['height'] / 2
            
            # Initial hover
            await page.mouse.move(current_x - 10, start_y)
            await asyncio.sleep(random.uniform(0.1, 0.2))
            await page.mouse.move(current_x, start_y)
            await asyncio.sleep(random.uniform(0.15, 0.25))
            
            # Mouse down
            await page.mouse.down()
            await asyncio.sleep(random.uniform(0.15, 0.25))
            
            # Drag with human-like movement
            steps = random.randint(40, 60)
            self.logger.info(f"[APPLY-ROTATE] Dragging with {steps} steps...")
            
            for i in range(steps + 1):
                progress = i / steps
                
                # Add slight vertical wobble
                wobble_y = random.uniform(-2, 2) if i > 0 and i < steps else 0
                
                # Add slight horizontal variation
                progress_variation = progress + random.uniform(-0.01, 0.01)
                progress_variation = max(0, min(1, progress_variation))
                
                # Calculate position
                move_x = current_x + (drag_distance * progress_variation)
                move_y = start_y + wobble_y
                
                await page.mouse.move(move_x, move_y)
                
                # Variable delay
                if i < steps * 0.2:
                    delay = random.uniform(0.04, 0.06)
                elif i < steps * 0.4:
                    delay = random.uniform(0.03, 0.05)
                elif i > steps * 0.8:
                    delay = random.uniform(0.04, 0.06)
                elif i > steps * 0.6:
                    delay = random.uniform(0.03, 0.05)
                else:
                    delay = random.uniform(0.02, 0.04)
                
                await asyncio.sleep(delay)
            
            # Pause before release
            await asyncio.sleep(random.uniform(0.1, 0.2))
            await page.mouse.up()
            await asyncio.sleep(random.uniform(0.4, 0.6))
            
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
