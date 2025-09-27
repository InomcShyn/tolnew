#!/usr/bin/env python3
"""
IMAP Backend Service - Tự động xử lý hoàn toàn
Không cần user consent, chỉ cần App Password
"""

import imaplib
import email
import re
import time
import json
from datetime import datetime, timedelta
from typing import Optional, Tuple

class IMAPBackendService:
    def __init__(self, email_address: str, app_password: str, 
                 server: str = "outlook.office365.com", port: int = 993):
        self.email_address = email_address
        self.app_password = app_password
        self.server = server
        self.port = port
        self.mail = None
    
    def connect(self) -> bool:
        """Kết nối IMAP server"""
        try:
            self.mail = imaplib.IMAP4_SSL(self.server, self.port)
            self.mail.login(self.email_address, self.app_password)
            self.mail.select('inbox')
            print(f"✅ Đã kết nối IMAP thành công: {self.email_address}")
            return True
        except Exception as e:
            print(f"❌ Lỗi kết nối IMAP: {e}")
            return False
    
    def disconnect(self):
        """Đóng kết nối IMAP"""
        if self.mail:
            try:
                self.mail.close()
                self.mail.logout()
            except:
                pass
    
    def search_tiktok_code(self, timeout: int = 90) -> Tuple[bool, str]:
        """Tìm mã TikTok trong email"""
        if not self.mail:
            return False, "Chưa kết nối IMAP"
        
        print("🔍 Đang tìm mã TikTok qua IMAP...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                # Tìm email từ TikTok trong 5 phút gần đây
                since_date = (datetime.now() - timedelta(minutes=5)).strftime("%d-%b-%Y")
                
                # Tìm kiếm email từ TikTok
                search_criteria = [
                    'FROM', 'tiktok.com',
                    'OR', 'FROM', 'no-reply@account.tiktok.com',
                    'OR', 'SUBJECT', 'TikTok',
                    'OR', 'SUBJECT', 'verification',
                    'OR', 'SUBJECT', 'code',
                    'SINCE', since_date
                ]
                
                status, messages = self.mail.search(None, *search_criteria)
                
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
                for email_id in reversed(email_ids[-10:]):  # Kiểm tra 10 email gần nhất
                    try:
                        status, msg_data = self.mail.fetch(email_id, '(RFC822)')
                        
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
                        
                        # Tìm mã 6 chữ số
                        code_pattern = r'\b\d{6}\b'
                        codes = re.findall(code_pattern, f"{subject} {body}")
                        
                        if codes:
                            # Kiểm tra thời gian email
                            try:
                                email_date = email.utils.parsedate_to_datetime(date_str)
                                now = datetime.now(email_date.tzinfo)
                                time_diff = (now - email_date).total_seconds()
                                
                                if time_diff <= 300:  # 5 phút
                                    code = codes[0]
                                    print(f"✅ Tìm thấy mã TikTok: {code}")
                                    print(f"📧 Email: {subject}")
                                    print(f"👤 Người gửi: {sender}")
                                    print(f"⏰ Thời gian: {date_str}")
                                    return True, code
                            except:
                                pass
                    
                    except Exception as e:
                        print(f"⚠️ Lỗi xử lý email: {e}")
                        continue
                
                print("⏳ Chưa tìm thấy mã mới...")
                time.sleep(5)
                
            except Exception as e:
                print(f"❌ Lỗi tìm kiếm: {e}")
                time.sleep(5)
        
        print(f"⏰ Hết thời gian chờ ({timeout}s)")
        return False, "Timeout"
    
    def get_tiktok_code(self, timeout: int = 90) -> Tuple[bool, str]:
        """Lấy mã TikTok (wrapper method)"""
        if not self.connect():
            return False, "Không thể kết nối IMAP"
        
        try:
            return self.search_tiktok_code(timeout)
        finally:
            self.disconnect()

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="IMAP Backend Service - Tự động lấy mã TikTok")
    parser.add_argument("--email", required=True, help="Email Hotmail/Outlook")
    parser.add_argument("--app-password", required=True, help="App Password (không phải password thường)")
    parser.add_argument("--timeout", type=int, default=90, help="Thời gian chờ (giây)")
    
    args = parser.parse_args()
    
    # Khởi tạo IMAP service
    service = IMAPBackendService(args.email, args.app_password)
    
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
