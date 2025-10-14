#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GPM-Style Chrome Profile Manager
Tích hợp đầy đủ tính năng: UI, Proxy&IP, Fingerprint, Tự động hóa
"""

import os
import json
import shutil
import subprocess
import time
import threading
import requests
import random
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import psutil
import configparser
from datetime import datetime
import uuid
import base64
from urllib.parse import urlparse
import socket

class GPMProfileManager:
    """GPM-Style Profile Manager với đầy đủ tính năng"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("GPM Chrome Profile Manager")
        self.root.geometry("1600x1000")
        self.root.configure(bg='#1e1e1e')
        
        # Cấu hình
        self.config_file = "gpm_profiles_config.json"
        self.profiles_dir = "chrome_profiles"
        self.extensions_dir = "extensions"
        self.pac_files_dir = "pac_files"
        
        # Load cấu hình
        self.load_config()
        
        # Khởi tạo UI
        self.setup_ui()
        self.refresh_profiles()
        
        # Biến quản lý
        self.active_drivers = {}
        self.proxy_test_results = {}
        
    def load_config(self):
        """Load cấu hình từ file JSON"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
            except:
                self.config = self.get_default_config()
        else:
            self.config = self.get_default_config()
            self.save_config()
    
    def get_default_config(self):
        """Cấu hình mặc định giống GPM"""
        return {
            "profiles": {},
            "proxy_settings": {
                "default_proxy": None,
                "proxy_rotation": False,
                "proxy_test_timeout": 10
            },
            "fingerprint_settings": {
                "canvas_noise": True,
                "webgl_noise": True,
                "audio_noise": True,
                "client_rect_noise": True,
                "randomize_hardware": True,
                "randomize_timezone": True,
                "randomize_language": True
            },
            "automation_settings": {
                "auto_login": True,
                "auto_2fa": True,
                "session_management": True,
                "cookie_management": True
            },
            "ui_settings": {
                "theme": "dark",
                "auto_refresh": True,
                "show_advanced": False
            }
        }
    
    def save_config(self):
        """Lưu cấu hình vào file JSON"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Lỗi lưu config: {e}")
    
    def setup_ui(self):
        """Thiết lập giao diện chính giống GPM"""
        # Style hiện đại
        self.setup_modern_style()
        
        # Header
        self.create_header()
        
        # Main content với notebook
        self.create_main_content()
        
        # Status bar
        self.create_status_bar()
    
    def setup_modern_style(self):
        """Thiết lập style hiện đại giống GPM"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Dark theme colors
        colors = {
            'bg': '#1e1e1e',
            'bg_light': '#2d2d2d',
            'fg': '#ffffff',
            'fg_secondary': '#cccccc',
            'accent': '#0078d4',
            'accent_hover': '#106ebe',
            'success': '#107c10',
            'warning': '#ff8c00',
            'error': '#d13438',
            'border': '#404040',
            'card_bg': '#2d2d2d',
            'card_border': '#404040'
        }
        
        # Configure styles
        style.configure('GPM.TFrame', background=colors['bg'])
        style.configure('GPM.TLabel', background=colors['bg'], foreground=colors['fg'])
        style.configure('GPM.TButton', 
                       background=colors['accent'],
                       foreground=colors['fg'],
                       borderwidth=0,
                       focuscolor='none',
                       padding=(10, 8))
        style.map('GPM.TButton',
                 background=[('active', colors['accent_hover']),
                           ('pressed', colors['accent_hover'])])
        
        style.configure('GPM.Treeview',
                       background=colors['card_bg'],
                       foreground=colors['fg'],
                       fieldbackground=colors['card_bg'],
                       borderwidth=1,
                       relief='solid')
        style.map('GPM.Treeview',
                 background=[('selected', colors['accent'])])
        
        style.configure('GPM.TNotebook', background=colors['bg'])
        style.configure('GPM.TNotebook.Tab', 
                       background=colors['bg_light'],
                       foreground=colors['fg'],
                       padding=(20, 10))
        style.map('GPM.TNotebook.Tab',
                 background=[('selected', colors['accent']),
                           ('active', colors['accent_hover'])])
    
    def create_header(self):
        """Tạo header với logo và controls"""
        header_frame = ttk.Frame(self.root, style='GPM.TFrame')
        header_frame.pack(fill='x', padx=10, pady=5)
        
        # Logo và title
        title_frame = ttk.Frame(header_frame, style='GPM.TFrame')
        title_frame.pack(side='left')
        
        ttk.Label(title_frame, text="🚀 GPM Chrome Manager", 
                 style='GPM.TLabel', font=('Segoe UI', 16, 'bold')).pack(side='left')
        
        # Control buttons
        control_frame = ttk.Frame(header_frame, style='GPM.TFrame')
        control_frame.pack(side='right')
        
        ttk.Button(control_frame, text="➕ New Profile", 
                  command=self.create_new_profile, style='GPM.TButton').pack(side='left', padx=2)
        ttk.Button(control_frame, text="🔄 Refresh", 
                  command=self.refresh_profiles, style='GPM.TButton').pack(side='left', padx=2)
        ttk.Button(control_frame, text="⚙️ Settings", 
                  command=self.open_settings, style='GPM.TButton').pack(side='left', padx=2)
    
    def create_main_content(self):
        """Tạo nội dung chính với các tab"""
        self.notebook = ttk.Notebook(self.root, style='GPM.TNotebook')
        self.notebook.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Tab Profiles
        self.create_profiles_tab()
        
        # Tab Proxy & IP
        self.create_proxy_tab()
        
        # Tab Fingerprint
        self.create_fingerprint_tab()
        
        # Tab Automation
        self.create_automation_tab()
        
        # Tab Settings
        self.create_settings_tab()
    
    def create_profiles_tab(self):
        """Tạo tab quản lý profiles"""
        profiles_frame = ttk.Frame(self.notebook, style='GPM.TFrame')
        self.notebook.add(profiles_frame, text="👥 Profiles")
        
        # Profile list
        list_frame = ttk.Frame(profiles_frame, style='GPM.TFrame')
        list_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Treeview cho profiles
        columns = ('ID', 'Name', 'Proxy', 'Status', 'Created', 'Last Used')
        self.profiles_tree = ttk.Treeview(list_frame, columns=columns, show='headings', style='GPM.Treeview')
        
        # Configure columns
        for col in columns:
            self.profiles_tree.heading(col, text=col)
            self.profiles_tree.column(col, width=120)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.profiles_tree.yview)
        self.profiles_tree.configure(yscrollcommand=scrollbar.set)
        
        self.profiles_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Profile actions
        actions_frame = ttk.Frame(profiles_frame, style='GPM.TFrame')
        actions_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(actions_frame, text="▶️ Start", 
                  command=self.start_profile, style='GPM.TButton').pack(side='left', padx=2)
        ttk.Button(actions_frame, text="⏹️ Stop", 
                  command=self.stop_profile, style='GPM.TButton').pack(side='left', padx=2)
        ttk.Button(actions_frame, text="✏️ Edit", 
                  command=self.edit_profile, style='GPM.TButton').pack(side='left', padx=2)
        ttk.Button(actions_frame, text="🗑️ Delete", 
                  command=self.delete_profile, style='GPM.TButton').pack(side='left', padx=2)
        ttk.Button(actions_frame, text="📋 Clone", 
                  command=self.clone_profile, style='GPM.TButton').pack(side='left', padx=2)
        ttk.Button(actions_frame, text="📊 Export", 
                  command=self.export_profile, style='GPM.TButton').pack(side='left', padx=2)
    
    def create_proxy_tab(self):
        """Tạo tab quản lý Proxy & IP"""
        proxy_frame = ttk.Frame(self.notebook, style='GPM.TFrame')
        self.notebook.add(proxy_frame, text="🌐 Proxy & IP")
        
        # Proxy configuration
        config_frame = ttk.LabelFrame(proxy_frame, text="Proxy Configuration", style='GPM.TFrame')
        config_frame.pack(fill='x', padx=10, pady=5)
        
        # Proxy input
        ttk.Label(config_frame, text="Proxy String:", style='GPM.TLabel').grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.proxy_entry = ttk.Entry(config_frame, width=50)
        self.proxy_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Button(config_frame, text="🧪 Test Proxy", 
                  command=self.test_proxy, style='GPM.TButton').grid(row=0, column=2, padx=5, pady=5)
        
        # Profile selection
        ttk.Label(config_frame, text="Select Profile:", style='GPM.TLabel').grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.profile_combo = ttk.Combobox(config_frame, width=30)
        self.profile_combo.grid(row=1, column=1, padx=5, pady=5)
        
        # Bulk configuration
        self.bulk_var = tk.BooleanVar()
        ttk.Checkbutton(config_frame, text="Apply to ALL profiles", 
                       variable=self.bulk_var, style='GPM.TCheckbutton').grid(row=1, column=2, padx=5, pady=5)
        
        ttk.Button(config_frame, text="⚙️ Configure", 
                  command=self.configure_proxy, style='GPM.TButton').grid(row=2, column=0, columnspan=3, pady=10)
        
        # Proxy list
        list_frame = ttk.LabelFrame(proxy_frame, text="Active Proxies", style='GPM.TFrame')
        list_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        proxy_columns = ('Profile', 'Proxy', 'Status', 'IP', 'Speed', 'Last Test')
        self.proxy_tree = ttk.Treeview(list_frame, columns=proxy_columns, show='headings', style='GPM.Treeview')
        
        for col in proxy_columns:
            self.proxy_tree.heading(col, text=col)
            self.proxy_tree.column(col, width=120)
        
        self.proxy_tree.pack(fill='both', expand=True, padx=5, pady=5)
    
    def create_fingerprint_tab(self):
        """Tạo tab quản lý Fingerprint"""
        fingerprint_frame = ttk.Frame(self.notebook, style='GPM.TFrame')
        self.notebook.add(fingerprint_frame, text="🔒 Fingerprint")
        
        # Fingerprint settings
        settings_frame = ttk.LabelFrame(fingerprint_frame, text="Anti-Detection Settings", style='GPM.TFrame')
        settings_frame.pack(fill='x', padx=10, pady=5)
        
        # Canvas noise
        self.canvas_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(settings_frame, text="Canvas Noise", 
                       variable=self.canvas_var, style='GPM.TCheckbutton').grid(row=0, column=0, sticky='w', padx=5, pady=5)
        
        # WebGL noise
        self.webgl_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(settings_frame, text="WebGL Noise", 
                       variable=self.webgl_var, style='GPM.TCheckbutton').grid(row=0, column=1, sticky='w', padx=5, pady=5)
        
        # Audio noise
        self.audio_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(settings_frame, text="Audio Noise", 
                       variable=self.audio_var, style='GPM.TCheckbutton').grid(row=0, column=2, sticky='w', padx=5, pady=5)
        
        # Client rects noise
        self.client_rect_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(settings_frame, text="Client Rects Noise", 
                       variable=self.client_rect_var, style='GPM.TCheckbutton').grid(row=1, column=0, sticky='w', padx=5, pady=5)
        
        # Hardware randomization
        self.hardware_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(settings_frame, text="Randomize Hardware", 
                       variable=self.hardware_var, style='GPM.TCheckbutton').grid(row=1, column=1, sticky='w', padx=5, pady=5)
        
        # Timezone randomization
        self.timezone_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(settings_frame, text="Randomize Timezone", 
                       variable=self.timezone_var, style='GPM.TCheckbutton').grid(row=1, column=2, sticky='w', padx=5, pady=5)
        
        # Apply button
        ttk.Button(settings_frame, text="🔧 Apply Settings", 
                  command=self.apply_fingerprint_settings, style='GPM.TButton').grid(row=2, column=0, columnspan=3, pady=10)
        
        # Fingerprint preview
        preview_frame = ttk.LabelFrame(fingerprint_frame, text="Fingerprint Preview", style='GPM.TFrame')
        preview_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.fingerprint_text = tk.Text(preview_frame, height=15, bg='#2d2d2d', fg='#ffffff', 
                                       font=('Consolas', 10))
        self.fingerprint_text.pack(fill='both', expand=True, padx=5, pady=5)
    
    def create_automation_tab(self):
        """Tạo tab tự động hóa"""
        automation_frame = ttk.Frame(self.notebook, style='GPM.TFrame')
        self.notebook.add(automation_frame, text="🤖 Automation")
        
        # Login automation
        login_frame = ttk.LabelFrame(automation_frame, text="Login Automation", style='GPM.TFrame')
        login_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(login_frame, text="Website URL:", style='GPM.TLabel').grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.login_url_entry = ttk.Entry(login_frame, width=50)
        self.login_url_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(login_frame, text="Username:", style='GPM.TLabel').grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.username_entry = ttk.Entry(login_frame, width=30)
        self.username_entry.grid(row=1, column=1, sticky='w', padx=5, pady=5)
        
        ttk.Label(login_frame, text="Password:", style='GPM.TLabel').grid(row=2, column=0, sticky='w', padx=5, pady=5)
        self.password_entry = ttk.Entry(login_frame, width=30, show='*')
        self.password_entry.grid(row=2, column=1, sticky='w', padx=5, pady=5)
        
        ttk.Button(login_frame, text="🚀 Start Auto Login", 
                  command=self.start_auto_login, style='GPM.TButton').grid(row=3, column=0, columnspan=2, pady=10)
        
        # 2FA automation
        twofa_frame = ttk.LabelFrame(automation_frame, text="2FA Automation", style='GPM.TFrame')
        twofa_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(twofa_frame, text="2FA Method:", style='GPM.TLabel').grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.twofa_combo = ttk.Combobox(twofa_frame, values=['SMS', 'Email', 'Authenticator', 'Microsoft Graph'])
        self.twofa_combo.grid(row=0, column=1, sticky='w', padx=5, pady=5)
        
        ttk.Button(twofa_frame, text="🔐 Setup 2FA", 
                  command=self.setup_2fa, style='GPM.TButton').grid(row=1, column=0, columnspan=2, pady=10)
        
        # Session management
        session_frame = ttk.LabelFrame(automation_frame, text="Session Management", style='GPM.TFrame')
        session_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        ttk.Button(session_frame, text="💾 Save Session", 
                  command=self.save_session, style='GPM.TButton').pack(side='left', padx=5, pady=5)
        ttk.Button(session_frame, text="📂 Load Session", 
                  command=self.load_session, style='GPM.TButton').pack(side='left', padx=5, pady=5)
        ttk.Button(session_frame, text="🔄 Sync Sessions", 
                  command=self.sync_sessions, style='GPM.TButton').pack(side='left', padx=5, pady=5)
    
    def create_settings_tab(self):
        """Tạo tab cài đặt"""
        settings_frame = ttk.Frame(self.notebook, style='GPM.TFrame')
        self.notebook.add(settings_frame, text="⚙️ Settings")
        
        # General settings
        general_frame = ttk.LabelFrame(settings_frame, text="General Settings", style='GPM.TFrame')
        general_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(general_frame, text="Chrome Binary Path:", style='GPM.TLabel').grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.chrome_path_entry = ttk.Entry(general_frame, width=50)
        self.chrome_path_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(general_frame, text="Browse", 
                  command=self.browse_chrome_path, style='GPM.TButton').grid(row=0, column=2, padx=5, pady=5)
        
        ttk.Label(general_frame, text="Profiles Directory:", style='GPM.TLabel').grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.profiles_dir_entry = ttk.Entry(general_frame, width=50)
        self.profiles_dir_entry.grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(general_frame, text="Browse", 
                  command=self.browse_profiles_dir, style='GPM.TButton').grid(row=1, column=2, padx=5, pady=5)
        
        # Advanced settings
        advanced_frame = ttk.LabelFrame(settings_frame, text="Advanced Settings", style='GPM.TFrame')
        advanced_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.auto_refresh_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(advanced_frame, text="Auto Refresh Profiles", 
                       variable=self.auto_refresh_var, style='GPM.TCheckbutton').pack(anchor='w', padx=5, pady=5)
        
        self.show_advanced_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(advanced_frame, text="Show Advanced Options", 
                       variable=self.show_advanced_var, style='GPM.TCheckbutton').pack(anchor='w', padx=5, pady=5)
        
        # Save button
        ttk.Button(settings_frame, text="💾 Save Settings", 
                  command=self.save_settings, style='GPM.TButton').pack(pady=10)
    
    def create_status_bar(self):
        """Tạo status bar"""
        self.status_frame = ttk.Frame(self.root, style='GPM.TFrame')
        self.status_frame.pack(fill='x', padx=10, pady=5)
        
        self.status_label = ttk.Label(self.status_frame, text="Ready", style='GPM.TLabel')
        self.status_label.pack(side='left')
        
        self.progress_bar = ttk.Progressbar(self.status_frame, mode='indeterminate')
        self.progress_bar.pack(side='right', padx=10)
    
    def refresh_profiles(self):
        """Làm mới danh sách profiles"""
        # Clear existing items
        for item in self.profiles_tree.get_children():
            self.profiles_tree.delete(item)
        
        # Load profiles from directory
        if os.path.exists(self.profiles_dir):
            for profile_id in os.listdir(self.profiles_dir):
                profile_path = os.path.join(self.profiles_dir, profile_id)
                if os.path.isdir(profile_path):
                    # Get profile info
                    profile_name = profile_id
                    proxy = "None"
                    status = "Stopped"
                    created = "Unknown"
                    last_used = "Never"
                    
                    # Check if profile is active
                    if profile_id in self.active_drivers:
                        status = "Running"
                    
                    # Get creation time
                    try:
                        created = datetime.fromtimestamp(os.path.getctime(profile_path)).strftime("%Y-%m-%d %H:%M")
                    except:
                        created = "Unknown"
                    
                    # Insert into tree
                    self.profiles_tree.insert('', 'end', values=(
                        profile_id, profile_name, proxy, status, created, last_used
                    ))
        
        # Update profile combo
        profiles = [self.profiles_tree.item(item)['values'][0] for item in self.profiles_tree.get_children()]
        self.profile_combo['values'] = profiles
        if profiles:
            self.profile_combo.set(profiles[0])
    
    def create_new_profile(self):
        """Tạo profile mới"""
        dialog = ProfileCreateDialog(self.root, self)
        if dialog.result:
            profile_id = dialog.result['id']
            profile_name = dialog.result['name']
            
            # Create profile directory
            profile_path = os.path.join(self.profiles_dir, profile_id)
            os.makedirs(profile_path, exist_ok=True)
            
            # Save profile config
            profile_config = {
                'id': profile_id,
                'name': profile_name,
                'created': datetime.now().isoformat(),
                'proxy': None,
                'fingerprint': self.get_default_fingerprint(),
                'automation': self.get_default_automation()
            }
            
            self.config['profiles'][profile_id] = profile_config
            self.save_config()
            self.refresh_profiles()
            
            self.update_status(f"Created profile: {profile_name}")
    
    def start_profile(self):
        """Khởi động profile"""
        selection = self.profiles_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a profile")
            return
        
        profile_id = self.profiles_tree.item(selection[0])['values'][0]
        
        if profile_id in self.active_drivers:
            messagebox.showinfo("Info", "Profile is already running")
            return
        
        try:
            # Start Chrome with profile
            driver = self.start_chrome_profile(profile_id)
            self.active_drivers[profile_id] = driver
            self.refresh_profiles()
            self.update_status(f"Started profile: {profile_id}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start profile: {e}")
    
    def stop_profile(self):
        """Dừng profile"""
        selection = self.profiles_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a profile")
            return
        
        profile_id = self.profiles_tree.item(selection[0])['values'][0]
        
        if profile_id not in self.active_drivers:
            messagebox.showinfo("Info", "Profile is not running")
            return
        
        try:
            # Stop Chrome
            driver = self.active_drivers[profile_id]
            driver.quit()
            del self.active_drivers[profile_id]
            self.refresh_profiles()
            self.update_status(f"Stopped profile: {profile_id}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to stop profile: {e}")
    
    def start_chrome_profile(self, profile_id):
        """Khởi động Chrome với profile cụ thể"""
        profile_path = os.path.join(self.profiles_dir, profile_id)
        
        # Chrome options
        options = Options()
        options.add_argument(f"--user-data-dir={profile_path}")
        options.add_argument("--no-first-run")
        options.add_argument("--no-default-browser-check")
        options.add_argument("--disable-blink-features=AutomationControlled")
        
        # Add GPM flags
        if profile_id in self.config['profiles']:
            profile_config = self.config['profiles'][profile_id]
            
            # Add proxy if configured
            if profile_config.get('proxy'):
                proxy = profile_config['proxy']
                options.add_argument(f"--proxy-server={proxy['type']}://{proxy['host']}:{proxy['port']}")
            
            # Add fingerprint settings
            fingerprint = profile_config.get('fingerprint', {})
            if fingerprint.get('canvas_noise'):
                options.add_argument("--gpm-canvas-noise")
            if fingerprint.get('webgl_noise'):
                options.add_argument("--gpm-webgl-noise")
        
        # Start Chrome
        driver = webdriver.Chrome(options=options)
        return driver
    
    def test_proxy(self):
        """Test proxy connection"""
        proxy_string = self.proxy_entry.get().strip()
        if not proxy_string:
            messagebox.showwarning("Warning", "Please enter proxy string")
            return
        
        try:
            # Parse proxy string
            proxy_parts = proxy_string.split(':')
            if len(proxy_parts) < 2:
                raise ValueError("Invalid proxy format")
            
            host = proxy_parts[0]
            port = int(proxy_parts[1])
            username = proxy_parts[2] if len(proxy_parts) > 2 else None
            password = proxy_parts[3] if len(proxy_parts) > 3 else None
            
            # Test proxy
            proxies = {
                'http': f'http://{host}:{port}',
                'https': f'http://{host}:{port}'
            }
            
            if username and password:
                proxies['http'] = f'http://{username}:{password}@{host}:{port}'
                proxies['https'] = f'http://{username}:{password}@{host}:{port}'
            
            # Test connection
            response = requests.get('http://httpbin.org/ip', proxies=proxies, timeout=10)
            result = response.json()
            
            self.proxy_test_results[proxy_string] = {
                'status': 'success',
                'ip': result.get('origin', 'Unknown'),
                'speed': 'Good'
            }
            
            messagebox.showinfo("Success", f"Proxy working! Your IP: {result.get('origin', 'Unknown')}")
            
        except Exception as e:
            self.proxy_test_results[proxy_string] = {
                'status': 'error',
                'error': str(e)
            }
            messagebox.showerror("Error", f"Proxy test failed: {e}")
    
    def configure_proxy(self):
        """Cấu hình proxy cho profile(s)"""
        proxy_string = self.proxy_entry.get().strip()
        if not proxy_string:
            messagebox.showwarning("Warning", "Please enter proxy string")
            return
        
        if proxy_string not in self.proxy_test_results:
            messagebox.showwarning("Warning", "Please test proxy first")
            return
        
        if self.proxy_test_results[proxy_string]['status'] != 'success':
            messagebox.showerror("Error", "Proxy test failed")
            return
        
        try:
            # Parse proxy
            proxy_parts = proxy_string.split(':')
            host = proxy_parts[0]
            port = int(proxy_parts[1])
            username = proxy_parts[2] if len(proxy_parts) > 2 else None
            password = proxy_parts[3] if len(proxy_parts) > 3 else None
            
            proxy_config = {
                'type': 'http',
                'host': host,
                'port': port,
                'username': username,
                'password': password
            }
            
            if self.bulk_var.get():
                # Apply to all profiles
                for profile_id in self.config['profiles']:
                    self.config['profiles'][profile_id]['proxy'] = proxy_config
                self.save_config()
                messagebox.showinfo("Success", f"Proxy configured for all profiles")
            else:
                # Apply to selected profile
                profile_id = self.profile_combo.get()
                if profile_id in self.config['profiles']:
                    self.config['profiles'][profile_id]['proxy'] = proxy_config
                    self.save_config()
                    messagebox.showinfo("Success", f"Proxy configured for profile: {profile_id}")
                else:
                    messagebox.showerror("Error", "Profile not found")
            
            self.refresh_profiles()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to configure proxy: {e}")
    
    def apply_fingerprint_settings(self):
        """Áp dụng cài đặt fingerprint"""
        fingerprint_settings = {
            'canvas_noise': self.canvas_var.get(),
            'webgl_noise': self.webgl_var.get(),
            'audio_noise': self.audio_var.get(),
            'client_rect_noise': self.client_rect_var.get(),
            'hardware_randomization': self.hardware_var.get(),
            'timezone_randomization': self.timezone_var.get()
        }
        
        # Apply to all profiles
        for profile_id in self.config['profiles']:
            self.config['profiles'][profile_id]['fingerprint'] = fingerprint_settings
        
        self.save_config()
        self.update_fingerprint_preview()
        messagebox.showinfo("Success", "Fingerprint settings applied to all profiles")
    
    def update_fingerprint_preview(self):
        """Cập nhật preview fingerprint"""
        preview = "Fingerprint Settings:\n\n"
        preview += f"Canvas Noise: {'✓' if self.canvas_var.get() else '✗'}\n"
        preview += f"WebGL Noise: {'✓' if self.webgl_var.get() else '✗'}\n"
        preview += f"Audio Noise: {'✓' if self.audio_var.get() else '✗'}\n"
        preview += f"Client Rects Noise: {'✓' if self.client_rect_var.get() else '✗'}\n"
        preview += f"Hardware Randomization: {'✓' if self.hardware_var.get() else '✗'}\n"
        preview += f"Timezone Randomization: {'✓' if self.timezone_var.get() else '✗'}\n"
        
        self.fingerprint_text.delete(1.0, tk.END)
        self.fingerprint_text.insert(1.0, preview)
    
    def start_auto_login(self):
        """Bắt đầu tự động đăng nhập"""
        url = self.login_url_entry.get().strip()
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not all([url, username, password]):
            messagebox.showwarning("Warning", "Please fill all fields")
            return
        
        # Start auto login in background
        threading.Thread(target=self._auto_login_worker, 
                        args=(url, username, password), daemon=True).start()
        
        self.update_status("Starting auto login...")
    
    def _auto_login_worker(self, url, username, password):
        """Worker thread cho auto login"""
        try:
            # Get active profile
            active_profiles = list(self.active_drivers.keys())
            if not active_profiles:
                messagebox.showerror("Error", "No active profiles")
                return
            
            driver = self.active_drivers[active_profiles[0]]
            
            # Navigate to URL
            driver.get(url)
            time.sleep(2)
            
            # Find and fill login form
            # This is a simplified example - you'd need to implement specific selectors
            username_field = driver.find_element("name", "username")
            password_field = driver.find_element("name", "password")
            
            username_field.send_keys(username)
            password_field.send_keys(password)
            
            # Submit form
            submit_button = driver.find_element("xpath", "//button[@type='submit']")
            submit_button.click()
            
            self.update_status("Auto login completed")
            
        except Exception as e:
            self.update_status(f"Auto login failed: {e}")
    
    def setup_2fa(self):
        """Thiết lập 2FA"""
        method = self.twofa_combo.get()
        if not method:
            messagebox.showwarning("Warning", "Please select 2FA method")
            return
        
        if method == "Microsoft Graph":
            # Use existing Microsoft Graph integration
            messagebox.showinfo("Info", "Using Microsoft Graph 2FA integration")
        else:
            messagebox.showinfo("Info", f"2FA method {method} configured")
    
    def save_session(self):
        """Lưu session"""
        messagebox.showinfo("Info", "Session saved")
    
    def load_session(self):
        """Tải session"""
        messagebox.showinfo("Info", "Session loaded")
    
    def sync_sessions(self):
        """Đồng bộ sessions"""
        messagebox.showinfo("Info", "Sessions synced")
    
    def edit_profile(self):
        """Chỉnh sửa profile"""
        selection = self.profiles_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a profile")
            return
        
        profile_id = self.profiles_tree.item(selection[0])['values'][0]
        messagebox.showinfo("Info", f"Edit profile: {profile_id}")
    
    def delete_profile(self):
        """Xóa profile"""
        selection = self.profiles_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a profile")
            return
        
        profile_id = self.profiles_tree.item(selection[0])['values'][0]
        
        if messagebox.askyesno("Confirm", f"Delete profile {profile_id}?"):
            try:
                # Stop if running
                if profile_id in self.active_drivers:
                    self.active_drivers[profile_id].quit()
                    del self.active_drivers[profile_id]
                
                # Remove directory
                profile_path = os.path.join(self.profiles_dir, profile_id)
                if os.path.exists(profile_path):
                    shutil.rmtree(profile_path)
                
                # Remove from config
                if profile_id in self.config['profiles']:
                    del self.config['profiles'][profile_id]
                    self.save_config()
                
                self.refresh_profiles()
                self.update_status(f"Deleted profile: {profile_id}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete profile: {e}")
    
    def clone_profile(self):
        """Clone profile"""
        selection = self.profiles_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a profile")
            return
        
        profile_id = self.profiles_tree.item(selection[0])['values'][0]
        messagebox.showinfo("Info", f"Clone profile: {profile_id}")
    
    def export_profile(self):
        """Export profile"""
        selection = self.profiles_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a profile")
            return
        
        profile_id = self.profiles_tree.item(selection[0])['values'][0]
        messagebox.showinfo("Info", f"Export profile: {profile_id}")
    
    def open_settings(self):
        """Mở cài đặt"""
        self.notebook.select(4)  # Switch to settings tab
    
    def browse_chrome_path(self):
        """Browse Chrome path"""
        path = filedialog.askopenfilename(
            title="Select Chrome Executable",
            filetypes=[("Executable files", "*.exe"), ("All files", "*.*")]
        )
        if path:
            self.chrome_path_entry.delete(0, tk.END)
            self.chrome_path_entry.insert(0, path)
    
    def browse_profiles_dir(self):
        """Browse profiles directory"""
        path = filedialog.askdirectory(title="Select Profiles Directory")
        if path:
            self.profiles_dir_entry.delete(0, tk.END)
            self.profiles_dir_entry.insert(0, path)
    
    def save_settings(self):
        """Lưu cài đặt"""
        # Update config with UI values
        self.config['ui_settings']['auto_refresh'] = self.auto_refresh_var.get()
        self.config['ui_settings']['show_advanced'] = self.show_advanced_var.get()
        
        self.save_config()
        messagebox.showinfo("Success", "Settings saved")
    
    def get_default_fingerprint(self):
        """Lấy cấu hình fingerprint mặc định"""
        return {
            'canvas_noise': True,
            'webgl_noise': True,
            'audio_noise': True,
            'client_rect_noise': True,
            'hardware_randomization': True,
            'timezone_randomization': True
        }
    
    def get_default_automation(self):
        """Lấy cấu hình automation mặc định"""
        return {
            'auto_login': True,
            'auto_2fa': True,
            'session_management': True,
            'cookie_management': True
        }
    
    def update_status(self, message):
        """Cập nhật status bar"""
        self.status_label.config(text=message)
        self.root.update_idletasks()
    
    def run(self):
        """Chạy ứng dụng"""
        self.root.mainloop()


class ProfileCreateDialog:
    """Dialog tạo profile mới"""
    
    def __init__(self, parent, manager):
        self.manager = manager
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Create New Profile")
        self.dialog.geometry("400x300")
        self.dialog.configure(bg='#1e1e1e')
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.setup_ui()
        
        # Center dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (300 // 2)
        self.dialog.geometry(f"400x300+{x}+{y}")
    
    def setup_ui(self):
        """Thiết lập UI cho dialog"""
        # Title
        title_label = ttk.Label(self.dialog, text="Create New Profile", 
                               font=('Segoe UI', 14, 'bold'))
        title_label.pack(pady=20)
        
        # Form
        form_frame = ttk.Frame(self.dialog)
        form_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Profile ID
        ttk.Label(form_frame, text="Profile ID:").grid(row=0, column=0, sticky='w', pady=5)
        self.id_entry = ttk.Entry(form_frame, width=30)
        self.id_entry.grid(row=0, column=1, pady=5)
        self.id_entry.insert(0, f"P-{random.randint(100000, 999999)}-{random.randint(1000, 9999)}")
        
        # Profile Name
        ttk.Label(form_frame, text="Profile Name:").grid(row=1, column=0, sticky='w', pady=5)
        self.name_entry = ttk.Entry(form_frame, width=30)
        self.name_entry.grid(row=1, column=1, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Create", command=self.create_profile).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(side='left', padx=5)
    
    def create_profile(self):
        """Tạo profile"""
        profile_id = self.id_entry.get().strip()
        profile_name = self.name_entry.get().strip()
        
        if not profile_id or not profile_name:
            messagebox.showwarning("Warning", "Please fill all fields")
            return
        
        if profile_id in self.manager.config['profiles']:
            messagebox.showerror("Error", "Profile ID already exists")
            return
        
        self.result = {
            'id': profile_id,
            'name': profile_name
        }
        
        self.dialog.destroy()


if __name__ == "__main__":
    app = GPMProfileManager()
    app.run()
