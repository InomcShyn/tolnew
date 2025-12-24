#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TikTok Captcha HTML Parser
Trích xuất và phân loại captcha từ HTML, tạo request body cho OmoCaptcha API

Hỗ trợ 4 loại captcha:
1. TikTokSliderWebTask - Slider puzzle
2. TikTokRotateWebTask - Rotate image
3. TikTokSelectObjectWebTask - Select object
4. TikTok3DSelectObjectWebTask - 3D select object
"""

import re
import json
from typing import List, Dict, Optional, Tuple


def extract_base64_images(html: str) -> List[str]:
    """
    Trích xuất tất cả ảnh base64 từ HTML
    
    Args:
        html: HTML string chứa captcha
        
    Returns:
        List các base64 image strings (không có prefix data:image/...)
    """
    print("[DEBUG] [extract_base64_images] START")
    print(f"[DEBUG] HTML length: {len(html)} characters")
    
    # Pattern để tìm base64 images
    # PRIORITY 1: WEBP images (TikTok captcha format)
    # PRIORITY 2: Other formats (PNG, JPEG) - fallback
    
    # Try WEBP first (most common for TikTok captcha)
    webp_patterns = [
        r'src="data:image/webp;base64,([^"]+)"',
        r"src='data:image/webp;base64,([^']+)'",
        r'data:image/webp;base64,([A-Za-z0-9+/=]+)',
    ]
    
    matches = []
    for pattern in webp_patterns:
        found = re.findall(pattern, html)
        if found:
            matches.extend(found)
            print(f"[DEBUG] WEBP pattern found {len(found)} images")
    
    # If no WEBP found, try other formats
    if not matches:
        print("[DEBUG] No WEBP images, trying other formats...")
        other_patterns = [
            r'src="data:image/[^;]+;base64,([^"]+)"',      # Double quotes
            r"src='data:image/[^;]+;base64,([^']+)'",      # Single quotes
            r'data:image/[^;]+;base64,([A-Za-z0-9+/=]+)',  # Any data:image
        ]
        
        for pattern in other_patterns:
            found = re.findall(pattern, html)
            if found:
                matches.extend(found)
                print(f"[DEBUG] Other format pattern found {len(found)} images")
    
    # Remove duplicates
    matches = list(set(matches))
    print(f"[DEBUG] Found {len(matches)} unique base64 images in HTML")
    
    # Log first 100 chars of each image
    for i, img in enumerate(matches):
        print(f"[DEBUG] Image {i+1}: {len(img)} chars, preview: {img[:100]}...")
    
    # Lọc bỏ các base64 quá ngắn (có thể là icon)
    # Giảm threshold từ 1000 → 500 để không bỏ sót ảnh rotate nhỏ
    images = [img for img in matches if len(img) > 500]
    print(f"[DEBUG] After filtering (>500 chars): {len(images)} images")
    
    if not images:
        print("[DEBUG] ❌ No valid base64 images found!")
        # Try to find any data:image in HTML
        all_data_images = re.findall(r'data:image/[^"]+', html)
        print(f"[DEBUG] Total data:image found: {len(all_data_images)}")
        for i, img in enumerate(all_data_images[:3]):
            print(f"[DEBUG] data:image {i+1}: {img[:200]}...")
    
    return images


def extract_dimensions(html: str) -> Tuple[int, int]:
    """
    Trích xuất kích thước captcha từ HTML
    
    Args:
        html: HTML string
        
    Returns:
        Tuple (width, height)
    """
    # Tìm width và height từ style hoặc class
    # TikTok thường dùng: cap-h-[170px] sm:cap-h-[210px]
    
    # Try to find height
    height_match = re.search(r'cap-h-\[(\d+)px\]', html)
    if height_match:
        height = int(height_match.group(1))
    else:
        # Default height cho TikTok
        height = 212
    
    # Width thường là 340px cho TikTok
    width = 340
    
    return width, height


def extract_question(html: str) -> Optional[str]:
    """
    Trích xuất câu hỏi từ HTML (cho select object captcha)
    
    Args:
        html: HTML string
        
    Returns:
        Question string hoặc None
    """
    # Tìm text có dạng "Which of these..." hoặc "Select..."
    patterns = [
        r'<span[^>]*>(Which of these[^<]+)</span>',
        r'<span[^>]*>(Select[^<]+)</span>',
        r'<span[^>]*>(Choose[^<]+)</span>',
        r'<div[^>]*>(Which of these[^<]+)</div>',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, html, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    
    return None


def detect_captcha_type(html: str, images: List[str]) -> str:
    """
    Phát hiện loại captcha dựa trên HTML và số lượng ảnh
    
    Args:
        html: HTML string
        images: List base64 images
        
    Returns:
        Captcha type: 'slider', 'rotate', 'select', '3d'
    """
    print("[DEBUG] [detect_captcha_type] START")
    num_images = len(images)
    print(f"[DEBUG] Number of images: {num_images}")
    
    # Check image sizes
    image_sizes = [len(img) for img in images]
    print(f"[DEBUG] Image sizes: {image_sizes}")
    
    # Check for keywords - STRICT matching only
    has_secsdk_drag = 'secsdk-captcha-drag' in html
    has_drag_text = 'Drag the slider' in html
    has_slider_keyword = has_secsdk_drag or has_drag_text
    has_rotate_keyword = 'rotate' in html.lower()
    has_3d_keyword = '3d' in html.lower() or '3D' in html
    
    print(f"[DEBUG] Keywords found:")
    print(f"  - secsdk-captcha-drag: {has_secsdk_drag}")
    print(f"  - 'Drag the slider': {has_drag_text}")
    print(f"  - slider (combined): {has_slider_keyword}")
    print(f"  - rotate: {has_rotate_keyword}")
    print(f"  - 3d: {has_3d_keyword}")
    
    # CRITICAL FIX: Prioritize image-based detection OVER keyword detection
    # TikTok's rotate captcha ALSO has secsdk-captcha-drag-icon because it uses a slider!
    # So we MUST check for 2 images + no question FIRST, before checking keywords
    
    # Check if we have exactly 2 images and no question → ROTATE
    if num_images == 2:
        question = extract_question(html)
        if not question:
            print("[DEBUG] ✅ Detected as ROTATE (2 images + no question, ignoring slider keyword)")
            return 'rotate'
    
    # TYPE 1: SLIDER
    # - Có slider button (secsdk-captcha-drag-icon)
    # - Có 1 ảnh lớn hoặc 2 ảnh (1 lớn + 1 nhỏ)
    # - Text "Drag the slider"
    # Only detect as slider if we have the keyword AND it's NOT 2 images
    if has_slider_keyword and num_images != 2:
        print("[DEBUG] ✅ Detected as SLIDER (has slider keyword + not 2 images)")
        return 'slider'
    
    # TYPE 2: ROTATE - Already handled above, this is just a fallback comment
    # (The main detection is at the top now)
    
    # TYPE 3: SELECT OBJECT
    # - Có question text
    # - Có 1 ảnh chính
    # - Text dạng "Which of these..." hoặc "Select..."
    question = extract_question(html)
    print(f"[DEBUG] Question found: {question}")
    
    if question:
        # Check if it's 3D or normal select
        if has_3d_keyword:
            print("[DEBUG] ✅ Detected as 3D SELECT (has question + 3D keyword)")
            return '3d'
        else:
            print("[DEBUG] ✅ Detected as SELECT (has question)")
            return 'select'
    
    # TYPE 4: 3D SELECT
    # - Có 1 ảnh
    # - Không có question
    # - Có indicator về 3D (class, id, hoặc texture)
    if num_images == 1:
        if has_3d_keyword or 'texture' in html.lower():
            print("[DEBUG] ✅ Detected as 3D SELECT (1 image + 3D keyword)")
            return '3d'
    
    # Default: nếu có 2 ảnh (bất kể size) và không có question thì là rotate
    if num_images == 2:
        question = extract_question(html)
        if not question:
            print("[DEBUG] ⚠️ Defaulting to ROTATE (2 images, no question)")
            return 'rotate'
    
    # Default: nếu có 2 ảnh nhỏ thì là rotate
    if num_images == 2 and all(size < 5000 for size in image_sizes):
        print("[DEBUG] ⚠️ Defaulting to ROTATE (2 small images)")
        return 'rotate'
    
    # Default: nếu có slider UI thì là slider
    if num_images >= 1:
        print("[DEBUG] ⚠️ Defaulting to SLIDER (has images)")
        return 'slider'
    
    # Fallback
    print("[DEBUG] ⚠️ Fallback to SLIDER")
    return 'slider'


def build_omocaptcha_body(
    captcha_type: str,
    images: List[str],
    api_key: str,
    width: int = 340,
    height: int = 212,
    question: Optional[str] = None
) -> Dict:
    """
    Tạo request body cho OmoCaptcha API theo đúng format
    
    Args:
        captcha_type: 'slider', 'rotate', 'select', '3d'
        images: List base64 images (không có prefix)
        api_key: OmoCaptcha API key
        width: Width của captcha
        height: Height của captcha
        question: Question text (cho select object)
        
    Returns:
        Dict request body sẵn sàng POST
    """
    print("[DEBUG] [build_omocaptcha_body] START")
    print(f"[DEBUG] Captcha type: {captcha_type}")
    print(f"[DEBUG] Number of images: {len(images)}")
    print(f"[DEBUG] Dimensions: {width}x{height}")
    print(f"[DEBUG] Question: {question}")
    print(f"[DEBUG] API key: {api_key[:10]}...{api_key[-10:]}")
    
    if captcha_type == 'slider':
        # TYPE 1: TikTokSliderWebTask
        # Chỉ cần 1 ảnh (ảnh puzzle gộp)
        # Nếu có nhiều ảnh, chọn ảnh lớn nhất (bỏ qua icon nhỏ)
        if len(images) > 1:
            # Sort by size descending and take the largest
            sorted_images = sorted(images, key=len, reverse=True)
            image_base64 = sorted_images[0]
            print(f"[DEBUG] Multiple images found, using largest: {len(image_base64)} chars")
        else:
            image_base64 = images[0] if images else ""
            print(f"[DEBUG] Using image 1: {len(image_base64)} chars")
        
        body = {
            "clientKey": api_key,
            "task": {
                "type": "TiktokSliderWebTask",
                "imageBase64": image_base64,
                "widthView": width
            }
        }
        print(f"[DEBUG] ✅ Created TiktokSliderWebTask body")
        return body
    
    elif captcha_type == 'rotate':
        # TYPE 2: TikTokRotateWebTask
        # Cần 2 ảnh: inside và outside
        if len(images) >= 2:
            image_base64s = [images[0], images[1]]
            print(f"[DEBUG] Using 2 images: {len(images[0])} + {len(images[1])} chars")
        elif len(images) == 1:
            # Nếu chỉ có 1 ảnh, dùng ảnh đó cho cả 2
            image_base64s = [images[0], images[0]]
            print(f"[DEBUG] Using 1 image for both: {len(images[0])} chars")
        else:
            image_base64s = ["", ""]
            print(f"[DEBUG] ⚠️ No images available!")
        
        body = {
            "clientKey": api_key,
            "task": {
                "type": "TiktokRotateWebTask",
                "imageBase64s": image_base64s
            }
        }
        print(f"[DEBUG] ✅ Created TiktokRotateWebTask body")
        return body
    
    elif captcha_type == 'select':
        # TYPE 3: TikTokSelectObjectWebTask
        task = {
            "type": "TiktokSelectObjectWebTask",
            "imageBase64": images[0] if images else "",
            "widthView": width,
            "heightView": height
        }
        
        # Thêm question nếu có
        if question:
            task["question"] = question
        
        return {
            "clientKey": api_key,
            "task": task
        }
    
    elif captcha_type == '3d':
        # TYPE 4: TikTok3DSelectObjectWebTask
        return {
            "clientKey": api_key,
            "task": {
                "type": "Tiktok3DSelectObjectWebTask",
                "imageBase64": images[0] if images else "",
                "widthView": width,
                "heightView": height
            }
        }
    
    else:
        # Default: slider
        return {
            "clientKey": api_key,
            "task": {
                "type": "TiktokSliderWebTask",
                "imageBase64": images[0] if images else "",
                "widthView": width
            }
        }


def solve_captcha_from_html(html: str, api_key: str) -> Dict:
    """
    Hàm chính: Xử lý toàn bộ logic từ HTML → JSON body
    
    Args:
        html: HTML string chứa captcha
        api_key: OmoCaptcha API key
        
    Returns:
        Dict request body sẵn sàng POST đến https://api.omocaptcha.com/v2/createTask
    """
    print("\n" + "="*70)
    print("[DEBUG] [solve_captcha_from_html] START")
    print("="*70)
    
    # Bước 1: Trích xuất base64 images
    print("\n[DEBUG] STEP 1: Extract base64 images")
    images = extract_base64_images(html)
    
    if not images:
        print("[DEBUG] ❌ ERROR: Không tìm thấy ảnh base64 trong HTML")
        raise ValueError("Không tìm thấy ảnh base64 trong HTML")
    
    print(f"[DEBUG] ✅ Found {len(images)} images")
    
    # Bước 2: Trích xuất dimensions
    print("\n[DEBUG] STEP 2: Extract dimensions")
    width, height = extract_dimensions(html)
    print(f"[DEBUG] ✅ Dimensions: {width}x{height}")
    
    # Bước 3: Trích xuất question (nếu có)
    print("\n[DEBUG] STEP 3: Extract question")
    question = extract_question(html)
    if question:
        print(f"[DEBUG] ✅ Question: {question}")
    else:
        print(f"[DEBUG] No question found")
    
    # Bước 4: Phát hiện loại captcha
    print("\n[DEBUG] STEP 4: Detect captcha type")
    captcha_type = detect_captcha_type(html, images)
    print(f"[DEBUG] ✅ Captcha type: {captcha_type}")
    
    # Bước 5: Tạo request body
    print("\n[DEBUG] STEP 5: Build request body")
    body = build_omocaptcha_body(
        captcha_type=captcha_type,
        images=images,
        api_key=api_key,
        width=width,
        height=height,
        question=question
    )
    
    print("\n[DEBUG] ✅ Request body created successfully")
    print(f"[DEBUG] Task type: {body['task']['type']}")
    print(f"[DEBUG] Task keys: {list(body['task'].keys())}")
    print("="*70 + "\n")
    
    return body


# ============================================================================
# TEST CASES
# ============================================================================

def test_slider_captcha():
    """Test case 1: Slider captcha"""
    html = '''
    <div class="TUXModal captcha-verify-container">
        <span>Drag the slider to fit the puzzle</span>
        <img src="data:image/webp;base64,UklGRowPAABXRUJQVlA4IIAPAADQggCdASpbAVsBP..." alt="Captcha" class="cap-h-[170px] sm:cap-h-[210px]">
        <button class="secsdk-captcha-drag-icon" id="captcha_slide_button"></button>
    </div>
    '''
    
    api_key = "test_api_key"
    result = solve_captcha_from_html(html, api_key)
    
    print("="*70)
    print("TEST 1: SLIDER CAPTCHA")
    print("="*70)
    print(json.dumps(result, indent=2))
    print()
    
    # Verify
    assert result["task"]["type"] == "TiktokSliderWebTask"
    assert "imageBase64" in result["task"]
    assert "widthView" in result["task"]
    print("✅ PASS: Slider captcha")


def test_rotate_captcha():
    """Test case 2: Rotate captcha"""
    html = '''
    <div class="captcha-container">
        <img src="data:image/webp;base64,UklGRowPAABXRUJQVlA4IIAPAADQggCdASpbAVsBP..." alt="Inside">
        <img src="data:image/webp;base64,UklGRvIHAABXRUJQVlA4IOYHAADQPwCdASrTANMAPw..." alt="Outside">
    </div>
    '''
    
    api_key = "test_api_key"
    result = solve_captcha_from_html(html, api_key)
    
    print("="*70)
    print("TEST 2: ROTATE CAPTCHA")
    print("="*70)
    print(json.dumps(result, indent=2))
    print()
    
    # Verify
    assert result["task"]["type"] == "TiktokRotateWebTask"
    assert "imageBase64s" in result["task"]
    assert len(result["task"]["imageBase64s"]) == 2
    print("✅ PASS: Rotate captcha")


def test_select_object_captcha():
    """Test case 3: Select object captcha"""
    html = '''
    <div class="captcha-container">
        <span>Which of these objects is a cat?</span>
        <img src="data:image/webp;base64,UklGRowPAABXRUJQVlA4IIAPAADQggCdASpbAVsBP..." alt="Captcha">
    </div>
    '''
    
    api_key = "test_api_key"
    result = solve_captcha_from_html(html, api_key)
    
    print("="*70)
    print("TEST 3: SELECT OBJECT CAPTCHA")
    print("="*70)
    print(json.dumps(result, indent=2))
    print()
    
    # Verify
    assert result["task"]["type"] == "TiktokSelectObjectWebTask"
    assert "imageBase64" in result["task"]
    assert "widthView" in result["task"]
    assert "heightView" in result["task"]
    assert "question" in result["task"]
    print("✅ PASS: Select object captcha")


def test_3d_select_captcha():
    """Test case 4: 3D select object captcha"""
    html = '''
    <div class="captcha-container 3d-captcha">
        <img src="data:image/webp;base64,UklGRowPAABXRUJQVlA4IIAPAADQggCdASpbAVsBP..." alt="Captcha">
    </div>
    '''
    
    api_key = "test_api_key"
    result = solve_captcha_from_html(html, api_key)
    
    print("="*70)
    print("TEST 4: 3D SELECT OBJECT CAPTCHA")
    print("="*70)
    print(json.dumps(result, indent=2))
    print()
    
    # Verify
    assert result["task"]["type"] == "Tiktok3DSelectObjectWebTask"
    assert "imageBase64" in result["task"]
    assert "widthView" in result["task"]
    assert "heightView" in result["task"]
    print("✅ PASS: 3D select object captcha")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("TIKTOK CAPTCHA HTML PARSER - TEST SUITE")
    print("="*70)
    print()
    
    # Run all tests
    test_slider_captcha()
    test_rotate_captcha()
    test_select_object_captcha()
    test_3d_select_captcha()
    
    print("="*70)
    print("ALL TESTS PASSED ✅")
    print("="*70)
