import os
import json

def load_gpm_setting(manager):
    """Load GPM setting.dat if exists; return normalized dict with keys: user_agent, language, webrtc_policy, raw_proxy"""
    try:
        candidates = [
            os.path.join(os.getcwd(), "setting.dat"),
            os.path.join(os.getcwd(), "gpm_setting.dat"),
            os.path.join("C:\\GPM-profile", "setting.dat"),
        ]
        for path in candidates:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                dps = data.get("DefaultProfileSetting", {}) if isinstance(data, dict) else {}
                mode = dps.get("webrtc_mode")
                policy = None
                if mode == 2:
                    policy = 'disable_non_proxied_udp'
                elif mode == 1:
                    policy = 'default_public_interface_only'
                elif mode == 0:
                    policy = 'default'
                lang = None
                if dps.get("auto_language") is True:
                    lang = 'en-US'
                return {
                    'user_agent': (dps.get('user_agent') or '').strip() or None,
                    'language': lang,
                    'webrtc_policy': policy,
                    'raw_proxy': (dps.get('raw_proxy') or '').strip() or None,
                }
    except Exception as e:
        print(f"[WARNING] [GPM-SETTING] Cannot load setting.dat: {e}")
    return {}
