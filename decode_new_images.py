#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Decode images from new HTML
"""

import re
import base64

html_file = r"logs\captcha_artifacts_v2\P-641043-0138\captcha_html_20251205_073953.html"

with open(html_file, 'r', encoding='utf-8') as f:
    html = f.read()

# Extract all base64 images
pattern = r'data:image/[^;]+;base64,([A-Za-z0-9+/=]+)'
matches = re.findall(pattern, html)

print(f"Found {len(matches)} images")

# Remove duplicates
unique_images = list(set(matches))
print(f"Unique images: {len(unique_images)}")

for i, img_data in enumerate(unique_images):
    print(f"\nImage {i+1}: {len(img_data)} chars")
    
    # Decode and save
    try:
        img_bytes = base64.b64decode(img_data)
        
        # Detect format from magic bytes
        if img_bytes[:4] == b'\x89PNG':
            ext = 'png'
        elif img_bytes[:2] == b'\xff\xd8':
            ext = 'jpg'
        elif img_bytes[:4] == b'RIFF':
            ext = 'webp'
        else:
            ext = 'bin'
        
        filename = f"captcha_new_{i+1}.{ext}"
        with open(filename, 'wb') as f:
            f.write(img_bytes)
        
        print(f"  ✅ Saved to: {filename}")
        print(f"  Format: {ext.upper()}")
        print(f"  Size: {len(img_bytes)} bytes")
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
