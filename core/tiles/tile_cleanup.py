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


