#!/usr/bin/env python3
"""
Script đơn giản để lấy mã TikTok 2FA mà không cần consent lại
"""

import argparse
import json
import os
import sys
import msal
import requests
import time
import re
from datetime import datetime, timedelta

def get_access_token_from_refresh(refresh_token, client_id="9e5f94bc-e8a4-4e73-b8be-63364c29d753"):
    """Lấy access token mới từ refresh token"""
    try:
        app = msal.ConfidentialClientApplication(
            client_id,
            authority="https://login.microsoftonline.com/consumers"
        )
        
        result = app.acquire_token_by_refresh_token(refresh_token, scopes=["Mail.Read"])
        
        if "error" in result:
            print(f"❌ Lỗi refresh token: {result.get('error_description', result.get('error'))}")
            return None
            
        return result.get("access_token")
        
    except Exception as e:
        print(f"❌ Lỗi khi refresh token: {e}")
        return None

def fetch_tiktok_code(email, access_token, timeout=90):
    """Tìm mã TikTok trong email"""
    print(f"🔍 Đang tìm mã TikTok cho email: {email}")
    print(f"⏱️  Timeout: {timeout} giây")
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    # Tìm email từ TikTok
    search_query = "from:tiktok.com OR subject:TikTok OR subject:verification"
    
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
                print("❌ Token hết hạn hoặc không hợp lệ")
                return False, "Token expired"
            
            if response.status_code != 200:
                print(f"❌ Lỗi API: {response.status_code} - {response.text}")
                return False, f"API error: {response.status_code}"
            
            data = response.json()
            messages = data.get('value', [])
            
            if not messages:
                print("⏳ Chưa tìm thấy email từ TikTok...")
                time.sleep(5)
                continue
            
            # Kiểm tra từng email
            for msg in messages:
                subject = msg.get('subject', '')
                body = msg.get('body', {}).get('content', '')
                received_time = msg.get('receivedDateTime', '')
                
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
    parser = argparse.ArgumentParser(description="Lấy mã TikTok 2FA từ Microsoft Graph")
    parser.add_argument("--email", required=True, help="Email Hotmail/Outlook")
    parser.add_argument("--refresh-token", help="Microsoft Graph refresh token")
    parser.add_argument("--token-file", help="File JSON chứa refresh token")
    parser.add_argument("--timeout", type=int, default=90, help="Thời gian chờ (giây)")
    
    args = parser.parse_args()
    
    refresh_token = None
    client_id = "9e5f94bc-e8a4-4e73-b8be-63364c29d753"
    
    # Lấy refresh token
    if args.token_file:
        try:
            with open(args.token_file, 'r', encoding='utf-8') as f:
                token_data = json.load(f)
            refresh_token = token_data.get("refresh_token")
            client_id = token_data.get("client_id", client_id)
            print(f"✅ Đã tải token từ file: {args.token_file}")
        except Exception as e:
            print(f"❌ Lỗi đọc file token: {e}")
            sys.exit(1)
    elif args.refresh_token:
        refresh_token = args.refresh_token
    else:
        print("❌ Cần cung cấp --refresh-token hoặc --token-file")
        sys.exit(1)
    
    if not refresh_token:
        print("❌ Không tìm thấy refresh token")
        sys.exit(1)
    
    # Lấy access token
    print("🔄 Đang lấy access token...")
    access_token = get_access_token_from_refresh(refresh_token, client_id)
    
    if not access_token:
        print("❌ Không thể lấy access token")
        sys.exit(1)
    
    print("✅ Đã lấy access token thành công")
    
    # Tìm mã TikTok
    success, result = fetch_tiktok_code(args.email, access_token, args.timeout)
    
    if success:
        print(f"🎉 OK - Lấy mã thành công: {result}")
        sys.exit(0)
    else:
        print(f"❌ FAIL - {result}")
        sys.exit(1)

if __name__ == "__main__":
    main()
