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
    """Client để giao tiếp với OMOcaptcha API"""
    
    def __init__(self, api_key: str):
        """
        Args:
            api_key: API key từ OMOcaptcha
        """
        self.api_key = api_key
        self.base_url = "https://api.omocaptcha.com/v2"
        self.logger = logger
        
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
            
            response = requests.post(
                f"{self.base_url}/createTask",
                json=payload,
                timeout=30
            )
            
            self.logger.info(f"🔗 [OMO] Response status: {response.status_code}")
            self.logger.info(f"🔗 [OMO] Response text: {response.text[:200]}")
            
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
                
                response = requests.post(
                    f"{self.base_url}/getTaskResult",
                    json={
                        "clientKey": self.api_key,
                        "taskId": task_id
                    },
                    timeout=30
                )
                
                self.logger.info(f"🔍 [OMO] Response status: {response.status_code}")
                self.logger.info(f"🔍 [OMO] Response text: {response.text[:200]}")
                
                response.raise_for_status()
                result = response.json()
                
                status = result.get("status")
                self.logger.info(f"🔍 [OMO] Task status: {status}")
                
                if status == "ready":
                    solution = result.get("solution")
                    self.logger.info(f"✅ [OMO] Task {task_id} completed successfully!")
                    self.logger.info(f"✅ [OMO] Solution: {solution}")
                    return solution
                elif status == "processing":
                    self.logger.info(f"⏳ [OMO] Task {task_id} still processing, waiting {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    error_code = result.get("errorCode", "")
                    error_desc = result.get("errorDescription", "")
                    error_id = result.get("errorId", "")
                    self.logger.error(f"❌ [OMO] Task failed: errorId={error_id}, code={error_code}, desc={error_desc}")
                    return None
                    
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
        Giải TikTok Slider captcha
        
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


def capture_captcha_image(driver) -> str:
    """
    Chụp ảnh captcha từ browser
    
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

