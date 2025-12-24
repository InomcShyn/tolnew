#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TikTok Captcha Solver - Production Ready API Based
Tự động detect và giải captcha TikTok bằng OMOcaptcha API
Không cần extension, call API trực tiếp
Docs: https://docs.omocaptcha.com/tai-lieu-api/tiktok/

Features:
- Step-by-step debug logging
- Retry with exponential backoff
- Artifact saving on failure
- Rate limiting
- Environment variable configuration
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


class TikTokCaptchaSolver:
    """
    Production-ready TikTok Captcha Solver với debug chi tiết
    
    Supported types:
    - Rotate (xoay ảnh)
    - Select Object (chọn 2 điểm)
    - 3D Select Object (chọn 2 điểm 3D)
    - Slider (kéo slider)
    
    Features:
    - Step-by-step debug logging
    - Retry with exponential backoff
    - Artifact saving on failure
    - Rate limiting
    """
    
    # TikTok captcha selectors (Updated based on actual HTML)
    CAPTCHA_SELECTORS = {
        'container': [
            # TikTok specific - EXACT match from HTML
            '.TUXModal.captcha-verify-container',
            'div.captcha-verify-container',
            '#captcha-verify-container-main-page',
            # Generic fallbacks
            '[class*="captcha"]',
            '[id*="captcha"]',
            '[data-testid*="captcha"]',
            '.secsdk-captcha-container',
            '#secsdk-captcha-container',
            'iframe[id*="captcha"]',
            'div[class*="verify"]',
            'div[id*="verify"]'
        ],
        'image': [
            # TikTok specific - Images with base64 data
            'img[alt="Captcha"]',
            'img[src^="data:image/webp;base64"]',
            'img[src^="data:image/"]',
            # Inside captcha container
            '.captcha-verify-container img',
            '.TUXModal img',
            '#captcha-verify-container-main-page img',
            # Generic
            'img[class*="captcha"]',
            'canvas[class*="captcha"]',
            'img[src*="captcha"]',
            'img[src*="verify"]',
            '[class*="captcha-verify-image"]',
            '[class*="captcha_verify_img"]',
            '[class*="captcha-image"]',
            '[class*="puzzle"]',
            'img[alt*="captcha"]',
            'img[alt*="verify"]',
            # Fallback - any visible image in captcha container
            'img',
            'canvas'
        ],
        'slider': [
            # TikTok specific - EXACT match from HTML
            'button#captcha_slide_button',
            'button.secsdk-captcha-drag-icon',
            '[class*="secsdk-captcha-drag"]',
            # Generic
            'button[class*="slider"]',
            'div[class*="slider"]',
            '[class*="captcha-slider"]',
            '.captcha_slider_button',
            '[class*="slider-button"]',
            '[id*="slider"]',
            '[role="button"]'
        ],
        'rotate': [
            '[class*="captcha-rotate"]',
            '[class*="rotate-captcha"]',
            '[class*="rotate"]'
        ],
        'select': [
            '[class*="captcha-select"]',
            '[class*="select-captcha"]',
            '[class*="select"]'
        ]
    }
    
    def __init__(self, omocaptcha_client, debug_level: str = "DEBUG", 
                 artifacts_dir: str = "logs/captcha_artifacts",
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
        
        # Configure logging level
        if debug_level == "DEBUG":
            self.logger.setLevel(logging.DEBUG)
        elif debug_level == "INFO":
            self.logger.setLevel(logging.INFO)
        elif debug_level == "WARN":
            self.logger.setLevel(logging.WARNING)
        elif debug_level == "ERROR":
            self.logger.setLevel(logging.ERROR)
        
        self.logger.info(f"[CAPTCHA] Initialized solver with debug_level={debug_level}")
        self.logger.info(f"[CAPTCHA] Artifacts directory: {self.artifacts_dir}")
        self.logger.info(f"[CAPTCHA] Rate limit delay: {rate_limit_delay}s")
    
    async def _enforce_rate_limit(self):
        """Enforce rate limiting between API calls"""
        elapsed = time.time() - self.last_api_call
        if elapsed < self.rate_limit_delay:
            wait_time = self.rate_limit_delay - elapsed
            self.logger.debug(f"[RATE_LIMIT] Waiting {wait_time:.2f}s before next API call")
            await asyncio.sleep(wait_time)
        self.last_api_call = time.time()
    
    async def _save_artifact(self, artifact_type: str, data: Any, extension: str = "txt"):
        """Save debug artifact to file"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            filename = f"{artifact_type}_{timestamp}.{extension}"
            filepath = self.artifacts_dir / filename
            
            if extension == "json":
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            elif extension == "png":
                # data should be bytes
                with open(filepath, 'wb') as f:
                    f.write(data)
            else:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(str(data))
            
            self.logger.debug(f"[ARTIFACT] Saved {artifact_type} to {filepath}")
            return str(filepath)
        except Exception as e:
            self.logger.error(f"[ARTIFACT] Failed to save {artifact_type}: {e}")
            return None
    
    async def detect_captcha(self, page) -> Optional[str]:
        """
        Detect xem có captcha không và loại gì
        
        Args:
            page: Playwright page object
            
        Returns:
            Loại captcha (rotate/select/3d/slider) hoặc None
        """
        self.logger.debug("[STEP 1] detect_captcha START")
        
        try:
            # Check for captcha container
            for idx, selector in enumerate(self.CAPTCHA_SELECTORS['container']):
                self.logger.debug(f"[STEP 1.{idx+1}] Checking selector: {selector}")
                
                element = await page.query_selector(selector)
                if element:
                    # Check if visible
                    is_visible = await element.is_visible()
                    self.logger.debug(f"[STEP 1.{idx+1}] Element found, visible={is_visible}")
                    
                    if is_visible:
                        self.logger.info(f"[STEP 1] ✅ Found captcha container: {selector}")
                        
                        # Detect type
                        captcha_type = await self._detect_captcha_type(page, element)
                        
                        if captcha_type:
                            self.logger.info(f"[STEP 1] ✅ Detected captcha type: {captcha_type}")
                        else:
                            self.logger.warning(f"[STEP 1] ⚠️ Found container but could not detect type")
                        
                        return captcha_type
            
            self.logger.debug("[STEP 1] ❌ No captcha detected")
            return None
            
        except Exception as e:
            self.logger.error(f"[STEP 1] ❌ Error detecting captcha: {e}")
            self.logger.debug(traceback.format_exc())
            return None
    
    async def _detect_captcha_type(self, page, container_element) -> Optional[str]:
        """Detect loại captcha cụ thể"""
        self.logger.debug("[STEP 1.A] _detect_captcha_type START")
        
        try:
            # Check for slider
            self.logger.debug("[STEP 1.A.1] Checking for SLIDER...")
            for idx, selector in enumerate(self.CAPTCHA_SELECTORS['slider']):
                slider = await page.query_selector(selector)
                if slider:
                    is_visible = await slider.is_visible()
                    self.logger.debug(f"[STEP 1.A.1.{idx+1}] Slider element: {selector}, visible={is_visible}")
                    if is_visible:
                        self.logger.info("[STEP 1.A] ✅ Detected: SLIDER")
                        return "slider"
            
            # Check for rotate
            self.logger.debug("[STEP 1.A.2] Checking for ROTATE...")
            for idx, selector in enumerate(self.CAPTCHA_SELECTORS['rotate']):
                rotate = await page.query_selector(selector)
                if rotate:
                    is_visible = await rotate.is_visible()
                    self.logger.debug(f"[STEP 1.A.2.{idx+1}] Rotate element: {selector}, visible={is_visible}")
                    if is_visible:
                        self.logger.info("[STEP 1.A] ✅ Detected: ROTATE")
                        return "rotate"
            
            # Check for select
            self.logger.debug("[STEP 1.A.3] Checking for SELECT...")
            for idx, selector in enumerate(self.CAPTCHA_SELECTORS['select']):
                select = await page.query_selector(selector)
                if select:
                    is_visible = await select.is_visible()
                    self.logger.debug(f"[STEP 1.A.3.{idx+1}] Select element: {selector}, visible={is_visible}")
                    if is_visible:
                        # Check if 3D
                        html = await page.content()
                        if '3d' in html.lower() or '3D' in html:
                            self.logger.info("[STEP 1.A] ✅ Detected: 3D SELECT")
                            return "3d"
                        else:
                            self.logger.info("[STEP 1.A] ✅ Detected: SELECT")
                            return "select"
            
            # Default: try to detect from image
            self.logger.debug("[STEP 1.A.4] Checking for IMAGE (fallback)...")
            for idx, selector in enumerate(self.CAPTCHA_SELECTORS['image']):
                image = await page.query_selector(selector)
                if image:
                    is_visible = await image.is_visible()
                    self.logger.debug(f"[STEP 1.A.4.{idx+1}] Image element: {selector}, visible={is_visible}")
                    if is_visible:
                        # Analyze image to guess type
                        # Default to slider (most common)
                        self.logger.info("[STEP 1.A] ⚠️ Detected: SLIDER (default fallback)")
                        return "slider"
            
            self.logger.warning("[STEP 1.A] ❌ Could not detect captcha type")
            return None
            
        except Exception as e:
            self.logger.error(f"[STEP 1.A] ❌ Error detecting type: {e}")
            self.logger.debug(traceback.format_exc())
            return None
    
    async def capture_captcha_image(self, page, captcha_type: str) -> Optional[Tuple[str, int, int]]:
        """
        Capture ảnh captcha
        
        Returns:
            Tuple (base64_image, width, height) hoặc None
        """
        self.logger.debug("[STEP 2] capture_captcha_image START")
        
        try:
            # Find captcha image element
            image_element = None
            found_selector = None
            
            # Try standard selectors first
            for idx, selector in enumerate(self.CAPTCHA_SELECTORS['image']):
                self.logger.debug(f"[STEP 2.{idx+1}] Trying selector: {selector}")
                element = await page.query_selector(selector)
                if element:
                    is_visible = await element.is_visible()
                    self.logger.debug(f"[STEP 2.{idx+1}] Element found, visible={is_visible}")
                    if is_visible:
                        image_element = element
                        found_selector = selector
                        break
            
            # If not found, try iframe
            if not image_element:
                self.logger.debug("[STEP 2.A] Trying to find captcha in iframe...")
                iframes = await page.query_selector_all('iframe')
                for iframe_idx, iframe in enumerate(iframes):
                    try:
                        frame = await iframe.content_frame()
                        if frame:
                            self.logger.debug(f"[STEP 2.A.{iframe_idx+1}] Checking iframe...")
                            for selector in self.CAPTCHA_SELECTORS['image']:
                                element = await frame.query_selector(selector)
                                if element:
                                    is_visible = await element.is_visible()
                                    if is_visible:
                                        image_element = element
                                        found_selector = f"iframe[{iframe_idx}] {selector}"
                                        self.logger.info(f"[STEP 2.A] Found in iframe: {found_selector}")
                                        break
                            if image_element:
                                break
                    except:
                        pass
            
            # If still not found, try capturing container
            if not image_element:
                self.logger.debug("[STEP 2.B] Trying to capture container instead...")
                for selector in self.CAPTCHA_SELECTORS['container']:
                    element = await page.query_selector(selector)
                    if element:
                        is_visible = await element.is_visible()
                        if is_visible:
                            image_element = element
                            found_selector = f"container: {selector}"
                            self.logger.info(f"[STEP 2.B] Using container: {found_selector}")
                            break
            
            if not image_element:
                self.logger.error("[STEP 2] ❌ Could not find captcha image")
                # Save page screenshot for debugging
                try:
                    page_screenshot = await page.screenshot()
                    await self._save_artifact("page_no_image", page_screenshot, "png")
                    
                    # Also save page HTML
                    html = await page.content()
                    await self._save_artifact("page_no_image_html", html, "html")
                except:
                    pass
                return None
            
            self.logger.info(f"[STEP 2] ✅ Found image element: {found_selector}")
            
            # For TikTok slider captcha, there are 2 images:
            # 1. Main puzzle image (larger, circular)
            # 2. Slider piece image (smaller, circular)
            # We need to capture the MAIN puzzle image (first one)
            
            # Check if this is inside captcha container
            try:
                # Try to get the first image (main puzzle)
                container = await page.query_selector('.captcha-verify-container, .TUXModal')
                if container:
                    images = await container.query_selector_all('img[alt="Captcha"]')
                    if len(images) >= 1:
                        # Use first image (main puzzle)
                        image_element = images[0]
                        self.logger.info(f"[STEP 2] Using first captcha image (main puzzle)")
            except:
                pass
            
            # Get dimensions
            box = await image_element.bounding_box()
            if not box:
                self.logger.error("[STEP 2] ❌ Could not get image dimensions")
                return None
            
            width = int(box['width'])
            height = int(box['height'])
            self.logger.debug(f"[STEP 2] Dimensions: {width}x{height}, position: ({box['x']}, {box['y']})")
            
            # Capture screenshot
            screenshot = await image_element.screenshot()
            image_base64 = base64.b64encode(screenshot).decode('utf-8')
            
            self.logger.info(f"[STEP 2] ✅ Captured: {len(image_base64)} bytes (base64), {width}x{height}px")
            
            # Save artifact for debugging
            await self._save_artifact("captcha_image", screenshot, "png")
            
            return (image_base64, width, height)
            
        except Exception as e:
            self.logger.error(f"[STEP 2] ❌ Error capturing image: {e}")
            self.logger.debug(traceback.format_exc())
            
            # Save page screenshot on error
            try:
                page_screenshot = await page.screenshot()
                await self._save_artifact("page_capture_error", page_screenshot, "png")
            except:
                pass
            
            return None
    
    async def solve_captcha(self, page, captcha_type: str, max_retries: int = 3, 
                           backoff_factor: float = 2.0) -> Optional[Dict]:
        """
        Giải captcha và apply solution với retry và exponential backoff
        
        Args:
            page: Playwright page
            captcha_type: Loại captcha
            max_retries: Số lần retry nếu fail
            backoff_factor: Hệ số tăng thời gian chờ giữa các retry
            
        Returns:
            Solution dict hoặc None
        """
        self.logger.info(f"[SOLVE] Starting captcha solve: type={captcha_type}, max_retries={max_retries}")
        
        for attempt in range(max_retries):
            try:
                self.logger.info(f"[SOLVE] ═══ Attempt {attempt + 1}/{max_retries} ═══")
                
                # Exponential backoff delay (except first attempt)
                if attempt > 0:
                    delay = backoff_factor ** (attempt - 1)
                    self.logger.info(f"[SOLVE] Waiting {delay:.1f}s before retry (exponential backoff)...")
                    await asyncio.sleep(delay)
                
                # STEP 2: Capture image
                capture_result = await self.capture_captcha_image(page, captcha_type)
                if not capture_result:
                    self.logger.error(f"[SOLVE] ❌ Attempt {attempt + 1}: Failed to capture image")
                    continue
                
                image_base64, width, height = capture_result
                
                # STEP 3: Prepare API request
                self.logger.debug("[STEP 3] prepare_request START")
                self.logger.info(f"[STEP 3] Captcha type: {captcha_type}")
                self.logger.info(f"[STEP 3] Image size: {len(image_base64)} bytes (base64)")
                self.logger.info(f"[STEP 3] Dimensions: {width}x{height}")
                
                # Mask API key for logging
                masked_key = f"{self.client.api_key[:10]}...{self.client.api_key[-10:]}" if len(self.client.api_key) > 20 else "***"
                self.logger.debug(f"[STEP 3] API Key: {masked_key}")
                self.logger.debug(f"[STEP 3] API URL: {self.client.base_url}")
                
                # Enforce rate limiting
                await self._enforce_rate_limit()
                
                # STEP 4: Call API to solve
                self.logger.debug("[STEP 4] api_call START")
                self.logger.info(f"[STEP 4] Calling OMOcaptcha API for {captcha_type}...")
                
                api_start_time = time.time()
                solution = self.client.solve_captcha_auto(
                    captcha_type,
                    image_base64,
                    width=width,
                    height=height
                )
                api_duration = time.time() - api_start_time
                
                self.logger.info(f"[STEP 4] API call completed in {api_duration:.2f}s")
                
                if not solution:
                    self.logger.error(f"[STEP 4] ❌ API returned no solution")
                    
                    # Save artifacts on API failure
                    await self._save_artifact("api_failure_request", {
                        "attempt": attempt + 1,
                        "captcha_type": captcha_type,
                        "width": width,
                        "height": height,
                        "image_size": len(image_base64)
                    }, "json")
                    
                    continue
                
                self.logger.info(f"[STEP 4] ✅ Got solution: {solution}")
                
                # Save solution artifact
                await self._save_artifact("solution", {
                    "attempt": attempt + 1,
                    "captcha_type": captcha_type,
                    "solution": solution,
                    "api_duration": api_duration
                }, "json")
                
                # STEP 5: Apply solution
                self.logger.debug("[STEP 5] apply_solution START")
                success = await self._apply_solution(page, captcha_type, solution)
                
                if success:
                    self.logger.info("[STEP 5] ✅ Solution applied successfully")
                    
                    # STEP 6: Verify solution
                    self.logger.debug("[STEP 6] verify_solution START")
                    self.logger.info("[STEP 6] Waiting 2s for verification...")
                    await asyncio.sleep(2)
                    
                    # Check if captcha disappeared
                    self.logger.info("[STEP 6] Checking if captcha is still present...")
                    captcha_still_there = await self.detect_captcha(page)
                    
                    if not captcha_still_there:
                        self.logger.info("[STEP 6] ✅ Captcha disappeared - SOLVED!")
                        self.logger.info(f"[SOLVE] ✅✅✅ SUCCESS after {attempt + 1} attempt(s) ✅✅✅")
                        
                        # Save success artifact
                        await self._save_artifact("success", {
                            "attempts": attempt + 1,
                            "captcha_type": captcha_type,
                            "solution": solution,
                            "total_duration": api_duration
                        }, "json")
                        
                        return solution
                    else:
                        self.logger.warning("[STEP 6] ⚠️ Captcha still present after applying solution")
                        
                        # Save page screenshot for analysis
                        try:
                            page_screenshot = await page.screenshot()
                            await self._save_artifact("captcha_still_present", page_screenshot, "png")
                        except:
                            pass
                        
                        self.logger.warning(f"[SOLVE] Attempt {attempt + 1} failed, will retry...")
                else:
                    self.logger.error("[STEP 5] ❌ Failed to apply solution")
                
            except Exception as e:
                self.logger.error(f"[SOLVE] ❌ Exception in attempt {attempt + 1}: {e}")
                self.logger.debug(traceback.format_exc())
                
                # Save error artifact
                await self._save_artifact("error", {
                    "attempt": attempt + 1,
                    "error": str(e),
                    "traceback": traceback.format_exc()
                }, "json")
                
                # Save page screenshot on error
                try:
                    page_screenshot = await page.screenshot()
                    await self._save_artifact("error_screenshot", page_screenshot, "png")
                except:
                    pass
        
        self.logger.error(f"[SOLVE] ❌❌❌ FAILED after {max_retries} attempts ❌❌❌")
        
        # Save final failure artifact
        await self._save_artifact("final_failure", {
            "captcha_type": captcha_type,
            "max_retries": max_retries,
            "message": "All retry attempts exhausted"
        }, "json")
        
        return None
    
    async def _apply_solution(self, page, captcha_type: str, solution) -> bool:
        """Apply solution vào captcha với debug chi tiết"""
        self.logger.info(f"[APPLY] Applying solution for {captcha_type}")
        actions_performed = []
        
        try:
            if captcha_type == "rotate":
                # Rotate image
                rotate_degree = solution
                self.logger.info(f"[APPLY] Rotating {rotate_degree}°...")
                actions_performed.append(f"rotate: {rotate_degree}°")
                
                # Find rotate control
                # TikTok usually has a slider or drag control for rotation
                slider = await page.query_selector('[class*="captcha-slider"]')
                if slider:
                    self.logger.debug(f"[APPLY] Found slider control")
                    
                    # Calculate slider position based on rotation
                    # Assuming 360° = full slider width
                    box = await slider.bounding_box()
                    if box:
                        slider_width = box['width']
                        target_x = (rotate_degree / 360) * slider_width
                        
                        self.logger.debug(f"[APPLY] Slider width: {slider_width}px")
                        self.logger.debug(f"[APPLY] Target X: {target_x}px")
                        
                        # Drag slider
                        await slider.hover()
                        actions_performed.append("hover on slider")
                        
                        await page.mouse.down()
                        actions_performed.append("mouse down")
                        
                        await page.mouse.move(box['x'] + target_x, box['y'])
                        actions_performed.append(f"move to ({box['x'] + target_x}, {box['y']})")
                        
                        await page.mouse.up()
                        actions_performed.append("mouse up")
                        
                        self.logger.info(f"[APPLY] ✅ Rotation applied: {actions_performed}")
                        return True
                    else:
                        self.logger.error("[APPLY] ❌ Could not get slider bounding box")
                else:
                    self.logger.error("[APPLY] ❌ Could not find slider control")
                
                return False
            
            elif captcha_type in ["select", "3d"]:
                # Click on two points
                pointA, pointB = solution
                self.logger.info(f"[APPLY] Clicking points: A({pointA['x']}, {pointA['y']}), B({pointB['x']}, {pointB['y']})")
                
                # Find captcha image to get offset
                image_element = None
                found_selector = None
                for selector in self.CAPTCHA_SELECTORS['image']:
                    element = await page.query_selector(selector)
                    if element:
                        is_visible = await element.is_visible()
                        if is_visible:
                            image_element = element
                            found_selector = selector
                            break
                
                if not image_element:
                    self.logger.error("[APPLY] ❌ Could not find image element")
                    return False
                
                self.logger.debug(f"[APPLY] Found image element: {found_selector}")
                
                # Get image position
                box = await image_element.bounding_box()
                if not box:
                    self.logger.error("[APPLY] ❌ Could not get image bounding box")
                    return False
                
                self.logger.debug(f"[APPLY] Image position: ({box['x']}, {box['y']}), size: {box['width']}x{box['height']}")
                
                # Calculate absolute coordinates
                abs_x_a = box['x'] + pointA['x']
                abs_y_a = box['y'] + pointA['y']
                abs_x_b = box['x'] + pointB['x']
                abs_y_b = box['y'] + pointB['y']
                
                self.logger.debug(f"[APPLY] Absolute Point A: ({abs_x_a}, {abs_y_a})")
                self.logger.debug(f"[APPLY] Absolute Point B: ({abs_x_b}, {abs_y_b})")
                
                # Click point A
                await page.mouse.click(abs_x_a, abs_y_a)
                actions_performed.append(f"click A at ({abs_x_a}, {abs_y_a})")
                self.logger.info(f"[APPLY] Clicked point A")
                
                await asyncio.sleep(0.5)
                
                # Click point B
                await page.mouse.click(abs_x_b, abs_y_b)
                actions_performed.append(f"click B at ({abs_x_b}, {abs_y_b})")
                self.logger.info(f"[APPLY] Clicked point B")
                
                self.logger.info(f"[APPLY] ✅ Points clicked: {actions_performed}")
                return True
            
            elif captcha_type in ["slider", "slider_phone"]:
                # Slide to position
                end_x = solution['x']
                self.logger.info(f"[APPLY] Sliding to {end_x}px...")
                
                # Find slider button - TikTok specific
                slider_button = None
                found_selector = None
                
                # Try TikTok specific selectors first
                for selector in self.CAPTCHA_SELECTORS['slider']:
                    element = await page.query_selector(selector)
                    if element:
                        is_visible = await element.is_visible()
                        if is_visible:
                            slider_button = element
                            found_selector = selector
                            break
                
                if not slider_button:
                    self.logger.error("[APPLY] ❌ Could not find slider button")
                    return False
                
                self.logger.debug(f"[APPLY] Found slider button: {found_selector}")
                
                # Get slider position
                box = await slider_button.bounding_box()
                if not box:
                    self.logger.error("[APPLY] ❌ Could not get slider bounding box")
                    return False
                
                # For TikTok slider:
                # - Button starts at left (translateX(0px))
                # - Need to drag to the right by end_x pixels
                # - Button is inside a draggable div
                
                start_x = box['x'] + box['width'] / 2
                start_y = box['y'] + box['height'] / 2
                target_x = start_x + end_x
                
                self.logger.debug(f"[APPLY] Slider start: ({start_x:.1f}, {start_y:.1f})")
                self.logger.debug(f"[APPLY] Slider target: ({target_x:.1f}, {start_y:.1f})")
                self.logger.debug(f"[APPLY] Distance: {end_x}px")
                
                # Move to slider button
                await page.mouse.move(start_x, start_y)
                actions_performed.append(f"move to start ({start_x:.1f}, {start_y:.1f})")
                await asyncio.sleep(0.1)
                
                # Press down
                await page.mouse.down()
                actions_performed.append("mouse down")
                await asyncio.sleep(0.1)
                
                # Drag with human-like motion (slower, with slight variations)
                steps = 30  # More steps for smoother motion
                self.logger.debug(f"[APPLY] Sliding in {steps} steps...")
                
                import random
                for i in range(steps + 1):
                    progress = i / steps
                    # Add slight random variation for human-like movement
                    variation = random.uniform(-1, 1) if i > 0 and i < steps else 0
                    current_x = start_x + (end_x * progress) + variation
                    current_y = start_y + variation * 0.5
                    await page.mouse.move(current_x, current_y)
                    await asyncio.sleep(0.02)  # Slower movement
                
                actions_performed.append(f"slide to ({target_x:.1f}, {start_y:.1f}) in {steps} steps")
                
                # Release
                await asyncio.sleep(0.1)
                await page.mouse.up()
                actions_performed.append("mouse up")
                
                self.logger.info(f"[APPLY] ✅ Slider moved: {actions_performed}")
                
                # Wait a bit for verification
                await asyncio.sleep(1)
                
                return True
            
            else:
                self.logger.error(f"[APPLY] ❌ Unknown captcha type: {captcha_type}")
                return False
            
        except Exception as e:
            self.logger.error(f"[APPLY] ❌ Error applying solution: {e}")
            self.logger.debug(f"[APPLY] Actions performed before error: {actions_performed}")
            self.logger.debug(traceback.format_exc())
            return False
    
    async def wait_and_solve_captcha(self, page, timeout: int = 30, check_interval: float = 1.0) -> bool:
        """
        Chờ captcha xuất hiện và tự động giải
        
        Args:
            page: Playwright page
            timeout: Timeout chờ captcha (seconds)
            check_interval: Khoảng thời gian giữa các lần check (seconds)
            
        Returns:
            True nếu giải thành công hoặc không có captcha
        """
        self.logger.info(f"[WAIT_SOLVE] Starting captcha monitor (timeout: {timeout}s, interval: {check_interval}s)")
        
        try:
            start_time = time.time()
            check_count = 0
            
            while True:
                elapsed = time.time() - start_time
                if elapsed > timeout:
                    self.logger.info(f"[WAIT_SOLVE] ✅ No captcha detected within {timeout}s timeout")
                    return True
                
                check_count += 1
                self.logger.debug(f"[WAIT_SOLVE] Check #{check_count} (elapsed: {elapsed:.1f}s)")
                
                # Check for captcha
                captcha_type = await self.detect_captcha(page)
                
                if captcha_type:
                    self.logger.info(f"[WAIT_SOLVE] 🎯 Detected {captcha_type} captcha after {elapsed:.1f}s, solving...")
                    
                    solution = await self.solve_captcha(page, captcha_type)
                    
                    if solution:
                        self.logger.info("[WAIT_SOLVE] ✅✅✅ Captcha solved successfully! ✅✅✅")
                        return True
                    else:
                        self.logger.error("[WAIT_SOLVE] ❌❌❌ Failed to solve captcha ❌❌❌")
                        return False
                
                # Wait before checking again
                await asyncio.sleep(check_interval)
            
        except Exception as e:
            self.logger.error(f"[WAIT_SOLVE] ❌ Error in wait_and_solve: {e}")
            self.logger.debug(traceback.format_exc())
            return False
    
    async def auto_solve_on_page_load(self, page, max_wait: int = 10) -> bool:
        """
        Tự động giải captcha ngay khi page load (dùng cho lifecycle integration)
        
        Args:
            page: Playwright page
            max_wait: Thời gian tối đa chờ captcha xuất hiện (seconds)
            
        Returns:
            True nếu không có captcha hoặc giải thành công
        """
        self.logger.info("[AUTO_SOLVE] Page loaded, checking for captcha...")
        
        try:
            # Wait a bit for page to fully render
            await asyncio.sleep(2)
            
            # Check for captcha
            captcha_type = await self.detect_captcha(page)
            
            if not captcha_type:
                self.logger.info("[AUTO_SOLVE] ✅ No captcha detected on page load")
                return True
            
            self.logger.info(f"[AUTO_SOLVE] 🎯 Captcha detected: {captcha_type}")
            
            # Solve captcha
            solution = await self.solve_captcha(page, captcha_type)
            
            if solution:
                self.logger.info("[AUTO_SOLVE] ✅ Captcha solved on page load")
                return True
            else:
                self.logger.error("[AUTO_SOLVE] ❌ Failed to solve captcha on page load")
                return False
                
        except Exception as e:
            self.logger.error(f"[AUTO_SOLVE] ❌ Error: {e}")
            self.logger.debug(traceback.format_exc())
            return False
