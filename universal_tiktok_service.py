#!/usr/bin/env python3
"""
Tổng hợp Backend Service - Tự động xử lý hoàn toàn
Kết hợp nhiều phương pháp để đảm bảo thành công
"""

import requests
import json
import time
import re
import imaplib
import email
from datetime import datetime, timedelta
from typing import Optional, Tuple, Dict, Any

class UniversalTikTokService:
    def __init__(self, email_address: str, password: str = None, 
                 refresh_token: str = None, client_id: str = "9e5f94bc-e8a4-4e73-b8be-63364c29d753"):
        self.email_address = email_address
        self.password = password
        self.refresh_token = refresh_token
        self.client_id = client_id
        self.access_token = None
        self.token_expires_at = None
    
    def try_graph_api(self, timeout: int = 90) -> Tuple[bool, str]:
        """Thử Microsoft Graph API với refresh token"""
        if not self.refresh_token:
            return False, "Không có refresh token"
        
        # Refresh access token
        if not self._refresh_access_token():
            return False, "Không thể refresh token"
        
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
                    print("❌ Token hết hạn, đang refresh...")
                    if not self._refresh_access_token():
                        return False, "Không thể refresh token"
                    headers['Authorization'] = f'Bearer {self.access_token}'
                    continue
                
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
    
    def try_imap(self, timeout: int = 90) -> Tuple[bool, str]:
        """Thử IMAP nếu có password"""
        if not self.password:
            return False, "Không có password"
        
        print("🔍 Đang tìm mã TikTok qua IMAP...")
        
        try:
            mail = imaplib.IMAP4_SSL("outlook.office365.com", 993)
            mail.login(self.email_address, self.password)
            mail.select('inbox')
            
            start_time = time.time()
            while time.time() - start_time < timeout:
                try:
                    # Tìm email từ TikTok trong 5 phút gần đây
                    since_date = (datetime.now() - timedelta(minutes=5)).strftime("%d-%b-%Y")
                    
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
    
    def _refresh_access_token(self) -> bool:
        """Refresh access token"""
        if self.access_token and self.token_expires_at and datetime.now() < self.token_expires_at:
            return True
        
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
            
            return True
            
        except Exception as e:
            print(f"❌ Lỗi refresh token: {e}")
            return False
    
    def _extract_tiktok_code(self, subject: str, body: str, received_time: str) -> Optional[str]:
        """Trích xuất mã TikTok từ email"""
        # Tìm mã 6 chữ số
        code_pattern = r'\b\d{6}\b'
        codes = re.findall(code_pattern, f"{subject} {body}")
        
        if not codes:
            return None
        
        # Kiểm tra thời gian email (trong 5 phút gần đây)
        try:
            if received_time:
                if 'T' in received_time:  # ISO format
                    received_dt = datetime.fromisoformat(received_time.replace('Z', '+00:00'))
                    now = datetime.now(received_dt.tzinfo)
                else:  # IMAP format
                    received_dt = email.utils.parsedate_to_datetime(received_time)
                    now = datetime.now(received_dt.tzinfo)
                
                time_diff = (now - received_dt).total_seconds()
                
                if time_diff <= 300:  # 5 phút
                    return codes[0]
        except:
            pass
        
        return None
    
    def get_tiktok_code(self, timeout: int = 90) -> Tuple[bool, str]:
        """Lấy mã TikTok (thử tất cả phương pháp)"""
        print(f"🎯 Đang tìm mã TikTok cho: {self.email_address}")
        
        # Thử Microsoft Graph API trước
        if self.refresh_token:
            print("1️⃣ Thử Microsoft Graph API...")
            success, result = self.try_graph_api(timeout)
            if success:
                return True, result
        
        # Thử IMAP nếu có password
        if self.password:
            print("2️⃣ Thử IMAP...")
            success, result = self.try_imap(timeout)
            if success:
                return True, result
        
        return False, "Không tìm thấy mã TikTok"

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Universal TikTok Code Service - Tự động xử lý hoàn toàn")
    parser.add_argument("--email", required=True, help="Email Hotmail/Outlook")
    parser.add_argument("--password", help="Email password hoặc App Password")
    parser.add_argument("--refresh-token", help="Microsoft Graph refresh token")
    parser.add_argument("--client-id", default="9e5f94bc-e8a4-4e73-b8be-63364c29d753", help="App Client ID")
    parser.add_argument("--timeout", type=int, default=90, help="Thời gian chờ (giây)")
    
    args = parser.parse_args()
    
    # Khởi tạo service
    service = UniversalTikTokService(
        email_address=args.email,
        password=args.password,
        refresh_token=args.refresh_token,
        client_id=args.client_id
    )
    
    # Lấy mã TikTok
    success, result = service.get_tiktok_code(args.timeout)
    
    if success:
        print(f"🎉 OK - Lấy mã thành công: {result}")
        return 0
    else:
        print(f"❌ FAIL - {result}")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
