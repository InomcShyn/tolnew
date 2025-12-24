#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TikTok Captcha Solver V2 - HTML-based
Sử dụng HTML parser để trích xuất và giải captcha
"""

import asyncio
import logging
from typing import Optional, Dict, Tuple
from pathlib import Path
from datetime import datetime

from core.tiktok_captcha_html_parser import solve_captcha_from_html
from core.omocaptcha_client import OMOcaptchaClient

logger = logging.getLogger(__name__)


class TikTokCaptchaSolverV2:
    """
    TikTok Captcha Solver V2 - Dựa trên HTML parsing
    
    Cải tiến:
    - Trích xuất captcha trực tiếp từ HTML
    - Tự động phát hiện loại captcha
    - Tạo request body đúng format cho từng loại
    """
    
    def __init__(self, omocaptcha_client: OMOcaptchaClient, debug_level: str = "INFO",
                 artifacts_dir: str = "logs/captcha_artifacts_v2",
                 save_samples: bool = False,
                 enable_manual_test: bool = False):
        """
        Args:
            omocaptcha_client: OMOcaptcha client instance
            debug_level: Logging level
            artifacts_dir: Directory to save artifacts
            save_samples: Save captcha samples for analysis
            enable_manual_test: Enable manual testing dialog
        """
        self.client = omocaptcha_client
        self.logger = logger
        self.debug_level = debug_level
        self.artifacts_dir = Path(artifacts_dir)
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)
        
        # Sample collection
        self.save_samples = save_samples
        self.enable_manual_test = enable_manual_test
        self.samples_dir = Path("captcha_samples")
        self.samples_index_file = self.samples_dir / "samples_index.json"
        self.last_calculated_coords = None  # Store last calculated coordinates
        
        if self.save_samples:
            self.samples_dir.mkdir(exist_ok=True)
            self.logger.info(f"[CAPTCHA-V2] Sample collection ENABLED → {self.samples_dir}")
        
        self.logger.info(f"[CAPTCHA-V2] Initialized with debug_level={debug_level}")
    
    async def detect_captcha(self, page) -> bool:
        """
        Detect xem có captcha không
        
        Args:
            page: Playwright page
            
        Returns:
            True nếu có captcha
        """
        try:
            # Check for captcha container
            selectors = [
                '.TUXModal.captcha-verify-container',
                'div.captcha-verify-container',
                '#captcha-verify-container-main-page',
                '[class*="captcha"]'
            ]
            
            for selector in selectors:
                element = await page.query_selector(selector)
                if element:
                    is_visible = await element.is_visible()
                    if is_visible:
                        self.logger.info(f"[CAPTCHA-V2] ✅ Captcha detected: {selector}")
                        return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"[CAPTCHA-V2] Error detecting captcha: {e}")
            return False
    
    async def _refresh_captcha(self, page) -> bool:
        """Refresh captcha to get a new one"""
        try:
            self.logger.info("[CAPTCHA-V2] 🔄 Refreshing captcha...")
            
            # IMPORTANT: Check slider position BEFORE refresh
            # bounding_box() already includes transform, so we just need box['x']
            box_before = None
            try:
                slider_before = await page.query_selector('div[draggable="true"]')
                if slider_before:
                    box_before = await slider_before.bounding_box()
                    if box_before:
                        center_before = box_before['x'] + box_before['width']/2
                        self.logger.info(f"[CAPTCHA-V2] 📊 Slider BEFORE refresh: x={box_before['x']}, center={center_before}")
            except Exception as e:
                self.logger.debug(f"[CAPTCHA-V2] Could not check slider before refresh: {e}")
            
            # Find refresh button (including SVG icons)
            refresh_selectors = [
                'svg[fill="currentColor"]',  # SVG refresh icon
                'button:has(svg)',  # Button containing SVG
                'div:has(svg[viewBox="0 0 72 72"])',  # Div with SVG
                'button[class*="refresh"]',
                'div[class*="refresh"]',
                'span[class*="refresh"]',
                '.secsdk-captcha-refresh',
                'button[aria-label*="refresh"]',
                'button[aria-label*="Refresh"]',
                # Try clicking near captcha image
                'div.captcha-verify-img-panel ~ div',
                'div[class*="captcha"] button',
            ]
            
            for selector in refresh_selectors:
                refresh_btn = await page.query_selector(selector)
                if refresh_btn:
                    self.logger.info(f"[CAPTCHA-V2] Found refresh button: {selector}")
                    try:
                        # Try to click with force (bypass overlay)
                        await refresh_btn.click(force=True, timeout=5000)
                        await asyncio.sleep(2)  # Wait for new captcha to load
                        self.logger.info("[CAPTCHA-V2] ✅ Captcha refreshed")
                        
                        # IMPORTANT: Check slider position AFTER refresh
                        # bounding_box() already includes transform, so we just need box['x']
                        try:
                            await asyncio.sleep(0.5)  # Extra wait for DOM update
                            slider_after = await page.query_selector('div[draggable="true"]')
                            if slider_after:
                                box_after = await slider_after.bounding_box()
                                if box_after:
                                    center_after = box_after['x'] + box_after['width']/2
                                    self.logger.info(f"[CAPTCHA-V2] 📊 Slider AFTER refresh: x={box_after['x']}, center={center_after}")
                                    
                                    # Check if slider was reset (compare actual x positions)
                                    if box_before:
                                        center_before = box_before['x'] + box_before['width']/2
                                        diff = abs(center_after - center_before)
                                        if diff < 5:
                                            self.logger.warning(f"[CAPTCHA-V2] ⚠️ WARNING: Slider did NOT reset! center before={center_before}, after={center_after}, diff={diff}px")
                                        else:
                                            self.logger.info(f"[CAPTCHA-V2] ✅ Slider was reset! center changed from {center_before} to {center_after} (diff={diff}px)")
                        except Exception as e:
                            self.logger.debug(f"[CAPTCHA-V2] Could not check slider after refresh: {e}")
                        
                        return True
                    except Exception as e:
                        self.logger.warning(f"[CAPTCHA-V2] ⚠️ Failed to click {selector}: {e}")
                        # Try next selector
                        continue
            
            self.logger.warning("[CAPTCHA-V2] ⚠️ Refresh button not found")
            return False
            
        except Exception as e:
            self.logger.error(f"[CAPTCHA-V2] ❌ Failed to refresh captcha: {e}")
            return False
    
    async def _save_sample(self, page, request_body: Dict, solution: Dict, attempt: int, 
                          calculated_coords: Optional[Dict] = None) -> Optional[Dict]:
        """Save captcha sample for analysis"""
        try:
            import json
            import base64
            
            # Load existing samples
            if self.samples_index_file.exists():
                with open(self.samples_index_file, 'r', encoding='utf-8') as f:
                    samples_data = json.load(f)
            else:
                samples_data = {"samples": []}
            
            # Create sample
            sample_id = len(samples_data['samples']) + 1
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            sample = {
                "id": sample_id,
                "timestamp": timestamp,
                "attempt": attempt,
                "rotate_value": solution.get('solution', {}).get('rotate'),
                "task_type": request_body['task']['type'],
                "image_count": len(request_body['task'].get('imageBase64s', [])),
                "track_width": 348,
                "button_width": 64,
                "track_start_x": 786,
                "manual_test_result": None,
                "manual_translateX": None,
                "notes": "",
                # Calculated coordinates from auto solver
                "auto_calculated": calculated_coords or {},
                # Actual result after auto drag
                "auto_actual_result": calculated_coords.get('actual_result', {}) if calculated_coords else {}
            }
            
            # Create sample folder
            sample_folder = self.samples_dir / f"sample_{sample_id:03d}_{timestamp}"
            sample_folder.mkdir(exist_ok=True)
            
            # Save images
            # NOTE: TikTok sends images in reverse order: [outer, inner]
            # We want: image_1 = inner (rotatable), image_2 = outer (frame)
            # So we need to reverse the order when saving
            images = request_body['task'].get('imageBase64s', [])
            
            # Reverse order: save outer as image_2, inner as image_1
            for i, img_base64 in enumerate(reversed(images), 1):
                img_file = sample_folder / f"image_{i}.webp"
                img_data = base64.b64decode(img_base64)
                with open(img_file, 'wb') as f:
                    f.write(img_data)
            
            # Save request body
            request_file = sample_folder / "request_body.json"
            with open(request_file, 'w', encoding='utf-8') as f:
                json.dump(request_body, f, indent=2)
            
            # Save solution
            solution_file = sample_folder / "solution.json"
            with open(solution_file, 'w', encoding='utf-8') as f:
                json.dump(solution, f, indent=2)
            
            # Save HTML
            html = await page.content()
            html_file = sample_folder / "captcha.html"
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(html)
            
            sample['folder'] = str(sample_folder)
            
            # Add to index
            samples_data['samples'].append(sample)
            with open(self.samples_index_file, 'w', encoding='utf-8') as f:
                json.dump(samples_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"[CAPTCHA-V2] 💾 Sample #{sample_id} saved → {sample_folder}")
            
            return sample
            
        except Exception as e:
            self.logger.error(f"[CAPTCHA-V2] ❌ Failed to save sample: {e}")
            return None
    
    async def _manual_test_dialog(self, page, sample: Dict) -> None:
        """Show manual test dialog"""
        try:
            import tkinter as tk
            from tkinter import messagebox, simpledialog
            
            self.logger.info(f"[CAPTCHA-V2] 🔍 Manual test dialog for sample #{sample['id']}")
            
            # Create dialog
            root = tk.Tk()
            root.withdraw()
            
            message = f"""Sample #{sample['id']} collected!

