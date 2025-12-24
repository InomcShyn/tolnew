#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug Logger - Advanced Debug System for Chrome Profiles
- Per-profile debug output
- CLI flags support
- Compact one-line summary
- Full detailed summary
- Performance metrics
- Save logs to file

Created: December 9, 2025
"""

import os
import sys
import time
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime


class DebugLogger:
    """Advanced debug logger for Chrome profiles"""
    
    def __init__(self, profile_name: str, profile_path: str = None):
        """
        Initialize debug logger
        
        Args:
            profile_name: Profile name
            profile_path: Path to profile directory (optional)
        """
        self.profile_name = profile_name
        self.profile_path = profile_path
        self.start_time = time.time()
        self.logs = []
        
        # Parse CLI flags
        self.debug_enabled = '--debug' in sys.argv
        self.debug_profile_id = self._get_debug_profile_id()
        self.show_profile = '--show-profile' in sys.argv
        self.show_ua = '--show-ua' in sys.argv or '--show-agent' in sys.argv
        self.show_flags = '--show-flags' in sys.argv
        self.show_ram = '--show-ram' in sys.argv
        self.show_gpu = '--show-gpu' in sys.argv
        
        # Check if this profile should be debugged
        self.should_debug = self.debug_enabled and (
            not self.debug_profile_id or 
            self.debug_profile_id == profile_name
        )
    
    def _get_debug_profile_id(self) -> Optional[str]:
        """Get debug profile ID from CLI args"""
        for arg in sys.argv:
            if arg.startswith('--debug-profile-id='):
                return arg.split('=')[1]
        return None
    
    def log(self, message: str, level: str = "INFO"):
        """
        Log message
        
        Args:
            message: Log message
            level: Log level (INFO, WARNING, ERROR, SUCCESS)
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"
        self.logs.append(log_entry)
        
        if self.should_debug:
            print(log_entry)
    
    def info(self, message: str):
        """Log info message"""
        self.log(message, "INFO")
    
    def warning(self, message: str):
        """Log warning message"""
        self.log(message, "WARNING")
    
    def error(self, message: str):
        """Log error message"""
        self.log(message, "ERROR")
    
    def success(self, message: str):
        """Log success message"""
        self.log(message, "SUCCESS")
    
    def print_compact_summary(
        self,
        ua: str = None,
        gpu: str = None,
        ram_target: str = "150-200MB",
        mode: str = "NORMAL",
        stealth_status: str = "✅",
        flags_count: int = 0
    ):
        """
        Print compact one-line summary
        
        Args:
            ua: User agent (Chrome version)
            gpu: GPU info
            ram_target: RAM target
            mode: Launch mode
            stealth_status: Stealth status (✅ or ❌)
            flags_count: Number of Chrome flags
        """
        if not self.should_debug:
            return
        
        # Extract Chrome version from UA
        chrome_version = "Unknown"
        if ua:
            import re
            match = re.search(r'Chrome/([\d.]+)', ua)
            if match:
                chrome_version = match.group(1)
        
        # Build summary
        parts = [f"[PROFILE {self.profile_name}]"]
        
        if self.show_ua and ua:
            parts.append(f"UA: Chrome/{chrome_version}")
        
        if self.show_gpu and gpu:
            parts.append(f"GPU: {gpu}")
        
        if self.show_ram:
            parts.append(f"RAM: {ram_target}")
        
        parts.append(f"Mode: {mode}")
        parts.append(f"Stealth: {stealth_status}")
        
        if self.show_flags:
            parts.append(f"Flags: {flags_count}")
        
        summary = " | ".join(parts)
        print(f"\n{'='*70}")
        print(summary)
        print(f"{'='*70}\n")
    
    def print_detailed_summary(
        self,
        ua: str = None,
        gpu: str = None,
        ram_target: str = "150-200MB",
        mode: str = "NORMAL",
        stealth_status: str = "✅",
        flags: List[str] = None,
        proxy: str = None,
        profile_path: str = None
    ):
        """
        Print detailed summary
        
        Args:
            ua: User agent
            gpu: GPU info
            ram_target: RAM target
            mode: Launch mode
            stealth_status: Stealth status
            flags: List of Chrome flags
            proxy: Proxy info
            profile_path: Profile path
        """
        if not self.should_debug:
            return
        
        elapsed = time.time() - self.start_time
        
        print(f"\n{'='*70}")
        print(f"DETAILED DEBUG SUMMARY - {self.profile_name}")
        print(f"{'='*70}")
        
        if self.show_profile:
            print(f"\n📁 PROFILE INFO:")
            print(f"   Name: {self.profile_name}")
            if profile_path:
                print(f"   Path: {profile_path}")
        
        if self.show_ua and ua:
            print(f"\n🌐 USER AGENT:")
            print(f"   {ua}")
            
            # Extract info
            import re
            chrome_match = re.search(r'Chrome/([\d.]+)', ua)
            if chrome_match:
                print(f"   Chrome Version: {chrome_match.group(1)}")
            
            if 'Windows' in ua:
                print(f"   OS: Windows")
            elif 'Macintosh' in ua:
                print(f"   OS: macOS")
            elif 'Linux' in ua:
                print(f"   OS: Linux")
        
        if self.show_gpu and gpu:
            print(f"\n🎮 GPU INFO:")
            print(f"   {gpu}")
        
        if self.show_ram:
            print(f"\n💾 RAM TARGET:")
            print(f"   {ram_target}")
        
        print(f"\n🚀 LAUNCH MODE:")
        print(f"   {mode}")
        
        print(f"\n🔒 STEALTH STATUS:")
        print(f"   {stealth_status}")
        
        if self.show_flags and flags:
            print(f"\n⚙️  CHROME FLAGS ({len(flags)}):")
            for i, flag in enumerate(flags[:10], 1):  # Show first 10
                print(f"   {i}. {flag}")
            if len(flags) > 10:
                print(f"   ... and {len(flags) - 10} more")
        
        if proxy:
            print(f"\n🌐 PROXY:")
            print(f"   {proxy}")
        
        print(f"\n⏱️  PERFORMANCE:")
        print(f"   Launch Time: {elapsed:.2f}s")
        
        print(f"\n{'='*70}\n")
    
    def save_logs_to_file(self, log_dir: str = "logs"):
        """
        Save logs to file
        
        Args:
            log_dir: Directory to save logs
        """
        try:
            # Create log directory
            log_path = Path(log_dir)
            log_path.mkdir(exist_ok=True)
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.profile_name}_{timestamp}.log"
            filepath = log_path / filename
            
            # Write logs
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"Debug Log - {self.profile_name}\n")
                f.write(f"Generated: {datetime.now().isoformat()}\n")
                f.write(f"{'='*70}\n\n")
                
                for log_entry in self.logs:
                    f.write(log_entry + '\n')
            
            print(f"[DEBUG] ✅ Logs saved to: {filepath}")
            return True
            
        except Exception as e:
            print(f"[DEBUG] ❌ Error saving logs: {e}")
            return False


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def create_debug_logger(profile_name: str, profile_path: str = None) -> DebugLogger:
    """
    Create debug logger for profile
    
    Args:
        profile_name: Profile name
        profile_path: Profile path (optional)
    
    Returns:
        DebugLogger instance
    """
    return DebugLogger(profile_name, profile_path)


