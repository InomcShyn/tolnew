#!/usr/bin/env python3
"""
Auto Refresh Token Service - Tự động xử lý hoàn toàn
Sử dụng refresh token đã có để tự động lấy mã TikTok
"""

import requests
import json
import time
import re
from datetime import datetime, timedelta
from typing import Optional, Tuple

class AutoRefreshTokenService:
    def __init__(self, refresh_token: str, client_id: str = "9e5f94bc-e8a4-4e73-b8be-63364c29d753"):
        self.refresh_token = refresh_token
        self.client_id = client_id
        self.access_token = None
        self.token_expires_at = None
    
    def refresh_access_token(self) -> bool:
        """Tự động refresh access token"""
        url = "https://login.microsoftonline.com/consumers/oauth2/v2.0/token"
        
        data = {
            'client_id': self.client_id,
            'refresh_token': self.refresh_token,
            'grant_type': 'refresh_token',
            'scope': 'Mail.Read'
        }
        
        try:
            response = requests.post(url, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data['access_token']
            expires_in = token_data.get('expires_in', 3600)
            self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 60)
            
            print("✅ Đã refresh access token thành công")
            return True
            
        except Exception as e:
            print(f"❌ Lỗi refresh token: {e}")
            return False
    
    def get_valid_access_token(self) -> Optional[str]:
        """Lấy access token hợp lệ"""
        if not self.access_token or not self.token_expires_at or datetime.now() >= self.token_expires_at:
            if not self.refresh_access_token():
                return None
        return self.access_token
    
    def search_tiktok_code(self, user_email: str, timeout: int = 90) -> Tuple[bool, str]:
        """Tìm mã TikTok trong email"""
        access_token = self.get_valid_access_token()
        if not access_token:
            return False, "Không thể lấy access token"
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        print(f"🔍 Đang tìm mã TikTok cho: {user_email}")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                # Tìm email gần đây
                url = f"https://graph.microsoft.com/v1.0/me/messages"
                params = {
                    '$top': 20,
                    '$orderby': 'receivedDateTime desc'
                }
                
                response = requests.get(url, headers=headers, params=params, timeout=10)
                
                if response.status_code == 401:
                    print("❌ Token hết hạn, đang refresh...")
                    access_token = self.get_valid_access_token()
                    if not access_token:
                        return False, "Không thể refresh token"
                    headers['Authorization'] = f'Bearer {access_token}'
                    continue
                
                if response.status_code != 200:
                    print(f"❌ Lỗi API: {response.status_code} - {response.text}")
                    return False, f"API error: {response.status_code}"
                
                data = response.json()
                messages = data.get('value', [])
                
                if not messages:
                    print("⏳ Chưa tìm thấy email...")
                    time.sleep(5)
                    continue
                
                # Kiểm tra từng email
                for msg in messages:
                    subject = msg.get('subject', '')
                    body = msg.get('body', {}).get('content', '')
                    received_time = msg.get('receivedDateTime', '')
                    sender = msg.get('from', {}).get('emailAddress', {}).get('address', '')
                    
                    # Tìm mã 6 chữ số
                    code_pattern = r'\b\d{6}\b'
                    codes = re.findall(code_pattern, f"{subject} {body}")
                    
                    if codes:
                        # Kiểm tra thời gian email (trong 5 phút gần đây)
                        try:
                            received_dt = datetime.fromisoformat(received_time.replace('Z', '+00:00'))
                            now = datetime.now(received_dt.tzinfo)
                            time_diff = (now - received_dt).total_seconds()
                            
                            if time_diff <= 300:  # 5 phút
                                code = codes[0]
                                print(f"✅ Tìm thấy mã TikTok: {code}")
                                print(f"📧 Email: {subject}")
                                print(f"👤 Người gửi: {sender}")
                                print(f"⏰ Thời gian: {received_time}")
                                return True, code
                        except:
                            pass
                
                print("⏳ Chưa tìm thấy mã mới...")
                time.sleep(5)
                
            except requests.exceptions.RequestException as e:
                print(f"❌ Lỗi kết nối: {e}")
                time.sleep(5)
            except Exception as e:
                print(f"❌ Lỗi không xác định: {e}")
                time.sleep(5)
        
        print(f"⏰ Hết thời gian chờ ({timeout}s)")
        return False, "Timeout"
    
    def get_tiktok_code(self, user_email: str, timeout: int = 90) -> Tuple[bool, str]:
        """Lấy mã TikTok (wrapper method)"""
        return self.search_tiktok_code(user_email, timeout)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Auto Refresh Token Service - Tự động lấy mã TikTok")
    parser.add_argument("--refresh-token", required=True, help="Microsoft Graph refresh token")
    parser.add_argument("--client-id", default="9e5f94bc-e8a4-4e73-b8be-63364c29d753", help="App Client ID")
    parser.add_argument("--user-email", required=True, help="User email để tìm mã TikTok")
    parser.add_argument("--timeout", type=int, default=90, help="Thời gian chờ (giây)")
    
    args = parser.parse_args()
    
    # Khởi tạo service
    service = AutoRefreshTokenService(args.refresh_token, args.client_id)
    
    # Lấy mã TikTok
    success, result = service.get_tiktok_code(args.user_email, args.timeout)
    
    if success:
        print(f"🎉 OK - Lấy mã thành công: {result}")
        return 0
    else:
        print(f"❌ FAIL - {result}")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