Rotate value from API: {sample['rotate_value']}
Sample folder: {sample['folder']}

Do you want to test manually?
- Click YES to drag slider manually
- Click NO to skip
"""
            
            result = messagebox.askyesno("Manual Test", message)
            
            if result:
                messagebox.showinfo("Manual Test", "Drag the slider manually now!\n\nClick OK when done.")
                
                # Get slider position after manual drag
                slider = await page.query_selector('div[draggable="true"]')
                manual_translateX = 0
                
                if slider:
                    transform = await slider.evaluate('el => window.getComputedStyle(el).transform')
                    if transform and transform != 'none':
                        import re
                        match = re.search(r'matrix\([^,]+,\s*[^,]+,\s*[^,]+,\s*[^,]+,\s*([^,]+)', transform)
                        if match:
                            manual_translateX = float(match.group(1))
                
                # Check if solved
                captcha_after = await page.query_selector('.TUXModal.captcha-verify-container')
                success = captcha_after is None
                
                # Ask for notes
                notes = simpledialog.askstring("Notes", "Any notes about this test?") or ""
                
                # Update sample
                import json
                with open(self.samples_index_file, 'r', encoding='utf-8') as f:
                    samples_data = json.load(f)
                
                for s in samples_data['samples']:
                    if s['id'] == sample['id']:
                        s['manual_test_result'] = 'success' if success else 'failed'
                        s['manual_translateX'] = manual_translateX
                        s['notes'] = notes
                        break
                
                with open(self.samples_index_file, 'w', encoding='utf-8') as f:
                    json.dump(samples_data, f, indent=2, ensure_ascii=False)
                
                self.logger.info(f"[CAPTCHA-V2] ✅ Manual test result: {success}, translateX: {manual_translateX}px")
            
            root.destroy()
            
        except Exception as e:
            self.logger.error(f"[CAPTCHA-V2] ❌ Manual test dialog error: {e}")
    
    async def solve_captcha(self, page, max_retries: int = 10) -> Optional[Dict]:
        """
        Giải captcha từ page
        
        Args:
            page: Playwright page
            max_retries: Số lần retry (default 6 để thử nhiều captcha khác nhau)
            
        Returns:
            Solution dict hoặc None
        """
        for attempt in range(max_retries):
            try:
                self.logger.info(f"[CAPTCHA-V2] ═══ Attempt {attempt + 1}/{max_retries} ═══")
                
                # Bước 1: Lấy HTML
                self.logger.info("[CAPTCHA-V2] [STEP 1] Getting page HTML...")
                html = await page.content()
                
                # Save HTML for debugging
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                html_file = self.artifacts_dir / f"captcha_html_{timestamp}.html"
                with open(html_file, 'w', encoding='utf-8') as f:
                    f.write(html)
                self.logger.debug(f"[CAPTCHA-V2] Saved HTML to {html_file}")
                
                # Bước 2: Parse HTML và tạo request body
                self.logger.info("[CAPTCHA-V2] [STEP 2] Parsing HTML and creating request body...")
                try:
                    request_body = solve_captcha_from_html(html, self.client.api_key)
                    self.logger.info(f"[CAPTCHA-V2] ✅ Captcha type: {request_body['task']['type']}")
                    
                    # Log request body details
                    task = request_body['task']
                    self.logger.info(f"[CAPTCHA-V2] Task type: {task['type']}")
                    self.logger.info(f"[CAPTCHA-V2] Task keys: {list(task.keys())}")
                    
                    # Log image sizes
                    if 'imageBase64' in task:
                        img_size = len(task['imageBase64'])
                        self.logger.info(f"[CAPTCHA-V2] imageBase64 size: {img_size} chars")
                        
                        # If image is too small (< 3000 chars), try screenshot
                        if img_size < 3000:
                            self.logger.warning(f"[CAPTCHA-V2] ⚠️ Image too small ({img_size} chars), trying screenshot...")
                            screenshot_base64 = await self._screenshot_captcha(page)
                            if screenshot_base64:
                                task['imageBase64'] = screenshot_base64
                                self.logger.info(f"[CAPTCHA-V2] ✅ Using screenshot: {len(screenshot_base64)} chars")
                    
                    if 'imageBase64s' in task:
                        sizes = [len(img) for img in task['imageBase64s']]
                        self.logger.info(f"[CAPTCHA-V2] imageBase64s sizes: {sizes}")
                    if 'widthView' in task:
                        self.logger.info(f"[CAPTCHA-V2] widthView: {task['widthView']}")
                    if 'heightView' in task:
                        self.logger.info(f"[CAPTCHA-V2] heightView: {task['heightView']}")
                    if 'question' in task:
                        self.logger.info(f"[CAPTCHA-V2] question: {task['question']}")
                    
                    # Save request body for debugging
                    import json
                    body_file = self.artifacts_dir / f"request_body_{timestamp}.json"
                    with open(body_file, 'w', encoding='utf-8') as f:
                        # Mask API key and truncate base64
                        masked_body = request_body.copy()
                        masked_body['clientKey'] = f"{request_body['clientKey'][:10]}...{request_body['clientKey'][-10:]}"
                        
                        # Truncate base64 for readability
                        masked_task = masked_body['task'].copy()
                        if 'imageBase64' in masked_task:
                            img = masked_task['imageBase64']
                            masked_task['imageBase64'] = f"{img[:100]}... ({len(img)} chars total)"
                        if 'imageBase64s' in masked_task:
                            masked_task['imageBase64s'] = [
                                f"{img[:100]}... ({len(img)} chars total)" 
                                for img in masked_task['imageBase64s']
                            ]
                        masked_body['task'] = masked_task
                        
                        json.dump(masked_body, f, indent=2)
                    self.logger.info(f"[CAPTCHA-V2] Saved request body to {body_file}")
                    
                except Exception as e:
                    self.logger.error(f"[CAPTCHA-V2] ❌ Failed to parse HTML: {e}")
                    import traceback
                    self.logger.error(traceback.format_exc())
                    continue
                
                # Bước 3: Gọi API
                self.logger.info("[CAPTCHA-V2] [STEP 3] Calling OmoCaptcha API...")
                
                # Extract task info
                task_type = request_body['task']['type']
                task_data = request_body['task']
                
                self.logger.info(f"[CAPTCHA-V2] Creating task with type: {task_type}")
                self.logger.info(f"[CAPTCHA-V2] Task data keys: {list(task_data.keys())}")
                
                # Create task
                task_id = self.client.create_task(task_type, task_data)
                
                if not task_id:
                    self.logger.error("[CAPTCHA-V2] ❌ Failed to create task")
                    self.logger.error("[CAPTCHA-V2] Check OMOcaptcha client logs above for details")
                    continue
                
                self.logger.info(f"[CAPTCHA-V2] ✅ Task created: {task_id}")
                
                # Get result
                self.logger.info(f"[CAPTCHA-V2] Waiting for task result...")
                solution = self.client.get_task_result(task_id)
                
                if solution:
                    self.logger.info(f"[CAPTCHA-V2] ✅ Solution received")
                    self.logger.info(f"[CAPTCHA-V2] Solution keys: {list(solution.keys())}")
                    self.logger.info(f"[CAPTCHA-V2] Solution: {solution}")
                else:
                    self.logger.error("[CAPTCHA-V2] ❌ No solution received")
                    self.logger.error("[CAPTCHA-V2] Check OMOcaptcha client logs above for details")
                    
                    # Refresh captcha để thử captcha mới
                    if attempt < max_retries - 1:  # Không refresh ở lần cuối
                        self.logger.info("[CAPTCHA-V2] 🔄 Trying to refresh captcha for next attempt...")
                        await self._refresh_captcha(page)
                        await asyncio.sleep(1)
                    
                    continue
                
                if solution:
                    self.logger.info(f"[CAPTCHA-V2] ✅ Got solution: {solution}")
                    
                    # Save sample if enabled
                    if self.save_samples:
                        # Calculate coords for THIS solution (not previous one)
                        current_coords = None
                        rotate_value = solution.get('rotate')
                        if rotate_value is not None and self.last_calculated_coords:
                            # Create new coords dict with CURRENT rotate_value
                            current_coords = self.last_calculated_coords.copy()
                            current_coords['rotate_value'] = rotate_value
                            # Recalculate translateX with correct rotate_value
                            current_coords['target_translateX_method2'] = (1 - rotate_value) * 284
                            current_coords['target_translateX_used'] = current_coords['target_translateX_method2']
                        
                        sample = await self._save_sample(
                            page, 
                            request_body, 
                            {'solution': solution}, 
                            attempt + 1,
                            calculated_coords=current_coords or self.last_calculated_coords
                        )
                        
                        # Manual test dialog if enabled
                        if self.enable_manual_test and sample:
                            await self._manual_test_dialog(page, sample)
                    
                    # NOTE: OMOcaptcha API accuracy is inconsistent for TiktokRotateWebTask
                    # Sometimes correct, sometimes wrong. We rely on multiple retries.
                    # DO NOT invert - use value as-is and let retry mechanism handle failures
                    
                    self.logger.info(f"[CAPTCHA-V2] Using rotate value AS-IS: {solution.get('rotate', 'N/A')}")
                    
                    # Bước 4: Apply solution
                    self.logger.info("[CAPTCHA-V2] [STEP 4] Applying solution...")
                    success = await self._apply_solution(page, task_type, solution)
                    
                    if success:
                        self.logger.info("[CAPTCHA-V2] ✅ Solution applied")
                        
                        # Verify
                        await asyncio.sleep(2)
                        
                        try:
                            still_there = await self.detect_captcha(page)
                            
                            if not still_there:
                                self.logger.info("[CAPTCHA-V2] ✅✅✅ CAPTCHA SOLVED! ✅✅✅")
                                return solution
                            else:
                                self.logger.warning("[CAPTCHA-V2] ⚠️ Captcha still present after applying solution")
                                # Refresh captcha để thử lại
                                if attempt < max_retries - 1:
                                    self.logger.info("[CAPTCHA-V2] 🔄 Refreshing captcha for next attempt...")
                                    await self._refresh_captcha(page)
                                    await asyncio.sleep(1)
                        except Exception as e:
                            # If page is closed, captcha might have been solved
                            if "closed" in str(e).lower():
                                self.logger.info("[CAPTCHA-V2] ✅ Page closed - captcha likely solved!")
                                return solution
                            else:
                                raise
                    else:
                        self.logger.error("[CAPTCHA-V2] ❌ Failed to apply solution")
                        # Refresh captcha để thử lại
                        if attempt < max_retries - 1:
                            self.logger.info("[CAPTCHA-V2] 🔄 Refreshing captcha for next attempt...")
                            await self._refresh_captcha(page)
                            await asyncio.sleep(1)
                else:
                    self.logger.error("[CAPTCHA-V2] ❌ No solution from API")
                
            except Exception as e:
                self.logger.error(f"[CAPTCHA-V2] ❌ Error in attempt {attempt + 1}: {e}")
                import traceback
                traceback.print_exc()
        
        self.logger.error(f"[CAPTCHA-V2] ❌❌❌ FAILED after {max_retries} attempts ❌❌❌")
        return None
    
    async def _screenshot_captcha(self, page) -> Optional[str]:
        """Take screenshot of captcha image and convert to base64"""
        try:
            import base64
            
            # Find captcha image element
            selectors = [
                'img[alt*="captcha"]',
                'img[class*="captcha"]',
                'canvas[class*="captcha"]',
                'div.captcha-verify-img-panel img',
                'div[class*="captcha"] img',
                '.secsdk-captcha-drag-img',
            ]
            
            captcha_img = None
            for selector in selectors:
                captcha_img = await page.query_selector(selector)
                if captcha_img:
                    self.logger.info(f"[CAPTCHA-V2] Found captcha image: {selector}")
                    break
            
            if not captcha_img:
                self.logger.warning("[CAPTCHA-V2] ⚠️ Captcha image element not found")
                return None
            
            # Take screenshot of element
            screenshot_bytes = await captcha_img.screenshot()
            
            # Convert to base64
            screenshot_base64 = base64.b64encode(screenshot_bytes).decode('utf-8')
            
            self.logger.info(f"[CAPTCHA-V2] ✅ Screenshot captured: {len(screenshot_base64)} chars")
            return screenshot_base64
            
        except Exception as e:
            self.logger.error(f"[CAPTCHA-V2] ❌ Failed to screenshot captcha: {e}")
            return None
    
    async def _apply_solution(self, page, task_type: str, solution: Dict) -> bool:
        """Apply solution to page"""
        try:
            if 'Slider' in task_type:
                # Slider captcha
                end_x = solution.get('end', {}).get('x', 0)
                self.logger.info(f"[CAPTCHA-V2] Sliding to {end_x}px...")
                
                # Find slider button
                slider = await page.query_selector('button#captcha_slide_button, button.secsdk-captcha-drag-icon')
                if not slider:
                    self.logger.error("[CAPTCHA-V2] ❌ Slider button not found")
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
                
                # Move with steps
                steps = 30
                for i in range(steps + 1):
                    progress = i / steps
                    current_x = start_x + (end_x * progress)
                    await page.mouse.move(current_x, start_y)
                    await asyncio.sleep(0.02)
                
                await asyncio.sleep(0.1)
                await page.mouse.up()
                
                return True
            
            elif 'Rotate' in task_type:
                # Rotate captcha
                rotate_value = solution.get('rotate', 0)
                self.logger.info(f"[CAPTCHA-V2] Rotating {rotate_value}...")
                
                # Log page structure for debugging
                self.logger.info("[CAPTCHA-V2] Searching for rotate control...")
                
                # Try multiple selectors
                rotate_selectors = [
                    'div[draggable="true"]',  # The draggable div wrapper
                    'div.secsdk-captcha-drag-icon',
                    'button#captcha_slide_button',  # The button inside
                    'button.secsdk-captcha-drag-icon',
                    'div[class*="slider"]',
                    'div[class*="drag"]',
                    'input[type="range"]',
                    'div[class*="rotate"]',
                    'div.captcha-slider-track',
                    'div[class*="track"]',
                    # Try finding any draggable element in captcha
                    'div.TUXModal div[draggable="true"]',
                    'div.captcha-verify-container div[class*="slider"]',
                ]
                
                slider = None
                for selector in rotate_selectors:
                    slider = await page.query_selector(selector)
                    if slider:
                        self.logger.info(f"[CAPTCHA-V2] ✅ Found rotate control: {selector}")
                        break
                    else:
                        self.logger.debug(f"[CAPTCHA-V2] Not found: {selector}")
                
                if not slider:
                    self.logger.warning("[CAPTCHA-V2] ⚠️ Rotate slider not found, trying alternative method...")
                    
                    # Try to find rotate images
                    rotate_img_selectors = [
                        'img[class*="rotate"]',
                        'canvas[class*="rotate"]',
                        'div[class*="rotate-inner"]',
                        'div[class*="captcha"] img',
                        'div.captcha-verify-img-panel img',
                        'img[alt*="captcha"]',
                    ]
                    
                    rotate_img = None
                    for selector in rotate_img_selectors:
                        rotate_img = await page.query_selector(selector)
                        if rotate_img:
                            self.logger.info(f"[CAPTCHA-V2] Found rotate image: {selector}")
                            break
                    
                    if rotate_img:
                        box = await rotate_img.bounding_box()
                        if box:
                            # Calculate drag distance based on rotate value (0-1 range)
                            # Typically 0 = no rotation, 1 = 360 degrees
                            center_x = box['x'] + box['width'] / 2
                            center_y = box['y'] + box['height'] / 2
                            drag_distance = rotate_value * box['width']  # Proportional to width
                            
                            self.logger.info(f"[CAPTCHA-V2] Dragging from center by {drag_distance}px...")
                            
                            # Human-like drag (BALANCED)
                            import random
                            
                            # Initial hover
                            await page.mouse.move(center_x - 10, center_y)
                            await asyncio.sleep(random.uniform(0.1, 0.2))
                            await page.mouse.move(center_x, center_y)
                            await asyncio.sleep(random.uniform(0.15, 0.25))
                            
                            # Mouse down
                            await page.mouse.down()
                            await asyncio.sleep(random.uniform(0.15, 0.25))
                            
                            # Drag with human-like movement (BALANCED)
                            steps = random.randint(40, 60)  # 40-60 steps
                            
                            self.logger.info(f"[CAPTCHA-V2] Dragging with {steps} steps (balanced movement)...")
                            
                            for i in range(steps + 1):
                                progress = i / steps
                                
                                # Add slight vertical wobble
                                wobble_y = random.uniform(-2, 2) if i > 0 and i < steps else 0
                                
                                # Add slight horizontal variation
                                progress_variation = progress + random.uniform(-0.01, 0.01)
                                progress_variation = max(0, min(1, progress_variation))
                                
                                current_x = center_x + (drag_distance * progress_variation)
                                current_y = center_y + wobble_y
                                
                                await page.mouse.move(current_x, current_y)
                                
                                # Variable delay (BALANCED)
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
                            
                            self.logger.info("[CAPTCHA-V2] ✅ Rotation applied via drag")
                            return True
                    
                    self.logger.error("[CAPTCHA-V2] ❌ Could not find rotate control")
                    return False
                
                # If slider found, drag it
                box = await slider.bounding_box()
                if not box:
                    self.logger.error("[CAPTCHA-V2] ❌ Could not get slider bounding box")
                    return False
                
                # Read transform to get actual position
                # TikTok uses transform: translateX() to move slider
                transform_value = await slider.evaluate('el => window.getComputedStyle(el).transform')
                current_translate_x = 0
                
                if transform_value and transform_value != 'none':
                    # Parse matrix(1, 0, 0, 1, translateX, translateY)
                    import re
                    match = re.search(r'matrix\([^,]+,\s*[^,]+,\s*[^,]+,\s*[^,]+,\s*([^,]+)', transform_value)
                    if match:
                        current_translate_x = float(match.group(1))
                
                # Get base position (without transform)
                base_x = box['x']
                base_y = box['y']
                
                # Calculate actual center (base + transform)
                current_x = base_x + box['width'] / 2 + current_translate_x
                current_y = base_y + box['height'] / 2
                
                self.logger.info(f"[CAPTCHA-V2] Slider button: base_x={base_x}, y={base_y}, w={box['width']}, h={box['height']}")
                self.logger.info(f"[CAPTCHA-V2] Transform: translateX={current_translate_x}px")
                self.logger.info(f"[CAPTCHA-V2] Actual center: ({current_x}, {current_y}) = base({base_x + box['width']/2}) + translateX({current_translate_x})")
                
                # IMPORTANT: Find the slider TRACK (not button) to get the start position
                # The track is usually the parent container or a sibling element
                # For TikTok rotate captcha, the track width is ~340px
                # We need to calculate the ABSOLUTE target position, not relative distance
                
                # Try to find the track/container
                track_selector = 'div.cap-flex.cap-w-full.cap-h-40'  # The track container
                track = await page.query_selector(track_selector)
                
                if track:
                    track_box = await track.bounding_box()
                    if track_box:
                        # Calculate target position based on track start + rotate value
                        track_start_x = track_box['x']
                        track_width = track_box['width']
                        
                        # IMPORTANT: OMOcaptcha returns rotate value in 0-1 range
                        # This represents the ANGLE rotation needed (0 = 0°, 1 = 360°)
                        # For TikTok rotate captcha, we need to convert this to slider position
                        
                        # The rotate value might represent the angle directly
                        # Let's try: target = track_start + (rotate * track_width)
                        # This assumes rotate is the percentage of track to cover
                        
                        button_width = box['width']
                        
                        # METHOD 1: Simple percentage of track (rotate * track_width)
                        # This assumes the API returns the exact percentage position on track
                        target_x_method1 = track_start_x + (rotate_value * track_width)
                        
                        # METHOD 2: Account for button width (our previous calculation)
                        usable_track_width = track_width - button_width
                        target_x_method2 = track_start_x + (button_width / 2) + (rotate_value * usable_track_width)
                        
                        # METHOD 3: Rotate might be in degrees (0-1 = 0-360°)
                        # For a 360° rotation, slider needs to move full track
                        # So: target = track_start + button_half + (rotate * usable_width)
                        # This is same as METHOD 2
                        
                        # Let's try METHOD 1 first (simpler)
                        target_x = target_x_method1
                        target_y = current_y
                        
                        # Calculate target translateX (not absolute position)
                        # The slider moves by changing translateX, not by changing position
                        # So we need to calculate the target translateX value
                        
                        # METHOD 1: Simple percentage of track
                        # target_translateX = rotate * track_width
                        target_translate_x_method1 = rotate_value * track_width
                        
                        # METHOD 2: Account for button width
                        # target_translateX = (1 - rotate) * (track_width - button_width)
                        # This is the CORRECT formula based on analysis
                        target_translate_x_method2 = (1 - rotate_value) * usable_track_width
                        
                        # Use METHOD 2 (more accurate)
                        target_translate_x = target_translate_x_method2
                        
                        # Calculate absolute target position for mouse movement
                        target_x = base_x + button_width / 2 + target_translate_x
                        
                        self.logger.info(f"[CAPTCHA-V2] Track: x={track_box['x']}, w={track_width}")
                        self.logger.info(f"[CAPTCHA-V2] Button: base_x={base_x}, w={button_width}px, current_translateX={current_translate_x}px")
                        self.logger.info(f"[CAPTCHA-V2] Current center: {current_x} (base + translateX)")
                        self.logger.info(f"[CAPTCHA-V2] Rotate value: {rotate_value} (0-1 range)")
                        self.logger.info(f"[CAPTCHA-V2] METHOD 1: rotate * track_width = {rotate_value} * {track_width} = {target_translate_x_method1:.2f}px")
                        self.logger.info(f"[CAPTCHA-V2] METHOD 2: (1-rotate) * usable_width = (1-{rotate_value}) * {usable_track_width} = {target_translate_x_method2:.2f}px")
                        self.logger.info(f"[CAPTCHA-V2] Using METHOD 2: target_translateX = {target_translate_x:.2f}px")
                        self.logger.info(f"[CAPTCHA-V2] Target position: {target_x:.2f} = base({base_x}) + button_half({button_width/2}) + translateX({target_translate_x:.2f})")
                        self.logger.info(f"[CAPTCHA-V2] Drag distance: {target_x - current_x:.2f}px (from {current_x} to {target_x:.2f})")
                        
                        # Store calculated coordinates for sample collection
                        self.last_calculated_coords = {
                            "rotate_value": rotate_value,
                            "track_width": track_width,
                            "button_width": button_width,
                            "track_start_x": track_box['x'],
                            "base_x": base_x,
                            "current_translateX": current_translate_x,
                            "current_center": current_x,
                            "target_translateX_method1": target_translate_x_method1,
                            "target_translateX_method2": target_translate_x_method2,
                            "target_translateX_used": target_translate_x,
                            "target_position": target_x,
                            "drag_distance": target_x - current_x,
                            "method_used": "METHOD 2"
                        }
                    else:
                        # Fallback: use relative distance
                        captcha_width = 340
                        target_x = current_x + (rotate_value * captcha_width)
                        target_y = current_y
                        self.logger.warning(f"[CAPTCHA-V2] Track box not found, using relative distance")
                        self.logger.info(f"[CAPTCHA-V2] Will drag from ({current_x}, {current_y}) to ({target_x}, {target_y})")
                else:
                    # Fallback: use relative distance from current position
                    captcha_width = 340
                    target_x = current_x + (rotate_value * captcha_width)
                    target_y = current_y
                    self.logger.warning(f"[CAPTCHA-V2] Track not found, using relative distance")
                    self.logger.info(f"[CAPTCHA-V2] Rotate value: {rotate_value} (0-1 range)")
                    self.logger.info(f"[CAPTCHA-V2] Will drag from ({current_x}, {current_y}) to ({target_x}, {target_y})")
                
                drag_distance = target_x - current_x
                
                # Track drag time
                import time
                drag_start_time = time.time()
                
                # Human-like drag with random delays and slight variations
                import random
                
                # Initial hover (người thật thường di chuột đến trước khi click)
                await page.mouse.move(current_x - 10, current_y)
                await asyncio.sleep(random.uniform(0.1, 0.2))
                await page.mouse.move(current_x, current_y)
                await asyncio.sleep(random.uniform(0.15, 0.25))
                
                # Mouse down
                await page.mouse.down()
                await asyncio.sleep(random.uniform(0.15, 0.25))
                
                # Drag with human-like movement (BALANCED - not too fast, not too slow)
                # Cân bằng: đủ chậm để tự nhiên nhưng không quá chậm khiến timeout
                steps = random.randint(40, 60)  # 40-60 steps (vừa phải)
                
                self.logger.info(f"[CAPTCHA-V2] Dragging with {steps} steps (balanced movement)...")
                self.logger.info(f"[CAPTCHA-V2] Drag distance: {drag_distance:.2f}px")
                
                for i in range(steps + 1):
                    progress = i / steps
                    
                    # Add slight vertical wobble (người thật không kéo hoàn toàn thẳng)
                    wobble_y = random.uniform(-2, 2) if i > 0 and i < steps else 0
                    
                    # Add slight horizontal variation (tốc độ không đều)
                    progress_variation = progress + random.uniform(-0.01, 0.01)
                    progress_variation = max(0, min(1, progress_variation))
                    
                    # Calculate position between current and target
                    move_x = current_x + (drag_distance * progress_variation)
                    move_y = current_y + wobble_y
                    
                    await page.mouse.move(move_x, move_y)
                    
                    # Variable delay (BALANCED - không quá nhanh, không quá chậm)
                    if i < steps * 0.2:  # 20% đầu - chậm
                        delay = random.uniform(0.04, 0.06)
                    elif i < steps * 0.4:  # 20% tiếp - trung bình
                        delay = random.uniform(0.03, 0.05)
                    elif i > steps * 0.8:  # 20% cuối - chậm
                        delay = random.uniform(0.04, 0.06)
                    elif i > steps * 0.6:  # 20% trước cuối - trung bình
                        delay = random.uniform(0.03, 0.05)
                    else:  # 40% giữa - nhanh hơn
                        delay = random.uniform(0.02, 0.04)
                    
                    await asyncio.sleep(delay)
                
                # Pause before release (người thật thường dừng 1 chút trước khi thả)
                await asyncio.sleep(random.uniform(0.1, 0.2))
                
                # Log position BEFORE releasing mouse
                try:
                    slider_before_release = await page.query_selector('div[draggable="true"]')
                    if slider_before_release:
                        transform_before_release = await slider_before_release.evaluate('el => window.getComputedStyle(el).transform')
                        translate_before_release = 0
                        if transform_before_release and transform_before_release != 'none':
                            import re
                            match = re.search(r'matrix\([^,]+,\s*[^,]+,\s*[^,]+,\s*[^,]+,\s*([^,]+)', transform_before_release)
                            if match:
                                translate_before_release = float(match.group(1))
                        self.logger.info(f"[CAPTCHA-V2] 🔍 Position BEFORE mouse.up(): translateX={translate_before_release}px")
                except Exception as e:
                    self.logger.debug(f"Could not check position before release: {e}")
                
                await page.mouse.up()
                
                # Wait for animation
                await asyncio.sleep(random.uniform(0.4, 0.6))
                
                # Verify final position by re-querying the slider
                try:
                    # IMPORTANT: Re-query slider to get updated position
                    # The slider element might have been updated by JavaScript
                    await asyncio.sleep(0.5)  # Extra wait for DOM update
                    
                    # Re-find the slider
                    slider_verify = await page.query_selector('div[draggable="true"]')
                    if slider_verify:
                        final_box = await slider_verify.bounding_box()
                        # Read final transform
                        final_transform = await slider_verify.evaluate('el => window.getComputedStyle(el).transform')
                        final_translate_x = 0
                        
                        if final_transform and final_transform != 'none':
                            import re
                            match = re.search(r'matrix\([^,]+,\s*[^,]+,\s*[^,]+,\s*[^,]+,\s*([^,]+)', final_transform)
                            if match:
                                final_translate_x = float(match.group(1))
                        
                        if final_box:
                            final_x = final_box['x'] + final_box['width'] / 2 + final_translate_x
                            actual_distance = final_translate_x - current_translate_x
                            self.logger.info(f"[CAPTCHA-V2] 📊 Verification:")
                            self.logger.info(f"[CAPTCHA-V2] 📊   Before: base_x={base_x}, translateX={current_translate_x}px, center={current_x}")
                            self.logger.info(f"[CAPTCHA-V2] 📊   After:  base_x={final_box['x']}, translateX={final_translate_x}px, center={final_x:.2f}")
                            self.logger.info(f"[CAPTCHA-V2] 📊   Expected drag: {drag_distance:.2f}px, actual translateX change: {actual_distance:.2f}px")
                            self.logger.info(f"[CAPTCHA-V2] 📊   Difference: {abs(actual_distance - drag_distance):.2f}px")
                            
                            # Store actual result for sample collection
                            if self.last_calculated_coords:
                                self.last_calculated_coords['actual_result'] = {
                                    "final_translateX": final_translate_x,
                                    "translateX_change": actual_distance,
                                    "expected_translateX": self.last_calculated_coords.get('target_translateX_used'),
                                    "difference": abs(final_translate_x - self.last_calculated_coords.get('target_translateX_used', 0)),
                                    "drag_successful": abs(actual_distance - drag_distance) <= 10
                                }
                            
                            # Check if drag was successful
                            if abs(actual_distance - drag_distance) > 10:
                                self.logger.warning(f"[CAPTCHA-V2] ⚠️ Drag distance mismatch! Expected {drag_distance:.2f}px but got {actual_distance:.2f}px")
                    else:
                        self.logger.warning("[CAPTCHA-V2] ⚠️ Could not re-find slider for verification")
                except Exception as e:
                    self.logger.warning(f"[CAPTCHA-V2] Could not verify final position: {e}")
                
                drag_duration = time.time() - drag_start_time
                self.logger.info(f"[CAPTCHA-V2] ✅ Rotation applied via slider (took {drag_duration:.2f}s)")
                return True
            
            elif 'Select' in task_type:
                # Select object captcha (3D)
                try:
                    pointA = solution.get('pointA', {})
                    pointB = solution.get('pointB', {})
                    self.logger.info(f"[CAPTCHA-V2] Clicking points A({pointA}) B({pointB})...")
                    
                    # Find captcha image element to get its position
                    self.logger.info("[CAPTCHA-V2] Looking for captcha image...")
                    captcha_img = await page.query_selector('div[class*="captcha"] img, img[alt*="captcha"]')
                    if not captcha_img:
                        self.logger.error("[CAPTCHA-V2] ❌ Captcha image not found")
                        return False
                    
                    self.logger.info("[CAPTCHA-V2] ✅ Found captcha image")
                except Exception as e:
                    self.logger.error(f"[CAPTCHA-V2] ❌ Exception in Select captcha setup: {e}")
                    import traceback
                    self.logger.error(traceback.format_exc())
                    return False
                
                try:
                    # Get image bounding box
                    self.logger.info("[CAPTCHA-V2] Getting image bounding box...")
                    img_box = await captcha_img.bounding_box()
                    if not img_box:
                        self.logger.error("[CAPTCHA-V2] ❌ Could not get image bounding box")
                        return False
                    
                    self.logger.info(f"[CAPTCHA-V2] Image box: x={img_box['x']}, y={img_box['y']}, w={img_box['width']}, h={img_box['height']}")
                    
                    # Calculate absolute positions
                    # pointA and pointB are relative to the image (widthView x heightView)
                    # We need to convert them to absolute page coordinates
                    abs_x_A = img_box['x'] + pointA.get('x', 0)
                    abs_y_A = img_box['y'] + pointA.get('y', 0)
                    abs_x_B = img_box['x'] + pointB.get('x', 0)
                    abs_y_B = img_box['y'] + pointB.get('y', 0)
                    
                    self.logger.info(f"[CAPTCHA-V2] Absolute point A: ({abs_x_A}, {abs_y_A})")
                    self.logger.info(f"[CAPTCHA-V2] Absolute point B: ({abs_x_B}, {abs_y_B})")
                    
                    # Click point A
                    self.logger.info("[CAPTCHA-V2] Clicking point A...")
                    import random
                    await page.mouse.move(abs_x_A, abs_y_A)
                    await asyncio.sleep(random.uniform(0.1, 0.2))
                    await page.mouse.click(abs_x_A, abs_y_A)
                    await asyncio.sleep(random.uniform(0.3, 0.5))
                    self.logger.info("[CAPTCHA-V2] ✅ Clicked point A")
                    
                    # Click point B
                    self.logger.info("[CAPTCHA-V2] Clicking point B...")
                    await page.mouse.move(abs_x_B, abs_y_B)
                    await asyncio.sleep(random.uniform(0.1, 0.2))
                    await page.mouse.click(abs_x_B, abs_y_B)
                    await asyncio.sleep(random.uniform(0.3, 0.5))
                    self.logger.info("[CAPTCHA-V2] ✅ Clicked point B")
                    
                    # Click confirm button
                    self.logger.info("[CAPTCHA-V2] Looking for confirm button...")
                    confirm_selectors = [
                        'button:has-text("Confirm")',
                        'button.TUXButton--primary',
                        'button[class*="confirm"]',
                        'div.TUXModal button.TUXButton--primary',
                    ]
                    
                    for selector in confirm_selectors:
                        confirm_btn = await page.query_selector(selector)
                        if confirm_btn:
                            is_disabled = await confirm_btn.get_attribute('aria-disabled')
                            self.logger.info(f"[CAPTCHA-V2] Found button {selector}, disabled={is_disabled}")
                            if is_disabled != 'true':
                                self.logger.info(f"[CAPTCHA-V2] Clicking confirm button: {selector}")
                                await confirm_btn.click()
                                await asyncio.sleep(0.5)
                                self.logger.info("[CAPTCHA-V2] ✅ Clicked confirm button")
                                return True
                    
                    self.logger.warning("[CAPTCHA-V2] ⚠️ Confirm button not found or disabled")
                    return False
                    
                except Exception as e:
                    self.logger.error(f"[CAPTCHA-V2] ❌ Exception during click sequence: {e}")
                    import traceback
                    self.logger.error(traceback.format_exc())
                    return False
            
            return False
            
        except Exception as e:
            self.logger.error(f"[CAPTCHA-V2] Error applying solution: {e}")
            return False


# ============================================================================
# USAGE EXAMPLE
# ============================================================================

async def example_usage():
    """Example: Sử dụng TikTokCaptchaSolverV2"""
    import os
    from core.chrome_manager import ChromeProfileManager
    
    # Initialize
    api_key = os.getenv('OMOCAPTCHA_API_KEY')
    if not api_key:
        print("❌ Set OMOCAPTCHA_API_KEY")
        return
    
    omocaptcha_client = OMOcaptchaClient(api_key=api_key)
    solver = TikTokCaptchaSolverV2(omocaptcha_client, debug_level="INFO")
    
    # Launch profile
    manager = ChromeProfileManager()
    success, page = manager.launch_chrome_profile(
        "test_profile",
        hidden=False,
        start_url="https://www.tiktok.com/login",

    )
    
    if not success:
        print("❌ Failed to launch")
        return
    
    # Wait for captcha
    await asyncio.sleep(5)
    
    # Detect and solve
    has_captcha = await solver.detect_captcha(page)
    if has_captcha:
        print("🎯 Captcha detected, solving...")
        solution = await solver.solve_captcha(page)
        
        if solution:
            print("✅ Captcha solved!")
        else:
            print("❌ Failed to solve")
    else:
        print("✅ No captcha")


if __name__ == "__main__":
    asyncio.run(example_usage())
