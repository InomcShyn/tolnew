#!/usr/bin/env python3
"""
Simple TikTok 2FA Test - Test đơn giản không có emoji
"""

import requests
import json
import time
import re
import msal
from datetime import datetime, timedelta

def test_tiktok_2fa(email, password=None, refresh_token=None):
    """Test tìm mã TikTok 2FA"""
    
    print(f"[TEST] Đang test TikTok 2FA cho: {email}")
    print(f"[TIME] Thời gian: {datetime.now().strftime('%H:%M:%S')}")
    
    # Thử device login
    try:
        print("[1] Thử device login...")
        client_id = "9e5f94bc-e8a4-4e73-b8be-63364c29d753"
        app = msal.PublicClientApplication(
            client_id, 
            authority="https://login.microsoftonline.com/consumers"
        )
        
        flow = app.initiate_device_flow(scopes=["Mail.Read"])
        print(f"[DEVICE] Mở trình duyệt: {flow.get('message', 'Open browser and complete the device code flow')}")
        print("[WAIT] Đang chờ bạn hoàn thành đăng nhập...")
        
        result = app.acquire_token_by_device_flow(flow)
        
        if "error" in result:
            print(f"[ERROR] Device login failed: {result.get('error_description', result.get('error'))}")
            return False, "Device login failed"
        
        access_token = result.get("access_token")
        if not access_token:
            print("[ERROR] Không lấy được access token")
            return False, "No access token"
        
        print("[SUCCESS] Device login thành công!")
        
        # Tìm mã TikTok
        print("[SEARCH] Đang tìm mã TikTok...")
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        start_time = time.time()
        timeout = 90
        
        while time.time() - start_time < timeout:
            try:
                url = f"https://graph.microsoft.com/v1.0/me/messages"
                params = {
                    '$top': 20,
                    '$orderby': 'receivedDateTime desc'
                }
                
                response = requests.get(url, headers=headers, params=params, timeout=10)
                
                if response.status_code != 200:
                    print(f"[ERROR] API error: {response.status_code}")
                    time.sleep(5)
                    continue
                
                data = response.json()
                messages = data.get('value', [])
                
                if not messages:
                    print("[WAIT] Chưa tìm thấy email...")
                    time.sleep(5)
                    continue
                
                # Tìm mã TikTok
                for msg in messages:
                    subject = msg.get('subject', '')
                    body = msg.get('body', {}).get('content', '')
                    received_time = msg.get('receivedDateTime', '')
                    sender = msg.get('from', {}).get('emailAddress', {}).get('address', '')
                    
                    # Tìm mã 6 chữ số
                    code_pattern = r'\b\d{6}\b'
                    codes = re.findall(code_pattern, f"{subject} {body}")
                    
                    if codes:
                        # Kiểm tra thời gian email (trong 10 phút gần đây)
                        try:
                            received_dt = datetime.fromisoformat(received_time.replace('Z', '+00:00'))
                            now = datetime.now(received_dt.tzinfo)
                            time_diff = (now - received_dt).total_seconds()
                            
                            if time_diff <= 600:  # 10 phút
                                code = codes[0]
                                print(f"[SUCCESS] Tìm thấy mã TikTok: {code}")
                                print(f"[EMAIL] Subject: {subject}")
                                print(f"[SENDER] From: {sender}")
                                print(f"[TIME] Received: {received_time}")
                                return True, code
                        except:
                            pass
                
                print("[WAIT] Chưa tìm thấy mã mới...")
                time.sleep(5)
                
            except Exception as e:
                print(f"[ERROR] Search error: {e}")
                time.sleep(5)
        
        print("[TIMEOUT] Hết thời gian chờ")
        return False, "Timeout"
        
    except Exception as e:
        print(f"[ERROR] Test error: {e}")
        return False, f"Test error: {e}"

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Simple TikTok 2FA Test")
    parser.add_argument("--email", required=True, help="Email Hotmail/Outlook")
    parser.add_argument("--password", help="Email password")
    parser.add_argument("--refresh-token", help="Refresh token")
    
    args = parser.parse_args()
    
    # Test
    success, result = test_tiktok_2fa(args.email, args.password, args.refresh_token)
    
    if success:
        print(f"[RESULT] OK - Lấy mã thành công: {result}")
        return 0
    else:
        print(f"[RESULT] FAIL - {result}")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
