#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TikTok Manager - Quản lý tất cả chức năng TikTok
Tích hợp: Status Check, Feature Block Check, Relogin, Storage
"""

import asyncio
import json
import os
from typing import Dict, Optional, Any, List, Tuple
from datetime import datetime


# ============================================================
# CONSTANTS - TikTok Error Codes
# ============================================================

class TikTokErrorCodes:
    """TikTok error codes constants"""
    # Comment blocks
    COMMENT_RESTRICTED = [2433, 2431]
    
    # Like blocks
    LIKE_BLOCKED = [2340, 3002041]
    
    # Follow blocks
    FOLLOW_BLOCKED = [20022, 20009]
    
    # Share blocks
    SHARE_BLOCKED = [3002080]
    
    # Live blocks
    LIVE_BLOCKED = [200004]
    
    # Login success
    SUCCESS = 0


class AccountStatus:
    """Account status constants"""
    LIVE = "live"
    DIE = "die"
    FEATURE_BLOCK = "feature_block"
    BANNED = "banned"
    LOGIN_FAILED = "login_failed"
    CAPTCHA = "captcha"
    NETWORK_ERROR = "network_error"
    UNKNOWN = "unknown"


# ============================================================
# 1. CHECK FEATURE BLOCK
# ============================================================

async def check_feature_block(page, account: str) -> Dict[str, Any]:
    """
    Kiểm tra các tính năng bị block của account
    
    Args:
        page: Playwright Page object
        account: TikTok username hoặc email
    
    Returns:
        {
            'status': 'live' | 'feature_block' | 'banned',
            'block_detail': {
                'comment': bool,
                'like': bool,
                'follow': bool,
                'share': bool,
                'live': bool,
                'shadowban': bool
            },
            'error_codes': [list],
            'timestamp': str
        }
    """
    result = {
        'status': AccountStatus.LIVE,
        'block_detail': {
            'comment': False,
            'like': False,
            'follow': False,
            'share': False,
            'live': False,
            'shadowban': False
        },
        'error_codes': [],
        'timestamp': datetime.now().isoformat()
    }
    
    try:
        print(f"[FEATURE-CHECK] Checking features for: {account}")
        
        blocked_features = []
        error_codes = []
        
        # Response handler
        async def handle_response(response):
            try:
                url = response.url
                if 'tiktok.com/api' not in url and 'tiktok.com/aweme' not in url:
                    return
                
                try:
                    body = await response.json()
                except:
                    return
                
                status_code = body.get('status_code') or body.get('error_code')
                status_msg = body.get('status_msg', '').lower()
                
                if status_code:
                    error_codes.append(status_code)
                
                # Check blocks
                if status_code in TikTokErrorCodes.COMMENT_RESTRICTED or 'comment restricted' in status_msg:
                    blocked_features.append('comment')
                    print(f"[FEATURE-CHECK] ❌ Comment blocked (code: {status_code})")
                
                if status_code in TikTokErrorCodes.LIKE_BLOCKED:
                    blocked_features.append('like')
                    print(f"[FEATURE-CHECK] ❌ Like blocked (code: {status_code})")
                
                if status_code in TikTokErrorCodes.FOLLOW_BLOCKED:
                    blocked_features.append('follow')
                    print(f"[FEATURE-CHECK] ❌ Follow blocked (code: {status_code})")
                
                if status_code in TikTokErrorCodes.SHARE_BLOCKED:
                    blocked_features.append('share')
                    print(f"[FEATURE-CHECK] ❌ Share blocked (code: {status_code})")
                
                if status_code in TikTokErrorCodes.LIVE_BLOCKED or 'live stream is not allowed' in status_msg:
                    blocked_features.append('live')
                    print(f"[FEATURE-CHECK] ❌ Live blocked (code: {status_code})")
                
            except:
                pass
        
        page.on('response', handle_response)
        
        # Navigate to profile
        try:
            username = account.lstrip('@')
            await page.goto(f'https://www.tiktok.com/@{username}', wait_until='domcontentloaded', timeout=10000)
            await asyncio.sleep(2)
        except:
            pass
        
        # Check shadowban
        try:
            await page.goto('https://www.tiktok.com/foryou', wait_until='domcontentloaded', timeout=10000)
            await asyncio.sleep(3)
            
            video_count = await page.locator('[data-e2e="recommend-list-item-container"]').count()
            if video_count < 3:
                blocked_features.append('shadowban')
                print(f"[FEATURE-CHECK] ⚠️ Possible shadowban (low feed: {video_count})")
        except:
            pass
        
        # Update result
        result['error_codes'] = list(set(error_codes))
        
        for feature in blocked_features:
            if feature in result['block_detail']:
                result['block_detail'][feature] = True
        
        if any(result['block_detail'].values()):
            result['status'] = AccountStatus.FEATURE_BLOCK
            print(f"[FEATURE-CHECK] ⚠️ Feature blocks: {blocked_features}")
        else:
            result['status'] = AccountStatus.LIVE
            print(f"[FEATURE-CHECK] ✅ All features OK")
        
    except Exception as e:
        print(f"[FEATURE-CHECK] Error: {e}")
        result['status'] = AccountStatus.UNKNOWN
    
    return result


# ============================================================
# 2. CHECK ACCOUNT STATUS (LIVE/DIE/LOGIN FAILED)
# ============================================================

def check_account_status(login_response: Dict[str, Any]) -> Dict[str, Any]:
    """
    Kiểm tra trạng thái account từ login response
    
    Args:
        login_response: Response từ login
    
    Returns:
        {
            'status': str,
            'error_message': str,
            'last_login_time': str
        }
    """
    result = {
        'status': AccountStatus.UNKNOWN,
        'error_message': '',
        'last_login_time': datetime.now().isoformat()
    }
    
    try:
        # From Playwright response
        if isinstance(login_response, dict):
            success = login_response.get('success', False)
            error = login_response.get('error')
            tiktok_data = login_response.get('tiktok', {})
            login_error = tiktok_data.get('login_error', '')
            
            if success:
                result['status'] = AccountStatus.LIVE
                print(f"[ACCOUNT-STATUS] ✅ LIVE")
            else:
                error_msg = str(error or login_error).lower()
                
                if 'captcha' in error_msg or 'verification' in error_msg:
                    result['status'] = AccountStatus.CAPTCHA
                    result['error_message'] = 'Captcha required'
                    print(f"[ACCOUNT-STATUS] 🔒 Captcha")
                
                elif 'banned' in error_msg or 'suspended' in error_msg or 'disabled' in error_msg:
                    result['status'] = AccountStatus.BANNED
                    result['error_message'] = 'Account banned'
                    print(f"[ACCOUNT-STATUS] ❌ BANNED")
                
                elif 'password' in error_msg or 'username' in error_msg or 'invalid' in error_msg:
                    result['status'] = AccountStatus.LOGIN_FAILED
                    result['error_message'] = 'Invalid credentials'
                    print(f"[ACCOUNT-STATUS] ❌ LOGIN FAILED")
                
                elif 'timeout' in error_msg or 'network' in error_msg or 'proxy' in error_msg:
                    result['status'] = AccountStatus.NETWORK_ERROR
                    result['error_message'] = 'Network error'
                    print(f"[ACCOUNT-STATUS] ⚠️ NETWORK ERROR")
                
                else:
                    result['status'] = AccountStatus.LOGIN_FAILED
                    result['error_message'] = error_msg[:200]
                    print(f"[ACCOUNT-STATUS] ❌ FAILED: {error_msg[:100]}")
        
        # From TikTok API
        elif isinstance(login_response, dict) and ('code' in login_response or 'status_code' in login_response):
            code = login_response.get('code') or login_response.get('status_code')
            message = login_response.get('message', '').lower()
            
            if code == TikTokErrorCodes.SUCCESS:
                result['status'] = AccountStatus.LIVE
                print(f"[ACCOUNT-STATUS] ✅ LIVE (code: 0)")
            elif 'captcha' in message:
                result['status'] = AccountStatus.CAPTCHA
                result['error_message'] = message
            elif 'banned' in message:
                result['status'] = AccountStatus.BANNED
                result['error_message'] = message
            else:
                result['status'] = AccountStatus.LOGIN_FAILED
                result['error_message'] = message
        
    except Exception as e:
        print(f"[ACCOUNT-STATUS] Error: {e}")
        result['status'] = AccountStatus.UNKNOWN
        result['error_message'] = str(e)
    
    return result


async def check_tiktok_live_status(page, username: str) -> str:
    """
    Kiểm tra live/die bằng cách check profile
    
    Returns:
        "live" | "die" | "unknown"
    """
    try:
        username = username.lstrip('@')
        profile_url = f"https://www.tiktok.com/@{username}"
        print(f"[LIVE-CHECK] Checking: {profile_url}")
        
        response = await page.goto(profile_url, wait_until='domcontentloaded', timeout=15000)
        
        if response and response.status == 200:
            await asyncio.sleep(2)
            content = await page.content()
            
            if '"userInfo"' in content or 'userInfo' in content:
                print(f"[LIVE-CHECK] ✅ LIVE")
                return AccountStatus.LIVE
            else:
                print(f"[LIVE-CHECK] ❌ DIE (no userInfo)")
                return AccountStatus.DIE
        elif response and response.status == 404:
            print(f"[LIVE-CHECK] ❌ DIE (404)")
            return AccountStatus.DIE
        else:
            print(f"[LIVE-CHECK] ⚠️ Unknown")
            return AccountStatus.UNKNOWN
            
    except Exception as e:
        print(f"[LIVE-CHECK] Error: {e}")
        return AccountStatus.UNKNOWN


# ============================================================
# 3. RELOGIN CHỈ ACCOUNTS BỊ FAIL
# ============================================================

def get_failed_accounts(accounts_data: List[Dict]) -> List[Dict]:
    """
    Lấy danh sách accounts cần relogin
    
    Args:
        accounts_data: List of account dicts
    
    Returns:
        List accounts cần relogin
    """
    failed = []
    
    for account in accounts_data:
        status = account.get('status', '')
        username = account.get('username', 'unknown')
        
        if status in [AccountStatus.LOGIN_FAILED, AccountStatus.NETWORK_ERROR]:
            failed.append(account)
            print(f"[RELOGIN] {username} needs relogin (status: {status})")
        elif status == AccountStatus.LIVE:
            print(f"[RELOGIN] Skip {username} (already live)")
    
    print(f"[RELOGIN] Found {len(failed)} accounts need relogin")
    return failed


async def handle_relogin(page, account_data: Dict, login_function) -> Dict[str, Any]:
    """
    Xử lý relogin cho một account
    
    Args:
        page: Playwright Page
        account_data: Account data
        login_function: Async login function
    
    Returns:
        Updated account data
    """
    username = account_data.get('username', 'unknown')
    print(f"[RELOGIN] Attempting: {username}")
    
    try:
        login_result = await login_function(page, account_data)
        status_result = check_account_status(login_result)
        
        if status_result['status'] == AccountStatus.LIVE:
            account_data['status'] = AccountStatus.LIVE
            account_data['error_message'] = ''
            account_data['last_login_time'] = datetime.now().isoformat()
            print(f"[RELOGIN] ✅ {username} SUCCESS")
        else:
            if status_result['status'] in [AccountStatus.BANNED, AccountStatus.LOGIN_FAILED]:
                account_data['status'] = AccountStatus.DIE
            else:
                account_data['status'] = status_result['status']
            
            account_data['error_message'] = status_result['error_message']
            account_data['last_login_time'] = datetime.now().isoformat()
            print(f"[RELOGIN] ❌ {username} FAILED: {status_result['status']}")
        
    except Exception as e:
        print(f"[RELOGIN] Error {username}: {e}")
        account_data['status'] = AccountStatus.NETWORK_ERROR
        account_data['error_message'] = str(e)
    
    return account_data


# ============================================================
# 4. STORAGE - LƯU KẾT QUẢ VÀO DATABASE
# ============================================================

def save_account_result(account: str, result_data: Dict[str, Any], storage_path: str = 'data/tiktok_accounts.json'):
    """
    Lưu kết quả vào JSON database
    
    Args:
        account: Account username/email
        result_data: Data to save
        storage_path: Path to JSON file
    """
    try:
        os.makedirs(os.path.dirname(storage_path), exist_ok=True)
        
        # Load existing
        accounts_db = {}
        if os.path.exists(storage_path):
            try:
                with open(storage_path, 'r', encoding='utf-8') as f:
                    accounts_db = json.load(f)
            except:
                accounts_db = {}
        
        # Update
        if account not in accounts_db:
            accounts_db[account] = {}
        
        accounts_db[account].update(result_data)
        accounts_db[account]['last_updated'] = datetime.now().isoformat()
        
        # Save
        with open(storage_path, 'w', encoding='utf-8') as f:
            json.dump(accounts_db, f, indent=2, ensure_ascii=False)
        
        print(f"[STORAGE] ✅ Saved: {account}")
        
    except Exception as e:
        print(f"[STORAGE] Error: {e}")


def load_accounts_data(storage_path: str = 'data/tiktok_accounts.json') -> Dict[str, Any]:
    """Load accounts data from storage"""
    try:
        if os.path.exists(storage_path):
            with open(storage_path, 'r', encoding='utf-8') as f:
                return json.load(f)
    except:
        pass
    return {}


def format_login_error(account: str, error: str) -> Dict[str, Any]:
    """
    Format kết quả login lỗi
    
    Returns:
        {
            "account": "xxx",
            "status": "login_failed",
            "error": "wrong password",
            "timestamp": "..."
        }
    """
    return {
        'account': account,
        'status': AccountStatus.LOGIN_FAILED,
        'error': error,
        'timestamp': datetime.now().isoformat()
    }


def format_login_success(account: str, features: Dict[str, bool]) -> Dict[str, Any]:
    """
    Format kết quả login thành công
    
    Returns:
        {
            "account": "xxx",
            "status": "live",
            "features": {
                "comment": true/false,
                "like": true/false,
                "follow": true/false,
                "share": true/false,
                "live": true/false
            }
        }
    """
    return {
        'account': account,
        'status': AccountStatus.LIVE,
        'features': features,
        'timestamp': datetime.now().isoformat()
    }


# ============================================================
# 5. MAIN INTEGRATION - GỌI SAU KHI LOGIN
# ============================================================

async def check_account_after_login(page, account: str, login_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Hàm tổng hợp - gọi sau khi login xong
    
    Usage:
        login_result = await your_login_function(...)
        full_result = await check_account_after_login(page, account, login_result)
        save_account_result(account, full_result)
    
    Args:
        page: Playwright Page
        account: Account username/email
        login_result: Kết quả từ login function
    
    Returns:
        Complete result với tất cả thông tin
    """
    print(f"\n{'='*70}")
    print(f"[POST-LOGIN] Checking: {account}")
    print(f"{'='*70}")
    
    # Step 1: Check status
    status_result = check_account_status(login_result)
    
    # Step 2: Check features (chỉ khi live)
    feature_result = None
    if status_result['status'] == AccountStatus.LIVE:
        feature_result = await check_feature_block(page, account)
        
        if feature_result['status'] == AccountStatus.FEATURE_BLOCK:
            status_result['status'] = AccountStatus.FEATURE_BLOCK
    
    # Step 3: Format final result
    final_result = {
        'account': account,
        'status': status_result['status'],
        'error_message': status_result.get('error_message', ''),
        'last_login_time': status_result.get('last_login_time'),
        'timestamp': datetime.now().isoformat()
    }
    
    # Add features if checked
    if feature_result:
        final_result['features'] = {
            'comment': not feature_result['block_detail']['comment'],
            'like': not feature_result['block_detail']['like'],
            'follow': not feature_result['block_detail']['follow'],
            'share': not feature_result['block_detail']['share'],
            'live': not feature_result['block_detail']['live']
        }
        final_result['block_detail'] = feature_result['block_detail']
        final_result['error_codes'] = feature_result['error_codes']
    
    print(f"[POST-LOGIN] Final status: {final_result['status']}")
    print(f"{'='*70}\n")
    
    return final_result


# ============================================================
# LEGACY COMPATIBILITY - Giữ tương thích với code cũ
# ============================================================

def create_tiktok_result(
    success: bool,
    page: Optional[Any] = None,
    error: Optional[Exception] = None,
    username: Optional[str] = None,
    check_live_status: bool = True
) -> Dict[str, Any]:
    """
    Legacy function - tương thích với code cũ
    """
    result = {
        'success': success,
        'page': page,
        'account_status': AccountStatus.UNKNOWN,
        'tiktok': {
            'login_error': None,
            'message': ''
        }
    }
    
    if success:
        result['tiktok']['message'] = 'Login success'
        result['account_status'] = AccountStatus.LIVE
    else:
        result['tiktok']['message'] = 'Login failed'
        result['account_status'] = AccountStatus.DIE
        if error:
            result['tiktok']['login_error'] = str(error)
    
    return result
