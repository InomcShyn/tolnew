"""
Tích hợp OMOcaptcha API để giải TikTok captcha tự động
Tài liệu: https://docs.omocaptcha.com/tai-lieu-api/tiktok/
"""

import requests
import time
import base64
import logging
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)


class OMOcaptchaClient:
    """
    Client để giao tiếp với OMOcaptcha API
    
    Hỗ trợ tất cả loại TikTok captcha:
    - TiktokRotateWebTask
    - TiktokSelectObjectWebTask
    - Tiktok3DSelectObjectWebTask
    - TiktokSliderWebTask
    - TiktokSliderPhoneTask
    - Tiktok3DSelectObjectPhoneTask
    
    Docs: https://docs.omocaptcha.com/tai-lieu-api/tiktok/
    """
    
    def __init__(self, api_key: str, api_url: str = None):
        """
        Args:
            api_key: API key từ OMOcaptcha
            api_url: Custom API URL (optional, default: https://api.omocaptcha.com/v2)
        """
        self.api_key = api_key
        self.base_url = api_url or "https://api.omocaptcha.com/v2"
        self.logger = logger
        
        self.logger.info(f"[OMO] Initialized with API URL: {self.base_url}")
        
    def get_balance(self) -> Optional[float]:
        """Kiểm tra số dư tài khoản OMOcaptcha.

        Returns:
            Số dư (float) nếu thành công, None nếu thất bại
        """
        try:
            self.logger.info("💰 [OMO] Checking account balance...")
            resp = requests.post(
                f"{self.base_url}/getBalance",
                json={"clientKey": self.api_key},
                timeout=20
            )
            self.logger.info(f"💰 [OMO] Balance status: {resp.status_code}")
            self.logger.info(f"💰 [OMO] Balance body: {resp.text[:200]}")
            resp.raise_for_status()
            data = resp.json()

            if data.get("errorId") == 0:
                balance = data.get("balance") or data.get("Balance")
                try:
                    balance = float(balance)
                except Exception:
                    balance = None
                self.logger.info(f"💰 [OMO] Balance: {balance}")
                return balance
            else:
                self.logger.error(
                    f"❌ [OMO] Balance check failed: errorId={data.get('errorId')}, "
                    f"code={data.get('errorCode','')}, desc={data.get('errorDescription','')}"
                )
                return None
        except requests.exceptions.RequestException as e:
            self.logger.error(f"❌ [OMO] Balance request error: {e}")
            return None
        except Exception as e:
            self.logger.error(f"❌ [OMO] Balance error: {e}")
            return None

    def create_task(self, task_type: str, task_data: Dict) -> Optional[str]:
        """
        Tạo task giải captcha
        
        Args:
            task_type: Loại captcha (TiktokRotateWebTask, TiktokSelectObjectWebTask, etc.)
            task_data: Dữ liệu cho task
            
        Returns:
            taskId nếu thành công, None nếu thất bại
        """
        try:
            self.logger.info(f"🔗 [OMO] Creating {task_type} task...")
            self.logger.info(f"🔗 [OMO] API Key: {self.api_key[:20]}...{self.api_key[-10:]}")
            self.logger.info(f"🔗 [OMO] Base URL: {self.base_url}")
            
            payload = {
                "clientKey": self.api_key,
                "task": {
                    "type": task_type,
                    **task_data
                }
            }
            
            self.logger.info(f"🔗 [OMO] Request URL: {self.base_url}/createTask")
            self.logger.info(f"🔗 [OMO] Task type: {task_type}")
            self.logger.info(f"🔗 [OMO] Task data keys: {list(task_data.keys())}")
            
            # Log detailed task data (without full base64)
            for key, value in task_data.items():
                if 'base64' in key.lower():
                    if isinstance(value, list):
                        sizes = [len(str(v)) for v in value]
                        self.logger.info(f"🔗 [OMO]   {key}: [{', '.join(f'{s} chars' for s in sizes)}]")
                    else:
                        self.logger.info(f"🔗 [OMO]   {key}: {len(str(value))} chars")
                else:
                    self.logger.info(f"🔗 [OMO]   {key}: {value}")
            
            # Log request body structure
            import json
            body_preview = json.dumps({
                "clientKey": f"{self.api_key[:10]}...{self.api_key[-5:]}",
                "task": {
                    "type": task_type,
                    **{k: f"<{len(str(v))} chars>" if 'base64' in k.lower() else v 
                       for k, v in task_data.items()}
                }
            }, indent=2)
            self.logger.info(f"🔗 [OMO] Request body preview:\n{body_preview}")
            
            response = requests.post(
                f"{self.base_url}/createTask",
                json=payload,
                timeout=30
            )
            
            self.logger.info(f"🔗 [OMO] Response status: {response.status_code}")
            self.logger.info(f"🔗 [OMO] Response headers: {dict(response.headers)}")
            self.logger.info(f"🔗 [OMO] Response text: {response.text}")
            
            response.raise_for_status()
            result = response.json()
            
            if result.get("errorId") == 0:
                task_id = result.get("taskId")
                self.logger.info(f"✅ [OMO] Created {task_type} task: {task_id}")
                return task_id
            else:
                error_code = result.get("errorCode", "")
                error_desc = result.get("errorDescription", "")
                self.logger.error(f"❌ [OMO] Failed to create task: errorId={result.get('errorId')}, code={error_code}, desc={error_desc}")
                return None
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"❌ [OMO] Request error: {e}")
            return None
        except Exception as e:
            self.logger.error(f"❌ [OMO] Error creating task: {e}")
            return None
    
    def get_task_result(self, task_id: str, wait_time: int = 2, max_wait: int = 120) -> Optional[Dict]:
        """
        Lấy kết quả giải captcha
        
        Args:
            task_id: ID của task
            wait_time: Thời gian chờ giữa các lần query (giây)
            max_wait: Thời gian tối đa chờ (giây)
            
        Returns:
            Dictionary chứa solution nếu ready, None nếu thất bại
        """
        start_time = time.time()
        query_count = 0
        
        self.logger.info(f"🔍 [OMO] Getting task result for: {task_id}")
        self.logger.info(f"🔍 [OMO] Max wait time: {max_wait}s, Query interval: {wait_time}s")
        
        while True:
            try:
                elapsed = time.time() - start_time
                if elapsed > max_wait:
                    self.logger.error(f"⏰ [OMO] Timeout after {elapsed:.1f}s waiting for task result: {task_id}")
                    return None
                
                query_count += 1
                self.logger.info(f"🔍 [OMO] Query #{query_count} (elapsed: {elapsed:.1f}s)")
                
                request_body = {
                    "clientKey": self.api_key,
                    "taskId": task_id
                }
                
                self.logger.debug(f"🔍 [OMO] Request body: {request_body}")
                
                response = requests.post(
                    f"{self.base_url}/getTaskResult",
                    json=request_body,
                    timeout=30
                )
                
                self.logger.info(f"🔍 [OMO] Response status: {response.status_code}")
                self.logger.info(f"🔍 [OMO] Response headers: {dict(response.headers)}")
                self.logger.info(f"🔍 [OMO] Response text (full): {response.text}")
                
                response.raise_for_status()
                result = response.json()
                
                status = result.get("status")
                self.logger.info(f"🔍 [OMO] Task status: {status}")
                
                if status == "ready":
                    solution = result.get("solution")
                    self.logger.info(f"✅ [OMO] Task {task_id} completed successfully!")
                    self.logger.info(f"✅ [OMO] Solution: {solution}")
                    return solution
                elif status == "processing" or status == "waiting":
                    self.logger.info(f"⏳ [OMO] Task {task_id} still {status}, waiting {wait_time}s...")
                    time.sleep(wait_time)
                elif status == "fail" or status == "failed":
                    error_code = result.get("errorCode", "")
                    error_desc = result.get("errorDescription", "")
                    error_id = result.get("errorId", "")
                    self.logger.error(f"❌ [OMO] Task failed: errorId={error_id}, code={error_code}, desc={error_desc}")
                    return None
                else:
                    # Unknown status - log and continue waiting
                    self.logger.warning(f"⚠️ [OMO] Unknown status '{status}', continuing to wait...")
                    time.sleep(wait_time)
                    
            except requests.exceptions.RequestException as e:
                self.logger.error(f"❌ [OMO] Request error getting task result: {e}")
                return None
            except Exception as e:
                self.logger.error(f"❌ [OMO] Error getting task result: {e}")
                return None
    
    def solve_tiktok_rotate(self, image_base64: str) -> Optional[float]:
        """
        Giải TikTok Rotate captcha
        
        Args:
            image_base64: Ảnh captcha dạng base64 (hoặc list 2 ảnh)
            
        Returns:
            Góc xoay (degree) hoặc None nếu thất bại
        """
        # TikTok Rotate cần array chứa 2 ảnh: [inside, outside]
        # Nếu chỉ có 1 ảnh, tạo array với 2 ảnh giống nhau
        if isinstance(image_base64, str):
            image_base64s = [image_base64, image_base64]
        else:
            image_base64s = image_base64
        
        task_id = self.create_task(
            "TiktokRotateWebTask",
            {"imageBase64s": image_base64s}
        )
        
        if not task_id:
            return None
        
        solution = self.get_task_result(task_id)
        if solution and "rotate" in solution:
            return solution["rotate"]
        return None
    
    def solve_tiktok_select_object(self, image_base64: str, width: int, height: int, 
                                   question: str = None) -> Optional[Tuple[Dict, Dict]]:
        """
        Giải TikTok Select Object captcha
        
        Args:
            image_base64: Ảnh captcha dạng base64
            width: Chiều rộng ảnh
            height: Chiều cao ảnh
            question: Câu hỏi (optional)
            
        Returns:
            Tuple (pointA, pointB) hoặc None nếu thất bại
        """
        task_data = {
            "imageBase64": image_base64,
            "widthView": width,
            "heightView": height
        }
        
        if question:
            task_data["question"] = question
        
        task_id = self.create_task("TiktokSelectObjectWebTask", task_data)
        
        if not task_id:
            return None
        
        solution = self.get_task_result(task_id)
        if solution and "pointA" in solution and "pointB" in solution:
            return (solution["pointA"], solution["pointB"])
        return None
    
    def solve_tiktok_3d_select_object(self, image_base64: str, width: int, height: int) -> Optional[Tuple[Dict, Dict]]:
        """
        Giải TikTok 3D Select Object captcha
        
        Args:
            image_base64: Ảnh captcha dạng base64
            width: Chiều rộng ảnh
            height: Chiều cao ảnh
            
        Returns:
            Tuple (pointA, pointB) hoặc None nếu thất bại
        """
        task_data = {
            "imageBase64": image_base64,
            "widthView": width,
            "heightView": height
        }
        
        task_id = self.create_task("Tiktok3DSelectObjectWebTask", task_data)
        
        if not task_id:
            return None
        
        solution = self.get_task_result(task_id)
        if solution and "pointA" in solution and "pointB" in solution:
            return (solution["pointA"], solution["pointB"])
        return None
    
    def solve_tiktok_slider(self, image_base64: str, width: int, height: int) -> Optional[Dict]:
        """
        Giải TikTok Slider captcha (Web version)
        
        Args:
            image_base64: Ảnh captcha dạng base64
            width: Chiều rộng ảnh
            height: Chiều cao ảnh
            
        Returns:
            Dict chứa vị trí end ({x: int}) hoặc None nếu thất bại
        """
        task_data = {
            "imageBase64": image_base64,
            "widthView": width,
            "heightView": height
        }
        
        task_id = self.create_task("TiktokSliderWebTask", task_data)
        
        if not task_id:
            return None
        
        solution = self.get_task_result(task_id)
        if solution and "end" in solution:
            return solution["end"]
        return None
    
    def solve_tiktok_slider_phone(self, image_base64: str, width: int, height: int) -> Optional[Dict]:
        """
        Giải TikTok Slider captcha (Phone version)
        
        Args:
            image_base64: Ảnh captcha dạng base64
            width: Chiều rộng ảnh
            height: Chiều cao ảnh
            
        Returns:
            Dict chứa vị trí end ({x: int}) hoặc None nếu thất bại
        """
        task_data = {
            "imageBase64": image_base64,
            "widthView": width,
            "heightView": height
        }
        
        task_id = self.create_task("TiktokSliderPhoneTask", task_data)
        
        if not task_id:
            return None
        
        solution = self.get_task_result(task_id)
        if solution and "end" in solution:
            return solution["end"]
        return None
    
    def solve_tiktok_3d_select_object_phone(self, image_base64: str, width: int, height: int) -> Optional[Tuple[Dict, Dict]]:
        """
        Giải TikTok 3D Select Object captcha (Phone version)
        
        Args:
            image_base64: Ảnh captcha dạng base64
            width: Chiều rộng ảnh
            height: Chiều cao ảnh
            
        Returns:
            Tuple (pointA, pointB) hoặc None nếu thất bại
        """
        task_data = {
            "imageBase64": image_base64,
            "widthView": width,
            "heightView": height
        }
        
        task_id = self.create_task("Tiktok3DSelectObjectPhoneTask", task_data)
        
        if not task_id:
            return None
        
        solution = self.get_task_result(task_id)
        if solution and "pointA" in solution and "pointB" in solution:
            return (solution["pointA"], solution["pointB"])
        return None
    
    def solve_captcha_auto(self, captcha_type: str, image_base64, width: int = None, 
                          height: int = None, question: str = None) -> Optional[any]:
        """
        Tự động giải captcha dựa trên type
        
        Args:
            captcha_type: Loại captcha (rotate, select, 3d, slider, slider_phone, 3d_phone)
            image_base64: Ảnh captcha (string hoặc list)
            width: Chiều rộng (required cho select/slider)
            height: Chiều cao (required cho select/slider)
            question: Câu hỏi (optional cho select)
            
        Returns:
            Solution tương ứng với từng loại captcha
        """
        captcha_type = captcha_type.lower()
        
        if captcha_type == "rotate":
            return self.solve_tiktok_rotate(image_base64)
        
        elif captcha_type == "select":
            if not width or not height:
                self.logger.error("[OMO] Width and height required for select captcha")
                return None
            return self.solve_tiktok_select_object(image_base64, width, height, question)
        
        elif captcha_type == "3d":
            if not width or not height:
                self.logger.error("[OMO] Width and height required for 3D captcha")
                return None
            return self.solve_tiktok_3d_select_object(image_base64, width, height)
        
        elif captcha_type == "slider":
            if not width or not height:
                self.logger.error("[OMO] Width and height required for slider captcha")
                return None
            return self.solve_tiktok_slider(image_base64, width, height)
        
        elif captcha_type == "slider_phone":
            if not width or not height:
                self.logger.error("[OMO] Width and height required for slider phone captcha")
                return None
            return self.solve_tiktok_slider_phone(image_base64, width, height)
        
        elif captcha_type == "3d_phone":
            if not width or not height:
                self.logger.error("[OMO] Width and height required for 3D phone captcha")
                return None
            return self.solve_tiktok_3d_select_object_phone(image_base64, width, height)
        
        else:
            self.logger.error(f"[OMO] Unknown captcha type: {captcha_type}")
            return None


