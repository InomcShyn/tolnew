#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TikTok Archived Data UI Component

This module provides UI components for viewing and managing archived TikTok data.
It's designed to be integrated into the existing TikTok management dialog.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import pyperclip
from datetime import datetime
from typing import Callable, Optional

from .tiktok_archived_data import TikTokArchivedDataManager


class ArchivedDataDialog:
    """
    Dialog for viewing and managing archived TikTok data
    
    This is a secondary dialog that opens from the main TikTok management screen.
    """
    
    def __init__(self, parent, archived_manager: TikTokArchivedDataManager, on_restore_callback: Optional[Callable] = None):
        """
        Initialize archived data dialog
        
        Args:
            parent: Parent window
            archived_manager: TikTokArchivedDataManager instance
            on_restore_callback: Callback function when account is restored
        """
        self.parent = parent
        self.archived_manager = archived_manager
        self.on_restore_callback = on_restore_callback
        
        # Create dialog
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("📦 Data cũ (đã sử dụng)")
        self.dialog.geometry("1000x600")
        self.dialog.resizable(True, True)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
        
        self._create_ui()
        self._load_data()
    
    def _create_ui(self):
        """Create UI components"""
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title with explanation
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 15))
        
        title_label = ttk.Label(title_frame, text="📦 Data cũ (đã sử dụng)", 
                               font=("Segoe UI", 14, "bold"))
        title_label.pack(side=tk.LEFT)
        
        # Info label
        info_label = ttk.Label(main_frame, 
                              text="Đây là dữ liệu TikTok từ các profile đã xóa. Data này được lưu riêng và không bị mất khi xóa profile.",
                              font=("Segoe UI", 9),
                              foreground="gray")
        info_label.pack(fill=tk.X, pady=(0, 10))
        
        # Data list frame
        list_frame = ttk.LabelFrame(main_frame, text="📋 Danh sách Data đã lưu", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Treeview for archived data
        columns = ("Username", "Email", "Original Profile", "Archived At", "Note")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        
        # Configure columns
        column_widths = {
            "Username": 150,
            "Email": 200,
            "Original Profile": 150,
            "Archived At": 180,
            "Note": 200
        }
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=column_widths.get(col, 100))
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Left buttons (actions)
        left_buttons = ttk.Frame(buttons_frame)
        left_buttons.pack(side=tk.LEFT)
        
        restore_btn = tk.Button(left_buttons, text="♻️ Khôi phục", 
                               command=self._restore_selected,
                               font=('Segoe UI', 9, 'bold'),
                               bg='#27ae60', fg='white', relief='flat', 
                               padx=15, pady=8, cursor='hand2')
        restore_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        copy_btn = tk.Button(left_buttons, text="📋 Copy thông tin", 
                            command=self._copy_credentials,
                            font=('Segoe UI', 9, 'bold'),
                            bg='#3498db', fg='white', relief='flat', 
                            padx=15, pady=8, cursor='hand2')
        copy_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        delete_btn = tk.Button(left_buttons, text="🗑️ Xóa vĩnh viễn", 
                              command=self._delete_selected,
                              font=('Segoe UI', 9, 'bold'),
                              bg='#e74c3c', fg='white', relief='flat', 
                              padx=15, pady=8, cursor='hand2')
        delete_btn.pack(side=tk.LEFT)
        
        # Right buttons (close)
        right_buttons = ttk.Frame(buttons_frame)
        right_buttons.pack(side=tk.RIGHT)
        
        refresh_btn = tk.Button(right_buttons, text="🔄 Refresh", 
                               command=self._load_data,
                               font=('Segoe UI', 9),
                               bg='#95a5a6', fg='white', relief='flat', 
                               padx=15, pady=8, cursor='hand2')
        refresh_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        close_btn = tk.Button(right_buttons, text="✖ Đóng", 
                             command=self.dialog.destroy,
                             font=('Segoe UI', 9),
                             bg='#7f8c8d', fg='white', relief='flat', 
                             padx=15, pady=8, cursor='hand2')
        close_btn.pack(side=tk.LEFT)
    
    def _load_data(self):
        """Load archived data into treeview"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Get archived data
        archived_data = self.archived_manager.get_archived_data()
        
        if not archived_data:
            # Show empty message
            self.tree.insert("", tk.END, values=(
                "Không có data nào",
                "",
                "",
                "",
                ""
            ))
            return
        
        # Add items
        for account in archived_data:
            username = account.get('username', 'N/A')
            email = account.get('email', 'N/A')
            original_profile = account.get('original_profile', 'N/A')
            archived_at = account.get('archived_at', 'N/A')
            note = account.get('note', '')
            
            # Format archived_at
            if archived_at != 'N/A':
                try:
                    dt = datetime.fromisoformat(archived_at)
                    archived_at = dt.strftime("%Y-%m-%d %H:%M:%S")
                except:
                    pass
            
            self.tree.insert("", tk.END, values=(
                username,
                email,
                original_profile,
                archived_at,
                note
            ))
        
        print(f"[ARCHIVED-UI] Loaded {len(archived_data)} archived accounts")
    
    def _get_selected_index(self) -> Optional[int]:
        """Get selected item index"""
        selection = self.tree.selection()
        if not selection:
            return None
        
        # Get index of selected item
        item = selection[0]
        children = self.tree.get_children()
        
        try:
            return children.index(item)
        except ValueError:
            return None
    
    def _restore_selected(self):
        """Restore selected archived account"""
        index = self._get_selected_index()
        if index is None:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn account cần khôi phục!")
            return
        
        # Get archived data to show info
        archived_data = self.archived_manager.get_archived_data()
        if index >= len(archived_data):
            messagebox.showerror("Lỗi", "Invalid selection")
            return
        
        account = archived_data[index]
        username = account.get('username', 'unknown')
        original_profile = account.get('original_profile', 'unknown')
        
        # Ask for new profile name
        new_profile = tk.simpledialog.askstring(
            "Khôi phục Account",
            f"Khôi phục account: {username}\n"
            f"Profile gốc: {original_profile}\n\n"
            f"Nhập tên profile mới (hoặc để trống để dùng tên gốc):",
            parent=self.dialog
        )
        
        if new_profile is None:  # User cancelled
            return
        
        # Use original profile if empty
        if not new_profile.strip():
            new_profile = original_profile
        
        # Restore
        success, message = self.archived_manager.restore_account(index, new_profile)
        
        if success:
            messagebox.showinfo("Thành công", f"Đã khôi phục account về profile: {new_profile}")
            self._load_data()  # Refresh list
            
            # Call callback if provided
            if self.on_restore_callback:
                self.on_restore_callback()
        else:
            messagebox.showerror("Lỗi", f"Không thể khôi phục: {message}")
    
    def _copy_credentials(self):
        """Copy credentials of selected account"""
        index = self._get_selected_index()
        if index is None:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn account cần copy!")
            return
        
        # Get credentials
        credentials = self.archived_manager.get_account_credentials(index)
        if not credentials:
            messagebox.showerror("Lỗi", "Không thể lấy thông tin account")
            return
        
        # Format for clipboard
        text = f"Username: {credentials['username']}\n"
        text += f"Email: {credentials['email']}\n"
        text += f"Password: {credentials['password']}"
        
        # Copy to clipboard
        try:
            pyperclip.copy(text)
            messagebox.showinfo("Thành công", "Đã copy thông tin vào clipboard!")
        except Exception as e:
            # Fallback: show in dialog
            messagebox.showinfo("Thông tin Account", text)
    
    def _delete_selected(self):
        """Permanently delete selected archived account"""
        index = self._get_selected_index()
        if index is None:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn account cần xóa!")
            return
        
        # Get account info
        archived_data = self.archived_manager.get_archived_data()
        if index >= len(archived_data):
            messagebox.showerror("Lỗi", "Invalid selection")
            return
        
        account = archived_data[index]
        username = account.get('username', 'unknown')
        
        # Confirm deletion
        if not messagebox.askyesno(
            "Xác nhận xóa",
            f"Bạn có chắc muốn XÓA VĨNH VIỄN account này?\n\n"
            f"Username: {username}\n\n"
            f"⚠️ Hành động này KHÔNG THỂ HOÀN TÁC!",
            icon='warning'
        ):
            return
        
        # Delete
        success, message = self.archived_manager.delete_archived(index)
        
        if success:
            messagebox.showinfo("Thành công", "Đã xóa account")
            self._load_data()  # Refresh list
        else:
            messagebox.showerror("Lỗi", f"Không thể xóa: {message}")


def open_archived_data_dialog(parent, base_dir: str = None, on_restore_callback: Optional[Callable] = None):
    """
    Open archived data dialog
    
    This is the main entry point to open the archived data UI.
    Call this from the TikTok management dialog.
    
    Args:
        parent: Parent window
        base_dir: Base directory for data storage
        on_restore_callback: Callback when account is restored
    
    Returns:
        ArchivedDataDialog instance
    """
    archived_manager = TikTokArchivedDataManager(base_dir)
    return ArchivedDataDialog(parent, archived_manager, on_restore_callback)
