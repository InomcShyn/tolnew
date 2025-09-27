#!/usr/bin/env python3
"""
Script để lưu Microsoft Graph refresh token sau device login
Chỉ cần chạy một lần để lưu token, sau đó có thể dùng lại mãi
"""

import argparse
import json
import os
import sys
import msal

def save_refresh_token(email, client_id="9e5f94bc-e8a4-4e73-b8be-63364c29d753"):
    """Lưu refresh token để dùng lại sau này"""
    
    print(f"🔐 Đang thiết lập Microsoft Graph cho email: {email}")
    print("📝 LƯU Ý: Bạn chỉ cần làm bước này MỘT LẦN duy nhất!")
    print()
    
    # Tạo MSAL app
    app = msal.PublicClientApplication(
        client_id, 
        authority="https://login.microsoftonline.com/consumers"
    )
    
    # Bắt đầu device flow
    flow = app.initiate_device_flow(scopes=["Mail.Read"])
    print("🌐 Mở trình duyệt và làm theo hướng dẫn:")
    print(f"   {flow.get('message', 'Open browser and complete the device code flow')}")
    print()
    print("⏳ Đang chờ bạn hoàn thành đăng nhập...")
    
    # Chờ user hoàn thành device flow
    result = app.acquire_token_by_device_flow(flow)
    
    if "error" in result:
        print(f"❌ Lỗi đăng nhập: {result.get('error_description', result.get('error'))}")
        return False
    
    access_token = result.get("access_token")
    refresh_token = result.get("refresh_token")
    
    if not access_token:
        print("❌ Không lấy được access token")
        return False
    
    if not refresh_token:
        print("⚠️  Không có refresh token - token này sẽ hết hạn sau 1 giờ")
        print("💡 Để có refresh token, bạn cần consent với scope offline_access")
        print("🔄 Thử lại với scope mở rộng...")
        
        # Thử lại với offline_access scope
        flow = app.initiate_device_flow(scopes=["Mail.Read", "offline_access"])
        print("🌐 Mở trình duyệt và làm theo hướng dẫn:")
        print(f"   {flow.get('message', 'Open browser and complete the device code flow')}")
        print()
        print("⏳ Đang chờ bạn hoàn thành đăng nhập...")
        
        result = app.acquire_token_by_device_flow(flow)
        
        if "error" in result:
            print(f"❌ Lỗi đăng nhập: {result.get('error_description', result.get('error'))}")
            return False
        
        refresh_token = result.get("refresh_token")
    
    # Lưu token vào file
    token_data = {
        "email": email,
        "client_id": client_id,
        "refresh_token": refresh_token,
        "access_token": access_token,
        "expires_at": result.get("expires_in", 3600) + int(result.get("expires_in", 3600))
    }
    
    token_file = f"ms_token_{email.replace('@', '_at_').replace('.', '_')}.json"
    
    try:
        with open(token_file, 'w', encoding='utf-8') as f:
            json.dump(token_data, f, indent=2)
        
        print(f"✅ Đã lưu token thành công!")
        print(f"📁 File: {token_file}")
        print()
        print("🎉 Từ giờ bạn có thể dùng lệnh sau để lấy mã TikTok:")
        print(f"   python test_tiktok_code.py --refresh-token-file {token_file}")
        print()
        print("💡 Hoặc tạo file account.txt với nội dung:")
        print(f"   u|p|{email}|ep|{refresh_token}|{client_id}")
        print("   Sau đó chạy: python test_tiktok_code.py --file account.txt")
        
        return True
        
    except Exception as e:
        print(f"❌ Lỗi lưu file: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Lưu Microsoft Graph refresh token")
    parser.add_argument("--email", required=True, help="Email Hotmail/Outlook của bạn")
    parser.add_argument("--client-id", default="9e5f94bc-e8a4-4e73-b8be-63364c29d753", help="Microsoft App Client ID")
    
    args = parser.parse_args()
    
    success = save_refresh_token(args.email, args.client_id)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
