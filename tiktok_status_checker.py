"""
TikTok Status Checker - Kiểm tra trạng thái tài khoản TikTok
"""
import asyncio
from typing import Dict, Optional, Any


async def check_tiktok_live_status(page, username: str) -> str:
    """
    Kiểm tra trạng thái live/die của tài khoản TikTok
    
    Args:
        page: Playwright Page object
        username: TikTok username (không có @)
    
    Returns:
        "live" | "die" | "unknown"
    """
    try:
        # Remove @ if present
        username = username.lstrip('@')
        
        profile_url = f"https://www.tiktok.com/@{username}"
        print(f"[TIKTOK-STATUS] Checking profile: {profile_url}")
        
        # Navigate to profile
        response = await page.goto(profile_url, wait_until='domcontentloaded', timeout=15000)
        
        # Check HTTP status
        if response and response.status == 200:
            # Wait a bit for page to load
            await asyncio.sleep(2)
            
            # Get page content
            content = await page.content()
            
            # Check if userInfo exists in HTML
            if '"userInfo"' in content or 'userInfo' in content:
                print(f"[TIKTOK-STATUS] ✅ Account is LIVE")
                return "live"
            else:
                print(f"[TIKTOK-STATUS] ❌ Account is DIE (no userInfo)")
                return "die"
        elif response and response.status == 404:
            print(f"[TIKTOK-STATUS] ❌ Account is DIE (404)")
            return "die"
        else:
            print(f"[TIKTOK-STATUS] ⚠️ Unknown status (HTTP {response.status if response else 'None'})")
            return "unknown"
            
    except asyncio.TimeoutError:
        print(f"[TIKTOK-STATUS] ⚠️ Timeout checking profile")
        return "unknown"
    except Exception as e:
        print(f"[TIKTOK-STATUS] ⚠️ Error checking profile: {e}")
        return "unknown"


def create_tiktok_result(
    success: bool,
    page: Optional[Any] = None,
    error: Optional[Exception] = None,
    username: Optional[str] = None,
    check_live_status: bool = True
) -> Dict[str, Any]:
    """
    Tạo result object với thông tin TikTok status
    
    Args:
        success: Login có thành công không
        page: Playwright Page object (nếu có)
        error: Exception nếu có lỗi
        username: TikTok username để check live status
        check_live_status: Có check live status không (chỉ khi success=True)
    
    Returns:
        Dict với structure:
        {
            'success': bool,
            'page': Page object hoặc None,
            'account_status': 'live' | 'die' | 'unknown',
            'tiktok': {
                'login_error': str hoặc None,
                'message': str
            }
        }
    """
    result = {
        'success': success,
        'page': page,
        'account_status': 'unknown',
        'tiktok': {
            'login_error': None,
            'message': ''
        }
    }
    
    if success:
        # Login thành công
        result['tiktok']['message'] = 'Login success'
        result['tiktok']['login_error'] = None
        
        # Check live status nếu được yêu cầu và có username
        if check_live_status and username and page:
            try:
                # Run async check in sync context
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # Already in async context, create task
                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(
                            asyncio.run,
                            check_tiktok_live_status(page, username)
                        )
                        live_status = future.result(timeout=20)
                else:
                    # Not in async context, run directly
                    live_status = loop.run_until_complete(
                        check_tiktok_live_status(page, username)
                    )
                
                result['account_status'] = live_status
                print(f"[TIKTOK-RESULT] Account status: {live_status}")
                
            except Exception as e:
                print(f"[TIKTOK-RESULT] Could not check live status: {e}")
                result['account_status'] = 'unknown'
        else:
            # Không check live status, mặc định là live nếu login thành công
            result['account_status'] = 'live'
    else:
        # Login thất bại
        result['tiktok']['message'] = 'Login failed'
        result['account_status'] = 'die'
        
        # Lưu error message
        if error:
            error_msg = str(error)
            result['tiktok']['login_error'] = error_msg
            print(f"[TIKTOK-RESULT] Login error: {error_msg}")
        else:
            result['tiktok']['login_error'] = 'Unknown error'
    
    return result


async def check_tiktok_live_status_async(page, username: str) -> str:
    """
    Async version of check_tiktok_live_status
    Alias for compatibility
    """
    return await check_tiktok_live_status(page, username)
