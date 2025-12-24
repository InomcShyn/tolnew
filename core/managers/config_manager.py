#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Config Manager - Quản lý configuration
Converted from core/tiles/tile_config_management.py
"""

import configparser
from pathlib import Path
from typing import Optional


class ConfigManager:
    """Quản lý configuration files"""
    
    def __init__(self, config_file: str = "config.ini"):
        self.config_file = Path(config_file)
        self.config = configparser.ConfigParser()
        self.load()
    
    def load(self) -> configparser.ConfigParser:
        """Load configuration from file"""
        try:
            if self.config_file.exists():
                self.config.read(self.config_file, encoding='utf-8')
            else:
                self.create_default()
            return self.config
        except Exception as e:
            print(f"Error loading config: {e}")
            return self.config
    
    def create_default(self):
        """Create default configuration"""
        self.config['CHROME'] = {
            'binary_path': '',
            'version': ''
        }
        
        self.config['PROXY'] = {
            'default_proxy': ''
        }
        
        self.config['CAPTCHA'] = {
            'omocaptcha_api_key': ''
        }
        
        self.save()
    
    def save(self) -> bool:
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                self.config.write(f)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    def get(self, section: str, key: str, fallback: str = '') -> str:
        """Get config value"""
        return self.config.get(section, key, fallback=fallback)
    
    def set(self, section: str, key: str, value: str):
        """Set config value"""
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, key, value)
    
    def has_section(self, section: str) -> bool:
        """Check if section exists"""
        return self.config.has_section(section)
    
    def has_option(self, section: str, key: str) -> bool:
        """Check if option exists"""
        return self.config.has_option(section, key)
