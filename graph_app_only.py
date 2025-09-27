#!/usr/bin/env python3
"""
Microsoft Graph App-Only Authentication - Không cần user consent
Chỉ hoạt động với Work/School accounts, không hoạt động với Personal accounts
"""

import requests
import json
import time
import re
from datetime import datetime, timedelta

class GraphAppOnlyAuth:
    def __init__(self, tenant_id, client_id, client_secret):
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.token_expires_at = None
    
    def get_access_token(self):
        """Lấy access token bằng App-Only authentication"""
        if self.access_token and self.token_expires_at and datetime.now() < self.token_expires_at:
            return self.access_token
        
        url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
        
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'scope': 'https://graph.microsoft.com/.default',
            'grant_type': 'client_credentials'
        }
        
        try:
            response = requests.post(url, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data['access_token']
            expires_in = token_data.get('expires_in', 3600)
            self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 60)
            
            print("✅ Đã lấy App-Only access token thành công")
            return self.access_token
            
        except Exception as e:
            print(f"❌ Lỗi lấy App-Only token: {e}")
            return None
    
    def search_emails(self, user_email, timeout=90):
        """Tìm email từ TikTok"""
        access_token = self.get_access_token()
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
                url = f"https://graph.microsoft.com/v1.0/users/{user_email}/messages"
                params = {
                    '$top': 20,
                    '$orderby': 'receivedDateTime desc'
                }
                
                response = requests.get(url, headers=headers, params=params, timeout=10)
                
                if response.status_code == 401:
                    print("❌ Token hết hạn, đang refresh...")
                    self.access_token = None
                    access_token = self.get_access_token()
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

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Microsoft Graph App-Only Authentication")
    parser.add_argument("--tenant-id", required=True, help="Tenant ID (Work/School account)")
    parser.add_argument("--client-id", required=True, help="App Client ID")
    parser.add_argument("--client-secret", required=True, help="App Client Secret")
    parser.add_argument("--user-email", required=True, help="User email để tìm mã TikTok")
    parser.add_argument("--timeout", type=int, default=90, help="Thời gian chờ (giây)")
    
    args = parser.parse_args()
    
    # Khởi tạo App-Only auth
    auth = GraphAppOnlyAuth(args.tenant_id, args.client_id, args.client_secret)
    
    # Tìm mã TikTok
    success, result = auth.search_emails(args.user_email, args.timeout)
    
    if success:
        print(f"🎉 OK - Lấy mã thành công: {result}")
        return 0
    else:
        print(f"❌ FAIL - {result}")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
