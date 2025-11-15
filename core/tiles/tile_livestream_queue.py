#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Livestream Queue Management
Quản lý queue profiles cho nhiều users treo livestream đồng thời
"""

import time
import threading
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta

class LivestreamQueue:
    """
    Quản lý queue profiles cho livestream.
    
    Features:
    - Phân bổ profiles cho nhiều users
    - Tự động giải phóng profiles sau khi hết thời gian
    - Tái sử dụng profiles đã giải phóng
    - Thread-safe
    """
    
    def __init__(self):
        self.lock = threading.Lock()
        
        # Danh sách tất cả profiles có thể sử dụng
        self.all_profiles: List[str] = []
        
        # Profiles đang được sử dụng: {profile_name: session_info}
        self.active_sessions: Dict[str, Dict] = {}
        
        # Profiles đang chờ (available)
        self.available_profiles: List[str] = []
        
        # Lịch sử sessions
        self.session_history: List[Dict] = []
        
    def initialize(self, profiles: List[str], manager=None):
        """
        Khởi tạo queue với danh sách profiles.
        
        Args:
            profiles: Danh sách tên profiles
            manager: ChromeManager instance để check login status (optional)
        """
        with self.lock:
            # ✅ FILTER: Chỉ sử dụng profiles đã login
            if manager:
                logged_in_profiles = [p for p in profiles if manager.is_profile_logged_in(p)]
                not_logged_in = [p for p in profiles if p not in logged_in_profiles]
                
                if not_logged_in:
                    print(f"[QUEUE] [WARNING] {len(not_logged_in)} profile(s) chưa login, bỏ qua")
                
                if not logged_in_profiles:
                    print("[QUEUE] [ERROR] Không có profile nào đã login!")
                    self.all_profiles = []
                    self.available_profiles = []
                    self.active_sessions = {}
                    return
                
                print(f"[QUEUE] [FILTER] Sử dụng {len(logged_in_profiles)}/{len(profiles)} profiles đã login")
                profiles = logged_in_profiles
            
            self.all_profiles = profiles.copy()
            self.available_profiles = profiles.copy()
            self.active_sessions = {}
            print(f"[QUEUE] Initialized with {len(profiles)} profiles")
    
    def request_profiles(self, user_id: str, count: int, duration_minutes: int) -> Tuple[bool, List[str], str]:
        """
        Request profiles cho một user.
        
        Args:
            user_id: ID của user (ví dụ: "user1", "user2")
            count: Số lượng profiles cần
            duration_minutes: Thời gian treo (phút)
        
        Returns:
            tuple: (success, profiles, message)
        """
        with self.lock:
            # Kiểm tra profiles available
            if len(self.available_profiles) < count:
                return False, [], f"Không đủ profiles. Available: {len(self.available_profiles)}, Requested: {count}"
            
            # Lấy profiles
            allocated_profiles = self.available_profiles[:count]
            self.available_profiles = self.available_profiles[count:]
            
            # Tạo session info
            start_time = datetime.now()
            end_time = start_time + timedelta(minutes=duration_minutes)
            
            for profile in allocated_profiles:
                self.active_sessions[profile] = {
                    'user_id': user_id,
                    'start_time': start_time,
                    'end_time': end_time,
                    'duration_minutes': duration_minutes,
                    'status': 'active'
                }
            
            message = f"Allocated {len(allocated_profiles)} profiles for {user_id} (Duration: {duration_minutes} min)"
            print(f"[QUEUE] {message}")
            print(f"[QUEUE] Profiles: {allocated_profiles}")
            print(f"[QUEUE] Remaining available: {len(self.available_profiles)}")
            
            return True, allocated_profiles, message
    
    def release_profiles(self, profiles: List[str], reason: str = "completed"):
        """
        Giải phóng profiles về available pool.
        
        Args:
            profiles: Danh sách profiles cần giải phóng
            reason: Lý do giải phóng
        """
        with self.lock:
            released = []
            for profile in profiles:
                if profile in self.active_sessions:
                    session_info = self.active_sessions[profile]
                    session_info['status'] = 'released'
                    session_info['release_time'] = datetime.now()
                    session_info['release_reason'] = reason
                    
                    # Thêm vào history
                    self.session_history.append(session_info.copy())
                    
                    # Xóa khỏi active
                    del self.active_sessions[profile]
                    
                    # Thêm vào available
                    if profile not in self.available_profiles:
                        self.available_profiles.append(profile)
                        released.append(profile)
            
            if released:
                print(f"[QUEUE] Released {len(released)} profiles: {released}")
                print(f"[QUEUE] Reason: {reason}")
                print(f"[QUEUE] Available profiles: {len(self.available_profiles)}")
    
    def check_expired_sessions(self):
        """
        Kiểm tra và tự động giải phóng sessions đã hết thời gian.
        
        Returns:
            list: Danh sách profiles đã được giải phóng
        """
        with self.lock:
            now = datetime.now()
            expired_profiles = []
            
            for profile, session_info in list(self.active_sessions.items()):
                if now >= session_info['end_time']:
                    expired_profiles.append(profile)
            
            if expired_profiles:
                self.release_profiles(expired_profiles, reason="expired")
            
            return expired_profiles
    
    def get_status(self) -> Dict:
        """
        Lấy trạng thái hiện tại của queue.
        
        Returns:
            dict: Thông tin trạng thái
        """
        with self.lock:
            # Tính toán thống kê
            active_by_user = {}
            for profile, session_info in self.active_sessions.items():
                user_id = session_info['user_id']
                if user_id not in active_by_user:
                    active_by_user[user_id] = []
                active_by_user[user_id].append(profile)
            
            return {
                'total_profiles': len(self.all_profiles),
                'available': len(self.available_profiles),
                'active': len(self.active_sessions),
                'active_by_user': active_by_user,
                'session_history_count': len(self.session_history)
            }
    
    def get_user_sessions(self, user_id: str) -> List[Dict]:
        """
        Lấy danh sách sessions của một user.
        
        Args:
            user_id: ID của user
        
        Returns:
            list: Danh sách session info
        """
        with self.lock:
            user_sessions = []
            for profile, session_info in self.active_sessions.items():
                if session_info['user_id'] == user_id:
                    info = session_info.copy()
                    info['profile'] = profile
                    info['remaining_minutes'] = (session_info['end_time'] - datetime.now()).total_seconds() / 60
                    user_sessions.append(info)
            
            return user_sessions
    
    def force_release_user_sessions(self, user_id: str):
        """
        Giải phóng tất cả sessions của một user.
        
        Args:
            user_id: ID của user
        """
        with self.lock:
            user_profiles = [
                profile for profile, session_info in self.active_sessions.items()
                if session_info['user_id'] == user_id
            ]
            
            if user_profiles:
                self.release_profiles(user_profiles, reason=f"force_release_by_{user_id}")


# Global queue instance
_global_queue = None

def get_global_queue() -> LivestreamQueue:
    """Lấy global queue instance (singleton)"""
    global _global_queue
    if _global_queue is None:
        _global_queue = LivestreamQueue()
    return _global_queue


def start_auto_cleanup_thread(interval_seconds: int = 60):
    """
    Bắt đầu thread tự động cleanup expired sessions.
    
    Args:
        interval_seconds: Khoảng thời gian kiểm tra (giây)
    """
    def cleanup_worker():
        queue = get_global_queue()
        while True:
            try:
                expired = queue.check_expired_sessions()
                if expired:
                    print(f"[QUEUE-CLEANUP] Auto-released {len(expired)} expired profiles")
            except Exception as e:
                print(f"[QUEUE-CLEANUP] Error: {e}")
            
            time.sleep(interval_seconds)
    
    thread = threading.Thread(target=cleanup_worker, daemon=True, name="QueueCleanup")
    thread.start()
    print(f"[QUEUE] Auto-cleanup thread started (interval: {interval_seconds}s)")
