# launcher.py
"""
Main launcher for Chrome Profile Manager GUI
Với debug logging cho captcha solver
"""

import logging
import sys

# Setup logging để hiển thị debug logs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - %(name)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('logs/launcher.log', encoding='utf-8')
    ]
)

from core.gui_manager_modern import ModernChromeProfileManager

if __name__ == "__main__":
    print("="*70)
    print("CHROME PROFILE MANAGER - LAUNCHER")
    print("With Auto Captcha Solver V2 (HTML-based)")
    print("="*70)
    print()
    
    app = ModernChromeProfileManager()
    app.run()