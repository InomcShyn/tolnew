#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chrome Command Line Fixer
Nhận vào command line hiện tại và trả về command line đã được fix theo rules
"""

import json
import re
import os

def fix_chrome_command(original_command, rules):
    """
    Fix Chrome command line theo rules
    
    Args:
        original_command (str): Command line gốc
        rules (dict): Rules để fix command line
    
    Returns:
        str: Command line đã được fix
    """
    try:
        # Parse command line - handle quotes properly
        import shlex
        parts = shlex.split(original_command)
        if not parts:
            return "ERROR: empty command"
        
        executable = parts[0]
        flags = parts[1:]
        
        # Validate executable
        if not executable.endswith('.exe'):
            return "ERROR: invalid executable path"
        
        # Parse flags
        parsed_flags = {}
        other_flags = []
        
        for flag in flags:
            if flag.startswith('--'):
                if '=' in flag:
                    key, value = flag.split('=', 1)
                    parsed_flags[key] = value
                else:
                    parsed_flags[flag] = True
            else:
                other_flags.append(flag)
        
        # Apply rules
        # 1. Replace user_data_dir
        if rules.get('user_data_dir'):
            parsed_flags['--user-data-dir'] = f'"{rules["user_data_dir"]}"'
        
        # 2. Replace lang
        if rules.get('lang'):
            parsed_flags['--lang'] = rules['lang']
        
        # 3. Replace user_agent
        if rules.get('user_agent'):
            parsed_flags['--user-agent'] = f'"{rules["user_agent"]}"'
        
        # 4. Handle extension_path
        if 'extension_path' in rules and rules['extension_path']:
            ext_path = str(rules['extension_path']).strip('"')
            parsed_flags['--load-extension'] = f'"{ext_path}"'
        else:
            # Remove load-extension if not explicitly provided
            parsed_flags.pop('--load-extension', None)
        
        # 5. Remove GPM flags if keep_gpm_flags is False
        if not rules.get('keep_gpm_flags', True):
            gpm_flags_to_remove = [k for k in parsed_flags.keys() if k.startswith('--gpm-')]
            for flag in gpm_flags_to_remove:
                parsed_flags.pop(flag, None)
        
        # 6. Remove automation flags (explicitly strip three problematic flags)
        if rules.get('remove_automation_flags', True):
            automation_patterns = [
                '--test-type=webdriver',
                '--remote-debugging-port',
                '--use-mock-keychain',
                '--enable-logging',
                '--log-level',
                '--headless',
                '--enable-automation',
                '--disable-blink-features=AutomationControlled',
                '--allow-pre-commit-input',
                '--disable-background-networking',
                '--disable-backgrounding-occluded-windows',
                '--disable-client-side-phishing-detection',
                '--disable-default-apps',
                '--disable-hang-monitor',
                '--disable-popup-blocking',
                '--disable-prompt-on-repost',
                '--disable-sync',
                '--no-first-run',
                '--no-service-autorun'
            ]
            # Ensure exact variants removed
            parsed_flags.pop('--no-first-run', None)
            for k in list(parsed_flags.keys()):
                if k.startswith('--log-level') or k.startswith('--remote-debugging-port'):
                    parsed_flags.pop(k, None)
            
            for pattern in automation_patterns:
                # Remove exact match
                if pattern in parsed_flags:
                    parsed_flags.pop(pattern, None)
                # Remove flags that start with pattern (without =)
                base_flag = pattern.split('=')[0]
                keys_to_remove = [k for k in parsed_flags.keys() if k.startswith(base_flag)]
                for key in keys_to_remove:
                    parsed_flags.pop(key, None)
            
            # Automation flags removed
        
        # 7. Remove forbidden flags
        forbidden_flags = rules.get('forbidden_flags', [])
        for flag in forbidden_flags:
            # Remove exact match
            if flag in parsed_flags:
                parsed_flags.pop(flag, None)
            # Remove flags that start with forbidden flag
            keys_to_remove = [k for k in parsed_flags.keys() if k.startswith(flag)]
            for key in keys_to_remove:
                parsed_flags.pop(key, None)
        
        # 8. Add forced flags
        force_flags = rules.get('force_flags', [])
        for flag in force_flags:
            if '=' in flag:
                key, value = flag.split('=', 1)
                parsed_flags[key] = value
            else:
                parsed_flags[flag] = True
        
        # 9. Build final command
        final_flags = []
        for key, value in parsed_flags.items():
            if value is True:
                final_flags.append(key)
            else:
                final_flags.append(f'{key}={value}')
        
        # Remove duplicate flags
        seen_flags = set()
        unique_flags = []
        for flag in final_flags:
            # Extract flag name (before =)
            flag_name = flag.split('=')[0]
            if flag_name not in seen_flags:
                seen_flags.add(flag_name)
                unique_flags.append(flag)
        
        # Combine executable + flags
        final_command = executable + ' ' + ' '.join(unique_flags)
        
        # Validate final command
        if not final_command.strip():
            return "ERROR: empty final command"
        
        return final_command
        
    except Exception as e:
        return f"ERROR: {str(e)}"

def load_gpm_config():
    """Load GPM config from gpm_config.json"""
    try:
        with open('gpm_config.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading gpm_config.json: {e}")
        return None

def create_rules_from_gpm_config(gpm_config):
    """Create rules from GPM config"""
    if not gpm_config:
        return {}
    
    profile_settings = gpm_config.get('profile_settings', {})
    software = profile_settings.get('software', {})
    
    rules = {
        'user_agent': software.get('user_agent'),
        'lang': 'vi',  # Force to vi instead of en-US
        'keep_gpm_flags': True,
        'remove_automation_flags': True,
        'force_flags': [
            '--no-default-browser-check',
            '--password-store=basic',
            '--gpm-disable-machine-id',
            '--gpm-use-pref-tracking-config-before-v137',
            '--flag-switches-begin',
            '--flag-switches-end'
        ],
        'forbidden_flags': [
            '--test-type=webdriver',
            '--remote-debugging-port=0',
            '--use-mock-keychain',
            '--enable-logging',
            '--log-level=0',
            '--allow-pre-commit-input',
            '--disable-background-networking',
            '--disable-backgrounding-occluded-windows',
            '--disable-client-side-phishing-detection',
            '--disable-default-apps',
            '--disable-hang-monitor',
            '--disable-popup-blocking',
            '--disable-prompt-on-repost',
            '--disable-sync',
            '--no-first-run',
            '--no-service-autorun'
        ]
    }
    
    return rules

def main():
    """Main function for testing"""
    # Load GPM config
    gpm_config = load_gpm_config()
    if not gpm_config:
        print("ERROR: Cannot load gpm_config.json")
        return
    
    # Create rules from GPM config
    rules = create_rules_from_gpm_config(gpm_config)
    
    # Test with your original command
    original_command = '"C:\\Users\\admin\\AppData\\Local\\Programs\\GPMLogin\\gpm_browser\\gpm_browser_chromium_core_139\\chrome.exe" --allow-pre-commit-input --disable-background-networking --disable-backgrounding-occluded-windows --disable-client-side-phishing-detection --disable-default-apps --disable-hang-monitor --disable-popup-blocking --disable-prompt-on-repost --disable-sync --enable-logging --flag-switches-begin --flag-switches-end --gpm-disable-machine-id --gpm-use-pref-tracking-config-before-v137 --lang=vi --load-extension="C:\\GPM-profile\\dx7rwzL1Rf-10102025\\Default\\GPMSoft\\Extensions\\clipboard-ext" --log-level=0 --no-default-browser-check --no-first-run --no-service-autorun --password-store=basic --remote-debugging-port=0 --test-type=webdriver --use-mock-keychain --user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36" --user-data-dir="C:\\Users\\admin\\tolnew\\chrome_profiles\\P-894813-5058" --flag-switches-begin --flag-switches-end'
    
    # Set user_data_dir from rules
    rules['user_data_dir'] = 'C:\\GPM-profile\\dx7rwzL1Rf-10102025'
    rules['extension_path'] = 'C:\\GPM-profile\\dx7rwzL1Rf-10102025\\Default\\GPMSoft\\Extensions\\clipboard-ext'
    
    # Fix command
    fixed_command = fix_chrome_command(original_command, rules)
    print(fixed_command)

if __name__ == "__main__":
    main()
