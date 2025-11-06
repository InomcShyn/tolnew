import os
import io
import zipfile
from datetime import datetime

# === Chrome binary helpers extracted from chrome_manager.py ===

def resolve_chrome_binary_path(manager, desired_version: str = '') -> str:
    try:
        if desired_version:
            gpm_base = r"C:\Users\admin\AppData\Local\Programs\GPMLogin\gpm_browser"
            major_version = desired_version.split('.')[0]
            gpm_path = os.path.join(gpm_base, f"gpm_browser_chromium_core_{major_version}", "chrome.exe")
            if os.path.exists(gpm_path):
                return gpm_path
    except Exception:
        pass
    try:
        env_path = os.environ.get('CHROME_BINARY')
        if env_path and os.path.exists(env_path):
            return env_path
    except Exception:
        pass
    try:
        if hasattr(manager, 'config'):
            import configparser
            if isinstance(manager.config, configparser.ConfigParser):
                bp = manager.config.get('chrome', 'binary_path', fallback='').strip()
            else:
                bp = ''
            if bp and os.path.exists(bp):
                return bp
    except Exception:
        pass
    return ''


def gpm_chrome_path_for_version(version: str) -> str:
    try:
        if not version:
            return ''
        major = str(version).split('.')[0]
        base = r"C:\Users\admin\AppData\Local\Programs\GPMLogin\gpm_browser"
        candidate = os.path.join(base, f"gpm_browser_chromium_core_{major}", "chrome.exe")
        return candidate
    except Exception:
        return ''


def ensure_cft_chrome_binary(desired_version: str) -> str:
    try:
        import urllib.request, json as _json
        if not desired_version:
            return ''
        base_dir = os.path.join(os.getcwd(), 'chrome_binaries')
        os.makedirs(base_dir, exist_ok=True)
        dst_dir = os.path.join(base_dir, desired_version)
        chrome_exe = os.path.join(dst_dir, 'chrome-win64', 'chrome.exe')
        if os.path.exists(chrome_exe):
            return chrome_exe
        def _download(url: str) -> bytes:
            with urllib.request.urlopen(url, timeout=60) as resp:
                if resp.status != 200:
                    raise RuntimeError(f"HTTP {resp.status}")
                return resp.read()
        def _extract(data: bytes, target: str):
            with zipfile.ZipFile(io.BytesIO(data)) as zf:
                zf.extractall(target)
        exact = f"https://storage.googleapis.com/chrome-for-testing-public/{desired_version}/win64/chrome-win64.zip"
        try:
            data = _download(exact)
            _extract(data, dst_dir)
            if os.path.exists(chrome_exe):
                return chrome_exe
        except Exception:
            pass
        try:
            import re
            major = re.split(r"[.]+", desired_version)[0]
            kgv = _download("https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json")
            info = _json.loads(kgv.decode('utf-8'))
            versions = info.get('versions', [])
            url = None
            for item in reversed(versions):
                v = item.get('version', '')
                if v.startswith(major + '.'):
                    for d in item.get('downloads', {}).get('chrome', []):
                        if d.get('platform') == 'win64':
                            url = d.get('url')
                            break
                if url:
                    break
            if url:
                data = _download(url)
                _extract(data, dst_dir)
                if os.path.exists(chrome_exe):
                    return chrome_exe
        except Exception:
            pass
    except Exception:
        pass
    return ''


def ensure_cft_chromedriver(desired_version: str) -> str:
    try:
        import urllib.request, json as _json
        if not desired_version:
            return ''
        base_dir = os.path.join(os.getcwd(), 'chrome_binaries')
        os.makedirs(base_dir, exist_ok=True)
        dst_dir = os.path.join(base_dir, desired_version)
        driver_exe = os.path.join(dst_dir, 'chromedriver-win64', 'chromedriver.exe')
        if os.path.exists(driver_exe):
            return driver_exe
        def _download(url: str) -> bytes:
            with urllib.request.urlopen(url, timeout=60) as resp:
                if resp.status != 200:
                    raise RuntimeError(f"HTTP {resp.status}")
                return resp.read()
        def _extract(data: bytes, target: str):
            with zipfile.ZipFile(io.BytesIO(data)) as zf:
                zf.extractall(target)
        exact = f"https://storage.googleapis.com/chrome-for-testing-public/{desired_version}/win64/chromedriver-win64.zip"
        try:
            data = _download(exact)
            _extract(data, dst_dir)
            if os.path.exists(driver_exe):
                return driver_exe
        except Exception:
            pass
        try:
            import re
            major = re.split(r"[.]+", desired_version)[0]
            kgv = _download("https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json")
            info = _json.loads(kgv.decode('utf-8'))
            versions = info.get('versions', [])
            url = None
            for item in reversed(versions):
                v = item.get('version', '')
                if v.startswith(major + '.'):
                    for d in item.get('downloads', {}).get('chromedriver', []):
                        if d.get('platform') == 'win64':
                            url = d.get('url')
                            break
                if url:
                    break
            if url:
                data = _download(url)
                _extract(data, dst_dir)
                if os.path.exists(driver_exe):
                    return driver_exe
        except Exception:
            pass
    except Exception:
        pass
    return ''


def apply_custom_chrome_binary(manager, chrome_options: "Options", profile_path: str, desired_version: str = '') -> None:
    try:
        gpm_path = ''
        try:
            if not desired_version:
                last_version_fp = os.path.join(profile_path, 'Last Version')
                if os.path.exists(last_version_fp):
                    try:
                        with open(last_version_fp, 'r', encoding='utf-8') as lvf:
                            desired_version = lvf.read().strip()
                    except Exception:
                        pass
            gpm_candidate = gpm_chrome_path_for_version(desired_version)
            if gpm_candidate and os.path.exists(gpm_candidate):
                gpm_path = gpm_candidate
        except Exception:
            pass
        binary = gpm_path or resolve_chrome_binary_path(manager, desired_version)
        if binary:
            chrome_options.binary_location = binary
            try:
                from core.tiles.tile_logging import append_app_log
                append_app_log(manager, profile_path, f"Using custom Chrome binary: {binary}")
            except Exception:
                pass
            return
        if desired_version:
            cft = ensure_cft_chrome_binary(desired_version)
            if cft and os.path.exists(cft):
                chrome_options.binary_location = cft
                try:
                    from core.tiles.tile_logging import append_app_log
                    append_app_log(manager, profile_path, f"Using CfT Chrome {desired_version}: {cft}")
                except Exception:
                    pass
        try:
            if getattr(chrome_options, 'binary_location', ''):
                if desired_version:
                    with open(os.path.join(profile_path, 'Last Version'), 'w', encoding='utf-8') as f:
                        f.write(desired_version)
                with open(os.path.join(profile_path, 'Last Browser'), 'w', encoding='utf-8') as f:
                    f.write(chrome_options.binary_location)
        except Exception:
            pass
    except Exception:
        pass
    manager.load_config()
    try:
        os.makedirs(os.path.join(os.getcwd(), "logs"), exist_ok=True)
    except Exception:
        pass
