import os
import shutil
import json

def clear_profile_name_cache(manager, profile_path):
    cache_file = os.path.join(profile_path, 'Local State')
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                local_state = json.load(f)
            local_state['profile']['info_cache'] = {}
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(local_state, f, ensure_ascii=False, indent=2)
        except Exception:
            pass


def clear_existing_proxy_data(manager, driver):
    """Dummy method as placeholder, will depend on how proxy is used in session."""
    pass
