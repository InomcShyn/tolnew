"""
Auto-close Windows Security dialog
Tự động click Cancel button khi Windows Security dialog xuất hiện
"""
import time
import threading

try:
    import pyautogui
    import win32gui
    import win32con
    MODULES_AVAILABLE = True
except ImportError:
    MODULES_AVAILABLE = False
    print("[AUTO-CLOSE] Warning: pyautogui or pywin32 not installed")


class WindowsSecurityCloser:
    """Auto-close Windows Security dialogs"""
    
    def __init__(self):
        self.running = False
        self.thread = None
    
    def find_and_close_security_dialog(self):
        """Find and close Windows Security dialog"""
        try:
            # Find window with title containing "Windows Security"
            def callback(hwnd, windows):
                if win32gui.IsWindowVisible(hwnd):
                    title = win32gui.GetWindowText(hwnd)
                    if "Windows Security" in title or "Making sure it's you" in title:
                        windows.append(hwnd)
                return True
            
            windows = []
            win32gui.EnumWindows(callback, windows)
            
            if windows:
                for hwnd in windows:
                    print(f"[AUTO-CLOSE] Found Windows Security dialog, closing...")
                    
                    # Try to find Cancel button and click it
                    try:
                        # Bring window to front
                        win32gui.SetForegroundWindow(hwnd)
                        time.sleep(0.2)
                        
                        # Press Escape key to close
                        pyautogui.press('escape')
                        print(f"[AUTO-CLOSE] ✅ Pressed Escape to close dialog")
                        
                        # Alternative: Click Cancel button
                        # Find button position and click
                        time.sleep(0.1)
                        
                        # If Escape didn't work, try clicking Cancel
                        if win32gui.IsWindow(hwnd) and win32gui.IsWindowVisible(hwnd):
                            # Get window rect
                            rect = win32gui.GetWindowRect(hwnd)
                            x, y, x2, y2 = rect
                            
                            # Cancel button is usually at bottom center
                            cancel_x = (x + x2) // 2
                            cancel_y = y2 - 50
                            
                            pyautogui.click(cancel_x, cancel_y)
                            print(f"[AUTO-CLOSE] ✅ Clicked Cancel button")
                        
                    except Exception as e:
                        print(f"[AUTO-CLOSE] Error clicking Cancel: {e}")
                        
                        # Last resort: Close window forcefully
                        try:
                            win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
                            print(f"[AUTO-CLOSE] ✅ Closed window forcefully")
                        except:
                            pass
                
                return True
            
        except Exception as e:
            print(f"[AUTO-CLOSE] Error: {e}")
        
        return False
    
    def monitor_loop(self):
        """Monitor and close dialogs in loop"""
        print(f"[AUTO-CLOSE] Started monitoring for Windows Security dialogs...")
        
        while self.running:
            try:
                self.find_and_close_security_dialog()
                time.sleep(0.5)  # Check every 0.5 seconds
            except Exception as e:
                print(f"[AUTO-CLOSE] Monitor error: {e}")
                time.sleep(1)
        
        print(f"[AUTO-CLOSE] Stopped monitoring")
    
    def start(self):
        """Start monitoring"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self.monitor_loop, daemon=True)
            self.thread.start()
            print(f"[AUTO-CLOSE] ✅ Auto-close enabled")
    
    def stop(self):
        """Stop monitoring"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
        print(f"[AUTO-CLOSE] Auto-close disabled")


# Global instance
_closer = None


def start_auto_close():
    """Start auto-close Windows Security dialogs"""
    if not MODULES_AVAILABLE:
        return False
    
    global _closer
    if _closer is None:
        _closer = WindowsSecurityCloser()
    _closer.start()
    return True


def stop_auto_close():
    """Stop auto-close"""
    global _closer
    if _closer:
        _closer.stop()


if __name__ == "__main__":
    # Test mode
    print("Testing auto-close Windows Security dialog...")
    print("Open a Windows Security dialog to test...")
    
    closer = WindowsSecurityCloser()
    closer.start()
    
    try:
        # Run for 60 seconds
        time.sleep(60)
    except KeyboardInterrupt:
        print("\nStopping...")
    
    closer.stop()
