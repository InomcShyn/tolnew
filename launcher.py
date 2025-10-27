#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NKT Browser Manager Launcher
Launcher script để chạy ứng dụng từ cấu trúc thư mục mới
"""

import os
import sys
from pathlib import Path

def main():
    """Main launcher function"""
    # Đảm bảo chạy từ thư mục gốc
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Thêm thư mục core vào Python path
    core_dir = script_dir / "core"
    if core_dir.exists():
        sys.path.insert(0, str(core_dir))
    
    # Import và chạy GUI
    try:
        from core.gui_manager_modern import ModernChromeProfileManager
        app = ModernChromeProfileManager()
        app.run()
    except ImportError as e:
        print(f"[LAUNCHER] Import error: {e}")
        print(f"[LAUNCHER] Current directory: {os.getcwd()}")
        print(f"[LAUNCHER] Core directory: {core_dir}")
        print(f"[LAUNCHER] Python path: {sys.path}")
        
        # Fallback: chạy trực tiếp
        print(f"[LAUNCHER] Trying direct execution...")
        os.system(f"python {core_dir}/gui_manager_modern.py")

if __name__ == "__main__":
    main()
