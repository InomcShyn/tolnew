#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Get Chrome Flags from Running Process
Lấy command line flags từ Chrome process đang chạy
"""

import psutil
import json
from datetime import datetime
from pathlib import Path

def get_chrome_processes():
    """Lấy tất cả Chrome processes đang chạy"""
    chrome_processes = []
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time']):
        try:
            proc_name = proc.info['name'].lower()
            if 'chrome' in proc_name or 'chromium' in proc_name:
                # Chỉ lấy main process (có --user-data-dir)
                cmdline = proc.info.get('cmdline', [])
                if cmdline and any('--user-data-dir' in arg for arg in cmdline):
                    chrome_processes.append({
                        'pid': proc.info['pid'],
                        'name': proc.info['name'],
                        'cmdline': cmdline,
                        'create_time': proc.info['create_time']
                    })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    return chrome_processes

def extract_profile_name(cmdline):
    """Extract profile name từ command line"""
    for arg in cmdline:
        if '--user-data-dir' in arg:
            # Extract profile name from path
            parts = arg.split('/')
            if parts:
                return parts[-1]
    return "unknown"

def parse_chrome_flags(cmdline):
    """Parse Chrome flags từ command line"""
    flags = {
        'all_flags': [],
        'disable_flags': [],
        'enable_flags': [],
        'enable_features': [],
        'disable_features': [],
        'other_flags': []
    }
    
    for arg in cmdline:
        if not arg.startswith('--'):
            continue
        
        flags['all_flags'].append(arg)
        
        if arg.startswith('--disable-'):
            flags['disable_flags'].append(arg)
        elif arg.startswith('--enable-'):
            flags['enable_flags'].append(arg)
        elif arg.startswith('--enable-features='):
            features = arg.replace('--enable-features=', '').split(',')
            flags['enable_features'].extend(features)
        elif arg.startswith('--disable-features='):
            features = arg.replace('--disable-features=', '').split(',')
            flags['disable_features'].extend(features)
        else:
            flags['other_flags'].append(arg)
    
    return flags

def format_flags_output(profile_name, flags):
    """Format flags thành output dễ đọc"""
    output = []
    output.append("=" * 70)
    output.append(f"PROFILE: {profile_name}")
    output.append("=" * 70)
    
    # Disable flags
    if flags['disable_flags']:
        output.append("\n🔴 DISABLE FLAGS:")
        for flag in sorted(flags['disable_flags']):
            output.append(f"  {flag}")
    
    # Enable flags
    if flags['enable_flags']:
        output.append("\n🟢 ENABLE FLAGS:")
        for flag in sorted(flags['enable_flags']):
            output.append(f"  {flag}")
    
    # Enable features
    if flags['enable_features']:
        output.append("\n✅ ENABLE FEATURES:")
        for feature in sorted(flags['enable_features']):
            output.append(f"  {feature}")
    
    # Disable features
    if flags['disable_features']:
        output.append("\n❌ DISABLE FEATURES:")
        for feature in sorted(flags['disable_features']):
            output.append(f"  {feature}")
    
    # Other flags
    if flags['other_flags']:
        output.append("\n⚙️  OTHER FLAGS:")
        for flag in sorted(flags['other_flags']):
            output.append(f"  {flag}")
    
    output.append("\n" + "=" * 70)
    
    return "\n".join(output)

def save_flags_to_file(profile_name, flags, cmdline):
    """Lưu flags vào file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create output directory
    output_dir = Path("chrome_flags_extracted")
    output_dir.mkdir(exist_ok=True)
    
    # Save as JSON
    json_file = output_dir / f"{profile_name}_{timestamp}.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump({
            'profile': profile_name,
            'timestamp': timestamp,
            'flags': flags,
            'full_cmdline': cmdline
        }, f, indent=2, ensure_ascii=False)
    
    # Save as text
    txt_file = output_dir / f"{profile_name}_{timestamp}.txt"
    with open(txt_file, 'w', encoding='utf-8') as f:
        f.write(format_flags_output(profile_name, flags))
        f.write("\n\n")
        f.write("FULL COMMAND LINE:\n")
        f.write("=" * 70 + "\n")
        for arg in cmdline:
            f.write(f"{arg}\n")
    
    return json_file, txt_file

def main():
    print("\n" + "=" * 70)
    print("🔍 GET CHROME FLAGS FROM RUNNING PROCESSES")
    print("=" * 70)
    print("Lấy command line flags từ Chrome processes đang chạy")
    print("=" * 70 + "\n")
    
    # Get Chrome processes
    print("🔍 Scanning for Chrome processes...")
    chrome_processes = get_chrome_processes()
    
    if not chrome_processes:
        print("❌ No Chrome processes found")
        print("   Hãy chạy profile trước, sau đó chạy script này")
        return
    
    print(f"✅ Found {len(chrome_processes)} Chrome process(es)\n")
    
    # Process each Chrome instance
    all_results = []
    
    for i, proc in enumerate(chrome_processes, 1):
        profile_name = extract_profile_name(proc['cmdline'])
        
        print(f"[{i}/{len(chrome_processes)}] Processing: {profile_name}")
        print(f"   PID: {proc['pid']}")
        
        # Parse flags
        flags = parse_chrome_flags(proc['cmdline'])
        
        print(f"   Total flags: {len(flags['all_flags'])}")
        print(f"   Disable: {len(flags['disable_flags'])}")
        print(f"   Enable: {len(flags['enable_flags'])}")
        print(f"   Features enabled: {len(flags['enable_features'])}")
        print(f"   Features disabled: {len(flags['disable_features'])}")
        
        # Save to file
        json_file, txt_file = save_flags_to_file(profile_name, flags, proc['cmdline'])
        
        print(f"   ✅ Saved to:")
        print(f"      JSON: {json_file}")
        print(f"      TXT:  {txt_file}")
        print()
        
        all_results.append({
            'profile': profile_name,
            'pid': proc['pid'],
            'flags': flags,
            'files': {
                'json': str(json_file),
                'txt': str(txt_file)
            }
        })
    
    # Print summary
    print("=" * 70)
    print("📊 SUMMARY")
    print("=" * 70)
    
    for result in all_results:
        print(f"\n{result['profile']} (PID: {result['pid']})")
        print(f"  Flags: {len(result['flags']['all_flags'])}")
        print(f"  Files: {result['files']['txt']}")
    
    print("\n" + "=" * 70)
    print("✅ DONE!")
    print("=" * 70)
    print(f"Đã lưu flags vào thư mục: chrome_flags_extracted/")
    print("=" * 70)

if __name__ == "__main__":
    main()
