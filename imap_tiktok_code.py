#!/usr/bin/env python3
"""
Script đọc email TikTok qua IMAP (không cần Microsoft Graph consent)
"""

import imaplib
import email
import re
import time
from datetime import datetime, timedelta

def connect_imap(email_address, password, server="outlook.office365.com", port=993):
    """Kết nối IMAP server"""
    try:
        mail = imaplib.IMAP4_SSL(server, port)
        mail.login(email_address, password)
        mail.select('inbox')
        return mail
    except Exception as e:
        print(f"❌ Lỗi kết nối IMAP: {e}")
        return None

def search_tiktok_code(mail, timeout=90):
    """Tìm mã TikTok trong email"""
    print("🔍 Đang tìm mã TikTok qua IMAP...")
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            # Tìm email từ TikTok
            search_criteria = [
                'FROM', 'tiktok.com',
                'OR', 'FROM', 'no-reply@account.tiktok.com',
                'OR', 'SUBJECT', 'TikTok',
                'OR', 'SUBJECT', 'verification',
                'OR', 'SUBJECT', 'code'
            ]
            
            # Tìm email trong 5 phút gần đây
            since_date = (datetime.now() - timedelta(minutes=5)).strftime("%d-%b-%Y")
            search_criteria.extend(['SINCE', since_date])
            
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
            for email_id in reversed(email_ids[-5:]):  # Chỉ kiểm tra 5 email gần nhất
                try:
                    status, msg_data = mail.fetch(email_id, '(RFC822)')
                    
                    if status != 'OK':
                        continue
                    
                    email_body = msg_data[0][1]
                    email_message = email.message_from_bytes(email_body)
                    
                    subject = email_message.get('Subject', '')
                    sender = email_message.get('From', '')
                    
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
                        date_str = email_message.get('Date', '')
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

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Lấy mã TikTok qua IMAP (không cần Graph consent)")
    parser.add_argument("--email", required=True, help="Email Hotmail/Outlook")
    parser.add_argument("--password", required=True, help="Password email")
    parser.add_argument("--timeout", type=int, default=90, help="Thời gian chờ (giây)")
    
    args = parser.parse_args()
    
    print(f"🔐 Đang kết nối IMAP cho: {args.email}")
    
    # Kết nối IMAP
    mail = connect_imap(args.email, args.password)
    
    if not mail:
        print("❌ Không thể kết nối IMAP")
        return 1
    
    print("✅ Đã kết nối IMAP thành công")
    
    # Tìm mã TikTok
    success, result = search_tiktok_code(mail, args.timeout)
    
    # Đóng kết nối
    try:
        mail.close()
        mail.logout()
    except:
        pass
    
    if success:
        print(f"🎉 OK - Lấy mã thành công: {result}")
        return 0
    else:
        print(f"❌ FAIL - {result}")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
