import random

def generate_user_agent(manager, profile_type, browser_version=None):
    if browser_version:
        major_version = browser_version.split('.')[0]
        return f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{major_version}.0.0.0 Safari/537.36"
    if profile_type in ("work", "cong_viec"):
        chrome_versions = [
            "120.0.6099.109",
            "120.0.6099.129",
            "121.0.6167.85",
            "121.0.6167.140",
        ]
        chrome_version = random.choice(chrome_versions)
        return f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_version} Safari/537.36"
    return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.109 Safari/537.36"
