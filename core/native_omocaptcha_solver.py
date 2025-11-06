"""
Native OMOcaptcha Solver - Giải captcha TikTok không cần WebDriver
Sử dụng PyAutoGUI + OMOcaptcha API để giải captcha
"""

import time
import base64
import logging
import pyautogui
from PIL import Image
import io
import os
from datetime import datetime

# Optional Windows focus helpers
try:
    import win32gui
    import win32con
    import win32process
    WIN32_AVAILABLE = True
except Exception:
    WIN32_AVAILABLE = False

try:
    from core.omocaptcha_client import OMOcaptchaClient
    OMOCAPTCHA_AVAILABLE = True
except ImportError:
    OMOCAPTCHA_AVAILABLE = False


class NativeOMOcaptchaSolver:
    """Solver cho TikTok captcha không cần WebDriver"""
    
    def __init__(self, omocaptcha_api_key=None):
        self.logger = logging.getLogger(__name__)
        self.omocaptcha_client = None
        pyautogui.FAILSAFE = False
        
        # Khởi tạo OMOcaptcha client
        if OMOCAPTCHA_AVAILABLE and omocaptcha_api_key:
            try:
                # Validate API key format (should be non-empty string)
                if not isinstance(omocaptcha_api_key, str) or not omocaptcha_api_key.strip():
                    self.logger.error("❌ [NATIVE-OMO] Invalid API key format: empty or not a string")
                    self.omocaptcha_client = None
                else:
                    # Check for placeholder values
                    key_lower = omocaptcha_api_key.strip().lower()
                    if key_lower in ('your_api_key_here', 'your_omocaptcha_api_key_here', ''):
                        self.logger.error("❌ [NATIVE-OMO] API key is a placeholder. Please set a valid API key in config.ini")
                        self.omocaptcha_client = None
                    else:
                        self.omocaptcha_client = OMOcaptchaClient(omocaptcha_api_key)
                        self.logger.info("✅ [NATIVE-OMO] OMOcaptcha client initialized")
            except Exception as e:
                self.logger.error(f"❌ [NATIVE-OMO] Failed to initialize OMOcaptcha: {e}")
                import traceback
                self.logger.error(f"Traceback: {traceback.format_exc()}")
                self.omocaptcha_client = None
        else:
            if not OMOCAPTCHA_AVAILABLE:
                self.logger.warning("⚠️ [NATIVE-OMO] OMOcaptcha module not available")
            if not omocaptcha_api_key:
                self.logger.warning("⚠️ [NATIVE-OMO] No API key provided")
    
    def _focus_chrome_window(self, title_keywords=("TikTok", "Chrome")) -> bool:
        if not WIN32_AVAILABLE:
            self.logger.info("[FOCUS] Win32 APIs unavailable; skipping window focus")
            return False
        target_hwnd = None
        def _enum_cb(hwnd, _):
            nonlocal target_hwnd
            try:
                if not win32gui.IsWindowVisible(hwnd):
                    return
                class_name = win32gui.GetClassName(hwnd)
                if class_name != "Chrome_WidgetWin_1":
                    return
                title = win32gui.GetWindowText(hwnd) or ""
                for kw in title_keywords:
                    if kw and kw.lower() in title.lower():
                        target_hwnd = hwnd
                        break
            except Exception:
                pass
        try:
            win32gui.EnumWindows(_enum_cb, None)
            if not target_hwnd:
                # Fallback: pick any visible Chrome window
                def _enum_any(hwnd, _):
                    nonlocal target_hwnd
                    try:
                        if win32gui.IsWindowVisible(hwnd) and win32gui.GetClassName(hwnd) == "Chrome_WidgetWin_1":
                            target_hwnd = hwnd
                    except Exception:
                        pass
                win32gui.EnumWindows(_enum_any, None)
            if target_hwnd:
                try:
                    # If window is off-screen (e.g., stealth-hidden mode), move it to visible area
                    try:
                        rect = win32gui.GetWindowRect(target_hwnd)
                        left, top, right, bottom = rect
                        width = max(400, right - left)
                        height = max(300, bottom - top)
                        if left < -100 or top < -100:
                            win32gui.MoveWindow(target_hwnd, 50, 50, width, height, True)
                            self.logger.info("[FOCUS] Moved off-screen Chrome window to (50,50)")
                    except Exception:
                        pass
                    win32gui.ShowWindow(target_hwnd, win32con.SW_RESTORE)
                    win32gui.SetForegroundWindow(target_hwnd)
                    self.logger.info(f"[FOCUS] Brought Chrome window to foreground: hwnd={target_hwnd}")
                    time.sleep(0.3)
                    return True
                except Exception as e:
                    self.logger.warning(f"[FOCUS] Failed to activate Chrome window: {e}")
            else:
                self.logger.warning("[FOCUS] No Chrome window found to focus")
        except Exception as e:
            self.logger.warning(f"[FOCUS] EnumWindows failed: {e}")
        return False

    def _get_active_chrome_client_rect(self):
        if not WIN32_AVAILABLE:
            return None
        try:
            hwnd = win32gui.GetForegroundWindow()
            if not hwnd:
                return None
            if win32gui.GetClassName(hwnd) != "Chrome_WidgetWin_1":
                return None
            # Get client rect in screen coordinates
            left, top, right, bottom = win32gui.GetClientRect(hwnd)
            # Convert client (0,0) to screen
            pt = win32gui.ClientToScreen(hwnd, (0, 0))
            cl = pt[0]
            ct = pt[1]
            cr = cl + (right - left)
            cb = ct + (bottom - top)
            return (cl, ct, cr, cb)
        except Exception:
            return None

    def capture_captcha_from_screen(self):
        """
        Chụp ảnh captcha từ màn hình (cropped to captcha area)
        
        Returns:
            Base64 string của ảnh captcha
        """
        try:
            self.logger.info("📸 [NATIVE-OMO] Capturing captcha from screen...")
            
            # Bắt buộc focus Chrome trước khi chụp
            self._focus_chrome_window()

            # Ưu tiên crop theo vùng client của cửa sổ Chrome (dialog nằm giữa)
            client_rect = self._get_active_chrome_client_rect()
            screenshot = pyautogui.screenshot()
            img = screenshot  # PIL Image

            # Kích thước dialog thường 312–380px, chọn rộng hơn để chắc chắn
            captcha_width = 380
            captcha_height = 260

            if client_rect:
                cl, ct, cr, cb = client_rect
                c_w = cr - cl
                c_h = cb - ct
                center_x = cl + c_w // 2
                center_y = ct + c_h // 2
                # Modal hơi lệch lên trên so với tâm một chút
                left = int(center_x - captcha_width / 2)
                top = int(center_y - captcha_height / 2 - 10)
                right = left + captcha_width
                bottom = top + captcha_height
                self.logger.info(f"📸 [NATIVE-OMO] Cropping by client rect: {left},{top} to {right},{bottom}")
            else:
                screen_width, screen_height = pyautogui.size()
                left = (screen_width - captcha_width) // 2
                top = (screen_height - captcha_height) // 2 - 10
                right = left + captcha_width
                bottom = top + captcha_height
                self.logger.info(f"📸 [NATIVE-OMO] Cropping by screen center: {left},{top} to {right},{bottom}")

            # Chặn ra ngoài màn hình
            left = max(0, left)
            top = max(0, top)
            right = min(img.width, right)
            bottom = min(img.height, bottom)

            img_cropped = img.crop((left, top, right, bottom))
            w, h = img_cropped.width, img_cropped.height
            
            # Convert to base64
            buffered = io.BytesIO()
            img_cropped.save(buffered, format="PNG")
            img_bytes = buffered.getvalue()
            base64_str = base64.b64encode(img_bytes).decode('utf-8')
            
            self.logger.info(f"📸 [NATIVE-OMO] Captured captcha crop {w}x{h} (base64 bytes: {len(base64_str)})")
            
            return base64_str, w, h
            
        except Exception as e:
            self.logger.error(f"❌ [NATIVE-OMO] Error capturing screenshot: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            
            # Fallback: chụp toàn màn hình nếu crop lỗi
            try:
                screenshot = pyautogui.screenshot()
                buffered = io.BytesIO()
                screenshot.save(buffered, format="PNG")
                img_bytes = buffered.getvalue()
                base64_str = base64.b64encode(img_bytes).decode('utf-8')
                self.logger.info(f"📸 [NATIVE-OMO] Fallback: Full screenshot (size: {len(base64_str)} bytes)")
                return base64_str, screenshot.width, screenshot.height
            except Exception as e2:
                self.logger.error(f"❌ [NATIVE-OMO] Fallback also failed: {e2}")
                return None

    def save_debug_images(self) -> dict:
        """
        Lưu nhiều biến thể ảnh (full + nhiều vùng crop) để người dùng xác nhận vùng captcha.
        
        Returns:
            dict mapping tên ảnh -> đường dẫn và toạ độ crop
        """
        try:
            out = {}
            base_dir = os.path.join("data", "logs", "captcha_debug")
            os.makedirs(base_dir, exist_ok=True)
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")

            shot = pyautogui.screenshot()
            full_path = os.path.join(base_dir, f"full_{ts}.png")
            shot.save(full_path)
            out["full"] = {"path": full_path}
            self.logger.info(f"🖼️ [DEBUG] Saved full screenshot: {full_path}")

            sw, sh = pyautogui.size()
            # Các vùng gợi ý: giữa, trên giữa, dưới giữa, trái giữa, phải giữa
            regions = {
                "center": (sw//2 - 200, sh//2 - 150, 400, 300),
                "upper_center": (sw//2 - 200, sh//3 - 150, 400, 300),
                "lower_center": (sw//2 - 200, int(sh*0.66) - 150, 400, 300),
                "left_center": (sw//4 - 200, sh//2 - 150, 400, 300),
                "right_center": (int(sw*0.75) - 200, sh//2 - 150, 400, 300),
            }

            # Thêm crop theo client rect của Chrome nếu có
            cr = self._get_active_chrome_client_rect()
            if cr:
                cl, ct, crx, cby = cr
                cw = crx - cl
                ch = cby - ct
                cx = cl + cw // 2
                cy = ct + ch // 2
                regions["client_center"] = (int(cx - 190), int(cy - 130 - 10), 380, 260)

            for name, (x, y, w, h) in regions.items():
                x = max(0, x); y = max(0, y)
                w = min(w, sw - x); h = min(h, sh - y)
                crop = shot.crop((x, y, x + w, y + h))
                p = os.path.join(base_dir, f"{name}_{w}x{h}_{ts}.png")
                crop.save(p)
                out[name] = {"path": p, "rect": [x, y, w, h]}
                self.logger.info(f"🖼️ [DEBUG] Saved {name} crop ({w}x{h}) at ({x},{y}): {p}")

            self.logger.info("🧭 [DEBUG] Please check which image contains the captcha (center/upper_center/lower_center/left_center/right_center/client_center).")
            return out
        except Exception as e:
            self.logger.error(f"❌ [DEBUG] Failed to save debug images: {e}")
            return {}
    
    def detect_captcha_type(self) -> str:
        """
        Phát hiện loại captcha từ màn hình
        
        Returns:
            Loại captcha ('slider', 'rotate', 'select_object', '3d_select_object')
        """
        try:
            # Chụp screenshot để phân tích
            screenshot = pyautogui.screenshot()
            
            # Convert to PIL Image
            img_array = screenshot
            
            # Kiểm tra các pattern thường gặp
            # TikTok thường dùng slider captcha
            
            # For now, default to slider (most common)
            return 'slider'
            
        except Exception as e:
            self.logger.error(f"❌ [NATIVE-OMO] Error detecting captcha type: {e}")
            return 'slider'  # Default
    
    def solve_slider_with_omocaptcha(self) -> bool:
        """
        Giải slider captcha bằng OMOcaptcha
        
        Returns:
            True nếu thành công
        """
        if not self.omocaptcha_client:
            self.logger.error("❌ [NATIVE-OMO] OMOcaptcha client not available")
            return False
        
        try:
            # 1. Chụp ảnh captcha
            self.logger.info("📸 [NATIVE-OMO] Step 1: Capturing captcha image...")
            cap = self.capture_captcha_from_screen()
            if not cap:
                self.logger.error("❌ [NATIVE-OMO] Failed to capture captcha")
                return False
            image_base64, width, height = cap
            self.logger.info(f"🔎 [NATIVE-OMO] Crop dims sent to OMO: {width}x{height}")
            
            # 2. Gửi lên OMOcaptcha với width/height khớp ảnh
            self.logger.info("🔗 [NATIVE-OMO] Step 2: Sending to OMOcaptcha API...")
            end = self.omocaptcha_client.solve_tiktok_slider(image_base64, width, height)
            
            if not end:
                self.logger.error("❌ [NATIVE-OMO] Failed to get solution")
                return False
            
            self.logger.info(f"✅ [NATIVE-OMO] Solution (end): {end}")
            
            # 4. Áp dụng solution
            x_pos = None
            if isinstance(end, dict) and 'x' in end:
                x_pos = end['x']
            elif isinstance(end, int):
                x_pos = end
            if x_pos is not None:
                self.logger.info(f"🖱️ [NATIVE-OMO] Step 4: Moving slider by {x_pos} pixels...")
                
                # Tìm vị trí slider trên màn hình
                screen_width, screen_height = pyautogui.size()
                # Nếu có client rect, đặt slider_y gần đáy client (modal thanh kéo nằm dưới ảnh)
                client_rect = self._get_active_chrome_client_rect()
                if client_rect:
                    cl, ct, cr, cb = client_rect
                    slider_x = (cl + cr) // 2
                    slider_y = cb - 90
                else:
                    slider_x = screen_width // 2
                    slider_y = screen_height - (screen_height // 3)
                
                self.logger.info(f"🖱️ [NATIVE-OMO] Slider position: x={slider_x}, y={slider_y}")
                
                # Click và kéo slider (kéo từ trái sang phải)
                pyautogui.moveTo(slider_x, slider_y)
                time.sleep(0.3)
                pyautogui.mouseDown()
                pyautogui.moveRel(x_pos, 0, duration=0.5)
                pyautogui.mouseUp()
                
                self.logger.info(f"✅ [NATIVE-OMO] Slider moved successfully by {x_pos} pixels!")
                time.sleep(2)  # Chờ captcha xử lý
                return True
            else:
                self.logger.error(f"❌ [NATIVE-OMO] Invalid solution format: {solution}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ [NATIVE-OMO] Error solving slider: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return False
    
    def solve_captcha(self) -> bool:
        """
        Giải captcha chính
        
        Returns:
            True nếu thành công
        """
        if not self.omocaptcha_client:
            self.logger.error("❌ [NATIVE-OMO] OMOcaptcha client not available")
            return False
        
        try:
            # Kiểm tra số dư trước khi giải
            balance = self.omocaptcha_client.get_balance()
            if balance is None:
                self.logger.warning("⚠️ [NATIVE-OMO] Could not fetch balance. Proceeding anyway.")
            else:
                self.logger.info(f"💰 [NATIVE-OMO] Balance: {balance}")
                if balance <= 0:
                    self.logger.error("❌ [NATIVE-OMO] Balance is zero. Please top up your OMOcaptcha account.")
                    return False

            # Phát hiện loại captcha
            captcha_type = self.detect_captcha_type()
            self.logger.info(f"🔍 [NATIVE-OMO] Detected captcha type: {captcha_type}")
            
            # Lưu ảnh debug để người dùng xác nhận
            self.save_debug_images()

            # Giải theo loại
            if captcha_type == 'slider':
                return self.solve_slider_with_omocaptcha()
            else:
                self.logger.warning(f"⚠️ [NATIVE-OMO] Unsupported captcha type: {captcha_type}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ [NATIVE-OMO] Error solving captcha: {e}")
            return False

