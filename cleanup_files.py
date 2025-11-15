#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Cleanup Script - Tự động dọn dẹp files không cần thiết
"""

import os
import shutil

# Files cần xóa
FILES_TO_DELETE = [
    # Test files
    'test_api_key_save.py',
    'test_launch_with_omocaptcha.py',
    'test_omocaptcha_install.py',
    'fix_profile_0005.py',
    
    # Fix scripts cũ
    'fix_chrome_command.py',
    'fix_syntax.py',
    
    # Documentation duplicate
    'DEBUG_OMOCAPTCHA.md',
    'OMOCAPTCHA_FIX_SUMMARY.md',
    'OMOCAPTCHA_FINAL_FIX.md',
    'OMOCAPTCHA_COMPLETE_FIX.md',
    'FINAL_TEST_GUIDE.md',
    
    # Temporary files
    'core/tiles/tile_omocaptcha_storage.py',
]

def main():
    print("="*70)
    print("CLEANUP SCRIPT - Dọn dẹp files không cần thiết")
    print("="*70)
    print()
    
    deleted_count = 0
    not_found_count = 0
    error_count = 0
    
    for file_path in FILES_TO_DELETE:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"✅ Deleted: {file_path}")
                deleted_count += 1
            except Exception as e:
                print(f"❌ Error deleting {file_path}: {e}")
                error_count += 1
        else:
            print(f"⚠️ Not found: {file_path}")
            not_found_count += 1
    
    print()
    print("="*70)
    print("SUMMARY")
    print("="*70)
    print(f"✅ Deleted: {deleted_count} files")
    print(f"⚠️ Not found: {not_found_count} files")
    print(f"❌ Errors: {error_count} files")
    print()
    
    if deleted_count > 0:
        print("🎉 Cleanup completed successfully!")
        print()
        print("📋 Remaining files:")
        print("   - launcher.py (main entry)")
        print("   - simple_test_server.py (test livestream)")
        print("   - test_queue_server.py (test queue)")
        print("   - Proxy utilities (3 files)")
        print("   - Core modules (core/)")
        print("   - Documentation (6 files)")
    else:
        print("ℹ️ No files were deleted (already clean or files not found)")
    
    print()
    print("="*70)

if __name__ == '__main__':
    main()
