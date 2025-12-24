#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Collect Baseline Simple - Thu thập baseline từ Chrome đang chạy

CÁCH DÙNG ĐƠN GIẢN:
1. Mở Chrome thủ công (launcher.py hoặc bất kỳ cách nào)
2. Vào TikTok LIVE và đảm bảo video đang chạy
3. Chạy script này
4. Nhập profile ID
5. Baseline sẽ được thu thập

KHÔNG CẦN: Playwright, browser_manager, hay bất kỳ setup phức tạp nào
CHỈ CẦN: Chrome đang chạy và đang xem LIVE
"""

print("""
╔══════════════════════════════════════════════════════════════════╗
║                  COLLECT BASELINE - SIMPLE                       ║
╚══════════════════════════════════════════════════════════════════╝

Hướng dẫn:
1. Mở Chrome thủ công (launcher.py)
2. Vào TikTok LIVE
3. Đảm bảo video đang chạy
4. Chạy script này

""")

print("⚠️  LƯU Ý: Script này chỉ hướng dẫn, không tự động thu thập")
print("    Vì cần Chrome đang chạy với đúng version và profile\n")

print("="*70)
print("HƯỚNG DẪN THU THẬP BASELINE")
print("="*70)

print("""
BƯỚC 1: Mở Chrome thủ công
   python launcher.py
   → Chọn profile 001
   → Vào TikTok LIVE
   → Đảm bảo video đang chạy

BƯỚC 2: Chạy AUTO mode để so sánh
   python launch_livestream_tiktok.py
   → Chọn option 1
   → Nhập profile 001
   → Nhập URL LIVE
   → Logging tự động chạy

BƯỚC 3: So sánh
   python analysis\\run_comparison.py
   → Xem differences
   → Apply fixes

""")

print("="*70)
print("GIẢI PHÁP ĐƠN GIẢN HƠN")
print("="*70)

print("""
Thay vì thu thập baseline riêng, bạn có thể:

1. Chạy launcher.py thủ công → Xem LIVE → Hoạt động tốt
   (Đây là MANUAL mode - working)

2. Chạy launch_livestream_tiktok.py → Xem LIVE → Có lỗi
   (Đây là AUTO mode - failing)
   → Logging tự động được thu thập

3. So sánh 2 logs:
   python analysis\\run_comparison.py
   
4. Fix dựa trên differences

""")

print("="*70)
print("VẤN ĐỀ VỚI SCRIPT TỰ ĐỘNG")
print("="*70)

print("""
Script tự động launch Chrome gặp vấn đề:
- Cần đúng Chrome version (GPM)
- Cần đúng flags
- Cần đúng profile path
- Phức tạp và dễ lỗi

GIẢI PHÁP:
→ Dùng launcher.py có sẵn (đã hoạt động tốt)
→ Chỉ cần thêm logging vào launch_livestream_tiktok.py (đã xong)
→ So sánh 2 logs

""")

print("="*70)
print("LOGGING ĐÃ ĐƯỢC THÊM VÀO")
print("="*70)

print("""
✅ launch_livestream_tiktok.py đã có logging tự động
   → Mỗi lần chạy sẽ tạo file: analysis/logs/startup_auto_*.json

✅ Bạn chỉ cần:
   1. Chạy launch_livestream_tiktok.py
   2. Chạy analysis/run_comparison.py
   3. Xem differences

""")

input("\nNhấn Enter để đóng...")
