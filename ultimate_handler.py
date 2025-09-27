#!/usr/bin/env python3
"""
Ultimate TikTok 2FA Auto Handler - Xử lý tự động hoàn toàn
"""

import requests
import json
import time
import re
import msal
from datetime import datetime, timedelta
import subprocess
import sys

class UltimateTikTokHandler:
    def __init__(self, email, password=None, refresh_token=None):
        self.email = email
        self.password = password
        self.refresh_token = refresh_token
        self.client_id = "9e5f94bc-e8a4-4e73-b8be-63364c29d753"
        self.access_token = None
        self.token_expires_at = None
        self.found_codes = set()
    
    def auto_device_login(self):
        """Tự động device login"""
        print(f"[AUTO] Tự động device login cho: {self.email}")
        
        try:
            app = msal.PublicClientApplication(
                self.client_id, 
                authority="https://login.microsoftonline.com/consumers"
            )
            
            flow = app.initiate_device_flow(scopes=["Mail.Read"])
            device_code = flow.get('user_code', '')
            device_url = flow.get('verification_uri', 'https://www.microsoft.com/link')
            
            print(f"[DEVICE] Mở trình duyệt: {device_url}")
            print(f"[CODE] Nhập code: {device_code}")
            print("[WAIT] Đang chờ bạn hoàn thành đăng nhập...")
            
            result = app.acquire_token_by_device_flow(flow)
            
            if "error" in result:
                print(f"[ERROR] Device login failed: {result.get('error_description', result.get('error'))}")
                return False
            
            access_token = result.get("access_token")
            if not access_token:
                print("[ERROR] Không lấy được access token")
                return False
            
            self.access_token = access_token
            expires_in = result.get('expires_in', 3600)
            self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 60)
            
            print("[SUCCESS] Device login thành công!")
            return True
            
        except Exception as e:
            print(f"[ERROR] Device login error: {e}")
            return False
    
    def search_tiktok_codes(self, max_attempts=10, interval=10):
        """Tìm mã TikTok với nhiều lần thử"""
        print(f"[SEARCH] Bắt đầu tìm mã TikTok...")
        print(f"[ATTEMPTS] Tối đa {max_attempts} lần thử, mỗi {interval} giây")
        
        if not self.access_token:
            print("[ERROR] Không có access token")
            return False, "No access token"
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        for attempt in range(1, max_attempts + 1):
            print(f"[ATTEMPT] Lần thử {attempt}/{max_attempts} - {datetime.now().strftime('%H:%M:%S')}")
            
            try:
                url = f"https://graph.microsoft.com/v1.0/me/messages"
                params = {
                    '$top': 50,  # Tăng số lượng email
                    '$orderby': 'receivedDateTime desc'
                }
                
                response = requests.get(url, headers=headers, params=params, timeout=15)
                
                if response.status_code == 401:
                    print("[ERROR] Token hết hạn")
                    return False, "Token expired"
                
                if response.status_code != 200:
                    print(f"[ERROR] API error: {response.status_code}")
                    time.sleep(interval)
                    continue
                
                data = response.json()
                messages = data.get('value', [])
                
                if not messages:
                    print("[WAIT] Chưa tìm thấy email...")
                    time.sleep(interval)
                    continue
                
                print(f"[INFO] Tìm thấy {len(messages)} email")
                
                # Tìm mã TikTok trong tất cả email
                for i, msg in enumerate(messages):
                    subject = msg.get('subject', '')
                    body = msg.get('body', {}).get('content', '')
                    received_time = msg.get('receivedDateTime', '')
                    sender = msg.get('from', {}).get('emailAddress', {}).get('address', '')
                    
                    # Tìm mã 6 chữ số
                    code_pattern = r'\b\d{6}\b'
                    codes = re.findall(code_pattern, f"{subject} {body}")
                    
                    if codes:
                        # Kiểm tra thời gian email (trong 30 phút gần đây)
                        try:
                            received_dt = datetime.fromisoformat(received_time.replace('Z', '+00:00'))
                            now = datetime.now(received_dt.tzinfo)
                            time_diff = (now - received_dt).total_seconds()
                            
                            if time_diff <= 1800:  # 30 phút
                                code = codes[0]
                                
                                # Kiểm tra xem mã đã tìm thấy chưa
                                if code not in self.found_codes:
                                    self.found_codes.add(code)
                                    
                                    print(f"[SUCCESS] Tìm thấy mã TikTok mới: {code}")
                                    print(f"[EMAIL] Subject: {subject}")
                                    print(f"[SENDER] From: {sender}")
                                    print(f"[TIME] Received: {received_time}")
                                    print(f"[TIME] Current: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                                    
                                    return True, code
                        except:
                            pass
                
                print("[WAIT] Chưa tìm thấy mã mới...")
                time.sleep(interval)
                
            except Exception as e:
                print(f"[ERROR] Search error: {e}")
                time.sleep(interval)
        
        print("[TIMEOUT] Hết thời gian tìm kiếm")
        return False, "Timeout"
    
    def auto_handle(self):
        """Xử lý tự động hoàn toàn"""
        print(f"[ULTIMATE] Bắt đầu xử lý tự động TikTok 2FA cho: {self.email}")
        print(f"[TIME] Thời gian bắt đầu: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # Bước 1: Device login
        print("[STEP 1] Device Login...")
        if not self.auto_device_login():
            return False, "Device login failed"
        
        # Bước 2: Tìm mã TikTok
        print("\n[STEP 2] Tìm mã TikTok...")
        success, result = self.search_tiktok_codes(max_attempts=20, interval=15)
        
        if success:
            print(f"\n[RESULT] THÀNH CÔNG! Mã TikTok: {result}")
            return True, result
        else:
            print(f"\n[RESULT] THẤT BẠI! {result}")
            return False, result

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Ultimate TikTok 2FA Auto Handler")
    parser.add_argument("--email", required=True, help="Email Hotmail/Outlook")
    parser.add_argument("--password", help="Email password")
    parser.add_argument("--refresh-token", help="Refresh token")
    
    args = parser.parse_args()
    
    # Khởi tạo handler
    handler = UltimateTikTokHandler(args.email, args.password, args.refresh_token)
    
    # Xử lý tự động
    success, result = handler.auto_handle()
    
    if success:
        print(f"\n🎉 ULTIMATE SUCCESS! Mã TikTok: {result}")
        return 0
    else:
        print(f"\n❌ ULTIMATE FAILED! {result}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
