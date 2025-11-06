"""
TikTok Captcha Solver sử dụng OMOcaptcha API
Dựa trên: https://docs.omocaptcha.com/tai-lieu-api/tiktok/
"""

import base64
import time
import logging
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# Import OMOcaptcha client
try:
    from core.omocaptcha_client import OMOcaptchaClient
    OMOCAPTCHA_AVAILABLE = True
except ImportError:
    OMOCAPTCHA_AVAILABLE = False
    print("⚠️ OMOcaptcha client not available. Please install: pip install requests")


class TikTokCaptchaSolver:
    """Solver cho TikTok captcha sử dụng OMOcaptcha API"""
    
    def __init__(self, driver, omocaptcha_api_key=None):
        self.driver = driver
        self.logger = logging.getLogger(__name__)
        self.omocaptcha_client = None
        
        self.logger.info(f"🔧 [CAPTCHA] Initializing TikTokCaptchaSolver...")
        self.logger.info(f"🔧 [CAPTCHA] OMOcaptcha available: {OMOCAPTCHA_AVAILABLE}")
        self.logger.info(f"🔧 [CAPTCHA] API key provided: {bool(omocaptcha_api_key)}")
        
        # Khởi tạo OMOcaptcha client nếu có API key
        if OMOCAPTCHA_AVAILABLE and omocaptcha_api_key:
            try:
                self.logger.info(f"🔧 [CAPTCHA] Creating OMOcaptcha client...")
                self.omocaptcha_client = OMOcaptchaClient(omocaptcha_api_key)
                self.logger.info("✅ [CAPTCHA] OMOcaptcha client initialized successfully")
            except Exception as e:
                self.logger.error(f"❌ [CAPTCHA] Failed to initialize OMOcaptcha: {e}")
                import traceback
                self.logger.error(f"❌ [CAPTCHA] Traceback: {traceback.format_exc()}")
                self.omocaptcha_client = None
        else:
            if not OMOCAPTCHA_AVAILABLE:
                self.logger.warning("⚠️ [CAPTCHA] OMOcaptcha module not available")
            if not omocaptcha_api_key:
                self.logger.warning("⚠️ [CAPTCHA] OMOcaptcha API key not provided")
    
    def capture_captcha_image(self) -> str:
        """
        Chụp ảnh captcha từ browser và convert sang base64
        
        Returns:
            Base64 string của ảnh captcha
        """
        try:
            self.logger.info(f"📸 [CAPTCHA] Starting captcha image capture...")
            
            # Các selector có thể có cho captcha
            captcha_selectors = [
                "iframe[title*='security']",
                "iframe[title*='verification']",
                "[data-testid*='captcha']",
                ".captcha-container",
                "img[alt*='captcha' i]",
                "canvas"  # TikTok thường dùng canvas cho captcha
            ]
            
            self.logger.info(f"📸 [CAPTCHA] Trying {len(captcha_selectors)} captcha selectors...")
            
            captcha_element = None
            for i, selector in enumerate(captcha_selectors):
                try:
                    self.logger.info(f"📸 [CAPTCHA] Selector {i+1}/{len(captcha_selectors)}: {selector}")
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    self.logger.info(f"📸 [CAPTCHA] Found {len(elements)} elements")
                    
                    for elem in elements:
                        if elem.is_displayed():
                            captcha_element = elem
                            self.logger.info(f"✅ [CAPTCHA] Found visible captcha element with selector: {selector}")
                    break
                    if captcha_element:
                        break
                except Exception as e:
                    self.logger.debug(f"📸 [CAPTCHA] Selector failed: {e}")
                    continue
            
            # Nếu tìm thấy element captcha, chụp nó
            if captcha_element:
                self.logger.info(f"📸 [CAPTCHA] Capturing element screenshot...")
                screenshot = captcha_element.screenshot_as_png()
            else:
                self.logger.warning(f"📸 [CAPTCHA] No captcha element found, capturing full page screenshot")
                # Fallback: chụp toàn màn hình
                screenshot = self.driver.get_screenshot_as_png()
            
            self.logger.info(f"📸 [CAPTCHA] Screenshot captured (size: {len(screenshot)} bytes)")
            
            # Convert to base64
            base64_str = base64.b64encode(screenshot).decode('utf-8')
            self.logger.info(f"📸 [CAPTCHA] Converted to base64 (length: {len(base64_str)})")
            
            return base64_str
            
        except Exception as e:
            self.logger.error(f"❌ [CAPTCHA] Error capturing captcha image: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return None
    
    def detect_captcha_type(self) -> str:
        """
        Phát hiện loại captcha từ page elements
        
        Returns:
            captcha type ('rotate', 'select_object', '3d_select_object', 'slider')
        """
        try:
            # Kiểm tra các element trên page để xác định loại captcha
            page_source = self.driver.page_source.lower()
            
            if 'rotate' in page_source or 'xoay' in page_source:
                return 'rotate'
            elif '3d' in page_source or '3-d' in page_source:
                return '3d_select_object'
            elif 'slider' in page_source or 'slide' in page_source or 'trượt' in page_source:
                return 'slider'
            elif 'click' in page_source or 'select' in page_source or 'chọn' in page_source:
                return 'select_object'
            else:
                # Default: select object
                return 'select_object'
            
        except Exception as e:
            self.logger.error(f"Error detecting captcha type: {e}")
            return 'select_object'  # Default
    
    def solve_captcha(self) -> bool:
        """
        Giải captcha chính - ưu tiên OMOcaptcha
        
        Returns:
            True nếu thành công
        """
        self.logger.info(f"🎯 [CAPTCHA] solve_captcha() called")
        
        if not self.omocaptcha_client:
            self.logger.error("❌ [CAPTCHA] OMOcaptcha client not available")
        return False
    
        self.logger.info(f"✅ [CAPTCHA] OMOcaptcha client is available")
        
        try:
            # Phát hiện loại captcha
            self.logger.info(f"🔍 [CAPTCHA] Detecting captcha type...")
            captcha_type = self.detect_captcha_type()
            self.logger.info(f"🔍 [CAPTCHA] Detected captcha type: {captcha_type}")
            
            # Chụp ảnh captcha
            self.logger.info(f"📸 [CAPTCHA] Capturing captcha image...")
            image_base64 = self.capture_captcha_image()
            if not image_base64:
                self.logger.error("❌ [CAPTCHA] Failed to capture captcha image")
            return False
            
            self.logger.info(f"📸 [CAPTCHA] Captcha image captured (size: {len(image_base64)} bytes)")
            
            # Tìm kích thước captcha
            try:
                captcha_element = self.driver.find_element(By.CSS_SELECTOR, "iframe[title*='security'], iframe[title*='verification']")
                width = captcha_element.size['width'] or 340
                height = captcha_element.size['height'] or 212
            except:
                width, height = 340, 212  # Default TikTok captcha size
            
            # Giải captcha theo loại
            solution = None
            
            if captcha_type == 'rotate':
                self.logger.info("🔄 Solving TikTok Rotate captcha...")
                # TikTok Rotate cần 2 ảnh (inside + outside)
                solution = self.omocaptcha_client.solve_tiktok_rotate(image_base64)
                
                if solution:
                    # Thực hiện xoay
                    try:
                        rotate_elem = self.driver.find_element(By.CSS_SELECTOR, "[data-rotate], .rotate-handle")
                        actions = ActionChains(self.driver)
                        actions.click_and_hold(rotate_elem)
                        actions.move_by_offset(0, -int(solution))
                        actions.release()
                        actions.perform()
                    except:
                        self.logger.warning("Could not find rotate element, trying JavaScript")
                        self.driver.execute_script(f"window.dispatchEvent(new KeyboardEvent('keydown', {{key: 'ArrowRight'}}));")
                
            elif captcha_type in ['select_object', '3d_select_object']:
                task_type = '3d_select_object' if captcha_type == '3d_select_object' else 'select_object'
                self.logger.info(f"🖱️ Solving TikTok {task_type} captcha...")
                
                # Lấy question nếu có
                question = None
                try:
                    question_elem = self.driver.find_element(By.CSS_SELECTOR, "[data-question], .captcha-question")
                    question = question_elem.text
                except:
                    pass
                
                if task_type == '3d_select_object':
                    solution = self.omocaptcha_client.solve_tiktok_3d_select_object(image_base64, width, height)
                else:
                    solution = self.omocaptcha_client.solve_tiktok_select_object(image_base64, width, height, question)
                
                if solution:
                    pointA, pointB = solution
                    # Click vào 2 điểm bằng JavaScript
                    x1 = pointA.get('x', 0) if isinstance(pointA, dict) else pointA['x']
                    y1 = pointA.get('y', 0) if isinstance(pointA, dict) else pointA['y']
                    x2 = pointB.get('x', 0) if isinstance(pointB, dict) else pointB['x']
                    y2 = pointB.get('y', 0) if isinstance(pointB, dict) else pointB['y']
                    
                    js_script = f"""
                    function clickAt(x, y) {{
                        var evt = new MouseEvent('click', {{
                            bubbles: true, cancelable: true, view: window,
                            clientX: x, clientY: y
                        }});
                        document.elementFromPoint(x, y).dispatchEvent(evt);
                    }}
                    clickAt({x1}, {y1});
                    setTimeout(() => clickAt({x2}, {y2}), 500);
                    """
                    self.driver.execute_script(js_script)
                
            elif captcha_type == 'slider':
                self.logger.info("↔️ Solving TikTok Slider captcha...")
                solution = self.omocaptcha_client.solve_tiktok_slider(image_base64, width, height)
                
                if solution and 'x' in solution:
                    # Kéo slider
                    try:
                        slider = self.driver.find_element(By.CSS_SELECTOR, "[data-slider], .slider-button, .captcha-slider")
                        actions = ActionChains(self.driver)
                        actions.click_and_hold(slider)
                        actions.move_by_offset(solution['x'], 0)
                        actions.release()
                        actions.perform()
                    except:
                        self.logger.warning("Could not find slider element")
            
            if solution:
                self.logger.info("✅ Captcha solved successfully with OMOcaptcha!")
                time.sleep(2)  # Chờ captcha xác thực
                return True
            else:
                self.logger.error("❌ Failed to get solution from OMOcaptcha")
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Error solving captcha: {e}")
            return False