async def capture_captcha_image_playwright(page, selector: str = None) -> Optional[str]:
    """
    Chụp ảnh captcha từ Playwright page
    
    Args:
        page: Playwright Page object
        selector: CSS selector của captcha element (optional)
        
    Returns:
        Base64 string của ảnh captcha
    """
    try:
        if selector:
            # Chụp element cụ thể
            element = await page.query_selector(selector)
            if not element:
                logger.error(f"[CAPTCHA] Element not found: {selector}")
                return None
            
            screenshot = await element.screenshot()
        else:
            # Chụp toàn bộ page
            screenshot = await page.screenshot()
        
        # Convert to base64
        return base64.b64encode(screenshot).decode('utf-8')
        
    except Exception as e:
        logger.error(f"[CAPTCHA] Error capturing image: {e}")
        return None


async def get_captcha_dimensions(page, selector: str) -> Optional[Tuple[int, int]]:
    """
    Lấy kích thước của captcha element
    
    Args:
        page: Playwright Page object
        selector: CSS selector của captcha element
        
    Returns:
        Tuple (width, height) hoặc None nếu thất bại
    """
    try:
        element = await page.query_selector(selector)
        if not element:
            logger.error(f"[CAPTCHA] Element not found: {selector}")
            return None
        
        box = await element.bounding_box()
        if not box:
            logger.error(f"[CAPTCHA] Could not get bounding box")
            return None
        
        return (int(box['width']), int(box['height']))
        
    except Exception as e:
        logger.error(f"[CAPTCHA] Error getting dimensions: {e}")
        return None


