#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TikTok Feature Block Checker
Kiểm tra các tính năng bị block của tài khoản TikTok
KHÔNG thay đổi flow hiện tại - chỉ THÊM logic check
"""

import asyncio
import json
from typing import Dict, Optional, Any, Tuple
from datetime import datetime


# ============================================================
# YÊU CẦU 1: CHECK FEATURE BLOCK
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
                'comment': bool,  # True = bị block
                'like': bool,
                'follow': bool,
                'share': bool,
                'live': bool,
                'shadowban': bool
            },
            'error_codes': [list of error codes],
            'timestamp': timestamp
        }
    """
    result = {
        'status': 'live',
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
        
        # Lắng nghe tất cả API responses
        blocked_features = []
        error_codes = []
        
        async def handle_response(response):
            try:
                url = response.url
                
                # Chỉ check TikTok API responses
                if 'tiktok.com/api' not in url and 'tiktok.com/aweme' not in url:
                    return
                
                # Get response body
                try:
                    body = await response.json()
                except:
                    return
                
                # Check error codes
                status_code = body.get('status_code') or body.get('error_code')
                status_msg = body.get('status_msg', '').lower()
                
                if status_code:
                    error_codes.append(status_code)
                
                # Check comment block
                if status_code in [2433, 2431] or 'comment restricted' in status_msg:
                    blocked_features.append('comment')
                    print(f"[FEATURE-CHECK] ❌ Comment blocked (code: {status_code})")
                
                # Check like block
                if status_code in [2340, 3002041]:
                    blocked_features.append('like')
                    print(f"[FEATURE-CHECK] ❌ Like blocked (code: {status_code})")
                
                # Check follow block
                if status_code in [20022, 20009]:
                    blocked_features.append('follow')
                    print(f"[FEATURE-CHECK] ❌ Follow blocked (code: {status_code})")
                
                # Check share block
                if status_code == 3002080:
                    blocked_features.append('share')
                    print(f"[FEATURE-CHECK] ❌ Share blocked (code: {status_code})")
                
                # Check live block
                if status_code == 200004 or 'live stream is not allowed' in status_msg:
                    blocked_features.append('live')
                    print(f"[FEATURE-CHECK] ❌ Live blocked (code: {status_code})")
                
            except Exception as e:
                pass  # Ignore errors in response handler
        
        # Attach response listener
        page.on('response', handle_response)
        
        # Navigate to profile to trigger API calls
        try:
            username = account.lstrip('@')
            await page.goto(f'https://www.tiktok.com/@{username}', wait_until='domcontentloaded', timeout=10000)
            await asyncio.sleep(2)  # Wait for API calls
        except:
            pass
        
        # Check shadowban (feed trả về toàn video rác)
        try:
            # Navigate to For You page
            await page.goto('https://www.tiktok.com/foryou', wait_until='domcontentloaded', timeout=10000)
            await asyncio.sleep(3)
            
            # Check if feed is empty or has very few videos
            video_count = await page.locator('[data-e2e="recommend-list-item-container"]').count()
            if video_count < 3:
                blocked_features.append('shadowban')
                print(f"[FEATURE-CHECK] ⚠️ Possible shadowban (low feed count: {video_count})")
        except:
            pass
        
        # Update result
        result['error_codes'] = list(set(error_codes))
        
        for feature in blocked_features:
            if feature in result['block_detail']:
                result['block_detail'][feature] = True
        
        # Determine overall status
        if any(result['block_detail'].values()):
            result['status'] = 'feature_block'
            print(f"[FEATURE-CHECK] ⚠️ Account has feature blocks: {blocked_features}")
        else:
            result['status'] = 'live'
            print(f"[FEATURE-CHECK] ✅ All features working")
        
    except Exception as e:
        print(f"[FEATURE-CHECK] Error: {e}")
        result['status'] = 'unknown'
    
    return result


# ============================================================
# YÊU CẦU 2: CHECK ACCOUNT STATUS (LIVE/DIE/LOGIN FAILED)
# ============================================================

def check_account_status(login_response: Dict[str, Any]) -> Dict[str, Any]:
    """
    Kiểm tra trạng thái account từ login response
    
    Args:
        login_response: Response từ TikTok login API hoặc Playwright
    
    Returns:
        {
            'status': 'live' | 'captcha' | 'banned' | 'login_failed' | 'network_error',
            'error_message': str,
            'last_login_time': timestamp
        }
    """
    result = {
        'status': 'unknown',
        'error_message': '',
        'last_login_time': datetime.now().isoformat()
    }
    
    try:
        # Check if login_response is from Playwright (has 'success' key)
        if isinstance(login_response, dict):
            success = login_response.get('success', False)
            error = login_response.get('error')
            tiktok_data = login_response.get('tiktok', {})
            login_error = tiktok_data.get('login_error', '')
            
            if success:
                # Login thành công
                result['status'] = 'live'
                result['error_message'] = ''
                print(f"[ACCOUNT-STATUS] ✅ Account is LIVE")
                
            else:
                # Login thất bại - phân tích lỗi
                error_msg = str(error or login_error).lower()
                
                # Check captcha
                if 'captcha' in error_msg or 'verification' in error_msg:
                    result['status'] = 'captcha'
                    result['error_message'] = 'Captcha required'
                    print(f"[ACCOUNT-STATUS] 🔒 Captcha required")
                
                # Check banned
                elif 'banned' in error_msg or 'suspended' in error_msg or 'disabled' in error_msg:
                    result['status'] = 'banned'
                    result['error_message'] = 'Account banned'
                    print(f"[ACCOUNT-STATUS] ❌ Account BANNED")
                
                # Check invalid credentials
                elif 'password' in error_msg or 'username' in error_msg or 'invalid' in error_msg or 'incorrect' in error_msg:
                    result['status'] = 'login_failed'
                    result['error_message'] = 'Invalid username/password'
                    print(f"[ACCOUNT-STATUS] ❌ LOGIN FAILED (wrong credentials)")
                
                # Check network errors
                elif 'timeout' in error_msg or 'network' in error_msg or 'connection' in error_msg or 'proxy' in error_msg:
                    result['status'] = 'network_error'
                    result['error_message'] = 'Network/proxy error'
                    print(f"[ACCOUNT-STATUS] ⚠️ NETWORK ERROR")
                
                else:
                    # Unknown error
                    result['status'] = 'login_failed'
                    result['error_message'] = error_msg[:200]  # Limit length
                    print(f"[ACCOUNT-STATUS] ❌ LOGIN FAILED: {error_msg[:100]}")
        
        # Check if login_response is from TikTok API (has 'code' or 'status_code')
        elif isinstance(login_response, dict) and ('code' in login_response or 'status_code' in login_response):
            code = login_response.get('code') or login_response.get('status_code')
            message = login_response.get('message', '').lower()
            
            if code == 0:
                result['status'] = 'live'
                print(f"[ACCOUNT-STATUS] ✅ Account is LIVE (code: 0)")
            elif 'captcha' in message:
                result['status'] = 'captcha'
                result['error_message'] = message
            elif 'banned' in message or 'suspended' in message:
                result['status'] = 'banned'
                result['error_message'] = message
            else:
                result['status'] = 'login_failed'
                result['error_message'] = message
        
    except Exception as e:
        print(f"[ACCOUNT-STATUS] Error checking status: {e}")
        result['status'] = 'unknown'
        result['error_message'] = str(e)
    
    return result


# ============================================================
# YÊU CẦU 3: RELOGIN CHỈ NHỮNG ACCOUNT BỊ FAIL
# ============================================================

def get_failed_accounts(accounts_data: list) -> list:
    """
    Lấy danh sách accounts cần relogin (chỉ những account bị fail)
    
    Args:
        accounts_data: List of account dicts với status
    
    Returns:
        List of accounts cần relogin
    """
    failed_accounts = []
    
    for account in accounts_data:
        status = account.get('status', '')
        
        # CHỈ relogin những account bị fail hoặc network error
        if status in ['login_failed', 'network_error']:
            failed_accounts.append(account)
            print(f"[RELOGIN] Account {account.get('username', 'unknown')} needs relogin (status: {status})")
        elif status == 'live':
            print(f"[RELOGIN] Skip {account.get('username', 'unknown')} (already live)")
    
    print(f"[RELOGIN] Found {len(failed_accounts)} accounts need relogin")
    return failed_accounts


async def handle_relogin(page, account_data: Dict, login_function) -> Dict[str, Any]:
    """
    Xử lý relogin cho một account
    
    Args:
        page: Playwright Page object
        account_data: Account data dict
        login_function: Hàm login hiện tại (async function)
    
    Returns:
        Updated account data với status mới
    """
    username = account_data.get('username', 'unknown')
    print(f"[RELOGIN] Attempting relogin for: {username}")
    
    try:
        # Gọi hàm login hiện tại
        login_result = await login_function(page, account_data)
        
        # Check status
        status_result = check_account_status(login_result)
        
        if status_result['status'] == 'live':
            # Relogin thành công
            account_data['status'] = 'live'
            account_data['error_message'] = ''
            account_data['last_login_time'] = datetime.now().isoformat()
            print(f"[RELOGIN] ✅ {username} relogin SUCCESS")
        else:
            # Relogin vẫn fail
            if status_result['status'] in ['banned', 'login_failed']:
                # Chuyển sang DIE nếu banned hoặc sai password
                account_data['status'] = 'die'
            else:
                # Giữ nguyên status nếu là network error hoặc captcha
                account_data['status'] = status_result['status']
            
            account_data['error_message'] = status_result['error_message']
            account_data['last_login_time'] = datetime.now().isoformat()
            print(f"[RELOGIN] ❌ {username} relogin FAILED: {status_result['status']}")
        
    except Exception as e:
        print(f"[RELOGIN] Error relogin {username}: {e}")
        account_data['status'] = 'network_error'
        account_data['error_message'] = str(e)
    
    return account_data


# ============================================================
# YÊU CẦU 4: LƯU KẾT QUẢ VÀO DATABASE/STORAGE
# ============================================================

def save_account_result(account: str, result_data: Dict[str, Any], storage_path: str = 'data/tiktok_accounts.json'):
    """
    Lưu kết quả vào file JSON (database)
    
    Args:
        account: Account username/email
        result_data: Data cần lưu
        storage_path: Path to JSON file
    """
    import os
    
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(storage_path), exist_ok=True)
        
        # Load existing data
        accounts_db = {}
        if os.path.exists(storage_path):
            try:
                with open(storage_path, 'r', encoding='utf-8') as f:
                    accounts_db = json.load(f)
            except:
                accounts_db = {}
        
        # Update account data
        if account not in accounts_db:
            accounts_db[account] = {}
        
        accounts_db[account].update(result_data)
        accounts_db[account]['last_updated'] = datetime.now().isoformat()
        
        # Save to file
        with open(storage_path, 'w', encoding='utf-8') as f:
            json.dump(accounts_db, f, indent=2, ensure_ascii=False)
        
        print(f"[STORAGE] ✅ Saved result for {account}")
        
    except Exception as e:
        print(f"[STORAGE] Error saving result: {e}")


