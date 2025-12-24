"""
TikTok Login Wrapper - Wrap login results với TikTok status check
"""
from typing import Tuple, Any, Optional, Dict
from core.tiktok_status_checker import create_tiktok_result, check_tiktok_live_status
import asyncio


def wrap_login_result(
    success: bool,
    result: Any,
    username: Optional[str] = None,
    check_live: bool = True
) -> Tuple[bool, Any]:
    """
    Wrap kết quả login với TikTok status information
    
    Args:
        success: Login có thành công không
        result: Result object (Page hoặc error message)
        username: TikTok username để check live status
        check_live: Có check live status không
    
    Returns:
        Tuple (success, enhanced_result)
        enhanced_result có thêm fields:
        - account_status: 'live' | 'die' | 'unknown'
        - tiktok: {'login_error': str|None, 'message': str}
    """
    # Nếu result đã là dict và có 'page' key, extract page
    page = None
    if isinstance(result, dict) and 'page' in result:
        page = result['page']
    elif hasattr(result, 'goto'):  # Playwright Page object
        page = result
    
    # Tạo enhanced result
    if success:
        # Login thành công
        enhanced_result = {
            'success': True,
            'page': page or result,
            'account_status': 'unknown',
            'tiktok': {
                'login_error': None,
                'message': 'Login success'
            }
        }
        
        # Check live status nếu có username và page
        if check_live and username and page:
            try:
                print(f"[TIKTOK-WRAPPER] Checking live status for @{username}...")
                
                # Check if we're in async context
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        # Create task for async check
                        async def check_async():
                            return await check_tiktok_live_status(page, username)
                        
                        # Run in thread pool to avoid blocking
                        import concurrent.futures
                        with concurrent.futures.ThreadPoolExecutor() as executor:
                            future = executor.submit(asyncio.run, check_async())
                            live_status = future.result(timeout=20)
                    else:
                        # Run directly
                        live_status = loop.run_until_complete(
                            check_tiktok_live_status(page, username)
                        )
                except RuntimeError:
                    # No event loop, create new one
                    live_status = asyncio.run(check_tiktok_live_status(page, username))
                
                enhanced_result['account_status'] = live_status
                print(f"[TIKTOK-WRAPPER] Account status: {live_status}")
                
            except Exception as e:
                print(f"[TIKTOK-WRAPPER] Could not check live status: {e}")
                enhanced_result['account_status'] = 'live'  # Default to live if check fails
        else:
            # Không check, mặc định là live
            enhanced_result['account_status'] = 'live'
        
        return True, enhanced_result
    else:
        # Login thất bại
        error_msg = str(result) if result else 'Unknown error'
        
        enhanced_result = {
            'success': False,
            'page': None,
            'account_status': 'die',
            'tiktok': {
                'login_error': error_msg,
                'message': 'Login failed'
            },
            'error': error_msg  # Keep original error for compatibility
        }
        
        return False, enhanced_result


async def wrap_login_result_async(
    success: bool,
    result: Any,
    username: Optional[str] = None,
    check_live: bool = True
) -> Tuple[bool, Any]:
    """
    Async version of wrap_login_result
    """
    page = None
    if isinstance(result, dict) and 'page' in result:
        page = result['page']
    elif hasattr(result, 'goto'):
        page = result
    
    if success:
        enhanced_result = {
            'success': True,
            'page': page or result,
            'account_status': 'unknown',
            'tiktok': {
                'login_error': None,
                'message': 'Login success'
            }
        }
        
        if check_live and username and page:
            try:
                print(f"[TIKTOK-WRAPPER] Checking live status for @{username}...")
                live_status = await check_tiktok_live_status(page, username)
                enhanced_result['account_status'] = live_status
                print(f"[TIKTOK-WRAPPER] Account status: {live_status}")
            except Exception as e:
                print(f"[TIKTOK-WRAPPER] Could not check live status: {e}")
                enhanced_result['account_status'] = 'live'
        else:
            enhanced_result['account_status'] = 'live'
        
        return True, enhanced_result
    else:
        error_msg = str(result) if result else 'Unknown error'
        enhanced_result = {
            'success': False,
            'page': None,
            'account_status': 'die',
            'tiktok': {
                'login_error': error_msg,
                'message': 'Login failed'
            },
            'error': error_msg
        }
        return False, enhanced_result