async def detect_captcha_type(page) -> Optional[str]:
    """
    Tự động detect loại captcha TikTok
    
    Args:
        page: Playwright Page object
        
    Returns:
        Loại captcha (rotate, select, 3d, slider) hoặc None
    """
    try:
        # Check for rotate captcha
        rotate_element = await page.query_selector('[class*="rotate"]')
        if rotate_element:
            return "rotate"
        
        # Check for slider captcha
        slider_element = await page.query_selector('[class*="slider"]')
        if slider_element:
            return "slider"
        
        # Check for select object captcha
        select_element = await page.query_selector('[class*="select"]')
        if select_element:
            # Check if 3D
            is_3d = await page.query_selector('[class*="3d"]')
            return "3d" if is_3d else "select"
        
        logger.warning("[CAPTCHA] Could not detect captcha type")
        return None
        
    except Exception as e:
        logger.error(f"[CAPTCHA] Error detecting captcha type: {e}")
        return None


def capture_captcha_image(driver) -> str:
    """
    Chụp ảnh captcha từ Selenium browser (deprecated, use Playwright version)
    
    Args:
        driver: Selenium WebDriver
        
    Returns:
        Base64 string của ảnh captcha
    """
    try:
        # Tìm element captcha (adjust selector as needed)
        captcha_element = driver.find_element("css selector", "[data-testid='captcha-image']")
        
        # Chụp screenshot của element
        screenshot = captcha_element.screenshot_as_png
        
        # Convert to base64
        import base64
        return base64.b64encode(screenshot).decode('utf-8')
        
    except Exception as e:
        logger.error(f"Error capturing captcha image: {e}")
        return None

