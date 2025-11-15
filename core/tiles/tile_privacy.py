import os

def enforce_chrome_policies(manager) -> None:
	try:
		import winreg
		policy_paths = [
			r"Software\Policies\Google\Chrome",
			r"Software\Policies\Chromium"
		]
		for policy_path in policy_paths:
			for root in (winreg.HKEY_CURRENT_USER,):
				try:
					key = winreg.CreateKeyEx(root, policy_path, 0, winreg.KEY_SET_VALUE)
					# 0 = disabled/false
					winreg.SetValueEx(key, "PasswordManagerEnabled", 0, winreg.REG_DWORD, 0)
					winreg.SetValueEx(key, "CredentialsEnableService", 0, winreg.REG_DWORD, 0)
					winreg.SetValueEx(key, "AutoSignInAllowed", 0, winreg.REG_DWORD, 0)
					winreg.SetValueEx(key, "AutofillAddressEnabled", 0, winreg.REG_DWORD, 0)
					winreg.SetValueEx(key, "AutofillCreditCardEnabled", 0, winreg.REG_DWORD, 0)
					winreg.SetValueEx(key, "PasswordLeakDetectionEnabled", 0, winreg.REG_DWORD, 0)
					winreg.CloseKey(key)
					print(f"[POLICY] Applied policies at HKCU\\{policy_path}")
				except Exception as _hkcu_err:
					print(f"[POLICY] Could not write HKCU policies at {policy_path}: {_hkcu_err}")
	except Exception as _e:
		print(f"[POLICY] Policy enforcement failed: {_e}")


def prelaunch_hardening(manager, profile_path: str, language: str = None) -> None:
	try:
		import json as _json
		os.makedirs(os.path.join(profile_path, 'Default'), exist_ok=True)

		# 1) Update Preferences for all profile directories (Default, Profile 1, Profile 2, ...)
		profile_dirs = []
		root = os.path.join(profile_path)
		try:
			for name in os.listdir(root):
				full_path = os.path.join(root, name)
				# Chỉ xử lý thư mục, không phải file
				if os.path.isdir(full_path):
					if name.lower() == 'default' or name.lower().startswith('profile'):
						profile_dirs.append(full_path)
		except Exception:
			profile_dirs = [os.path.join(profile_path, 'Default')]

		for prof_dir in profile_dirs:
			# Đảm bảo prof_dir là thư mục hợp lệ
			if not os.path.isdir(prof_dir):
				continue
			prefs_path = os.path.join(prof_dir, 'Preferences')
			prefs_obj = None
			if os.path.exists(prefs_path):
				try:
					with open(prefs_path, 'r', encoding='utf-8') as pf:
						content = pf.read().strip()
						prefs_obj = _json.loads(content) if content else {}
				except Exception:
					prefs_obj = {}
			else:
				prefs_obj = {}

			if isinstance(prefs_obj, dict):
				if language:
					intl = prefs_obj.get('intl', {})
					intl['accept_languages'] = language
					prefs_obj['intl'] = intl

				# Disable Google signin, GCM beacons, and SafeBrowsing reporting
				prefs_obj['google'] = {}
				prefs_obj['signin'] = {"allowed": False}
				gcm = prefs_obj.get('gcm', {})
				gcm['product_category_for_subtypes'] = ""
				gcm['wake_from_idle'] = False
				prefs_obj['gcm'] = gcm
				sb = prefs_obj.get('safebrowsing', {})
				sb['enabled'] = False
				sb['scout_reporting_enabled_when_deprecated'] = False
				prefs_obj['safebrowsing'] = sb

				# Disable Autofill & form data
				autofill = prefs_obj.get('autofill', {})
				autofill['enabled'] = False
				autofill['profile_enabled'] = False
				autofill['credit_card_enabled'] = False
				prefs_obj['autofill'] = autofill

				# Ensure minimal search config and disable omnibox
				search_block = prefs_obj.get('search', {})
				search_block['engine_forice'] = {"made_by_user": True}
				prefs_obj['search'] = search_block
				omnibox = prefs_obj.get('omnibox', {})
				omnibox['suggestion_enabled'] = False
				omnibox['suppress_suggestions'] = True
				prefs_obj['omnibox'] = omnibox

				# Reduce client hints / hints to Google domains
				prefs_obj.setdefault('privacy_sandbox', {})
				ch = prefs_obj.get('client_hints', {})
				ch['enabled'] = False
				prefs_obj['client_hints'] = ch

				session_block = prefs_obj.get('session', {})
				session_block['restore_on_startup'] = 1
				session_block['startup_urls'] = []
				prefs_obj['session'] = session_block

				profile_block = prefs_obj.get('profile', {})
				profile_block['exit_type'] = 'Normal'
				profile_block['password_manager_enabled'] = False
				prefs_obj['profile'] = profile_block

				# Disable credentials services & autosignin
				prefs_obj['credentials_enable_service'] = False
				prefs_obj['credentials_enable_autosignin'] = False

				try:
					with open(prefs_path, 'w', encoding='utf-8') as pfw:
						_json.dump(prefs_obj, pfw, ensure_ascii=False, indent=2)
					print(f"[PRIVACY] [HARDEN] Preferences updated in: {prefs_path}")
				except Exception as _pw:
					print(f"[WARNING] [HARDEN] Could not write {prefs_path}: {_pw}")

		# 2) Update Local State: drop 'google' block to avoid background registrations
		local_state_path = os.path.join(profile_path, 'Local State')
		if os.path.exists(local_state_path):
			try:
				with open(local_state_path, 'r', encoding='utf-8') as lf:
					ls_content = lf.read().strip()
					if ls_content:
						ls = _json.loads(ls_content)
					else:
						ls = {}
			except Exception:
				ls = {}

			if 'google' in ls:
				try:
					del ls['google']
				except Exception:
					pass
			# Remove GCM/invalidations blocks if present to stop background registrations
			for _k in ('gcm', 'invalidation', 'invalidations'):
				if _k in ls:
					try:
						del ls[_k]
					except Exception:
						pass

			with open(local_state_path, 'w', encoding='utf-8') as lfw:
				_json.dump(ls, lfw, ensure_ascii=False)

		# Clean sessions artifacts
		try:
			import glob, shutil as _shutil
			default_dir = os.path.join(profile_path, 'Default')
			sessions_dir = os.path.join(default_dir, 'Sessions')
			if os.path.isdir(sessions_dir):
				_shutil.rmtree(sessions_dir, ignore_errors=True)
			remove_patterns = [
				'Current Session', 'Current Tabs', 'Last Session', 'Last Tabs',
				'Sessions*', 'Tabs_*', 'Session_*'
			]
			for pat in remove_patterns:
				for fp in glob.glob(os.path.join(default_dir, pat)):
					try:
						if os.path.isdir(fp):
							_shutil.rmtree(fp, ignore_errors=True)
						else:
							os.remove(fp)
					except Exception:
						pass
		except Exception:
			pass
	except Exception:
		pass