def format_login_error_result(account: str, error: str) -> Dict[str, Any]:
    """
    Format kết quả khi login lỗi (YÊU CẦU 4)
    
    Returns:
        {
            "account": "xxx",
            "status": "login_failed",
            "error": "wrong password",
            "timestamp": Date.now()
        }
    """
    return {
        'account': account,
        'status': 'login_failed',
        'error': error,
        'timestamp': datetime.now().isoformat()
    }


def format_login_success_result(account: str, features: Dict[str, bool]) -> Dict[str, Any]:
    """
    Format kết quả khi login OK (YÊU CẦU 4)
    
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
        'status': 'live',
        'features': features,
        'timestamp': datetime.now().isoformat()
    }


# ============================================================
# HELPER: INTEGRATE VÀO FLOW HIỆN TẠI
# ============================================================

async def check_account_after_login(page, account: str, login_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Hàm tổng hợp - gọi sau khi login xong
    Tích hợp tất cả các check vào một hàm duy nhất
    
    Usage trong code hiện tại:
        login_result = await your_login_function(...)
        full_result = await check_account_after_login(page, account, login_result)
        save_account_result(account, full_result)
    
    Args:
        page: Playwright Page object
        account: Account username/email
        login_result: Kết quả từ hàm login hiện tại
    
    Returns:
        Complete result với tất cả thông tin
    """
    print(f"\n{'='*70}")
    print(f"[POST-LOGIN-CHECK] Checking account: {account}")
    print(f"{'='*70}")
    
    # Step 1: Check account status
    status_result = check_account_status(login_result)
    
    # Step 2: Check feature blocks (chỉ khi login thành công)
    feature_result = None
    if status_result['status'] == 'live':
        feature_result = await check_feature_block(page, account)
        
        # Update status nếu có feature block
        if feature_result['status'] == 'feature_block':
            status_result['status'] = 'feature_block'
    
    # Step 3: Format final result
    final_result = {
        'account': account,
        'status': status_result['status'],
        'error_message': status_result.get('error_message', ''),
        'last_login_time': status_result.get('last_login_time'),
        'timestamp': datetime.now().isoformat()
    }
    
    # Add feature details if checked
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
    
    print(f"[POST-LOGIN-CHECK] Final status: {final_result['status']}")
    print(f"{'='*70}\n")
    
    return final_result
