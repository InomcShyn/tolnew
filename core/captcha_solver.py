"""
Sử dụng OpenCV và computer vision để giải captcha TikTok
"""

import cv2
import numpy as np
import pyautogui
import base64
from PIL import Image, ImageEnhance, ImageFilter
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
import logging

class TikTokCaptchaSolver:
    def __init__(self, driver):
        self.driver = driver
        self.logger = logging.getLogger(__name__)
        
        # Template matching cho các loại captcha
        self.templates = {
            'rotate': self.load_rotate_templates(),
            'slide': self.load_slide_templates(),
            'click': self.load_click_templates()
        }
        
        self.setup_opencv()
        
    def setup_opencv(self):
        """Cấu hình OpenCV cho xử lý hình ảnh"""
        self.match_threshold = 0.8
        
    def load_rotate_templates(self):
        """Load các template cho captcha xoay"""
        templates = {}
        
        # Các template phổ biến cho captcha xoay TikTok
        common_objects = [
            'car', 'bike', 'bus', 'truck', 'motorcycle',
            'house', 'building', 'tree', 'flower',
            'traffic_light', 'crosswalk', 'bicycle', 'car',
            'person', 'dog', 'cat', 'bird', 'fish'
        ]
        
        for obj in common_objects:
            template_path = f"templates/rotate_{obj}.png"
            try:
                template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
                if template is not None:
                    templates[obj] = template
                else:
                    continue
            except:
                continue
                
        return templates
        
    def load_slide_templates(self):
        """Load các template cho captcha trượt"""
        templates = {}
        
        puzzle_pieces = ['piece_1', 'piece_2', 'piece_3', 'piece_4']
        
        for piece in puzzle_pieces:
            try:
                template_path = f"templates/slide_{piece}.png"
                template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
                if template is not None:
                    templates[piece] = template
                else:
                    continue
            except:
                continue
                
        return templates
        
    def load_click_templates(self):
        """Load các template cho captcha click"""
        templates = {}
        
        # Template cho các đối tượng cần click
        click_objects = [
            'traffic_light', 'crosswalk', 'bicycle', 'car',
            'house', 'building', 'tree', 'flower',
            'person', 'dog', 'cat', 'bird', 'fish'
        ]
        
        for obj in click_objects:
            try:
                template_path = f"templates/click_{obj}.png"
                template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
                if template is not None:
                    templates[obj] = template
                else:
                    continue
            except:
                continue
                
        return templates
        
    def detect_captcha_type(self, driver):
        """Phát hiện loại captcha từ screenshot"""
        try:
            # Chuyển đổi screenshot thành OpenCV format
            screenshot = driver.get_screenshot_as_png()
            img = self.screenshot_to_cv2(screenshot)
            
            captcha_type = None
            confidence = 0.0
            
            # Kiểm tra từng loại captcha
            rotate_confidence = self.detect_rotate_captcha(img)
            if rotate_confidence > 0.7:
                captcha_type = 'rotate'
                confidence = rotate_confidence
            else:
                slide_confidence = self.detect_slide_captcha(img)
                if slide_confidence > 0.7:
                    captcha_type = 'slide'
                    confidence = slide_confidence
                else:
                    click_confidence = self.detect_click_captcha(img)
                    if click_confidence > 0.7:
                        captcha_type = 'click'
                        confidence = click_confidence
            
            return captcha_type, confidence
            
        except Exception as e:
            self.logger.error(f"Error detecting captcha type: {e}")
            return None, 0
            
    def detect_rotate_captcha(self, img):
        """Phát hiện captcha xoay"""
        try:
            rotate_keywords = [
                'rotate', 'turn', 'spin', 'xoay', 'quay',
                'drag to rotate', 'drag to turn'
            ]
            
            text_found = self.extract_text_from_image(img)
            
            for keyword in rotate_keywords:
                if keyword.lower() in text_found.lower():
                    return 0.9
                    
            # Kiểm tra UI elements đặc trưng của rotate
            if self.has_rotation_ui_elements(img):
                return 0.8
                
            return 0.0
            
        except Exception as e:
            self.logger.error(f"Error detecting rotate captcha: {e}")
            return 0.0
            
    def has_rotation_ui_elements(self, img):
        """Kiểm tra có UI elements của captcha xoay không"""
        try:
            # 1. Nút xoay (rotate button)
            # 2. Cursor thay đổi khi hover
            # 3. Sử dụng template matching để tìm rotate button
            rotate_button_template = None
            if rotate_button_template is not None:
                result = cv2.matchTemplate(img, rotate_button_template, cv2.TM_CCOEFF_NORMED)
                if np.max(result) > 0.7:
                    return True
                    
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking rotation UI elements: {e}")
            return False
            
    def detect_slide_captcha(self, img):
        """Phát hiện captcha trượt"""
        try:
            slide_keywords = [
                'slide', 'drag', 'move', 'trượt', 'kéo',
                'drag to slide', 'move the slider'
            ]
            
            # Tìm kiếm slider element
            for keyword in slide_keywords:
                if keyword.lower() in self.extract_text_from_image(img).lower():
                    return 0.9
                    
            # Kiểm tra UI elements đặc trưng của slider
            if self.has_slider_ui_elements(img):
                return 0.8
                
            return 0.0
            
        except Exception as e:
            self.logger.error(f"Error detecting slide captcha: {e}")
            return 0.0
            
    def has_slider_ui_elements(self, img):
        """Kiểm tra có UI elements của captcha trượt không"""
        try:
            # Tìm kiếm slider track và handle
            slider_template = None
            if slider_template is not None:
                result = cv2.matchTemplate(img, slider_template, cv2.TM_CCOEFF_NORMED)
                if np.max(result) > 0.7:
                    return True
                    
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking slider UI elements: {e}")
            return False
            
    def detect_click_captcha(self, img):
        """Phát hiện captcha click"""
        try:
            click_keywords = [
                'click', 'select', 'choose', 'chọn', 'nhấn',
                'click all', 'select all', 'chọn tất cả'
            ]
            
            for keyword in click_keywords:
                if keyword.lower() in self.extract_text_from_image(img).lower():
                    return 0.9
                    
            # Kiểm tra grid layout đặc trưng của click captcha
            if self.has_click_grid_layout(img):
                return 0.8
                
            return 0.0
            
        except Exception as e:
            self.logger.error(f"Error detecting click captcha: {e}")
            return 0.0
            
    def has_click_grid_layout(self, img):
        """Kiểm tra có layout grid của captcha click không"""
        try:
            # Tìm kiếm grid pattern (3x3, 2x4, etc.)
            edges = cv2.Canny(img, 50, 150)
            
            # Sử dụng Hough Transform để tìm đường thẳng
            lines = cv2.HoughLines(edges, 1, np.pi/180, threshold=100)
            
            if lines is not None and len(lines) > 4:
                return True
                
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking click grid layout: {e}")
            return False
            
    def extract_text_from_image(self, img):
        """Trích xuất text từ hình ảnh sử dụng OCR"""
        try:
            import pytesseract
            
            # Preprocessing image để cải thiện OCR
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            processed = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
            
            # OCR
            text = pytesseract.image_to_string(processed, config='--psm 6')
            return text
            
        except ImportError:
            self.logger.warning("pytesseract not available, using basic text detection")
            return ""
        except Exception as e:
            self.logger.error(f"Error extracting text: {e}")
            return ""
    
    def solve_rotate_captcha(self, driver):
        """Giải captcha xoay"""
        try:
            self.logger.info("Solving rotate captcha...")
            
            # 1. Lấy screenshot của captcha
            screenshot = driver.get_screenshot_as_png()
            img = self.screenshot_to_cv2(screenshot)
            
            # 2. Tìm đối tượng cần xoay
            target_object = self.find_rotate_target(img)
            if target_object is None:
                self.logger.error("Could not find target object to rotate")
                return False
            
            # 3. Tính toán góc xoay cần thiết
            rotation_angle = self.calculate_rotation_angle(img, target_object)
            if rotation_angle is None:
                self.logger.error("Could not calculate rotation angle")
                return False
            
            # 4. Thực hiện xoay
            success = self.perform_rotation(driver, rotation_angle)
            
            if success:
                self.logger.info(f"Successfully rotated by {rotation_angle} degrees")
                time.sleep(1)  # Chờ captcha xử lý
                return True
            else:
                self.logger.error("Failed to perform rotation")
                return False
            
        except Exception as e:
            self.logger.error(f"Error solving rotate captcha: {e}")
            return False
    
    def find_rotate_target(self, img):
        """Tìm đối tượng cần xoay trong hình ảnh"""
        try:
            # Sử dụng template matching để tìm đối tượng
            best_match = None
            best_score = 0
            
            for obj_name, template in self.templates['rotate'].items():
                result = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                
                if max_val > best_score and max_val > self.match_threshold:
                    best_score = max_val
                    best_match = {
                        'name': obj_name,
                        'template': template,
                        'location': max_loc,
                        'score': max_val
                    }
            
            return best_match
            
        except Exception as e:
            self.logger.error(f"Error finding rotate target: {e}")
            return None
            
    def calculate_rotation_angle(self, img, target_object):
        """Tính toán góc xoay cần thiết"""
        try:
            # Sử dụng Hough Transform để tìm đường thẳng
            edges = cv2.Canny(img, 50, 150)
            lines = cv2.HoughLines(edges, 1, np.pi/180, threshold=100)
            
            if lines is not None:
                # Tính toán góc trung bình
                angles = []
                for line in lines:
                    rho, theta = line[0]
                    angle = theta * 180 / np.pi
                    angles.append(angle)
                
                if angles:
                    avg_angle = np.mean(angles)
                    # Tính góc cần xoay để đưa về 0 độ
                    rotation_angle = -avg_angle
                    return rotation_angle
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error calculating rotation angle: {e}")
            return None
            
    def perform_rotation(self, driver, angle):
        """Thực hiện xoay đối tượng"""
        try:
            # Sử dụng ActionChains để drag và xoay
            actions = ActionChains(driver)
            
            # Tìm element cần xoay
            rotate_element = driver.find_element("css selector", "[data-testid='rotate-button']")
            
            # Thực hiện drag rotation
            self.drag_rotation(driver, rotate_element, angle)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error performing rotation: {e}")
            return False
            
    def drag_rotation(self, driver, element, angle):
        """Thực hiện drag rotation"""
        try:
            # Tính toán vị trí bắt đầu và kết thúc
            location = element.location
            size = element.size
            
            start_x = location['x'] + size['width'] // 2
            start_y = location['y'] + size['height'] // 2
            
            # Tính toán vị trí kết thúc dựa trên góc
            end_x = start_x + int(50 * np.cos(np.radians(angle)))
            end_y = start_y + int(50 * np.sin(np.radians(angle)))
            
            # Thực hiện drag
            actions = ActionChains(driver)
            actions.move_to_element_with_offset(element, start_x - location['x'], start_y - location['y'])
            actions.click_and_hold()
            actions.move_by_offset(end_x - start_x, end_y - start_y)
            actions.release()
            actions.perform()
            
            self.logger.info(f"Performed drag rotation: {angle} degrees")
            return True
            
        except Exception as e:
            self.logger.error(f"Error in drag rotation: {e}")
            return False
    
    def solve_slide_captcha(self, driver):
        """Giải captcha trượt"""
        try:
            self.logger.info("Solving slide captcha...")
            
            # Tìm slider element
            slider = self.find_slider_element(driver)
            if slider is None:
                self.logger.error("Could not find slider element")
                return False
            
            # Tính toán khoảng cách cần trượt
            distance = self.calculate_slide_distance(driver, slider)
            if distance is None:
                self.logger.error("Could not calculate slide distance")
                return False
            
            # Thực hiện trượt
            success = self.perform_slide(driver, slider, distance)
            
            if success:
                self.logger.info(f"Successfully slid by {distance} pixels")
                time.sleep(1)  # Chờ captcha xử lý
                return True
            else:
                self.logger.error("Failed to perform slide")
                return False
                
        except Exception as e:
            self.logger.error(f"Error solving slide captcha: {e}")
            return False
            
    def find_slider_element(self, driver):
        """Tìm slider element"""
        try:
            # Tìm kiếm slider bằng các selector khác nhau
            selectors = [
                "[data-testid='slider']",
                ".slider",
                "[role='slider']",
                ".captcha-slider"
            ]
            
            for selector in selectors:
                try:
                    element = driver.find_element("css selector", selector)
                    if element.is_displayed():
                        return element
                except:
                    continue
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error finding slider element: {e}")
            return None
            
    def calculate_slide_distance(self, driver, slider):
        """Tính toán khoảng cách cần trượt"""
        try:
            # Lấy screenshot để phân tích
            screenshot = driver.get_screenshot_as_png()
            img = self.screenshot_to_cv2(screenshot)
            
            # Tìm gap trong puzzle
            gap_position = self.find_slide_gap(img)
            if gap_position is None:
                return None
            
            # Tính toán khoảng cách từ slider đến gap
            slider_location = slider.location
            slider_size = slider.size
            
            slider_center_x = slider_location['x'] + slider_size['width'] // 2
            distance = gap_position - slider_center_x
            
            return distance
            
        except Exception as e:
            self.logger.error(f"Error calculating slide distance: {e}")
            return None
            
    def find_slide_gap(self, img):
        """Tìm gap trong puzzle"""
        try:
            # Sử dụng edge detection để tìm gap
            edges = cv2.Canny(img, 50, 150)
            
            # Tìm kiếm đường thẳng dọc
            lines = cv2.HoughLines(edges, 1, np.pi/180, threshold=100)
            
            if lines is not None:
                # Tìm đường thẳng dọc (gần 90 độ)
                vertical_lines = []
                for line in lines:
                    rho, theta = line[0]
                    angle = theta * 180 / np.pi
                    if 80 < angle < 100:  # Gần 90 độ
                        vertical_lines.append(rho)
                
                if vertical_lines:
                    # Trả về vị trí trung bình của các đường thẳng dọc
                    return int(np.mean(vertical_lines))
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error finding slide gap: {e}")
            return None
            
    def perform_slide(self, driver, slider, distance):
        """Thực hiện trượt slider"""
        try:
            actions = ActionChains(driver)
            actions.move_to_element(slider)
            actions.click_and_hold()
            actions.move_by_offset(distance, 0)
            actions.release()
            actions.perform()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error performing slide: {e}")
            return False
    
    def solve_click_captcha(self, driver):
        """Giải captcha click"""
        try:
            self.logger.info("Solving click captcha...")
            
            # Lấy screenshot để phân tích
            screenshot = driver.get_screenshot_as_png()
            img = self.screenshot_to_cv2(screenshot)
            
            # Tìm các đối tượng cần click
            click_targets = self.find_click_targets(img)
            if not click_targets:
                self.logger.error("Could not find click targets")
                return False
            
            # Thực hiện click
            success = self.perform_clicks(driver, click_targets)
            
            if success:
                self.logger.info(f"Successfully clicked {len(click_targets)} targets")
                time.sleep(1)
                return True
            else:
                self.logger.error("Failed to perform clicks")
                return False
                
        except Exception as e:
            self.logger.error(f"Error solving click captcha: {e}")
            return False
    
    def find_click_targets(self, img):
        """Tìm các đối tượng cần click"""
        try:
            click_targets = []
            
            # Sử dụng template matching để tìm các đối tượng
            for obj_name, template in self.templates['click'].items():
                result = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
                locations = np.where(result >= self.match_threshold)
                
                for pt in zip(*locations[::-1]):
                    click_targets.append({
                        'name': obj_name,
                        'position': pt,
                        'confidence': result[pt[1], pt[0]]
                    })
            
            return click_targets
            
        except Exception as e:
            self.logger.error(f"Error finding click targets: {e}")
            return []
            
    def perform_clicks(self, driver, targets):
        """Thực hiện click các đối tượng"""
        try:
            for target in targets:
                # Tìm element tương ứng với vị trí
                element = driver.find_element("css selector", f"[data-testid='{target['name']}']")
                
                # Click vào element
                actions = ActionChains(driver)
                actions.move_to_element(element)
                actions.click()
                actions.perform()
                
                time.sleep(0.5)  # Chờ giữa các click
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error performing clicks: {e}")
            return False
            
    def screenshot_to_cv2(self, screenshot):
        """Chuyển đổi screenshot thành OpenCV format"""
        try:
            # Chuyển đổi từ base64 sang numpy array
            img_array = np.frombuffer(screenshot, np.uint8)
            img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            return img
            
        except Exception as e:
            self.logger.error(f"Error converting screenshot: {e}")
            return None
            
    def solve_captcha(self, driver):
        """Giải captcha chính"""
        try:
            # Phát hiện loại captcha
            captcha_type, confidence = self.detect_captcha_type(driver)
            
            if captcha_type is None:
                self.logger.warning("Could not detect captcha type")
                return False
            
            self.logger.info(f"Detected {captcha_type} captcha with confidence {confidence}")
            
            # Giải captcha theo loại
            if captcha_type == 'rotate':
                return self.solve_rotate_captcha(driver)
            elif captcha_type == 'slide':
                return self.solve_slide_captcha(driver)
            elif captcha_type == 'click':
                return self.solve_click_captcha(driver)
            else:
                self.logger.warning(f"Unknown captcha type: {captcha_type}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error solving captcha: {e}")
            return False