#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Convert GPM Profile to NKT Profile
- Rename GPMSoft to NKTSoft
- Import cookies from ExportCookies.json
- Update Local State with necessary metadata
"""

import os
import json
import shutil
import sqlite3
from pathlib import Path

class GPMToNKTConverter:
    def __init__(self, gpm_profile_path, nkt_profile_path):
        self.gpm_profile_path = Path(gpm_profile_path)
        self.nkt_profile_path = Path(nkt_profile_path)
        
    def convert_profile(self):
        """Convert GPM profile to NKT profile"""
        print(f"🔄 [CONVERT] Converting GPM profile to NKT profile")
        print(f"📂 [CONVERT] Source: {self.gpm_profile_path}")
        print(f"📂 [CONVERT] Target: {self.nkt_profile_path}")
        
        try:
            # 1. Rename GPMSoft to NKTSoft
            self.rename_gpmsoft_to_nktsoft()
            
            # 2. Import cookies from ExportCookies.json
            self.import_cookies()
            
            # 3. Update Local State with necessary metadata
            self.update_local_state()
            
            # 4. Update profile settings
            self.update_profile_settings()
            
            print("✅ [CONVERT] Profile conversion completed successfully!")
            return True
            
        except Exception as e:
            print(f"❌ [CONVERT] Error converting profile: {str(e)}")
            return False
    
    def rename_gpmsoft_to_nktsoft(self):
        """Rename GPMSoft directory to NKTSoft"""
        gpmsoft_path = self.gpm_profile_path / "Default" / "GPMSoft"
        nktsoft_path = self.gpm_profile_path / "Default" / "NKTSoft"
        
        if gpmsoft_path.exists():
            print(f"📁 [RENAME] Renaming GPMSoft to NKTSoft")
            shutil.move(str(gpmsoft_path), str(nktsoft_path))
            print(f"✅ [RENAME] Successfully renamed GPMSoft to NKTSoft")
        else:
            print(f"⚠️ [RENAME] GPMSoft directory not found")
    
    def import_cookies(self):
        """Import cookies from ExportCookies.json to Chrome cookies database"""
        cookies_file = self.gpm_profile_path / "Default" / "NKTSoft" / "Exporter" / "ExportCookies.json"
        
        if not cookies_file.exists():
            print(f"⚠️ [COOKIES] ExportCookies.json not found")
            return
        
        print(f"🍪 [COOKIES] Importing cookies from ExportCookies.json")
        
        try:
            # Read cookies from JSON
            with open(cookies_file, 'r', encoding='utf-8') as f:
                cookies_data = json.load(f)
            
            cookies = cookies_data.get('cookies', [])
            print(f"📊 [COOKIES] Found {len(cookies)} cookies to import")
            
            # Chrome cookies database path
            cookies_db = self.gpm_profile_path / "Default" / "Network" / "Cookies"
            
            if not cookies_db.exists():
                print(f"⚠️ [COOKIES] Chrome cookies database not found")
                return
            
            # Import cookies to Chrome database
            self.import_cookies_to_chrome_db(cookies, cookies_db)
            
        except Exception as e:
            print(f"❌ [COOKIES] Error importing cookies: {str(e)}")
    
    def import_cookies_to_chrome_db(self, cookies, cookies_db):
        """Import cookies to Chrome cookies database"""
        try:
            # Backup original database
            backup_db = str(cookies_db) + ".backup"
            shutil.copy2(str(cookies_db), backup_db)
            
            # Connect to cookies database
            conn = sqlite3.connect(str(cookies_db))
            cursor = conn.cursor()
            
            # Clear existing cookies (optional)
            # cursor.execute("DELETE FROM cookies")
            
            # Import each cookie
            imported_count = 0
            for cookie in cookies:
                try:
                    # Convert cookie data to Chrome format
                    chrome_cookie = self.convert_cookie_to_chrome_format(cookie)
                    
                    # Insert cookie into database
                    cursor.execute("""
                        INSERT OR REPLACE INTO cookies 
                        (creation_utc, host_key, name, value, path, expires_utc, 
                         is_secure, is_httponly, last_access_utc, has_expires, 
                         is_persistent, priority, encrypted_value, samesite, 
                         source_scheme, source_port, is_same_party)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, chrome_cookie)
                    
                    imported_count += 1
                    
                except Exception as e:
                    print(f"⚠️ [COOKIES] Error importing cookie {cookie.get('name', 'unknown')}: {str(e)}")
                    continue
            
            conn.commit()
            conn.close()
            
            print(f"✅ [COOKIES] Successfully imported {imported_count} cookies")
            
        except Exception as e:
            print(f"❌ [COOKIES] Error accessing cookies database: {str(e)}")
    
    def convert_cookie_to_chrome_format(self, cookie):
        """Convert cookie from JSON format to Chrome database format"""
        import time
        
        # Current timestamp
        current_time = int(time.time() * 1000000)  # microseconds
        
        # Expiration time
        expires_utc = cookie.get('expirationDate', 0)
        if expires_utc > 0:
            expires_utc = int(expires_utc * 1000000)  # convert to microseconds
        else:
            expires_utc = 0
        
        # Chrome cookie format
        chrome_cookie = (
            current_time,  # creation_utc
            cookie.get('domain', ''),  # host_key
            cookie.get('name', ''),  # name
            cookie.get('value', ''),  # value
            cookie.get('path', '/'),  # path
            expires_utc,  # expires_utc
            1 if cookie.get('secure', False) else 0,  # is_secure
            1 if cookie.get('httpOnly', False) else 0,  # is_httponly
            current_time,  # last_access_utc
            1 if expires_utc > 0 else 0,  # has_expires
            1 if expires_utc > 0 else 0,  # is_persistent
            0,  # priority
            b'',  # encrypted_value
            0,  # samesite
            0,  # source_scheme
            -1,  # source_port
            0   # is_same_party
        )
        
        return chrome_cookie
    
    def update_local_state(self):
        """Update Local State with necessary metadata"""
        local_state_file = self.gpm_profile_path / "Local State"
        
        if not local_state_file.exists():
            print(f"⚠️ [LOCAL-STATE] Local State file not found")
            return
        
        print(f"📝 [LOCAL-STATE] Updating Local State with NKT metadata")
        
        try:
            # Read current Local State
            with open(local_state_file, 'r', encoding='utf-8') as f:
                local_state = json.load(f)
            
            # Update profile info
            if 'profile' not in local_state:
                local_state['profile'] = {}
            
            if 'info_cache' not in local_state['profile']:
                local_state['profile']['info_cache'] = {}
            
            if 'Default' not in local_state['profile']['info_cache']:
                local_state['profile']['info_cache']['Default'] = {}
            
            # Update profile name and metadata
            profile_info = local_state['profile']['info_cache']['Default']
            profile_info.update({
                'name': 'NKT Browser',
                'is_using_default_name': False,
                'profile_color_seed': -5715974,
                'profile_highlight_color': -14737376,
                'active_time': int(time.time()),
                'avatar_icon': 'chrome://theme/IDR_PROFILE_AVATAR_26',
                'background_apps': False,
                'default_avatar_fill_color': -14737376,
                'default_avatar_stroke_color': -3684409,
                'enterprise_label': '',
                'force_signin_profile_locked': False,
                'gaia_given_name': '',
                'gaia_id': '',
                'gaia_name': '',
                'hosted_domain': '',
                'is_consented_primary_account': False,
                'is_ephemeral': False,
                'is_glic_eligible': False,
                'is_managed': 0,
                'is_using_default_avatar': True,
                'managed_user_id': '',
                'metrics_bucket_index': 1,
                'signin.with_credential_provider': False,
                'user_name': ''
            })
            
            # Add NKT-specific metadata
            local_state['nkt_browser'] = {
                'version': '1.0.0',
                'profile_type': 'nkt',
                'converted_from_gpm': True,
                'conversion_date': int(time.time())
            }
            
            # Update browser info
            local_state['browser'] = {
                'first_run_finished': True,
                'shortcut_migration_version': '139.0.7258.139'
            }
            
            # Save updated Local State
            with open(local_state_file, 'w', encoding='utf-8') as f:
                json.dump(local_state, f, ensure_ascii=False, indent=2)
            
            print(f"✅ [LOCAL-STATE] Successfully updated Local State")
            
        except Exception as e:
            print(f"❌ [LOCAL-STATE] Error updating Local State: {str(e)}")
    
    def update_profile_settings(self):
        """Update profile settings for NKT"""
        settings_file = self.gpm_profile_path / "profile_settings.json"
        
        if not settings_file.exists():
            print(f"⚠️ [SETTINGS] profile_settings.json not found, creating new one")
            settings_data = {}
        else:
            try:
                with open(settings_file, 'r', encoding='utf-8') as f:
                    settings_data = json.load(f)
            except:
                settings_data = {}
        
        print(f"⚙️ [SETTINGS] Updating profile settings for NKT")
        
        # Update profile info
        if 'profile_info' not in settings_data:
            settings_data['profile_info'] = {}
        
        settings_data['profile_info'].update({
            'name': 'NKT Browser',
            'display_name': 'NKT Browser',
            'type': 'nkt',
            'created_at': time.strftime('%Y-%m-%d %H:%M:%S'),
            'converted_from_gpm': True,
            'conversion_date': int(time.time())
        })
        
        # Update software info
        if 'software' not in settings_data:
            settings_data['software'] = {}
        
        settings_data['software'].update({
            'browser_version': '139.0.7258.139',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.7258.139 Safari/537.36',
            'language': 'en-US',
            'startup_url': '',
            'webrtc_policy': 'default_public_interface_only',
            'os_font': 'Real'
        })
        
        # Update hardware info
        if 'hardware' not in settings_data:
            settings_data['hardware'] = {}
        
        settings_data['hardware'].update({
            'ram': '16 GB',
            'cpu': 'Intel(R) Core(TM) i7-10700K CPU @ 3.80GHz',
            'memory': '16 GB',
            'device': 'Desktop',
            'vendor': 'Google Inc.',
            'renderer': 'ANGLE (Intel, Intel(R) HD Graphics 620 Direct3D11 vs_5_0 ps_5_0, D3D11)',
            'canvas_noise': 'Off',
            'webgl_image_noise': 'Off',
            'client_rect_noise': 'Off',
            'audio_noise': 'Off',
            'webgl_meta_masked': True,
            'media_devices_masked': True
        })
        
        # Save updated settings
        with open(settings_file, 'w', encoding='utf-8') as f:
            json.dump(settings_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ [SETTINGS] Successfully updated profile settings")

def main():
    """Main function to convert GPM profile to NKT profile"""
    import sys
    import time
    
    if len(sys.argv) != 3:
        print("Usage: python convert_gpm_to_nkt.py <gpm_profile_path> <nkt_profile_path>")
        print("Example: python convert_gpm_to_nkt.py 'C:\\GPM-profile\\dx7rwzL1Rf-10102025' 'C:\\Users\\admin\\tolnew\\chrome_profiles\\P-442282-0002'")
        return
    
    gpm_profile_path = sys.argv[1]
    nkt_profile_path = sys.argv[2]
    
    converter = GPMToNKTConverter(gpm_profile_path, nkt_profile_path)
    success = converter.convert_profile()
    
    if success:
        print("\n🎉 [SUCCESS] GPM profile successfully converted to NKT profile!")
        print("📋 [NEXT] You can now use this profile with your NKT tool")
    else:
        print("\n❌ [FAILED] Profile conversion failed")

if __name__ == "__main__":
    main()
