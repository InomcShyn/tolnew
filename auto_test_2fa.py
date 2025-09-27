#!/usr/bin/env python3
"""
Auto Test TikTok 2FA - Tự động test và tìm mã 2FA mới
"""

import time
import subprocess
import sys
from datetime import datetime

def run_auto_test(email, password=None, refresh_token=None, max_attempts=5):
    """Chạy test tự động nhiều lần để tìm mã 2FA mới"""
    
    print(f"🚀 Bắt đầu Auto Test TikTok 2FA cho: {email}")
    print(f"⏰ Thời gian bắt đầu: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔄 Số lần test tối đa: {max_attempts}")
    print("=" * 60)
    
    for attempt in range(1, max_attempts + 1):
        print(f"\n🔄 Lần test thứ {attempt}/{max_attempts}")
        print(f"⏰ Thời gian: {datetime.now().strftime('%H:%M:%S')}")
        
        try:
            # Tạo command
            cmd = [sys.executable, "auto_tiktok_fetcher.py", "--email", email]
            
            if password:
                cmd.extend(["--password", password])
            if refresh_token:
                cmd.extend(["--refresh-token", refresh_token])
            
            # Chạy command
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            print("📤 Output:")
            print(result.stdout)
            
            if result.stderr:
                print("⚠️ Errors:")
                print(result.stderr)
            
            # Kiểm tra kết quả
            if result.returncode == 0:
                if "🎉 OK - Lấy mã thành công:" in result.stdout:
                    print("✅ THÀNH CÔNG! Tìm thấy mã TikTok!")
                    return True, result.stdout
                else:
                    print("⚠️ Không tìm thấy mã TikTok trong lần này")
            else:
                print(f"❌ Lỗi trong lần test {attempt}")
            
        except subprocess.TimeoutExpired:
            print("⏰ Timeout - Lần test này quá lâu")
        except Exception as e:
            print(f"❌ Lỗi không xác định: {e}")
        
        # Nghỉ giữa các lần test
        if attempt < max_attempts:
            print(f"⏳ Nghỉ 30 giây trước lần test tiếp theo...")
            time.sleep(30)
    
    print("\n" + "=" * 60)
    print("❌ Kết thúc test - Không tìm thấy mã TikTok")
    return False, "No TikTok code found"

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Auto Test TikTok 2FA - Tự động test và tìm mã 2FA mới")
    parser.add_argument("--email", required=True, help="Email Hotmail/Outlook")
    parser.add_argument("--password", help="Email password hoặc App Password")
    parser.add_argument("--refresh-token", help="Microsoft Graph refresh token")
    parser.add_argument("--max-attempts", type=int, default=5, help="Số lần test tối đa")
    
    args = parser.parse_args()
    
    # Chạy auto test
    success, result = run_auto_test(
        email=args.email,
        password=args.password,
        refresh_token=args.refresh_token,
        max_attempts=args.max_attempts
    )
    
    if success:
        print(f"\n🎉 AUTO TEST THÀNH CÔNG!")
        print(f"📋 Kết quả: {result}")
        return 0
    else:
        print(f"\n❌ AUTO TEST THẤT BẠI!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
