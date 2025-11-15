"""
MinProxy API Integration
Tích hợp với API MinProxy để treo mắt livestream tự động
"""

import requests
import json
import time
from typing import Dict, List, Tuple, Optional


class MinProxyAPI:
    """Client để tương tác với MinProxy API"""
    
    def __init__(self, api_key: str, base_url: str = "https://dash.minproxy.vn/api"):
        """
        Khởi tạo MinProxy API client
        
        Args:
            api_key: API key từ MinProxy dashboard
            base_url: Base URL của API (mặc định: https://dash.minproxy.vn/api)
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'User-Agent': 'ChromeManager/2.0'
        })
    
    def get_account_info(self) -> Tuple[bool, Dict]:
        """
        Lấy thông tin tài khoản
        
        Returns:
            Tuple[bool, Dict]: (success, data/error_message)
        """
        try:
            response = self.session.get(f"{self.base_url}/account/info")
            response.raise_for_status()
            return True, response.json()
        except requests.exceptions.RequestException as e:
            return False, {'error': str(e)}
    
    def start_livestream_viewer(self, 
                                livestream_url: str,
                                profile_id: Optional[str] = None,
                                duration_minutes: int = 60,
                                auto_interact: bool = False) -> Tuple[bool, Dict]:
        """
        Bắt đầu treo mắt livestream
        
        Args:
            livestream_url: URL của livestream (TikTok, Facebook, YouTube, etc.)
            profile_id: ID của profile để sử dụng (optional)
            duration_minutes: Thời gian treo (phút)
            auto_interact: Tự động tương tác (like, comment)
        
        Returns:
            Tuple[bool, Dict]: (success, response_data/error_message)
        """
        try:
            payload = {
                'url': livestream_url,
                'duration': duration_minutes,
                'auto_interact': auto_interact
            }
            
            if profile_id:
                payload['profile_id'] = profile_id
            
            response = self.session.post(
                f"{self.base_url}/livestream/start",
                json=payload
            )
            response.raise_for_status()
            return True, response.json()
        except requests.exceptions.RequestException as e:
            return False, {'error': str(e)}
    
    def stop_livestream_viewer(self, session_id: str) -> Tuple[bool, Dict]:
        """
        Dừng treo mắt livestream
        
        Args:
            session_id: ID của session đang chạy
        
        Returns:
            Tuple[bool, Dict]: (success, response_data/error_message)
        """
        try:
            response = self.session.post(
                f"{self.base_url}/livestream/stop",
                json={'session_id': session_id}
            )
            response.raise_for_status()
            return True, response.json()
        except requests.exceptions.RequestException as e:
            return False, {'error': str(e)}
    
    def get_active_sessions(self) -> Tuple[bool, List[Dict]]:
        """
        Lấy danh sách các session đang chạy
        
        Returns:
            Tuple[bool, List[Dict]]: (success, sessions_list/error_message)
        """
        try:
            response = self.session.get(f"{self.base_url}/livestream/sessions")
            response.raise_for_status()
            data = response.json()
            return True, data.get('sessions', [])
        except requests.exceptions.RequestException as e:
            return False, {'error': str(e)}
    
    def get_balance(self) -> Tuple[bool, Dict]:
        """
        Lấy số dư tài khoản
        
        Returns:
            Tuple[bool, Dict]: (success, balance_data/error_message)
        """
        try:
            response = self.session.get(f"{self.base_url}/account/balance")
            response.raise_for_status()
            return True, response.json()
        except requests.exceptions.RequestException as e:
            return False, {'error': str(e)}


def start_minproxy_livestream_batch(
    api_key: str,
    livestream_url: str,
    profile_names: List[str],
    duration_minutes: int = 60,
    auto_interact: bool = False,
    delay_between_requests: float = 1.0
) -> List[Tuple[str, bool, str]]:
    """
    Bắt đầu treo livestream cho nhiều profile
    
    Args:
        api_key: MinProxy API key
        livestream_url: URL livestream
        profile_names: Danh sách tên profile
        duration_minutes: Thời gian treo (phút)
        auto_interact: Tự động tương tác
        delay_between_requests: Delay giữa các request (giây)
    
    Returns:
        List[Tuple[str, bool, str]]: Danh sách (profile_name, success, message)
    """
    if not api_key or not api_key.strip():
        return [(p, False, "API key không hợp lệ") for p in profile_names]
    
    if not livestream_url or not livestream_url.strip():
        return [(p, False, "URL livestream không hợp lệ") for p in profile_names]
    
    client = MinProxyAPI(api_key)
    results = []
    
    # Kiểm tra API key trước
    print(f"[MINPROXY] Kiểm tra API key...")
    success, account_info = client.get_account_info()
    if not success:
        error_msg = f"API key không hợp lệ: {account_info.get('error', 'Unknown error')}"
        print(f"[ERROR] [MINPROXY] {error_msg}")
        return [(p, False, error_msg) for p in profile_names]
    
    print(f"[MINPROXY] API key hợp lệ. Tài khoản: {account_info.get('username', 'N/A')}")
    
    # Lấy số dư
    success, balance_info = client.get_balance()
    if success:
        balance = balance_info.get('balance', 0)
        print(f"[MINPROXY] Số dư: {balance:,.0f} VNĐ")
    
    # Bắt đầu treo cho từng profile
    print(f"[MINPROXY] Bắt đầu treo {len(profile_names)} profile...")
    for idx, profile_name in enumerate(profile_names, 1):
        try:
            print(f"[MINPROXY] [{idx}/{len(profile_names)}] Đang xử lý profile: {profile_name}")
            
            success, response = client.start_livestream_viewer(
                livestream_url=livestream_url,
                profile_id=profile_name,
                duration_minutes=duration_minutes,
                auto_interact=auto_interact
            )
            
            if success:
                session_id = response.get('session_id', 'N/A')
                message = f"Đã bắt đầu treo livestream (Session: {session_id})"
                print(f"[SUCCESS] [MINPROXY] {profile_name}: {message}")
                results.append((profile_name, True, message))
            else:
                error = response.get('error', 'Unknown error')
                message = f"Lỗi: {error}"
                print(f"[ERROR] [MINPROXY] {profile_name}: {message}")
                results.append((profile_name, False, message))
            
            # Delay giữa các request
            if idx < len(profile_names):
                time.sleep(delay_between_requests)
        
        except Exception as e:
            message = f"Exception: {str(e)}"
            print(f"[ERROR] [MINPROXY] {profile_name}: {message}")
            results.append((profile_name, False, message))
    
    success_count = sum(1 for _, s, _ in results if s)
    print(f"[MINPROXY] Hoàn thành: {success_count}/{len(profile_names)} thành công")
    
    return results


def stop_minproxy_sessions(api_key: str, session_ids: List[str]) -> List[Tuple[str, bool, str]]:
    """
    Dừng các session đang chạy
    
    Args:
        api_key: MinProxy API key
        session_ids: Danh sách session ID cần dừng
    
    Returns:
        List[Tuple[str, bool, str]]: Danh sách (session_id, success, message)
    """
    if not api_key or not api_key.strip():
        return [(s, False, "API key không hợp lệ") for s in session_ids]
    
    client = MinProxyAPI(api_key)
    results = []
    
    print(f"[MINPROXY] Dừng {len(session_ids)} session...")
    for session_id in session_ids:
        try:
            success, response = client.stop_livestream_viewer(session_id)
            
            if success:
                message = "Đã dừng session"
                print(f"[SUCCESS] [MINPROXY] {session_id}: {message}")
                results.append((session_id, True, message))
            else:
                error = response.get('error', 'Unknown error')
                message = f"Lỗi: {error}"
                print(f"[ERROR] [MINPROXY] {session_id}: {message}")
                results.append((session_id, False, message))
        
        except Exception as e:
            message = f"Exception: {str(e)}"
            print(f"[ERROR] [MINPROXY] {session_id}: {message}")
            results.append((session_id, False, message))
    
    return results


def get_minproxy_active_sessions(api_key: str) -> Tuple[bool, List[Dict]]:
    """
    Lấy danh sách session đang chạy
    
    Args:
        api_key: MinProxy API key
    
    Returns:
        Tuple[bool, List[Dict]]: (success, sessions_list/error_message)
    """
    if not api_key or not api_key.strip():
        return False, {'error': 'API key không hợp lệ'}
    
    client = MinProxyAPI(api_key)
    return client.get_active_sessions()
