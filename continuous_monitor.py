#!/usr/bin/env python3
"""
Continuous TikTok 2FA Monitor - Liên tục monitor và tìm mã 2FA mới
"""

import requests
import json
import time
import re
import msal
from datetime import datetime, timedelta
import threading
import queue

class TikTok2FAMonitor:
    def __init__(self, email, password=None, refresh_token=None):
        self.email = email
        self.password = password
        self.refresh_token = refresh_token
        self.client_id = "9e5f94bc-e8a4-4e73-b8be-63364c29d753"
        self.access_token = None
        self.token_expires_at = None
        self.found_codes = set()  # Lưu các mã đã tìm thấy để tránh trùng lặp
        self.running = False
        self.result_queue = queue.Queue()
    
    def get_access_token(self):
        """Lấy access token mới"""
        try:
            app = msal.PublicClientApplication(
                self.client_id, 
                authority="https://login.microsoftonline.com/consumers"
            )
            
            flow = app.initiate_device_flow(scopes=["Mail.Read"])
            print(f"[DEVICE] Mở trình duyệt: {flow.get('message', 'Open browser and complete the device code flow')}")
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
    
    def search_new_codes(self):
        """Tìm mã TikTok mới"""
        if not self.access_token:
            return False
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        try:
            url = f"https://graph.microsoft.com/v1.0/me/messages"
            params = {
                '$top': 30,  # Tăng số lượng email để tìm kiếm
                '$orderby': 'receivedDateTime desc'
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 401:
                print("[ERROR] Token hết hạn")
                return False
            
            if response.status_code != 200:
                print(f"[ERROR] API error: {response.status_code}")
                return False
            
            data = response.json()
            messages = data.get('value', [])
            
            if not messages:
                return False
            
            # Tìm mã TikTok mới
            for msg in messages:
                subject = msg.get('subject', '')
                body = msg.get('body', {}).get('content', '')
                received_time = msg.get('receivedDateTime', '')
                sender = msg.get('from', {}).get('emailAddress', {}).get('address', '')
                
                # Tìm mã 6 chữ số
                code_pattern = r'\b\d{6}\b'
                codes = re.findall(code_pattern, f"{subject} {body}")
                
                if codes:
                    # Kiểm tra thời gian email (trong 15 phút gần đây)
                    try:
                        received_dt = datetime.fromisoformat(received_time.replace('Z', '+00:00'))
                        now = datetime.now(received_dt.tzinfo)
                        time_diff = (now - received_dt).total_seconds()
                        
                        if time_diff <= 900:  # 15 phút
                            code = codes[0]
                            
                            # Kiểm tra xem mã đã tìm thấy chưa
                            if code not in self.found_codes:
                                self.found_codes.add(code)
                                
                                print(f"[NEW CODE] Tìm thấy mã TikTok mới: {code}")
                                print(f"[EMAIL] Subject: {subject}")
                                print(f"[SENDER] From: {sender}")
                                print(f"[TIME] Received: {received_time}")
                                print(f"[TIME] Current: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                                
                                # Gửi kết quả vào queue
                                self.result_queue.put({
                                    'code': code,
                                    'subject': subject,
                                    'sender': sender,
                                    'received_time': received_time,
                                    'found_time': datetime.now().isoformat()
                                })
                                
                                return True
                    except:
                        pass
            
            return False
            
        except Exception as e:
            print(f"[ERROR] Search error: {e}")
            return False
    
    def monitor_loop(self, interval=30):
        """Vòng lặp monitor liên tục"""
        print(f"[MONITOR] Bắt đầu monitor TikTok 2FA cho: {self.email}")
        print(f"[INTERVAL] Kiểm tra mỗi {interval} giây")
        print(f"[TIME] Thời gian bắt đầu: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        self.running = True
        
        # Lấy access token ban đầu
        if not self.get_access_token():
            print("[ERROR] Không thể lấy access token ban đầu")
            return
        
        while self.running:
            try:
                print(f"[CHECK] Kiểm tra mã mới... {datetime.now().strftime('%H:%M:%S')}")
                
                # Tìm mã mới
                found = self.search_new_codes()
                
                if not found:
                    print("[WAIT] Chưa có mã mới")
                
                # Nghỉ trước lần kiểm tra tiếp theo
                time.sleep(interval)
                
            except KeyboardInterrupt:
                print("[STOP] Dừng monitor...")
                self.running = False
                break
            except Exception as e:
                print(f"[ERROR] Monitor error: {e}")
                time.sleep(interval)
        
        print("[END] Kết thúc monitor")
    
    def stop_monitor(self):
        """Dừng monitor"""
        self.running = False
    
    def get_latest_code(self):
        """Lấy mã mới nhất"""
        try:
            return self.result_queue.get_nowait()
        except queue.Empty:
            return None

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Continuous TikTok 2FA Monitor")
    parser.add_argument("--email", required=True, help="Email Hotmail/Outlook")
    parser.add_argument("--password", help="Email password")
    parser.add_argument("--refresh-token", help="Refresh token")
    parser.add_argument("--interval", type=int, default=30, help="Khoảng thời gian kiểm tra (giây)")
    parser.add_argument("--duration", type=int, default=300, help="Thời gian monitor (giây)")
    
    args = parser.parse_args()
    
    # Khởi tạo monitor
    monitor = TikTok2FAMonitor(args.email, args.password, args.refresh_token)
    
    # Chạy monitor trong thread riêng
    monitor_thread = threading.Thread(target=monitor.monitor_loop, args=(args.interval,))
    monitor_thread.daemon = True
    monitor_thread.start()
    
    print(f"[INFO] Monitor sẽ chạy trong {args.duration} giây")
    print("[INFO] Nhấn Ctrl+C để dừng sớm")
    
    try:
        # Chạy trong thời gian chỉ định
        time.sleep(args.duration)
        monitor.stop_monitor()
        monitor_thread.join()
        
        # Hiển thị kết quả
        print("\n[RESULTS] Các mã đã tìm thấy:")
        while True:
            result = monitor.get_latest_code()
            if result is None:
                break
            print(f"  - Mã: {result['code']} | Email: {result['subject']} | Thời gian: {result['found_time']}")
        
    except KeyboardInterrupt:
        print("\n[STOP] Dừng monitor...")
        monitor.stop_monitor()
        monitor_thread.join()

if __name__ == "__main__":
    main()
