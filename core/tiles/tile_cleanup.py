import os
import shutil
import time


def _safe_remove(path: str, retries: int = 3, delay_sec: float = 0.5) -> bool:
    """Safely remove file if exists with simple retry to handle transient locks."""
    if not path or not os.path.exists(path):
        return True
    for attempt in range(max(1, int(retries))):
        try:
            os.remove(path)
            return True
        except Exception:
            time.sleep(delay_sec)
    # Final attempt: rename then delete on next start
    try:
        bak = f"{path}.bak_{int(time.time())}"
        os.replace(path, bak)
        return True
    except Exception:
        return False


def clear_browsing_history(manager, profile_names):
    """
    Clear browsing history for given profiles without removing cache or saved passwords.

    Targets (if exist):
      Default/History,
      Default/History Provider Cache,
      Default/Visited Links,
      Default/Top Sites,
      Default/Shortcuts

    Returns: (success: bool, message: str)
    """
    if not profile_names:
        return False, "No profiles selected"

    targets = [
        os.path.join("Default", "History"),
        os.path.join("Default", "History Provider Cache"),
        os.path.join("Default", "Visited Links"),
        os.path.join("Default", "Top Sites"),
        os.path.join("Default", "Shortcuts"),
    ]

    cleaned = []
    errors = []

    for profile_name in profile_names:
        try:
            profile_path = manager.get_profile_path(profile_name)
            removed_any = False
            for rel in targets:
                fp = os.path.join(profile_path, rel)
                if os.path.exists(fp):
                    ok = _safe_remove(fp)
                    removed_any = removed_any or ok
            if removed_any:
                cleaned.append(profile_name)
            else:
                # Nothing to remove is also ok
                cleaned.append(profile_name)
        except Exception as e:
            errors.append((profile_name, str(e)))

    if errors:
        return False, f"Cleaned {len(cleaned)}; errors: {len(errors)}"
    return True, f"Cleaned history for {len(cleaned)} profiles"


def _seconds_until(hour: int, minute: int) -> float:
    try:
        import datetime as _dt
        now = _dt.datetime.now()
        target = now.replace(hour=int(hour), minute=int(minute), second=0, microsecond=0)
        if target <= now:
            target = target + _dt.timedelta(days=1)
        return (target - now).total_seconds()
    except Exception:
        # Default: 1 hour later
        return 3600.0


def start_daily_history_cleanup(manager, hour: int = 3, minute: int = 0, profiles=None, jitter_sec: int = 90):
    """
    Start a background daemon thread that clears browsing history daily at given local time.
    - Preserves cookies, passwords, and cache.
    - If profiles is None, applies to all profiles.
    """
    try:
        import threading, random
        if getattr(manager, '_daily_history_cleanup_thread', None):
            # Already running
            return False, "Daily cleanup already running"
        stop_event = threading.Event()
        manager._daily_history_cleanup_stop = stop_event
        def _worker():
            while not stop_event.is_set():
                try:
                    wait_s = max(1.0, _seconds_until(hour, minute))
                    # Add small jitter to avoid exact same second each day
                    wait_s += random.uniform(0, max(0, int(jitter_sec)))
                    stop_event.wait(wait_s)
                    if stop_event.is_set():
                        break
                    try:
                        # Determine targets
                        if profiles is None:
                            targets = manager.get_all_profiles()
                        else:
                            targets = list(profiles)
                        ok, msg = clear_browsing_history(manager, targets)
                        print(f"[CLEANUP] [DAILY] {msg}")
                    except Exception as _e:
                        print(f"[CLEANUP] [DAILY] Error: {_e}")
                    # Sleep a little to avoid immediate re-run if clock quirks
                    stop_event.wait(10.0)
                except Exception:
                    # Ensure loop continues next day
                    stop_event.wait(60.0)
        th = threading.Thread(target=_worker, name="DailyHistoryCleanup", daemon=True)
        manager._daily_history_cleanup_thread = th
        th.start()
        return True, f"Scheduled daily cleanup at {hour:02d}:{minute:02d}"
    except Exception as e:
        return False, f"Failed to start daily cleanup: {str(e)}"


def stop_daily_history_cleanup(manager):
    """Stop the background daily history cleanup thread if running."""
    try:
        ev = getattr(manager, '_daily_history_cleanup_stop', None)
        th = getattr(manager, '_daily_history_cleanup_thread', None)
        if ev:
            ev.set()
        if th:
            try:
                th.join(timeout=2.0)
            except Exception:
                pass
        manager._daily_history_cleanup_thread = None
        manager._daily_history_cleanup_stop = None
        return True, "Stopped daily cleanup"
    except Exception as e:
        return False, f"Failed to stop daily cleanup: {str(e)}"

