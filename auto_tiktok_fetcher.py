#!/usr/bin/env python3
"""
Auto TikTok Code Fetcher - Tự động xử lý hoàn toàn
Xử lý tất cả các trường hợp: refresh token, password, device login
"""

import requests
import json
import time
import re
import imaplib
import email
import msal
from datetime import datetime, timedelta
from typing import Optional, Tuple

class AutoTikTokFetcher:
    def __init__(self, email_address: str, password: str = None, 
                 refresh_token: str = None, client_id: str = "9e5f94bc-e8a4-4e73-b8be-63364c29d753"):
        self.email_address = email_address
        self.password = password
        self.refresh_token = refresh_token
        self.client_id = client_id
        self.access_token = None
        self.token_expires_at = None
    
    def try_device_login(self, timeout: int = 90) -> Tuple[bool, str]:
        """Thử device login để lấy token mới"""
        print("🔄 Đang thử device login...")
        
        try:
            app = msal.PublicClientApplication(
                self.client_id, 
                authority="https://login.microsoftonline.com/consumers"
            )
            
            flow = app.initiate_device_flow(scopes=["Mail.Read"])
            print(f"🌐 Mở trình duyệt và làm theo hướng dẫn:")
            print(f"   {flow.get('message', 'Open browser and complete the device code flow')}")
            print()
            print("⏳ Đang chờ bạn hoàn thành đăng nhập...")
            
            result = app.acquire_token_by_device_flow(flow)
            
            if "error" in result:
                print(f"❌ Lỗi device login: {result.get('error_description', result.get('error'))}")
                return False, "Device login failed"
            
            access_token = result.get("access_token")
            if not access_token:
                print("❌ Không lấy được access token")
                return False, "No access token"
            
            self.access_token = access_token
            expires_in = result.get('expires_in', 3600)
            self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 60)
            
            print("✅ Device login thành công!")
            return True, "Device login success"
            
        except Exception as e:
            print(f"❌ Lỗi device login: {e}")
            return False, f"Device login error: {e}"
    
    def try_refresh_token(self, timeout: int = 90) -> Tuple[bool, str]:
        """Thử refresh token"""
        if not self.refresh_token:
            return False, "No refresh token"
        
        print("🔄 Đang thử refresh token...")
        
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
            
            print("✅ Refresh token thành công!")
            return True, "Refresh token success"
            
        except Exception as e:
            print(f"❌ Lỗi refresh token: {e}")
            return False, f"Refresh token error: {e}"
    
    def try_imap(self, timeout: int = 90) -> Tuple[bool, str]:
        """Thử IMAP"""
        if not self.password:
            return False, "No password"
        
        print("🔄 Đang thử IMAP...")
        
        try:
            mail = imaplib.IMAP4_SSL("outlook.office365.com", 993)
            mail.login(self.email_address, self.password)
            mail.select('inbox')
            
            print("✅ IMAP kết nối thành công!")
            
            start_time = time.time()
            while time.time() - start_time < timeout:
                try:
                    # Tìm email từ TikTok trong 10 phút gần đây
                    since_date = (datetime.now() - timedelta(minutes=10)).strftime("%d-%b-%Y")
                    
                    search_criteria = [
                        'FROM', 'tiktok.com',
                        'OR', 'FROM', 'no-reply@account.tiktok.com',
                        'OR', 'SUBJECT', 'TikTok',
                        'OR', 'SUBJECT', 'verification',
                        'OR', 'SUBJECT', 'code',
                        'SINCE', since_date
                    ]
                    
                    status, messages = mail.search(None, *search_criteria)
                    
                    if status != 'OK':
                        print("⏳ Chưa tìm thấy email từ TikTok...")
                        time.sleep(5)
                        continue
                    
                    email_ids = messages[0].split()
                    
                    if not email_ids:
                        print("⏳ Chưa tìm thấy email mới...")
                        time.sleep(5)
                        continue
                    
                    # Kiểm tra email mới nhất
                    for email_id in reversed(email_ids[-10:]):
                        try:
                            status, msg_data = mail.fetch(email_id, '(RFC822)')
                            
                            if status != 'OK':
                                continue
                            
                            email_body = msg_data[0][1]
                            email_message = email.message_from_bytes(email_body)
                            
                            subject = email_message.get('Subject', '')
                            sender = email_message.get('From', '')
                            date_str = email_message.get('Date', '')
                            
                            # Lấy nội dung email
                            body = ""
                            if email_message.is_multipart():
                                for part in email_message.walk():
                                    if part.get_content_type() == "text/plain":
                                        body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                                        break
                            else:
                                body = email_message.get_payload(decode=True).decode('utf-8', errors='ignore')
                            
                            code = self._extract_tiktok_code(subject, body, date_str)
                            if code:
                                print(f"✅ Tìm thấy mã TikTok: {code}")
                                print(f"📧 Email: {subject}")
                                print(f"👤 Người gửi: {sender}")
                                print(f"⏰ Thời gian: {date_str}")
                                return True, code
                        
                        except Exception as e:
                            print(f"⚠️ Lỗi xử lý email: {e}")
                            continue
                    
                    print("⏳ Chưa tìm thấy mã mới...")
                    time.sleep(5)
                    
                except Exception as e:
                    print(f"❌ Lỗi IMAP: {e}")
                    time.sleep(5)
            
            mail.close()
            mail.logout()
            return False, "Timeout"
            
        except Exception as e:
            print(f"❌ Lỗi kết nối IMAP: {e}")
            return False, f"IMAP error: {e}"
    
    def search_graph_api(self, timeout: int = 90) -> Tuple[bool, str]:
        """Tìm mã TikTok qua Graph API"""
        if not self.access_token:
            return False, "No access token"
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        print("🔍 Đang tìm mã TikTok qua Microsoft Graph...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                url = f"https://graph.microsoft.com/v1.0/me/messages"
                params = {
                    '$top': 20,
                    '$orderby': 'receivedDateTime desc'
                }
                
                response = requests.get(url, headers=headers, params=params, timeout=10)
                
                if response.status_code == 401:
                    print("❌ Token hết hạn")
                    return False, "Token expired"
                
                if response.status_code != 200:
                    print(f"❌ Lỗi API: {response.status_code}")
                    return False, f"API error: {response.status_code}"
                
                data = response.json()
                messages = data.get('value', [])
                
                if not messages:
                    print("⏳ Chưa tìm thấy email...")
                    time.sleep(5)
                    continue
                
                # Tìm mã TikTok
                for msg in messages:
                    subject = msg.get('subject', '')
                    body = msg.get('body', {}).get('content', '')
                    received_time = msg.get('receivedDateTime', '')
                    sender = msg.get('from', {}).get('emailAddress', {}).get('address', '')
                    
                    code = self._extract_tiktok_code(subject, body, received_time)
                    if code:
                        print(f"✅ Tìm thấy mã TikTok: {code}")
                        print(f"📧 Email: {subject}")
                        print(f"👤 Người gửi: {sender}")
                        print(f"⏰ Thời gian: {received_time}")
                        return True, code
                
                print("⏳ Chưa tìm thấy mã mới...")
                time.sleep(5)
                
            except Exception as e:
                print(f"❌ Lỗi Graph API: {e}")
                time.sleep(5)
        
        return False, "Timeout"
    
    def _extract_tiktok_code(self, subject: str, body: str, received_time: str) -> Optional[str]:
        """Trích xuất mã TikTok từ email"""
        # Tìm mã 6 chữ số
        code_pattern = r'\b\d{6}\b'
        codes = re.findall(code_pattern, f"{subject} {body}")
        
        if not codes:
            return None
        
        # Kiểm tra thời gian email (trong 10 phút gần đây để có thêm thời gian)
        try:
            if received_time:
                if 'T' in received_time:  # ISO format
                    received_dt = datetime.fromisoformat(received_time.replace('Z', '+00:00'))
                    now = datetime.now(received_dt.tzinfo)
                else:  # IMAP format
                    received_dt = email.utils.parsedate_to_datetime(received_time)
                    now = datetime.now(received_dt.tzinfo)
                
                time_diff = (now - received_dt).total_seconds()
                
                if time_diff <= 600:  # 10 phút
                    return codes[0]
        except:
            pass
        
        return None
    
    def get_tiktok_code(self, timeout: int = 90) -> Tuple[bool, str]:
        """Lấy mã TikTok (thử tất cả phương pháp)"""
        print(f"[TARGET] Đang tìm mã TikTok cho: {self.email_address}")
        
        # 1. Thử refresh token trước
        if self.refresh_token:
            print("[1] Thử refresh token...")
            success, result = self.try_refresh_token(timeout)
            if success:
                success, result = self.search_graph_api(timeout)
                if success:
                    return True, result
        
        # 2. Thử IMAP
        if self.password:
            print("[2] Thử IMAP...")
            success, result = self.try_imap(timeout)
            if success:
                return True, result
        
        # 3. Thử device login
        print("[3] Thử device login...")
        success, result = self.try_device_login(timeout)
        if success:
            success, result = self.search_graph_api(timeout)
            if success:
                return True, result
        
        return False, "Không tìm thấy mã TikTok"

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Auto TikTok Code Fetcher - Tự động xử lý hoàn toàn")
    parser.add_argument("--email", required=True, help="Email Hotmail/Outlook")
    parser.add_argument("--password", help="Email password hoặc App Password")
    parser.add_argument("--refresh-token", help="Microsoft Graph refresh token")
    parser.add_argument("--client-id", default="9e5f94bc-e8a4-4e73-b8be-63364c29d753", help="App Client ID")
    parser.add_argument("--timeout", type=int, default=90, help="Thời gian chờ (giây)")
    
    args = parser.parse_args()
    
    # Khởi tạo fetcher
    fetcher = AutoTikTokFetcher(
        email_address=args.email,
        password=args.password,
        refresh_token=args.refresh_token,
        client_id=args.client_id
    )
    
    # Lấy mã TikTok
    success, result = fetcher.get_tiktok_code(args.timeout)
    
    if success:
        print(f"🎉 OK - Lấy mã thành công: {result}")
        return 0
    else:
        print(f"❌ FAIL - {result}")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
