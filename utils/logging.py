#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Logging Utilities - Quản lý logs cho profiles
Converted from core/tiles/tile_logging.py
"""

import os
from pathlib import Path
from datetime import datetime
from typing import Optional


class LoggingManager:
    """Quản lý logging cho profiles"""
    
    def __init__(self, profiles_dir: Path):
        self.profiles_dir = Path(profiles_dir)
        self.logs_dir = Path(os.getcwd()) / "logs"
        self.logs_dir.mkdir(exist_ok=True)
    
    def get_chrome_log_path(self, profile_name: str) -> str:
        """
        Lấy đường dẫn log file cho profile
        
        Args:
            profile_name: Tên profile
        
        Returns:
            Đường dẫn đến log file
        """
        log_file = self.logs_dir / f"{profile_name}.log"
        return str(log_file)
    
    def append_app_log(
        self,
        profile_name: str,
        message: str,
        level: str = "INFO"
    ):
        """
        Ghi log cho profile
        
        Args:
            profile_name: Tên profile
            message: Nội dung log
            level: Log level (INFO, WARNING, ERROR)
        """
        try:
            log_file = self.get_chrome_log_path(profile_name)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            log_entry = f"[{timestamp}] [{level}] {message}\n"
            
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)
                
        except Exception as e:
            print(f"[LOGGING] Error writing log: {e}")
    
    def read_chrome_log(
        self,
        profile_name: str,
        tail_lines: int = 200
    ) -> str:
        """
        Đọc log file của profile
        
        Args:
            profile_name: Tên profile
            tail_lines: Số dòng cuối cần đọc (0 = all)
        
        Returns:
            Nội dung log
        """
        try:
            log_file = self.get_chrome_log_path(profile_name)
            
            if not os.path.exists(log_file):
                return f"No log file found for {profile_name}"
            
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            if tail_lines > 0 and len(lines) > tail_lines:
                lines = lines[-tail_lines:]
            
            return ''.join(lines)
            
        except Exception as e:
            return f"Error reading log: {e}"
    
    def clear_log(self, profile_name: str) -> bool:
        """
        Xóa log file của profile
        
        Args:
            profile_name: Tên profile
        
        Returns:
            True nếu thành công
        """
        try:
            log_file = self.get_chrome_log_path(profile_name)
            
            if os.path.exists(log_file):
                os.remove(log_file)
                print(f"[LOGGING] Cleared log for {profile_name}")
                return True
            
            return False
            
        except Exception as e:
            print(f"[LOGGING] Error clearing log: {e}")
            return False
    
    def get_all_logs(self) -> list:
        """
        Lấy danh sách tất cả log files
        
        Returns:
            List các log file paths
        """
        try:
            log_files = []
            
            for file in self.logs_dir.glob("*.log"):
                log_files.append({
                    'profile': file.stem,
                    'path': str(file),
                    'size': file.stat().st_size,
                    'modified': datetime.fromtimestamp(file.stat().st_mtime)
                })
            
            return log_files
            
        except Exception as e:
            print(f"[LOGGING] Error listing logs: {e}")
            return []
    
    def log_info(self, profile_name: str, message: str):
        """Log INFO level"""
        self.append_app_log(profile_name, message, "INFO")
    
    def log_warning(self, profile_name: str, message: str):
        """Log WARNING level"""
        self.append_app_log(profile_name, message, "WARNING")
    
    def log_error(self, profile_name: str, message: str):
        """Log ERROR level"""
        self.append_app_log(profile_name, message, "ERROR")
    
    def log_success(self, profile_name: str, message: str):
        """Log SUCCESS level"""
        self.append_app_log(profile_name, message, "SUCCESS")
