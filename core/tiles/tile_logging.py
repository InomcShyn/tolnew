import os
from datetime import datetime

# === Logging helpers extracted from chrome_manager.py ===

def append_app_log(manager, profile_path: str, message: str) -> None:
    try:
        logs_dir = os.path.join(profile_path, 'logs')
        os.makedirs(logs_dir, exist_ok=True)
        log_file = os.path.join(logs_dir, 'app_launch.log')
        ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"[{ts}] {message}\n")
    except Exception:
        pass


def get_chrome_log_path(manager, profile_name: str) -> str:
    try:
        profile_path = os.path.join(manager.profiles_dir, profile_name)
        logs_dir = os.path.join(profile_path, 'logs')
        os.makedirs(logs_dir, exist_ok=True)
        return os.path.join(logs_dir, 'chrome.log')
    except Exception:
        return os.path.join(manager.profiles_dir, profile_name, 'logs', 'chrome.log')


def read_chrome_log(manager, profile_name: str, tail_lines: int = 200) -> str:
    try:
        log_path = get_chrome_log_path(manager, profile_name)
        if not os.path.exists(log_path):
            return f"[LOG] No log file: {log_path}"
        with open(log_path, 'r', encoding='utf-8', errors='replace') as f:
            lines = f.readlines()
        tail = lines[-tail_lines:] if len(lines) > tail_lines else lines
        return ''.join(tail)
    except Exception as e:
        return f"[LOG] Cannot read chrome.log: {e}"
