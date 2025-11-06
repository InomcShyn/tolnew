import os
import json
import socket
import time

def _pick_free_port():
    """Pick a free port for remote debugging"""
    s = socket.socket()
    s.bind(("", 0))
    port = s.getsockname()[1]
    s.close()
    return port

def launch_chrome_profile(manager, profile_name, hidden=True, auto_login=False, login_data=None, start_url=None, optimized_mode=False, ultra_low_memory=False):
    """
    Launch Chrome profile - calls manager's launch_chrome_profile directly.
    Since wrapper was removed, we can call it directly without recursion risk.
    Ensures start_url is navigated for livestream if needed.
    """
    try:
        # Call manager's launch_chrome_profile directly (no wrapper anymore)
        result = manager.launch_chrome_profile(
            profile_name=profile_name,
            hidden=hidden,
            auto_login=auto_login,
            login_data=login_data,
            start_url=start_url,
            optimized_mode=optimized_mode,
            ultra_low_memory=ultra_low_memory,
        )
        
        # Double-check navigation if driver exists and start_url provided
        # (Original function should already navigate, but ensure it)
        if isinstance(result, tuple):
            success, driver_or_msg = result
            if success and start_url and hasattr(driver_or_msg, 'get'):
                try:
                    current_url = driver_or_msg.current_url if hasattr(driver_or_msg, 'current_url') else None
                    if current_url and start_url not in current_url:
                        print(f"[LIVESTREAM] [NAVIGATE] Double-check: Navigating to {start_url}")
                        driver_or_msg.get(start_url)
                        time.sleep(2)
                        print(f"[SUCCESS] [LIVESTREAM] Navigated to: {start_url}")
                except Exception as nav_err:
                    print(f"[WARNING] [LIVESTREAM] Navigation check error: {nav_err}")
            return result
        return result
        
    except RecursionError as re:
        print("[CRITICAL] [TILE-AUTO] Recursion detected!")
        return False, f"Recursion error: {re}"
    except Exception as e:
        print(f"[ERROR] [LAUNCH-AUTO] {e}")
        import traceback
        traceback.print_exc()
        return False, str(e)