def is_debug_enabled() -> bool:
    """Check if debug mode is enabled"""
    return '--debug' in sys.argv


def get_debug_profile_id() -> Optional[str]:
    """Get debug profile ID from CLI args"""
    for arg in sys.argv:
        if arg.startswith('--debug-profile-id='):
            return arg.split('=')[1]
    return None


def should_debug_profile(profile_name: str) -> bool:
    """
    Check if profile should be debugged
    
    Args:
        profile_name: Profile name
    
    Returns:
        True if should debug
    """
    if not is_debug_enabled():
        return False
    
    debug_profile_id = get_debug_profile_id()
    if not debug_profile_id:
        return True  # Debug all profiles
    
    return debug_profile_id == profile_name


def print_cli_help():
    """Print CLI help for debug flags"""
    print(f"\n{'='*70}")
    print("DEBUG FLAGS HELP")
    print(f"{'='*70}")
    print("\nAvailable flags:")
    print("  --debug                    Enable debug mode")
    print("  --debug-profile-id=xxx     Debug specific profile")
    print("  --show-profile             Show profile info")
    print("  --show-ua / --show-agent   Show user agent")
    print("  --show-flags               Show Chrome flags")
    print("  --show-ram                 Show RAM target")
    print("  --show-gpu                 Show GPU info")
    print("\nExamples:")
    print("  python launch_livestream_simple.py --debug --show-profile --show-ua")
    print("  python launch_livestream_simple.py --debug-profile-id=p-123-456 --show-gpu")
    print(f"{'='*70}\n")


# ============================================================
# MAIN (for testing)
# ============================================================

if __name__ == "__main__":
    # Test debug logger
    print("Testing Debug Logger...\n")
    
    # Create logger
    logger = create_debug_logger("p-test-123")
    
    # Log messages
    logger.info("Starting profile launch...")
    logger.success("Profile launched successfully")
    logger.warning("High RAM usage detected")
    logger.error("Failed to connect to proxy")
    
    # Print compact summary
    logger.print_compact_summary(
        ua="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        gpu="Intel UHD 630",
        ram_target="150-200MB",
        mode="FAKE_HEADLESS",
        stealth_status="✅",
        flags_count=48
    )
    
    # Print detailed summary
    logger.print_detailed_summary(
        ua="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        gpu="Intel UHD 630",
        ram_target="150-200MB",
        mode="FAKE_HEADLESS",
        stealth_status="✅",
        flags=['--disable-blink-features=AutomationControlled', '--enable-gpu', '--js-flags=--max-old-space-size=64'],
        proxy="http://proxy.example.com:8080",
        profile_path="/path/to/profile"
    )
    
    # Save logs
    logger.save_logs_to_file()
    
    # Print help
    print_cli_help()
