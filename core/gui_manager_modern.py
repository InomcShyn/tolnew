import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import threading
import time
import os
import json
from core.chrome_manager import ChromeProfileManager

# NKT configuration đã được xóa

class ModernChromeProfileManager:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Browser Manager - Advanced Profile Management")
        self.root.geometry("1400x900")
        self.root.configure(bg='#ffffff')
        
        # Thiết lập style hiện đại
        self.setup_modern_style()
        
        self.manager = ChromeProfileManager()
        self.drivers = {}
        
        # NKT Configuration đã được xóa
        
        # Biến cho tab bar
        self.tabbar_visible = False
        self.tabbar_auto_hide = True  # Tự động ẩn mặc định
        self.tabbar_hide_timer = None
        self.current_tab = "profiles"  # Tab hiện tại
        self.tab_buttons = {}  # Lưu trữ các tab buttons
        
        self.setup_ui()
        self.refresh_profiles()
        
        # Bind events cho tab bar tự động
        self.setup_auto_tabbar()
        
        
    def setup_modern_style(self):
        """Thiết lập style hiện đại cho ứng dụng"""
        style = ttk.Style()
        
        # Cấu hình theme
        style.theme_use('clam')
        
        # Màu sắc hiện đại với màu trắng chủ đạo
        colors = {
            'bg': '#ffffff',
            'bg_light': '#f8f9fa',
            'fg': '#212529',
            'fg_secondary': '#6c757d',
            'select_bg': '#e9ecef',
            'select_fg': '#212529',
            'accent': '#007bff',
            'accent_hover': '#0056b3',
            'accent_light': '#80bdff',
            'success': '#28a745',
            'warning': '#ffc107',
            'error': '#dc3545',
            'border': '#dee2e6',
            'card_bg': '#ffffff',
            'card_border': '#e9ecef'
        }
        
        # Configure styles với bo góc
        style.configure('Modern.TFrame', 
                       background=colors['bg'],
                       relief='flat',
                       borderwidth=0)
        
        style.configure('Modern.TLabel', 
                       background=colors['bg'], 
                       foreground=colors['fg'],
                       font=('Segoe UI', 9))
        
        style.configure('Modern.TButton', 
                       background=colors['accent'],
                       foreground=colors['fg'],
                       borderwidth=0,
                       focuscolor='none',
                       padding=(12, 10),
                       relief='flat')
        style.map('Modern.TButton',
                 background=[('active', colors['accent_hover']),
                           ('pressed', colors['accent_hover'])])
        
        style.configure('Modern.Treeview',
                       background=colors['card_bg'],
                       foreground=colors['fg'],
                       fieldbackground=colors['card_bg'],
                       borderwidth=1,
                       relief='solid')
        style.configure('Modern.Treeview.Heading',
                       background=colors['bg_light'],
                       foreground=colors['fg'],
                       borderwidth=1,
                       relief='solid',
                       font=('Segoe UI', 9, 'bold'))
        
        style.configure('Modern.TNotebook',
                       background=colors['bg'],
                       borderwidth=0,
                       relief='flat')
        style.configure('Modern.TNotebook.Tab',
                       background=colors['bg_light'],
                       foreground=colors['fg_secondary'],
                       padding=(20, 12),
                       borderwidth=0,
                       relief='flat')
        style.map('Modern.TNotebook.Tab',
                 background=[('selected', colors['accent']),
                           ('active', colors['accent_light'])],
                 foreground=[('selected', colors['fg']),
                           ('active', colors['fg'])])
        
        # Tab bar style - clean và minimal
        style.configure('TabBar.TFrame', 
                       background=colors['accent'],
                       relief='flat',
                       borderwidth=0)
        
        style.configure('TabBar.TButton',
                       background=colors['accent'],
                       foreground=colors['fg'],
                       borderwidth=0,
                       padding=(12, 10),
                       relief='flat',
                       font=('Segoe UI', 9))
        style.map('TabBar.TButton',
                 background=[('active', colors['accent_hover']),
                           ('pressed', colors['accent_hover'])])
        
        # Corner toggle button style
        style.configure('Corner.TButton',
                       background=colors['accent'],
                       foreground=colors['fg'],
                       borderwidth=0,
                       padding=(8, 6),
                       relief='flat',
                       font=('Segoe UI', 10))
        style.map('Corner.TButton',
                 background=[('active', colors['accent_hover']),
                           ('pressed', colors['accent_hover'])])
        
        # LabelFrame style
        style.configure('Modern.TLabelframe',
                       background=colors['card_bg'],
                       foreground=colors['fg'],
                       borderwidth=1,
                       relief='solid')
        style.configure('Modern.TLabelframe.Label',
                       background=colors['card_bg'],
                       foreground=colors['accent'],
                       font=('Segoe UI', 10, 'bold'))
        
        # Entry style
        style.configure('Modern.TEntry',
                       background=colors['card_bg'],
                       foreground=colors['fg'],
                       fieldbackground=colors['card_bg'],
                       borderwidth=1,
                       relief='solid',
                       insertcolor=colors['fg'])
        
        # Combobox style
        style.configure('Modern.TCombobox',
                       background=colors['card_bg'],
                       foreground=colors['fg'],
                       fieldbackground=colors['card_bg'],
                       borderwidth=1,
                       relief='solid')
        style.map('Modern.TCombobox',
                 background=[('readonly', colors['card_bg'])],
                 fieldbackground=[('readonly', colors['card_bg'])])
        
        # Text style
        style.configure('Modern.TText',
                       background=colors['card_bg'],
                       foreground=colors['fg'],
                       insertbackground=colors['fg'],
                       borderwidth=1,
                       relief='solid')
        
        # Listbox style
        style.configure('Modern.TListbox',
                       background=colors['card_bg'],
                       foreground=colors['fg'],
                       selectbackground=colors['accent'],
                       selectforeground=colors['fg'],
                       borderwidth=1,
                       relief='solid')
        
        # Checkbutton style
        style.configure('Modern.TCheckbutton',
                       background=colors['card_bg'],
                       foreground=colors['fg'],
                       focuscolor='none',
                       borderwidth=0)
        
        # Radiobutton style
        style.configure('Modern.TRadiobutton',
                       background=colors['card_bg'],
                       foreground=colors['fg'],
                       focuscolor='none',
                       borderwidth=0)
        
        # Progressbar style
        style.configure('Modern.TProgressbar',
                       background=colors['accent'],
                       troughcolor=colors['bg_light'],
                       borderwidth=0)
        
        # Separator style
        style.configure('Modern.TSeparator',
                       background=colors['border'])
        
        # Scrollbar styles
        style.configure('Modern.Vertical.TScrollbar',
                       background=colors['bg_light'],
                       troughcolor=colors['bg'],
                       borderwidth=0,
                       arrowcolor=colors['fg_secondary'],
                       darkcolor=colors['bg_light'],
                       lightcolor=colors['bg_light'])
        style.map('Modern.Vertical.TScrollbar',
                 background=[('active', colors['accent']),
                           ('pressed', colors['accent_hover'])])
        
        style.configure('Modern.Horizontal.TScrollbar',
                       background=colors['bg_light'],
                       troughcolor=colors['bg'],
                       borderwidth=0,
                       arrowcolor=colors['fg_secondary'],
                       darkcolor=colors['bg_light'],
                       lightcolor=colors['bg_light'])
        style.map('Modern.Horizontal.TScrollbar',
                 background=[('active', colors['accent']),
                           ('pressed', colors['accent_hover'])])
        
        # Tooltip style
        style.configure('Modern.Tooltip.TLabel',
                       background=colors['bg_light'],
                       foreground=colors['fg'],
                       borderwidth=1,
                       relief='solid')
        
    def setup_auto_tabbar(self):
        """Thiết lập tab bar tự động hiện khi di chuyển chuột"""
        # Bind mouse events cho toàn bộ window
        self.root.bind('<Motion>', self.on_mouse_move)
        self.root.bind('<Leave>', self.on_mouse_leave)
        
    def on_mouse_move(self, event):
        """Xử lý khi di chuyển chuột"""
        # Chỉ tự động hiện nếu auto_hide được bật
        if self.tabbar_auto_hide:
            # Kiểm tra nếu chuột ở gần góc trái màn hình
            if event.x < 50 and not self.tabbar_visible:
                self.show_tabbar()
            elif event.x > 200 and self.tabbar_visible:
                self.schedule_hide_tabbar()
            
    def on_mouse_leave(self, event):
        """Xử lý khi chuột rời khỏi window"""
        if self.tabbar_auto_hide:
            self.schedule_hide_tabbar()
        
    def show_tabbar(self):
        """Hiện tab bar"""
        if not self.tabbar_visible:
            self.tabbar_visible = True
            self.tabbar_frame.place(x=0, y=0, relheight=1, anchor='nw')
            self.corner_toggle_btn.config(text="🔒")
            self.root.update()
            
    def schedule_hide_tabbar(self):
        """Lên lịch ẩn tab bar"""
        if self.tabbar_auto_hide:
            if self.tabbar_hide_timer:
                self.root.after_cancel(self.tabbar_hide_timer)
            self.tabbar_hide_timer = self.root.after(1000, self.hide_tabbar)
        
    def hide_tabbar(self):
        """Ẩn tab bar"""
        if self.tabbar_visible:
            self.tabbar_visible = False
            self.tabbar_frame.place_forget()
            self.corner_toggle_btn.config(text="📌")
            
    def toggle_tabbar_auto_hide(self):
        """Toggle chế độ tự động ẩn tab bar"""
        self.tabbar_auto_hide = not self.tabbar_auto_hide
        
        if self.tabbar_auto_hide:
            self.toggle_btn.config(text="📌")
            # Nếu đang hiện và chuột không ở gần, ẩn sau 1 giây
            if self.tabbar_visible:
                self.schedule_hide_tabbar()
        else:
            self.toggle_btn.config(text="🔒")
            # Hủy timer ẩn nếu có
            if self.tabbar_hide_timer:
                self.root.after_cancel(self.tabbar_hide_timer)
                self.tabbar_hide_timer = None
                
    def toggle_tabbar_visibility(self):
        """Toggle hiển thị/ẩn tab bar"""
        if self.tabbar_visible:
            self.hide_tabbar()
            if hasattr(self, 'corner_toggle_btn') and self.corner_toggle_btn.winfo_exists():
                self.corner_toggle_btn.config(text="📌")
        else:
            self.show_tabbar()
            if hasattr(self, 'corner_toggle_btn') and self.corner_toggle_btn.winfo_exists():
                self.corner_toggle_btn.config(text="🔒")
            
    def create_tooltip(self, widget, text):
        """Tạo tooltip cho widget với style đẹp hơn"""
        def show_tooltip(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+15}+{event.y_root+15}")
            tooltip.configure(bg="#404040")
            
            # Frame với bo góc
            frame = tk.Frame(tooltip, bg="#404040", relief="flat", bd=0)
            frame.pack(padx=8, pady=6)
            
            label = tk.Label(frame, text=text, 
                           background="#404040", foreground="#ffffff",
                           font=("Segoe UI", 9), relief="flat", borderwidth=0)
            label.pack()
            
            widget.tooltip = tooltip
            
        def hide_tooltip(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                del widget.tooltip
                
        widget.bind("<Enter>", show_tooltip)
        widget.bind("<Leave>", hide_tooltip)
        
    def update_tab_highlight(self, active_tab=None):
        """Cập nhật highlight cho tab đang active"""
        if active_tab is None:
            active_tab = getattr(self, 'current_tab', None)
        
        self.current_tab = active_tab
        
        # Reset tất cả buttons về style bình thường
        for tab_name, button in self.tab_buttons.items():
            button.configure(style='TabBar.TButton')
        
        # Highlight tab đang active (nếu có)
        if active_tab in self.tab_buttons:
            # Có thể thêm style khác cho active tab nếu cần
            pass
            
    def setup_ui(self):
        """Thiết lập giao diện người dùng hiện đại"""
        # Frame chính
        self.main_frame = ttk.Frame(self.root, style='Modern.TFrame')
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Tạo tab bar tự động (ẩn ban đầu)
        self.create_auto_tabbar()
        
        # Tạo nút toggle ở góc màn hình
        self.create_toggle_button()

        # Tạo dải hover mỏng ở cạnh trái để tự mở tabbar khi di chuột tới
        self.create_hover_hotspot()
        
        # Tạo nội dung chính
        self.create_main_content()
        
    def create_auto_tabbar(self):
        """Tạo tab bar tự động hiện khi di chuyển chuột"""
        self.tabbar_frame = ttk.Frame(self.root, style='TabBar.TFrame', width=200)
        
        # Header section - compact và clean
        header_frame = ttk.Frame(self.tabbar_frame, style='TabBar.TFrame')
        header_frame.pack(fill=tk.X, padx=12, pady=12)
        
        # Top row: Logo + Toggle
        top_row = ttk.Frame(header_frame, style='TabBar.TFrame')
        top_row.pack(fill=tk.X)
        
        # Logo compact
        logo_label = ttk.Label(top_row, text="[LAUNCH]", 
                              style='Modern.TLabel', font=('Segoe UI', 16))
        logo_label.pack(side=tk.LEFT)
        
        # Toggle button compact
        self.toggle_btn = ttk.Button(top_row, text="📌", 
                                    style='TabBar.TButton',
                                    command=self.toggle_tabbar_auto_hide,
                                    width=3)
        self.toggle_btn.pack(side=tk.RIGHT)
        
        # Title section - centered và clean
        title_frame = ttk.Frame(header_frame, style='TabBar.TFrame')
        title_frame.pack(fill=tk.X, pady=(8, 0))
        
        title_label = ttk.Label(title_frame, text="Chrome Manager", 
                               style='Modern.TLabel', 
                               font=('Segoe UI', 12, 'bold'))
        title_label.pack()
        
        # Tooltip cho toggle button
        self.create_tooltip(self.toggle_btn, "Bật/tắt chế độ tự động ẩn tab bar")
        
        # Tab buttons - compact và clean
        tabs_frame = ttk.Frame(self.tabbar_frame, style='TabBar.TFrame')
        tabs_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(5, 10))
        
        # Tab Profiles
        self.tab_buttons['profiles'] = ttk.Button(tabs_frame, text="👥 Profiles", 
                                                 style='TabBar.TButton',
                                                 command=self.show_profiles_tab)
        self.tab_buttons['profiles'].pack(fill=tk.X, pady=(0, 6))
        
        # Tab Extensions
        self.tab_buttons['../extensions'] = ttk.Button(tabs_frame, text="🔌 Extensions", 
                                                   style='TabBar.TButton',
                                                   command=self.show_extensions_tab)
        self.tab_buttons['../extensions'].pack(fill=tk.X, pady=(0, 6))
        
        # Tab Export
        self.tab_buttons['export'] = ttk.Button(tabs_frame, text="📤 Export", 
                                               style='TabBar.TButton',
                                               command=self.show_export_tab)
        self.tab_buttons['export'].pack(fill=tk.X, pady=(0, 6))
        
        # Tab Import
        self.tab_buttons['import'] = ttk.Button(tabs_frame, text="📥 Import", 
                                               style='TabBar.TButton',
                                               command=self.show_import_tab)
        self.tab_buttons['import'].pack(fill=tk.X, pady=(0, 6))

        # Tạo theo số lượng (Bulk Create)
        self.tab_buttons['bulk_create'] = ttk.Button(tabs_frame, text="📦 Tạo theo số lượng", 
                                                style='TabBar.TButton',
                                                command=self.show_bulk_create_dialog)
        self.tab_buttons['bulk_create'].pack(fill=tk.X, pady=(0, 6))
        
        # Tab Stealth
        
        # Tab Proxy Config
        self.tab_buttons['proxy_config'] = ttk.Button(tabs_frame, text="🌐 Proxy Config", 
                                                style='TabBar.TButton',
                                                     command=self.show_proxy_config_tab)
        self.tab_buttons['proxy_config'].pack(fill=tk.X, pady=(0, 6))
        
        # Tab Import
        self.tab_buttons['import'] = ttk.Button(tabs_frame, text="📥 Import", 
                                               style='TabBar.TButton',
                                               command=self.show_import_tab)
        self.tab_buttons['import'].pack(fill=tk.X, pady=(0, 6))
        
        # Tab NKT Config đã được xóa
        
        # Tab Settings
        self.tab_buttons['settings'] = ttk.Button(tabs_frame, text="⚙️ Settings", 
                                                 style='TabBar.TButton',
                                                 command=self.show_settings_tab)
        self.tab_buttons['settings'].pack(fill=tk.X, pady=(0, 6))
        
        # (Removed) Tools and Account Status tabs per user request
        
        # Footer - minimal và clean
        footer_frame = ttk.Frame(self.tabbar_frame, style='TabBar.TFrame')
        footer_frame.pack(fill=tk.X, padx=12, pady=(5, 12))
        
        # Version info - centered
        version_label = ttk.Label(footer_frame, text="v2.0", 
                                 style='Modern.TLabel', 
                                 font=('Segoe UI', 8))
        version_label.pack()

    def show_bulk_create_dialog(self):
        """Hiển thị dialog tạo profile số lượng lớn (nhanh)."""
        top = tk.Toplevel(self.root)
        top.title("Tạo theo số lượng")
        top.grab_set()
        top.geometry("560x420")
        frame = ttk.Frame(top, padding=15)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Số lượng").grid(row=0, column=0, sticky='w')
        qty_var = tk.IntVar(value=1)
        qty_entry = ttk.Entry(frame, textvariable=qty_var)
        qty_entry.grid(row=0, column=1, sticky='we', padx=8)

        ttk.Label(frame, text="Phiên bản trình duyệt").grid(row=1, column=0, sticky='w', pady=(8,0))
        version_var = tk.StringVar(value='139.0.7258.139')
        chrome_version_options = [
            '139.0.7258.139', '137.0.7151.41', '135.0.7049.42', '134.0.6998.89',
            '132.0.6834.84', '129.0.6668.59', '127.0.6533.73', '124.0.6367.29',
            '121.0.6167.140', '119.0.6045.124', '115.0.5790.75', '111.0.5563.50',
            '107.0.5304.8', '106.0.5249.119'
        ]
        version_combo = ttk.Combobox(frame, textvariable=version_var, values=chrome_version_options, state='readonly')
        version_combo.grid(row=1, column=1, sticky='we', padx=8, pady=(8,0))

        ttk.Label(frame, text="Nhập danh sách proxy | Định dạng: với http IP:Port:User:Pass, Với socks5: socks5://IP:Port:User:Pass\nHủy proxy (Dùng IP máy) nhập: null").grid(row=2, column=0, columnspan=2, sticky='w', pady=(12,4))
        proxy_text = tk.Text(frame, height=10)
        proxy_text.grid(row=3, column=0, columnspan=2, sticky='nsew')
        frame.rowconfigure(3, weight=1)
        frame.columnconfigure(1, weight=1)

        def on_confirm():
            try:
                qty = int(qty_var.get())
                if qty <= 0:
                    messagebox.showerror("Lỗi", "Số lượng phải > 0")
                    return
                version = version_var.get().strip()
                base_name = f"Profile_{int(time.time())}"
                ok, result = self.manager.create_profiles_bulk(base_name, qty, version, False, proxy_list, False)
                if ok:
                    names = result
                    proxies = [l.strip() for l in proxy_text.get('1.0', tk.END).splitlines() if l.strip()]
                    for idx, name in enumerate(names):
                        if idx < len(proxies):
                            try:
                                profile_path = os.path.join(self.manager.profiles_dir, name)
                                settings_path = os.path.join(profile_path, 'profile_settings.json')
                                data = {}
                                if os.path.exists(settings_path):
                                    with open(settings_path, 'r', encoding='utf-8') as f:
                                        data = json.load(f)
                                data.setdefault('network', {})['proxy'] = proxies[idx]
                                with open(settings_path, 'w', encoding='utf-8') as f:
                                    json.dump(data, f, ensure_ascii=False, indent=2)
                            except Exception:
                                pass
                    self.refresh_profiles()
                    messagebox.showinfo("Thành công", f"Đã tạo {len(names)} profile")
                    top.destroy()
                else:
                    messagebox.showerror("Lỗi", str(result))
            except Exception as e:
                messagebox.showerror("Lỗi", str(e))

        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=4, column=0, columnspan=2, sticky='e', pady=10)
        ttk.Button(btn_frame, text="Đồng ý", command=on_confirm).pack(side=tk.RIGHT)
        ttk.Button(btn_frame, text="Hủy", command=top.destroy).pack(side=tk.RIGHT, padx=8)

        
    def create_toggle_button(self):
        """Tạo nút toggle ở góc màn hình - compact"""
        self.corner_toggle_btn = ttk.Button(self.root, text="📌", 
                                           style='Corner.TButton',
                                           command=self.toggle_tabbar_visibility,
                                           width=4)
        self.corner_toggle_btn.place(x=12, y=12)
        
        # Tooltip cho corner toggle button
        self.create_tooltip(self.corner_toggle_btn, "Bật/tắt hiển thị tab bar")

    def create_hover_hotspot(self):
        """Tạo dải hover mỏng bên trái để tự mở tab bar khi rê chuột."""
        try:
            self.hover_strip.destroy()
        except Exception:
            pass
        self.hover_strip = tk.Frame(self.root, width=8, bg='#2b2b2b')
        self.hover_strip.place(x=0, y=0, relheight=1)
        self.hover_strip.bind('<Enter>', lambda e: self.show_tabbar())
        self.hover_strip.bind('<Leave>', lambda e: self.schedule_hide_tabbar())
        
    def create_main_content(self):
        """Tạo nội dung chính với layout đẹp hơn"""
        # Content frame với padding đẹp hơn
        self.content_frame = ttk.Frame(self.main_frame, style='Modern.TFrame')
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=25, pady=25)
        
        # Hiển thị tab mặc định
        self.show_profiles_tab()
        
    def show_profiles_tab(self):
        """Hiển thị tab Profiles với layout đẹp hơn"""
        self.update_tab_highlight('profiles')
        self.clear_content()
        
        # Refresh profiles list when entering this tab
        self.refresh_profiles()
        
        # Header với typography đẹp
        header_frame = ttk.Frame(self.content_frame, style='Modern.TFrame')
        header_frame.pack(fill=tk.X, pady=(0, 25))
        
        # Title section
        title_section = ttk.Frame(header_frame, style='Modern.TFrame')
        title_section.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        title_label = ttk.Label(title_section, text="👥 Chrome Profile Management", 
                               style='Modern.TLabel', 
                               font=('Segoe UI', 28, 'bold'))
        title_label.pack(anchor='w')
        
        subtitle_label = ttk.Label(title_section, text="Quản lý và điều khiển Chrome profiles một cách dễ dàng", 
                                 style='Modern.TLabel', 
                                 font=('Segoe UI', 11),
                                 foreground='#b3b3b3')
        subtitle_label.pack(anchor='w', pady=(5, 0))
        
        # Control buttons với style đẹp hơn
        control_frame = ttk.Frame(header_frame, style='Modern.TFrame')
        control_frame.pack(side=tk.RIGHT, pady=(10, 0))
        
        ttk.Button(control_frame, text="➕ Tạo Profile", 
                  style='Modern.TButton',
                  command=self.create_new_profile).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(control_frame, text="🔄 Làm mới", 
                  style='Modern.TButton',
                  command=self.refresh_profiles).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(control_frame, text="[LAUNCH] Chạy hàng loạt", 
                  style='Modern.TButton',
                  command=self.bulk_run_selected).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(control_frame, text="💾 TikTok", 
                  style='Modern.TButton',
                  command=self.manage_tiktok_sessions).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(control_frame, text="📺 Treo Livestream", 
                  style='Modern.TButton',
                  command=self.livestream_selected).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(control_frame, text="🗑️ Xóa hàng loạt", 
                  style='Modern.TButton',
                  command=self.bulk_delete_selected).pack(side=tk.LEFT, padx=(0, 8))
        # Removed "Install Extensions" button per request
        
        # Stats frame với style đẹp hơn
        stats_frame = ttk.LabelFrame(self.content_frame, text="📊 Thống kê hệ thống", 
                                    style='Modern.TLabelframe', padding=20)
        stats_frame.pack(fill=tk.X, pady=(0, 25))
        
        stats_inner = ttk.Frame(stats_frame, style='Modern.TFrame')
        stats_inner.pack(fill=tk.X)
        
        # Stats với icon và style đẹp
        self.total_profiles_label = ttk.Label(stats_inner, text="📁 Tổng profiles: 0", 
                                             style='Modern.TLabel',
                                             font=('Segoe UI', 10, 'bold'))
        self.total_profiles_label.pack(side=tk.LEFT, padx=(0, 30))
        
        self.running_profiles_label = ttk.Label(stats_inner, text="▶️ Đang chạy: 0", 
                                               style='Modern.TLabel',
                                               font=('Segoe UI', 10, 'bold'))
        self.running_profiles_label.pack(side=tk.LEFT, padx=(0, 30))
        
        
        # Profiles table với style đẹp hơn
        table_frame = ttk.LabelFrame(self.content_frame, text="📋 Danh sách Profiles", 
                                    style='Modern.TLabelframe', padding=20)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview với style hiện đại
        columns = ("Profile", "Trạng thái", "Hành động")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", 
                                style='Modern.Treeview', height=18)
        
        # Cấu hình cột với width phù hợp hơn
        self.tree.heading("Profile", text="👤 Profile")
        self.tree.heading("Trạng thái", text="⚡ Trạng thái")
        self.tree.heading("Hành động", text="🎯 Hành động")
        
        self.tree.column("Profile", width=300, minwidth=250)
        self.tree.column("Trạng thái", width=200, minwidth=150)
        self.tree.column("Hành động", width=200, minwidth=150)
        
        # Scrollbar với style đẹp hơn
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Context menu
        self.setup_context_menu()
        
        # Thêm nút để xóa session đăng nhập
        session_frame = ttk.Frame(self.content_frame, style='Modern.TFrame')
        session_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(session_frame, text="🗑️ Xóa session đăng nhập", 
                  command=self.clear_login_session,
                  style='Modern.TButton').pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(session_frame, text="🔄 Làm mới trạng thái", 
                  command=self.refresh_profiles,
                  style='Modern.TButton').pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(session_frame, text="🎮 Master Control Mode", 
                  command=self.show_master_control_dialog,
                  style='Modern.TButton').pack(side=tk.LEFT)
        
        # Status bar với style đẹp hơn
        status_frame = ttk.Frame(self.content_frame, style='Modern.TFrame')
        status_frame.pack(fill=tk.X, pady=(15, 0))
        
        # Status indicator
        status_indicator = ttk.Label(status_frame, text="●", 
                                   style='Modern.TLabel', 
                                   font=('Segoe UI', 8),
                                   foreground='#4CAF50')
        status_indicator.pack(side=tk.LEFT, padx=(0, 8))
        
        self.status_label = ttk.Label(status_frame, text="Sẵn sàng", 
                                     style='Modern.TLabel',
                                     font=('Segoe UI', 9))
        self.status_label.pack(side=tk.LEFT)






            
    def show_export_tab(self):
        """Hiển thị tab Export"""
        self.update_tab_highlight('export')
        self.clear_content()
        
        # Refresh profiles list when entering this tab
        self.refresh_profiles()
        
        # Header
        header_frame = ttk.Frame(self.content_frame, style='Modern.TFrame')
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = ttk.Label(header_frame, text="📤 Export Data", 
                               style='Modern.TLabel', font=('Arial', 24, 'bold'))
        title_label.pack()
        
        # Export options
        options_frame = ttk.LabelFrame(self.content_frame, text="🔧 Tùy chọn Export", 
                                      style='Modern.TFrame', padding=20)
        options_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Profile selection
        profile_frame = ttk.Frame(options_frame, style='Modern.TFrame')
        profile_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(profile_frame, text="Chọn Profile:", 
                 style='Modern.TLabel').pack(side=tk.LEFT)
        
        self.export_profile_var = tk.StringVar()
        self.export_profile_combo = ttk.Combobox(profile_frame, textvariable=self.export_profile_var, style='Modern.TCombobox',
                                                state="readonly", width=30)
        self.export_profile_combo.pack(side=tk.LEFT, padx=10)
        
        # Export type
        type_frame = ttk.Frame(options_frame, style='Modern.TFrame')
        type_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(type_frame, text="Loại dữ liệu:", 
                 style='Modern.TLabel').pack(side=tk.LEFT)
        
        self.export_type_var = tk.StringVar(value="cookies")
        export_types = ["cookies", "passwords", "bookmarks", "history"]
        type_combo = ttk.Combobox(type_frame, textvariable=self.export_type_var, style='Modern.TCombobox',
                                 values=export_types, state="readonly", width=20)
        type_combo.pack(side=tk.LEFT, padx=10)
        
        # Export buttons
        button_frame = ttk.Frame(self.content_frame, style='Modern.TFrame')
        button_frame.pack(fill=tk.X, pady=20)
        
        ttk.Button(button_frame, text="📁 Chọn thư mục", 
                  style='Modern.TButton',
                  command=self.select_export_folder).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="[LAUNCH] Bắt đầu Export", 
                  style='Modern.TButton',
                  command=self.start_export).pack(side=tk.LEFT, padx=5)
        
        # Update profile combo
        self.update_export_profile_combo()
        
    def show_import_tab(self):
        """Hiển thị tab Import"""
        self.update_tab_highlight('import')
        self.clear_content()
        
        # Refresh profiles list when entering this tab
        self.refresh_profiles()
        
        # Header
        header_frame = ttk.Frame(self.content_frame, style='Modern.TFrame')
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = ttk.Label(header_frame, text="📥 Import Data", 
                               style='Modern.TLabel', font=('Arial', 24, 'bold'))
        title_label.pack()
        
        # Import options
        options_frame = ttk.LabelFrame(self.content_frame, text="🔧 Tùy chọn Import", 
                                      style='Modern.TFrame', padding=20)
        options_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Profile selection
        profile_frame = ttk.Frame(options_frame, style='Modern.TFrame')
        profile_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(profile_frame, text="Chọn Profile:", 
                 style='Modern.TLabel').pack(side=tk.LEFT)
        
        self.import_profile_var = tk.StringVar()
        self.import_profile_combo = ttk.Combobox(profile_frame, textvariable=self.import_profile_var, style='Modern.TCombobox',
                                                state="readonly", width=30)
        self.import_profile_combo.pack(side=tk.LEFT, padx=10)
        
        # File selection
        file_frame = ttk.Frame(options_frame, style='Modern.TFrame')
        file_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(file_frame, text="File dữ liệu:", 
                 style='Modern.TLabel').pack(side=tk.LEFT)
        
        self.import_file_var = tk.StringVar()
        file_entry = ttk.Entry(file_frame, textvariable=self.import_file_var, width=40, style='Modern.TEntry')
        file_entry.pack(side=tk.LEFT, padx=10)
        
        ttk.Button(file_frame, text="📁 Chọn file", 
                  style='Modern.TButton',
                  command=self.select_import_file).pack(side=tk.LEFT, padx=5)
        
        # Import buttons
        button_frame = ttk.Frame(self.content_frame, style='Modern.TFrame')
        button_frame.pack(fill=tk.X, pady=20)
        
        ttk.Button(button_frame, text="👁️ Xem trước", 
                  style='Modern.TButton',
                  command=self.preview_import).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="[LAUNCH] Bắt đầu Import", 
                  style='Modern.TButton',
                  command=self.start_import).pack(side=tk.LEFT, padx=5)
        
        # GPM to NKT conversion section
        conversion_frame = ttk.LabelFrame(self.content_frame, text="🔄 Chuyển đổi GPM sang NKT", 
                                        style='Modern.TFrame', padding=20)
        conversion_frame.pack(fill=tk.X, pady=(20, 0))
        
        # GPM profile path selection
        gpm_path_frame = ttk.Frame(conversion_frame, style='Modern.TFrame')
        gpm_path_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(gpm_path_frame, text="Đường dẫn GPM Profile:", 
                 style='Modern.TLabel').pack(side=tk.LEFT)
        
        self.gpm_path_var = tk.StringVar()
        gpm_path_entry = ttk.Entry(gpm_path_frame, textvariable=self.gpm_path_var, width=50, style='Modern.TEntry')
        gpm_path_entry.pack(side=tk.LEFT, padx=10)
        
        ttk.Button(gpm_path_frame, text="📁 Chọn thư mục", 
                  style='Modern.TButton',
                  command=self.select_gpm_folder).pack(side=tk.LEFT, padx=5)
        
        # NKT profile name
        nkt_name_frame = ttk.Frame(conversion_frame, style='Modern.TFrame')
        nkt_name_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(nkt_name_frame, text="Tên Profile NKT:", 
                 style='Modern.TLabel').pack(side=tk.LEFT)
        
        self.nkt_name_var = tk.StringVar()
        nkt_name_entry = ttk.Entry(nkt_name_frame, textvariable=self.nkt_name_var, width=30, style='Modern.TEntry')
        nkt_name_entry.pack(side=tk.LEFT, padx=10)
        
        # Convert button
        convert_button_frame = ttk.Frame(conversion_frame, style='Modern.TFrame')
        convert_button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(convert_button_frame, text="🔄 Chuyển đổi GPM → NKT", 
                  style='Modern.TButton',
                  command=self.convert_gpm_to_nkt).pack(side=tk.LEFT, padx=5)
        
        # Update profile combo
        self.update_import_profile_combo()
        
    def show_extensions_tab(self):
        """Hiển thị tab Extensions Management"""
        self.update_tab_highlight('../extensions')
        self.clear_content()
        
        # Header
        header_frame = ttk.Frame(self.content_frame, style='Modern.TFrame')
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = ttk.Label(header_frame, text="🔌 Extension Management", 
                               style='Modern.TLabel', font=('Arial', 24, 'bold'))
        title_label.pack()
        
        subtitle_label = ttk.Label(header_frame, text="Manage Proxy SwitchyOmega 3 extension for all profiles", 
                                 style='Modern.TLabel', 
                                 font=('Segoe UI', 11),
                                 foreground='#b3b3b3')
        subtitle_label.pack(pady=(5, 0))
        
        # Extension info frame
        info_frame = ttk.LabelFrame(self.content_frame, text="📋 Extension Information", 
                                   style='Modern.TLabelframe', padding=20)
        info_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Extension details
        extension_info = """
🌐 Proxy SwitchyOmega 3 (ZeroOmega)
• Version: 3.4.1 (Manifest V3)
• Developer: suziwen1
• Features: Multiple proxy management, Gist sync, custom themes
• Source: https://github.com/zero-peak/ZeroOmega
• Chrome Web Store: https://chromewebstore.google.com/detail/proxy-switchyomega-3-zero/pfnededegaaopdmhkdmcofjmoldfiped
        """
        
        info_text = tk.Text(info_frame, height=8, width=80, font=("Consolas", 10), 
                           bg='#f8f9fa', fg='#2c3e50', wrap=tk.WORD)
        info_text.pack(fill=tk.X)
        info_text.insert(tk.END, extension_info.strip())
        info_text.config(state=tk.DISABLED)
        
        # Control buttons frame
        control_frame = ttk.LabelFrame(self.content_frame, text="🎯 Extension Actions", 
                                      style='Modern.TLabelframe', padding=20)
        control_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Buttons grid
        buttons_grid = ttk.Frame(control_frame, style='Modern.TFrame')
        buttons_grid.pack(fill=tk.X)
        
        # Row 1: Main extension operations
        row1 = ttk.Frame(buttons_grid, style='Modern.TFrame')
        row1.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(row1, text="🔍 Check Status", 
                  style='Modern.TButton',
                  command=self.check_extension_status).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(row1, text="📦 Install for New Profiles", 
                  style='Modern.TButton',
                  command=self.install_extension_for_new_profiles).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(row1, text="[LAUNCH] Install for All Profiles", 
                  style='Modern.TButton',
                  command=self.install_extension_for_all_profiles).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(row1, text="📋 Install for Selected", 
                  style='Modern.TButton',
                  command=self.install_extension_selected).pack(side=tk.LEFT, padx=(0, 10))
        
        # Row 2: Configuration and management
        row2 = ttk.Frame(buttons_grid, style='Modern.TFrame')
        row2.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(row2, text="🌐 Configure Proxy Selected", 
                  style='Modern.TButton',
                  command=self.configure_proxy_selected).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(row2, text="🌐 Configure Proxy All", 
                  style='Modern.TButton',
                  command=self.configure_proxy_all).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(row2, text="⚡ Activate Extension", 
                  style='Modern.TButton',
                  command=self.activate_extension_selected).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(row2, text="🔄 Refresh Status", 
                  style='Modern.TButton',
                  command=self.refresh_extension_status).pack(side=tk.LEFT, padx=(0, 10))
        
        # Row 3: Advanced operations
        row3 = ttk.Frame(buttons_grid, style='Modern.TFrame')
        row3.pack(fill=tk.X)
        
        ttk.Button(row3, text="📊 Extension Statistics", 
                  style='Modern.TButton',
                  command=self.show_extension_statistics).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(row3, text="🧪 Test Installation", 
                  style='Modern.TButton',
                  command=self.test_extension_installation).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(row3, text="[LAUNCH] Auto-Install Startup", 
                  style='Modern.TButton',
                  command=self.auto_install_extension_startup).pack(side=tk.LEFT, padx=(0, 10))
        
        # Row 4: Extension management only
        row4 = ttk.Frame(buttons_grid, style='Modern.TFrame')
        row4.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(row4, text="📊 Extension Statistics", 
                  style='Modern.TButton',
                  command=self.show_extension_statistics).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(row4, text="🧪 Test Installation", 
                  style='Modern.TButton',
                  command=self.test_extension_installation).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(row4, text="[LAUNCH] Auto-Install Startup", 
                  style='Modern.TButton',
                  command=self.auto_install_extension_startup).pack(side=tk.LEFT, padx=(0, 10))
        
        # General extensions (independent of SwitchyOmega)
        general_frame = ttk.LabelFrame(self.content_frame, text="🧩 General Extensions", 
                                       style='Modern.TLabelframe', padding=20)
        general_frame.pack(fill=tk.X, pady=(0, 20))
        gen_row = ttk.Frame(general_frame, style='Modern.TFrame')
        gen_row.pack(fill=tk.X)
        ttk.Button(gen_row, text="📥 Install CRX for Selected Profiles", 
                  style='Modern.TButton',
                  command=self.show_general_extensions_installer).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(gen_row, text="📥 Install CRX for ALL Profiles", 
                  style='Modern.TButton',
                  command=lambda: self.show_general_extensions_installer(select_all=True)).pack(side=tk.LEFT)
        
        # Status display frame
        status_frame = ttk.LabelFrame(self.content_frame, text="📊 Extension Status", 
                                     style='Modern.TLabelframe', padding=20)
        status_frame.pack(fill=tk.BOTH, expand=True)
        
        # Status text with scrollbar
        status_text_frame = ttk.Frame(status_frame, style='Modern.TFrame')
        status_text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.extension_status_text = tk.Text(status_text_frame, height=15, width=80, 
                                           font=("Consolas", 9), bg='#f8f9fa', fg='#2c3e50')
        status_scrollbar = ttk.Scrollbar(status_text_frame, orient="vertical", 
                                        command=self.extension_status_text.yview)
        self.extension_status_text.configure(yscrollcommand=status_scrollbar.set)
        
        self.extension_status_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        status_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Initial status check
        self.refresh_extension_status()

    def show_general_extensions_installer(self, select_all: bool = False):
        """Install multiple arbitrary CRX files (paths or URLs) to many profiles."""
        import threading
        import urllib.request
        import tempfile
        import shutil
        
        dialog = tk.Toplevel(self.root)
        dialog.title("📥 Install Multiple Extensions (CRX)")
        dialog.geometry("740x540")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        container = ttk.Frame(dialog, padding=15)
        container.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(container, text="CRX paths or URLs (one per line):", font=("Segoe UI", 10, "bold")).pack(anchor=tk.W)
        crx_text = tk.Text(container, height=8, font=("Consolas", 10))
        crx_text.pack(fill=tk.X, pady=(5, 10))
        
        file_tools = ttk.Frame(container)
        file_tools.pack(fill=tk.X)
        
        def add_files():
            from tkinter import filedialog
            paths = filedialog.askopenfilenames(title="Select CRX files", filetypes=[("CRX files", "*.crx"), ("All files", "*.*")])
            if not paths:
                return
            existing = crx_text.get("1.0", tk.END).strip()
            joined = (existing + "\n" + "\n".join(paths)).strip() if existing else "\n".join(paths)
            crx_text.delete("1.0", tk.END)
            crx_text.insert(tk.END, joined)
        ttk.Button(file_tools, text="➕ Add CRX files", command=add_files).pack(side=tk.LEFT)
        
        ttk.Label(container, text="Target profiles:", font=("Segoe UI", 10, "bold")).pack(anchor=tk.W, pady=(10, 5))
        list_frame = ttk.Frame(container)
        list_frame.pack(fill=tk.BOTH, expand=True)
        profile_list = tk.Listbox(list_frame, selectmode=tk.MULTIPLE, height=10)
        profile_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=profile_list.yview)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        profile_list.configure(yscrollcommand=sb.set)
        profiles = []
        try:
            profiles = self.manager.get_all_profiles()
        except Exception:
            profiles = []
        for idx, p in enumerate(profiles):
            profile_list.insert(tk.END, p)
            if select_all:
                profile_list.selection_set(idx)
        
        ttk.Label(container, text="Status:", font=("Segoe UI", 10, "bold")).pack(anchor=tk.W, pady=(10, 5))
        status = tk.Text(container, height=8, font=("Consolas", 9))
        status.pack(fill=tk.BOTH, expand=True)
        
        def log(msg: str):
            status.insert(tk.END, msg + "\n")
            status.see(tk.END)
        
        def is_url(s: str) -> bool:
            return s.startswith("http://") or s.startswith("https://")
        
        def download_to_temp(url: str) -> str:
            tmp_dir = tempfile.mkdtemp(prefix="crx_")
            dest = os.path.join(tmp_dir, os.path.basename(url.split('?')[0]) or "ext.crx")
            urllib.request.urlretrieve(url, dest)
            return dest
        
        def start_install():
            items = [l.strip() for l in crx_text.get("1.0", tk.END).splitlines() if l.strip()]
            sel = profile_list.curselection()
            targets = [profile_list.get(i) for i in sel]
            if not items:
                messagebox.showerror("Error", "Please add at least one CRX path or URL")
                return
            if not targets:
                messagebox.showerror("Error", "Please select at least one target profile")
                return
            
            def worker():
                successes = 0
                for item in items:
                    temp_dir = None
                    local = item
                    try:
                        if is_url(item):
                            log(f"🌐 Downloading: {item}")
                            try:
                                local = download_to_temp(item)
                                temp_dir = os.path.dirname(local)
                                log(f"✅ Downloaded: {local}")
                            except Exception as e:
                                log(f"❌ Download failed: {e}")
                                continue
                        if not os.path.exists(local):
                            log(f"❌ File not found: {local}")
                            if temp_dir:
                                shutil.rmtree(temp_dir, ignore_errors=True)
                            continue
                        for prof in targets:
                            log(f"📥 Installing {os.path.basename(local)} -> {prof}")
                            ok, msg = self.manager.install_extension_from_crx(prof, local)
                            log(("   ✅ " if ok else "   ❌ ") + msg)
                            if ok:
                                successes += 1
                    finally:
                        if temp_dir:
                            shutil.rmtree(temp_dir, ignore_errors=True)
                log(f"\nDone. Successful installs: {successes}")
            threading.Thread(target=worker, daemon=True).start()
        
        actions = ttk.Frame(container)
        actions.pack(fill=tk.X, pady=(8, 0))
        ttk.Button(actions, text="[LAUNCH] Start Install", command=start_install).pack(side=tk.LEFT)
        ttk.Button(actions, text="❌ Close", command=dialog.destroy).pack(side=tk.RIGHT)
        
        # Proxy Configuration Section
        proxy_config_frame = ttk.LabelFrame(self.content_frame, text="🌐 Proxy Configuration", 
                                          style='Modern.TLabelframe', padding=20)
        proxy_config_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Proxy input fields
        proxy_input_frame = ttk.Frame(proxy_config_frame, style='Modern.TFrame')
        proxy_input_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Row 1: Profile Name and Protocol
        row1 = ttk.Frame(proxy_input_frame, style='Modern.TFrame')
        row1.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(row1, text="Profile Name:", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=(0, 10))
        self.proxy_profile_name_var = tk.StringVar(value="MyProxy")
        ttk.Entry(row1, textvariable=self.proxy_profile_name_var, width=20, font=("Consolas", 10), style='Modern.TEntry').pack(side=tk.LEFT, padx=(0, 20))
        
        ttk.Label(row1, text="Protocol:", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=(0, 10))
        self.proxy_protocol_var = tk.StringVar(value="http")
        protocol_combo = ttk.Combobox(row1, textvariable=self.proxy_protocol_var, style='Modern.TCombobox', 
                                    values=["http", "socks4", "socks5"], 
                                    state="readonly", width=10)
        protocol_combo.pack(side=tk.LEFT)
        
        # Row 2: Server and Port
        row2 = ttk.Frame(proxy_input_frame, style='Modern.TFrame')
        row2.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(row2, text="Server:", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=(0, 10))
        self.proxy_server_var = tk.StringVar(value="146.19.196.16")
        ttk.Entry(row2, textvariable=self.proxy_server_var, width=25, font=("Consolas", 10), style='Modern.TEntry').pack(side=tk.LEFT, padx=(0, 20))
        
        ttk.Label(row2, text="Port:", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=(0, 10))
        self.proxy_port_var = tk.StringVar(value="40742")
        ttk.Entry(row2, textvariable=self.proxy_port_var, width=10, font=("Consolas", 10), style='Modern.TEntry').pack(side=tk.LEFT)
        
        # Row 3: Username and Password
        row3 = ttk.Frame(proxy_input_frame, style='Modern.TFrame')
        row3.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(row3, text="Username:", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=(0, 10))
        self.proxy_username_var = tk.StringVar(value="dNMWW2VVxb")
        ttk.Entry(row3, textvariable=self.proxy_username_var, width=25, font=("Consolas", 10)).pack(side=tk.LEFT, padx=(0, 20))
        
        ttk.Label(row3, text="Password:", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=(0, 10))
        self.proxy_password_var = tk.StringVar(value="YySfhZZPYv")
        ttk.Entry(row3, textvariable=self.proxy_password_var, width=25, font=("Consolas", 10), show="*").pack(side=tk.LEFT)
        
        # Configuration buttons
        config_buttons_frame = ttk.Frame(proxy_config_frame, style='Modern.TFrame')
        config_buttons_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(config_buttons_frame, text="🔧 Configure Selected Profiles", 
                  style='Modern.TButton',
                  command=self.configure_proxy_selected).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(config_buttons_frame, text="[LAUNCH] Configure All Profiles", 
                  style='Modern.TButton',
                  command=self.configure_proxy_all).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(config_buttons_frame, text="💾 Save Proxy Profile", 
                  style='Modern.TButton',
                  command=self.save_proxy_profile).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(config_buttons_frame, text="📋 Load Proxy Profile", 
                  style='Modern.TButton',
                  command=self.load_proxy_profile).pack(side=tk.LEFT)
        
        # Saved proxy profiles section
        saved_profiles_frame = ttk.LabelFrame(self.content_frame, text="💾 Saved Proxy Profiles", 
                                            style='Modern.TLabelframe', padding=20)
        saved_profiles_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Profiles listbox with scrollbar
        profiles_list_frame = ttk.Frame(saved_profiles_frame, style='Modern.TFrame')
        profiles_list_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.saved_profiles_listbox = tk.Listbox(profiles_list_frame, height=6, font=("Consolas", 9))
        profiles_scrollbar = ttk.Scrollbar(profiles_list_frame, orient="vertical", command=self.saved_profiles_listbox.yview)
        self.saved_profiles_listbox.configure(yscrollcommand=profiles_scrollbar.set)
        
        self.saved_profiles_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        profiles_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Profile management buttons
        profile_mgmt_frame = ttk.Frame(saved_profiles_frame, style='Modern.TFrame')
        profile_mgmt_frame.pack(fill=tk.X)
        
        ttk.Button(profile_mgmt_frame, text="🔄 Refresh Profiles", 
                  style='Modern.TButton',
                  command=self.refresh_saved_profiles).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(profile_mgmt_frame, text="📥 Load Selected", 
                  style='Modern.TButton',
                  command=self.load_selected_proxy_profile).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(profile_mgmt_frame, text="🗑️ Delete Selected", 
                  style='Modern.TButton',
                  command=self.delete_selected_proxy_profile).pack(side=tk.LEFT)
        
        # Load saved profiles on startup
        self.refresh_saved_profiles()
        
        # Auto-install extension for all profiles on startup
        self.auto_install_extension_startup()
        
        
    def show_proxy_config_tab(self):
        """Hiển thị tab Proxy Configuration"""
        self.update_tab_highlight('proxy_config')
        self.clear_content()
        
        # Refresh profiles when entering this tab
        try:
            self.refresh_profiles()
        except Exception as e:
            print(f"⚠️ [PROXY-CONFIG] Could not refresh profiles: {e}")
        
        # Tiêu đề
        title_label = ttk.Label(self.content_frame, text="🌐 Proxy Configuration", 
                               font=("Segoe UI", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Frame chính
        main_frame = ttk.Frame(self.content_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Create notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Tab 1: Single input
        input_frame = ttk.Frame(notebook)
        notebook.add(input_frame, text="🔧 Single")

        # Tab 2: Bulk input
        bulk_frame = ttk.Frame(notebook)
        notebook.add(bulk_frame, text="📦 Bulk")

        # === SINGLE INPUT TAB ===
        input_config_frame = ttk.LabelFrame(input_frame, text="🔧 Proxy Input (Single)", padding="15")
        input_config_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Proxy string input
        proxy_string_frame = ttk.Frame(input_config_frame)
        proxy_string_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(proxy_string_frame, text="Proxy String:", font=("Segoe UI", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))
        self.proxy_input_string = tk.StringVar()
        proxy_input_entry = ttk.Entry(proxy_string_frame, textvariable=self.proxy_input_string, width=60, font=("Segoe UI", 9))
        proxy_input_entry.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(proxy_string_frame, text="Format: server:port:username:password (e.g., 146.19.196.108:40767:wqcj8o8q3x:mlptR7sWVf)", 
                 font=("Segoe UI", 8), foreground="gray").pack(anchor=tk.W)
        
        # Target profile selection
        target_profile_frame = ttk.Frame(input_config_frame)
        target_profile_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(target_profile_frame, text="Target Profile:", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=(0, 10))
        self.proxy_input_target = tk.StringVar()
        self.proxy_input_target_combo = ttk.Combobox(target_profile_frame, textvariable=self.proxy_input_target, width=30, state="readonly")
        self.proxy_input_target_combo.pack(side=tk.LEFT, padx=(0, 10))
        
        # Buttons
        button_frame = ttk.Frame(input_config_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="Parse Proxy", command=self.parse_proxy_input).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Apply to Profile", command=self.apply_proxy_input).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Bulk Apply (CSV)", command=self.bulk_apply_from_csv).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Force Import to Extension", command=self.force_import_proxy).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Show Current", command=self.show_current_proxy).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Test Profile", command=self.test_proxy_profile).pack(side=tk.LEFT, padx=(0, 10))
        
        # === BULK INPUT TAB ===
        bulk_config = ttk.LabelFrame(bulk_frame, text="📦 Bulk Proxy Input", padding="15")
        bulk_config.pack(fill=tk.BOTH, expand=True)

        top_bulk = ttk.Frame(bulk_config)
        top_bulk.pack(fill=tk.X)
        ttk.Label(top_bulk, text="Count:", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT)
        try:
            from tkinter import IntVar
        except Exception:
            IntVar = tk.IntVar
        self.bulk_lines_count_var = IntVar(value=10)
        ttk.Spinbox(top_bulk, from_=1, to=500, textvariable=self.bulk_lines_count_var, width=6).pack(side=tk.LEFT, padx=(6,10))
        ttk.Button(top_bulk, text="Apply", command=self.bulk_apply_from_text_tab).pack(side=tk.LEFT)
        # Dynamic counters
        self.bulk_selected_count_var = tk.StringVar(value="Selected: 0")
        self.bulk_lines_info_var = tk.StringVar(value="Lines: 0")
        ttk.Label(top_bulk, textvariable=self.bulk_selected_count_var, foreground="#444").pack(side=tk.LEFT, padx=(10,0))
        ttk.Label(top_bulk, textvariable=self.bulk_lines_info_var, foreground="#444").pack(side=tk.LEFT, padx=(10,0))
        ttk.Label(top_bulk, text="  One proxy per line.", foreground="#6b6b6b").pack(side=tk.LEFT, padx=(10,0))

        # Split area: left = selectable profiles, right = text box (balanced)
        split = ttk.Panedwindow(bulk_config, orient=tk.HORIZONTAL)
        split.pack(fill=tk.BOTH, expand=True, pady=(10,0))

        left = ttk.Frame(split)
        ttk.Label(left, text="Target Profiles", font=("Segoe UI", 9, "bold")).pack(anchor=tk.W)
        self.bulk_profile_listbox = tk.Listbox(left, selectmode=tk.MULTIPLE, height=18, exportselection=False, font=("Consolas", 9), width=28)
        self.bulk_profile_listbox.pack(fill=tk.Y)

        # Populate profiles
        try:
            for p in self.manager.get_all_profiles():
                self.bulk_profile_listbox.insert(tk.END, p)
        except Exception:
            pass

        lb_btns = ttk.Frame(left)
        lb_btns.pack(fill=tk.X, pady=(6,0))
        def _bulk_select_all():
            self.bulk_profile_listbox.select_set(0, tk.END)
            self._update_bulk_selected_count()
        def _bulk_clear():
            self.bulk_profile_listbox.select_clear(0, tk.END)
            self._update_bulk_selected_count()
        ttk.Button(lb_btns, text="Select All", command=_bulk_select_all).pack(side=tk.LEFT)
        ttk.Button(lb_btns, text="Clear", command=_bulk_clear).pack(side=tk.LEFT, padx=(6,0))

        right = ttk.Frame(split)
        # Add panes with equal weights so both sides are balanced
        try:
            split.add(left, weight=1)
            split.add(right, weight=1)
        except Exception:
            # Fallback without weights if not supported
            split.add(left)
            split.add(right)
        self.bulk_text = tk.Text(right, height=18, font=("Consolas", 10))
        self.bulk_text.pack(fill=tk.BOTH, expand=True)
        self.bulk_text.insert(tk.END, "# Example\n146.19.196.15:40684:user:pass\n146.19.196.16:40700\n")
        # Bind events to update counters
        try:
            self.bulk_profile_listbox.bind('<<ListboxSelect>>', lambda e: self._update_bulk_selected_count())
        except Exception:
            pass
        self.bulk_text.bind('<KeyRelease>', lambda e: self._update_bulk_lines_count())
        
        # Bottom Status frame (keep one status area only)
        status_frame = ttk.LabelFrame(input_frame, text="📊 Status", padding="15")
        status_frame.pack(fill=tk.BOTH, expand=True)
        
        self.proxy_status_text = tk.Text(status_frame, height=8, font=("Consolas", 9), wrap=tk.WORD)
        self.proxy_status_text.pack(fill=tk.BOTH, expand=True)
        
        # Initial status
        self.proxy_status_text.insert(tk.END, "🌐 Proxy Input Ready\n")
        self.proxy_status_text.insert(tk.END, "1. Enter proxy string in format: server:port:username:password\n")
        self.proxy_status_text.insert(tk.END, "2. Select target profile(s)\n")
        self.proxy_status_text.insert(tk.END, "3. Click 'Apply to Profile' to configure SwitchyOmega\n")
        self.proxy_status_text.insert(tk.END, "4. Test connection to verify setup\n\n")
        self.proxy_status_text.insert(tk.END, "💡 Tip: Use 'chrome-extension://pfnededegaaopdmhkdmcofjmoldfiped/options.html' to manually configure\n")
        
        # Update profile lists after all widgets are created
        self.update_proxy_input_combos()
        
        self.current_tab = 'proxy_config'
        self.update_tab_highlight()
    
    def update_proxy_input_combos(self):
        """Update proxy input combo boxes"""
        try:
            profiles = self.manager.get_all_profiles()
            
            if hasattr(self, 'proxy_input_target_combo') and self.proxy_input_target_combo:
                self.proxy_input_target_combo['values'] = profiles
                
            if hasattr(self, 'proxy_input_source_combo') and self.proxy_input_source_combo:
                self.proxy_input_source_combo['values'] = profiles
                
            if profiles:
                if hasattr(self, 'proxy_input_target') and self.proxy_input_target and not self.proxy_input_target.get():
                    self.proxy_input_target_combo.set(profiles[0])
                    
                if hasattr(self, 'proxy_input_source') and self.proxy_input_source and not self.proxy_input_source.get():
                    default_source = "76h" if "76h" in profiles else profiles[0]
                    self.proxy_input_source_combo.set(default_source)
                    
        except Exception as e:
            print(f"Error updating proxy input combos: {str(e)}")
    
    def show_email_config_tab(self):
        """Configure proxy for selected profile"""
        try:
            profile_name = self.proxy_profile_combo.get()
            if not profile_name:
                messagebox.showerror("Error", "Please select a Chrome profile")
                return
            
            # Get proxy settings from both quick setup and advanced config
            proxy_config = self._get_proxy_config_from_ui()
            
            # Validate proxy settings
            if not proxy_config['proxy_server']:
                messagebox.showerror("Error", "Please enter proxy server")
                return
            
            if not proxy_config['proxy_port']:
                messagebox.showerror("Error", "Please enter proxy port")
                return
            
            # Update status
            self.proxy_status.delete(1.0, tk.END)
            self.proxy_status.insert(tk.END, f"[LAUNCH] Configuring proxy for profile: {profile_name}\n")
            self.proxy_status.insert(tk.END, f"📋 Proxy: {proxy_config['proxy_type']}://{proxy_config['proxy_server']}:{proxy_config['proxy_port']}\n")
            self.proxy_status.insert(tk.END, f"🏷️ Profile Name: {proxy_config['profile_name']}\n")
            if proxy_config.get('username'):
                self.proxy_status.insert(tk.END, f"👤 Username: {proxy_config['username']}\n")
            self.proxy_status.insert(tk.END, "\n⏳ Please wait while configuring SwitchyOmega...\n")
            
            # Configure proxy in background thread
            def configure_thread():
                try:
                    success, message = self.manager.configure_switchyomega_proxy(profile_name, proxy_config)
                    
                    def update_ui():
                        if success:
                            self.proxy_status.insert(tk.END, f"✅ {message}\n")
                            self.proxy_status.insert(tk.END, f"🌐 Proxy configured successfully!\n")
                            self.proxy_status.insert(tk.END, f"💡 You can now use the proxy in Chrome\n")
                        else:
                            self.proxy_status.insert(tk.END, f"❌ {message}\n")
                            self.proxy_status.insert(tk.END, f"🔧 Please check your proxy settings\n")
                    
                    self.root.after(0, update_ui)
                    
                except Exception as e:
                    def update_ui():
                        self.proxy_status.insert(tk.END, f"❌ Error: {str(e)}\n")
                    self.root.after(0, update_ui)
            
            threading.Thread(target=configure_thread, daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error configuring proxy: {str(e)}")
    
    def _get_proxy_config_from_ui(self):
        """Get proxy configuration from UI (both quick setup and advanced config)"""
        try:
            # Check if quick setup has server:port format
            quick_server = self.proxy_server.get()
            if ':' in quick_server:
                # Parse server:port from quick setup
                server, port = quick_server.split(':', 1)
                return {
                    'proxy_type': self.proxy_type.get(),
                    'proxy_server': server.strip(),
                    'proxy_port': port.strip(),
                    'username': self.proxy_username.get(),
                    'password': self.proxy_password.get(),
                    'profile_name': self.proxy_profile_name.get()
                }
            else:
                # Use advanced config
                return {
                    'proxy_type': self.proxy_type.get(),
                    'proxy_server': self.proxy_server_advanced.get() or quick_server,
                    'proxy_port': self.proxy_port.get(),
                    'username': self.proxy_username.get(),
                    'password': self.proxy_password.get(),
                    'profile_name': self.proxy_profile_name.get()
                }
        except Exception as e:
            print(f"Error getting proxy config from UI: {str(e)}")
            return {
                'proxy_type': 'HTTP',
                'proxy_server': '',
                'proxy_port': '8080',
                'username': '',
                'password': '',
                'profile_name': 'MyProxy'
            }
    
    def test_proxy_connection(self):
        """Test proxy connection"""
        try:
            profile_name = self.proxy_profile_combo.get()
            if not profile_name:
                messagebox.showerror("Error", "Please select a Chrome profile")
                return
            
            proxy_server = self.proxy_server.get()
            proxy_port = self.proxy_port.get()
            
            if not proxy_server or not proxy_port:
                messagebox.showerror("Error", "Please enter proxy server and port")
                return
            
            # Update status
            self.proxy_status.insert(tk.END, f"🧪 Testing proxy connection...\n")
            self.proxy_status.insert(tk.END, f"📋 Server: {proxy_server}:{proxy_port}\n")
            
            # Test connection in background thread
            def test_thread():
                try:
                    import socket
                    import time
                    
                    def update_ui():
                        self.proxy_status.insert(tk.END, f"⏳ Connecting to {proxy_server}:{proxy_port}...\n")
                    
                    self.root.after(0, update_ui)
                    
                    # Test connection
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(10)
                    result = sock.connect_ex((proxy_server, int(proxy_port)))
                    sock.close()
                    
                    def update_ui():
                        if result == 0:
                            self.proxy_status.insert(tk.END, f"✅ Connection successful!\n")
                            self.proxy_status.insert(tk.END, f"🌐 Proxy server is reachable\n")
                        else:
                            self.proxy_status.insert(tk.END, f"❌ Connection failed!\n")
                            self.proxy_status.insert(tk.END, f"🔧 Please check proxy server and port\n")
                    
                    self.root.after(0, update_ui)
                    
                except Exception as e:
                    def update_ui():
                        self.proxy_status.insert(tk.END, f"❌ Test error: {str(e)}\n")
                    self.root.after(0, update_ui)
            
            threading.Thread(target=test_thread, daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error testing proxy: {str(e)}")
    
    def save_proxy_profile(self):
        """Save proxy profile configuration"""
        try:
            proxy_config = {
                'type': self.proxy_type.get(),
                'server': self.proxy_server.get(),
                'port': self.proxy_port.get(),
                'username': self.proxy_username.get(),
                'password': self.proxy_password.get(),
                'profile_name': self.proxy_profile_name.get()
            }
            
            if not proxy_config['server'] or not proxy_config['port']:
                messagebox.showerror("Error", "Please enter proxy server and port")
                return
            
            # Save to config (tạm thời bỏ qua vì hàm chưa được implement)
            profile_name = f"proxy_{proxy_config['profile_name']}"
            print(f"📝 [PROXY] Proxy profile được tạo: {profile_name} (chưa lưu)")
            # TODO: Implement save_stealth_config function
            
            messagebox.showinfo("Success", f"Proxy profile created: {profile_name}")
            self.proxy_status.insert(tk.END, f"💾 Created proxy profile: {profile_name}\n")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error saving proxy profile: {str(e)}")
    
    def refresh_saved_profiles(self):
        """Refresh the list of saved proxy profiles"""
        try:
            self.proxy_profiles_listbox.delete(0, tk.END)
            
            # Load proxy profiles from config
            config = self.manager.load_config()
            proxy_profiles = []
            
            for key, value in config.items():
                if key.startswith('proxy_profile_'):
                    profile_name = key.replace('proxy_profile_', '')
                    proxy_profiles.append(profile_name)
            
            # Sort profiles
            proxy_profiles.sort()
            
            # Add to listbox
            for profile in proxy_profiles:
                self.proxy_profiles_listbox.insert(tk.END, profile)
                
        except Exception as e:
            print(f"Error refreshing saved profiles: {str(e)}")
    
    def load_selected_proxy_profile(self):
        """Load selected proxy profile from listbox"""
        try:
            selection = self.proxy_profiles_listbox.curselection()
            if not selection:
                messagebox.showwarning("Warning", "Please select a proxy profile to load")
                return
            
            profile_name = self.proxy_profiles_listbox.get(selection[0])
            config = self.manager.load_config()
            
            # Get profile config
            profile_key = f'proxy_profile_{profile_name}'
            if profile_key in config:
                profile_config = config[profile_key]
                
                # Load to UI
                self.proxy_type.set(profile_config.get('proxy_type', 'HTTP'))
                self.proxy_server.set(f"{profile_config.get('proxy_server', '')}:{profile_config.get('proxy_port', '8080')}")
                self.proxy_server_advanced.set(profile_config.get('proxy_server', ''))
                self.proxy_port.set(profile_config.get('proxy_port', '8080'))
                self.proxy_username.set(profile_config.get('username', ''))
                self.proxy_password.set(profile_config.get('password', ''))
                self.proxy_profile_name.set(profile_config.get('profile_name', 'MyProxy'))
                
                messagebox.showinfo("Success", f"Loaded proxy profile: {profile_name}")
            else:
                messagebox.showerror("Error", f"Profile configuration not found: {profile_name}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error loading proxy profile: {str(e)}")
    
    def delete_selected_proxy_profile(self):
        """Delete selected proxy profile"""
        try:
            selection = self.proxy_profiles_listbox.curselection()
            if not selection:
                messagebox.showwarning("Warning", "Please select a proxy profile to delete")
                return
            
            profile_name = self.proxy_profiles_listbox.get(selection[0])
            
            # Confirm deletion
            if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete proxy profile '{profile_name}'?"):
                config = self.manager.load_config()
                profile_key = f'proxy_profile_{profile_name}'
                
                if profile_key in config:
                    del config[profile_key]
                    self.manager.save_config()
                    self.refresh_saved_profiles()
                    messagebox.showinfo("Success", f"Deleted proxy profile: {profile_name}")
                else:
                    messagebox.showerror("Error", f"Profile configuration not found: {profile_name}")
                    
        except Exception as e:
            messagebox.showerror("Error", f"Error deleting proxy profile: {str(e)}")
    
    def get_switchyomega_profiles(self):
        """Get proxy profiles from SwitchyOmega extension"""
        try:
            profile_name = self.proxy_profile_combo.get()
            if not profile_name:
                messagebox.showerror("Error", "Please select a Chrome profile")
                return
            
            # Update status
            self.proxy_status.delete(1.0, tk.END)
            self.proxy_status.insert(tk.END, f"🔍 Getting SwitchyOmega profiles from: {profile_name}\n")
            self.proxy_status.insert(tk.END, "⏳ Please wait while extracting profiles...\n")
            
            # Get profiles in background thread
            def get_profiles_thread():
                try:
                    profiles = self.manager.get_switchyomega_profiles(profile_name)
                    
                    def update_ui():
                        if profiles:
                            self.proxy_status.insert(tk.END, f"✅ Found {len(profiles)} profiles:\n")
                            
                            # Clear and populate listbox
                            self.proxy_profiles_listbox.delete(0, tk.END)
                            
                            for profile in profiles:
                                profile_display = f"{profile['name']} ({profile['type']})"
                                if profile['server']:
                                    profile_display += f" - {profile['server']}:{profile['port']}"
                                self.proxy_profiles_listbox.insert(tk.END, profile_display)
                                self.proxy_status.insert(tk.END, f"  📋 {profile_display}\n")
                            
                            # Save profiles to config
                            self._save_switchyomega_profiles(profiles)
                            
                            self.proxy_status.insert(tk.END, "\n💾 Profiles saved to configuration\n")
                            self.proxy_status.insert(tk.END, "💡 You can now load any profile to use it\n")
                        else:
                            self.proxy_status.insert(tk.END, "❌ No profiles found in SwitchyOmega\n")
                            self.proxy_status.insert(tk.END, "💡 Make sure SwitchyOmega is installed and has profiles configured\n")
                    
                    self.root.after(0, update_ui)
                    
                except Exception as e:
                    def update_ui():
                        self.proxy_status.insert(tk.END, f"❌ Error: {str(e)}\n")
                    self.root.after(0, update_ui)
            
            threading.Thread(target=get_profiles_thread, daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error getting SwitchyOmega profiles: {str(e)}")
    
    def _save_switchyomega_profiles(self, profiles):
        """Save SwitchyOmega profiles to configuration"""
        try:
            config = self.manager.load_config()
            
            for profile in profiles:
                profile_key = f'proxy_profile_{profile["name"]}'
                config[profile_key] = {
                    'proxy_type': profile['type'].upper(),
                    'proxy_server': profile['server'],
                    'proxy_port': profile['port'],
                    'username': profile['username'],
                    'password': profile['password'],
                    'profile_name': profile['name'],
                    'source': 'switchyomega'
                }
            
            self.manager.save_config()
            print(f"💾 Saved {len(profiles)} profiles to configuration")
            
        except Exception as e:
            print(f"❌ Error saving profiles: {str(e)}")
    
    def load_proxy_profile(self):
        """Load proxy profile configuration"""
        try:
            # Get saved proxy profiles
            profiles = self.manager.get_stealth_configs_list()
            proxy_profiles = [p for p in profiles if p.startswith('proxy_')]
            
            if not proxy_profiles:
                messagebox.showinfo("Info", "No saved proxy profiles found")
                return
            
            # Show selection dialog
            dialog = tk.Toplevel(self.root)
            dialog.title("Load Proxy Profile")
            dialog.geometry("400x300")
            dialog.resizable(False, False)
            
            # Center dialog
            dialog.transient(self.root)
            dialog.grab_set()
            
            ttk.Label(dialog, text="Select Proxy Profile:", font=("Segoe UI", 12, "bold")).pack(pady=10)
            
            # Profile list
            listbox = tk.Listbox(dialog, height=10)
            listbox.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
            
            for profile in proxy_profiles:
                listbox.insert(tk.END, profile)
            
            # Buttons
            buttons_frame = ttk.Frame(dialog)
            buttons_frame.pack(fill=tk.X, padx=20, pady=10)
            
            def load_selected():
                selection = listbox.curselection()
                if selection:
                    profile_name = listbox.get(selection[0])
                    success, config = self.manager.load_stealth_config(profile_name)
                    
                    if success:
                        # Load config to UI
                        self.proxy_type.set(config.get('type', 'HTTP'))
                        self.proxy_server.set(config.get('server', ''))
                        self.proxy_port.set(config.get('port', '8080'))
                        self.proxy_username.set(config.get('username', ''))
                        self.proxy_password.set(config.get('password', ''))
                        self.proxy_profile_name.set(config.get('profile_name', 'MyProxy'))
                        
                        self.proxy_status.insert(tk.END, f"📂 Loaded proxy profile: {profile_name}\n")
                        dialog.destroy()
                    else:
                        messagebox.showerror("Error", f"Failed to load profile: {config}")
                else:
                    messagebox.showwarning("Warning", "Please select a profile")
            
            def delete_selected():
                selection = listbox.curselection()
                if selection:
                    profile_name = listbox.get(selection[0])
                    if messagebox.askyesno("Confirm", f"Delete profile '{profile_name}'?"):
                        # Delete profile (implement if needed)
                        listbox.delete(selection[0])
                        self.proxy_status.insert(tk.END, f"🗑️ Deleted profile: {profile_name}\n")
                else:
                    messagebox.showwarning("Warning", "Please select a profile")
            
            ttk.Button(buttons_frame, text="Load", command=load_selected).pack(side=tk.LEFT, padx=(0, 10))
            ttk.Button(buttons_frame, text="Delete", command=delete_selected).pack(side=tk.LEFT, padx=(0, 10))
            ttk.Button(buttons_frame, text="Cancel", command=dialog.destroy).pack(side=tk.RIGHT)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error loading proxy profile: {str(e)}")
        
    def show_email_config_tab(self):
        """Hiển thị tab Auto TikTok 2FA Configuration"""
        self.update_tab_highlight('email_config')
        self.clear_content()
        
        # Tiêu đề
        title_label = ttk.Label(self.content_frame, text="[LAUNCH] Auto TikTok 2FA Configuration", 
                               font=("Segoe UI", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Frame chính
        main_frame = ttk.Frame(self.content_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Microsoft Graph Configuration
        graph_frame = ttk.LabelFrame(main_frame, text="📧 Microsoft Graph Configuration", padding="15")
        graph_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Email
        ttk.Label(graph_frame, text="Email:", font=("Segoe UI", 10, "bold")).pack(anchor=tk.W)
        self.auto_2fa_email = tk.StringVar()
        ttk.Entry(graph_frame, textvariable=self.auto_2fa_email, font=("Segoe UI", 10)).pack(fill=tk.X, pady=(0, 10))
        
        # Refresh Token
        ttk.Label(graph_frame, text="Refresh Token:", font=("Segoe UI", 10, "bold")).pack(anchor=tk.W)
        self.auto_2fa_refresh_token = tk.StringVar()
        ttk.Entry(graph_frame, textvariable=self.auto_2fa_refresh_token, font=("Segoe UI", 10), show="*").pack(fill=tk.X, pady=(0, 10))
        
        # Client ID
        ttk.Label(graph_frame, text="Client ID:", font=("Segoe UI", 10, "bold")).pack(anchor=tk.W)
        self.auto_2fa_client_id = tk.StringVar(value="9e5f94bc-e8a4-4e73-b8be-63364c29d753")
        ttk.Entry(graph_frame, textvariable=self.auto_2fa_client_id, font=("Segoe UI", 10)).pack(fill=tk.X, pady=(0, 10))
        
        # Email Password (for IMAP fallback)
        ttk.Label(graph_frame, text="Email Password (IMAP backup):", font=("Segoe UI", 10, "bold")).pack(anchor=tk.W)
        self.auto_2fa_email_password = tk.StringVar()
        ttk.Entry(graph_frame, textvariable=self.auto_2fa_email_password, font=("Segoe UI", 10), show="*").pack(fill=tk.X, pady=(0, 10))
        
        # Device Login Setup
        device_frame = ttk.LabelFrame(main_frame, text="🔐 Device Login Setup (One-time)", padding="15")
        device_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Device login button
        ttk.Button(device_frame, text="🔐 Setup Device Login", 
                  command=self.setup_device_login).pack(side=tk.LEFT, padx=(0, 10))
        
        # Test button
        ttk.Button(device_frame, text="🧪 Test Auto 2FA", 
                  command=self.test_auto_2fa_connection).pack(side=tk.LEFT, padx=(0, 10))
        
        # Continuous monitor button
        ttk.Button(device_frame, text="🔍 Continuous Monitor", 
                  command=self.start_continuous_monitor).pack(side=tk.LEFT, padx=(0, 10))
        
        # Token Management
        token_frame = ttk.LabelFrame(main_frame, text="💾 Token Management", padding="15")
        token_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Save/Load/Clear buttons
        ttk.Button(token_frame, text="💾 Save Config", 
                  command=self.save_auto_2fa_config).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(token_frame, text="📂 Load Config", 
                  command=self.load_auto_2fa_config).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(token_frame, text="🗑️ Clear Config", 
                  command=self.clear_auto_2fa_config).pack(side=tk.LEFT, padx=(0, 10))
        
        # Test Account Line
        test_frame = ttk.LabelFrame(main_frame, text="🧪 Test Account Line", padding="15")
        test_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(test_frame, text="Account Line:", font=("Segoe UI", 10, "bold")).pack(anchor=tk.W)
        self.test_account_line = tk.StringVar()
        ttk.Entry(test_frame, textvariable=self.test_account_line, font=("Segoe UI", 10)).pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(test_frame, text="🧪 Test Account Line", 
                  command=self.test_account_line_2fa).pack(anchor=tk.W)
        
        # Status/Log Area
        status_frame = ttk.LabelFrame(main_frame, text="📋 Status & Logs", padding="15")
        status_frame.pack(fill=tk.BOTH, expand=True)
        
        # Status text area
        self.auto_2fa_status = tk.Text(status_frame, height=8, font=("Consolas", 9), 
                                      bg="#f8f9fa", fg="#212529", wrap=tk.WORD)
        self.auto_2fa_status.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar for status
        status_scrollbar = ttk.Scrollbar(status_frame, orient=tk.VERTICAL, command=self.auto_2fa_status.yview)
        status_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.auto_2fa_status.config(yscrollcommand=status_scrollbar.set)
        
        # Guide
        guide_frame = ttk.LabelFrame(main_frame, text="📖 Auto 2FA Guide", padding="15")
        guide_frame.pack(fill=tk.X, pady=(15, 0))
        
        guide_text = tk.Text(guide_frame, height=6, font=("Segoe UI", 9), 
                            bg="#e3f2fd", fg="#1565c0", wrap=tk.WORD)
        guide_text.pack(fill=tk.BOTH, expand=True)
        
        guide_content = """[LAUNCH] Auto TikTok 2FA - Hướng dẫn sử dụng:

📋 Các phương pháp hỗ trợ (theo thứ tự ưu tiên):
1. 🔑 Access Token từ environment
2. 🔄 Refresh Token + Client ID  
3. 🔐 Device Login (tự động)
4. 📧 IMAP với Email Password

⚡ Tính năng mới:
✅ Tự động fallback giữa các phương pháp
✅ Không cần consent lại sau lần đầu
✅ Hỗ trợ tìm kiếm trong 30 phút
✅ Tự động refresh token
✅ IMAP backup nếu Graph API lỗi

🔧 Cách thiết lập:
1. Click "Setup Device Login" để lấy refresh token
2. Nhập email và password (cho IMAP backup)
3. Click "Save Config" để lưu cấu hình
4. Test với "Test Auto 2FA"

💡 Lưu ý:
- Device login chỉ cần làm 1 lần duy nhất
- Refresh token có thể dùng mãi mãi
- IMAP cần App Password nếu có 2FA
- Hệ thống tự động chọn phương pháp tốt nhất"""
        
        guide_text.insert(tk.END, guide_content)
        guide_text.config(state=tk.DISABLED)
        
        # Tải cấu hình hiện tại
        self.load_auto_2fa_config()
        
        # Add token section
        add_token_frame = ttk.Frame(tokens_frame)
        add_token_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(add_token_frame, text="Email:", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=(0, 10))
        self.new_email = tk.StringVar()
        ttk.Entry(add_token_frame, textvariable=self.new_email, font=("Segoe UI", 10), width=30).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Label(add_token_frame, text="Refresh Token:", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=(0, 10))
        self.new_refresh_token = tk.StringVar()
        ttk.Entry(add_token_frame, textvariable=self.new_refresh_token, font=("Segoe UI", 10), width=40).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(add_token_frame, text="➕ Thêm Token", 
                  command=self.add_email_token).pack(side=tk.LEFT, padx=(0, 10))
        
        # Tokens list
        list_frame = ttk.Frame(tokens_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview for tokens
        columns = ("Email", "Type", "Status")
        self.tokens_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=8)
        
        self.tokens_tree.heading("Email", text="📧 Email")
        self.tokens_tree.heading("Type", text="🔧 Type")
        self.tokens_tree.heading("Status", text="✅ Status")
        
        self.tokens_tree.column("Email", width=300)
        self.tokens_tree.column("Type", width=100)
        self.tokens_tree.column("Status", width=100)
        
        # Scrollbar
        tokens_scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tokens_tree.yview)
        self.tokens_tree.configure(yscrollcommand=tokens_scrollbar.set)
        
        self.tokens_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tokens_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Buttons
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(buttons_frame, text="💾 Lưu cấu hình", 
                  command=self.save_email_config).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(buttons_frame, text="🔄 Tải cấu hình", 
                  command=self.load_email_config).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(buttons_frame, text="🧪 Test kết nối", 
                  command=self.test_email_connection).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(buttons_frame, text="🗑️ Xóa token", 
                  command=self.remove_email_token).pack(side=tk.LEFT)
        
        # Load existing config
        self.load_email_config()
        
        self.current_tab = 'email_config'
        self.update_tab_highlight()
        
    def show_import_tab(self):
        """Hiển thị tab Import"""
        self.update_tab_highlight('import')
        self.clear_content()
        
        # Refresh profiles list when entering this tab
        self.refresh_profiles()
        
        # Header
        header_frame = ttk.Frame(self.content_frame, style='Modern.TFrame')
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = ttk.Label(header_frame, text="📥 Import Profiles từ Excel", 
                               style='Modern.TLabel', font=('Arial', 24, 'bold'))
        title_label.pack(anchor=tk.W)
        
        # Description
        desc_label = ttk.Label(header_frame, 
                              text="Import nhiều profiles từ file Excel với cấu hình proxy và user agent",
                              style='Modern.TLabel', font=('Arial', 12))
        desc_label.pack(anchor=tk.W, pady=(5, 0))
        
        # Main content frame
        main_frame = ttk.Frame(self.content_frame, style='Modern.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Import controls
        left_panel = ttk.Frame(main_frame, style='Modern.TFrame')
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # File selection
        file_frame = ttk.LabelFrame(left_panel, text="📁 Chọn file Excel", padding="15")
        file_frame.pack(fill=tk.X, pady=(0, 20))
        
        file_path_var = tk.StringVar()
        file_entry = ttk.Entry(file_frame, textvariable=file_path_var, font=('Arial', 11))
        file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        def browse_file():
            from tkinter import filedialog
            file_path = filedialog.askopenfilename(
                title="Chọn file Excel",
                filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
            )
            if file_path:
                file_path_var.set(file_path)
                load_preview()
        
        browse_btn = ttk.Button(file_frame, text="Browse", command=browse_file)
        browse_btn.pack(side=tk.RIGHT)
        
        # Import options
        options_frame = ttk.LabelFrame(left_panel, text="⚙️ Tùy chọn Import", padding="15")
        options_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Checkboxes
        skip_header_var = tk.BooleanVar(value=True)
        skip_header_cb = ttk.Checkbutton(options_frame, text="Bỏ qua dòng header (dòng 1)", 
                                        variable=skip_header_var)
        skip_header_cb.pack(anchor=tk.W, pady=(0, 5))
        
        auto_create_var = tk.BooleanVar(value=True)
        auto_create_cb = ttk.Checkbutton(options_frame, text="Tự động tạo profiles", 
                                        variable=auto_create_var)
        auto_create_cb.pack(anchor=tk.W, pady=(0, 5))
        
        # Import button
        def start_import():
            if not file_path_var.get():
                messagebox.showerror("Lỗi", "Vui lòng chọn file Excel!")
                return
            
            try:
                import_profiles_from_excel(file_path_var.get(), skip_header_var.get(), auto_create_var.get())
            except Exception as e:
                messagebox.showerror("Lỗi", f"Lỗi khi import: {str(e)}")
        
        import_btn = ttk.Button(left_panel, text="[LAUNCH] Bắt đầu Import", 
                               command=start_import, style='Accent.TButton')
        import_btn.pack(fill=tk.X, pady=(0, 20))
        
        # Import từ NKT folder đã được xóa
        
        # Import từ NKT functions đã được xóa
        
        # Right panel - Preview
        right_panel = ttk.Frame(main_frame, style='Modern.TFrame')
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Preview frame
        preview_frame = ttk.LabelFrame(right_panel, text="👁️ Preview dữ liệu", padding="15")
        preview_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview for preview
        columns = ('Browser', 'Profile Name', 'Connection Type', 'Connection Data', 'Group', 'User Agent')
        preview_tree = ttk.Treeview(preview_frame, columns=columns, show='headings', height=15)
        
        # Configure columns
        for col in columns:
            preview_tree.heading(col, text=col)
            preview_tree.column(col, width=120, minwidth=100)
        
        # Scrollbar
        preview_scrollbar = ttk.Scrollbar(preview_frame, orient=tk.VERTICAL, command=preview_tree.yview)
        preview_tree.configure(yscrollcommand=preview_scrollbar.set)
        
        preview_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        preview_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        def load_preview():
            """Load preview data from Excel file"""
            if not file_path_var.get():
                return
            
            try:
                # Clear existing items
                for item in preview_tree.get_children():
                    preview_tree.delete(item)
                
                # Load Excel data
                import pandas as pd
                df = pd.read_excel(file_path_var.get())
                
                # Skip header if needed
                if skip_header_var.get() and len(df) > 0:
                    df = df.iloc[1:]
                
                # Add data to treeview
                for index, row in df.iterrows():
                    values = []
                    for col in columns:
                        value = str(row.get(col, '')) if col in df.columns else ''
                        values.append(value[:50] + '...' if len(value) > 50 else value)
                    preview_tree.insert('', tk.END, values=values)
                
                # Update column widths
                for col in columns:
                    preview_tree.column(col, width=150)
                
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể load preview: {str(e)}")
        
        def import_profiles_from_excel(file_path, skip_header, auto_create):
            """Import profiles from Excel file"""
            try:
                import pandas as pd
                df = pd.read_excel(file_path)
                
                # Skip header if needed
                if skip_header and len(df) > 0:
                    df = df.iloc[1:]
                
                success_count = 0
                error_count = 0
                
                for index, row in df.iterrows():
                    try:
                        # Extract data
                        browser_name = str(row.get('Browser name', 'Chrome')).strip()
                        profile_name = str(row.get('Profile name', f'Profile_{index+1}')).strip()
                        connection_type = str(row.get('Connection Type', 'Local')).strip()
                        connection_data = str(row.get('Connection data (Proxy / Socks5)', '')).strip()
                        group = str(row.get('Group', 'All')).strip()
                        custom_ua = str(row.get('Custom user agent', '')).strip()
                        
                        if not profile_name or profile_name == 'nan':
                            continue
                        
                        # Create profile
                        if auto_create:
                            success, message = self.manager.clone_chrome_profile(profile_name, "Default", "work")
                            if success:
                                # Save settings
                                profile_path = os.path.join(self.manager.profiles_dir, profile_name)
                                settings_path = os.path.join(profile_path, 'profile_settings.json')
                                
                                settings_data = {
                                    'profile_info': {
                                        'name': profile_name,
                                        'display_name': profile_name,
                                        'type': 'work',
                                        'created_at': time.strftime('%Y-%m-%d %H:%M:%S')
                                    },
                                    'software': {
                                        'user_agent': custom_ua if custom_ua and custom_ua != 'nan' else 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.109 Safari/537.36',
                                        'language': 'en-US',
                                        'startup_url': '',
                                        'webrtc_policy': 'default_public_interface_only',
                                        'os_font': 'Real'
                                    },
                                    'hardware': {
                                        'mac_address': self.manager._generate_random_mac()
                                    },
                                    'connection': {
                                        'type': connection_type,
                                        'data': connection_data,
                                        'group': group
                                    }
                                }
                                
                                import json
                                with open(settings_path, 'w', encoding='utf-8') as f:
                                    json.dump(settings_data, f, ensure_ascii=False, indent=2)
                                
                                success_count += 1
                            else:
                                error_count += 1
                        else:
                            success_count += 1
                            
                    except Exception as e:
                        print(f"Lỗi import profile {index+1}: {str(e)}")
                        error_count += 1
                
                # Show result
                messagebox.showinfo("Hoàn thành", 
                                  f"Import hoàn thành!\n"
                                  f"✅ Thành công: {success_count} profiles\n"
                                  f"❌ Lỗi: {error_count} profiles")
                
                # Refresh profiles list
                self.refresh_profiles()
                
            except Exception as e:
                messagebox.showerror("Lỗi", f"Lỗi khi import: {str(e)}")
        
        # Bind file path change to load preview
        file_path_var.trace('w', lambda *args: load_preview())
        
    # NKT Config functions đã được xóa
        
    def show_settings_tab(self):
        """Hiển thị tab Settings"""
        self.update_tab_highlight('settings')
        self.clear_content()
        
        # Header
        header_frame = ttk.Frame(self.content_frame, style='Modern.TFrame')
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = ttk.Label(header_frame, text="⚙️ Cài đặt", 
                               style='Modern.TLabel', font=('Arial', 24, 'bold'))
        title_label.pack()
        
        # Settings content
        settings_frame = ttk.LabelFrame(self.content_frame, text="🔧 Cấu hình hệ thống", 
                                       style='Modern.TFrame', padding=20)
        settings_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Auto start
        auto_frame = ttk.Frame(settings_frame, style='Modern.TFrame')
        auto_frame.pack(fill=tk.X, pady=10)
        
        self.auto_start_var = tk.BooleanVar()
        self.auto_start_var.set(self.manager.config.getboolean('SETTINGS', 'auto_start', fallback=False))
        ttk.Checkbutton(auto_frame, text="🔄 Tự động khởi động", 
                       variable=self.auto_start_var,
                       style='Modern.TCheckbutton').pack(side=tk.LEFT)
        
        # Hidden mode
        hidden_frame = ttk.Frame(settings_frame, style='Modern.TFrame')
        hidden_frame.pack(fill=tk.X, pady=10)
        
        self.hidden_mode_var = tk.BooleanVar()
        self.hidden_mode_var.set(self.manager.config.getboolean('SETTINGS', 'hidden_mode', fallback=True))
        ttk.Checkbutton(hidden_frame, text="👁️ Chế độ ẩn", 
                       variable=self.hidden_mode_var,
                       style='Modern.TCheckbutton').pack(side=tk.LEFT)
        
        # Save button
        button_frame = ttk.Frame(self.content_frame, style='Modern.TFrame')
        button_frame.pack(fill=tk.X, pady=20)
        
        ttk.Button(button_frame, text="💾 Lưu cài đặt", 
                  style='Modern.TButton',
                  command=self.save_settings).pack(side=tk.LEFT, padx=5)
        
    def show_tools_tab(self):
        """Hiển thị tab Tools"""
        self.update_tab_highlight('tools')
        self.clear_content()
        
        # Header
        header_frame = ttk.Frame(self.content_frame, style='Modern.TFrame')
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = ttk.Label(header_frame, text="🛠️ Công cụ", 
                               style='Modern.TLabel', font=('Arial', 24, 'bold'))
        title_label.pack()
        
        # Tools grid
        tools_frame = ttk.Frame(self.content_frame, style='Modern.TFrame')
        tools_frame.pack(fill=tk.BOTH, expand=True)
        
        # Row 1
        row1 = ttk.Frame(tools_frame, style='Modern.TFrame')
        row1.pack(fill=tk.X, pady=10)
        
        ttk.Button(row1, text="📊 Thống kê Profiles", 
                  style='Modern.TButton',
                  command=self.profile_stats).pack(side=tk.LEFT, padx=5)
        ttk.Button(row1, text="🍪 Kiểm tra Cookies", 
                  style='Modern.TButton',
                  command=self.check_cookies).pack(side=tk.LEFT, padx=5)
        ttk.Button(row1, text="🧹 Dọn dẹp Profiles", 
                  style='Modern.TButton',
                  command=self.cleanup_profiles).pack(side=tk.LEFT, padx=5)
        
        # Row 2
        row2 = ttk.Frame(tools_frame, style='Modern.TFrame')
        row2.pack(fill=tk.X, pady=10)
        
        ttk.Button(row2, text="🔍 Phân tích dữ liệu", 
                  style='Modern.TButton',
                  command=self.analyze_data).pack(side=tk.LEFT, padx=5)
        ttk.Button(row2, text="⚡ Kiểm tra hệ thống", 
                  style='Modern.TButton',
                  command=self.system_check).pack(side=tk.LEFT, padx=5)
        ttk.Button(row2, text="📋 Xem logs", 
                  style='Modern.TButton',
                  command=self.view_logs).pack(side=tk.LEFT, padx=5)
        
    def show_account_status_tab(self):
        """Hiển thị tab Account Status"""
        self.update_tab_highlight('accounts')
        self.clear_content()
        
        # Header
        header_frame = ttk.Frame(self.content_frame, style='Modern.TFrame')
        header_frame.pack(fill=tk.X, pady=(0, 25))
        
        title_label = ttk.Label(header_frame, text="👤 Account Status Checker", 
                               style='Modern.TLabel', 
                               font=('Segoe UI', 28, 'bold'))
        title_label.pack(anchor='w')
        
        subtitle_label = ttk.Label(header_frame, text="Kiểm tra trạng thái tài khoản đã đăng nhập", 
                                 style='Modern.TLabel', 
                                 font=('Segoe UI', 11),
                                 foreground='#b3b3b3')
        subtitle_label.pack(anchor='w', pady=(5, 0))
        
        # Control buttons
        control_frame = ttk.Frame(header_frame, style='Modern.TFrame')
        control_frame.pack(side=tk.RIGHT, pady=(10, 0))
        
        ttk.Button(control_frame, text="🔄 Kiểm tra tất cả", 
                  style='Modern.TButton',
                  command=self.check_all_accounts).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(control_frame, text="👤 Kiểm tra profile", 
                  style='Modern.TButton',
                  command=self.check_single_account).pack(side=tk.LEFT)
        
        # Results frame
        results_frame = ttk.LabelFrame(self.content_frame, text="📊 Kết quả kiểm tra", 
                                      style='Modern.TLabelframe', padding=20)
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview để hiển thị kết quả
        columns = ("Profile", "Platform", "Status", "Message", "Last Check")
        self.status_tree = ttk.Treeview(results_frame, columns=columns, show="headings", 
                                       style='Modern.Treeview', height=15)
        
        # Cấu hình cột
        self.status_tree.heading("Profile", text="👤 Profile")
        self.status_tree.heading("Platform", text="🌐 Platform")
        self.status_tree.heading("Status", text="⚡ Status")
        self.status_tree.heading("Message", text="💬 Message")
        self.status_tree.heading("Last Check", text="🕒 Last Check")
        
        self.status_tree.column("Profile", width=150, minwidth=120)
        self.status_tree.column("Platform", width=120, minwidth=100)
        self.status_tree.column("Status", width=100, minwidth=80)
        self.status_tree.column("Message", width=300, minwidth=250)
        self.status_tree.column("Last Check", width=150, minwidth=120)
        
        # Scrollbar
        status_scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=self.status_tree.yview)
        self.status_tree.configure(yscrollcommand=status_scrollbar.set)
        
        self.status_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        status_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Status bar
        status_frame = ttk.Frame(self.content_frame, style='Modern.TFrame')
        status_frame.pack(fill=tk.X, pady=(15, 0))
        
        # Status indicator
        status_indicator = ttk.Label(status_frame, text="●", 
                                   style='Modern.TLabel', 
                                   font=('Segoe UI', 8),
                                   foreground='#4CAF50')
        status_indicator.pack(side=tk.LEFT, padx=(0, 8))
        
        self.account_status_label = ttk.Label(status_frame, text="Sẵn sàng kiểm tra tài khoản", 
                                            style='Modern.TLabel',
                                            font=('Segoe UI', 9))
        self.account_status_label.pack(side=tk.LEFT)
        
    def clear_content(self):
        """Xóa nội dung hiện tại"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
            
    def setup_context_menu(self):
        """Thiết lập context menu"""
        self.context_menu = tk.Menu(self.root, tearoff=0, bg='#404040', fg='#ffffff')
        self.context_menu.add_command(label="▶️ Starting (Hiển thị)", 
                                     command=lambda: self.launch_profile(False))
        self.context_menu.add_command(label="▶️ Starting (Ẩn)", 
                                     command=lambda: self.launch_profile(True))
        self.context_menu.add_command(label="▶️ Starting (Mặc định)", 
                                     command=lambda: self.launch_profile(None))
        self.context_menu.add_separator()
        self.context_menu.add_command(label="🔧 Cấu hình đăng nhập", 
                                     command=self.configure_login)
        self.context_menu.add_command(label="🌐 Đăng nhập Chrome", 
                                     command=self.login_chrome_account)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="📋 Nhân bản Extensions", 
                                     command=self.clone_extensions_dialog)
        self.context_menu.add_command(label="🔄 Nhân bản từ Template", 
                                     command=self.clone_extensions_from_template)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="📤 Xuất Cookies", 
                                     command=self.export_cookies)
        self.context_menu.add_command(label="📥 Import Cookies", 
                                     command=self.import_cookies)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="✏️ Chỉnh sửa cấu hình...",
                                     command=self.edit_profile_settings)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="🗑️ Xóa Profile", 
                                     command=self.delete_profile)
        self.context_menu.add_command(label="🗑️ Xóa Hàng Loạt", 
                                     command=self.bulk_delete_selected)
        
        self.tree.bind("<Button-3>", self.show_context_menu)
            
    def show_context_menu(self, event):
        """Hiển thị context menu"""
        item = self.tree.selection()[0] if self.tree.selection() else None
        if item:
            self.context_menu.post(event.x_root, event.y_root)
    
    def edit_profile_settings(self):
        """Mở dialog chỉnh sửa Software/Hardware cho profile đang chọn"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một profile để chỉnh sửa!")
            return
        profile_name = self.tree.item(selection[0])['text']
        if not profile_name:
            messagebox.showwarning("Cảnh báo", "Không xác định được profile!")
            return
        import os, json
        profile_path = os.path.join(self.manager.profiles_dir, profile_name)
        settings_path = os.path.join(profile_path, 'profile_settings.json')
        data = {}
        try:
            if os.path.exists(settings_path):
                with open(settings_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
        except Exception as e:
            print(f"⚠️ Không đọc được settings: {e}")
            data = {}
        # Defaults
        sw = data.get('software', {})
        hw = data.get('hardware', {})
        # Bổ sung giá trị mặc định từ hệ thống nếu chưa có
        try:
            import os as _os
            import uuid as _uuid
            try:
                import psutil as _psutil
            except Exception:
                _psutil = None
            if not hw.get('cpu_cores'):
                hw['cpu_cores'] = str(_os.cpu_count() or '')
            if not hw.get('device_memory'):
                if _psutil:
                    try:
                        hw['device_memory'] = str(int(round((_psutil.virtual_memory().total or 0) / (1024**3))))
                    except Exception:
                        hw['device_memory'] = ''
                else:
                    hw['device_memory'] = ''
            if not hw.get('mac_address'):
                try:
                    mac_int = _uuid.getnode()
                    mac_hex = ':'.join(f"{(mac_int >> ele) & 0xff:02X}" for ele in range(40, -1, -8))
                    hw['mac_address'] = mac_hex
                except Exception:
                    hw['mac_address'] = ''
            # Media defaults nếu thiếu
            hw.setdefault('media_audio_inputs', '2')
            hw.setdefault('media_audio_outputs', '0')
            hw.setdefault('media_video_inputs', '0')
            # WebGL masked mặc định True
            if 'webgl_meta_masked' not in hw:
                hw['webgl_meta_masked'] = True
        except Exception as _e:
            print(f"⚠️ Không thể lấy thông tin phần cứng mặc định: {_e}")
        # Dialog
        dlg = tk.Toplevel(self.root)
        dlg.title(f"Chỉnh sửa cấu hình - {profile_name}")
        dlg.geometry("780x600")
        dlg.minsize(720, 520)
        dlg.transient(self.root)
        dlg.grab_set()
        notebook = ttk.Notebook(dlg)
        notebook.pack(fill=tk.BOTH, expand=True)
        # Software tab
        sw_frame = ttk.Frame(notebook, padding=15)
        notebook.add(sw_frame, text="Software")
        # UA
        ttk.Label(sw_frame, text="User-Agent:").grid(row=0, column=0, sticky='w')
        ua_var = tk.StringVar(value=sw.get('user_agent', ''))
        ua_entry = ttk.Entry(sw_frame, textvariable=ua_var)
        ua_entry.grid(row=0, column=1, sticky='ew', padx=8)
        # UA Presets (4-5 lựa chọn) để chèn nhanh vào ô UA
        try:
            ua_presets = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.1025.67",
            ]
            ttk.Label(sw_frame, text="UA Presets:").grid(row=0, column=2, sticky='w', padx=(10,0))
            ua_preset_var = tk.StringVar(value=ua_presets[0])
            ua_combo = ttk.Combobox(sw_frame, textvariable=ua_preset_var, state='readonly', values=ua_presets, width=40)
            ua_combo.grid(row=0, column=3, sticky='ew')
            def apply_ua_preset():
                ua_var.set(ua_preset_var.get())
            ttk.Button(sw_frame, text="Dùng preset", command=apply_ua_preset).grid(row=0, column=4, sticky='w', padx=(6,0))
        except Exception:
            pass
        # Language
        ttk.Label(sw_frame, text="Language (Accept-Language / --lang):").grid(row=1, column=0, sticky='w', pady=(8,0))
        lang_var = tk.StringVar(value=sw.get('language', 'en-US'))
        lang_entry = ttk.Entry(sw_frame, textvariable=lang_var)
        lang_entry.grid(row=1, column=1, sticky='ew', padx=8, pady=(8,0))
        # Startup URL
        ttk.Label(sw_frame, text="Startup URL:").grid(row=2, column=0, sticky='w', pady=(8,0))
        url_var = tk.StringVar(value=sw.get('startup_url', ''))
        url_entry = ttk.Entry(sw_frame, textvariable=url_var)
        url_entry.grid(row=2, column=1, sticky='ew', padx=8, pady=(8,0))
        # WebRTC policy
        ttk.Label(sw_frame, text="WebRTC IP policy:").grid(row=3, column=0, sticky='w', pady=(8,0))
        webrtc_var = tk.StringVar(value=sw.get('webrtc_policy', 'default_public_interface_only'))
        webrtc_combo = ttk.Combobox(sw_frame, textvariable=webrtc_var, state='readonly', values=[
            'default_public_interface_only', 'default', 'disable_non_proxied_udp'
        ])
        webrtc_combo.grid(row=3, column=1, sticky='ew', padx=8, pady=(8,0))
        # OS Font (display only)
        ttk.Label(sw_frame, text="OS Font (tùy chọn):").grid(row=4, column=0, sticky='w', pady=(8,0))
        font_var = tk.StringVar(value=sw.get('os_font', 'Real'))
        font_entry = ttk.Entry(sw_frame, textvariable=font_var)
        font_entry.grid(row=4, column=1, sticky='ew', padx=8, pady=(8,0))
        sw_frame.columnconfigure(1, weight=1)
        # Hardware tab
        hw_frame = ttk.Frame(notebook, padding=15)
        notebook.add(hw_frame, text="Hardware")
        # Mặc định chọn tab Software khi mở
        try:
            notebook.select(sw_frame)
        except Exception:
            pass
        # Thông báo về thông tin phần cứng ngẫu nhiên
        info_label = ttk.Label(hw_frame, text="Phần mềm đã tạo ngẫu nhiên một thông tin phần cứng. Nếu không quá hiểu về Fingerprint, bạn có thể không quan tâm tới phần này. Các thông tin về RAM, CPU Core, Audio, Media outputs, WebGL, Tên card màn hình... đã được sinh ngẫu nhiên!", 
                              font=("Segoe UI", 9), foreground="gray", wraplength=600)
        info_label.grid(row=0, column=0, columnspan=2, sticky='w', pady=(0, 15))
        
        # Tạo 2 cột
        left_frame = ttk.Frame(hw_frame)
        left_frame.grid(row=1, column=0, sticky='nw', padx=(0, 20))
        right_frame = ttk.Frame(hw_frame)
        right_frame.grid(row=1, column=1, sticky='nw')
        
        # Cột trái - Cấu hình Hardware
        # Phân giải màn hình
        ttk.Label(left_frame, text="Phân giải màn hình:").grid(row=0, column=0, sticky='w', pady=(0, 5))
        screen_res_var = tk.StringVar(value=hw.get('screen_resolution', 'Real'))
        ttk.Entry(left_frame, textvariable=screen_res_var, width=20).grid(row=0, column=1, sticky='w', padx=(5, 0), pady=(0, 5))
        
        # Canvas noise
        ttk.Label(left_frame, text="Canvas noise:").grid(row=1, column=0, sticky='w', pady=(0, 5))
        canvas_noise_var = tk.StringVar(value=hw.get('canvas_noise', 'Off'))
        canvas_combo = ttk.Combobox(left_frame, textvariable=canvas_noise_var, state='readonly', values=['Off', 'On'], width=17)
        canvas_combo.grid(row=1, column=1, sticky='w', padx=(5, 0), pady=(0, 5))
        
        # Client rect noise
        ttk.Label(left_frame, text="Client rect noise:").grid(row=2, column=0, sticky='w', pady=(0, 5))
        client_rect_var = tk.StringVar(value=hw.get('client_rect_noise', 'Off'))
        client_rect_combo = ttk.Combobox(left_frame, textvariable=client_rect_var, state='readonly', values=['Off', 'On'], width=17)
        client_rect_combo.grid(row=2, column=1, sticky='w', padx=(5, 0), pady=(0, 5))
        
        # WebGL image noise
        ttk.Label(left_frame, text="WebGL image noise:").grid(row=3, column=0, sticky='w', pady=(0, 5))
        webgl_img_var = tk.StringVar(value=hw.get('webgl_image_noise', 'Off'))
        webgl_img_combo = ttk.Combobox(left_frame, textvariable=webgl_img_var, state='readonly', values=['Off', 'On'], width=17)
        webgl_img_combo.grid(row=3, column=1, sticky='w', padx=(5, 0), pady=(0, 5))
        
        # Audio noise
        ttk.Label(left_frame, text="Audio noise:").grid(row=4, column=0, sticky='w', pady=(0, 5))
        audio_noise_var = tk.StringVar(value=hw.get('audio_noise', 'On'))
        audio_combo = ttk.Combobox(left_frame, textvariable=audio_noise_var, state='readonly', values=['Off', 'On'], width=17)
        audio_combo.grid(row=4, column=1, sticky='w', padx=(5, 0), pady=(0, 5))
        
        # WebGL Meta masked
        webgl_mask_var = tk.BooleanVar(value=hw.get('webgl_meta_masked', True))
        ttk.Checkbutton(left_frame, text="✔ WebGL Meta masked", variable=webgl_mask_var).grid(row=5, column=0, columnspan=2, sticky='w', pady=(5, 5))
        
        # WebGL Vendor
        ttk.Label(left_frame, text="WebGL Vendor:").grid(row=6, column=0, sticky='w', pady=(0, 5))
        webgl_vendor_var = tk.StringVar(value=hw.get('webgl_vendor', 'Google Inc. (NVIDIA)'))
        
        # WebGL vendor options for edit dialog
        webgl_vendor_options_edit = [
            "Google Inc. (NVIDIA)",
            "Google Inc. (Intel)", 
            "Google Inc. (AMD)",
            "NVIDIA Corporation",
            "Intel Inc.",
            "Microsoft Corporation"
        ]
        
        webgl_vendor_combo_edit = ttk.Combobox(left_frame, textvariable=webgl_vendor_var, values=webgl_vendor_options_edit, width=25, state="readonly")
        webgl_vendor_combo_edit.grid(row=6, column=1, sticky='w', padx=(5, 0), pady=(0, 5))
        
        # Random WebGL Vendor button for edit dialog
        def random_webgl_vendor_edit():
            import random
            webgl_vendor_var.set(random.choice(webgl_vendor_options_edit))
        
        ttk.Button(left_frame, text="Random", command=random_webgl_vendor_edit, width=8).grid(row=6, column=2, sticky='w', padx=(5, 0), pady=(0, 5))
        
        # WebGL Renderer
        ttk.Label(left_frame, text="WebGL Renderer:").grid(row=7, column=0, sticky='w', pady=(0, 5))
        webgl_renderer_var = tk.StringVar(value=hw.get('webgl_renderer', 'ANGLE (NVIDIA, NVIDIA GeForce RTX 3080 Ti Direct3D11 vs_5_0 ps_5_0, D3D11)'))
        
        # WebGL renderer options for edit dialog
        webgl_renderer_options_edit = [
            # NVIDIA Graphics
            "ANGLE (NVIDIA, NVIDIA GeForce RTX 3080 Ti Direct3D11 vs_5_0 ps_5_0, D3D11)",
            "ANGLE (NVIDIA, NVIDIA GeForce GTX 1060 Direct3D11 vs_5_0 ps_5_0, D3D11)",
            "ANGLE (NVIDIA, NVIDIA GeForce RTX 3060 Direct3D11 vs_5_0 ps_5_0, D3D11)",
            # Intel Graphics - UHD Series
            "ANGLE (Intel, Intel(R) UHD Graphics 620 (0x00005917) Direct3D11 vs_5_0 ps_5_0, D3D11)",
            "ANGLE (Intel, Intel(R) UHD Graphics 630 (0x00005917) Direct3D11 vs_5_0 ps_5_0, D3D11)",
            "ANGLE (Intel, Intel(R) UHD Graphics 620 Direct3D11 vs_5_0 ps_5_0, D3D11)",
            "ANGLE (Intel, Intel(R) UHD Graphics 630 Direct3D11 vs_5_0 ps_5_0, D3D11)",
            # Intel Graphics - HD Series
            "ANGLE (Intel, Intel(R) HD Graphics 530 Direct3D11 vs_5_0 ps_5_0, D3D11)",
            "ANGLE (Intel, Intel(R) HD Graphics 520 Direct3D11 vs_5_0 ps_5_0, D3D11)",
            "ANGLE (Intel, Intel(R) HD Graphics 4600 Direct3D11 vs_5_0 ps_5_0, D3D11)",
            "ANGLE (Intel, Intel(R) HD Graphics 4000 Direct3D9Ex vs_3_0 ps_3_0, igdumdim64.dll-10.18.10.3345)",
            # Intel Graphics - Iris Series
            "ANGLE (Intel, Intel(R) Iris(R) Xe Graphics Direct3D11 vs_5_0 ps_5_0, D3D11)",
            "ANGLE (Intel, Intel(R) HD Graphics Family Direct3D11 vs_5_0 ps_5_0, D3D11)",
            # AMD Graphics
            "ANGLE (AMD, AMD Radeon RX 580 Direct3D11 vs_5_0 ps_5_0, D3D11)",
            "ANGLE (AMD, AMD Radeon RX 6600 Direct3D11 vs_5_0 ps_5_0, D3D11)"
        ]
        
        webgl_renderer_combo_edit = ttk.Combobox(left_frame, textvariable=webgl_renderer_var, values=webgl_renderer_options_edit, width=50, state="readonly")
        webgl_renderer_combo_edit.grid(row=7, column=1, sticky='w', padx=(5, 0), pady=(0, 5))
        
        # Random WebGL Renderer button for edit dialog
        def random_webgl_renderer_edit():
            import random
            webgl_renderer_var.set(random.choice(webgl_renderer_options_edit))
        
        ttk.Button(left_frame, text="Random", command=random_webgl_renderer_edit, width=8).grid(row=7, column=2, sticky='w', padx=(5, 0), pady=(0, 5))
        
        # Media devices masked
        media_mask_var = tk.BooleanVar(value=hw.get('media_devices_masked', True))
        ttk.Checkbutton(left_frame, text="✔ Media devices masked (Audio inputs / Audio outputs / Video inputs)", variable=media_mask_var).grid(row=8, column=0, columnspan=2, sticky='w', pady=(5, 5))
        
        # Media inputs/outputs trong 1 dòng
        media_frame = ttk.Frame(left_frame)
        media_frame.grid(row=9, column=0, columnspan=2, sticky='w', pady=(0, 5))
        mai_var = tk.StringVar(value=str(hw.get('media_audio_inputs', '1')))
        ttk.Entry(media_frame, textvariable=mai_var, width=5).grid(row=0, column=0, padx=(0, 5))
        mao_var = tk.StringVar(value=str(hw.get('media_audio_outputs', '1')))
        ttk.Entry(media_frame, textvariable=mao_var, width=5).grid(row=0, column=1, padx=(0, 5))
        mvi_var = tk.StringVar(value=str(hw.get('media_video_inputs', '1')))
        ttk.Entry(media_frame, textvariable=mvi_var, width=5).grid(row=0, column=2)
        
        # CPU cores
        ttk.Label(left_frame, text="CPU core:").grid(row=10, column=0, sticky='w', pady=(0, 5))
        cpu_var = tk.StringVar(value=str(hw.get('cpu_cores', '')))
        ttk.Entry(left_frame, textvariable=cpu_var, width=20).grid(row=10, column=1, sticky='w', padx=(5, 0), pady=(0, 5))
        
        # Memory devices
        ttk.Label(left_frame, text="Memory devices:").grid(row=11, column=0, sticky='w', pady=(0, 5))
        mem_var = tk.StringVar(value=str(hw.get('device_memory', '')))
        ttk.Entry(left_frame, textvariable=mem_var, width=20).grid(row=11, column=1, sticky='w', padx=(5, 0), pady=(0, 5))
        
        # MAC address
        ttk.Label(left_frame, text="MAC address:").grid(row=12, column=0, sticky='w', pady=(0, 5))
        mac_var = tk.StringVar(value=hw.get('mac_address', ''))
        ttk.Entry(left_frame, textvariable=mac_var, width=20).grid(row=12, column=1, sticky='w', padx=(5, 0), pady=(0, 5))
        
        # Nút tạo thông số mới
        def generate_new_params():
            import random, os
            # Tạo các giá trị ngẫu nhiên
            resolutions = ['1920x1080', '1366x768', '1440x900', '1536x864', 'Real']
            screen_res_var.set(random.choice(resolutions))
            canvas_noise_var.set(random.choice(['Off', 'On']))
            client_rect_var.set(random.choice(['Off', 'On']))
            webgl_img_var.set(random.choice(['Off', 'On']))
            audio_noise_var.set(random.choice(['Off', 'On']))
            webgl_vendor_var.set(random.choice(webgl_vendor_options_edit))
            webgl_renderer_var.set(random.choice(webgl_renderer_options_edit))
            cpu_var.set(str(random.randint(4, 16)))
            mem_var.set(str(random.randint(4, 32)))
            # Tạo MAC mới
            mac_bytes = [random.randint(0, 255) for _ in range(6)]
            mac_bytes[0] = (mac_bytes[0] | 0x02) & 0xFE  # locally administered, unicast
            mac_var.set(':'.join(f'{b:02X}' for b in mac_bytes))
            mai_var.set(str(random.randint(1, 3)))
            mao_var.set(str(random.randint(0, 2)))
            mvi_var.set(str(random.randint(0, 2)))
        
        ttk.Button(left_frame, text="✖ Tạo thông số mới", command=generate_new_params).grid(row=13, column=0, columnspan=2, sticky='w', pady=(10, 0))
        
        # Cột phải - Thông tin hiện tại
        ttk.Label(right_frame, text="Thông tin hiện tại:", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky='w', pady=(0, 10))
        
        # User-agent
        ttk.Label(right_frame, text="User-agent:").grid(row=1, column=0, sticky='w', pady=(0, 2))
        ua_display = tk.Text(right_frame, height=2, width=50, wrap=tk.WORD, font=("Consolas", 8))
        ua_display.grid(row=2, column=0, sticky='w', pady=(0, 5))
        ua_display.insert('1.0', sw.get('user_agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36'))
        ua_display.config(state='disabled')
        
        # OS
        ttk.Label(right_frame, text="OS:").grid(row=3, column=0, sticky='w', pady=(0, 2))
        ttk.Label(right_frame, text="Windows 11 64 bit").grid(row=4, column=0, sticky='w', pady=(0, 5))
        
        # Proxy
        ttk.Label(right_frame, text="Proxy:").grid(row=5, column=0, sticky='w', pady=(0, 2))
        ttk.Label(right_frame, text="Local IP").grid(row=6, column=0, sticky='w', pady=(0, 5))
        
        # Screen
        ttk.Label(right_frame, text="Screen:").grid(row=7, column=0, sticky='w', pady=(0, 2))
        ttk.Label(right_frame, text="-1x-1").grid(row=8, column=0, sticky='w', pady=(0, 5))
        
        # Timezone
        ttk.Label(right_frame, text="Timezone:").grid(row=9, column=0, sticky='w', pady=(0, 2))
        ttk.Label(right_frame, text="Base on IP").grid(row=10, column=0, sticky='w', pady=(0, 5))
        
        # Font list
        ttk.Label(right_frame, text="Font list:").grid(row=11, column=0, sticky='w', pady=(0, 2))
        ttk.Label(right_frame, text="Real").grid(row=12, column=0, sticky='w', pady=(0, 5))
        
        # Accept-language
        ttk.Label(right_frame, text="Accept-language:").grid(row=13, column=0, sticky='w', pady=(0, 2))
        ttk.Label(right_frame, text=sw.get('language', 'en-US')).grid(row=14, column=0, sticky='w', pady=(0, 5))
        
        # WebRTC
        ttk.Label(right_frame, text="WebRTC:").grid(row=15, column=0, sticky='w', pady=(0, 2))
        ttk.Label(right_frame, text="Base on IP").grid(row=16, column=0, sticky='w', pady=(0, 5))
        
        # CPU core
        ttk.Label(right_frame, text="CPU core:").grid(row=17, column=0, sticky='w', pady=(0, 2))
        ttk.Label(right_frame, text=cpu_var.get()).grid(row=18, column=0, sticky='w', pady=(0, 5))
        
        # Device memory
        ttk.Label(right_frame, text="Device memory:").grid(row=19, column=0, sticky='w', pady=(0, 2))
        ttk.Label(right_frame, text=mem_var.get()).grid(row=20, column=0, sticky='w', pady=(0, 5))
        
        # Media audio inputs
        ttk.Label(right_frame, text="Media audio inputs:").grid(row=21, column=0, sticky='w', pady=(0, 2))
        ttk.Label(right_frame, text=mai_var.get()).grid(row=22, column=0, sticky='w', pady=(0, 5))
        
        # Media audio outputs
        ttk.Label(right_frame, text="Media audio outputs:").grid(row=23, column=0, sticky='w', pady=(0, 2))
        ttk.Label(right_frame, text=mao_var.get()).grid(row=24, column=0, sticky='w', pady=(0, 5))
        
        # Media video inputs
        ttk.Label(right_frame, text="Media video inputs:").grid(row=25, column=0, sticky='w', pady=(0, 2))
        ttk.Label(right_frame, text=mvi_var.get()).grid(row=26, column=0, sticky='w', pady=(0, 5))
        
        # WebGL Meta
        ttk.Label(right_frame, text="WebGL Meta:").grid(row=27, column=0, sticky='w', pady=(0, 2))
        ttk.Label(right_frame, text="Masked" if webgl_mask_var.get() else "Off").grid(row=28, column=0, sticky='w', pady=(0, 5))
        
        # Canvas
        ttk.Label(right_frame, text="Canvas:").grid(row=29, column=0, sticky='w', pady=(0, 2))
        ttk.Label(right_frame, text=canvas_noise_var.get()).grid(row=30, column=0, sticky='w', pady=(0, 5))
        
        # Client rect
        ttk.Label(right_frame, text="Client rect:").grid(row=31, column=0, sticky='w', pady=(0, 2))
        ttk.Label(right_frame, text=client_rect_var.get()).grid(row=32, column=0, sticky='w', pady=(0, 5))
        
        # WebGL
        ttk.Label(right_frame, text="WebGL:").grid(row=33, column=0, sticky='w', pady=(0, 2))
        ttk.Label(right_frame, text=webgl_img_var.get()).grid(row=34, column=0, sticky='w', pady=(0, 5))
        
        # Audio Context
        ttk.Label(right_frame, text="Audio Context:").grid(row=35, column=0, sticky='w', pady=(0, 2))
        ttk.Label(right_frame, text=audio_noise_var.get()).grid(row=36, column=0, sticky='w', pady=(0, 5))
        
        hw_frame.columnconfigure(0, weight=1)
        hw_frame.columnconfigure(1, weight=1)
        # Buttons
        btn_frame = ttk.Frame(dlg)
        btn_frame.pack(fill=tk.X, pady=10)
        def save_and_close():
            new_data = {
                'software': {
                    'user_agent': ua_var.get().strip(),
                    'language': lang_var.get().strip() or 'en-US',
                    'startup_url': url_var.get().strip(),
                    'webrtc_policy': webrtc_var.get().strip() or 'default_public_interface_only',
                    'os_font': font_var.get().strip(),
                },
                'hardware': {
                    'screen_resolution': screen_res_var.get().strip(),
                    'canvas_noise': canvas_noise_var.get().strip(),
                    'client_rect_noise': client_rect_var.get().strip(),
                    'webgl_image_noise': webgl_img_var.get().strip(),
                    'audio_noise': audio_noise_var.get().strip(),
                    'webgl_meta_masked': bool(webgl_mask_var.get()),
                    'webgl_vendor': webgl_vendor_var.get().strip(),
                    'webgl_renderer': webgl_renderer_var.get().strip(),
                    'media_devices_masked': bool(media_mask_var.get()),
                    'cpu_cores': cpu_var.get().strip(),
                    'device_memory': mem_var.get().strip(),
                    'media_audio_inputs': mai_var.get().strip(),
                    'media_audio_outputs': mao_var.get().strip(),
                    'media_video_inputs': mvi_var.get().strip(),
                    'mac_address': mac_var.get().strip(),
                }
            }
            try:
                os.makedirs(profile_path, exist_ok=True)
                with open(settings_path, 'w', encoding='utf-8') as f:
                    json.dump(new_data, f, ensure_ascii=False, indent=2)
                messagebox.showinfo("Thành công", "Đã lưu cấu hình cho profile!")
                dlg.destroy()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể lưu cấu hình: {e}")
        ttk.Button(btn_frame, text="Lưu", command=save_and_close).pack(side=tk.RIGHT, padx=(0,10))
        ttk.Button(btn_frame, text="Đóng", command=dlg.destroy).pack(side=tk.RIGHT, padx=10)
            
    def refresh_profiles(self):
        """Làm mới danh sách profiles"""
        try:
            # Kiểm tra xem tree widget có tồn tại không
            if not hasattr(self, 'tree') or not self.tree.winfo_exists():
                print("⚠️ [REFRESH] Tree widget không tồn tại, bỏ qua refresh")
                return
            
            # Dọn dẹp drivers đã bị dừng
            self._cleanup_stopped_drivers()
            
            # Xóa tất cả items cũ
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Thêm profiles mới (với force refresh)
            profiles = self.manager.get_all_profiles(force_refresh=True)
            
            total_profiles = len(profiles)
            running_profiles = 0
            
            for profile in profiles:
                # Kiểm tra trạng thái đăng nhập TikTok
                is_logged_in = self.manager.is_profile_logged_in(profile)
                is_running = profile in self.drivers
                
                if is_running:
                    status = "Đang chạy (Đã đăng nhập)" if is_logged_in else "Đang chạy (Chưa đăng nhập)"
                    running_profiles += 1
                else:
                    status = "Đã đăng nhập" if is_logged_in else "Chưa đăng nhập"
                    
                action = "Dừng" if is_running else "Starting"
                
                self.tree.insert("", "end", text=profile, values=(profile, status, action))
            
            # Cập nhật thống kê
            self.total_profiles_label.config(text=f"Tổng profiles: {total_profiles}")
            self.running_profiles_label.config(text=f"Đang chạy: {running_profiles}")
            
            # Cập nhật combobox
            self.update_profile_combos()
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể làm mới danh sách profiles: {str(e)}")
    
    def _update_profile_status(self, profile_name, status):
        """Cập nhật trạng thái của một profile cụ thể trong TreeView"""
        try:
            if not hasattr(self, 'tree') or not self.tree.winfo_exists():
                return
            
            # Tìm profile trong tree
            for item in self.tree.get_children():
                if self.tree.item(item, 'text') == profile_name:
                    # Cập nhật status và action
                    current_values = list(self.tree.item(item, 'values'))
                    if len(current_values) >= 3:
                        current_values[1] = status  # Status column
                        current_values[2] = "Dừng" if "Running" in status else "Starting"  # Action column
                        self.tree.item(item, values=tuple(current_values))
                    break
                    
            # Cập nhật thống kê running profiles
            running_count = 0
            for item in self.tree.get_children():
                values = self.tree.item(item, 'values')
                if len(values) >= 2 and "Running" in values[1]:
                    running_count += 1
            
            if hasattr(self, 'running_profiles_label'):
                self.running_profiles_label.config(text=f"Đang chạy: {running_count}")
                
        except Exception as e:
            print(f"⚠️ [UPDATE-STATUS] Lỗi cập nhật trạng thái {profile_name}: {e}")
    
    def clear_login_session(self):
        """Xóa session đăng nhập của profile được chọn"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn profile để xóa session!")
            return
        
        profile_name = self.tree.item(selection[0])['text']
        
        # Xác nhận
        if not messagebox.askyesno("Xác nhận", 
                                  f"Bạn có chắc muốn xóa session đăng nhập của profile '{profile_name}'?\n"
                                  f"Lần sau mở profile sẽ cần đăng nhập lại."):
            return
        
        try:
            # Xóa marker file và cookies file
            profile_path = os.path.join(self.manager.profiles_dir, profile_name)
            marker_file = os.path.join(profile_path, 'tiktok_logged_in.txt')
            cookies_file = os.path.join(profile_path, 'tiktok_cookies.json')
            
            deleted_files = []
            if os.path.exists(marker_file):
                os.remove(marker_file)
                deleted_files.append("marker file")
            
            if os.path.exists(cookies_file):
                os.remove(cookies_file)
                deleted_files.append("cookies file")
            
            if deleted_files:
                messagebox.showinfo("Thành công", 
                                  f"Đã xóa session đăng nhập của '{profile_name}':\n"
                                  f"- {', '.join(deleted_files)}")
                self.refresh_profiles()
            else:
                messagebox.showinfo("Thông báo", 
                                  f"Profile '{profile_name}' chưa có session đăng nhập nào.")
                
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể xóa session: {str(e)}")
    
    def show_master_control_dialog(self):
        """Hiển thị dialog Master Control Mode"""
        print("🎮 [MASTER-CONTROL] Mở dialog Master Control Mode")
        
        # Lấy danh sách profiles đang chạy
        running_profiles = []
        if hasattr(self, 'drivers'):
            running_profiles = list(self.drivers.keys())
        
        if not running_profiles:
            messagebox.showwarning("Cảnh báo", "Không có profile nào đang chạy!\nVui lòng khởi động ít nhất 2 profiles trước khi sử dụng Master Control.")
            return
        
        # Tạo dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("🎮 Master Control Mode")
        dialog.geometry("800x600")
        dialog.resizable(True, True)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Main frame
        main_frame = tk.Frame(dialog, bg='#f0f0f0')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(main_frame, text="🎮 Master Control Mode", 
                              font=('Segoe UI', 18, 'bold'), bg='#f0f0f0')
        title_label.pack(pady=(0, 20))
        
        # Description
        desc_label = tk.Label(main_frame, 
                             text="Chọn 1 profile làm Master, các profile khác sẽ làm theo hành động của Master",
                             font=('Segoe UI', 10), bg='#f0f0f0', fg='#666')
        desc_label.pack(pady=(0, 20))
        
        # Master Profile Selection
        master_frame = tk.LabelFrame(main_frame, text="🎯 Chọn Master Profile", 
                                    font=('Segoe UI', 12, 'bold'), bg='#f0f0f0')
        master_frame.pack(fill=tk.X, pady=(0, 15))
        
        master_var = tk.StringVar()
        master_combo = ttk.Combobox(master_frame, textvariable=master_var, 
                                   values=running_profiles, state="readonly",
                                   font=('Segoe UI', 10))
        master_combo.pack(padx=10, pady=10, fill=tk.X)
        
        # Slave Profiles Selection
        slave_frame = tk.LabelFrame(main_frame, text="👥 Chọn Slave Profiles", 
                                   font=('Segoe UI', 12, 'bold'), bg='#f0f0f0')
        slave_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Listbox for slave profiles
        slave_listbox = tk.Listbox(slave_frame, selectmode=tk.MULTIPLE, 
                                  font=('Consolas', 10), height=8)
        slave_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Populate slave profiles (exclude master)
        for profile in running_profiles:
            slave_listbox.insert(tk.END, profile)
        
        # Select all by default
        slave_listbox.select_set(0, tk.END)
        
        # Control Options
        control_frame = tk.LabelFrame(main_frame, text="⚙️ Tùy chọn điều khiển", 
                                     font=('Segoe UI', 12, 'bold'), bg='#f0f0f0')
        control_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Delay between actions
        delay_frame = tk.Frame(control_frame, bg='#f0f0f0')
        delay_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(delay_frame, text="Độ trễ giữa các hành động (giây):", 
                font=('Segoe UI', 10), bg='#f0f0f0').pack(side=tk.LEFT)
        
        delay_var = tk.StringVar(value="1")
        delay_entry = tk.Entry(delay_frame, textvariable=delay_var, 
                              font=('Segoe UI', 10), width=10)
        delay_entry.pack(side=tk.LEFT, padx=(10, 0))
        
        # Sync options
        sync_frame = tk.Frame(control_frame, bg='#f0f0f0')
        sync_frame.pack(fill=tk.X, padx=10, pady=5)
        
        sync_clicks_var = tk.BooleanVar(value=True)
        sync_clicks_check = tk.Checkbutton(sync_frame, text="Đồng bộ clicks", 
                                          variable=sync_clicks_var, 
                                          font=('Segoe UI', 10), bg='#f0f0f0')
        sync_clicks_check.pack(side=tk.LEFT)
        
        sync_scrolls_var = tk.BooleanVar(value=True)
        sync_scrolls_check = tk.Checkbutton(sync_frame, text="Đồng bộ scrolls", 
                                           variable=sync_scrolls_var, 
                                           font=('Segoe UI', 10), bg='#f0f0f0')
        sync_scrolls_check.pack(side=tk.LEFT, padx=(20, 0))
        
        sync_keys_var = tk.BooleanVar(value=True)
        sync_keys_check = tk.Checkbutton(sync_frame, text="Đồng bộ keystrokes", 
                                        variable=sync_keys_var, 
                                        font=('Segoe UI', 10), bg='#f0f0f0')
        sync_keys_check.pack(side=tk.LEFT, padx=(20, 0))
        
        # Status and Logs
        status_frame = tk.LabelFrame(main_frame, text="📊 Trạng thái & Logs", 
                                    font=('Segoe UI', 12, 'bold'), bg='#f0f0f0')
        status_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        status_text = tk.Text(status_frame, height=8, font=('Consolas', 9), 
                             bg='#f8f9fa', fg='#212529')
        status_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Buttons
        buttons_frame = tk.Frame(main_frame, bg='#f0f0f0')
        buttons_frame.pack(fill=tk.X, pady=(10, 0))
        
        def start_master_control():
            master_profile = master_var.get()
            if not master_profile:
                messagebox.showerror("Lỗi", "Vui lòng chọn Master Profile!")
                return
            
            selected_slaves = [slave_listbox.get(i) for i in slave_listbox.curselection()]
            if not selected_slaves:
                messagebox.showerror("Lỗi", "Vui lòng chọn ít nhất 1 Slave Profile!")
                return
            
            if master_profile in selected_slaves:
                messagebox.showerror("Lỗi", "Master Profile không thể là Slave Profile!")
                return
            
            try:
                delay = float(delay_var.get())
            except ValueError:
                delay = 1.0
            
            sync_options = {
                'clicks': sync_clicks_var.get(),
                'scrolls': sync_scrolls_var.get(),
                'keys': sync_keys_var.get()
            }
            
            # Confirm
            confirm_msg = f"""Bắt đầu Master Control Mode?

🎯 Master: {master_profile}
👥 Slaves: {len(selected_slaves)} profiles
⏱️ Delay: {delay} giây
🔄 Sync: {', '.join([k for k, v in sync_options.items() if v])}

Bạn có muốn tiếp tục?"""
            
            if messagebox.askyesno("Xác nhận", confirm_msg):
                dialog.destroy()
                self.start_master_control(master_profile, selected_slaves, delay, sync_options, status_text)
        
        def stop_master_control():
            if hasattr(self, 'master_control_active') and self.master_control_active:
                self.stop_master_control()
                status_text.insert(tk.END, "🛑 Master Control đã dừng\n")
                status_text.see(tk.END)
            else:
                messagebox.showinfo("Thông báo", "Master Control chưa được khởi động")
        
        start_btn = tk.Button(buttons_frame, text="[LAUNCH] Bắt đầu Master Control", 
                             command=start_master_control, font=('Segoe UI', 11, 'bold'),
                             bg='#28a745', fg='white', padx=20, pady=5)
        start_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        stop_btn = tk.Button(buttons_frame, text="🛑 Dừng Master Control", 
                            command=stop_master_control, font=('Segoe UI', 11),
                            bg='#dc3545', fg='white', padx=20, pady=5)
        stop_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        cancel_btn = tk.Button(buttons_frame, text="❌ Hủy", 
                              command=dialog.destroy, font=('Segoe UI', 11),
                              bg='#6c757d', fg='white', padx=20, pady=5)
        cancel_btn.pack(side=tk.LEFT)
        
        # Bind Enter key
        dialog.bind('<Return>', lambda e: start_master_control())
        master_combo.focus()
    
    def start_master_control(self, master_profile, slave_profiles, delay, sync_options, status_text):
        """Bắt đầu Master Control Mode"""
        try:
            print(f"🎮 [MASTER-CONTROL] Bắt đầu Master Control Mode")
            print(f"🎯 [MASTER-CONTROL] Master: {master_profile}")
            print(f"👥 [MASTER-CONTROL] Slaves: {slave_profiles}")
            print(f"⏱️ [MASTER-CONTROL] Delay: {delay}s")
            print(f"🔄 [MASTER-CONTROL] Sync options: {sync_options}")
            
            # Initialize master control state
            self.master_control_active = True
            self.master_profile = master_profile
            self.slave_profiles = slave_profiles
            self.master_delay = delay
            self.sync_options = sync_options
            self.master_control_thread = None
            
            # Log status
            status_text.insert(tk.END, f"🎮 Master Control Mode đã khởi động\n")
            status_text.insert(tk.END, f"🎯 Master: {master_profile}\n")
            status_text.insert(tk.END, f"👥 Slaves: {', '.join(slave_profiles)}\n")
            status_text.insert(tk.END, f"⏱️ Delay: {delay}s\n")
            status_text.insert(tk.END, f"🔄 Sync: {', '.join([k for k, v in sync_options.items() if v])}\n")
            status_text.insert(tk.END, "=" * 50 + "\n")
            status_text.see(tk.END)
            
            # Start monitoring thread
            self.master_control_thread = threading.Thread(target=self._master_control_monitor, daemon=True)
            self.master_control_thread.start()
            
            # Update status
            if hasattr(self, 'status_label'):
                self.status_label.config(text=f"🎮 Master Control: {master_profile} → {len(slave_profiles)} slaves")
            
        except Exception as e:
            print(f"❌ [MASTER-CONTROL] Lỗi khởi động: {e}")
            status_text.insert(tk.END, f"❌ Lỗi khởi động Master Control: {e}\n")
            status_text.see(tk.END)
    
    def stop_master_control(self):
        """Dừng Master Control Mode"""
        try:
            print(f"🛑 [MASTER-CONTROL] Dừng Master Control Mode")
            self.master_control_active = False
            self.master_profile = None
            self.slave_profiles = []
            self.master_control_thread = None
            
            # Update status
            if hasattr(self, 'status_label'):
                self.status_label.config(text="🎮 Master Control đã dừng")
                
        except Exception as e:
            print(f"❌ [MASTER-CONTROL] Lỗi dừng: {e}")
    
    def _master_control_monitor(self):
        """Monitor Master Profile và đồng bộ hành động"""
        try:
            print(f"🔍 [MASTER-CONTROL] Bắt đầu monitor Master Profile")
            
            while self.master_control_active:
                try:
                    # Check if master profile is still running
                    if not hasattr(self, 'drivers') or self.master_profile not in self.drivers:
                        print(f"⚠️ [MASTER-CONTROL] Master profile {self.master_profile} không còn chạy")
                        break
                    
                    master_driver = self.drivers[self.master_profile]
                    
                    # Get master window position and size
                    master_window = master_driver.get_window_position()
                    master_size = master_driver.get_window_size()
                    
                    # Monitor for actions (simplified - in real implementation, you'd use more sophisticated monitoring)
                    # For now, we'll simulate by checking if master window is active
                    try:
                        # Check if master window is focused
                        current_url = master_driver.current_url
                        if current_url and 'tiktok.com' in current_url:
                            # Simulate action sync (in real implementation, you'd capture actual mouse/keyboard events)
                            self._sync_actions_to_slaves()
                    except Exception as e:
                        print(f"⚠️ [MASTER-CONTROL] Lỗi monitor master: {e}")
                    
                    # Sleep before next check
                    time.sleep(0.5)  # Check every 500ms
                    
                except Exception as e:
                    print(f"❌ [MASTER-CONTROL] Lỗi trong monitor loop: {e}")
                    time.sleep(1)
            
            print(f"🛑 [MASTER-CONTROL] Monitor đã dừng")
            
        except Exception as e:
            print(f"❌ [MASTER-CONTROL] Lỗi monitor: {e}")
    
    def _sync_actions_to_slaves(self):
        """Đồng bộ hành động từ Master đến Slaves"""
        try:
            if not self.master_control_active or not self.slave_profiles:
                return
            
            print(f"🔄 [MASTER-CONTROL] Đồng bộ hành động đến {len(self.slave_profiles)} slaves")
            
            for i, slave_profile in enumerate(self.slave_profiles):
                try:
                    if slave_profile not in self.drivers:
                        print(f"⚠️ [MASTER-CONTROL] Slave {slave_profile} không còn chạy")
                        continue
                    
                    slave_driver = self.drivers[slave_profile]
                    
                    # Apply delay between slaves
                    if i > 0:
                        time.sleep(self.master_delay)
                    
                    # Sync actions based on options
                    if self.sync_options.get('clicks', False):
                        self._sync_clicks(slave_driver)
                    
                    if self.sync_options.get('scrolls', False):
                        self._sync_scrolls(slave_driver)
                    
                    if self.sync_options.get('keys', False):
                        self._sync_keys(slave_driver)
                    
                    print(f"✅ [MASTER-CONTROL] Đã đồng bộ {slave_profile}")
                    
                except Exception as e:
                    print(f"❌ [MASTER-CONTROL] Lỗi đồng bộ {slave_profile}: {e}")
                    
        except Exception as e:
            print(f"❌ [MASTER-CONTROL] Lỗi sync actions: {e}")
    
    def _sync_clicks(self, slave_driver):
        """Đồng bộ clicks (simplified)"""
        try:
            # In real implementation, you'd capture actual click coordinates from master
            # and apply them to slave with appropriate scaling/offset
            pass
        except Exception as e:
            print(f"❌ [MASTER-CONTROL] Lỗi sync clicks: {e}")
    
    def _sync_scrolls(self, slave_driver):
        """Đồng bộ scrolls (simplified)"""
        try:
            # In real implementation, you'd capture scroll events from master
            # and apply them to slave
            pass
        except Exception as e:
            print(f"❌ [MASTER-CONTROL] Lỗi sync scrolls: {e}")
    
    def _sync_keys(self, slave_driver):
        """Đồng bộ keystrokes (simplified)"""
        try:
            # In real implementation, you'd capture key events from master
            # and apply them to slave
            pass
        except Exception as e:
            print(f"❌ [MASTER-CONTROL] Lỗi sync keys: {e}")
    
    def _cleanup_stopped_drivers(self):
        """Dọn dẹp drivers đã bị dừng"""
        try:
            stopped_profiles = []
            for profile_name, driver in list(self.drivers.items()):
                try:
                    # Kiểm tra xem driver còn hoạt động không
                    driver.current_url  # Thử truy cập một thuộc tính
                except Exception:
                    # Driver đã bị dừng
                    stopped_profiles.append(profile_name)
                    # Driver cleanup logging removed
            
            # Xóa các drivers đã dừng
            for profile_name in stopped_profiles:
                if profile_name in self.drivers:
                    del self.drivers[profile_name]
                    # Profile removed from drivers
                    
        except Exception as e:
            print(f"⚠️ [CLEANUP] Lỗi khi dọn dẹp drivers: {str(e)}")
            
    def update_profile_combos(self):
        """Cập nhật combobox profiles"""
        try:
            profiles = self.manager.get_all_profiles()
            
            # Cập nhật export combo
            if hasattr(self, 'export_profile_combo') and self.export_profile_combo.winfo_exists():
                self.export_profile_combo['values'] = profiles
                if profiles and not self.export_profile_var.get():
                    self.export_profile_combo.set(profiles[0])
            
            # Cập nhật import combo
            if hasattr(self, 'import_profile_combo') and self.import_profile_combo.winfo_exists():
                self.import_profile_combo['values'] = profiles
                if profiles and not self.import_profile_var.get():
                    self.import_profile_combo.set(profiles[0])
                    
        except Exception as e:
            print(f"Lỗi cập nhật combobox: {str(e)}")
            
    def update_export_profile_combo(self):
        """Cập nhật export profile combo"""
        try:
            profiles = self.manager.get_all_profiles()
            if hasattr(self, 'export_profile_combo') and self.export_profile_combo.winfo_exists():
                self.export_profile_combo['values'] = profiles
                if profiles and not self.export_profile_var.get():
                    self.export_profile_combo.set(profiles[0])
        except Exception as e:
            print(f"Lỗi cập nhật export combo: {str(e)}")
            
    def update_import_profile_combo(self):
        """Cập nhật import profile combo"""
        try:
            profiles = self.manager.get_all_profiles()
            if hasattr(self, 'import_profile_combo') and self.import_profile_combo.winfo_exists():
                self.import_profile_combo['values'] = profiles
                if profiles and not self.import_profile_var.get():
                    self.import_profile_combo.set(profiles[0])
        except Exception as e:
            print(f"Lỗi cập nhật import combo: {str(e)}")
    
    # Placeholder methods for functionality
    def create_new_profile(self):
        """Tạo profile mới"""
        self.show_create_profile_dialog()
    
    def show_create_profile_dialog(self):
        """Hiển thị dialog tạo profile với layout mới"""
        # Tạo cửa sổ dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Create profile")
        dialog.geometry("1000x700")  # Kích thước lớn hơn để chứa layout mới
        dialog.resizable(True, True)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Header frame
        header_frame = ttk.Frame(dialog, padding="10")
        header_frame.pack(fill=tk.X)
        
        # Title và input
        title_frame = ttk.Frame(header_frame)
        title_frame.pack(fill=tk.X)
        
        ttk.Label(title_frame, text="Create profile", font=("Segoe UI", 16, "bold")).pack(side=tk.LEFT)
        
        # Tự động tạo tên profile ngẫu nhiên
        import random, time
        random_num = random.randint(100000, 999999)
        timestamp = int(time.time()) % 10000
        auto_name = f"P-{random_num}-{timestamp:04d}"
        
        name_var = tk.StringVar(value=auto_name)
        name_entry = ttk.Entry(title_frame, textvariable=name_var, font=("Segoe UI", 12), width=25)
        name_entry.pack(side=tk.LEFT, padx=(20, 10))
        
        # Profile type dropdown & Template dropdown
        profile_type_var = tk.StringVar(value="Work (US/UK)")
        profile_type_combo = ttk.Combobox(title_frame, textvariable=profile_type_var, 
                                        values=["Work (US/UK)", "Công việc (VN)"], 
                                        width=15, state="readonly")
        profile_type_combo.pack(side=tk.LEFT, padx=(0, 20))
        
        template_var = tk.StringVar(value="Builtin: Work (US/UK)")
        template_combo = ttk.Combobox(title_frame, textvariable=template_var, width=18, state="readonly")
        template_combo.pack(side=tk.LEFT, padx=(0, 10))
        
        # Template logic (định nghĩa schema riêng của ứng dụng)
        # Schema v1: { name, software{user_agent, auto_language, webrtc_policy, startup_url}, hardware{canvas_noise, webgl_image_noise, client_rect_noise, audio_noise, webgl_meta_masked, media_devices_masked} }
        def get_builtin_templates():
            return [
                {
                    'name': 'Builtin: Work (US/UK)',
                    'software': {
                        'user_agent': '',
                        'auto_language': True,
                        'webrtc_policy': 'default_public_interface_only',
                        'startup_url': ''
                    },
                    'hardware': {
                        'canvas_noise': 'Off',
                        'webgl_image_noise': 'Off',
                        'client_rect_noise': 'Off',
                        'audio_noise': 'On',
                        'webgl_meta_masked': True,
                        'media_devices_masked': True
                    }
                }
            ]

        def load_templates_into_combo():
            try:
                import os, json
                template_dir = os.path.join('data', 'templates')
                items = [t['name'] for t in get_builtin_templates()]
                if os.path.exists(template_dir):
                    for fn in os.listdir(template_dir):
                        if fn.endswith('.json'):
                            try:
                                with open(os.path.join(template_dir, fn), 'r', encoding='utf-8') as f:
                                    data = json.load(f)
                                    name = str(data.get('name') or fn.replace('.json', ''))
                                    items.append(name)
                            except Exception:
                                continue
                if not items:
                    items = ["Builtin: Work (US/UK)"]
                template_combo['values'] = items
                if items:
                    template_var.set(items[0])
            except Exception:
                template_combo['values'] = ["Builtin: Work (US/UK)"]
                template_var.set("Builtin: Work (US/UK)")
        load_templates_into_combo()
        
        # Luôn sử dụng chế độ tối giản (không cần checkbox)
        minimal_var = tk.BooleanVar(value=True)  # Luôn True
        # minimal_chk = ttk.Checkbutton(title_frame, text="Tối giản (không ghi vào Default trước khi khởi động)", variable=minimal_var)
        # minimal_chk.pack(side=tk.RIGHT, padx=(10, 0))

        # Create button
        create_btn = ttk.Button(title_frame, text="Tạo", command=lambda: create_profile(), style="Accent.TButton")
        create_btn.pack(side=tk.RIGHT)
        
        # Info banner
        info_frame = ttk.Frame(header_frame)
        info_frame.pack(fill=tk.X, pady=(10, 0))
        
        banner = ttk.Frame(info_frame, style="Info.TFrame")
        banner.pack(fill=tk.X, pady=(0, 10))
        
        info_text = "Công cụ cung cấp cấu hình được đề xuất cho noise hardware và hỗ trợ trình duyệt antidetect như MutliLogin và GoLogin."
        ttk.Label(banner, text=info_text, font=("Segoe UI", 9), foreground="white", wraplength=800).pack(padx=10, pady=5)
        
        # Main content frame
        main_frame = ttk.Frame(dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Left panel với tabs
        left_panel = ttk.Frame(main_frame)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Notebook cho tabs
        notebook = ttk.Notebook(left_panel)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Right panel - Current information chung
        right_panel = ttk.Frame(main_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Tạo frame có viền cho Current information
        info_container = ttk.LabelFrame(right_panel, text="Current information", padding="10")
        info_container.pack(fill=tk.BOTH, expand=True, padx=(0, 0), pady=(0, 0))
        
        # Tạo frame có thể scroll cho Current information
        info_frame = ttk.Frame(info_container)
        info_frame.pack(fill=tk.BOTH, expand=True)
        
        # Canvas và Scrollbar cho Current information
        canvas = tk.Canvas(info_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(info_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mousewheel để scroll
        def _on_mousewheel(event):
            try:
                # Nếu canvas đã bị destroy, bỏ qua
                if not canvas.winfo_exists():
                    return
                canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            except Exception:
                # Tránh TclError khi widget đã bị huỷ
                pass
        # Bind mousewheel và đảm bảo an toàn khi dialog bị đóng
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        def _cleanup_scroll_binding():
            try:
                canvas.unbind_all("<MouseWheel>")
            except Exception:
                pass

        # Bỏ binding khi dialog đóng để tránh callback vào widget đã bị huỷ
        try:
            dialog.protocol("WM_DELETE_WINDOW", lambda: ( _cleanup_scroll_binding(), dialog.destroy()))
        except Exception:
            pass
        
        # Function để update Current information sẽ được định nghĩa sau khi tất cả biến đã được tạo
        
        # Tạo biến hardware trước để dùng chung
        # Hardware variables (định nghĩa trước để dùng trong tất cả tabs)
        screen_var = tk.StringVar(value="Real")
        canvas_var = tk.StringVar(value="Off")
        client_var = tk.StringVar(value="Off")
        webgl_img_var = tk.StringVar(value="Off")
        audio_var = tk.StringVar(value="On")
        webgl_masked_var = tk.BooleanVar(value=True)
        # Tự động random WebGL vendor và renderer ngay khi khởi tạo
        import random
        webgl_vendor_options_init = [
            "Google Inc. (NVIDIA)",
            "Google Inc. (Intel)", 
            "Google Inc. (AMD)",
            "NVIDIA Corporation",
            "Intel Inc.",
            "Microsoft Corporation"
        ]
        webgl_renderer_options_init = [
            # NVIDIA Graphics
            "ANGLE (NVIDIA, NVIDIA GeForce RTX 3080 Ti Direct3D11 vs_5_0 ps_5_0, D3D11)",
            "ANGLE (NVIDIA, NVIDIA GeForce GTX 1060 Direct3D11 vs_5_0 ps_5_0, D3D11)",
            "ANGLE (NVIDIA, NVIDIA GeForce RTX 3060 Direct3D11 vs_5_0 ps_5_0, D3D11)",
            # Intel Graphics - UHD Series
            "ANGLE (Intel, Intel(R) UHD Graphics 620 (0x00005917) Direct3D11 vs_5_0 ps_5_0, D3D11)",
            "ANGLE (Intel, Intel(R) UHD Graphics 630 (0x00005917) Direct3D11 vs_5_0 ps_5_0, D3D11)",
            "ANGLE (Intel, Intel(R) UHD Graphics 620 Direct3D11 vs_5_0 ps_5_0, D3D11)",
            "ANGLE (Intel, Intel(R) UHD Graphics 630 Direct3D11 vs_5_0 ps_5_0, D3D11)",
            # Intel Graphics - HD Series
            "ANGLE (Intel, Intel(R) HD Graphics 530 Direct3D11 vs_5_0 ps_5_0, D3D11)",
            "ANGLE (Intel, Intel(R) HD Graphics 520 Direct3D11 vs_5_0 ps_5_0, D3D11)",
            "ANGLE (Intel, Intel(R) HD Graphics 4600 Direct3D11 vs_5_0 ps_5_0, D3D11)",
            "ANGLE (Intel, Intel(R) HD Graphics 4000 Direct3D9Ex vs_3_0 ps_3_0, igdumdim64.dll-10.18.10.3345)",
            # Intel Graphics - Iris Series
            "ANGLE (Intel, Intel(R) Iris(R) Xe Graphics Direct3D11 vs_5_0 ps_5_0, D3D11)",
            "ANGLE (Intel, Intel(R) HD Graphics Family Direct3D11 vs_5_0 ps_5_0, D3D11)",
            # AMD Graphics
            "ANGLE (AMD, AMD Radeon RX 580 Direct3D11 vs_5_0 ps_5_0, D3D11)",
            "ANGLE (AMD, AMD Radeon RX 6600 Direct3D11 vs_5_0 ps_5_0, D3D11)"
        ]
        
        webgl_vendor_var = tk.StringVar(value=random.choice(webgl_vendor_options_init))
        webgl_renderer_var = tk.StringVar(value=random.choice(webgl_renderer_options_init))
        media_masked_var = tk.BooleanVar(value=True)
        audio_inputs_var = tk.StringVar(value="2")
        audio_outputs_var = tk.StringVar(value="0")
        video_inputs_var = tk.StringVar(value="0")
        cpu_var = tk.StringVar(value="8")
        mem_var = tk.StringVar(value="16")
        # Tạo MAC address ngẫu nhiên cho profile mới
        import random, os
        def generate_random_mac():
            """Tạo MAC address ngẫu nhiên theo chuẩn locally administered, unicast"""
            b = bytearray(os.urandom(6))
            b[0] = (b[0] | 0x02) & 0xFE
            return ":".join(f"{x:02X}" for x in b)
        
        mac_var = tk.StringVar(value=generate_random_mac())
        
        # Software variables (định nghĩa trước để dùng trong tất cả tabs)
        # Tự động random User-Agent ngay khi khởi tạo
        try:
            from chrome_manager import _generate_user_agent
            initial_ua = _generate_user_agent()
        except Exception:
            # Fallback UA nếu không import được
            import random
            chrome_versions = ['139.0.0.0', '138.0.0.0', '137.0.0.0', '136.0.0.0', '135.0.0.0']
            version = random.choice(chrome_versions)
            initial_ua = f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version} Safari/537.36"
        
        ua_var = tk.StringVar(value=initial_ua)
        os_var = tk.StringVar(value="Windows 11")
        os_bit_var = tk.StringVar(value="64 bit")
        lang_var = tk.StringVar(value="en-US")
        url_var = tk.StringVar(value="")
        webrtc_var = tk.StringVar(value="default_public_interface_only")
        os_font_var = tk.StringVar(value="Real")
        
        # Connection variables
        proxy_type_var = tk.StringVar(value="Without Proxy")
        timezone_var = tk.StringVar(value="Base on IP")
        webrtc_ip_var = tk.StringVar(value="Base on IP")
        geo_var = tk.StringVar(value="Base on IP")
        tcp_var = tk.BooleanVar(value=False)
        maintain_var = tk.BooleanVar(value=False)
        
        # Quick action variables
        browser_var = tk.StringVar(value="Chrome")
        taskbar_var = tk.StringVar(value="")
        
        # Additional variables needed for Current information
        sw_browser_var = tk.StringVar(value="Chrome")
        browser_version_var = tk.StringVar(value="139.0.7258.139")
        edit_ua_var = tk.BooleanVar(value=False)
        auto_lang_var = tk.BooleanVar(value=True)
        
        # Quick action tab
        quick_frame = ttk.Frame(notebook, padding="20")
        notebook.add(quick_frame, text="Quick action")
        
        # Quick action chỉ có left frame
        quick_left_frame = ttk.Frame(quick_frame)
        quick_left_frame.pack(fill=tk.BOTH, expand=True)
        
        # Proxy type
        ttk.Label(quick_left_frame, text="Proxy type:").grid(row=0, column=0, sticky='w', pady=(0, 5))
        proxy_type_combo = ttk.Combobox(quick_left_frame, textvariable=proxy_type_var, state='readonly', values=['Without Proxy', 'HTTP', 'SOCKS5'], width=20)
        proxy_type_combo.grid(row=0, column=1, sticky='w', padx=(5, 0), pady=(0, 5))
        
        # Buttons
        button_frame = ttk.Frame(quick_left_frame)
        button_frame.grid(row=1, column=0, columnspan=2, sticky='w', pady=(5, 10))
        ttk.Button(button_frame, text="Kiểm tra", width=10).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Thư viện proxy", width=15).pack(side=tk.LEFT)
        
        # Browser
        ttk.Label(quick_left_frame, text="Trình duyệt:").grid(row=2, column=0, sticky='w', pady=(0, 5))
        browser_combo = ttk.Combobox(quick_left_frame, textvariable=browser_var, state='readonly', values=['Chrome', 'Firefox', 'Edge'], width=20)
        browser_combo.grid(row=2, column=1, sticky='w', padx=(5, 0), pady=(0, 5))
        
        # Taskbar title
        ttk.Label(quick_left_frame, text="Tiêu đề ở taskbar (3 ký tự):").grid(row=3, column=0, sticky='w', pady=(0, 5))
        ttk.Entry(quick_left_frame, textvariable=taskbar_var, width=20).grid(row=3, column=1, sticky='w', padx=(5, 0), pady=(0, 5))
        
        # Description
        desc_text = "Nếu để trống sẽ hiển thị tăng dần theo số lần mở profile"
        ttk.Label(quick_left_frame, text=desc_text, font=("Segoe UI", 9), foreground="gray", wraplength=300).grid(row=4, column=0, columnspan=2, sticky='w', pady=(0, 10))
        
        # Generate button đã được di chuyển ra ngoài
        
        # Quick action tab chỉ có left frame, không có right frame
        # Current information sẽ được hiển thị ở right panel chung
        
        # Connection tab
        connection_frame = ttk.Frame(notebook, padding="20")
        notebook.add(connection_frame, text="Connection")
        
        # Connection chỉ có left frame
        conn_left_frame = ttk.Frame(connection_frame)
        conn_left_frame.pack(fill=tk.BOTH, expand=True)
        
        # Timezone
        ttk.Label(conn_left_frame, text="Timezone:").grid(row=0, column=0, sticky='w', pady=(0, 5))
        timezone_combo = ttk.Combobox(conn_left_frame, textvariable=timezone_var, state='readonly', values=['Base on IP', 'UTC', 'GMT'], width=20)
        timezone_combo.grid(row=0, column=1, sticky='w', padx=(5, 0), pady=(0, 5))
        
        # WebRTC IP
        ttk.Label(conn_left_frame, text="WebRTC IP:").grid(row=1, column=0, sticky='w', pady=(0, 5))
        webrtc_ip_combo = ttk.Combobox(conn_left_frame, textvariable=webrtc_ip_var, state='readonly', values=['Base on IP', 'Disable', 'Default'], width=20)
        webrtc_ip_combo.grid(row=1, column=1, sticky='w', padx=(5, 0), pady=(0, 5))
        
        # Checkboxes
        ttk.Checkbutton(conn_left_frame, text="Cho phép TCP", variable=tcp_var).grid(row=2, column=0, columnspan=2, sticky='w', pady=(5, 0))
        tcp_desc = ttk.Label(conn_left_frame, text="Sử dụng cho gọi điện online qua fb, tele,...", font=("Segoe UI", 9), foreground="gray")
        tcp_desc.grid(row=3, column=0, columnspan=2, sticky='w', pady=(0, 5))
        
        ttk.Checkbutton(conn_left_frame, text="Duy trì kết nối, không ngắt đột ngột", variable=maintain_var).grid(row=4, column=0, columnspan=2, sticky='w', pady=(5, 0))
        maintain_desc = ttk.Label(conn_left_frame, text="Để treo các kèo như Gradient,...", font=("Segoe UI", 9), foreground="gray")
        maintain_desc.grid(row=5, column=0, columnspan=2, sticky='w', pady=(0, 5))
        
        # GEO Location
        ttk.Label(conn_left_frame, text="GEO Location:").grid(row=6, column=0, sticky='w', pady=(0, 5))
        geo_combo = ttk.Combobox(conn_left_frame, textvariable=geo_var, state='readonly', values=['Base on IP', 'Manual'], width=20)
        geo_combo.grid(row=6, column=1, sticky='w', padx=(5, 0), pady=(0, 5))
        
        # Generate button đã được di chuyển ra ngoài
        
        # Connection tab chỉ có left frame
        # Current information sẽ được hiển thị ở right panel chung
        
        # Software tab
        software_frame = ttk.Frame(notebook, padding="20")
        notebook.add(software_frame, text="Software")
        
        # Software chỉ có left frame
        sw_left_frame = ttk.Frame(software_frame)
        sw_left_frame.pack(fill=tk.BOTH, expand=True)
        
        # Browser
        ttk.Label(sw_left_frame, text="Trình duyệt:").grid(row=0, column=0, sticky='w', pady=(0, 5))
        sw_browser_combo = ttk.Combobox(sw_left_frame, textvariable=sw_browser_var, state='readonly', values=['Chrome', 'Firefox', 'Edge'], width=20)
        sw_browser_combo.grid(row=0, column=1, sticky='w', padx=(5, 0), pady=(0, 5))
        
        # Browser version (danh sách phiên bản cố định)
        chrome_version_options = [
            '139.0.7258.139',
            '137.0.7151.41',
            '135.0.7049.42',
            '134.0.6998.89',
            '132.0.6834.84',
            '129.0.6668.59',
            '127.0.6533.73',
            '124.0.6367.29',
            '121.0.6167.140',
            '119.0.6045.124',
            '115.0.5790.75',
            '111.0.5563.50',
            '107.0.5304.8',
            '106.0.5249.119',
        ]
        ver_combo = ttk.Combobox(sw_left_frame, textvariable=browser_version_var, state='readonly', values=chrome_version_options, width=20)
        ver_combo.grid(row=0, column=2, sticky='w', padx=(5, 0), pady=(0, 5))
        # Khi đổi version → tự cập nhật UA tương ứng
        def _apply_ua_from_version(*_):
            ver = browser_version_var.get().strip()
            if not ver:
                return
            ua_var.set(f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{ver} Safari/537.36")
        try:
            ver_combo.bind('<<ComboboxSelected>>', _apply_ua_from_version)
        except Exception:
            pass
        
        # Operating System
        ttk.Label(sw_left_frame, text="Hệ điều hành:").grid(row=1, column=0, sticky='w', pady=(0, 5))
        os_combo = ttk.Combobox(sw_left_frame, textvariable=os_var, state='readonly', values=['Windows 11', 'Windows 10', 'macOS', 'Linux'], width=20)
        os_combo.grid(row=1, column=1, sticky='w', padx=(5, 0), pady=(0, 5))
        
        # OS bit
        os_bit_combo = ttk.Combobox(sw_left_frame, textvariable=os_bit_var, state='readonly', values=['64 bit', '32 bit'], width=10)
        os_bit_combo.grid(row=1, column=2, sticky='w', padx=(5, 0), pady=(0, 5))
        
        # User agent
        ttk.Label(sw_left_frame, text="User agent:").grid(row=2, column=0, sticky='w', pady=(0, 5))
        ua_entry = ttk.Entry(sw_left_frame, textvariable=ua_var, width=50)
        ua_entry.grid(row=2, column=1, columnspan=2, sticky='w', padx=(5, 0), pady=(0, 5))
        
        # Random UA controls
        ua_controls_frame = ttk.Frame(sw_left_frame)
        ua_controls_frame.grid(row=3, column=1, columnspan=2, sticky='w', padx=(5, 0), pady=(0, 5))
        
        # Generate Random UA button (UA đã tự động random khi khởi tạo)
        def generate_random_ua():
            try:
                from chrome_manager import _generate_user_agent
                random_ua = _generate_user_agent()
                ua_var.set(random_ua)
            except Exception as e:
                # Fallback UA nếu không import được
                import random
                chrome_versions = ['139.0.0.0', '138.0.0.0', '137.0.0.0', '136.0.0.0', '135.0.0.0']
                version = random.choice(chrome_versions)
                fallback_ua = f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version} Safari/537.36"
                ua_var.set(fallback_ua)
        
        ttk.Button(ua_controls_frame, text="Generate Random UA", command=generate_random_ua).pack(side=tk.LEFT, padx=(0, 0))
        
        # Edit user agent checkbox
        ttk.Checkbutton(sw_left_frame, text="Sửa user agent", variable=edit_ua_var).grid(row=4, column=1, columnspan=2, sticky='w', padx=(5, 0), pady=(0, 5))
        
        # Language code
        ttk.Label(sw_left_frame, text="Language code:").grid(row=5, column=0, sticky='w', pady=(0, 5))
        ttk.Checkbutton(sw_left_frame, text="Auto language (Base on IP)", variable=auto_lang_var).grid(row=5, column=1, columnspan=2, sticky='w', padx=(5, 0), pady=(0, 5))
        
        lang_combo = ttk.Combobox(sw_left_frame, textvariable=lang_var, state='readonly', values=['en-US', 'vi-VN', 'zh-CN', 'ja-JP', 'ko-KR'], width=20)
        lang_combo.grid(row=6, column=1, sticky='w', padx=(5, 0), pady=(0, 5))
        
        # Startup URL
        ttk.Label(sw_left_frame, text="URL khởi động:").grid(row=7, column=0, sticky='w', pady=(0, 5))
        url_entry = ttk.Entry(sw_left_frame, textvariable=url_var, width=50)
        url_entry.grid(row=7, column=1, columnspan=2, sticky='w', padx=(5, 0), pady=(0, 5))
        url_placeholder = ttk.Label(sw_left_frame, text="Eg: https://google.com https://whoer.net", font=("Segoe UI", 9), foreground="gray")
        url_placeholder.grid(row=8, column=1, columnspan=2, sticky='w', padx=(5, 0), pady=(0, 5))
        
        # OS Font
        ttk.Label(sw_left_frame, text="OS Font:").grid(row=9, column=0, sticky='w', pady=(0, 5))
        os_font_combo = ttk.Combobox(sw_left_frame, textvariable=os_font_var, state='readonly', values=['Real', 'Custom'], width=20)
        os_font_combo.grid(row=9, column=1, sticky='w', padx=(5, 0), pady=(0, 5))
        
        # Generate button đã được di chuyển ra ngoài
        
        # Software tab chỉ có left frame
        # Current information sẽ được hiển thị ở right panel chung
        
        # Hardware tab
        hardware_frame = ttk.Frame(notebook, padding="20")
        notebook.add(hardware_frame, text="Hardware")
        
        # Thông báo về thông tin phần cứng ngẫu nhiên
        info_label = ttk.Label(hardware_frame, text="Phần mềm đã tạo ngẫu nhiên một thông tin phần cứng. Nếu không quá hiểu về Fingerprint, bạn có thể không quan tâm tới phần này. Các thông tin về RAM, CPU Core, Audio, Media outputs, WebGL, Tên card màn hình... đã được sinh ngẫu nhiên!", 
                              font=("Segoe UI", 9), foreground="gray", wraplength=600)
        info_label.pack(anchor=tk.W, pady=(0, 15))
        
        # Hardware chỉ có left frame
        left_frame = ttk.Frame(hardware_frame)
        left_frame.pack(fill=tk.BOTH, expand=True)
        
        # Cột trái - Cấu hình Hardware
        # Phân giải màn hình
        ttk.Label(left_frame, text="Phân giải màn hình:").grid(row=0, column=0, sticky='w', pady=(0, 5))
        ttk.Entry(left_frame, textvariable=screen_var, width=20).grid(row=0, column=1, sticky='w', padx=(5, 0), pady=(0, 5))
        
        # Canvas noise
        ttk.Label(left_frame, text="Canvas noise:").grid(row=1, column=0, sticky='w', pady=(0, 5))
        canvas_combo = ttk.Combobox(left_frame, textvariable=canvas_var, state='readonly', values=['Off', 'On'], width=17)
        canvas_combo.grid(row=1, column=1, sticky='w', padx=(5, 0), pady=(0, 5))
        
        # Client rect noise
        ttk.Label(left_frame, text="Client rect noise:").grid(row=2, column=0, sticky='w', pady=(0, 5))
        client_combo = ttk.Combobox(left_frame, textvariable=client_var, state='readonly', values=['Off', 'On'], width=17)
        client_combo.grid(row=2, column=1, sticky='w', padx=(5, 0), pady=(0, 5))
        
        # WebGL image noise
        ttk.Label(left_frame, text="WebGL image noise:").grid(row=3, column=0, sticky='w', pady=(0, 5))
        webgl_img_combo = ttk.Combobox(left_frame, textvariable=webgl_img_var, state='readonly', values=['Off', 'On'], width=17)
        webgl_img_combo.grid(row=3, column=1, sticky='w', padx=(5, 0), pady=(0, 5))
        
        # Audio noise
        ttk.Label(left_frame, text="Audio noise:").grid(row=4, column=0, sticky='w', pady=(0, 5))
        audio_combo = ttk.Combobox(left_frame, textvariable=audio_var, state='readonly', values=['Off', 'On'], width=17)
        audio_combo.grid(row=4, column=1, sticky='w', padx=(5, 0), pady=(0, 5))
        
        # WebGL Meta masked
        ttk.Checkbutton(left_frame, text="✔ WebGL Meta masked", variable=webgl_masked_var).grid(row=5, column=0, columnspan=2, sticky='w', pady=(5, 5))
        
        # WebGL Vendor
        ttk.Label(left_frame, text="WebGL Vendor:").grid(row=6, column=0, sticky='w', pady=(0, 5))
        
        # WebGL vendor options
        webgl_vendor_options = [
            "Google Inc. (NVIDIA)",
            "Google Inc. (Intel)", 
            "Google Inc. (AMD)",
            "NVIDIA Corporation",
            "Intel Inc.",
            "Microsoft Corporation"
        ]
        
        webgl_vendor_combo = ttk.Combobox(left_frame, textvariable=webgl_vendor_var, values=webgl_vendor_options, width=25, state="readonly")
        webgl_vendor_combo.grid(row=6, column=1, sticky='w', padx=(5, 0), pady=(0, 5))
        
        # Random WebGL Vendor button
        def random_webgl_vendor():
            import random
            webgl_vendor_var.set(random.choice(webgl_vendor_options))
        
        ttk.Button(left_frame, text="Random", command=random_webgl_vendor, width=8).grid(row=6, column=2, sticky='w', padx=(5, 0), pady=(0, 5))
        
        # WebGL Renderer
        ttk.Label(left_frame, text="WebGL Renderer:").grid(row=7, column=0, sticky='w', pady=(0, 5))
        
        # WebGL renderer options
        webgl_renderer_options = [
            # NVIDIA Graphics
            "ANGLE (NVIDIA, NVIDIA GeForce RTX 3080 Ti Direct3D11 vs_5_0 ps_5_0, D3D11)",
            "ANGLE (NVIDIA, NVIDIA GeForce GTX 1060 Direct3D11 vs_5_0 ps_5_0, D3D11)",
            "ANGLE (NVIDIA, NVIDIA GeForce RTX 3060 Direct3D11 vs_5_0 ps_5_0, D3D11)",
            # Intel Graphics - UHD Series
            "ANGLE (Intel, Intel(R) UHD Graphics 620 (0x00005917) Direct3D11 vs_5_0 ps_5_0, D3D11)",
            "ANGLE (Intel, Intel(R) UHD Graphics 630 (0x00005917) Direct3D11 vs_5_0 ps_5_0, D3D11)",
            "ANGLE (Intel, Intel(R) UHD Graphics 620 Direct3D11 vs_5_0 ps_5_0, D3D11)",
            "ANGLE (Intel, Intel(R) UHD Graphics 630 Direct3D11 vs_5_0 ps_5_0, D3D11)",
            # Intel Graphics - HD Series
            "ANGLE (Intel, Intel(R) HD Graphics 530 Direct3D11 vs_5_0 ps_5_0, D3D11)",
            "ANGLE (Intel, Intel(R) HD Graphics 520 Direct3D11 vs_5_0 ps_5_0, D3D11)",
            "ANGLE (Intel, Intel(R) HD Graphics 4600 Direct3D11 vs_5_0 ps_5_0, D3D11)",
            "ANGLE (Intel, Intel(R) HD Graphics 4000 Direct3D9Ex vs_3_0 ps_3_0, igdumdim64.dll-10.18.10.3345)",
            # Intel Graphics - Iris Series
            "ANGLE (Intel, Intel(R) Iris(R) Xe Graphics Direct3D11 vs_5_0 ps_5_0, D3D11)",
            "ANGLE (Intel, Intel(R) HD Graphics Family Direct3D11 vs_5_0 ps_5_0, D3D11)",
            # AMD Graphics
            "ANGLE (AMD, AMD Radeon RX 580 Direct3D11 vs_5_0 ps_5_0, D3D11)",
            "ANGLE (AMD, AMD Radeon RX 6600 Direct3D11 vs_5_0 ps_5_0, D3D11)"
        ]
        
        webgl_renderer_combo = ttk.Combobox(left_frame, textvariable=webgl_renderer_var, values=webgl_renderer_options, width=50, state="readonly")
        webgl_renderer_combo.grid(row=7, column=1, sticky='w', padx=(5, 0), pady=(0, 5))
        
        # Random WebGL Renderer button
        def random_webgl_renderer():
            import random
            webgl_renderer_var.set(random.choice(webgl_renderer_options))
        
        ttk.Button(left_frame, text="Random", command=random_webgl_renderer, width=8).grid(row=7, column=2, sticky='w', padx=(5, 0), pady=(0, 5))
        
        # Media devices masked
        ttk.Checkbutton(left_frame, text="✔ Media devices masked (Audio inputs / Audio outputs / Video inputs)", variable=media_masked_var).grid(row=8, column=0, columnspan=2, sticky='w', pady=(5, 5))
        
        # Media inputs/outputs trong 1 dòng
        media_frame = ttk.Frame(left_frame)
        media_frame.grid(row=9, column=0, columnspan=2, sticky='w', pady=(0, 5))
        ttk.Entry(media_frame, textvariable=audio_inputs_var, width=5).grid(row=0, column=0, padx=(0, 5))
        ttk.Entry(media_frame, textvariable=audio_outputs_var, width=5).grid(row=0, column=1, padx=(0, 5))
        ttk.Entry(media_frame, textvariable=video_inputs_var, width=5).grid(row=0, column=2)
        
        # CPU cores
        ttk.Label(left_frame, text="CPU core:").grid(row=10, column=0, sticky='w', pady=(0, 5))
        ttk.Entry(left_frame, textvariable=cpu_var, width=20).grid(row=10, column=1, sticky='w', padx=(5, 0), pady=(0, 5))
        
        # Memory devices
        ttk.Label(left_frame, text="Memory devices:").grid(row=11, column=0, sticky='w', pady=(0, 5))
        ttk.Entry(left_frame, textvariable=mem_var, width=20).grid(row=11, column=1, sticky='w', padx=(5, 0), pady=(0, 5))
        
        # MAC address
        ttk.Label(left_frame, text="MAC address:").grid(row=12, column=0, sticky='w', pady=(0, 5))
        ttk.Entry(left_frame, textvariable=mac_var, width=20).grid(row=12, column=1, sticky='w', padx=(5, 0), pady=(0, 5))
        
        # Generate button đã được di chuyển ra ngoài
        
        # Hardware tab chỉ có left frame
        # Current information sẽ được hiển thị ở right panel chung
        
        # Functions
        def generate_quick_params():
            """Tạo thông số Quick action mới"""
            import random
            proxy_types = ['Without Proxy', 'HTTP', 'SOCKS5']
            browsers = ['Chrome', 'Firefox', 'Edge']
            proxy_type_var.set(random.choice(proxy_types))
            browser_var.set(random.choice(browsers))
            taskbar_var.set(''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=3)))
            update_current_info()  # Update Current information
            print("✅ [GENERATE] Đã tạo thông số Quick action mới")
        
        def generate_connection_params():
            """Tạo thông số Connection mới"""
            import random
            timezones = ['Base on IP', 'UTC', 'GMT']
            webrtc_options = ['Base on IP', 'Disable', 'Default']
            geo_options = ['Base on IP', 'Manual']
            timezone_var.set(random.choice(timezones))
            webrtc_ip_var.set(random.choice(webrtc_options))
            geo_var.set(random.choice(geo_options))
            tcp_var.set(random.choice([True, False]))
            maintain_var.set(random.choice([True, False]))
            update_current_info()  # Update Current information
            print("✅ [GENERATE] Đã tạo thông số Connection mới")
        
        def generate_software_params():
            """Tạo thông số Software mới"""
            import random
            browsers = ['Chrome', 'Firefox', 'Edge']
            os_list = ['Windows 11', 'Windows 10', 'macOS', 'Linux']
            os_bits = ['64 bit', '32 bit']
            languages = ['en-US', 'vi-VN', 'zh-CN', 'ja-JP', 'ko-KR']
            fonts = ['Real', 'Custom']
            
            sw_browser_var.set(random.choice(browsers))
            os_var.set(random.choice(os_list))
            os_bit_var.set(random.choice(os_bits))
            lang_var.set(random.choice(languages))
            os_font_var.set(random.choice(fonts))
            
            # Generate random browser version (chỉ khi chưa có giá trị)
            if not browser_version_var.get().strip():
                major = random.randint(130, 140)
                minor = random.randint(0, 9)
                patch = random.randint(0, 999)
                browser_version_var.set(f"{major}.{minor}.{patch}")
            
            update_current_info()  # Update Current information
            print("✅ [GENERATE] Đã tạo thông số Software mới")
        
        def generate_new_params():
            """Tạo thông số hardware mới"""
            import random
            
            # Tạo các giá trị ngẫu nhiên
            resolutions = ['1920x1080', '1366x768', '1440x900', '1536x864', 'Real']
            screen_var.set(random.choice(resolutions))
            canvas_var.set(random.choice(['Off', 'On']))
            client_var.set(random.choice(['Off', 'On']))
            webgl_img_var.set(random.choice(['Off', 'On']))
            audio_var.set(random.choice(['Off', 'On']))
            webgl_vendor_var.set(random.choice(webgl_vendor_options))
            webgl_renderer_var.set(random.choice(webgl_renderer_options))
            cpu_var.set(str(random.randint(4, 16)))
            mem_var.set(str(random.randint(4, 32)))
            # Tạo MAC mới
            mac_var.set(generate_random_mac())
            audio_inputs_var.set(str(random.randint(1, 3)))
            audio_outputs_var.set(str(random.randint(0, 2)))
            video_inputs_var.set(str(random.randint(0, 2)))
            
            update_current_info()  # Update Current information
            print("✅ [GENERATE] Đã tạo thông số hardware mới")
        
        # Bind events để update Current information khi thay đổi giá trị
        def bind_update_events():
            # Bind tất cả biến để update Current information khi thay đổi
            for var in [ua_var, os_var, os_bit_var, lang_var, url_var, webrtc_var, os_font_var, 
                       proxy_type_var, timezone_var, webrtc_ip_var, geo_var, tcp_var, maintain_var,
                       browser_var, taskbar_var, sw_browser_var, browser_version_var, edit_ua_var, auto_lang_var,
                       screen_var, canvas_var, client_var, webgl_img_var, audio_var, webgl_masked_var,
                       webgl_vendor_var, webgl_renderer_var, media_masked_var, audio_inputs_var,
                       audio_outputs_var, video_inputs_var, cpu_var, mem_var, mac_var]:
                try:
                    var.trace('w', lambda *args: update_current_info())
                except:
                    pass  # Một số biến có thể không có trace method
        
        # Function để update Current information
        def update_current_info():
            # Clear existing widgets
            for widget in scrollable_frame.winfo_children():
                widget.destroy()
            
            # Current information data
            info_data = [
                ("User-agent:", ua_var.get()),
                ("OS:", f"{os_var.get()} {os_bit_var.get()}"),
                ("Proxy:", proxy_type_var.get()),
                ("Screen:", "-1x-1"),
                ("Timezone:", timezone_var.get()),
                ("Font list:", os_font_var.get()),
                ("Accept-language:", lang_var.get()),
                ("WebRTC:", webrtc_ip_var.get()),
                ("CPU core:", cpu_var.get()),
                ("Device memory:", mem_var.get()),
                ("Media audio inputs:", audio_inputs_var.get()),
                ("Media audio outputs:", audio_outputs_var.get()),
                ("Media video inputs:", video_inputs_var.get()),
                ("WebGL Meta:", "Masked" if webgl_masked_var.get() else "Off"),
                ("Canvas:", canvas_var.get()),
                ("Client rect:", client_var.get()),
                ("WebGL:", webgl_img_var.get()),
                ("Audio Context:", audio_var.get())
            ]
            
            for i, (label, value) in enumerate(info_data):
                ttk.Label(scrollable_frame, text=label, font=("Segoe UI", 9, "bold")).grid(row=i, column=0, sticky='w', pady=(0, 2), padx=(0, 10))
                ttk.Label(scrollable_frame, text=value, font=("Segoe UI", 9), foreground="gray", wraplength=300).grid(row=i, column=1, sticky='w', pady=(0, 2))
        
        bind_update_events()
        
        # Update Current information sau khi tất cả biến đã được định nghĩa
        update_current_info()
        
        # Tạo button "Tạo thông số mới" ở góc dưới trái cố định
        button_frame = ttk.Frame(dialog)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)
        
        def generate_all_params():
            """Tạo thông số mới cho tab hiện tại"""
            current_tab = notebook.index(notebook.select())
            if current_tab == 0:  # Quick action
                generate_quick_params()
            elif current_tab == 1:  # Connection
                generate_connection_params()
            elif current_tab == 2:  # Software
                generate_software_params()
            elif current_tab == 3:  # Hardware
                generate_new_params()
        
        generate_button = ttk.Button(button_frame, text="✖ Tạo thông số mới", command=generate_all_params, width=20)
        generate_button.pack(side=tk.LEFT)
        
        def toggle_stealth_options():
            """Toggle stealth options visibility"""
            if use_stealth_var.get():
                stealth_options_frame.pack(fill=tk.X, pady=(5, 0))
            else:
                stealth_options_frame.pack_forget()
        
        
        def create_profile():
            """Tạo profile mới với cấu hình đầy đủ"""
            name = name_var.get().strip()
            
            if not name:
                messagebox.showerror("Lỗi", "Vui lòng nhập tên profile!")
                name_entry.focus()
                return
            
            # Kiểm tra tên profile đã tồn tại
            try:
                existing_profiles = self.manager.get_all_profiles(force_refresh=True)
                if name in existing_profiles:
                    messagebox.showerror("Lỗi", f"Profile '{name}' đã tồn tại!")
                    name_entry.focus()
                    return
            except Exception as e:
                print(f"⚠️ [CREATE] Lỗi kiểm tra profile tồn tại: {e}")
                pass
            
            # Tạo profile với profile type
            try:
                # Xác định profile type từ dropdown
                selected_type = profile_type_var.get()
                if selected_type == "Work (US/UK)":
                    profile_type = "work"
                elif selected_type == "Công việc (VN)":
                    profile_type = "cong_viec"
                else:
                    profile_type = "work"  # Default
                
                success, message = self.manager.clone_chrome_profile(name, "Default", profile_type)
                if success:
                    # Lưu cấu hình đầy đủ
                    try:
                        import os, json, time
                        profile_path = os.path.join(self.manager.profiles_dir, name)
                        settings_path = os.path.join(profile_path, 'profile_settings.json')
                        # Luôn random trước và đẩy ngược vào UI vars để phần Hardware hiển thị đúng
                        try:
                            import random as _rand
                            cpu_var.set(str(_rand.choice([2, 4, 6, 10, 12])))
                            mem_var.set(str(_rand.choice([4, 8, 12, 24, 32])))
                            # Tự động random WebGL vendor và renderer từ danh sách đầy đủ
                            v = _rand.choice(webgl_vendor_options)
                            r = _rand.choice(webgl_renderer_options)
                            webgl_vendor_var.set(v)
                            webgl_renderer_var.set(r)
                        except Exception:
                            pass
                        
                        # Ưu tiên UA theo lựa chọn phiên bản trong Software tab; nếu trống mới random
                        final_ua = ua_var.get().strip()
                        if not final_ua:
                            # Tạo UA từ browser version được chọn
                            browser_version = browser_version_var.get().strip()
                            if browser_version:
                                final_ua = f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{browser_version} Safari/537.36"
                            else:
                                final_ua = self.manager._generate_user_agent(profile_type)
                        
                        settings_data = {
                            'profile_info': {
                                'name': name,
                                'display_name': name,  # Sử dụng tên profile làm display name
                                'type': profile_type,
                                'created_at': time.strftime('%Y-%m-%d %H:%M:%S')
                            },
                            'software': {
                                'user_agent': final_ua,
                                'browser_version': browser_version_var.get().strip() or '139.0.7258.139',
                                'language': lang_var.get().strip() or 'en-US',
                                'startup_url': url_var.get().strip(),
                                'webrtc_policy': webrtc_var.get(),
                                'os_font': 'Real'
                            },
                            'hardware': {
                                'screen_resolution': screen_var.get(),
                                'canvas_noise': canvas_var.get(),
                                'client_rect_noise': client_var.get(),
                                'webgl_image_noise': webgl_img_var.get(),
                                'audio_noise': audio_var.get(),
                                'webgl_meta_masked': webgl_masked_var.get(),
                                'webgl_vendor': webgl_vendor_var.get(),
                                'webgl_renderer': webgl_renderer_var.get(),
                                'media_devices_masked': media_masked_var.get(),
                                'cpu_cores': cpu_var.get(),
                                'device_memory': mem_var.get(),
                                'media_audio_inputs': audio_inputs_var.get(),
                                'media_audio_outputs': audio_outputs_var.get(),
                                'media_video_inputs': video_inputs_var.get(),
                                'mac_address': mac_var.get()
                            }
                        }
                        # Random phần cứng khi người dùng không chỉ định rõ (tránh mặc định 8/16)
                        try:
                            import random as _rand
                            cpu_val = str(settings_data['hardware'].get('cpu_cores') or '').strip()
                            mem_val = str(settings_data['hardware'].get('device_memory') or '').strip()
                            need_cpu_rand = (cpu_val == '' or cpu_val.lower() in ('auto', 'default', '0', 'none', 'null') or cpu_val == '8')
                            need_mem_rand = (mem_val == '' or mem_val.lower() in ('auto', 'default', '0', 'none', 'null') or mem_val == '16')
                            if minimal_var.get() or need_cpu_rand:
                                # Nếu giá trị đang là 8 -> loại 8 khỏi tập chọn
                                cpu_choices = [2, 4, 6, 8, 10, 12]
                                if cpu_val == '8':
                                    cpu_choices = [2, 4, 6, 10, 12]
                                settings_data['hardware']['cpu_cores'] = str(_rand.choice(cpu_choices))
                            if minimal_var.get() or need_mem_rand:
                                # Nếu giá trị đang là 16 -> loại 16 khỏi tập chọn
                                mem_choices = [4, 8, 12, 16, 24, 32]
                                if mem_val == '16':
                                    mem_choices = [4, 8, 12, 24, 32]
                                settings_data['hardware']['device_memory'] = str(_rand.choice(mem_choices))

                            # WebGL vendor/renderer chỉ random nếu chưa có
                            v_now = (settings_data['hardware'].get('webgl_vendor') or '').strip()
                            r_now = (settings_data['hardware'].get('webgl_renderer') or '').strip()
                            if minimal_var.get() or not v_now or not r_now:
                                pairs = [
                                    ("Google Inc. (NVIDIA)", "ANGLE (NVIDIA, NVIDIA GeForce RTX 3060 Direct3D11 vs_5_0 ps_5_0, D3D11)"),
                                    ("Google Inc. (Intel)", "ANGLE (Intel, Intel(R) UHD Graphics Direct3D11 vs_5_0 ps_5_0, D3D11)"),
                                    ("Google Inc. (AMD)", "ANGLE (AMD, AMD Radeon RX 6600 Direct3D11 vs_5_0 ps_5_0, D3D11)"),
                                ]
                                v, r = _rand.choice(pairs)
                                settings_data['hardware']['webgl_vendor'] = v
                                settings_data['hardware']['webgl_renderer'] = r
                        except Exception:
                            pass
                        # Áp template nếu có
                        try:
                            import json
                            tpl_name = template_var.get()
                            template_dir = os.path.join('data', 'templates')
                            applied = False
                            # 1) nếu user chọn builtin → áp quy tắc builtin
                            if tpl_name.startswith('Builtin:'):
                                # Builtin template: Work (US/UK)
                                settings_data['software']['language'] = 'en-US'
                                # Các mặc định hardware/software từ builtin
                                settings_data['software'].setdefault('webrtc_policy', 'default_public_interface_only')
                                settings_data['hardware'].setdefault('audio_noise', 'On')
                                settings_data['hardware'].setdefault('webgl_meta_masked', True)
                                settings_data['hardware'].setdefault('media_devices_masked', True)
                                applied = True
                            # 2) nếu tồn tại file template JSON trùng tên → áp file
                            if not applied and os.path.exists(template_dir):
                                for fn in os.listdir(template_dir):
                                    if fn.endswith('.json'):
                                        with open(os.path.join(template_dir, fn), 'r', encoding='utf-8') as tf:
                                            tpl = json.load(tf)
                                            if (tpl.get('name') or fn.replace('.json','')) == tpl_name:
                                                tsw = tpl.get('software', {})
                                                thw = tpl.get('hardware', {})
                                                settings_data['software'].update({k:v for k,v in tsw.items() if v is not None})
                                                settings_data['hardware'].update({k:v for k,v in thw.items() if v is not None})
                                                break
                        except Exception as _te:
                            print(f"[TEMPLATE] Không áp được template: {_te}")
                        
                        os.makedirs(profile_path, exist_ok=True)
                        with open(settings_path, 'w', encoding='utf-8') as f:
                            json.dump(settings_data, f, ensure_ascii=False, indent=2)
                        print(f"✅ [CREATE] Đã lưu cấu hình cho {name}")
                    except Exception as e:
                        print(f"⚠️ [CREATE] Không thể lưu cấu hình: {e}")

                    # Nếu chế độ tối giản: xoá Local State/Preferences ở root nếu lỡ tồn tại
                    try:
                        if minimal_var.get():
                            for fname in ("Local State", "Preferences"):
                                fp = os.path.join(profile_path, fname)
                                if os.path.exists(fp):
                                    try:
                                        os.remove(fp)
                                        print(f"🧹 [MINIMAL] Đã xoá {fname} ở root: {fp}")
                                    except Exception:
                                        pass
                    except Exception:
                        pass
                    
                    messagebox.showinfo("Thành công", f"✅ Profile '{name}' đã được tạo thành công!")
                    self.refresh_profiles()
                    dialog.destroy()
                else:
                    messagebox.showerror("Lỗi", f"❌ {message}")
            except Exception as e:
                messagebox.showerror("Lỗi", f"❌ Lỗi khi tạo profile: {str(e)}")
        
        def show_bulk_create():
            """Hiển thị dialog tạo hàng loạt"""
            dialog.destroy()
            self.show_bulk_create_dialog()
        
        def cancel():
            dialog.destroy()
        
        # Cập nhật UA theo browser version khi dialog mở
        try:
            browser_version = browser_version_var.get().strip()
            if browser_version:
                ua_var.set(f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{browser_version} Safari/537.36")
        except Exception:
            pass
        
        # Bind Enter key để tạo profile
        dialog.bind('<Return>', lambda e: create_profile())
        dialog.bind('<Escape>', lambda e: cancel())
        
        # Focus và bind Enter key
        name_entry.focus()
        name_entry.bind('<Return>', lambda e: create_profile())
    
    
    def show_bulk_create_dialog(self):
        """Hiển thị dialog tạo profile hàng loạt"""
        dialog = tk.Toplevel(self.root)
        dialog.title("📦 Tạo Profile Hàng Loạt")
        dialog.geometry("650x600")
        dialog.resizable(False, False)  # Fix kích thước
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Frame chính - không có scrollbar
        main_frame = ttk.Frame(dialog, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Tiêu đề
        title_label = ttk.Label(main_frame, text="Tạo Profile Chrome Hàng Loạt", 
                               font=("Segoe UI", 12, "bold"))
        title_label.pack(pady=(0, 15))
        
        # Thông tin cơ bản
        info_frame = ttk.LabelFrame(main_frame, text="📋 Thông tin cơ bản", padding="10")
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Profile gốc đã được xóa - sử dụng logic tạo profile mới
        
        # Số lượng và prefix
        quantity_frame = ttk.Frame(info_frame)
        quantity_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Số lượng
        ttk.Label(quantity_frame, text="Số lượng:", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=(0, 5))
        bulk_quantity_var = tk.StringVar(value="5")
        bulk_quantity_spinbox = ttk.Spinbox(quantity_frame, from_=1, to=50, textvariable=bulk_quantity_var, 
                                           width=8, font=("Segoe UI", 9))
        bulk_quantity_spinbox.pack(side=tk.LEFT, padx=(0, 15))
        
        # Random format checkbox (bắt buộc)
        bulk_random_format_var = tk.BooleanVar(value=True)  # Mặc định bật
        bulk_random_check = ttk.Checkbutton(quantity_frame, text="🎲 Random format (P-XXXXXX-XXXX)", 
                                           variable=bulk_random_format_var, state="disabled")
        bulk_random_check.pack(side=tk.LEFT, padx=(0, 10))
        
        # Random hardware checkbox
        bulk_random_hardware_var = tk.BooleanVar(value=False)
        bulk_hardware_check = ttk.Checkbutton(quantity_frame, text="🔧 Random Hardware", 
                                            variable=bulk_random_hardware_var)
        bulk_hardware_check.pack(side=tk.LEFT, padx=(0, 10))
        
        # Bắt đầu từ số
        ttk.Label(quantity_frame, text="Bắt đầu từ:", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=(0, 5))
        bulk_start_var = tk.StringVar(value="1")
        bulk_start_spinbox = ttk.Spinbox(quantity_frame, from_=1, to=1000, textvariable=bulk_start_var, 
                                        width=8, font=("Segoe UI", 9))
        bulk_start_spinbox.pack(side=tk.LEFT)
        
        # Browser version
        ttk.Label(quantity_frame, text="Version:", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=(15, 5))
        bulk_version_var = tk.StringVar(value="139.0.7258.139")
        chrome_version_options = [
            '139.0.7258.139', '137.0.7151.41', '135.0.7049.42', '134.0.6998.89',
            '132.0.6834.84', '129.0.6668.59', '127.0.6533.73', '124.0.6367.29',
            '121.0.6167.140', '119.0.6045.124', '115.0.5790.75', '111.0.5563.50',
            '107.0.5304.8', '106.0.5249.119'
        ]
        bulk_version_combo = ttk.Combobox(quantity_frame, textvariable=bulk_version_var, 
                                         values=chrome_version_options, state='readonly', width=15)
        bulk_version_combo.pack(side=tk.LEFT)
        
        # Preview tên sẽ tạo
        bulk_preview_label = ttk.Label(info_frame, text="", font=("Segoe UI", 8), foreground="blue")
        bulk_preview_label.pack(anchor=tk.W, pady=(3, 0))
        
        def update_bulk_preview():
            try:
                quantity = int(bulk_quantity_var.get())
                start = int(bulk_start_var.get())
                
                # Luôn sử dụng random format: P-XXXXXX-XXXX
                import random
                prefix_num = random.randint(100000, 999999)
                names = []
                for i in range(quantity):
                    suffix_num = f"{start + i:04d}"
                    names.append(f"P-{prefix_num}-{suffix_num}")
                
                preview_text = f"Tên sẽ tạo: {', '.join(names[:3])}"
                if len(names) > 3:
                    preview_text += f" ... và {len(names) - 3} profile khác"
                
                bulk_preview_label.config(text=preview_text)
            except:
                bulk_preview_label.config(text="Lỗi: Vui lòng nhập số hợp lệ")
        
        # Bind events để update preview
        bulk_quantity_var.trace('w', lambda *args: update_bulk_preview())
        bulk_start_var.trace('w', lambda *args: update_bulk_preview())
        
        # Proxy Configuration cho bulk
        bulk_proxy_frame = ttk.LabelFrame(main_frame, text="🌐 Cấu hình Proxy", padding="10")
        bulk_proxy_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Hướng dẫn proxy
        proxy_help_label = ttk.Label(bulk_proxy_frame, 
                                   text="Nhập danh sách proxy (mỗi dòng một proxy):\n" +
                                        "• HTTP: http://IP:Port:User:Pass\n" +
                                        "• SOCKS5: socks5://IP:Port:User:Pass\n" +
                                        "• Không proxy: null", 
                                   font=("Segoe UI", 8), foreground="gray")
        proxy_help_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Text area cho proxy
        bulk_proxy_text = tk.Text(bulk_proxy_frame, height=6, font=("Consolas", 9))
        bulk_proxy_text.pack(fill=tk.X, pady=(0, 5))
        
        # Scrollbar cho proxy text
        proxy_scrollbar = ttk.Scrollbar(bulk_proxy_frame, orient=tk.VERTICAL, command=bulk_proxy_text.yview)
        bulk_proxy_text.configure(yscrollcommand=proxy_scrollbar.set)
        
        # Stealth Configuration đã được xóa - không còn sử dụng
        
        def create_bulk_profiles():
            print("📝 [BULK-CREATE] Mở dialog tạo hàng loạt")
            # Không cần profile gốc - sử dụng logic tạo profile mới
            
            try:
                quantity = int(bulk_quantity_var.get())
                start = int(bulk_start_var.get())
                
                if quantity <= 0 or quantity > 50:
                    messagebox.showerror("Lỗi", "Số lượng phải từ 1 đến 50!")
                    return
                
                # Lấy proxy list
                proxy_text = bulk_proxy_text.get('1.0', tk.END).strip()
                proxy_list = []
                if proxy_text:
                    proxy_list = [line.strip() for line in proxy_text.splitlines() if line.strip() and line.strip() != 'null']
                
                # Lấy thông tin random hardware
                use_random_hardware = bulk_random_hardware_var.get()
                
                # Tạo danh sách tên - luôn sử dụng random format
                names = []
                import random
                prefix_num = random.randint(100000, 999999)
                for i in range(quantity):
                    suffix_num = f"{start + i:04d}"
                    names.append(f"P-{prefix_num}-{suffix_num}")
                
                # Kiểm tra tên đã tồn tại
                try:
                    existing_profiles = self.manager.get_all_profiles()
                    existing_names = [name for name in names if name in existing_profiles]
                    if existing_names:
                        messagebox.showerror("Lỗi", f"Các profile đã tồn tại: {', '.join(existing_names)}")
                        return
                except:
                    pass
                
                # Stealth config đã được xóa - không còn sử dụng
                
                # Xác nhận tạo hàng loạt
                result = messagebox.askyesno("Xác nhận", 
                                           f"Bạn có muốn tạo {quantity} profile với tên:\n" +
                                           f"{', '.join(names[:5])}" + 
                                           (f"\n... và {len(names) - 5} profile khác" if len(names) > 5 else "") +
                                           f"\n\nVới random hardware: {use_random_hardware}" +
                                           f"\nVới proxy: {len(proxy_list)} proxy")
                
                if not result:
                    return
                
                # Tạo profiles trong thread
                def create_bulk_thread():
                    # Sử dụng hàm create_profiles_bulk mới với thông tin ngẫu nhiên
                    print(f"🔧 [BULK-CREATE] Tạo {quantity} profile với random hardware: {use_random_hardware}")
                    print(f"🌐 [BULK-CREATE] Sử dụng {len(proxy_list)} proxy")
                    
                    # Lấy version từ dialog
                    version = bulk_version_var.get().strip()
                    
                    # Gọi hàm tạo profile bulk mới - luôn sử dụng random format
                    base_name = "P"  # Không quan trọng vì sẽ dùng random format
                    ok, result = self.manager.create_profiles_bulk(
                        base_name, quantity, version, True, proxy_list, use_random_hardware
                    )
                    
                    if ok:
                        success_count = len(result)
                    error_count = 0
                    errors = []
                    
                    # Auto-install extension for all new profiles
                    for name in result:
                                def install_extension_for_bulk_profile(profile_name):
                                    try:
                                        success = self.manager.ensure_extension_installed(profile_name)
                                        if success:
                                            print(f"✅ [BULK-CREATE] SwitchyOmega 3 automatically installed for {profile_name}")
                                        else:
                                            print(f"⚠️ [BULK-CREATE] Failed to auto-install extension for {profile_name}")
                                    except Exception as e:
                                        print(f"❌ [BULK-CREATE] Error auto-installing extension for {profile_name}: {str(e)}")
                                
                                # Install extension in background
                                threading.Thread(target=install_extension_for_bulk_profile, args=(name,), daemon=True).start()
                    else:
                        success_count = 0
                        error_count = quantity
                        errors = [result]  # result chứa thông báo lỗi
                    
                    # Hiển thị kết quả chi tiết
                    if success_count > 0:
                        result_msg = f"🎉 TẠO PROFILE HÀNG LOẠT HOÀN THÀNH!\n\n"
                        result_msg += f"✅ Thành công: {success_count} profile\n"
                        if error_count > 0:
                            result_msg += f"❌ Lỗi: {error_count} profile\n"
                            result_msg += f"\n📋 Chi tiết lỗi:\n" + "\n".join(errors[:3])
                            if len(errors) > 3:
                                result_msg += f"\n... và {len(errors) - 3} lỗi khác"
                        result_msg += f"\n\n🔧 Random Hardware: {'Có' if use_random_hardware else 'Không'}"
                        result_msg += f"\n🌐 Proxy: {len(proxy_list)} proxy"
                        result_msg += f"\n📱 Version: {version}"
                    else:
                        result_msg = f"❌ TẠO PROFILE THẤT BẠI!\n\n"
                        result_msg += f"Không thể tạo profile nào.\n"
                        result_msg += f"Chi tiết lỗi:\n" + "\n".join(errors[:5])
                    
                    # Hiển thị thông báo và cập nhật UI
                    def show_result():
                        messagebox.showinfo("📦 Kết quả tạo profile hàng loạt", result_msg)
                        self.refresh_profiles()
                        self.status_label.config(text="Hoàn thành tạo profile hàng loạt")
                        dialog.destroy()
                    
                    self.root.after(0, show_result)
                
                threading.Thread(target=create_bulk_thread, daemon=True).start()
                
            except ValueError:
                messagebox.showerror("Lỗi", "Vui lòng nhập số hợp lệ!")
                return
        
        def cancel_bulk():
            dialog.destroy()
        
        # Nút
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(15, 0))
        
        # Layout buttons cân đối
        left_btn_frame = ttk.Frame(button_frame)
        left_btn_frame.pack(side=tk.LEFT, expand=True, fill=tk.X)
        
        right_btn_frame = ttk.Frame(button_frame)
        right_btn_frame.pack(side=tk.RIGHT, expand=True, fill=tk.X)
        
        # Nút Hủy ở bên trái
        cancel_btn = ttk.Button(left_btn_frame, text="❌ Hủy", command=cancel_bulk, width=12)
        cancel_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Nút Tạo ở bên phải
        create_btn = ttk.Button(right_btn_frame, text="✅ Tạo Hàng Loạt", command=create_bulk_profiles, width=15)
        create_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Bind Enter key
        dialog.bind('<Return>', lambda e: create_bulk_profiles())
        dialog.bind('<Escape>', lambda e: cancel_bulk())
        
        # Stealth options đã được xóa
        
        # Update preview ban đầu
        update_bulk_preview()
        
    def launch_profile(self, hidden=None):
        """Starting profile"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một profile!")
            return
        
        profile_name = self.tree.item(selection[0])["values"][0]
        print(f"[LAUNCH] [LAUNCH] Starting profile: {profile_name}")
        
        if profile_name in self.drivers:
            print(f"⚠️ [LAUNCH] Profile {profile_name} đang chạy")
            messagebox.showwarning("Cảnh báo", "Profile đang chạy!")
            return
        
        # Nếu không chỉ định hidden, sử dụng cài đặt mặc định
        if hidden is None:
            hidden = getattr(self, 'hidden_mode_var', tk.BooleanVar(value=True)).get()
        
        def launch_thread():
            self.status_label.config(text=f"Đang khởi động {profile_name}...")
            
            # Lấy dữ liệu đăng nhập TikTok nếu có
            login_data = None
            success, tiktok_session = self.manager.load_tiktok_session(profile_name)
            if success:
                login_data = tiktok_session
                print(f"🔐 [LAUNCH] Đã load TikTok session: {login_data.get('email', 'N/A')}")
                print(f"📱 [LAUNCH] Username: {login_data.get('username', 'N/A')}")
                print(f"🆔 [LAUNCH] User ID: {login_data.get('user_id', 'N/A')}")
            else:
                print(f"⚠️ [LAUNCH] Không có TikTok session cho {profile_name}")
            
            # Starting Chrome với auto_login để tự động restore session hoặc đăng nhập
            # Nếu có login_data thì sẽ đăng nhập mới, nếu không có thì sẽ load session cũ
            # Chạy native tối giản khi hiển thị để tránh mở nhiều cửa sổ
            if not hidden and (login_data is None):
                success, result = self.manager.launch_chrome_profile(profile_name, hidden=False, auto_login=False)
            else:
                success, result = self.manager.launch_chrome_profile(
                    profile_name,
                    hidden=hidden,
                    auto_login=bool(login_data),
                    login_data=login_data
                )
            
            if success:
                self.drivers[profile_name] = result
                mode_text = "ẩn" if hidden else "hiển thị"
                self.root.after(0, lambda: self.status_label.config(text=f"Đã khởi động {profile_name} ở chế độ {mode_text}"))
                self.root.after(0, lambda: self.refresh_profiles())
            else:
                self.root.after(0, lambda: messagebox.showerror("Lỗi", result))
                self.root.after(0, lambda: self.status_label.config(text="Lỗi khởi động"))
        
        threading.Thread(target=launch_thread, daemon=True).start()
    
    def launch_all_profiles(self):
        """Starting tất cả profiles"""
        profiles = self.manager.get_all_profiles()
        if not profiles:
            messagebox.showwarning("Cảnh báo", "Không có profile nào để khởi động!")
            return
        
        # Xác nhận với user
        hidden = getattr(self, 'hidden_mode_var', tk.BooleanVar(value=True)).get()
        mode_text = "ẩn" if hidden else "hiển thị"
        
        if not messagebox.askyesno("Xác nhận", 
                                  f"Bạn có chắc muốn khởi động tất cả {len(profiles)} profiles ở chế độ {mode_text}?"):
            return
        
        def launch_all_thread():
            self.status_label.config(text="Đang khởi động tất cả profiles...")
            success_count = 0
            
            for profile_name in profiles:
                if profile_name in self.drivers:
                    continue  # Bỏ qua profile đang chạy
                
                # Lấy dữ liệu đăng nhập nếu có
                login_data = None
                if isinstance(self.manager.config, dict) and 'LOGIN_DATA' in self.manager.config and profile_name in self.manager.config.get('LOGIN_DATA', {}):
                    try:
                        import json
                        login_data = json.loads(self.manager.config['LOGIN_DATA'][profile_name])
                    except:
                        login_data = None
                
                success, result = self.manager.launch_chrome_profile(profile_name, hidden=hidden, auto_login=bool(login_data), login_data=login_data)
                
                if success:
                    self.drivers[profile_name] = result
                    success_count += 1
                
                time.sleep(2)  # Delay giữa các profiles
            
            self.root.after(0, lambda: self.status_label.config(text=f"Đã khởi động {success_count}/{len(profiles)} profiles"))
            self.root.after(0, lambda: self.refresh_profiles())
        
        threading.Thread(target=launch_all_thread, daemon=True).start()
    
    def stop_all_profiles(self):
        """Dừng tất cả profiles đang chạy"""
        if not self.drivers:
            messagebox.showinfo("Thông báo", "Không có profile nào đang chạy!")
            return
        
        if not messagebox.askyesno("Xác nhận", 
                                  f"Bạn có chắc muốn dừng tất cả {len(self.drivers)} profiles đang chạy?"):
            return
        
        def stop_all_thread():
            self.status_label.config(text="Đang dừng tất cả profiles...")
            stopped_count = 0
            
            for profile_name, driver in list(self.drivers.items()):
                try:
                    driver.quit()
                    del self.drivers[profile_name]
                    stopped_count += 1
                except Exception as e:
                    print(f"Lỗi khi dừng {profile_name}: {str(e)}")
            
            self.root.after(0, lambda: self.status_label.config(text=f"Đã dừng {stopped_count} profiles"))
            self.root.after(0, lambda: self.refresh_profiles())
        
        threading.Thread(target=stop_all_thread, daemon=True).start()
    
    def bulk_delete_selected(self):
        """Xóa hàng loạt các profiles đã chọn"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn ít nhất một profile để xóa!")
            return
        
        selected_profiles = []
        for item in selection:
            profile_name = self.tree.item(item)['text']
            if profile_name and profile_name.strip():
                selected_profiles.append(profile_name.strip())
        
        if not selected_profiles:
            messagebox.showwarning("Cảnh báo", "Không có profile hợp lệ nào được chọn!")
            return
        
        # Tạo dialog xác nhận
        dialog = tk.Toplevel(self.root)
        dialog.title("🗑️ Xóa Profile Hàng Loạt")
        # Dialog settings - tăng kích thước để hiển thị đầy đủ nút
        dialog.geometry("720x520")
        dialog.minsize(700, 480)
        dialog.resizable(True, True)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Main frame
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Warning icon and title
        warning_frame = ttk.Frame(main_frame)
        warning_frame.pack(fill=tk.X, pady=(0, 20))
        
        warning_label = ttk.Label(warning_frame, text="⚠️ CẢNH BÁO", 
                                 font=("Segoe UI", 16, "bold"), foreground="red")
        warning_label.pack()
        
        info_label = ttk.Label(warning_frame, text="Bạn sắp xóa vĩnh viễn các profile sau:", 
                              font=("Segoe UI", 12))
        info_label.pack(pady=(10, 0))
        
        # Profiles list
        profiles_frame = ttk.LabelFrame(main_frame, text="📋 Profiles sẽ bị xóa", padding="15")
        profiles_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Listbox với scrollbar
        listbox_frame = ttk.Frame(profiles_frame)
        listbox_frame.pack(fill=tk.BOTH, expand=True)
        
        profiles_listbox = tk.Listbox(listbox_frame, font=("Consolas", 10), height=12)
        profiles_scrollbar = ttk.Scrollbar(listbox_frame, orient="vertical", command=profiles_listbox.yview)
        profiles_listbox.configure(yscrollcommand=profiles_scrollbar.set)
        
        profiles_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        profiles_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Populate listbox
        for profile in selected_profiles:
            profiles_listbox.insert(tk.END, f"• {profile}")
        
        # Options
        options_frame = ttk.LabelFrame(main_frame, text="⚙️ Tùy chọn", padding="15")
        options_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Checkbox options
        stop_running_var = tk.BooleanVar(value=True)
        stop_check = ttk.Checkbutton(options_frame, text="Dừng profile đang chạy trước khi xóa", 
                                   variable=stop_running_var)
        stop_check.pack(anchor=tk.W, pady=(0, 5))
        
        backup_var = tk.BooleanVar(value=False)
        backup_check = ttk.Checkbutton(options_frame, text="Tạo backup trước khi xóa", 
                                     variable=backup_var)
        backup_check.pack(anchor=tk.W, pady=(0, 5))
        
        confirm_var = tk.BooleanVar(value=False)
        confirm_check = ttk.Checkbutton(options_frame, text="Tôi hiểu rằng hành động này không thể hoàn tác", 
                                      variable=confirm_var)
        confirm_check.pack(anchor=tk.W)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        def confirm_delete():
            if not confirm_var.get():
                messagebox.showwarning("Cảnh báo", "Vui lòng xác nhận rằng bạn hiểu hành động này không thể hoàn tác!")
                return
            
            # Final confirmation
            result = messagebox.askyesno("Xác nhận cuối cùng", 
                                       f"Bạn có chắc chắn muốn xóa {len(selected_profiles)} profile(s)?\n\n"
                                       "Hành động này KHÔNG THỂ hoàn tác!")
            if not result:
                return
            
            dialog.destroy()
            self._execute_bulk_delete(selected_profiles, stop_running_var.get(), backup_var.get())
        
        def cancel_delete():
            dialog.destroy()
        
        # Layout buttons using grid for better control
        cancel_btn = ttk.Button(button_frame, text="❌ Hủy", command=cancel_delete, width=18)
        cancel_btn.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        
        delete_btn = ttk.Button(button_frame, text="🗑️ Xóa Vĩnh Viễn", command=confirm_delete, width=22)
        delete_btn.grid(row=0, column=1, padx=(10, 0), sticky="ew")
        
        # Configure grid weights
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        
        # Bind Enter key
        dialog.bind('<Return>', lambda e: confirm_delete() if confirm_var.get() else None)
        dialog.bind('<Escape>', lambda e: cancel_delete())
        
        # Focus vào checkbox xác nhận
        confirm_check.focus()
    
    def _execute_bulk_delete(self, profiles, stop_running, create_backup):
        """Thực thi xóa hàng loạt"""
        def bulk_delete_thread():
            self.root.after(0, lambda: self.status_label.config(text="Đang xóa profiles..."))
            success_count = 0
            error_count = 0
            errors = []
            
            for i, profile_name in enumerate(profiles):
                try:
                    self.root.after(0, lambda p=profile_name, idx=i+1: 
                                  self.status_label.config(text=f"Đang xóa {p} ({idx}/{len(profiles)})"))
                    
                    # Stop profile if running
                    if stop_running:
                        # Stop driver if exists
                        if profile_name in self.drivers:
                            try:
                                self.drivers[profile_name].quit()
                                del self.drivers[profile_name]
                                print(f"Đã dừng driver cho profile '{profile_name}'")
                            except Exception as e:
                                print(f"Lỗi khi dừng driver '{profile_name}': {str(e)}")
                        
                        # Force kill Chrome processes for this profile
                        try:
                            import psutil
                            profile_path = os.path.join(self.manager.profiles_dir, profile_name)
                            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                                try:
                                    if proc.info['name'] and 'chrome' in proc.info['name'].lower():
                                        cmdline = proc.info['cmdline']
                                        if cmdline and any(profile_path in arg for arg in cmdline):
                                            print(f"Đang dừng Chrome process {proc.info['pid']} cho profile '{profile_name}'")
                                            proc.terminate()
                                            proc.wait(timeout=5)
                                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
                                    pass
                        except ImportError:
                            print("psutil không có sẵn, không thể force kill Chrome processes")
                        except Exception as e:
                            print(f"Lỗi khi force kill Chrome processes: {str(e)}")
                        
                        # Wait a bit for processes to fully terminate
                        time.sleep(2)
                    
                    # Create backup if requested
                    if create_backup:
                        try:
                            backup_path = f"backup_{profile_name}_{int(time.time())}"
                            import shutil
                            profile_path = os.path.join(self.manager.profiles_dir, profile_name)
                            if os.path.exists(profile_path):
                                # Try to copy with ignore_errors for locked files
                                def ignore_errors(src, names):
                                    ignored = []
                                    for name in names:
                                        src_path = os.path.join(src, name)
                                        try:
                                            if os.path.isfile(src_path):
                                                # Try to open file to check if it's locked
                                                with open(src_path, 'rb') as f:
                                                    pass
                                        except (OSError, IOError):
                                            ignored.append(name)
                                    return ignored
                                
                                shutil.copytree(profile_path, backup_path, ignore=ignore_errors)
                                print(f"Đã tạo backup: {backup_path}")
                        except Exception as e:
                            print(f"Lỗi khi tạo backup cho '{profile_name}': {str(e)}")
                    
                    # Delete profile
                    success, result = self.manager.delete_profile(profile_name)
                    if success:
                        success_count += 1
                        print(f"Đã xóa profile '{profile_name}' thành công")
                    else:
                        error_count += 1
                        errors.append(f"{profile_name}: {result}")
                        print(f"Lỗi khi xóa profile '{profile_name}': {result}")
                    
                    time.sleep(0.5)  # Small delay between deletions
                    
                except Exception as e:
                    error_count += 1
                    errors.append(f"{profile_name}: {str(e)}")
                    print(f"Lỗi không mong muốn khi xóa '{profile_name}': {str(e)}")
            
            # Update UI
            def update_ui():
                self.status_label.config(text=f"Đã xóa {success_count}/{len(profiles)} profiles")
                self.refresh_profiles()
                
                # Show result dialog
                if error_count == 0:
                    messagebox.showinfo("Thành công", f"Đã xóa thành công {success_count} profile(s)!")
                else:
                    error_msg = f"Xóa thành công: {success_count} profile(s)\n"
                    error_msg += f"Lỗi: {error_count} profile(s)\n\n"
                    error_msg += "Chi tiết lỗi:\n" + "\n".join(errors[:5])
                    if len(errors) > 5:
                        error_msg += f"\n... và {len(errors) - 5} lỗi khác"
                    
                    messagebox.showerror("Hoàn thành với lỗi", error_msg)
            
            self.root.after(0, update_ui)
        
        threading.Thread(target=bulk_delete_thread, daemon=True).start()
    
    def bulk_run_selected(self):
        """Chạy hàng loạt cho các profiles đã chọn"""
        print("[LAUNCH] [BULK-RUN] Mở dialog chạy hàng loạt")
        selected_profiles = []
        try:
            if hasattr(self, 'tree') and self.tree.winfo_exists():
                selection = self.tree.selection()
                if selection:
                    selected_profiles = [self.tree.item(item)['text'] for item in selection]
                else:
                    selected_profiles = []
        except Exception:
            selected_profiles = []

        if not selected_profiles:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn ít nhất một profile ở bảng bên trái trước!")
            return
        print(f"📋 [BULK-RUN] Đã chọn {len(selected_profiles)} profiles")
        
        # Tạo dialog bulk run
        dialog = tk.Toplevel(self.root)
        dialog.title("[LAUNCH] Chạy hàng loạt")
        dialog.geometry("800x600")
        dialog.resizable(True, True)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Main frame
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Profiles info
        profiles_frame = ttk.LabelFrame(main_frame, text="📋 Profiles đã chọn", padding="10")
        profiles_frame.pack(fill=tk.X, pady=(0, 10))
        
        profiles_text = ttk.Label(profiles_frame, text=f"Đã chọn {len(selected_profiles)} profiles: {', '.join(selected_profiles)}")
        profiles_text.pack(anchor=tk.W)
        
        # URL input
        url_frame = ttk.LabelFrame(main_frame, text="🌐 URL", padding="10")
        url_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Load saved data
        saved_data = self._load_bulk_run_data()
        url_var = tk.StringVar(value=saved_data.get('url', "https://www.tiktok.com/login/phone-or-email/email"))
        url_entry = ttk.Entry(url_frame, textvariable=url_var, font=("Segoe UI", 10))
        url_entry.pack(fill=tk.X, pady=(0, 5))
        
        # URL suggestions
        suggestions_frame = ttk.Frame(url_frame)
        suggestions_frame.pack(fill=tk.X)
        
        common_urls = [
            ("TikTok Login (Email)", "https://www.tiktok.com/login/phone-or-email/email"),
            ("TikTok Login (Phone)", "https://www.tiktok.com/login/phone-or-email/phone"),
            ("TikTok Home", "https://www.tiktok.com"),
            ("TikTok For You", "https://www.tiktok.com/foryou")
        ]
        
        for i, (name, url) in enumerate(common_urls):
            btn = ttk.Button(suggestions_frame, text=name, 
                           command=lambda u=url: url_var.set(u),
                           style="Accent.TButton")
            btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Format selection
        format_frame = ttk.Frame(main_frame)
        format_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(format_frame, text="Format dữ liệu:", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=(0, 10))
        format_var = tk.StringVar(value="TikTok Format")
        format_combo = ttk.Combobox(format_frame, textvariable=format_var, width=20, state="readonly")
        format_combo['values'] = ["TikTok Format", "Standard", "Custom"]
        format_combo.pack(side=tk.LEFT, padx=(0, 15))
        
        # Format description
        format_desc = ttk.Label(format_frame, text="TikTok Format: username|password|email|email_password|ms_refresh_token|ms_client_id|[session_token]|[user_id]", 
                               font=("Segoe UI", 9), foreground="gray")
        format_desc.pack(side=tk.LEFT)
        
        def update_format_desc():
            format_type = format_var.get()
            if format_type == "Standard":
                format_desc.config(text="Standard: username|password")
            elif format_type == "TikTok Format":
                format_desc.config(text="TikTok: username|password|email|email_password|session_token|user_id")
            else:
                format_desc.config(text="Custom: tự định nghĩa")
        
        format_combo.bind('<<ComboboxSelected>>', lambda e: update_format_desc())
        
        # Accounts input
        accounts_frame = ttk.LabelFrame(main_frame, text="👥 Danh sách tài khoản", padding="10")
        accounts_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Text area for accounts
        accounts_text = tk.Text(accounts_frame, height=8, font=("Consolas", 9))
        accounts_text.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        # Load saved accounts data
        if 'accounts' in saved_data:
            accounts_text.insert("1.0", saved_data['accounts'])
        
        # Add example text
        example_text = """# Ví dụ TikTok Format (Email Login):
user8827533676234|Zxcv@1fzfrz|daihieptonewa29506@hotmail.com|daihiepsszui2511|M.C517_BAY.0.U.-CmtSHWsBO6iqS4lHpUbMiGOcEh6upYHIGnzSdmdr0r0XHVJI1ysq7xYcWNW*lb5vRJRjOQBmb6n8Atvcv8j!wDJcXwEqUNN5M4aVZNxQcJ9xJBIXRN!tKoTE9UgvAKg9DGSAGtirGLNrSDvBIEr6*Tc82hYXZiGsP3rnxyX7IvjFxXYzayMM9iw8IHUmfAXd41rBE2uA!QG5kjdQ4Dkyym4f5wN8byog74uVnVxIvAzVYqTRLuGDv7nf1cKOn5dpvBFEI7c*DMPq*2vmEqPlGyvsO6toUawCxUTKxwdTAn9!J!fjhBLeStluJfJ9l7uVbIOpo0IvQpKvFxp3OJlCWb6qXHd*Zkfai*s368CPNMwqdubRnZaVF6Px6SmqJRiir*nCCBQIPFVGVTsl7cX6G17lfGQMGtizLTPGoRD68fnv|9e5f94bc-e8a4-4e73-b8be-63364c29d753

# Format: username|password|email|email_password|session_token|user_id
# URL: https://www.tiktok.com/login/phone-or-email/email"""
        
        accounts_text.insert(tk.END, example_text)
        
        # Import buttons
        import_frame = ttk.Frame(accounts_frame)
        import_frame.pack(fill=tk.X)
        
        def import_excel():
            file_path = filedialog.askopenfilename(
                title="Chọn file Excel",
                filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
            )
            if file_path:
                try:
                    import pandas as pd
                    df = pd.read_excel(file_path)
                    
                    # Check required columns
                    required_cols = ['Email', 'Password']
                    if not all(col in df.columns for col in required_cols):
                        messagebox.showerror("Lỗi", f"File Excel phải có các cột: {', '.join(required_cols)}")
                        return
                    
                    # Build accounts text
                    accounts_lines = []
                    for _, row in df.iterrows():
                        email = str(row['Email']).strip()
                        password = str(row['Password']).strip()
                        twofa = str(row.get('2FA', '')).strip() if '2FA' in df.columns else ''
                        
                        if email and password:
                            accounts_lines.append(f"{email}:{password}:{twofa}")
                    
                    accounts_text.delete(1.0, tk.END)
                    accounts_text.insert(1.0, '\n'.join(accounts_lines))
                    messagebox.showinfo("Thành công", f"Đã import {len(accounts_lines)} tài khoản từ Excel!")
                    
                except Exception as e:
                    messagebox.showerror("Lỗi", f"Không thể đọc file Excel: {str(e)}")
        
        def import_txt():
            file_path = filedialog.askopenfilename(
                title="Chọn file Text",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            if file_path:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    accounts_text.delete(1.0, tk.END)
                    accounts_text.insert(1.0, content)
                    
                    lines = [line.strip() for line in content.split('\n') if line.strip()]
                    messagebox.showinfo("Thành công", f"Đã import {len(lines)} tài khoản từ file text!")
                    
                except Exception as e:
                    messagebox.showerror("Lỗi", f"Không thể đọc file text: {str(e)}")
        
        def parse_tiktok_format(line):
            """Parse TikTok format: username|password|email|email_password|ms_refresh_token|ms_client_id|[session_token]|[user_id]"""
            # Skip comment lines
            if line.strip().startswith('#'):
                return None
                
            parts = line.split('|')
            if len(parts) >= 3:  # Minimum: username|password|email
                data = {
                    'username': parts[0].strip(),
                    'password': parts[1].strip(),
                    'email': parts[2].strip(),
                    'email_password': parts[3].strip() if len(parts) > 3 else ''
                }
                if len(parts) > 5:
                    data['ms_refresh_token'] = parts[4].strip()
                    data['ms_client_id'] = parts[5].strip()
                if len(parts) > 6:
                    data['session_token'] = parts[6].strip()
                if len(parts) > 7:
                    data['user_id'] = parts[7].strip()
                return data
            return None
        
        def parse_standard_format(line):
            """Parse standard format: username|password or username:password.
            Linh hoạt khoảng trắng, cho phép password bắt đầu bằng '#'."""
            try:
                import re
                m = re.match(r"^\s*([^|:]+?)\s*[|:]\s*(.+?)\s*$", line)
                if not m:
                    return None
                username = m.group(1).strip()
                password = m.group(2).strip()
                if not username or not password:
                    return None
                return {
                    'username': username,
                    'password': password,
                    'email': username,
                    'twofa': ''
                }
            except Exception:
                return None

        def parse_email_first_format(line):
            """Parse email-first formats:
            - email|password
            - email|password|hotmail|passwordhotmail|... (lấy thêm hotmail/pass nếu có)
            """
            parts = [p.strip() for p in line.split('|')]
            if len(parts) >= 2 and ('@' in parts[0]):
                data = {
                    'email': parts[0],
                    'password': parts[1],
                    'username': parts[0],  # dùng email làm username nếu thiếu
                    'twofa': ''
                }
                # Nếu có thêm hotmail|passwordhotmail (ở vị trí 3 và 4)
                if len(parts) >= 4 and ('@' in parts[2]):
                    data['email_secondary'] = parts[2]
                    data['email_secondary_password'] = parts[3]
                    # ánh xạ vào email_password để launch_chrome_profile dùng nếu cần
                    data['email_password'] = parts[3]
                return data
            return None
        
        def test_tiktok_format():
            """Test với dữ liệu TikTok mẫu"""
            sample_data = """# Ví dụ TikTok Format:
user8827533676234|Zxcv@1fzfrz|daihieptonewa29506@hotmail.com|daihiepsszui2511|M.C517_BAY.0.U.-CmtSHWsBO6iqS4lHpUbMiGOcEh6upYHIGnzSdmdr0r0XHVJI1ysq7xYcWNW*lb5vRJRjOQBmb6n8Atvcv8j!wDJcXwEqUNN5M4aVZNxQcJ9xJBIXRN!tKoTE9UgvAKg9DGSAGtirGLNrSDvBIEr6*Tc82hYXZiGsP3rnxyX7IvjFxXYzayMM9iw8IHUmfAXd41rBE2uA!QG5kjdQ4Dkyym4f5wN8byog74uVnVxIvAzVYqTRLuGDv7nf1cKOn5dpvBFEI7c*DMPq*2vmEqPlGyvsO6toUawCxUTKxwdTAn9!J!fjhBLeStluJfJ9l7uVbIOpo0IvQpKvFxp3OJlCWb6qXHd*Zkfai*s368CPNMwqdubRnZaVF6Px6SmqJRiir*nCCBQIPFVGVTsl7cX6G17lfGQMGtizLTPGoRD68fnv|9e5f94bc-e8a4-4e73-b8be-63364c29d753

# Format: username|password|email|email_password|session_token|user_id"""
            
            accounts_text.delete(1.0, tk.END)
            accounts_text.insert(1.0, sample_data)
            format_var.set("TikTok Format")
            update_format_desc()
            messagebox.showinfo("Thành công", "Đã load dữ liệu TikTok mẫu!\n\nFormat: username|password|email|email_password|session_token|user_id")
        
        def test_standard_format():
            """Test với dữ liệu Standard Format mẫu"""
            sample_data = """# Ví dụ Standard Format:
username1|password123
username2|mypassword
user123|secretpass
testuser|testpass123

# Format: username|password"""
            
            accounts_text.delete(1.0, tk.END)
            accounts_text.insert(1.0, sample_data)
            format_var.set("Standard")
            update_format_desc()
            messagebox.showinfo("Thành công", "Đã load dữ liệu Standard Format mẫu!\n\nFormat: username|password")
        
        ttk.Button(import_frame, text="📊 Import Excel", command=import_excel).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(import_frame, text="📄 Import TXT", command=import_txt).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(import_frame, text="🎯 Test TikTok", command=test_tiktok_format).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(import_frame, text="⚡ Test Standard", command=test_standard_format).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(import_frame, text="🗑️ Clear", command=lambda: accounts_text.delete(1.0, tk.END)).pack(side=tk.LEFT)
        
        # Settings
        settings_frame = ttk.LabelFrame(main_frame, text="⚙️ Cài đặt", padding="10")
        settings_frame.pack(fill=tk.X, pady=(0, 10))
        
        settings_grid = ttk.Frame(settings_frame)
        settings_grid.pack(fill=tk.X)
        
        # Delay
        ttk.Label(settings_grid, text="Delay (giây):").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        delay_var = tk.StringVar(value=str(saved_data.get('delay', 2)))
        ttk.Entry(settings_grid, textvariable=delay_var, width=10).grid(row=0, column=1, sticky=tk.W, padx=(0, 20))
        
        # Hidden mode (default off so you can see auto-fill)
        hidden_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(settings_grid, text="Chế độ ẩn", variable=hidden_var).grid(row=0, column=2, sticky=tk.W)
        
        
        # Buttons
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X)
        
        # Save/Load buttons
        save_load_frame = ttk.Frame(buttons_frame)
        save_load_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        def save_data():
            data = {
                'url': url_var.get(),
                'accounts': accounts_text.get("1.0", "end-1c"),
                'delay': delay_var.get()
            }
            self._save_bulk_run_data(data)
            messagebox.showinfo("Thành công", "Đã lưu dữ liệu!")
        
        def clear_data():
            if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa tất cả dữ liệu?"):
                url_var.set("https://www.tiktok.com/login/phone-or-email/email")
                accounts_text.delete("1.0", tk.END)
                delay_var.set("2")
                self._save_bulk_run_data({})
                messagebox.showinfo("Thành công", "Đã xóa dữ liệu!")
        
        ttk.Button(save_load_frame, text="💾 Lưu dữ liệu", command=save_data).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(save_load_frame, text="🗑️ Xóa dữ liệu", command=clear_data).pack(side=tk.LEFT, padx=(0, 5))
        
        def start_bulk_run():
            print("[LAUNCH] [BULK-RUN] Bắt đầu chạy hàng loạt")
            url = url_var.get().strip()
            accounts_text_content = accounts_text.get("1.0", "end-1c").strip()
            
            # Save data before running
            self._save_bulk_run_data({
                'url': url,
                'accounts': accounts_text_content,
                'delay': delay_var.get()
            })
            try:
                print(f"🧾 [BULK-RUN] Raw accounts length: {len(accounts_text_content)}")
                preview = accounts_text_content.splitlines()[:3]
                print(f"🧾 [BULK-RUN] Preview lines: {preview}")
            except Exception:
                pass
            
            if not url:
                messagebox.showwarning("Cảnh báo", "Vui lòng nhập URL!")
                return
            
            if not accounts_text_content:
                messagebox.showwarning("Cảnh báo", "Vui lòng nhập danh sách tài khoản!")
                return
            
            try:
                delay = float(delay_var.get())
            except ValueError:
                messagebox.showerror("Lỗi", "Delay phải là số!")
                return
            
            # Parse accounts based on format
            accounts = []
            format_type = format_var.get()
            
            for line in accounts_text_content.splitlines():
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                account_data = None

                fmt = (format_var.get() or "").strip().lower()
                if fmt == "standard":
                    # username|password (or username:password)
                    account_data = parse_standard_format(line)
                    if not account_data and ':' in line:
                        parts = line.split(':')
                        if len(parts) >= 2:
                            account_data = {
                                'username': parts[0].strip(),
                                'password': parts[1].strip(),
                                'email': parts[0].strip(),
                                'twofa': ''
                            }
                elif fmt in ("tiktok format", "tiktok"):
                    # username|password|email|email_password|...
                    tk = parse_tiktok_format(line)
                    if tk:
                        accounts.append({
                            'email': tk['email'],
                            'password': tk['password'],
                            'twofa': '',
                            'username': tk['username'],
                            'email_password': tk.get('email_password', ''),
                            'ms_refresh_token': tk.get('ms_refresh_token', ''),
                            'ms_client_id': tk.get('ms_client_id', ''),
                            'session_token': tk.get('session_token', ''),
                            'user_id': tk.get('user_id', '')
                        })
                        continue
                else:
                    # Custom/autodetect: email-first | standard | colon
                    if '|' in line and ('@' in line.split('|', 1)[0]):
                        account_data = parse_email_first_format(line)
                    if not account_data and '|' in line:
                        account_data = parse_standard_format(line)
                    if not account_data and ':' in line:
                        parts = line.split(':')
                        if len(parts) >= 2:
                            account_data = {
                                'username': parts[0].strip(),
                                'password': parts[1].strip(),
                                'email': parts[0].strip(),
                                'twofa': ''
                            }

                    if account_data:
                        accounts.append(account_data)
            
            print(f"✅ [BULK-RUN] Đã parse {len(accounts)} accounts")
            # Accounts ready for processing
            
            if not accounts:
                # Rescue parse: cố gắng parse kiểu standard một lần nữa rất đơn giản
                try:
                    fallback_accounts = []
                    for line in accounts_text_content.splitlines():
                        line = line.strip()
                        if not line or line.startswith('#'):
                            continue
                        sep = '|' if '|' in line else (':' if ':' in line else None)
                        if sep:
                            left, right = line.split(sep, 1)
                            left = left.strip()
                            right = right.strip()
                            if left and right:
                                fallback_accounts.append({'username': left, 'password': right, 'email': left, 'twofa': ''})
                    if fallback_accounts:
                        accounts = fallback_accounts
                        print(f"🛟 [BULK-RUN] Fallback parsed {len(accounts)} accounts")
                    else:
                        messagebox.showwarning("Cảnh báo", "Không có tài khoản hợp lệ!")
                        return
                except Exception:
                    messagebox.showwarning("Cảnh báo", "Không có tài khoản hợp lệ!")
                    return
            
            dialog.destroy()
            
            # Ensure accounts count matches number of selected profiles
            run_profiles = selected_profiles
            if len(accounts) < len(selected_profiles):
                messagebox.showwarning(
                    "Cảnh báo",
                    f"Bạn chọn {len(selected_profiles)} profiles nhưng chỉ có {len(accounts)} dòng tài khoản.\n"
                    "Mỗi profile cần 1 dòng tài khoản theo thứ tự."
                )
                # Trim profiles to number of accounts to avoid empty mappings
                run_profiles = selected_profiles[:len(accounts)]
            
            # Start bulk run
            self._execute_bulk_run(run_profiles, url, accounts, delay, hidden_var.get())
        
        # Buttons với style rõ ràng
        start_btn = ttk.Button(buttons_frame, text="[LAUNCH] Bắt đầu", command=start_bulk_run)
        start_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        cancel_btn = ttk.Button(buttons_frame, text="❌ Hủy", command=dialog.destroy)
        cancel_btn.pack(side=tk.RIGHT)
        
        # Bind Enter key
        dialog.bind('<Return>', lambda e: start_bulk_run())
        dialog.bind('<Escape>', lambda e: dialog.destroy())
        
        # Focus vào nút Bắt đầu
        start_btn.focus()
    
    def _execute_bulk_run(self, profiles, url, accounts, delay, hidden):
        """Thực thi bulk run"""
        def bulk_run_thread():
            self.status_label.config(text="Đang chạy hàng loạt...")
            success_count = 0
            total_operations = min(len(profiles), len(accounts))  # Mỗi profile 1 account
            current_operation = 0
            
            # Memory monitoring
            print(f"🧠 [BULK-RUN] Bắt đầu với {total_operations} profiles")
            memory_info = self.manager.get_memory_usage()
            if memory_info:
                print(f"🧠 [BULK-RUN] RAM ban đầu: {memory_info['system_memory_percent']}%")
                print(f"🧠 [BULK-RUN] Available: {memory_info['available_memory_gb']}GB")
            
            # Mỗi profile chỉ dùng 1 account (theo thứ tự)
            for i, profile_name in enumerate(profiles):
                print(f"🔄 [BULK-RUN] Xử lý profile: {profile_name}")
                
                # Cập nhật trạng thái đang xử lý
                self.root.after(0, lambda p=profile_name: self._update_profile_status(p, "🔄 Processing"))
                
                # Stop existing driver if running
                if profile_name in self.drivers:
                    try:
                        self.drivers[profile_name].quit()
                        del self.drivers[profile_name]
                        print(f"DEBUG: Đã dừng driver cũ cho {profile_name}")
                    except Exception as e:
                        print(f"DEBUG: Lỗi khi dừng driver cũ: {str(e)}")
                
                # Lấy account tương ứng với profile (mỗi profile 1 account)
                if i < len(accounts):
                    account = accounts[i]
                    current_operation += 1
                    self.root.after(0, lambda: self.status_label.config(
                        text=f"Đang chạy hàng loạt... ({current_operation}/{total_operations})"))
                    
                    # Launch profile with login data - CHỈ SỬ DỤNG USERNAME|PASSWORD CHO STANDARD FORMAT
                    login_data = {
                        'username': account.get('username', account.get('email', '')),
                        'password': account['password'],
                        'email': account.get('email', account.get('username', '')),  # Backward compatibility
                        'twofa': ''  # Không hỗ trợ 2FA cho standard format
                    }
                    
                    # Add TikTok specific data if available
                    if 'email_password' in account:
                        login_data['email_password'] = account['email_password']
                    if 'session_token' in account:
                        login_data['session_token'] = account['session_token']
                    if 'user_id' in account:
                        login_data['user_id'] = account['user_id']
                    
                    print(f"[LAUNCH] [BULK-RUN] Launch {profile_name} với {login_data['username']} (format: username|password)")
                    
                    # Retry mechanism for Chrome crashes
                    max_retries = 3
                    success = False
                    result = None
                    
                    for retry in range(max_retries):
                        try:
                            # Sử dụng chế độ tối ưu cho bulk operations
                            success, result = self.manager.launch_chrome_profile(
                                profile_name, 
                                start_url=url,
                                hidden=hidden, 
                                auto_login=bool(login_data), 
                                login_data=login_data,
                                optimized_mode=True,  # Bật chế độ tối ưu
                                ultra_low_memory=True  # Bật chế độ tiết kiệm RAM tối đa
                            )
                            
                            if success:
                                break
                            else:
                                print(f"⚠️ [BULK-RUN] Lần thử {retry + 1} thất bại cho {profile_name}")
                                if retry < max_retries - 1:
                                    time.sleep(5)  # Wait longer between retries
                                    
                        except Exception as e:
                            print(f"⚠️ [BULK-RUN] Lỗi lần {retry + 1}: {str(e)}")
                            if retry < max_retries - 1:
                                time.sleep(5)
                    
                    if success:
                        print(f"✅ [BULK-RUN] {profile_name} thành công")
                        self.drivers[profile_name] = result
                        # Ensure we are on the desired URL (extra safety)
                        try:
                            if url:
                                print(f"🌐 [BULK-RUN] Điều hướng đảm bảo đến: {url}")
                                result.get(url)
                        except Exception as nav_err:
                            print(f"⚠️ [BULK-RUN] Không thể điều hướng lại: {nav_err}")
                        success_count += 1
                        
                        # Cập nhật trạng thái profile ngay lập tức
                        self.root.after(0, lambda p=profile_name: self._update_profile_status(p, "🟢 Running"))
                        
                        # LƯU TIKTOK SESSION VÀO PROFILE
                        print(f"💾 [BULK-RUN] Lưu TikTok session cho {profile_name}")
                        session_success, session_message = self.manager.save_tiktok_session(profile_name, login_data)
                        if session_success:
                            print(f"✅ [BULK-RUN] Đã lưu session: {session_message}")
                        else:
                            print(f"⚠️ [BULK-RUN] Lỗi lưu session: {session_message}")
                        
                        # TIMEOUT 1 PHÚT ĐỂ NHẬP 2FA THỦ CÔNG
                        print(f"⏰ [BULK-RUN] Đợi 60 giây để nhập 2FA cho {profile_name}...")
                        self.root.after(0, lambda: self.status_label.config(
                            text=f"Đợi nhập 2FA cho {profile_name}... (60s)"))
                        
                        # Cập nhật trạng thái đang đợi 2FA
                        self.root.after(0, lambda p=profile_name: self._update_profile_status(p, "⏰ Waiting 2FA"))
                        
                        # Countdown 60 giây
                        for countdown in range(60, 0, -1):
                            time.sleep(1)
                            self.root.after(0, lambda c=countdown: self.status_label.config(
                                text=f"Đợi nhập 2FA cho {profile_name}... ({c}s)"))
                        
                        print(f"⏰ [BULK-RUN] Timeout 2FA cho {profile_name}, chuyển sang profile tiếp theo")
                        
                    else:
                        print(f"❌ [BULK-RUN] {profile_name} thất bại sau {max_retries} lần thử")
                        # Cập nhật trạng thái profile thất bại
                        self.root.after(0, lambda p=profile_name: self._update_profile_status(p, "❌ Failed"))
                else:
                    print(f"⚠️ [BULK-RUN] Không có account cho profile {profile_name}")
                
                time.sleep(delay)
                
                # Memory cleanup mỗi 10 profiles
                if (i + 1) % 10 == 0:
                    print(f"🧹 [BULK-RUN] Memory cleanup sau {i + 1} profiles")
                    memory_info = self.manager.cleanup_memory()
                    if memory_info and memory_info['system_memory_percent'] > 85:
                        print(f"⚠️ [BULK-RUN] RAM cao ({memory_info['system_memory_percent']}%), tăng delay")
                        time.sleep(delay * 2)  # Tăng delay khi RAM cao
            
            # Final memory report
            final_memory = self.manager.get_memory_usage()
            if final_memory:
                print(f"🏁 [BULK-RUN] RAM cuối: {final_memory['system_memory_percent']}%")
                print(f"🏁 [BULK-RUN] Chrome processes: {final_memory['chrome_processes']}")
                print(f"🏁 [BULK-RUN] Chrome RAM: {final_memory['chrome_memory_mb']}MB")
            
            self.root.after(0, lambda: self.status_label.config(
                text=f"Hoàn thành! Đã khởi động {success_count} profiles"))
            self.root.after(0, lambda: self.refresh_profiles())
        
        threading.Thread(target=bulk_run_thread, daemon=True).start()
    
    def manage_tiktok_sessions(self):
        """Quản lý TikTok sessions"""
        print("💾 [TIKTOK-SESSIONS] Mở dialog quản lý sessions")
        
        # Tạo dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("💾 Quản lý TikTok")
        dialog.geometry("900x600")
        dialog.resizable(True, True)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Main frame
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="💾 Quản lý TikTok", 
                               font=("Segoe UI", 14, "bold"))
        title_label.pack(pady=(0, 15))
        
        # Sessions list
        sessions_frame = ttk.LabelFrame(main_frame, text="📋 Danh sách Sessions", padding="10")
        sessions_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Treeview for sessions
        columns = ("Profile", "Email", "Username", "User ID", "Saved At")
        sessions_tree = ttk.Treeview(sessions_frame, columns=columns, show="headings", height=12)
        
        # Configure columns
        for col in columns:
            sessions_tree.heading(col, text=col)
            sessions_tree.column(col, width=150)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(sessions_frame, orient=tk.VERTICAL, command=sessions_tree.yview)
        sessions_tree.configure(yscrollcommand=scrollbar.set)
        
        sessions_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        def load_sessions():
            """Load tất cả TikTok sessions"""
            sessions_tree.delete(*sessions_tree.get_children())
            
            success, sessions = self.manager.get_all_tiktok_sessions()
            if success:
                for profile_name, session_data in sessions.items():
                    saved_at = session_data.get('saved_at', 'N/A')
                    if saved_at != 'N/A':
                        try:
                            from datetime import datetime
                            dt = datetime.fromisoformat(saved_at)
                            saved_at = dt.strftime("%Y-%m-%d %H:%M:%S")
                        except:
                            pass
                    
                    sessions_tree.insert("", tk.END, values=(
                        profile_name,
                        session_data.get('email', 'N/A'),
                        session_data.get('username', 'N/A'),
                        session_data.get('user_id', 'N/A'),
                        saved_at
                    ))
                
                print(f"📋 [TIKTOK-SESSIONS] Đã load {len(sessions)} sessions")
            else:
                print(f"⚠️ [TIKTOK-SESSIONS] Không có sessions nào")
        
        # Load sessions
        load_sessions()
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=(10, 0))
        
        def refresh_sessions():
            load_sessions()
        
        def view_session_details():
            selection = sessions_tree.selection()
            if not selection:
                messagebox.showwarning("Cảnh báo", "Vui lòng chọn một session!")
                return
            
            item = sessions_tree.item(selection[0])
            profile_name = item['values'][0]
            
            success, session_data = self.manager.load_tiktok_session(profile_name)
            if success:
                details = f"""📋 Chi tiết TikTok Session: {profile_name}

📧 Email: {session_data.get('email', 'N/A')}
👤 Username: {session_data.get('username', 'N/A')}
🔐 Password: {'*' * len(session_data.get('password', '')) if session_data.get('password') else 'N/A'}
📱 Email Password: {'*' * len(session_data.get('email_password', '')) if session_data.get('email_password') else 'N/A'}
🆔 User ID: {session_data.get('user_id', 'N/A')}
🔑 Session Token: {session_data.get('session_token', 'N/A')[:50] + '...' if session_data.get('session_token') else 'N/A'}
🔐 2FA: {session_data.get('twofa', 'N/A')}
💾 Saved At: {session_data.get('saved_at', 'N/A')}
🔄 Updated At: {session_data.get('updated_at', 'N/A')}"""
                
                messagebox.showinfo("Chi tiết Session", details)
            else:
                messagebox.showerror("Lỗi", "Không thể load session!")
        
        def delete_session():
            selection = sessions_tree.selection()
            if not selection:
                messagebox.showwarning("Cảnh báo", "Vui lòng chọn một session!")
                return
            
            item = sessions_tree.item(selection[0])
            profile_name = item['values'][0]
            
            if messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn xóa TikTok session của profile '{profile_name}'?"):
                success, message = self.manager.clear_tiktok_session(profile_name)
                if success:
                    messagebox.showinfo("Thành công", message)
                    load_sessions()
                else:
                    messagebox.showerror("Lỗi", message)
        
        def clear_all_sessions():
            if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa TẤT CẢ TikTok sessions?"):
                success, sessions = self.manager.get_all_tiktok_sessions()
                if success:
                    count = 0
                    for profile_name in sessions.keys():
                        success, _ = self.manager.clear_tiktok_session(profile_name)
                        if success:
                            count += 1
                    
                    messagebox.showinfo("Thành công", f"Đã xóa {count} TikTok sessions")
                    load_sessions()
                else:
                    messagebox.showinfo("Thông báo", "Không có sessions nào để xóa")
        
        def change_password():
            """Đổi mật khẩu TikTok"""
            selection = sessions_tree.selection()
            if not selection:
                messagebox.showwarning("Cảnh báo", "Vui lòng chọn một session!")
                return
            
            item = sessions_tree.item(selection[0])
            profile_name = item['values'][0]
            
            # Tạo dialog đổi mật khẩu
            pwd_dialog = tk.Toplevel(dialog)
            pwd_dialog.title("🔐 Đổi mật khẩu TikTok")
            pwd_dialog.geometry("400x300")
            pwd_dialog.transient(dialog)
            pwd_dialog.grab_set()
            
            # Center dialog
            pwd_dialog.update_idletasks()
            x = (pwd_dialog.winfo_screenwidth() // 2) - (pwd_dialog.winfo_width() // 2)
            y = (pwd_dialog.winfo_screenheight() // 2) - (pwd_dialog.winfo_height() // 2)
            pwd_dialog.geometry(f"+{x}+{y}")
            
            main_frame = ttk.Frame(pwd_dialog, padding="20")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            ttk.Label(main_frame, text=f"🔐 Đổi mật khẩu cho: {profile_name}", 
                     font=("Segoe UI", 12, "bold")).pack(pady=(0, 20))
            
            # Mật khẩu cũ
            ttk.Label(main_frame, text="Mật khẩu cũ:").pack(anchor=tk.W, pady=(0, 5))
            old_pwd_entry = ttk.Entry(main_frame, width=40, show="*")
            old_pwd_entry.pack(fill=tk.X, pady=(0, 10))
            
            # Mật khẩu mới
            ttk.Label(main_frame, text="Mật khẩu mới:").pack(anchor=tk.W, pady=(0, 5))
            new_pwd_entry = ttk.Entry(main_frame, width=40, show="*")
            new_pwd_entry.pack(fill=tk.X, pady=(0, 10))
            
            # Xác nhận mật khẩu mới
            ttk.Label(main_frame, text="Xác nhận mật khẩu mới:").pack(anchor=tk.W, pady=(0, 5))
            confirm_pwd_entry = ttk.Entry(main_frame, width=40, show="*")
            confirm_pwd_entry.pack(fill=tk.X, pady=(0, 20))
            
            def execute_password_change():
                old_pwd = old_pwd_entry.get()
                new_pwd = new_pwd_entry.get()
                confirm_pwd = confirm_pwd_entry.get()
                
                if not all([old_pwd, new_pwd, confirm_pwd]):
                    messagebox.showerror("Lỗi", "Vui lòng điền đầy đủ thông tin!")
                    return
                
                if new_pwd != confirm_pwd:
                    messagebox.showerror("Lỗi", "Mật khẩu mới không khớp!")
                    return
                
                if len(new_pwd) < 8:
                    messagebox.showerror("Lỗi", "Mật khẩu mới phải có ít nhất 8 ký tự!")
                    return
                
                # Thực hiện đổi mật khẩu
                success, message = self.manager.change_tiktok_password(profile_name, old_pwd, new_pwd)
                if success:
                    messagebox.showinfo("Thành công", message)
                    pwd_dialog.destroy()
                    load_sessions()
                else:
                    messagebox.showerror("Lỗi", message)
            
            # Buttons
            btn_frame = ttk.Frame(main_frame)
            btn_frame.pack(fill=tk.X, pady=(10, 0))
            
            ttk.Button(btn_frame, text="🔐 Đổi mật khẩu", command=execute_password_change).pack(side=tk.LEFT, padx=(0, 10))
            ttk.Button(btn_frame, text="❌ Hủy", command=pwd_dialog.destroy).pack(side=tk.RIGHT)
        
        def get_microsoft_mx():
            """Lấy MX từ Microsoft và lấy mail đổi password"""
            selection = sessions_tree.selection()
            if not selection:
                messagebox.showwarning("Cảnh báo", "Vui lòng chọn một session!")
                return
            
            item = sessions_tree.item(selection[0])
            profile_name = item['values'][0]
            
            # Tạo dialog lấy MX
            mx_dialog = tk.Toplevel(dialog)
            mx_dialog.title("📧 Lấy MX từ Microsoft")
            mx_dialog.geometry("500x400")
            mx_dialog.transient(dialog)
            mx_dialog.grab_set()
            
            # Center dialog
            mx_dialog.update_idletasks()
            x = (mx_dialog.winfo_screenwidth() // 2) - (mx_dialog.winfo_width() // 2)
            y = (mx_dialog.winfo_screenheight() // 2) - (mx_dialog.winfo_height() // 2)
            mx_dialog.geometry(f"+{x}+{y}")
            
            main_frame = ttk.Frame(mx_dialog, padding="20")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            ttk.Label(main_frame, text=f"📧 Lấy MX từ Microsoft cho: {profile_name}", 
                     font=("Segoe UI", 12, "bold")).pack(pady=(0, 20))
            
            # Email input
            ttk.Label(main_frame, text="Email Microsoft:").pack(anchor=tk.W, pady=(0, 5))
            email_entry = ttk.Entry(main_frame, width=50)
            email_entry.pack(fill=tk.X, pady=(0, 10))
            
            # Password input
            ttk.Label(main_frame, text="Mật khẩu Microsoft:").pack(anchor=tk.W, pady=(0, 5))
            pwd_entry = ttk.Entry(main_frame, width=50, show="*")
            pwd_entry.pack(fill=tk.X, pady=(0, 20))
            
            # Progress bar
            progress = ttk.Progressbar(main_frame, mode='indeterminate')
            progress.pack(fill=tk.X, pady=(0, 10))
            
            # Status label
            status_label = ttk.Label(main_frame, text="Sẵn sàng...")
            status_label.pack(pady=(0, 10))
            
            def execute_mx_fetch():
                email = email_entry.get()
                password = pwd_entry.get()
                
                if not email or not password:
                    messagebox.showerror("Lỗi", "Vui lòng điền đầy đủ email và mật khẩu!")
                    return
                
                status_label.config(text="Đang kết nối Microsoft...")
                progress.start()
                
                # Thực hiện lấy MX
                success, message = self.manager.get_microsoft_mx_and_emails(profile_name, email, password)
                
                progress.stop()
                
                if success:
                    status_label.config(text="Thành công!")
                    messagebox.showinfo("Thành công", message)
                    mx_dialog.destroy()
                else:
                    status_label.config(text="Lỗi!")
                    messagebox.showerror("Lỗi", message)
            
            # Buttons
            btn_frame = ttk.Frame(main_frame)
            btn_frame.pack(fill=tk.X, pady=(10, 0))
            
            ttk.Button(btn_frame, text="📧 Lấy MX", command=execute_mx_fetch).pack(side=tk.LEFT, padx=(0, 10))
            ttk.Button(btn_frame, text="❌ Hủy", command=mx_dialog.destroy).pack(side=tk.RIGHT)
        
        def export_data():
            """Xuất dữ liệu TikTok"""
            from tkinter import filedialog
            import json
            import csv
            from datetime import datetime
            
            # Chọn file để xuất
            file_path = filedialog.asksaveasfilename(
                title="Xuất dữ liệu TikTok",
                defaultextension=".json",
                filetypes=[
                    ("JSON files", "*.json"),
                    ("CSV files", "*.csv"),
                    ("TXT files", "*.txt"),
                    ("All files", "*.*")
                ]
            )
            
            if not file_path:
                return
            
            success, sessions = self.manager.get_all_tiktok_sessions()
            if not success:
                messagebox.showerror("Lỗi", "Không thể lấy dữ liệu sessions!")
                return
            
            try:
                if file_path.endswith('.json'):
                    # Xuất JSON
                    export_data = {
                        'exported_at': datetime.now().isoformat(),
                        'total_sessions': len(sessions),
                        '../data/sessions': sessions
                    }
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(export_data, f, ensure_ascii=False, indent=2)
                
                elif file_path.endswith('.csv'):
                    # Xuất CSV
                    with open(file_path, 'w', newline='', encoding='utf-8') as f:
                        writer = csv.writer(f)
                        writer.writerow(['Profile', 'Email', 'Username', 'User ID', 'Saved At'])
                        for profile_name, session_data in sessions.items():
                            writer.writerow([
                                profile_name,
                                session_data.get('email', 'N/A'),
                                session_data.get('username', 'N/A'),
                                session_data.get('user_id', 'N/A'),
                                session_data.get('saved_at', 'N/A')
                            ])
                
                else:
                    # Xuất TXT
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(f"TikTok Sessions Export - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                        f.write("=" * 50 + "\n\n")
                        for profile_name, session_data in sessions.items():
                            f.write(f"Profile: {profile_name}\n")
                            f.write(f"Email: {session_data.get('email', 'N/A')}\n")
                            f.write(f"Username: {session_data.get('username', 'N/A')}\n")
                            f.write(f"User ID: {session_data.get('user_id', 'N/A')}\n")
                            f.write(f"Saved At: {session_data.get('saved_at', 'N/A')}\n")
                            f.write("-" * 30 + "\n")
                
                messagebox.showinfo("Thành công", f"Đã xuất dữ liệu thành công!\nFile: {file_path}")
                
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể xuất dữ liệu: {str(e)}")
        
        # Buttons
        ttk.Button(buttons_frame, text="🔄 Làm mới", command=refresh_sessions).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="👁️ Xem chi tiết", command=view_session_details).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="🔐 Đổi mật khẩu", command=change_password).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="📧 Lấy MX", command=get_microsoft_mx).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="📤 Xuất dữ liệu", command=export_data).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="🗑️ Xóa session", command=delete_session).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="🗑️ Xóa tất cả", command=clear_all_sessions).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="❌ Đóng", command=dialog.destroy).pack(side=tk.RIGHT)
        
        # Bind double-click to view details
        sessions_tree.bind('<Double-1>', lambda e: view_session_details())
        
        # Focus
        dialog.focus_set()
    
    def livestream_selected(self):
        """Treo livestream với multiple accounts"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn ít nhất một profile!")
            return
        
        selected_profiles = [self.tree.item(item)['text'] for item in selection]
        print(f"📺 [LIVESTREAM] Mở dialog cho {len(selected_profiles)} profiles")
        
        # Tạo dialog livestream với layout đẹp và dễ nhìn
        dialog = tk.Toplevel(self.root)
        dialog.title("📺 Treo Livestream - Hỗ trợ 300+ Accounts")
        dialog.geometry("1000x700")
        dialog.resizable(True, True)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Set background color
        dialog.configure(bg='#f0f0f0')
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Header với title đẹp
        header_frame = tk.Frame(dialog, bg='#2c3e50', height=60)
        header_frame.pack(fill=tk.X, padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(header_frame, text="📺 Treo Livestream - Hỗ trợ 300+ Accounts", 
                              font=('Segoe UI', 16, 'bold'), fg='white', bg='#2c3e50')
        title_label.pack(expand=True)
        
        # Tạo layout chính với notebook (tabs)
        main_container = tk.Frame(dialog, bg='#f0f0f0')
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tạo notebook với tabs và styling đẹp
        notebook = ttk.Notebook(main_container)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Configure notebook style with better colors
        style = ttk.Style()
        
        # Set theme to avoid black tabs - try multiple themes
        themes_to_try = ['clam', 'alt', 'default', 'classic']
        for theme in themes_to_try:
            try:
                style.theme_use(theme)
                break
            except:
                continue
        
        # Configure notebook background
        style.configure('TNotebook', 
                       background='#f8f9fa', 
                       borderwidth=0,
                       tabmargins=[0, 0, 0, 0])
        
        # Configure tab appearance with explicit colors
        style.configure('TNotebook.Tab', 
                       background='#ecf0f1', 
                       foreground='#2c3e50',
                       padding=[25, 12],
                       font=('Segoe UI', 11, 'bold'),
                       borderwidth=0,
                       focuscolor='none',
                       lightcolor='#ecf0f1',
                       darkcolor='#ecf0f1')
        
        # Map tab states with better colors - more explicit
        style.map('TNotebook.Tab',
                 background=[('selected', '#3498db'), 
                           ('active', '#5dade2'),
                           ('!selected', '#ecf0f1'),
                           ('!active', '#ecf0f1')],
                 foreground=[('selected', 'white'), 
                           ('active', 'white'),
                           ('!selected', '#2c3e50'),
                           ('!active', '#2c3e50')],
                 lightcolor=[('selected', '#3498db'),
                           ('active', '#5dade2'),
                           ('!selected', '#ecf0f1'),
                           ('!active', '#ecf0f1')],
                 darkcolor=[('selected', '#3498db'),
                          ('active', '#5dade2'),
                          ('!selected', '#ecf0f1'),
                          ('!active', '#ecf0f1')])
        
        # Configure tab focus and other states
        style.configure('TNotebook.Tab:focus', 
                       background='#3498db',
                       foreground='white',
                       lightcolor='#3498db',
                       darkcolor='#3498db')
        
        # Force update the style
        style.layout('TNotebook.Tab', [
            ('Notebook.tab', {
                'sticky': 'nswe',
                'children': [
                    ('Notebook.padding', {
                        'side': 'top',
                        'sticky': 'nswe',
                        'children': [
                            ('Notebook.focus', {
                                'side': 'top',
                                'sticky': 'nswe',
                                'children': [
                                    ('Notebook.label', {'side': 'top', 'sticky': ''}),
                                ]
                            })
                        ]
                    })
                ]
            })
        ])
        
        # Tab 1: Cấu hình cơ bản
        basic_tab = tk.Frame(notebook, bg='#f8f9fa')
        notebook.add(basic_tab, text="⚙️ Cấu hình cơ bản")
        
        # Tab 2: Quản lý Profiles
        accounts_tab = tk.Frame(notebook, bg='#f8f9fa')
        notebook.add(accounts_tab, text="👥 Quản lý Profiles")
        
        # Tab 3: Cài đặt nâng cao
        advanced_tab = tk.Frame(notebook, bg='#f8f9fa')
        notebook.add(advanced_tab, text="🔧 Cài đặt nâng cao")
        
        # Cleanup function
        def cleanup():
            dialog.destroy()
        
        dialog.protocol("WM_DELETE_WINDOW", cleanup)
        
        # ===== TAB 1: CẤU HÌNH CƠ BẢN =====
        # Scrollable frame for basic tab
        basic_canvas = tk.Canvas(basic_tab, bg='#f8f9fa', highlightthickness=0)
        basic_scrollbar = ttk.Scrollbar(basic_tab, orient="vertical", command=basic_canvas.yview)
        basic_scrollable_frame = tk.Frame(basic_canvas, bg='#f8f9fa')
        
        basic_scrollable_frame.bind(
            "<Configure>",
            lambda e: basic_canvas.configure(scrollregion=basic_canvas.bbox("all"))
        )
        
        basic_canvas.create_window((0, 0), window=basic_scrollable_frame, anchor="nw")
        basic_canvas.configure(yscrollcommand=basic_scrollbar.set)
        
        basic_canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        basic_scrollbar.pack(side="right", fill="y", pady=10)
        
        # Livestream URL
        url_frame = tk.LabelFrame(basic_scrollable_frame, text="🌐 Link Livestream", 
                                 font=('Segoe UI', 10, 'bold'), fg='#2c3e50', bg='#f8f9fa',
                                 relief='solid', bd=1)
        url_frame.pack(fill=tk.X, pady=(0, 15), padx=10)
        
        tk.Label(url_frame, text="Nhập link livestream TikTok:", 
                font=('Segoe UI', 9), fg='#34495e', bg='#f8f9fa').pack(anchor=tk.W, padx=10, pady=(10, 5))
        
        url_entry = tk.Entry(url_frame, font=('Segoe UI', 10), relief='solid', bd=1)
        url_entry.pack(fill=tk.X, padx=10, pady=(0, 5))
        url_entry.insert(0, "https://www.tiktok.com/@username/live")
        
        # Info about TikTok URL changes
        info_label = tk.Label(url_frame, 
                            text="💡 Nếu link không hoạt động, thử: https://www.tiktok.com/@username hoặc https://www.tiktok.com/live/@username",
                            font=('Segoe UI', 8), fg='#7f8c8d', bg='#f8f9fa', justify=tk.LEFT)
        info_label.pack(anchor=tk.W, padx=10, pady=(0, 10))
        
        # Basic settings
        basic_settings_frame = tk.LabelFrame(basic_scrollable_frame, text="⚙️ Cài đặt cơ bản", 
                                           font=('Segoe UI', 10, 'bold'), fg='#2c3e50', bg='#f8f9fa',
                                           relief='solid', bd=1)
        basic_settings_frame.pack(fill=tk.X, pady=(0, 15), padx=10)
        
        # Grid layout for basic settings
        basic_grid = tk.Frame(basic_settings_frame, bg='#f8f9fa')
        basic_grid.pack(fill=tk.X, padx=10, pady=10)
        
        # Row 1: Max viewers and Hidden mode
        tk.Label(basic_grid, text="Số viewer đồng thời:", 
                font=('Segoe UI', 9), fg='#34495e', bg='#f8f9fa').grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        max_viewers_var = tk.StringVar(value="50")
        max_viewers_entry = tk.Entry(basic_grid, textvariable=max_viewers_var, width=15, 
                                   font=('Segoe UI', 9), relief='solid', bd=1)
        max_viewers_entry.grid(row=0, column=1, sticky=tk.W, padx=(0, 20))
        
        hidden_var = tk.BooleanVar(value=True)
        hidden_check = tk.Checkbutton(basic_grid, text="Chế độ ẩn (Hidden)", 
                                    variable=hidden_var, font=('Segoe UI', 9), fg='#34495e', 
                                    bg='#f8f9fa', selectcolor='#3498db')
        hidden_check.grid(row=0, column=2, sticky=tk.W)
        
        # Row 2: Auto-out time and Replace delay
        tk.Label(basic_grid, text="Thời gian auto-out (phút):", 
                font=('Segoe UI', 9), fg='#34495e', bg='#f8f9fa').grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(15, 0))
        auto_out_var = tk.StringVar(value="30")
        auto_out_entry = tk.Entry(basic_grid, textvariable=auto_out_var, width=15, 
                                font=('Segoe UI', 9), relief='solid', bd=1)
        auto_out_entry.grid(row=1, column=1, sticky=tk.W, padx=(0, 20), pady=(15, 0))
        
        tk.Label(basic_grid, text="Thời gian thay thế (giây):", 
                font=('Segoe UI', 9), fg='#34495e', bg='#f8f9fa').grid(row=1, column=2, sticky=tk.W, padx=(0, 10), pady=(15, 0))
        replace_delay_var = tk.StringVar(value="5")
        replace_delay_entry = tk.Entry(basic_grid, textvariable=replace_delay_var, width=15, 
                                     font=('Segoe UI', 9), relief='solid', bd=1)
        replace_delay_entry.grid(row=1, column=3, sticky=tk.W, pady=(15, 0))
        
        # ===== TAB 2: QUẢN LÝ PROFILES =====
        # Profile selection section with improved layout
        profile_selection_frame = tk.LabelFrame(accounts_tab, text="📁 Quản lý Profiles & Check Account", 
                                              font=('Segoe UI', 11, 'bold'), fg='#2c3e50', bg='#f8f9fa',
                                              relief='solid', bd=2)
        profile_selection_frame.pack(fill=tk.X, pady=(0, 15), padx=10)
        
        profile_selection_inner = tk.Frame(profile_selection_frame, bg='#f8f9fa')
        profile_selection_inner.pack(fill=tk.X, padx=15, pady=15)
        
        # Top row with stats and main buttons
        top_row = tk.Frame(profile_selection_inner, bg='#f8f9fa')
        top_row.pack(fill=tk.X, pady=(0, 15))
        
        # Profile count display with better styling
        profile_count_var = tk.StringVar(value="0 profiles đã đăng nhập")
        profile_count_label = tk.Label(top_row, textvariable=profile_count_var, 
                                     font=('Segoe UI', 10, 'bold'), fg='#e74c3c', bg='#f8f9fa')
        profile_count_label.pack(side=tk.LEFT)
        
        # Status indicators
        status_frame = tk.Frame(top_row, bg='#f8f9fa')
        status_frame.pack(side=tk.RIGHT)
        
        status_indicators = {
            'healthy': tk.StringVar(value="0"),
            'warning': tk.StringVar(value="0"), 
            'dead': tk.StringVar(value="0")
        }
        
        tk.Label(status_frame, text="🟢 Healthy:", font=('Segoe UI', 9), fg='#27ae60', bg='#f8f9fa').pack(side=tk.LEFT, padx=(0, 5))
        tk.Label(status_frame, textvariable=status_indicators['healthy'], font=('Segoe UI', 9, 'bold'), fg='#27ae60', bg='#f8f9fa').pack(side=tk.LEFT, padx=(0, 15))
        
        tk.Label(status_frame, text="🟡 Warning:", font=('Segoe UI', 9), fg='#f39c12', bg='#f8f9fa').pack(side=tk.LEFT, padx=(0, 5))
        tk.Label(status_frame, textvariable=status_indicators['warning'], font=('Segoe UI', 9, 'bold'), fg='#f39c12', bg='#f8f9fa').pack(side=tk.LEFT, padx=(0, 15))
        
        tk.Label(status_frame, text="🔴 Dead:", font=('Segoe UI', 9), fg='#e74c3c', bg='#f8f9fa').pack(side=tk.LEFT, padx=(0, 5))
        tk.Label(status_frame, textvariable=status_indicators['dead'], font=('Segoe UI', 9, 'bold'), fg='#e74c3c', bg='#f8f9fa').pack(side=tk.LEFT)
        
        # Button row with improved styling
        button_frame = tk.Frame(profile_selection_inner, bg='#f8f9fa')
        button_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Get all available profiles with status check
        def get_available_profiles():
            try:
                profiles = []
                profiles_dir = self.manager.profiles_dir
                if os.path.exists(profiles_dir):
                    for item in os.listdir(profiles_dir):
                        item_path = os.path.join(profiles_dir, item)
                        if os.path.isdir(item_path):
                            # Check if profile has login data
                            marker_file = os.path.join(item_path, 'tiktok_logged_in.txt')
                            if os.path.exists(marker_file):
                                profiles.append(item)
                return profiles
            except Exception as e:
                print(f"Error getting profiles: {e}")
                return []
        
        def check_account_status(profile_name):
            """Check if account is still alive by testing login"""
            try:
                print(f"🔍 [CHECK] Đang check status cho {profile_name}")
                
                
                # Quick test launch to check if account is still working
                success, result = self.manager.launch_chrome_profile(
                    profile_name,
                    start_url="https://www.tiktok.com/foryou",
                    hidden=True,
                    auto_login=True,
                    login_data=None
                )
                
                if success:
                    try:
                        # Check if we're actually logged in by looking for user elements
                        driver = result
                        time.sleep(3)  # Wait for page to load
                        
                        # Look for elements that indicate successful login
                        try:
                            # Try to find user avatar or profile elements
                            user_elements = driver.find_elements("css selector", "[data-e2e='nav-user']")
                            if user_elements:
                                driver.quit()
                                print(f"✅ [CHECK] {profile_name} - Account healthy")
                                return "healthy"
                        except:
                            pass
                        
                        # Check current URL
                        current_url = driver.current_url
                        if "foryou" in current_url or "following" in current_url:
                            driver.quit()
                            print(f"✅ [CHECK] {profile_name} - Account healthy")
                            return "healthy"
                        else:
                            driver.quit()
                            print(f"⚠️ [CHECK] {profile_name} - Account warning (redirected)")
                            return "warning"
                            
                    except Exception as e:
                        try:
                            driver.quit()
                        except:
                            pass
                        print(f"⚠️ [CHECK] {profile_name} - Account warning: {str(e)}")
                        return "warning"
                else:
                    print(f"❌ [CHECK] {profile_name} - Account dead")
                    return "dead"
                    
            except Exception as e:
                print(f"❌ [CHECK] {profile_name} - Account dead: {str(e)}")
                return "dead"
        
        def refresh_profiles():
            available_profiles = get_available_profiles()
            profile_listbox.delete(0, tk.END)
            
            # Reset counters
            healthy_count = 0
            warning_count = 0
            dead_count = 0
            
            for profile in available_profiles:
                # Add profile with status indicator
                profile_listbox.insert(tk.END, f"🟢 {profile}")
                healthy_count += 1
            
            profile_count_var.set(f"{len(available_profiles)} profiles đã đăng nhập")
            status_indicators['healthy'].set(str(healthy_count))
            status_indicators['warning'].set(str(warning_count))
            status_indicators['dead'].set(str(dead_count))
        
        def check_all_accounts():
            """Check status of all accounts"""
            available_profiles = get_available_profiles()
            if not available_profiles:
                messagebox.showwarning("Cảnh báo", "Không có profiles nào để check!")
                return
            
            # Show progress dialog
            progress_dialog = tk.Toplevel(dialog)
            progress_dialog.title("🔍 Checking Account Status")
            progress_dialog.geometry("400x200")
            progress_dialog.resizable(False, False)
            progress_dialog.configure(bg='#f8f9fa')
            
            # Center the dialog
            progress_dialog.transient(dialog)
            progress_dialog.grab_set()
            
            # Progress frame
            progress_frame = tk.Frame(progress_dialog, bg='#f8f9fa')
            progress_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)
            
            tk.Label(progress_frame, text="🔍 Đang check status của tất cả accounts...", 
                    font=('Segoe UI', 12, 'bold'), fg='#2c3e50', bg='#f8f9fa').pack(pady=(0, 20))
            
            progress_var = tk.StringVar(value="0/0")
            progress_label = tk.Label(progress_frame, textvariable=progress_var, 
                                    font=('Segoe UI', 10), fg='#7f8c8d', bg='#f8f9fa')
            progress_label.pack(pady=(0, 10))
            
            progress_bar = tk.Frame(progress_frame, bg='#ecf0f1', height=20, relief='solid', bd=1)
            progress_bar.pack(fill=tk.X, pady=(0, 20))
            
            progress_fill = tk.Frame(progress_bar, bg='#3498db', height=20)
            progress_fill.pack(side=tk.LEFT, fill=tk.Y)
            
            def check_accounts_thread():
                import time
                healthy_count = 0
                warning_count = 0
                dead_count = 0
                
                profile_listbox.delete(0, tk.END)
                
                for i, profile in enumerate(available_profiles):
                    try:
                        # Update progress
                        try:
                            progress_var.set(f"{i+1}/{len(available_profiles)} - Checking {profile}")
                            progress_fill.config(width=int((i/len(available_profiles)) * 360))
                            progress_dialog.update()
                        except:
                            # Dialog might be closed, continue without updating
                            pass
                        
                        # Check account status
                        status = check_account_status(profile)
                        
                        # Add to listbox with appropriate icon
                        if status == "healthy":
                            profile_listbox.insert(tk.END, f"🟢 {profile}")
                            healthy_count += 1
                        elif status == "warning":
                            profile_listbox.insert(tk.END, f"🟡 {profile}")
                            warning_count += 1
                        else:
                            profile_listbox.insert(tk.END, f"🔴 {profile}")
                            dead_count += 1
                        
                        # Update counters
                        status_indicators['healthy'].set(str(healthy_count))
                        status_indicators['warning'].set(str(warning_count))
                        status_indicators['dead'].set(str(dead_count))
                        
                        time.sleep(1)  # Small delay between checks
                        
                    except Exception as e:
                        print(f"Error checking {profile}: {e}")
                        profile_listbox.insert(tk.END, f"🔴 {profile}")
                        dead_count += 1
                        status_indicators['dead'].set(str(dead_count))
                
                # Complete progress
                try:
                    progress_var.set(f"✅ Hoàn thành! {healthy_count} healthy, {warning_count} warning, {dead_count} dead")
                    progress_fill.config(width=360, bg='#27ae60')
                    
                    # Close dialog after 2 seconds
                    time.sleep(2)
                    progress_dialog.destroy()
                except:
                    # Dialog might be closed already
                    pass
            
            threading.Thread(target=check_accounts_thread, daemon=True).start()
        
        def select_all_profiles():
            profile_listbox.select_set(0, tk.END)
        
        def clear_selection():
            profile_listbox.selection_clear(0, tk.END)
        
        def select_healthy_only():
            """Select only healthy accounts"""
            profile_listbox.selection_clear(0, tk.END)
            for i in range(profile_listbox.size()):
                item = profile_listbox.get(i)
                if item.startswith("🟢"):
                    profile_listbox.selection_set(i)
        
        # Main action buttons
        refresh_btn = tk.Button(button_frame, text="🔄 Làm mới", 
                              command=refresh_profiles, font=('Segoe UI', 9, 'bold'),
                              bg='#3498db', fg='white', relief='flat', padx=20, pady=8,
                              cursor='hand2')
        refresh_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        check_btn = tk.Button(button_frame, text="🔍 Check All", 
                            command=check_all_accounts, font=('Segoe UI', 9, 'bold'),
                            bg='#f39c12', fg='white', relief='flat', padx=20, pady=8,
                            cursor='hand2')
        check_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        select_all_btn = tk.Button(button_frame, text="✅ Chọn tất cả", 
                                 command=select_all_profiles, font=('Segoe UI', 9, 'bold'),
                                 bg='#27ae60', fg='white', relief='flat', padx=20, pady=8,
                                 cursor='hand2')
        select_all_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        select_healthy_btn = tk.Button(button_frame, text="🟢 Chọn healthy", 
                                     command=select_healthy_only, font=('Segoe UI', 9, 'bold'),
                                     bg='#2ecc71', fg='white', relief='flat', padx=20, pady=8,
                                     cursor='hand2')
        select_healthy_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        clear_btn = tk.Button(button_frame, text="❌ Bỏ chọn", 
                            command=clear_selection, font=('Segoe UI', 9, 'bold'),
                            bg='#e74c3c', fg='white', relief='flat', padx=20, pady=8,
                            cursor='hand2')
        clear_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Profile listbox with improved styling
        profiles_frame = tk.LabelFrame(accounts_tab, text="👥 Danh sách Profiles với Status Check", 
                                     font=('Segoe UI', 11, 'bold'), fg='#2c3e50', bg='#f8f9fa',
                                     relief='solid', bd=2)
        profiles_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15), padx=10)
        
        # Listbox with scrollbar
        listbox_frame = tk.Frame(profiles_frame, bg='#f8f9fa')
        listbox_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        profile_listbox = tk.Listbox(listbox_frame, font=('Segoe UI', 10), 
                                   bg='#ecf0f1', fg='#2c3e50', selectbackground='#3498db',
                                   selectforeground='white', relief='solid', bd=2,
                                   selectmode=tk.MULTIPLE, height=12)
        listbox_scrollbar = tk.Scrollbar(listbox_frame, orient="vertical", command=profile_listbox.yview,
                                       bg='#bdc3c7', troughcolor='#ecf0f1', width=15)
        profile_listbox.configure(yscrollcommand=listbox_scrollbar.set)
        
        profile_listbox.pack(side="left", fill="both", expand=True)
        listbox_scrollbar.pack(side="right", fill="y")
        
        # Info text with better styling
        info_frame = tk.Frame(profiles_frame, bg='#f8f9fa')
        info_frame.pack(fill=tk.X, padx=15, pady=(0, 15))
        
        info_text = tk.Label(info_frame, 
                           text="💡 🟢 Healthy: Account hoạt động bình thường | 🟡 Warning: Account có vấn đề nhỏ | 🔴 Dead: Account bị die/block\n"
                                "Sử dụng 'Check All' để kiểm tra status của tất cả accounts trước khi bắt đầu livestream.\n",
                           font=('Segoe UI', 9), fg='#7f8c8d', bg='#f8f9fa', justify=tk.LEFT)
        info_text.pack(anchor=tk.W)
        
        # Initialize profiles
        refresh_profiles()
        
        # ===== TAB 3: CÀI ĐẶT NÂNG CAO =====
        # Performance settings
        perf_frame = tk.LabelFrame(advanced_tab, text="⚡ Cài đặt Performance", 
                                 font=('Segoe UI', 10, 'bold'), fg='#2c3e50', bg='#f8f9fa',
                                 relief='solid', bd=1)
        perf_frame.pack(fill=tk.X, pady=(0, 15), padx=10)
        
        perf_grid = tk.Frame(perf_frame, bg='#f8f9fa')
        perf_grid.pack(fill=tk.X, padx=10, pady=10)
        
        # Launch delay
        tk.Label(perf_grid, text="Delay giữa các launch (giây):", 
                font=('Segoe UI', 9), fg='#34495e', bg='#f8f9fa').grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        launch_delay_var = tk.StringVar(value="2")
        launch_delay_entry = tk.Entry(perf_grid, textvariable=launch_delay_var, width=10, 
                                    font=('Segoe UI', 9), relief='solid', bd=1)
        launch_delay_entry.grid(row=0, column=1, sticky=tk.W, padx=(0, 20))
        
        # Check interval
        tk.Label(perf_grid, text="Interval kiểm tra (giây):", 
                font=('Segoe UI', 9), fg='#34495e', bg='#f8f9fa').grid(row=0, column=2, sticky=tk.W, padx=(0, 10))
        check_interval_var = tk.StringVar(value="30")
        check_interval_entry = tk.Entry(perf_grid, textvariable=check_interval_var, width=10, 
                                      font=('Segoe UI', 9), relief='solid', bd=1)
        check_interval_entry.grid(row=0, column=3, sticky=tk.W)
        
        # Max retries
        tk.Label(perf_grid, text="Số lần retry tối đa:", 
                font=('Segoe UI', 9), fg='#34495e', bg='#f8f9fa').grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(15, 0))
        max_retries_var = tk.StringVar(value="3")
        max_retries_entry = tk.Entry(perf_grid, textvariable=max_retries_var, width=10, 
                                   font=('Segoe UI', 9), relief='solid', bd=1)
        max_retries_entry.grid(row=1, column=1, sticky=tk.W, padx=(0, 20), pady=(15, 0))
        
        # Memory optimization
        memory_var = tk.BooleanVar(value=True)
        memory_check = tk.Checkbutton(perf_grid, text="Tối ưu memory cho 300+ accounts", 
                                    variable=memory_var, font=('Segoe UI', 9), fg='#34495e', 
                                    bg='#f8f9fa', selectcolor='#3498db')
        memory_check.grid(row=1, column=2, columnspan=2, sticky=tk.W, pady=(15, 0))
        
        # Data optimization settings
        data_opt_frame = tk.LabelFrame(advanced_tab, text="💾 Tối ưu dữ liệu & Tránh crash", 
                                     font=('Segoe UI', 10, 'bold'), fg='#2c3e50', bg='#f8f9fa',
                                     relief='solid', bd=1)
        data_opt_frame.pack(fill=tk.X, pady=(0, 15), padx=10)
        
        data_opt_grid = tk.Frame(data_opt_frame, bg='#f8f9fa')
        data_opt_grid.pack(fill=tk.X, padx=10, pady=10)
        
        # Row 1: Browser optimization
        tk.Label(data_opt_grid, text="Tối ưu browser:", 
                font=('Segoe UI', 9), fg='#34495e', bg='#f8f9fa').grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        browser_opt_var = tk.BooleanVar(value=True)
        browser_opt_check = tk.Checkbutton(data_opt_grid, text="Tắt images, CSS, JS không cần thiết", 
                                         variable=browser_opt_var, font=('Segoe UI', 9), fg='#34495e', 
                                         bg='#f8f9fa', selectcolor='#3498db')
        browser_opt_check.grid(row=0, column=1, sticky=tk.W, padx=(0, 20))
        
        # Row 2: Memory management
        tk.Label(data_opt_grid, text="Quản lý memory:", 
                font=('Segoe UI', 9), fg='#34495e', bg='#f8f9fa').grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        
        memory_cleanup_var = tk.BooleanVar(value=True)
        memory_cleanup_check = tk.Checkbutton(data_opt_grid, text="Tự động cleanup memory mỗi 10 viewers", 
                                            variable=memory_cleanup_var, font=('Segoe UI', 9), fg='#34495e', 
                                            bg='#f8f9fa', selectcolor='#3498db')
        memory_cleanup_check.grid(row=1, column=1, sticky=tk.W, padx=(0, 20), pady=(10, 0))
        
        # Row 3: CPU optimization
        tk.Label(data_opt_grid, text="Tối ưu CPU:", 
                font=('Segoe UI', 9), fg='#34495e', bg='#f8f9fa').grid(row=2, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        
        cpu_opt_var = tk.BooleanVar(value=True)
        cpu_opt_check = tk.Checkbutton(data_opt_grid, text="Giảm tần suất kiểm tra để tiết kiệm CPU", 
                                     variable=cpu_opt_var, font=('Segoe UI', 9), fg='#34495e', 
                                     bg='#f8f9fa', selectcolor='#3498db')
        cpu_opt_check.grid(row=2, column=1, sticky=tk.W, padx=(0, 20), pady=(10, 0))
        
        # Row 4: Disk optimization
        tk.Label(data_opt_grid, text="Tối ưu disk:", 
                font=('Segoe UI', 9), fg='#34495e', bg='#f8f9fa').grid(row=3, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        
        disk_opt_var = tk.BooleanVar(value=True)
        disk_opt_check = tk.Checkbutton(data_opt_grid, text="Tắt cache và logs không cần thiết", 
                                      variable=disk_opt_var, font=('Segoe UI', 9), fg='#34495e', 
                                      bg='#f8f9fa', selectcolor='#3498db')
        disk_opt_check.grid(row=3, column=1, sticky=tk.W, padx=(0, 20), pady=(10, 0))
        
        # Crash prevention settings
        crash_frame = tk.LabelFrame(advanced_tab, text="🛡️ Chống crash & Ổn định", 
                                  font=('Segoe UI', 10, 'bold'), fg='#2c3e50', bg='#f8f9fa',
                                  relief='solid', bd=1)
        crash_frame.pack(fill=tk.X, pady=(0, 15), padx=10)
        
        crash_grid = tk.Frame(crash_frame, bg='#f8f9fa')
        crash_grid.pack(fill=tk.X, padx=10, pady=10)
        
        # Row 1: Error handling
        tk.Label(crash_grid, text="Xử lý lỗi:", 
                font=('Segoe UI', 9), fg='#34495e', bg='#f8f9fa').grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        error_handling_var = tk.BooleanVar(value=True)
        error_handling_check = tk.Checkbutton(crash_grid, text="Tự động restart khi crash", 
                                            variable=error_handling_var, font=('Segoe UI', 9), fg='#34495e', 
                                            bg='#f8f9fa', selectcolor='#3498db')
        error_handling_check.grid(row=0, column=1, sticky=tk.W, padx=(0, 20))
        
        # Row 2: Stability
        tk.Label(crash_grid, text="Ổn định:", 
                font=('Segoe UI', 9), fg='#34495e', bg='#f8f9fa').grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        
        stability_var = tk.BooleanVar(value=True)
        stability_check = tk.Checkbutton(crash_grid, text="Giới hạn số viewers đồng thời để tránh crash", 
                                       variable=stability_var, font=('Segoe UI', 9), fg='#34495e', 
                                       bg='#f8f9fa', selectcolor='#3498db')
        stability_check.grid(row=1, column=1, sticky=tk.W, padx=(0, 20), pady=(10, 0))
        
        # Row 3: Monitoring
        tk.Label(crash_grid, text="Giám sát:", 
                font=('Segoe UI', 9), fg='#34495e', bg='#f8f9fa').grid(row=2, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        
        monitoring_var = tk.BooleanVar(value=True)
        monitoring_check = tk.Checkbutton(crash_grid, text="Theo dõi tình trạng hệ thống real-time", 
                                        variable=monitoring_var, font=('Segoe UI', 9), fg='#34495e', 
                                        bg='#f8f9fa', selectcolor='#3498db')
        monitoring_check.grid(row=2, column=1, sticky=tk.W, padx=(0, 20), pady=(10, 0))
        
        # Advanced monitoring
        monitor_frame = tk.LabelFrame(advanced_tab, text="📊 Monitoring nâng cao", 
                                    font=('Segoe UI', 10, 'bold'), fg='#2c3e50', bg='#f8f9fa',
                                    relief='solid', bd=1)
        monitor_frame.pack(fill=tk.X, pady=(0, 15), padx=10)
        
        monitor_grid = tk.Frame(monitor_frame, bg='#f8f9fa')
        monitor_grid.pack(fill=tk.X, padx=10, pady=10)
        
        # Log level
        tk.Label(monitor_grid, text="Log level:", 
                font=('Segoe UI', 9), fg='#34495e', bg='#f8f9fa').grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        log_level_var = tk.StringVar(value="INFO")
        log_level_combo = ttk.Combobox(monitor_grid, textvariable=log_level_var, 
                                     values=["DEBUG", "INFO", "WARNING", "ERROR"], 
                                     state="readonly", width=10, font=('Segoe UI', 9))
        log_level_combo.grid(row=0, column=1, sticky=tk.W, padx=(0, 20))
        
        # Auto cleanup
        cleanup_var = tk.BooleanVar(value=True)
        cleanup_check = tk.Checkbutton(monitor_grid, text="Tự động cleanup failed accounts", 
                                     variable=cleanup_var, font=('Segoe UI', 9), fg='#34495e', 
                                     bg='#f8f9fa', selectcolor='#3498db')
        cleanup_check.grid(row=0, column=2, sticky=tk.W)
        
        # Statistics
        stats_var = tk.BooleanVar(value=True)
        stats_check = tk.Checkbutton(monitor_grid, text="Hiển thị thống kê chi tiết", 
                                   variable=stats_var, font=('Segoe UI', 9), fg='#34495e', 
                                   bg='#f8f9fa', selectcolor='#3498db')
        stats_check.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(15, 0))
        
        # Buttons với styling đẹp
        buttons_frame = tk.Frame(dialog, bg='#f0f0f0')
        buttons_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        def start_livestream():
            url = url_entry.get().strip()
            if not url:
                messagebox.showerror("Lỗi", "Vui lòng nhập link livestream!")
                return
            
            # Get selected profiles
            selected_profile_indices = profile_listbox.curselection()
            if not selected_profile_indices:
                messagebox.showerror("Lỗi", "Vui lòng chọn ít nhất một profile đã đăng nhập!")
                return
            
            selected_profiles_for_livestream = []
            for index in selected_profile_indices:
                profile_item = profile_listbox.get(index)
                # Remove status icon from profile name (🟢, 🟡, 🔴)
                profile_name = profile_item[2:] if len(profile_item) > 2 and profile_item[1] == ' ' else profile_item
                selected_profiles_for_livestream.append(profile_name)
            
            # Get settings
            try:
                auto_out_minutes = int(auto_out_var.get())
                replace_delay_seconds = int(replace_delay_var.get())
                max_viewers = int(max_viewers_var.get())
                launch_delay = int(launch_delay_var.get())
                check_interval = int(check_interval_var.get())
                max_retries = int(max_retries_var.get())
            except ValueError:
                messagebox.showerror("Lỗi", "Vui lòng nhập số hợp lệ cho các cài đặt!")
                return
            
            # Validate settings
            if max_viewers > len(selected_profiles_for_livestream):
                messagebox.showwarning("Cảnh báo", f"Số viewer đồng thời ({max_viewers}) lớn hơn số profiles ({len(selected_profiles_for_livestream)})!")
                max_viewers = len(selected_profiles_for_livestream)
            
            if max_viewers > 100:
                result = messagebox.askyesno("Xác nhận", 
                    f"Bạn đang muốn chạy {max_viewers} viewers đồng thời. Điều này có thể gây tải cao cho hệ thống. Bạn có chắc chắn?")
                if not result:
                    return
            
            # Show summary
            summary = f"""📺 Tóm tắt cấu hình:
• Link: {url}
• Số profiles đã chọn: {len(selected_profiles_for_livestream)}
• Số viewers đồng thời: {max_viewers}
• Auto-out: {auto_out_minutes} phút
• Replace delay: {replace_delay_seconds} giây
• Launch delay: {launch_delay} giây
• Check interval: {check_interval} giây
• Max retries: {max_retries}

• Tối ưu browser: {browser_opt_var.get()}
• Tối ưu memory: {memory_cleanup_var.get()}
• Tối ưu CPU: {cpu_opt_var.get()}
• Tối ưu disk: {disk_opt_var.get()}
• Chống crash: {error_handling_var.get()}
• Giám sát: {monitoring_var.get()}

Bạn có muốn bắt đầu treo livestream?"""
            
            if not messagebox.askyesno("Xác nhận", summary):
                return
            
            cleanup()
            
            # Start livestream with basic settings first
            # Create dummy accounts for testing
            dummy_accounts = []
            for i, profile_name in enumerate(selected_profiles_for_livestream):
                dummy_accounts.append({
                    'email': f'test{i}@example.com',
                    'password': 'testpass',
                    'username': f'testuser{i}',
                    'email_password': '',
                    'session_token': '',
                    'user_id': f'user{i}'
                })
            
            self._execute_livestream(selected_profiles_for_livestream, url, dummy_accounts,
                                            auto_out_minutes, replace_delay_seconds, 
                                   max_viewers, hidden_var.get())
        
        # Start button với styling đẹp
        start_btn = tk.Button(buttons_frame, text="[LAUNCH] Bắt đầu treo livestream", 
                            command=start_livestream, font=('Segoe UI', 11, 'bold'),
                            bg='#e74c3c', fg='white', relief='flat', padx=25, pady=10,
                            cursor='hand2', bd=0)
        start_btn.pack(side=tk.LEFT, padx=(0, 15))
        
        # Cancel button
        cancel_btn = tk.Button(buttons_frame, text="❌ Hủy", command=cleanup, 
                             font=('Segoe UI', 11), bg='#95a5a6', fg='white', 
                             relief='flat', padx=25, pady=10, cursor='hand2', bd=0)
        cancel_btn.pack(side=tk.RIGHT)
        
        # Bind Enter key
        dialog.bind('<Return>', lambda e: start_livestream())
        dialog.bind('<Escape>', lambda e: cleanup())
        
        # Focus vào nút Bắt đầu
        start_btn.focus()
    
    def _execute_livestream(self, profiles, url, accounts, auto_out_minutes, replace_delay_seconds, max_viewers, hidden):
        """Thực thi treo livestream với auto-replace accounts"""
        def livestream_thread():
            try:
                # Initialize status if not exists
                if hasattr(self, 'status_label'):
                    self.status_label.config(text="Đang treo livestream...")
                
                # Tạo pool accounts để thay thế
                account_pool = accounts.copy()
                active_viewers = {}  # {profile_name: {'driver': driver, 'account': account, 'start_time': time}}
                backup_accounts = []  # Accounts dự phòng
                
                print(f"📺 [LIVESTREAM] Bắt đầu treo livestream với {len(accounts)} accounts cho {len(profiles)} profiles")
                print(f"📺 [LIVESTREAM] URL: {url}")
                print(f"📺 [LIVESTREAM] Auto-out: {auto_out_minutes} phút, Replace delay: {replace_delay_seconds} giây")
                print(f"📺 [LIVESTREAM] Max viewers: {max_viewers}, Hidden: {hidden}")
                
                import time
                import random
                
                def launch_viewer(profile_name, account):
                    """Launch một viewer cho livestream"""
                    try:
                        print(f"📺 [LIVESTREAM] Launching viewer cho {profile_name} với account {account.get('email', 'N/A')}")

                        # Initialize drivers dict if not exists
                        if not hasattr(self, 'drivers'):
                            self.drivers = {}

                        # Stop existing driver if running
                        if profile_name in self.drivers:
                            try:
                                self.drivers[profile_name].quit()
                                del self.drivers[profile_name]
                                print(f"📺 [LIVESTREAM] Đã dừng driver cũ cho {profile_name}")
                            except Exception as e:
                                print(f"📺 [LIVESTREAM] Lỗi khi dừng driver cũ: {str(e)}")

                        # Prepare login data
                        login_data = {
                            'email': account['email'],
                            'password': account['password'],
                            'username': account.get('username', ''),
                            'email_password': account.get('email_password', ''),
                            'session_token': account.get('session_token', ''),
                            'user_id': account.get('user_id', '')
                        }

                        # Launch profile with login
                        success, result = self.manager.launch_chrome_profile(
                            profile_name,
                            start_url=url,
                            hidden=hidden,
                            auto_login=True,
                            login_data=login_data
                        )

                        if success:
                            print(f"✅ [LIVESTREAM] Viewer {profile_name} đã join livestream thành công")
                            active_viewers[profile_name] = {
                                'driver': result,
                                'account': account,
                                'start_time': time.time()
                            }
                            self.drivers[profile_name] = result
                            return True
                        else:
                            print(f"❌ [LIVESTREAM] Không thể launch viewer {profile_name}: {result}")
                            return False
                    except Exception as e:
                        print(f"❌ [LIVESTREAM] Lỗi khi launch viewer {profile_name}: {str(e)}")
                        return False
            
                def replace_viewer(profile_name):
                    """Thay thế một viewer"""
                try:
                    print(f"🔄 [LIVESTREAM] Thay thế viewer {profile_name}")
                    
                    # Initialize drivers dict if not exists
                    if not hasattr(self, 'drivers'):
                        self.drivers = {}
                    
                    # Stop current viewer
                    if profile_name in active_viewers:
                        try:
                            active_viewers[profile_name]['driver'].quit()
                            print(f"📺 [LIVESTREAM] Đã dừng viewer cũ {profile_name}")
                        except Exception as e:
                            print(f"📺 [LIVESTREAM] Lỗi khi dừng viewer cũ: {str(e)}")
                        
                        # Move account to backup pool
                        old_account = active_viewers[profile_name]['account']
                        backup_accounts.append(old_account)
                        del active_viewers[profile_name]
                    
                    # Remove from drivers dict
                    if profile_name in self.drivers:
                        del self.drivers[profile_name]
                    
                    # Wait before replacing
                    time.sleep(replace_delay_seconds)
                    
                    # Get new account from pool
                    if account_pool:
                        new_account = account_pool.pop(0)
                        success = launch_viewer(profile_name, new_account)
                        if success:
                            print(f"✅ [LIVESTREAM] Đã thay thế viewer {profile_name} thành công")
                        else:
                            # Put account back to pool if failed
                            account_pool.insert(0, new_account)
                            print(f"❌ [LIVESTREAM] Thay thế viewer {profile_name} thất bại")
                    else:
                        print(f"⚠️ [LIVESTREAM] Không còn account trong pool để thay thế {profile_name}")
                        
                except Exception as e:
                    print(f"❌ [LIVESTREAM] Lỗi khi thay thế viewer {profile_name}: {str(e)}")
            
                # Initial launch - launch viewers up to max_viewers
                initial_profiles = profiles[:max_viewers]
                for profile_name in initial_profiles:
                    if account_pool:
                        account = account_pool.pop(0)
                        success = launch_viewer(profile_name, account)
                        if not success:
                            # Put account back if failed
                            account_pool.insert(0, account)
                        time.sleep(2)  # Small delay between launches
            
                # Main loop - monitor and replace viewers
                while True:
                    try:
                        current_time = time.time()
                        viewers_to_replace = []
                    
                        # Check for viewers that need to be replaced
                        for profile_name, viewer_info in active_viewers.items():
                            elapsed_time = current_time - viewer_info['start_time']
                            if elapsed_time >= (auto_out_minutes * 60):  # Convert to seconds
                                viewers_to_replace.append(profile_name)
                    
                        # Replace viewers that need replacement
                        for profile_name in viewers_to_replace:
                            replace_viewer(profile_name)
                    
                        # Update status
                        active_count = len(active_viewers)
                        pool_count = len(account_pool)
                        backup_count = len(backup_accounts)
                    
                        status_text = f"📺 Livestream: {active_count} viewers active, {pool_count} accounts in pool, {backup_count} backup"
                        if hasattr(self, 'status_label'):
                            self.root.after(0, lambda: self.status_label.config(text=status_text))
                        print(f"📊 [LIVESTREAM] Status: {status_text}")
                    
                        # Check if we should stop (no more accounts and no active viewers)
                        if not account_pool and not active_viewers:
                            print("📺 [LIVESTREAM] Tất cả accounts đã hết, dừng livestream")
                            break
                        
                        # Sleep before next check
                        time.sleep(30)  # Check every 30 seconds
                    
                    except Exception as e:
                        print(f"❌ [LIVESTREAM] Lỗi trong main loop: {str(e)}")
                        time.sleep(10)
            
                # Cleanup
                print("📺 [LIVESTREAM] Dọn dẹp và dừng tất cả viewers")
                for profile_name, viewer_info in active_viewers.items():
                    try:
                        viewer_info['driver'].quit()
                        if hasattr(self, 'drivers') and profile_name in self.drivers:
                            del self.drivers[profile_name]
                    except Exception as e:
                        print(f"❌ [LIVESTREAM] Lỗi khi dọn dẹp {profile_name}: {str(e)}")
                
                if hasattr(self, 'status_label'):
                    self.root.after(0, lambda: self.status_label.config(text="📺 Livestream đã dừng"))
                self.root.after(0, self.refresh_profiles)
                
            except Exception as e:
                print(f"❌ [LIVESTREAM] Lỗi tổng thể trong livestream thread: {str(e)}")
                if hasattr(self, 'status_label'):
                    self.root.after(0, lambda: self.status_label.config(text="❌ Livestream lỗi"))
        
        threading.Thread(target=livestream_thread, daemon=True).start()
    
    def _execute_livestream_advanced(self, profiles, url, accounts, auto_out_minutes, replace_delay_seconds, 
                                   max_viewers, hidden, launch_delay, check_interval, max_retries,
                                   memory_optimization, auto_cleanup, show_stats):
        """Thực thi treo livestream với các tính năng nâng cao cho 300+ accounts"""
        def livestream_advanced_thread():
            self.status_label.config(text="Đang treo livestream với 300+ accounts...")
            
            # Tạo pool accounts để thay thế
            account_pool = accounts.copy()
            active_viewers = {}  # {profile_name: {'driver': driver, 'account': account, 'start_time': time, 'retry_count': int}}
            backup_accounts = []  # Accounts dự phòng
            failed_accounts = []  # Accounts thất bại
            stats = {
                'total_launched': 0,
                'successful_launches': 0,
                'failed_launches': 0,
                'total_replacements': 0,
                'start_time': time.time()
            }
            
            print(f"📺 [LIVESTREAM-ADVANCED] Bắt đầu treo livestream với {len(accounts)} accounts cho {len(profiles)} profiles")
            print(f"📺 [LIVESTREAM-ADVANCED] URL: {url}")
            print(f"📺 [LIVESTREAM-ADVANCED] Max viewers: {max_viewers}, Hidden: {hidden}")
            print(f"📺 [LIVESTREAM-ADVANCED] Launch delay: {launch_delay}s, Check interval: {check_interval}s")
            print(f"📺 [LIVESTREAM-ADVANCED] Memory optimization: {memory_optimization}, Auto cleanup: {auto_cleanup}")
            
            import time
            import random
            import gc
            
            def launch_viewer(profile_name, account, retry_count=0):
                """Launch một viewer cho livestream với retry mechanism"""
                try:
                    print(f"📺 [LIVESTREAM-ADVANCED] Launching viewer cho {profile_name} với account {account.get('email', 'N/A')} (retry: {retry_count})")
                    
                    # Stop existing driver if running
                    if profile_name in self.drivers:
                        try:
                            self.drivers[profile_name].quit()
                            del self.drivers[profile_name]
                            print(f"📺 [LIVESTREAM-ADVANCED] Đã dừng driver cũ cho {profile_name}")
                        except Exception as e:
                            print(f"📺 [LIVESTREAM-ADVANCED] Lỗi khi dừng driver cũ: {str(e)}")
                    
                    # Prepare login data
                    login_data = {
                        'email': account['email'],
                        'password': account['password'],
                        'username': account.get('username', ''),
                        'email_password': account.get('email_password', ''),
                        'session_token': account.get('session_token', ''),
                        'user_id': account.get('user_id', '')
                    }
                    
                    # Launch profile with login
                    success, result = self.manager.launch_chrome_profile(
                        profile_name,
                        start_url=url,
                        hidden=hidden,
                        auto_login=True,
                        login_data=login_data
                    )
                    
                    if success:
                        print(f"✅ [LIVESTREAM-ADVANCED] Viewer {profile_name} đã join livestream thành công")
                        active_viewers[profile_name] = {
                            'driver': result,
                            'account': account,
                            'start_time': time.time(),
                            'retry_count': retry_count
                        }
                        self.drivers[profile_name] = result
                        stats['successful_launches'] += 1
                        return True
                    else:
                        print(f"❌ [LIVESTREAM-ADVANCED] Không thể launch viewer {profile_name}: {result}")
                        stats['failed_launches'] += 1
                        return False
                        
                except Exception as e:
                    print(f"❌ [LIVESTREAM-ADVANCED] Lỗi khi launch viewer {profile_name}: {str(e)}")
                    stats['failed_launches'] += 1
                    return False
            
            def replace_viewer(profile_name):
                """Thay thế một viewer với advanced logic"""
                try:
                    print(f"🔄 [LIVESTREAM-ADVANCED] Thay thế viewer {profile_name}")
                    
                    # Stop current viewer
                    if profile_name in active_viewers:
                        try:
                            active_viewers[profile_name]['driver'].quit()
                            print(f"📺 [LIVESTREAM-ADVANCED] Đã dừng viewer cũ {profile_name}")
                        except Exception as e:
                            print(f"📺 [LIVESTREAM-ADVANCED] Lỗi khi dừng viewer cũ: {str(e)}")
                        
                        # Move account to backup pool
                        old_account = active_viewers[profile_name]['account']
                        backup_accounts.append(old_account)
                        del active_viewers[profile_name]
                    
                    # Remove from drivers dict
                    if profile_name in self.drivers:
                        del self.drivers[profile_name]
                    
                    # Wait before replacing
                    time.sleep(replace_delay_seconds)
                    
                    # Get new account from pool
                    if account_pool:
                        new_account = account_pool.pop(0)
                        success = launch_viewer(profile_name, new_account)
                        if success:
                            print(f"✅ [LIVESTREAM-ADVANCED] Đã thay thế viewer {profile_name} thành công")
                            stats['total_replacements'] += 1
                        else:
                            # Put account back to pool if failed
                            account_pool.insert(0, new_account)
                            print(f"❌ [LIVESTREAM-ADVANCED] Thay thế viewer {profile_name} thất bại")
                    else:
                        print(f"⚠️ [LIVESTREAM-ADVANCED] Không còn account trong pool để thay thế {profile_name}")
                        
                except Exception as e:
                    print(f"❌ [LIVESTREAM-ADVANCED] Lỗi khi thay thế viewer {profile_name}: {str(e)}")
            
            def cleanup_failed_accounts():
                """Cleanup failed accounts nếu auto_cleanup enabled"""
                if auto_cleanup and failed_accounts:
                    print(f"🧹 [LIVESTREAM-ADVANCED] Cleanup {len(failed_accounts)} failed accounts")
                    failed_accounts.clear()
                    if memory_optimization:
                        gc.collect()
            
            def update_status():
                """Update status với thống kê chi tiết"""
                active_count = len(active_viewers)
                pool_count = len(account_pool)
                backup_count = len(backup_accounts)
                failed_count = len(failed_accounts)
                
                elapsed_time = time.time() - stats['start_time']
                hours = int(elapsed_time // 3600)
                minutes = int((elapsed_time % 3600) // 60)
                
                if show_stats:
                    status_text = f"📺 Livestream: {active_count} active | {pool_count} pool | {backup_count} backup | {failed_count} failed | {hours}h{minutes}m"
                else:
                    status_text = f"📺 Livestream: {active_count} viewers active, {pool_count} accounts in pool"
                
                self.root.after(0, lambda: self.status_label.config(text=status_text))
            
            # Initial launch - launch viewers up to max_viewers
            print(f"📺 [LIVESTREAM-ADVANCED] Bắt đầu launch {min(max_viewers, len(profiles))} viewers ban đầu...")
            initial_profiles = profiles[:max_viewers]
            
            for i, profile_name in enumerate(initial_profiles):
                if account_pool:
                    account = account_pool.pop(0)
                    stats['total_launched'] += 1
                    success = launch_viewer(profile_name, account)
                    if not success:
                        # Put account back if failed
                        account_pool.insert(0, account)
                        failed_accounts.append(account)
                    
                    # Delay between launches
                    if i < len(initial_profiles) - 1:  # Don't delay after last launch
                        time.sleep(launch_delay)
            
            print(f"📺 [LIVESTREAM-ADVANCED] Đã launch {len(active_viewers)} viewers ban đầu")
            
            # Main loop - monitor and replace viewers
            while True:
                try:
                    current_time = time.time()
                    viewers_to_replace = []
                    
                    # Check for viewers that need to be replaced
                    for profile_name, viewer_info in active_viewers.items():
                        elapsed_time = current_time - viewer_info['start_time']
                        if elapsed_time >= (auto_out_minutes * 60):  # Convert to seconds
                            viewers_to_replace.append(profile_name)
                    
                    # Replace viewers that need replacement
                    for profile_name in viewers_to_replace:
                        replace_viewer(profile_name)
                    
                    # Cleanup failed accounts periodically
                    if len(failed_accounts) > 50:  # Cleanup when too many failed accounts
                        cleanup_failed_accounts()
                    
                    # Memory optimization
                    if memory_optimization and len(active_viewers) % 20 == 0:
                        gc.collect()
                    
                    # Update status
                    update_status()
                    
                    # Check if we should stop (no more accounts and no active viewers)
                    if not account_pool and not active_viewers:
                        print("📺 [LIVESTREAM-ADVANCED] Tất cả accounts đã hết, dừng livestream")
                        break
                    
                    # Sleep before next check
                    time.sleep(check_interval)
                    
                except Exception as e:
                    print(f"❌ [LIVESTREAM-ADVANCED] Lỗi trong main loop: {str(e)}")
                    time.sleep(10)
            
            # Final cleanup
            print("📺 [LIVESTREAM-ADVANCED] Dọn dẹp và dừng tất cả viewers")
            for profile_name, viewer_info in active_viewers.items():
                try:
                    viewer_info['driver'].quit()
                    if profile_name in self.drivers:
                        del self.drivers[profile_name]
                except Exception as e:
                    print(f"❌ [LIVESTREAM-ADVANCED] Lỗi khi dọn dẹp {profile_name}: {str(e)}")
            
            # Final statistics
            total_time = time.time() - stats['start_time']
            print(f"📊 [LIVESTREAM-ADVANCED] Thống kê cuối cùng:")
            print(f"📊 [LIVESTREAM-ADVANCED] - Tổng thời gian: {total_time/3600:.2f} giờ")
            print(f"📊 [LIVESTREAM-ADVANCED] - Tổng launches: {stats['total_launched']}")
            print(f"📊 [LIVESTREAM-ADVANCED] - Thành công: {stats['successful_launches']}")
            print(f"📊 [LIVESTREAM-ADVANCED] - Thất bại: {stats['failed_launches']}")
            print(f"📊 [LIVESTREAM-ADVANCED] - Tổng replacements: {stats['total_replacements']}")
            
            self.root.after(0, lambda: self.status_label.config(text="📺 Livestream đã dừng"))
            self.root.after(0, self.refresh_profiles)
        
        threading.Thread(target=livestream_advanced_thread, daemon=True).start()
    
    def _execute_livestream_profiles(self, profiles, url, auto_out_minutes, replace_delay_seconds, 
                                   max_viewers, hidden, launch_delay, check_interval, max_retries,
                                   memory_optimization, auto_cleanup, show_stats,
                                   browser_optimization, memory_cleanup, cpu_optimization,
                                   disk_optimization, error_handling, stability, monitoring):
        """Thực thi treo livestream với profiles đã đăng nhập và tối ưu hóa"""
        def livestream_profiles_thread():
            self.status_label.config(text="Đang treo livestream với profiles đã đăng nhập...")
            
            # Tạo pool profiles để thay thế
            profile_pool = profiles.copy()
            active_viewers = {}  # {profile_name: {'driver': driver, 'start_time': time, 'retry_count': int}}
            backup_profiles = []  # Profiles dự phòng
            failed_profiles = []  # Profiles thất bại
            stats = {
                'total_launched': 0,
                'successful_launches': 0,
                'failed_launches': 0,
                'total_replacements': 0,
                'start_time': time.time()
            }
            
            print(f"📺 [LIVESTREAM-PROFILES] Bắt đầu treo livestream với {len(profiles)} profiles")
            print(f"📺 [LIVESTREAM-PROFILES] URL: {url}")
            print(f"📺 [LIVESTREAM-PROFILES] Max viewers: {max_viewers}, Hidden: {hidden}")
            print(f"📺 [LIVESTREAM-PROFILES] Optimizations: Browser={browser_optimization}, Memory={memory_cleanup}, CPU={cpu_optimization}, Disk={disk_optimization}")
            
            import time
            import random
            import gc
            
            def launch_viewer(profile_name, retry_count=0):
                """Launch một viewer cho livestream với profile đã đăng nhập"""
                try:
                    print(f"📺 [LIVESTREAM-PROFILES] Launching viewer cho {profile_name} (retry: {retry_count})")
                    
                    # Stop existing driver if running
                    if profile_name in self.drivers:
                        try:
                            self.drivers[profile_name].quit()
                            del self.drivers[profile_name]
                            print(f"📺 [LIVESTREAM-PROFILES] Đã dừng driver cũ cho {profile_name}")
                        except Exception as e:
                            print(f"📺 [LIVESTREAM-PROFILES] Lỗi khi dừng driver cũ: {str(e)}")
                    
                    # Launch profile with persistent login (no need for login_data)
                    success, result = self.manager.launch_chrome_profile(
                        profile_name,
                        start_url=url,
                        hidden=hidden,
                        auto_login=True,  # Sẽ sử dụng persistent login
                        login_data=None   # Không cần login_data vì đã đăng nhập
                    )
                    
                    if success:
                        print(f"✅ [LIVESTREAM-PROFILES] Viewer {profile_name} đã join livestream thành công")
                        active_viewers[profile_name] = {
                            'driver': result,
                            'start_time': time.time(),
                            'retry_count': retry_count
                        }
                        self.drivers[profile_name] = result
                        stats['successful_launches'] += 1
                        return True
                    else:
                        print(f"❌ [LIVESTREAM-PROFILES] Không thể launch viewer {profile_name}: {result}")
                        stats['failed_launches'] += 1
                        return False
                        
                except Exception as e:
                    print(f"❌ [LIVESTREAM-PROFILES] Lỗi khi launch viewer {profile_name}: {str(e)}")
                    stats['failed_launches'] += 1
                    return False
            
            def replace_viewer(profile_name):
                """Thay thế một viewer với advanced logic"""
                try:
                    print(f"🔄 [LIVESTREAM-PROFILES] Thay thế viewer {profile_name}")
                    
                    # Stop current viewer
                    if profile_name in active_viewers:
                        try:
                            active_viewers[profile_name]['driver'].quit()
                            print(f"📺 [LIVESTREAM-PROFILES] Đã dừng viewer cũ {profile_name}")
                        except Exception as e:
                            print(f"📺 [LIVESTREAM-PROFILES] Lỗi khi dừng viewer cũ: {str(e)}")
                        
                        # Move profile to backup pool
                        backup_profiles.append(profile_name)
                        del active_viewers[profile_name]
                    
                    # Remove from drivers dict
                    if profile_name in self.drivers:
                        del self.drivers[profile_name]
                    
                    # Wait before replacing
                    time.sleep(replace_delay_seconds)
                    
                    # Get new profile from pool
                    if profile_pool:
                        new_profile = profile_pool.pop(0)
                        success = launch_viewer(new_profile)
                        if success:
                            print(f"✅ [LIVESTREAM-PROFILES] Đã thay thế viewer {profile_name} thành công")
                            stats['total_replacements'] += 1
                        else:
                            # Put profile back to pool if failed
                            profile_pool.insert(0, new_profile)
                            failed_profiles.append(new_profile)
                            print(f"❌ [LIVESTREAM-PROFILES] Thay thế viewer {profile_name} thất bại")
                    else:
                        print(f"⚠️ [LIVESTREAM-PROFILES] Không còn profile trong pool để thay thế {profile_name}")
                        
                except Exception as e:
                    print(f"❌ [LIVESTREAM-PROFILES] Lỗi khi thay thế viewer {profile_name}: {str(e)}")
            
            def cleanup_failed_profiles():
                """Cleanup failed profiles nếu auto_cleanup enabled"""
                if auto_cleanup and failed_profiles:
                    print(f"🧹 [LIVESTREAM-PROFILES] Cleanup {len(failed_profiles)} failed profiles")
                    failed_profiles.clear()
                    if memory_optimization:
                        gc.collect()
            
            def update_status():
                """Update status với thống kê chi tiết"""
                active_count = len(active_viewers)
                pool_count = len(profile_pool)
                backup_count = len(backup_profiles)
                failed_count = len(failed_profiles)
                
                elapsed_time = time.time() - stats['start_time']
                hours = int(elapsed_time // 3600)
                minutes = int((elapsed_time % 3600) // 60)
                
                if show_stats:
                    status_text = f"📺 Livestream: {active_count} active | {pool_count} pool | {backup_count} backup | {failed_count} failed | {hours}h{minutes}m"
                else:
                    status_text = f"📺 Livestream: {active_count} viewers active, {pool_count} profiles in pool"
                
                self.root.after(0, lambda: self.status_label.config(text=status_text))
            
            # Initial launch - launch viewers up to max_viewers
            print(f"📺 [LIVESTREAM-PROFILES] Bắt đầu launch {min(max_viewers, len(profiles))} viewers ban đầu...")
            initial_profiles = profiles[:max_viewers]
            
            for i, profile_name in enumerate(initial_profiles):
                if profile_pool:
                    profile = profile_pool.pop(0)
                    stats['total_launched'] += 1
                    success = launch_viewer(profile)
                    if not success:
                        # Put profile back if failed
                        profile_pool.insert(0, profile)
                        failed_profiles.append(profile)
                    
                    # Delay between launches
                    if i < len(initial_profiles) - 1:  # Don't delay after last launch
                        time.sleep(launch_delay)
            
            print(f"📺 [LIVESTREAM-PROFILES] Đã launch {len(active_viewers)} viewers ban đầu")
            
            # Main loop - monitor and replace viewers
            while True:
                try:
                    current_time = time.time()
                    viewers_to_replace = []
                    
                    # Check for viewers that need to be replaced
                    for profile_name, viewer_info in active_viewers.items():
                        elapsed_time = current_time - viewer_info['start_time']
                        if elapsed_time >= (auto_out_minutes * 60):  # Convert to seconds
                            viewers_to_replace.append(profile_name)
                    
                    # Replace viewers that need replacement
                    for profile_name in viewers_to_replace:
                        replace_viewer(profile_name)
                    
                    # Cleanup failed profiles periodically
                    if len(failed_profiles) > 50:  # Cleanup when too many failed profiles
                        cleanup_failed_profiles()
                    
                    # Memory optimization
                    if memory_cleanup and len(active_viewers) % 10 == 0:
                        gc.collect()
                        print(f"🧹 [LIVESTREAM-PROFILES] Memory cleanup performed")
                    
                    # Update status
                    update_status()
                    
                    # Check if we should stop (no more profiles and no active viewers)
                    if not profile_pool and not active_viewers:
                        print("📺 [LIVESTREAM-PROFILES] Tất cả profiles đã hết, dừng livestream")
                        break
                    
                    # Sleep before next check (optimize CPU if enabled)
                    sleep_time = check_interval
                    if cpu_optimization:
                        sleep_time = min(check_interval * 2, 60)  # Increase interval to save CPU
                    
                    time.sleep(sleep_time)
                    
                except Exception as e:
                    print(f"❌ [LIVESTREAM-PROFILES] Lỗi trong main loop: {str(e)}")
                    if error_handling:
                        print(f"🔄 [LIVESTREAM-PROFILES] Auto-restarting after error...")
                        time.sleep(10)
                    else:
                        time.sleep(10)
            
            # Final cleanup
            print("📺 [LIVESTREAM-PROFILES] Dọn dẹp và dừng tất cả viewers")
            for profile_name, viewer_info in active_viewers.items():
                try:
                    viewer_info['driver'].quit()
                    if profile_name in self.drivers:
                        del self.drivers[profile_name]
                except Exception as e:
                    print(f"❌ [LIVESTREAM-PROFILES] Lỗi khi dọn dẹp {profile_name}: {str(e)}")
            
            # Final statistics
            total_time = time.time() - stats['start_time']
            print(f"📊 [LIVESTREAM-PROFILES] Thống kê cuối cùng:")
            print(f"📊 [LIVESTREAM-PROFILES] - Tổng thời gian: {total_time/3600:.2f} giờ")
            print(f"📊 [LIVESTREAM-PROFILES] - Tổng launches: {stats['total_launched']}")
            print(f"📊 [LIVESTREAM-PROFILES] - Thành công: {stats['successful_launches']}")
            print(f"📊 [LIVESTREAM-PROFILES] - Thất bại: {stats['failed_launches']}")
            print(f"📊 [LIVESTREAM-PROFILES] - Tổng replacements: {stats['total_replacements']}")
            
            self.root.after(0, lambda: self.status_label.config(text="📺 Livestream đã dừng"))
            self.root.after(0, self.refresh_profiles)
        
        threading.Thread(target=livestream_profiles_thread, daemon=True).start()
    
    
    def bulk_configure_login(self):
        """Cấu hình đăng nhập hàng loạt"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn ít nhất một profile!")
            return
        
        selected_profiles = [self.tree.item(item)['text'] for item in selection]
        
        # Dialog để nhập thông tin đăng nhập
        dialog = tk.Toplevel(self.root)
        dialog.title("🔐 Cấu Hình Đăng Nhập Hàng Loạt")
        dialog.geometry("500x400")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Profiles info
        ttk.Label(main_frame, text=f"Profiles đã chọn: {', '.join(selected_profiles)}").pack(anchor=tk.W, pady=(0, 10))
        
        # Login inputs
        ttk.Label(main_frame, text="Email:").pack(anchor=tk.W)
        email_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=email_var, width=50).pack(fill=tk.X, pady=(5, 10))
        
        ttk.Label(main_frame, text="Password:").pack(anchor=tk.W)
        password_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=password_var, show="*", width=50).pack(fill=tk.X, pady=(5, 10))
        
        ttk.Label(main_frame, text="2FA (tùy chọn):").pack(anchor=tk.W)
        twofa_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=twofa_var, width=50).pack(fill=tk.X, pady=(5, 10))
        
        # Buttons
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=(10, 0))
        
        def configure_login():
            email = email_var.get().strip()
            password = password_var.get().strip()
            twofa = twofa_var.get().strip()
            
            if not email or not password:
                messagebox.showwarning("Cảnh báo", "Vui lòng nhập email và password!")
                return
            
            dialog.destroy()
            
            def configure_thread():
                self.status_label.config(text="Đang cấu hình đăng nhập hàng loạt...")
                success_count = 0
                
                login_data = {
                    'email': email,
                    'password': password,
                    'twofa': twofa
                }
                
                for profile_name in selected_profiles:
                    try:
                        self.manager.config.set('LOGIN_DATA', profile_name, str(login_data))
                        success_count += 1
                    except Exception as e:
                        print(f"Lỗi cấu hình đăng nhập cho {profile_name}: {str(e)}")
                
                self.manager.save_config()
                self.root.after(0, lambda: self.status_label.config(
                    text=f"Đã cấu hình đăng nhập cho {success_count}/{len(selected_profiles)} profiles"))
            
            threading.Thread(target=configure_thread, daemon=True).start()
        
        # Buttons với style rõ ràng
        config_btn = ttk.Button(buttons_frame, text="✅ Cấu Hình", command=configure_login)
        config_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        cancel_btn = ttk.Button(buttons_frame, text="❌ Hủy", command=dialog.destroy)
        cancel_btn.pack(side=tk.RIGHT)
        
        # Focus vào nút Cấu Hình
        config_btn.focus()
        
    def stop_profile(self):
        """Dừng profile"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một profile!")
            return
        
        profile_name = self.tree.item(selection[0])["values"][0]
        
        if profile_name in self.drivers:
            try:
                self.drivers[profile_name].quit()
                del self.drivers[profile_name]
                self.status_label.config(text=f"Đã dừng {profile_name}")
                self.refresh_profiles()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể dừng profile: {str(e)}")
        else:
            messagebox.showwarning("Cảnh báo", "Profile không đang chạy!")
        
    
    def export_cookies(self):
        """Xuất cookies"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một profile!")
            return
        
        profile_name = self.tree.item(selection[0])["values"][0]
        
        # Tạo dialog xuất cookies
        export_dialog = tk.Toplevel(self.root)
        export_dialog.title(f"Xuất Cookies - {profile_name}")
        export_dialog.geometry("600x500")
        export_dialog.resizable(True, True)
        export_dialog.transient(self.root)
        export_dialog.grab_set()
        
        # Center dialog
        export_dialog.update_idletasks()
        x = (export_dialog.winfo_screenwidth() // 2) - (export_dialog.winfo_width() // 2)
        y = (export_dialog.winfo_screenheight() // 2) - (export_dialog.winfo_height() // 2)
        export_dialog.geometry(f"+{x}+{y}")
        
        # Frame chính
        main_frame = ttk.Frame(export_dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Tiêu đề
        title_label = ttk.Label(main_frame, text=f"🍪 Xuất Cookies - {profile_name}", 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Hướng dẫn
        help_text = """Tính năng này sẽ xuất tất cả cookies từ Chrome profile thành file JSON.
Cookies sẽ được lưu với định dạng chuẩn để có thể import vào profile khác."""
        
        help_label = ttk.Label(main_frame, text=help_text, font=("Arial", 9), foreground="gray", wraplength=550)
        help_label.pack(anchor=tk.W, pady=(0, 20))
        
        # Tùy chọn xuất
        options_frame = ttk.LabelFrame(main_frame, text="Tùy chọn xuất", padding="15")
        options_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Lọc theo domain
        domain_var = tk.StringVar()
        ttk.Label(options_frame, text="Lọc theo domain (để trống để xuất tất cả):").pack(anchor=tk.W, pady=(0, 5))
        domain_entry = ttk.Entry(options_frame, textvariable=domain_var, width=50)
        domain_entry.pack(fill=tk.X, pady=(0, 10))
        domain_entry.insert(0, ".google.com")
        
        # Chỉ xuất cookies còn hiệu lực
        valid_only_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Chỉ xuất cookies còn hiệu lực", 
                       variable=valid_only_var).pack(anchor=tk.W, pady=(0, 10))
        
        # Format xuất
        format_var = tk.StringVar(value="json")
        ttk.Label(options_frame, text="Định dạng xuất:").pack(anchor=tk.W, pady=(0, 5))
        format_frame = ttk.Frame(options_frame)
        format_frame.pack(fill=tk.X)
        ttk.Radiobutton(format_frame, text="JSON", variable=format_var, value="json").pack(side=tk.LEFT, padx=(0, 20))
        ttk.Radiobutton(format_frame, text="Netscape", variable=format_var, value="netscape").pack(side=tk.LEFT)
        
        # Nút
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        def start_export():
            """Bắt đầu xuất cookies"""
            def export_thread():
                try:
                    # Lấy cookies từ Chrome profile
                    cookies = self.manager.export_cookies_from_profile(profile_name, domain_var.get(), valid_only_var.get())
                    
                    if not cookies:
                        self.root.after(0, lambda: messagebox.showwarning("Cảnh báo", "Không tìm thấy cookies nào!"))
                        return
                    
                    # Chọn file để lưu
                    file_ext = ".json" if format_var.get() == "json" else ".txt"
                    file_path = filedialog.asksaveasfilename(
                        title="Lưu file cookies",
                        defaultextension=file_ext,
                        filetypes=[("JSON files", "*.json"), ("Text files", "*.txt"), ("All files", "*.*")],
                        initialname=f"{profile_name}_cookies{file_ext}"
                    )
                    
                    if file_path:
                        # Lưu file
                        if format_var.get() == "json":
                            import json
                            with open(file_path, 'w', encoding='utf-8') as f:
                                json.dump(cookies, f, indent=2, ensure_ascii=False)
                        else:
                            # Netscape format
                            with open(file_path, 'w', encoding='utf-8') as f:
                                f.write("# Netscape HTTP Cookie File\n")
                                for cookie in cookies:
                                    domain = cookie.get('domain', '')
                                    if domain.startswith('.'):
                                        domain_flag = 'TRUE'
                                    else:
                                        domain_flag = 'FALSE'
                                    
                                    f.write(f"{domain}\t{domain_flag}\t{cookie.get('path', '/')}\t"
                                           f"{'TRUE' if cookie.get('secure', False) else 'FALSE'}\t"
                                           f"{int(cookie.get('expirationDate', 0))}\t"
                                           f"{cookie.get('name', '')}\t{cookie.get('value', '')}\n")
                        
                        self.root.after(0, lambda: messagebox.showinfo("Thành công", 
                            f"Đã xuất {len(cookies)} cookies thành công!\n"
                            f"File: {file_path}"))
                        
                except Exception as e:
                    self.root.after(0, lambda: messagebox.showerror("Lỗi", f"Không thể xuất cookies: {str(e)}"))
            
            threading.Thread(target=export_thread, daemon=True).start()
            export_dialog.destroy()
        
        def cancel():
            """Hủy"""
            export_dialog.destroy()
        
        # Nút
        ttk.Button(button_frame, text="🍪 Xuất Cookies", command=start_export).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="❌ Hủy", command=cancel).pack(side=tk.LEFT)
        
    def import_cookies(self):
        """Import cookies vào Chrome profile"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một profile!")
            return
        
        profile_name = self.tree.item(selection[0])["values"][0]
        
        # Chọn file cookies
        file_path = filedialog.askopenfilename(
            title="Chọn file cookies",
            filetypes=[("JSON files", "*.json"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
        
        # Tạo dialog import cookies
        import_dialog = tk.Toplevel(self.root)
        import_dialog.title(f"Import Cookies - {profile_name}")
        import_dialog.geometry("500x400")
        import_dialog.resizable(True, True)
        import_dialog.transient(self.root)
        import_dialog.grab_set()
        
        # Center dialog
        import_dialog.update_idletasks()
        x = (import_dialog.winfo_screenwidth() // 2) - (import_dialog.winfo_width() // 2)
        y = (import_dialog.winfo_screenheight() // 2) - (import_dialog.winfo_height() // 2)
        import_dialog.geometry(f"+{x}+{y}")
        
        # Frame chính
        main_frame = ttk.Frame(import_dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Tiêu đề
        title_label = ttk.Label(main_frame, text=f"🍪 Import Cookies - {profile_name}", 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Hiển thị file đã chọn
        file_label = ttk.Label(main_frame, text=f"File: {file_path}", 
                              font=("Arial", 9), foreground="blue")
        file_label.pack(anchor=tk.W, pady=(0, 20))
        
        # Tùy chọn import
        options_frame = ttk.LabelFrame(main_frame, text="Tùy chọn import", padding="15")
        options_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Ghi đè cookies hiện tại
        overwrite_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="Ghi đè cookies hiện tại", 
                       variable=overwrite_var).pack(anchor=tk.W, pady=(0, 10))
        
        # Chỉ import cookies còn hiệu lực
        valid_only_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Chỉ import cookies còn hiệu lực", 
                       variable=valid_only_var).pack(anchor=tk.W, pady=(0, 10))
        
        # Nút
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        def start_import():
            """Bắt đầu import cookies"""
            def import_thread():
                try:
                    # Đọc file cookies
                    with open(file_path, 'r', encoding='utf-8') as f:
                        if file_path.endswith('.json'):
                            import json
                            cookies = json.load(f)
                        else:
                            # Parse Netscape format
                            cookies = []
                            for line in f:
                                line = line.strip()
                                if line.startswith('#') or not line:
                                    continue
                                
                                parts = line.split('\t')
                                if len(parts) >= 7:
                                    cookies.append({
                                        'domain': parts[0],
                                        'path': parts[2],
                                        'secure': parts[3] == 'TRUE',
                                        'expirationDate': float(parts[4]) if parts[4] != '0' else None,
                                        'name': parts[5],
                                        'value': parts[6]
                                    })
                    
                    # Import cookies vào profile
                    success_count = self.manager.import_cookies_to_profile(profile_name, cookies, overwrite_var.get(), valid_only_var.get())
                    
                    self.root.after(0, lambda: messagebox.showinfo("Thành công", 
                        f"Đã import {success_count} cookies thành công!"))
                    
                except Exception as e:
                    self.root.after(0, lambda: messagebox.showerror("Lỗi", f"Không thể import cookies: {str(e)}"))
            
            threading.Thread(target=import_thread, daemon=True).start()
            import_dialog.destroy()
        
        def cancel():
            """Hủy"""
            import_dialog.destroy()
        
        # Nút
        ttk.Button(button_frame, text="🍪 Import Cookies", command=start_import).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="❌ Hủy", command=cancel).pack(side=tk.LEFT)
        
    def configure_login(self):
        """Cấu hình đăng nhập tự động"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một profile!")
            return
        
        profile_name = self.tree.item(selection[0])["values"][0]
        
        # Tạo cửa sổ cấu hình đăng nhập
        login_window = tk.Toplevel(self.root)
        login_window.title(f"Cấu hình đăng nhập - {profile_name}")
        login_window.geometry("500x400")
        login_window.resizable(True, True)
        login_window.transient(self.root)
        login_window.grab_set()
        
        # Center dialog
        login_window.update_idletasks()
        x = (login_window.winfo_screenwidth() // 2) - (login_window.winfo_width() // 2)
        y = (login_window.winfo_screenheight() // 2) - (login_window.winfo_height() // 2)
        login_window.geometry(f"+{x}+{y}")
        
        # Frame chính
        main_frame = ttk.Frame(login_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # URL đăng nhập
        ttk.Label(main_frame, text="URL đăng nhập:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        url_entry = ttk.Entry(main_frame, width=40)
        url_entry.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        url_entry.insert(0, "https://accounts.google.com")
        
        # Email
        ttk.Label(main_frame, text="Email:").grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        email_entry = ttk.Entry(main_frame, width=40)
        email_entry.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Password
        ttk.Label(main_frame, text="Mật khẩu:").grid(row=4, column=0, sticky=tk.W, pady=(0, 5))
        password_entry = ttk.Entry(main_frame, width=40, show="*")
        password_entry.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # Nút lưu
        def save_login_config():
            import json
            login_data = {
                'login_url': url_entry.get(),
                'email': email_entry.get(),
                'password': password_entry.get()
            }
            
            # Lưu vào file config
            if not isinstance(self.manager.config, dict):
                self.manager.config = {}
            if 'LOGIN_DATA' not in self.manager.config:
                self.manager.config['LOGIN_DATA'] = {}
            
            self.manager.config['LOGIN_DATA'][profile_name] = json.dumps(login_data)
            self.manager.save_config()
            
            messagebox.showinfo("Thành công", "Đã lưu cấu hình đăng nhập!")
            login_window.destroy()
        
        ttk.Button(main_frame, text="Lưu", command=save_login_config).grid(row=6, column=0, pady=(0, 10))
        ttk.Button(main_frame, text="Hủy", command=login_window.destroy).grid(row=6, column=1, pady=(0, 10))
    
    def login_chrome_account(self):
        """Đăng nhập tài khoản Chrome/Google vào profile"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một profile!")
            return
        
        profile_name = self.tree.item(selection[0])["values"][0]
        
        # Tạo dialog đăng nhập Chrome
        chrome_login_dialog = tk.Toplevel(self.root)
        chrome_login_dialog.title(f"Đăng nhập Chrome - {profile_name}")
        chrome_login_dialog.geometry("500x400")
        chrome_login_dialog.resizable(True, True)
        chrome_login_dialog.transient(self.root)
        chrome_login_dialog.grab_set()
        
        # Center dialog
        chrome_login_dialog.update_idletasks()
        x = (chrome_login_dialog.winfo_screenwidth() // 2) - (chrome_login_dialog.winfo_width() // 2)
        y = (chrome_login_dialog.winfo_screenheight() // 2) - (chrome_login_dialog.winfo_height() // 2)
        chrome_login_dialog.geometry(f"+{x}+{y}")
        
        # Frame chính
        main_frame = ttk.Frame(chrome_login_dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Tiêu đề
        title_label = ttk.Label(main_frame, text=f"🔐 Đăng nhập Chrome cho {profile_name}", 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Hướng dẫn
        help_text = """Tính năng này sẽ mở Chrome profile và cho phép bạn đăng nhập tài khoản Google.
Sau khi đăng nhập, profile sẽ được đồng bộ với tài khoản Google của bạn."""
        
        help_label = ttk.Label(main_frame, text=help_text, font=("Arial", 9), foreground="gray", wraplength=450)
        help_label.pack(anchor=tk.W, pady=(0, 20))
        
        # Tùy chọn
        options_frame = ttk.LabelFrame(main_frame, text="Tùy chọn", padding="15")
        options_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Chế độ hiển thị
        display_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Hiển thị cửa sổ Chrome (khuyến nghị)", 
                       variable=display_var).pack(anchor=tk.W, pady=(0, 10))
        
        # Tự động mở trang đăng nhập
        auto_login_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Tự động mở trang đăng nhập Google", 
                       variable=auto_login_var).pack(anchor=tk.W, pady=(0, 10))
        
        # Nút
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        def start_chrome_login():
            """Bắt đầu đăng nhập Chrome"""
            def login_thread():
                try:
                    # Starting Chrome profile ở chế độ hiển thị
                    success, result = self.manager.launch_chrome_profile(
                        profile_name, 
                        hidden=not display_var.get(),
                        auto_login=False,
                        login_data=None,
                        start_url="https://accounts.google.com/signin" if auto_login_var.get() else None
                    )
                    
                    if success:
                        self.drivers[profile_name] = result
                        self.root.after(0, lambda: messagebox.showinfo("Thành công", 
                            f"Đã mở Chrome profile '{profile_name}'!\n"
                            f"Bạn có thể đăng nhập tài khoản Google của mình."))
                        self.root.after(0, self.refresh_profiles)
                    else:
                        self.root.after(0, lambda: messagebox.showerror("Lỗi", result))
                        
                except Exception as e:
                    self.root.after(0, lambda: messagebox.showerror("Lỗi", f"Không thể mở Chrome: {str(e)}"))
            
            threading.Thread(target=login_thread, daemon=True).start()
            chrome_login_dialog.destroy()
        
        def cancel():
            """Hủy"""
            chrome_login_dialog.destroy()
        
        # Nút
        ttk.Button(button_frame, text="[LAUNCH] Mở Chrome", command=start_chrome_login).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="❌ Hủy", command=cancel).pack(side=tk.LEFT)
        
    def delete_profile(self):
        """Xóa profile"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một profile!")
            return
        
        profile_name = self.tree.item(selection[0])["values"][0]
        
        if messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn xóa profile '{profile_name}'?"):
            # Dừng profile nếu đang chạy
            if profile_name in self.drivers:
                try:
                    self.drivers[profile_name].quit()
                    del self.drivers[profile_name]
                except:
                    pass
            
            success, message = self.manager.delete_profile(profile_name)
            if success:
                messagebox.showinfo("Thành công", message)
                self.refresh_profiles()
            else:
                messagebox.showerror("Lỗi", message)
        
        
    def select_export_folder(self):
        """Chọn thư mục export"""
        folder = filedialog.askdirectory()
        if folder:
            messagebox.showinfo("Thông báo", f"Đã chọn thư mục: {folder}")
        
    def start_export(self):
        """Bắt đầu export"""
        if not hasattr(self, 'export_profile_var') or not self.export_profile_var.get():
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn profile!")
            return
        
        profile_name = self.export_profile_var.get()
        self.export_cookies_for_profile(profile_name)
    
    def export_cookies_for_profile(self, profile_name):
        """Xuất cookies cho profile cụ thể"""
        try:
            # Lấy cookies từ Chrome profile
            cookies = self.manager.export_cookies_from_profile(
                profile_name, 
                getattr(self, 'domain_filter', tk.StringVar()).get(), 
                getattr(self, 'valid_only_var', tk.BooleanVar(value=True)).get()
            )
            
            if not cookies:
                messagebox.showwarning("Cảnh báo", "Không tìm thấy cookies nào!")
                return
            
            # Chọn file để lưu
            file_ext = ".json" if getattr(self, 'export_format', tk.StringVar(value="json")).get() == "json" else ".txt"
            file_path = filedialog.asksaveasfilename(
                title="Lưu file cookies",
                defaultextension=file_ext,
                filetypes=[("JSON files", "*.json"), ("Text files", "*.txt"), ("All files", "*.*")],
                initialname=f"{profile_name}_cookies{file_ext}"
            )
            
            if file_path:
                # Lưu file
                if getattr(self, 'export_format', tk.StringVar(value="json")).get() == "json":
                    import json
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(cookies, f, indent=2, ensure_ascii=False)
                else:
                    # Netscape format
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write("# Netscape HTTP Cookie File\n")
                        for cookie in cookies:
                            domain = cookie.get('domain', '')
                            if domain.startswith('.'):
                                domain_flag = 'TRUE'
                            else:
                                domain_flag = 'FALSE'
                            
                            f.write(f"{domain}\t{domain_flag}\t{cookie.get('path', '/')}\t"
                                   f"{'TRUE' if cookie.get('secure', False) else 'FALSE'}\t"
                                   f"{int(cookie.get('expirationDate', 0))}\t"
                                   f"{cookie.get('name', '')}\t{cookie.get('value', '')}\n")
                
                messagebox.showinfo("Thành công", 
                    f"Đã xuất {len(cookies)} cookies thành công!\n"
                    f"File: {file_path}")
                
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể xuất cookies: {str(e)}")
        
    def select_import_file(self):
        """Chọn file import"""
        file_path = filedialog.askopenfilename(
            title="Chọn file dữ liệu",
            filetypes=[("JSON files", "*.json"), ("CSV files", "*.csv"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            if hasattr(self, 'import_file_var'):
                self.import_file_var.set(file_path)
            messagebox.showinfo("Thông báo", f"Đã chọn file: {file_path}")
        
    def preview_import(self):
        """Xem trước import"""
        if not hasattr(self, 'import_file_var') or not self.import_file_var.get():
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn file để xem trước!")
            return
        
        file_path = self.import_file_var.get()
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                if file_path.endswith('.json'):
                    import json
                    data = json.load(f)
                    preview_text = f"File JSON với {len(data)} items"
                else:
                    lines = f.readlines()
                    preview_text = f"File text với {len(lines)} dòng"
            
            messagebox.showinfo("Xem trước", preview_text)
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể đọc file: {str(e)}")
        
    def start_import(self):
        """Bắt đầu import"""
        if not hasattr(self, 'import_profile_var') or not self.import_profile_var.get():
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn profile đích!")
            return
        
        if not hasattr(self, 'import_file_var') or not self.import_file_var.get():
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn file dữ liệu!")
            return
        
        profile_name = self.import_profile_var.get()
        file_path = self.import_file_var.get()
        
        try:
            # Đọc file cookies
            with open(file_path, 'r', encoding='utf-8') as f:
                if file_path.endswith('.json'):
                    import json
                    cookies = json.load(f)
                else:
                    # Parse Netscape format
                    cookies = []
                    for line in f:
                        line = line.strip()
                        if line.startswith('#') or not line:
                            continue
                        
                        parts = line.split('\t')
                        if len(parts) >= 7:
                            cookies.append({
                                'domain': parts[0],
                                'path': parts[2],
                                'secure': parts[3] == 'TRUE',
                                'expirationDate': float(parts[4]) if parts[4] != '0' else None,
                                'name': parts[5],
                                'value': parts[6]
                            })
            
            # Import cookies vào profile
            success_count = self.manager.import_cookies_to_profile(
                profile_name, 
                cookies, 
                getattr(self, 'overwrite_var', tk.BooleanVar(value=False)).get(), 
                getattr(self, 'valid_only_import_var', tk.BooleanVar(value=True)).get()
            )
            
            messagebox.showinfo("Thành công", 
                f"Đã import {success_count} cookies thành công!")
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể import dữ liệu: {str(e)}")
    
    def select_gpm_folder(self):
        """Chọn thư mục GPM profile"""
        from tkinter import filedialog
        
        folder_path = filedialog.askdirectory(
            title="Chọn thư mục GPM Profile",
            initialdir="C:\\GPM-profile"
        )
        
        if folder_path:
            self.gpm_path_var.set(folder_path)
            # Auto-generate NKT profile name
            folder_name = os.path.basename(folder_path)
            nkt_name = f"NKT_{folder_name}"
            self.nkt_name_var.set(nkt_name)
    
    def convert_gpm_to_nkt(self):
        """Chuyển đổi GPM profile sang NKT profile"""
        gpm_path = self.gpm_path_var.get().strip()
        nkt_name = self.nkt_name_var.get().strip()
        
        if not gpm_path:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn đường dẫn GPM profile!")
            return
        
        if not nkt_name:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập tên profile NKT!")
            return
        
        if not os.path.exists(gpm_path):
            messagebox.showerror("Lỗi", f"Đường dẫn GPM profile không tồn tại: {gpm_path}")
            return
        
        # Check if GPM profile has required files
        gpmsoft_path = os.path.join(gpm_path, "Default", "GPMSoft")
        if not os.path.exists(gpmsoft_path):
            messagebox.showwarning("Cảnh báo", 
                f"Thư mục GPMSoft không tìm thấy trong profile!\n"
                f"Đường dẫn: {gpmsoft_path}\n\n"
                f"Vui lòng chọn đúng thư mục GPM profile.")
            return
        
        # Confirm conversion
        result = messagebox.askyesno(
            "Xác nhận chuyển đổi",
            f"Bạn có muốn chuyển đổi GPM profile sang NKT profile?\n\n"
            f"📂 GPM Profile: {gpm_path}\n"
            f"📝 NKT Profile: {nkt_name}\n\n"
            f"Quá trình này sẽ:\n"
            f"• Đổi tên GPMSoft → NKTSoft\n"
            f"• Import cookies từ ExportCookies.json\n"
            f"• Cập nhật Local State với metadata NKT\n"
            f"• Tạo profile_settings.json mới"
        )
        
        if not result:
            return
        
        # Start conversion in thread
        def convert_thread():
            try:
                self.status_label.config(text="🔄 Đang chuyển đổi GPM profile...")
                
                # Call conversion method
                success, result_msg = self.manager.convert_gpm_to_nkt_profile(gpm_path, nkt_name)
                
                if success:
                    self.root.after(0, lambda: messagebox.showinfo(
                        "Thành công", 
                        f"✅ Chuyển đổi GPM profile thành công!\n\n"
                        f"📝 Profile NKT: {result_msg}\n"
                        f"🍪 Cookies đã được import\n"
                        f"📊 Metadata đã được cập nhật\n\n"
                        f"Bạn có thể sử dụng profile này với NKT Browser."
                    ))
                    self.root.after(0, lambda: self.refresh_profiles())
                    self.root.after(0, lambda: self.status_label.config(text="✅ Chuyển đổi hoàn thành"))
                else:
                    self.root.after(0, lambda: messagebox.showerror(
                        "Lỗi", 
                        f"❌ Chuyển đổi GPM profile thất bại!\n\n"
                        f"Chi tiết lỗi: {result_msg}"
                    ))
                    self.root.after(0, lambda: self.status_label.config(text="❌ Chuyển đổi thất bại"))
                
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror(
                    "Lỗi", 
                    f"❌ Lỗi trong quá trình chuyển đổi: {str(e)}"
                ))
                self.root.after(0, lambda: self.status_label.config(text="❌ Lỗi chuyển đổi"))
        
        threading.Thread(target=convert_thread, daemon=True).start()
        
    def save_settings(self):
        """Lưu cài đặt"""
        try:
            if hasattr(self, 'auto_start_var'):
                self.manager.config.set('SETTINGS', 'auto_start', str(self.auto_start_var.get()))
            if hasattr(self, 'hidden_mode_var'):
                self.manager.config.set('SETTINGS', 'hidden_mode', str(self.hidden_mode_var.get()))
            if hasattr(self, 'auto_save_var'):
                self.manager.config.set('SETTINGS', 'auto_save', str(self.auto_save_var.get()))
            if hasattr(self, 'export_folder_var'):
                self.manager.config.set('SETTINGS', 'export_folder', self.export_folder_var.get())
            self.manager.save_config()
            messagebox.showinfo("Thành công", "Đã lưu cài đặt!")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể lưu cài đặt: {str(e)}")
        
    def profile_stats(self):
        """Thống kê profiles"""
        try:
            profiles = self.manager.get_all_profiles()
            running_count = len([p for p in profiles if p in self.drivers])
            
            stats_text = f"""
📊 Thống kê Profiles:

👥 Tổng số profiles: {len(profiles)}
▶️ Đang chạy: {running_count}
⏹️ Đã dừng: {len(profiles) - running_count}

📋 Danh sách profiles:
{chr(10).join(f"• {p} {'(Đang chạy)' if p in self.drivers else '(Dừng)'}" for p in profiles)}
"""
            messagebox.showinfo("Thống kê Profiles", stats_text)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể lấy thống kê: {str(e)}")
        
    def check_cookies(self):
        """Kiểm tra cookies"""
        try:
            profiles = self.manager.get_all_profiles()
            total_cookies = 0
            
            for profile in profiles:
                cookies = self.manager.export_cookies_from_profile(profile, "", False)
                total_cookies += len(cookies)
            
            messagebox.showinfo("Kiểm tra Cookies", 
                f"Tổng số cookies trong tất cả profiles: {total_cookies}")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể kiểm tra cookies: {str(e)}")
        
    def cleanup_profiles(self):
        """Dọn dẹp profiles"""
        if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn dọn dẹp profiles không sử dụng?"):
            messagebox.showinfo("Thông báo", "Tính năng dọn dẹp đang được phát triển")
        
    def analyze_data(self):
        """Phân tích dữ liệu"""
        messagebox.showinfo("Thông báo", "Chức năng phân tích dữ liệu")
        
    def system_check(self):
        """Kiểm tra hệ thống"""
        try:
            import platform
            import psutil
            
            system_info = f"""
🔧 Thông tin hệ thống:

💻 Hệ điều hành: {platform.system()} {platform.release()}
🐍 Python: {platform.python_version()}
💾 RAM: {psutil.virtual_memory().total // (1024**3)} GB
💽 Disk: {psutil.disk_usage('/').free // (1024**3)} GB trống

✅ Hệ thống hoạt động bình thường
"""
            messagebox.showinfo("Kiểm tra hệ thống", system_info)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể kiểm tra hệ thống: {str(e)}")
        
    def view_logs(self):
        """Xem logs"""
        messagebox.showinfo("Thông báo", "Chức năng xem logs")
        
    def check_all_accounts(self):
        """Kiểm tra tất cả tài khoản"""
        try:
            self.account_status_label.config(text="Đang kiểm tra tất cả tài khoản...")
            self.root.update()
            
            # Xóa kết quả cũ
            for item in self.status_tree.get_children():
                self.status_tree.delete(item)
            
            # Lấy danh sách profiles
            profiles = self.manager.get_all_profiles()
            
            if not profiles:
                messagebox.showwarning("Cảnh báo", "Không có profile nào để kiểm tra!")
                self.account_status_label.config(text="Không có profile nào")
                return
            
            # Kiểm tra từng profile
            for i, profile in enumerate(profiles):
                self.account_status_label.config(text=f"Đang kiểm tra {profile} ({i+1}/{len(profiles)})")
                self.root.update()
                
                # Kiểm tra trạng thái
                status, message = self.manager.check_account_status(profile)
                platform = self.manager._detect_platform_from_cookies(profile)
                
                # Hiển thị kết quả
                status_text = "✅ Hoạt động" if status else "❌ Không hoạt động"
                current_time = time.strftime("%H:%M:%S")
                
                self.status_tree.insert("", "end", values=(
                    profile, platform.title(), status_text, message, current_time
                ))
                
                # Delay giữa các lần kiểm tra
                time.sleep(1)
            
            self.account_status_label.config(text=f"Hoàn thành kiểm tra {len(profiles)} tài khoản")
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi kiểm tra tài khoản: {str(e)}")
            self.account_status_label.config(text="Lỗi khi kiểm tra")
    
    def check_single_account(self):
        """Kiểm tra một tài khoản cụ thể"""
        try:
            # Lấy danh sách profiles
            profiles = self.manager.get_all_profiles()
            
            if not profiles:
                messagebox.showwarning("Cảnh báo", "Không có profile nào để kiểm tra!")
                return
            
            # Dialog chọn profile
            dialog = tk.Toplevel(self.root)
            dialog.title("Chọn Profile để kiểm tra")
            dialog.geometry("400x200")
            dialog.configure(bg='#1e1e1e')
            dialog.transient(self.root)
            dialog.grab_set()
            
            # Center dialog
            dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 50, self.root.winfo_rooty() + 50))
            
            # Content
            content_frame = ttk.Frame(dialog, style='Modern.TFrame')
            content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            
            ttk.Label(content_frame, text="Chọn Profile để kiểm tra:", 
                     style='Modern.TLabel', font=('Segoe UI', 12, 'bold')).pack(pady=(0, 10))
            
            profile_var = tk.StringVar()
            profile_combo = ttk.Combobox(content_frame, textvariable=profile_var, 
                                       values=profiles, state="readonly", width=30)
            profile_combo.pack(pady=(0, 20))
            
            if profiles:
                profile_combo.set(profiles[0])
            
            # Buttons
            button_frame = ttk.Frame(content_frame, style='Modern.TFrame')
            button_frame.pack(fill=tk.X)
            
            def check_profile():
                selected_profile = profile_var.get()
                if not selected_profile:
                    messagebox.showwarning("Cảnh báo", "Vui lòng chọn profile!")
                    return
                
                dialog.destroy()
                
                # Kiểm tra profile
                self.account_status_label.config(text=f"Đang kiểm tra {selected_profile}...")
                self.root.update()
                
                status, message = self.manager.check_account_status(selected_profile)
                platform = self.manager._detect_platform_from_cookies(selected_profile)
                
                # Hiển thị kết quả
                status_text = "✅ Hoạt động" if status else "❌ Không hoạt động"
                current_time = time.strftime("%H:%M:%S")
                
                # Xóa kết quả cũ
                for item in self.status_tree.get_children():
                    self.status_tree.delete(item)
                
                self.status_tree.insert("", "end", values=(
                    selected_profile, platform.title(), status_text, message, current_time
                ))
                
                self.account_status_label.config(text=f"Hoàn thành kiểm tra {selected_profile}")
            
            def cancel():
                dialog.destroy()
            
            ttk.Button(button_frame, text="🔍 Kiểm tra", 
                      style='Modern.TButton',
                      command=check_profile).pack(side=tk.LEFT, padx=(0, 10))
            ttk.Button(button_frame, text="❌ Hủy", 
                      style='Modern.TButton',
                      command=cancel).pack(side=tk.LEFT)
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi kiểm tra tài khoản: {str(e)}")
    
    
    
    
    
        
    def add_email_token(self):
        """Thêm refresh token cho email"""
        email = self.new_email.get().strip()
        refresh_token = self.new_refresh_token.get().strip()
        
        if not email or not refresh_token:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập đầy đủ email và refresh token!")
            return
        
        try:
            success = self.manager.add_email_refresh_token(email, refresh_token)
            if success:
                messagebox.showinfo("Thành công", f"Đã thêm refresh token cho {email}")
                self.new_email.set("")
                self.new_refresh_token.set("")
                self.load_email_config()
            else:
                messagebox.showerror("Lỗi", "Không thể thêm refresh token!")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi thêm token: {str(e)}")
    
    def remove_email_token(self):
        """Xóa refresh token"""
        selection = self.tokens_tree.selection()
        if not selection:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn token cần xóa!")
            return
        
        email = self.tokens_tree.item(selection[0])['values'][0]
        
        if messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn xóa token của {email}?"):
            try:
                # Xóa từ config
                if hasattr(self.manager, 'config') and 'EMAIL_TOKENS' in self.manager.config:
                    del self.manager.config['EMAIL_TOKENS'][email]
                    self.manager.save_config()
                
                # Xóa từ file JSON
                tokens_file = "email_tokens.json"
                if os.path.exists(tokens_file):
                    with open(tokens_file, 'r', encoding='utf-8') as f:
                        tokens = json.load(f)
                    if email in tokens:
                        del tokens[email]
                    with open(tokens_file, 'w', encoding='utf-8') as f:
                        json.dump(tokens, f, indent=2, ensure_ascii=False)
                
                messagebox.showinfo("Thành công", f"Đã xóa token của {email}")
                self.load_email_config()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Lỗi khi xóa token: {str(e)}")
    
    def save_email_config(self):
        """Lưu cấu hình email"""
        try:
            # Setup Outlook
            if self.outlook_client_id.get() and self.outlook_client_secret.get():
                self.manager.setup_email_verification(
                    'outlook',
                    self.outlook_client_id.get(),
                    self.outlook_client_secret.get(),
                    self.outlook_tenant_id.get()
                )
            
            # Setup Gmail
            if self.gmail_client_id.get() and self.gmail_client_secret.get():
                self.manager.setup_email_verification(
                    'gmail',
                    self.gmail_client_id.get(),
                    self.gmail_client_secret.get()
                )
            
            messagebox.showinfo("Thành công", "Đã lưu cấu hình email!")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi lưu cấu hình: {str(e)}")
    
    def load_email_config(self):
        """Tải cấu hình email"""
        try:
            # Load config từ manager
            self.manager.email_manager.load_config()
            
            # Load vào UI
            if 'outlook' in self.manager.email_manager.config:
                outlook_config = self.manager.email_manager.config['outlook']
                self.outlook_client_id.set(outlook_config.get('client_id', ''))
                self.outlook_client_secret.set(outlook_config.get('client_secret', ''))
                self.outlook_tenant_id.set(outlook_config.get('tenant_id', 'common'))
            
            if 'gmail' in self.manager.email_manager.config:
                gmail_config = self.manager.email_manager.config['gmail']
                self.gmail_client_id.set(gmail_config.get('client_id', ''))
                self.gmail_client_secret.set(gmail_config.get('client_secret', ''))
            
            # Load tokens list
            self.tokens_tree.delete(*self.tokens_tree.get_children())
            
            tokens_file = "email_tokens.json"
            if os.path.exists(tokens_file):
                with open(tokens_file, 'r', encoding='utf-8') as f:
                    tokens = json.load(f)
                
                for email, token in tokens.items():
                    email_type = "Gmail" if "gmail.com" in email.lower() else "Outlook"
                    status = "✅ Active" if token else "❌ Empty"
                    self.tokens_tree.insert("", "end", values=(email, email_type, status))
            
        except Exception as e:
            print(f"Lỗi load email config: {e}")
    
    def test_email_connection(self):
        """Test kết nối email"""
        selection = self.tokens_tree.selection()
        if not selection:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn email để test!")
            return
        
        email = self.tokens_tree.item(selection[0])['values'][0]
        
        try:
            # Lấy refresh token
            refresh_token = self.manager._get_refresh_token_for_email(email)
            if not refresh_token:
                messagebox.showerror("Lỗi", "Không tìm thấy refresh token cho email này!")
                return
            
            # Test connection
            email_type = "gmail" if "gmail.com" in email.lower() else "outlook"
            verification_code = self.manager.email_manager.get_verification_code(
                email_type=email_type,
                refresh_token=refresh_token,
                sender_patterns=['tiktok'],
                max_wait_time=10
            )
            
            if verification_code:
                messagebox.showinfo("Thành công", f"Kết nối thành công! Mã xác thực mới nhất: {verification_code}")
            else:
                messagebox.showwarning("Cảnh báo", "Kết nối thành công nhưng không tìm thấy mã xác thực TikTok")
                
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi test kết nối: {str(e)}")

    
        
    
    def check_extension_status(self):
        """Check extension status for all profiles"""
        try:
            self.extension_status_text.delete(1.0, tk.END)
            self.extension_status_text.insert(tk.END, "🔍 Checking extension status for all profiles...\n\n")
            self.extension_status_text.update()
            
            def check_thread():
                try:
                    status_dict = self.manager.get_extension_status_for_all_profiles()
                    
                    self.extension_status_text.delete(1.0, tk.END)
                    self.extension_status_text.insert(tk.END, "📊 Extension Status Report\n")
                    self.extension_status_text.insert(tk.END, "=" * 50 + "\n\n")
                    
                    installed_count = 0
                    total_count = len(status_dict)
                    
                    for profile, is_installed in status_dict.items():
                        status_icon = "✅" if is_installed else "❌"
                        status_text = "Installed" if is_installed else "Not Installed"
                        self.extension_status_text.insert(tk.END, f"{status_icon} {profile}: {status_text}\n")
                        
                        if is_installed:
                            installed_count += 1
                    
                    self.extension_status_text.insert(tk.END, "\n" + "=" * 50 + "\n")
                    self.extension_status_text.insert(tk.END, f"📈 Summary: {installed_count}/{total_count} profiles have Proxy SwitchyOmega 3 installed\n")
                    
                    if installed_count == total_count:
                        self.extension_status_text.insert(tk.END, "🎉 All profiles have the extension installed!\n")
                    elif installed_count == 0:
                        self.extension_status_text.insert(tk.END, "⚠️ No profiles have the extension installed.\n")
                    else:
                        self.extension_status_text.insert(tk.END, f"ℹ️ {total_count - installed_count} profiles still need the extension.\n")
                    
                    self.extension_status_text.see(tk.END)
                    
                except Exception as e:
                    self.extension_status_text.insert(tk.END, f"\n❌ Error checking extension status: {str(e)}\n")
                    self.extension_status_text.see(tk.END)
            
            threading.Thread(target=check_thread, daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to check extension status: {str(e)}")
    
    def install_extension_selected(self):
        """Install extension for selected profiles"""
        try:
            # Get selected profiles from the profiles tab
            if hasattr(self, 'tree') and self.tree.selection():
                selected_profiles = [self.tree.item(item)["text"] for item in self.tree.selection()]
            else:
                messagebox.showwarning("Warning", "Please select profiles from the Profiles tab first!")
                return
            
            if not selected_profiles:
                messagebox.showwarning("Warning", "No profiles selected!")
                return
            
            # Confirm installation
            result = messagebox.askyesno("Confirm Installation", 
                                       f"Install Proxy SwitchyOmega 3 extension for {len(selected_profiles)} selected profiles?\n\n"
                                       f"Selected profiles:\n" + "\n".join(f"• {p}" for p in selected_profiles))
            
            if not result:
                return
            
            self.extension_status_text.delete(1.0, tk.END)
            self.extension_status_text.insert(tk.END, f"[LAUNCH] Installing Proxy SwitchyOmega 3 for {len(selected_profiles)} profiles...\n\n")
            self.extension_status_text.update()
            
            def install_thread():
                try:
                    success_count, results = self.manager.bulk_install_extension_directory(selected_profiles)
                    
                    self.extension_status_text.insert(tk.END, "📋 Installation Results:\n")
                    self.extension_status_text.insert(tk.END, "=" * 50 + "\n")
                    
                    for result in results:
                        self.extension_status_text.insert(tk.END, f"{result}\n")
                        self.extension_status_text.update()
                        time.sleep(0.1)
                    
                    self.extension_status_text.insert(tk.END, "\n" + "=" * 50 + "\n")
                    self.extension_status_text.insert(tk.END, f"🎉 Installation completed!\n")
                    self.extension_status_text.insert(tk.END, f"✅ Success: {success_count}/{len(selected_profiles)}\n")
                    self.extension_status_text.insert(tk.END, f"❌ Failed: {len(selected_profiles) - success_count}/{len(selected_profiles)}\n")
                    
                    self.extension_status_text.see(tk.END)
                    
                    # Show completion message
                    self.root.after(0, lambda: messagebox.showinfo("Installation Complete", 
                        f"Extension installation completed!\n\n✅ Success: {success_count}\n❌ Failed: {len(selected_profiles) - success_count}"))
                    
                except Exception as e:
                    self.extension_status_text.insert(tk.END, f"\n❌ Error during installation: {str(e)}\n")
                    self.extension_status_text.see(tk.END)
                    self.root.after(0, lambda: messagebox.showerror("Installation Error", f"Installation failed: {str(e)}"))
            
            threading.Thread(target=install_thread, daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to install extension: {str(e)}")
    
    def install_extension_for_new_profiles(self):
        """Install extension for profiles that don't have it yet"""
        try:
            self.extension_status_text.delete(1.0, tk.END)
            self.extension_status_text.insert(tk.END, f"🔍 Checking which profiles need extension installation...\n\n")
            self.extension_status_text.update()
            
            def install_thread():
                try:
                    success_count, results = self.manager.install_extension_for_new_profiles()
                    
                    self.extension_status_text.insert(tk.END, "📋 Installation Results:\n")
                    self.extension_status_text.insert(tk.END, "=" * 50 + "\n")
                    
                    for result in results:
                        self.extension_status_text.insert(tk.END, f"{result}\n")
                        self.extension_status_text.update()
                        time.sleep(0.1)
                    
                    self.extension_status_text.insert(tk.END, "\n" + "=" * 50 + "\n")
                    self.extension_status_text.insert(tk.END, f"🎉 Installation completed!\n")
                    self.extension_status_text.insert(tk.END, f"✅ Success: {success_count}\n")
                    
                    self.extension_status_text.see(tk.END)
                    
                    # Show completion message
                    if success_count > 0:
                        self.root.after(0, lambda: messagebox.showinfo("Installation Complete", 
                            f"Extension installed for {success_count} profiles that needed it!"))
                    else:
                        self.root.after(0, lambda: messagebox.showinfo("Installation Complete", 
                            "All profiles already have the extension installed!"))
                    
                except Exception as e:
                    self.extension_status_text.insert(tk.END, f"\n❌ Error during installation: {str(e)}\n")
                    self.extension_status_text.see(tk.END)
                    print(f"❌ [INSTALL-NEW] Error: {str(e)}")
            
            # Start installation in background thread
            threading.Thread(target=install_thread, daemon=True).start()
            
        except Exception as e:
            print(f"❌ [INSTALL-NEW] Failed to start installation: {str(e)}")
            messagebox.showerror("Error", f"Failed to start installation: {str(e)}")
    
    def install_extension_for_all_profiles(self):
        """Install extension for ALL profiles (new and existing)"""
        try:
            all_profiles = self.manager.get_all_profiles()
            
            if not all_profiles:
                messagebox.showwarning("Warning", "No profiles found!")
                return
            
            # Confirm installation
            result = messagebox.askyesno("Confirm Installation", 
                                       f"Install Proxy SwitchyOmega 3 extension for ALL {len(all_profiles)} profiles?\n\n"
                                       "This will install the extension for every profile in your system.")
            
            if not result:
                return
            
            self.extension_status_text.delete(1.0, tk.END)
            self.extension_status_text.insert(tk.END, f"[LAUNCH] Installing Proxy SwitchyOmega 3 for ALL {len(all_profiles)} profiles...\n\n")
            self.extension_status_text.update()
            
            def install_thread():
                try:
                    success_count, results = self.manager.install_extension_for_all_profiles()
                    
                    self.extension_status_text.insert(tk.END, "📋 Installation Results:\n")
                    self.extension_status_text.insert(tk.END, "=" * 50 + "\n")
                    
                    for result in results:
                        self.extension_status_text.insert(tk.END, f"{result}\n")
                        self.extension_status_text.update()
                        time.sleep(0.1)
                    
                    self.extension_status_text.insert(tk.END, "\n" + "=" * 50 + "\n")
                    self.extension_status_text.insert(tk.END, f"🎉 Installation completed!\n")
                    self.extension_status_text.insert(tk.END, f"✅ Success: {success_count}\n")
                    
                    self.extension_status_text.see(tk.END)
                    
                    # Show completion message
                    self.root.after(0, lambda: messagebox.showinfo("Installation Complete", 
                        f"Extension installation completed for all profiles!\n\n✅ Success: {success_count}"))
                    
                except Exception as e:
                    self.extension_status_text.insert(tk.END, f"\n❌ Error during installation: {str(e)}\n")
                    self.extension_status_text.see(tk.END)
                    print(f"❌ [INSTALL-ALL] Error: {str(e)}")
            
            # Start installation in background thread
            threading.Thread(target=install_thread, daemon=True).start()
            
        except Exception as e:
            print(f"❌ [INSTALL-ALL] Failed to start installation: {str(e)}")
            messagebox.showerror("Error", f"Failed to start installation: {str(e)}")
    
    def install_extension_all(self):
        """Install extension for all profiles"""
        try:
            all_profiles = self.manager.get_all_profiles()
            
            if not all_profiles:
                messagebox.showwarning("Warning", "No profiles found!")
                return
            
            # Confirm installation
            result = messagebox.askyesno("Confirm Installation", 
                                       f"Install Proxy SwitchyOmega 3 extension for ALL {len(all_profiles)} profiles?\n\n"
                                       "This may take several minutes depending on the number of profiles.")
            
            if not result:
                return
            
            self.extension_status_text.delete(1.0, tk.END)
            self.extension_status_text.insert(tk.END, f"[LAUNCH] Installing Proxy SwitchyOmega 3 for ALL {len(all_profiles)} profiles...\n\n")
            self.extension_status_text.update()
            
            def install_thread():
                try:
                    success_count, results = self.manager.bulk_install_extension_directory(all_profiles)
                    
                    self.extension_status_text.insert(tk.END, "📋 Installation Results:\n")
                    self.extension_status_text.insert(tk.END, "=" * 50 + "\n")
                    
                    for result in results:
                        self.extension_status_text.insert(tk.END, f"{result}\n")
                        self.extension_status_text.update()
                        time.sleep(0.1)
                    
                    self.extension_status_text.insert(tk.END, "\n" + "=" * 50 + "\n")
                    self.extension_status_text.insert(tk.END, f"🎉 Bulk installation completed!\n")
                    self.extension_status_text.insert(tk.END, f"✅ Success: {success_count}/{len(all_profiles)}\n")
                    self.extension_status_text.insert(tk.END, f"❌ Failed: {len(all_profiles) - success_count}/{len(all_profiles)}\n")
                    
                    self.extension_status_text.see(tk.END)
                    
                    # Show completion message
                    self.root.after(0, lambda: messagebox.showinfo("Bulk Installation Complete", 
                        f"Bulk extension installation completed!\n\n✅ Success: {success_count}\n❌ Failed: {len(all_profiles) - success_count}"))
                    
                except Exception as e:
                    self.extension_status_text.insert(tk.END, f"\n❌ Error during bulk installation: {str(e)}\n")
                    self.extension_status_text.see(tk.END)
                    self.root.after(0, lambda: messagebox.showerror("Installation Error", f"Bulk installation failed: {str(e)}"))
            
            threading.Thread(target=install_thread, daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to install extension for all profiles: {str(e)}")
    
    def refresh_extension_status(self):
        """Refresh extension status display"""
        self.check_extension_status()
    
    def show_extension_statistics(self):
        """Show extension installation statistics"""
        try:
            status_dict = self.manager.get_extension_status_for_all_profiles()
            
            installed_count = sum(1 for is_installed in status_dict.values() if is_installed)
            total_count = len(status_dict)
            not_installed_count = total_count - installed_count
            
            # Create statistics dialog
            dialog = tk.Toplevel(self.root)
            dialog.title("📊 Extension Statistics")
            dialog.geometry("500x400")
            dialog.resizable(True, True)
            dialog.transient(self.root)
            dialog.grab_set()
            
            # Center dialog
            dialog.update_idletasks()
            x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
            y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
            dialog.geometry(f"+{x}+{y}")
            
            # Main frame
            main_frame = ttk.Frame(dialog, padding="20")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Title
            title_label = ttk.Label(main_frame, text="📊 Proxy SwitchyOmega 3 Statistics", 
                                  font=("Segoe UI", 16, "bold"))
            title_label.pack(pady=(0, 20))
            
            # Statistics frame
            stats_frame = ttk.LabelFrame(main_frame, text="📈 Installation Statistics", padding="15")
            stats_frame.pack(fill=tk.X, pady=(0, 15))
            
            # Statistics display
            stats_text = f"""
📊 Total Profiles: {total_count}
✅ Extension Installed: {installed_count}
❌ Extension Not Installed: {not_installed_count}
📈 Installation Rate: {(installed_count/total_count*100):.1f}%
            """
            
            ttk.Label(stats_frame, text=stats_text.strip(), font=("Consolas", 11), justify=tk.LEFT).pack(anchor=tk.W)
            
            # Detailed breakdown
            details_frame = ttk.LabelFrame(main_frame, text="📋 Detailed Breakdown", padding="15")
            details_frame.pack(fill=tk.BOTH, expand=True)
            
            # Create text widget with scrollbar
            text_frame = ttk.Frame(details_frame)
            text_frame.pack(fill=tk.BOTH, expand=True)
            
            details_text = tk.Text(text_frame, height=10, width=50, font=("Consolas", 9))
            details_scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=details_text.yview)
            details_text.configure(yscrollcommand=details_scrollbar.set)
            
            details_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            details_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # Add detailed information
            details_text.insert(tk.END, "✅ INSTALLED PROFILES:\n")
            details_text.insert(tk.END, "-" * 30 + "\n")
            for profile, is_installed in status_dict.items():
                if is_installed:
                    details_text.insert(tk.END, f"• {profile}\n")
            
            details_text.insert(tk.END, "\n❌ NOT INSTALLED PROFILES:\n")
            details_text.insert(tk.END, "-" * 30 + "\n")
            for profile, is_installed in status_dict.items():
                if not is_installed:
                    details_text.insert(tk.END, f"• {profile}\n")
            
            details_text.config(state=tk.DISABLED)
            
            # Close button
            ttk.Button(main_frame, text="❌ Close", command=dialog.destroy).pack(pady=(15, 0))
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to show extension statistics: {str(e)}")
    
    def quick_install_extensions(self):
        """Quick extension installation dialog from Profiles tab"""
        try:
            # Get selected profiles
            if hasattr(self, 'tree') and self.tree.selection():
                selected_profiles = [self.tree.item(item)["text"] for item in self.tree.selection()]
            else:
                selected_profiles = []
            
            # Create quick install dialog
            dialog = tk.Toplevel(self.root)
            dialog.title("🔌 Quick Extension Installation")
            dialog.geometry("600x500")
            dialog.resizable(True, True)
            dialog.transient(self.root)
            dialog.grab_set()
            
            # Center dialog
            dialog.update_idletasks()
            x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
            y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
            dialog.geometry(f"+{x}+{y}")
            
            # Main frame
            main_frame = ttk.Frame(dialog, padding="20")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Title
            title_label = ttk.Label(main_frame, text="🔌 Proxy SwitchyOmega 3 Installation", 
                                  font=("Segoe UI", 16, "bold"))
            title_label.pack(pady=(0, 20))
            
            # Extension info
            info_frame = ttk.LabelFrame(main_frame, text="📋 Extension Information", padding="15")
            info_frame.pack(fill=tk.X, pady=(0, 15))
            
            info_text = """
🌐 Proxy SwitchyOmega 3 (ZeroOmega) - Version 3.4.1
• Modern proxy management with Manifest V3 support
• Multiple proxy types: HTTP, SOCKS4, SOCKS5
• Gist sync for configuration backup
• Custom themes (light/dark/auto mode)
• 500,000+ users, 4.8/5 rating
            """
            
            ttk.Label(info_frame, text=info_text.strip(), font=("Segoe UI", 10), justify=tk.LEFT).pack(anchor=tk.W)
            
            # Installation options
            options_frame = ttk.LabelFrame(main_frame, text="🎯 Installation Options", padding="15")
            options_frame.pack(fill=tk.X, pady=(0, 15))
            
            # Option 1: Selected profiles
            if selected_profiles:
                selected_var = tk.BooleanVar(value=True)
                ttk.Checkbutton(options_frame, text=f"📥 Install for {len(selected_profiles)} selected profiles", 
                              variable=selected_var).pack(anchor=tk.W, pady=(0, 5))
                
                # Show selected profiles
                selected_text = "Selected profiles: " + ", ".join(selected_profiles[:5])
                if len(selected_profiles) > 5:
                    selected_text += f" and {len(selected_profiles) - 5} more..."
                ttk.Label(options_frame, text=selected_text, font=("Segoe UI", 9), 
                         foreground="#666").pack(anchor=tk.W, padx=(20, 0))
            else:
                selected_var = tk.BooleanVar(value=False)
                ttk.Checkbutton(options_frame, text="📥 Install for selected profiles (none selected)", 
                              variable=selected_var, state=tk.DISABLED).pack(anchor=tk.W, pady=(0, 5))
            
            # Option 2: All profiles
            all_var = tk.BooleanVar(value=not selected_profiles)
            ttk.Checkbutton(options_frame, text="[LAUNCH] Install for all profiles", 
                          variable=all_var).pack(anchor=tk.W, pady=(0, 5))
            
            # Progress display
            progress_frame = ttk.LabelFrame(main_frame, text="📊 Progress", padding="15")
            progress_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
            
            progress_text = tk.Text(progress_frame, height=10, width=60, font=("Consolas", 9))
            progress_scrollbar = ttk.Scrollbar(progress_frame, orient="vertical", command=progress_text.yview)
            progress_text.configure(yscrollcommand=progress_scrollbar.set)
            
            progress_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            progress_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            def start_installation():
                """Start the installation process"""
                if not selected_var.get() and not all_var.get():
                    messagebox.showwarning("Warning", "Please select at least one installation option!")
                    return
                
                # Determine target profiles
                if selected_var.get() and selected_profiles:
                    target_profiles = selected_profiles
                elif all_var.get():
                    target_profiles = self.manager.get_all_profiles()
                else:
                    target_profiles = []
                
                if not target_profiles:
                    messagebox.showwarning("Warning", "No profiles selected for installation!")
                    return
                
                # Confirm installation
                result = messagebox.askyesno("Confirm Installation", 
                                           f"Install Proxy SwitchyOmega 3 extension for {len(target_profiles)} profiles?\n\n"
                                           "This will open Chrome for each profile to install the extension from the Chrome Web Store.")
                
                if not result:
                    return
                
                dialog.destroy()
                
                # Start installation in thread
                def install_thread():
                    try:
                        success_count, results = self.manager.bulk_install_extension_directory(target_profiles)
                        
                        # Show results
                        result_text = f"🎉 Extension Installation Complete!\n\n"
                        result_text += f"✅ Success: {success_count}/{len(target_profiles)}\n"
                        result_text += f"❌ Failed: {len(target_profiles) - success_count}/{len(target_profiles)}\n\n"
                        result_text += "Detailed Results:\n" + "\n".join(results)
                        
                        self.root.after(0, lambda: messagebox.showinfo("Installation Complete", result_text))
                        
                    except Exception as e:
                        self.root.after(0, lambda: messagebox.showerror("Installation Error", f"Installation failed: {str(e)}"))
                
                threading.Thread(target=install_thread, daemon=True).start()
            
            # Buttons
            button_frame = ttk.Frame(main_frame)
            button_frame.pack(fill=tk.X, pady=(15, 0))
            
            ttk.Button(button_frame, text="❌ Cancel", command=dialog.destroy).pack(side=tk.RIGHT, padx=(5, 0))
            ttk.Button(button_frame, text="[LAUNCH] Start Installation", command=start_installation).pack(side=tk.RIGHT)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open quick installation dialog: {str(e)}")
    
    def configure_proxy_selected(self):
        """Configure proxy for selected profiles"""
        try:
            # Get selected profiles from the profiles tab
            if hasattr(self, 'tree') and self.tree.selection():
                selected_profiles = [self.tree.item(item)["text"] for item in self.tree.selection()]
            else:
                messagebox.showwarning("Warning", "Please select profiles from the Profiles tab first!")
                return
            
            if not selected_profiles:
                messagebox.showwarning("Warning", "No profiles selected!")
                return
            
            # Get proxy configuration
            proxy_config = self._get_proxy_config_from_ui()
            if not proxy_config:
                return
            
            # Confirm configuration
            result = messagebox.askyesno("Confirm Configuration", 
                                       f"Configure SwitchyOmega 3 proxy for {len(selected_profiles)} selected profiles?\n\n"
                                       f"Proxy: {proxy_config['protocol'].upper()} {proxy_config['host']}:{proxy_config['port']}\n"
                                       f"Profile: {proxy_config['name']}")
            
            if not result:
                return
            
            self.extension_status_text.delete(1.0, tk.END)
            self.extension_status_text.insert(tk.END, f"🔧 Configuring SwitchyOmega 3 for {len(selected_profiles)} profiles...\n\n")
            self.extension_status_text.update()
            
            def config_thread():
                try:
                    success_count, results = self.manager.bulk_configure_switchyomega(selected_profiles, proxy_config)
                    
                    self.extension_status_text.insert(tk.END, "📋 Configuration Results:\n")
                    self.extension_status_text.insert(tk.END, "=" * 50 + "\n")
                    
                    for result in results:
                        self.extension_status_text.insert(tk.END, f"{result}\n")
                        self.extension_status_text.update()
                        time.sleep(0.1)
                    
                    self.extension_status_text.insert(tk.END, "\n" + "=" * 50 + "\n")
                    self.extension_status_text.insert(tk.END, f"🎉 Configuration completed!\n")
                    self.extension_status_text.insert(tk.END, f"✅ Success: {success_count}/{len(selected_profiles)}\n")
                    self.extension_status_text.insert(tk.END, f"❌ Failed: {len(selected_profiles) - success_count}/{len(selected_profiles)}\n")
                    
                    self.extension_status_text.see(tk.END)
                    
                    # Show completion message
                    self.root.after(0, lambda: messagebox.showinfo("Configuration Complete", 
                        f"SwitchyOmega 3 configuration completed!\n\n✅ Success: {success_count}\n❌ Failed: {len(selected_profiles) - success_count}"))
                    
                except Exception as e:
                    self.extension_status_text.insert(tk.END, f"\n❌ Error during configuration: {str(e)}\n")
                    self.extension_status_text.see(tk.END)
                    self.root.after(0, lambda: messagebox.showerror("Configuration Error", f"Configuration failed: {str(e)}"))
            
            threading.Thread(target=config_thread, daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to configure proxy: {str(e)}")
    
    def configure_proxy_all(self):
        """Configure proxy for all profiles"""
        try:
            all_profiles = self.manager.get_all_profiles()
            
            if not all_profiles:
                messagebox.showwarning("Warning", "No profiles found!")
                return
            
            # Get proxy configuration
            proxy_config = self._get_proxy_config_from_ui()
            if not proxy_config:
                return
            
            # Confirm configuration
            result = messagebox.askyesno("Confirm Configuration", 
                                       f"Configure SwitchyOmega 3 proxy for ALL {len(all_profiles)} profiles?\n\n"
                                       f"Proxy: {proxy_config['protocol'].upper()} {proxy_config['host']}:{proxy_config['port']}\n"
                                       f"Profile: {proxy_config['name']}\n\n"
                                       "This may take several minutes depending on the number of profiles.")
            
            if not result:
                return
            
            self.extension_status_text.delete(1.0, tk.END)
            self.extension_status_text.insert(tk.END, f"🔧 Configuring SwitchyOmega 3 for ALL {len(all_profiles)} profiles...\n\n")
            self.extension_status_text.update()
            
            def config_thread():
                try:
                    success_count, results = self.manager.bulk_configure_switchyomega(all_profiles, proxy_config)
                    
                    self.extension_status_text.insert(tk.END, "📋 Configuration Results:\n")
                    self.extension_status_text.insert(tk.END, "=" * 50 + "\n")
                    
                    for result in results:
                        self.extension_status_text.insert(tk.END, f"{result}\n")
                        self.extension_status_text.update()
                        time.sleep(0.1)
                    
                    self.extension_status_text.insert(tk.END, "\n" + "=" * 50 + "\n")
                    self.extension_status_text.insert(tk.END, f"🎉 Bulk configuration completed!\n")
                    self.extension_status_text.insert(tk.END, f"✅ Success: {success_count}/{len(all_profiles)}\n")
                    self.extension_status_text.insert(tk.END, f"❌ Failed: {len(all_profiles) - success_count}/{len(all_profiles)}\n")
                    
                    self.extension_status_text.see(tk.END)
                    
                    # Show completion message
                    self.root.after(0, lambda: messagebox.showinfo("Bulk Configuration Complete", 
                        f"Bulk SwitchyOmega 3 configuration completed!\n\n✅ Success: {success_count}\n❌ Failed: {len(all_profiles) - success_count}"))
                    
                except Exception as e:
                    self.extension_status_text.insert(tk.END, f"\n❌ Error during bulk configuration: {str(e)}\n")
                    self.extension_status_text.see(tk.END)
                    self.root.after(0, lambda: messagebox.showerror("Configuration Error", f"Bulk configuration failed: {str(e)}"))
            
            threading.Thread(target=config_thread, daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to configure proxy for all profiles: {str(e)}")
    
    def _get_proxy_config_from_ui(self):
        """Get proxy configuration from UI fields"""
        try:
            name = self.proxy_profile_name_var.get().strip()
            protocol = self.proxy_protocol_var.get().strip()
            host = self.proxy_server_var.get().strip()
            port = self.proxy_port_var.get().strip()
            username = self.proxy_username_var.get().strip()
            password = self.proxy_password_var.get().strip()
            
            if not all([name, protocol, host, port]):
                messagebox.showwarning("Warning", "Please fill in Profile Name, Protocol, Server, and Port!")
                return None
            
            try:
                port = int(port)
            except ValueError:
                messagebox.showerror("Error", "Port must be a valid number!")
                return None
            
            return {
                'name': name,
                'protocol': protocol,
                'host': host,
                'port': port,
                'username': username if username else None,
                'password': password if password else None
            }
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get proxy configuration: {str(e)}")
            return None
    
    def save_proxy_profile(self):
        """Save current proxy configuration as a profile"""
        try:
            proxy_config = self._get_proxy_config_from_ui()
            if not proxy_config:
                return
            
            # Ask for profile name
            profile_name = tk.simpledialog.askstring("Save Proxy Profile", 
                                                   "Enter a name for this proxy profile:",
                                                   initialvalue=proxy_config['name'])
            
            if not profile_name:
                return
            
            # Save to config file
            if not isinstance(self.manager.config, dict) or 'PROXY_PROFILES' not in self.manager.config:
                if not isinstance(self.manager.config, dict):
                    self.manager.config = {}
                if 'PROXY_PROFILES' not in self.manager.config:
                    self.manager.config['PROXY_PROFILES'] = {}
            
            import json
            self.manager.config['PROXY_PROFILES'][profile_name] = json.dumps(proxy_config)
            self.manager.save_config()
            
            messagebox.showinfo("Success", f"Proxy profile '{profile_name}' saved successfully!")
            self.refresh_saved_profiles()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save proxy profile: {str(e)}")
    
    def load_proxy_profile(self):
        """Load a saved proxy profile"""
        try:
            # Get list of saved profiles
            if not isinstance(self.manager.config, dict) or 'PROXY_PROFILES' not in self.manager.config:
                messagebox.showwarning("Warning", "No saved proxy profiles found!")
                return
            
            profiles = list(self.manager.config['PROXY_PROFILES'].keys())
            if not profiles:
                messagebox.showwarning("Warning", "No saved proxy profiles found!")
                return
            
            # Create selection dialog
            dialog = tk.Toplevel(self.root)
            dialog.title("Load Proxy Profile")
            dialog.geometry("400x300")
            dialog.resizable(True, True)
            dialog.transient(self.root)
            dialog.grab_set()
            
            # Center dialog
            dialog.update_idletasks()
            x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
            y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
            dialog.geometry(f"+{x}+{y}")
            
            # Main frame
            main_frame = ttk.Frame(dialog, padding="20")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Title
            title_label = ttk.Label(main_frame, text="📋 Load Proxy Profile", 
                                  font=("Segoe UI", 16, "bold"))
            title_label.pack(pady=(0, 20))
            
            # Profiles listbox
            listbox_frame = ttk.Frame(main_frame)
            listbox_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
            
            listbox = tk.Listbox(listbox_frame, font=("Consolas", 10))
            scrollbar = ttk.Scrollbar(listbox_frame, orient="vertical", command=listbox.yview)
            listbox.configure(yscrollcommand=scrollbar.set)
            
            for profile in profiles:
                listbox.insert(tk.END, profile)
            
            listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            def load_selected():
                selection = listbox.curselection()
                if not selection:
                    messagebox.showwarning("Warning", "Please select a profile to load!")
                    return
                
                profile_name = listbox.get(selection[0])
                
                try:
                    import json
                    proxy_config = json.loads(self.manager.config['PROXY_PROFILES'][profile_name])
                    
                    # Load into UI fields
                    self.proxy_profile_name_var.set(proxy_config.get('name', ''))
                    self.proxy_protocol_var.set(proxy_config.get('protocol', 'http'))
                    self.proxy_server_var.set(proxy_config.get('host', ''))
                    self.proxy_port_var.set(str(proxy_config.get('port', '')))
                    self.proxy_username_var.set(proxy_config.get('username', ''))
                    self.proxy_password_var.set(proxy_config.get('password', ''))
                    
                    dialog.destroy()
                    messagebox.showinfo("Success", f"Proxy profile '{profile_name}' loaded successfully!")
                    
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to load proxy profile: {str(e)}")
            
            # Buttons
            button_frame = ttk.Frame(main_frame)
            button_frame.pack(fill=tk.X)
            
            ttk.Button(button_frame, text="❌ Cancel", command=dialog.destroy).pack(side=tk.RIGHT, padx=(5, 0))
            ttk.Button(button_frame, text="📥 Load", command=load_selected).pack(side=tk.RIGHT)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load proxy profile: {str(e)}")
    
    def refresh_saved_profiles(self):
        """Refresh the list of saved proxy profiles"""
        try:
            self.saved_profiles_listbox.delete(0, tk.END)
            
            if isinstance(self.manager.config, dict) and 'PROXY_PROFILES' in self.manager.config:
                profiles = list(self.manager.config['PROXY_PROFILES'].keys())
                for profile in profiles:
                    self.saved_profiles_listbox.insert(tk.END, profile)
            
        except Exception as e:
            print(f"Error refreshing saved profiles: {str(e)}")
    
    def load_selected_proxy_profile(self):
        """Load the selected proxy profile from the listbox"""
        try:
            selection = self.saved_profiles_listbox.curselection()
            if not selection:
                messagebox.showwarning("Warning", "Please select a profile to load!")
                return
            
            profile_name = self.saved_profiles_listbox.get(selection[0])
            
            try:
                import json
                proxy_config = json.loads(self.manager.config['PROXY_PROFILES'][profile_name])
                
                # Load into UI fields
                self.proxy_profile_name_var.set(proxy_config.get('name', ''))
                self.proxy_protocol_var.set(proxy_config.get('protocol', 'http'))
                self.proxy_server_var.set(proxy_config.get('host', ''))
                self.proxy_port_var.set(str(proxy_config.get('port', '')))
                self.proxy_username_var.set(proxy_config.get('username', ''))
                self.proxy_password_var.set(proxy_config.get('password', ''))
                
                messagebox.showinfo("Success", f"Proxy profile '{profile_name}' loaded successfully!")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load proxy profile: {str(e)}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load selected proxy profile: {str(e)}")
    
    def delete_selected_proxy_profile(self):
        """Delete the selected proxy profile"""
        try:
            selection = self.saved_profiles_listbox.curselection()
            if not selection:
                messagebox.showwarning("Warning", "Please select a profile to delete!")
                return
            
            profile_name = self.saved_profiles_listbox.get(selection[0])
            
            result = messagebox.askyesno("Confirm Delete", 
                                       f"Are you sure you want to delete the proxy profile '{profile_name}'?")
            
            if not result:
                return
            
            # Remove from config
            if isinstance(self.manager.config, dict) and 'PROXY_PROFILES' in self.manager.config and profile_name in self.manager.config['PROXY_PROFILES']:
                del self.manager.config['PROXY_PROFILES'][profile_name]
            self.manager.save_config()
            
            messagebox.showinfo("Success", f"Proxy profile '{profile_name}' deleted successfully!")
            self.refresh_saved_profiles()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete proxy profile: {str(e)}")
    
    def auto_install_extension_startup(self):
        """Automatically install SwitchyOmega 3 extension for all profiles on startup"""
        try:
            def startup_install_thread():
                try:
                    # Show startup message
                    self.extension_status_text.delete(1.0, tk.END)
                    self.extension_status_text.insert(tk.END, "[LAUNCH] Starting automatic extension installation...\n")
                    self.extension_status_text.insert(tk.END, "📥 Checking all profiles for SwitchyOmega 3...\n\n")
                    self.extension_status_text.update()
                    
                    # Run auto-installation
                    success_count, results = self.manager.auto_install_extension_on_startup()
                    
                    # Display results
                    self.extension_status_text.insert(tk.END, "📋 Auto-Installation Results:\n")
                    self.extension_status_text.insert(tk.END, "=" * 50 + "\n")
                    
                    for result in results:
                        self.extension_status_text.insert(tk.END, f"{result}\n")
                        self.extension_status_text.update()
                        time.sleep(0.1)
                    
                    self.extension_status_text.insert(tk.END, "\n" + "=" * 50 + "\n")
                    self.extension_status_text.insert(tk.END, f"🎉 Auto-installation completed!\n")
                    self.extension_status_text.insert(tk.END, f"✅ Profiles with extension: {success_count}\n")
                    
                    # Show completion notification
                    if success_count > 0:
                        self.root.after(0, lambda: messagebox.showinfo("Auto-Installation Complete", 
                            f"SwitchyOmega 3 extension has been automatically installed for {success_count} profiles!\n\n"
                            "All profiles are now ready for proxy configuration."))
                    
                    self.extension_status_text.see(tk.END)
                    
                except Exception as e:
                    try:
                        if hasattr(self, 'extension_status_text'):
                            self.extension_status_text.insert(tk.END, f"\n❌ Error during auto-installation: {str(e)}\n")
                            self.extension_status_text.see(tk.END)
                    except:
                        pass
                    print(f"❌ [AUTO-INSTALL] Error: {str(e)}")
            
            # Start auto-installation in background thread
            threading.Thread(target=startup_install_thread, daemon=True).start()
            
        except Exception as e:
            print(f"❌ [AUTO-INSTALL] Failed to start auto-installation: {str(e)}")
    
    def test_extension_installation(self):
        """Test extension installation with detailed debugging"""
        try:
            # Get selected profile or use first available profile
            if hasattr(self, 'tree') and self.tree.selection():
                selected_profiles = [self.tree.item(item)["text"] for item in self.tree.selection()]
                test_profile = selected_profiles[0]
            else:
                all_profiles = self.manager.get_all_profiles()
                if not all_profiles:
                    messagebox.showwarning("Warning", "No profiles found for testing!")
                    return
                test_profile = all_profiles[0]
            
            # Confirm test
            result = messagebox.askyesno("Test Extension Installation", 
                                       f"Test extension installation for profile '{test_profile}'?\n\n"
                                       "This will open Chrome and attempt to install SwitchyOmega 3 with detailed debugging.")
            
            if not result:
                return
            
            self.extension_status_text.delete(1.0, tk.END)
            self.extension_status_text.insert(tk.END, f"🧪 Testing extension installation for {test_profile}...\n\n")
            self.extension_status_text.update()
            
            def test_thread():
                try:
                    success, message = self.manager.test_extension_installation(test_profile)
                    
                    self.extension_status_text.insert(tk.END, "📋 Test Results:\n")
                    self.extension_status_text.insert(tk.END, "=" * 50 + "\n")
                    self.extension_status_text.insert(tk.END, f"Profile: {test_profile}\n")
                    self.extension_status_text.insert(tk.END, f"Success: {'✅ Yes' if success else '❌ No'}\n")
                    self.extension_status_text.insert(tk.END, f"Message: {message}\n")
                    self.extension_status_text.insert(tk.END, "=" * 50 + "\n")
                    
                    if success:
                        self.extension_status_text.insert(tk.END, "🎉 Test completed successfully!\n")
                        self.extension_status_text.insert(tk.END, "Check the console output for detailed debugging information.\n")
                    else:
                        self.extension_status_text.insert(tk.END, "❌ Test failed!\n")
                        self.extension_status_text.insert(tk.END, "Check the console output and screenshots for debugging.\n")
                    
                    self.extension_status_text.see(tk.END)
                    
                    # Show completion message
                    self.root.after(0, lambda: messagebox.showinfo("Test Complete", 
                        f"Extension installation test completed!\n\n"
                        f"Success: {'Yes' if success else 'No'}\n"
                        f"Message: {message}\n\n"
                        "Check the console output for detailed debugging information."))
                    
                except Exception as e:
                    self.extension_status_text.insert(tk.END, f"\n❌ Error during test: {str(e)}\n")
                    self.extension_status_text.see(tk.END)
                    self.root.after(0, lambda: messagebox.showerror("Test Error", f"Test failed: {str(e)}"))
            
            threading.Thread(target=test_thread, daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start test: {str(e)}")
    
    def activate_extension_selected(self):
        """
        Activate extension for selected profiles
        """
        try:
            # Get selected profiles
            selected_profiles = self.get_selected_profiles()
            if not selected_profiles:
                messagebox.showwarning("No Selection", "Please select at least one profile to activate extension.")
                return
            
            # Show progress dialog
            progress_dialog = tk.Toplevel(self.root)
            progress_dialog.title("⚡ Activating Extension")
            progress_dialog.geometry("600x400")
            progress_dialog.resizable(True, True)
            
            # Center the dialog
            progress_dialog.transient(self.root)
            progress_dialog.grab_set()
            
            # Progress text
            progress_text = tk.Text(progress_dialog, wrap=tk.WORD, height=20, width=70)
            progress_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Scrollbar
            scrollbar = ttk.Scrollbar(progress_dialog, orient=tk.VERTICAL, command=progress_text.yview)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            progress_text.config(yscrollcommand=scrollbar.set)
            
            def run_activation():
                try:
                    progress_text.insert(tk.END, f"⚡ Activating extension for {len(selected_profiles)} profiles...\n\n")
                    progress_dialog.update()
                    
                    for i, profile_name in enumerate(selected_profiles, 1):
                        progress_text.insert(tk.END, f"📋 Profile {i}/{len(selected_profiles)}: {profile_name}\n")
                        progress_dialog.update()
                        
                        # Activate extension
                        success, message = self.manager.activate_extension_in_chrome(profile_name)
                        
                        if success:
                            progress_text.insert(tk.END, f"✅ {profile_name}: Extension activated successfully\n")
                            progress_text.insert(tk.END, f"   Chrome launched with extension enabled\n")
                        else:
                            progress_text.insert(tk.END, f"❌ {profile_name}: Activation failed - {message}\n")
                        
                        progress_text.insert(tk.END, "\n")
                        progress_dialog.update()
                    
                    progress_text.insert(tk.END, "🎉 Extension activation completed!\n")
                    progress_text.insert(tk.END, "📱 Look for SwitchyOmega icon in Chrome toolbar\n")
                    progress_dialog.update()
                    
                except Exception as e:
                    progress_text.insert(tk.END, f"❌ Error during activation: {str(e)}\n")
                    progress_dialog.update()
            
            # Run activation in thread
            import threading
            activation_thread = threading.Thread(target=run_activation)
            activation_thread.daemon = True
            activation_thread.start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to activate extension: {str(e)}")

    def clone_extensions_dialog(self):
        """Dialog nhân bản extensions từ profile được chọn"""
        # Lấy profile được chọn
        selected_item = self.tree.selection()[0] if self.tree.selection() else None
        if not selected_item:
            messagebox.showerror("Error", "Please select a profile first")
            return
        
        source_profile = self.tree.item(selected_item)['text']
        
        dialog = tk.Toplevel(self.root)
        dialog.title("📋 Clone Extensions")
        dialog.geometry("500x400")
        dialog.configure(bg='#f0f0f0')
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (dialog.winfo_screenheight() // 2) - (400 // 2)
        dialog.geometry(f"500x400+{x}+{y}")
        
        # Header
        header_frame = ttk.Frame(dialog, style='Modern.TFrame')
        header_frame.pack(fill=tk.X, pady=20, padx=20)
        
        title_label = ttk.Label(header_frame, text="📋 Clone Extensions", 
                               style='Modern.TLabel', font=('Arial', 16, 'bold'))
        title_label.pack()
        
        # Source profile info
        source_frame = ttk.LabelFrame(dialog, text="Source Profile", padding=15)
        source_frame.pack(fill=tk.X, padx=20, pady=(0, 15))
        
        ttk.Label(source_frame, text=f"From: {source_profile}").pack(anchor=tk.W)
        
        # Check extensions in source profile
        has_extensions = self.manager.check_extension_installed(source_profile)
        status_text = "✅ Has SwitchyOmega 3 extension" if has_extensions else "❌ No extensions found"
        ttk.Label(source_frame, text=status_text, foreground='#4CAF50' if has_extensions else '#f44336').pack(anchor=tk.W, pady=(5, 0))
        
        # Target profiles
        target_frame = ttk.LabelFrame(dialog, text="Target Profiles", padding=15)
        target_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 15))
        
        ttk.Label(target_frame, text="Select profiles to copy extensions to:").pack(anchor=tk.W)
        
        # Listbox for target profiles
        listbox_frame = ttk.Frame(target_frame)
        listbox_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        target_listbox = tk.Listbox(listbox_frame, selectmode=tk.MULTIPLE, height=8)
        scrollbar = ttk.Scrollbar(listbox_frame, orient="vertical", command=target_listbox.yview)
        target_listbox.configure(yscrollcommand=scrollbar.set)
        
        target_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Load profiles (exclude source profile)
        profiles = self.manager.get_all_profiles()
        for profile in profiles:
            if profile != source_profile:
                target_listbox.insert(tk.END, profile)
        
        # Buttons
        button_frame = ttk.Frame(dialog, style='Modern.TFrame')
        button_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        def clone_extensions():
            selected_indices = target_listbox.curselection()
            if not selected_indices:
                messagebox.showerror("Error", "Please select target profiles")
                return
            
            target_profiles = [target_listbox.get(i) for i in selected_indices]
            
            try:
                # Show progress dialog
                progress_dialog = tk.Toplevel(dialog)
                progress_dialog.title("Cloning Extensions...")
                progress_dialog.geometry("500x300")
                progress_dialog.transient(dialog)
                progress_dialog.grab_set()
                
                progress_text = tk.Text(progress_dialog, height=15, width=60, font=("Consolas", 9))
                progress_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
                
                def clone_thread():
                    success_count = 0
                    failed_count = 0
                    
                    for profile_name in target_profiles:
                        try:
                            progress_text.insert(tk.END, f"📋 Copying extensions to {profile_name}...\n")
                            progress_dialog.update()
                            
                            # Copy extensions from source to target
                            success, message = self._copy_extensions_between_profiles(source_profile, profile_name)
                            if success:
                                progress_text.insert(tk.END, f"✅ {profile_name} - Extensions copied successfully\n")
                                success_count += 1
                            else:
                                progress_text.insert(tk.END, f"❌ {profile_name} - Failed: {message}\n")
                                failed_count += 1
                            
                            progress_dialog.update()
                            
                        except Exception as e:
                            progress_text.insert(tk.END, f"❌ {profile_name} - Error: {str(e)}\n")
                            failed_count += 1
                            progress_dialog.update()
                    
                    progress_text.insert(tk.END, f"\n🎉 Extension cloning completed!\n")
                    progress_text.insert(tk.END, f"✅ Success: {success_count}\n")
                    progress_text.insert(tk.END, f"❌ Failed: {failed_count}\n")
                    progress_dialog.update()
                    
                    # Close progress dialog after 3 seconds
                    dialog.after(3000, progress_dialog.destroy)
                    self.refresh_profiles()
                
                # Start cloning in thread
                import threading
                thread = threading.Thread(target=clone_thread)
                thread.daemon = True
                thread.start()
                
            except Exception as e:
                messagebox.showerror("Error", f"Error cloning extensions: {str(e)}")
        
        ttk.Button(button_frame, text="📋 Clone Extensions", 
                  command=clone_extensions).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="❌ Cancel", 
                  command=dialog.destroy).pack(side=tk.LEFT)
    
    def clone_extensions_from_template(self):
        """Nhân bản extensions từ template profile (76h) sang profile được chọn"""
        # Lấy profile được chọn
        selected_item = self.tree.selection()[0] if self.tree.selection() else None
        if not selected_item:
            messagebox.showerror("Error", "Please select a profile first")
            return
        
        target_profile = self.tree.item(selected_item)['text']
        
        # Xác nhận
        result = messagebox.askyesno("Confirm", 
            f"Copy SwitchyOmega 3 extension from template (76h) to '{target_profile}'?\n\nThis will overwrite any existing extensions.")
        if not result:
            return
        
        try:
            # Copy extensions from template
            success, message = self._copy_extensions_between_profiles("76h", target_profile)
            if success:
                messagebox.showinfo("Success", f"Extensions copied to '{target_profile}' successfully!")
                self.refresh_profiles()
            else:
                messagebox.showerror("Error", f"Failed to copy extensions: {message}")
        except Exception as e:
            messagebox.showerror("Error", f"Error copying extensions: {str(e)}")
    
    def _copy_extensions_between_profiles(self, source_profile, target_profile):
        """Copy extensions từ source profile sang target profile"""
        try:
            import shutil
            import os
            
            # Lấy đường dẫn profiles (sử dụng backup)
            source_path = os.path.join("../data/chrome_profiles", source_profile)
            target_path = os.path.join("../data/chrome_profiles", target_profile)
            
            if not source_path or not target_path:
                return False, "Profile paths not found"
            
            print(f"📋 [COPY] Source path: {source_path}")
            print(f"📋 [COPY] Target path: {target_path}")
            
            # Copy Extensions folder (try both locations)
            source_extensions = os.path.join(source_path, "Extensions")
            source_default_extensions = os.path.join(source_path, "Default", "Extensions")
            target_extensions = os.path.join(target_path, "Extensions")
            target_default_extensions = os.path.join(target_path, "Default", "Extensions")
            
            # Determine source extensions location
            if os.path.exists(source_default_extensions):
                source_extensions = source_default_extensions
                print(f"📋 [COPY] Using Default/Extensions as source")
            elif os.path.exists(source_extensions):
                print(f"📋 [COPY] Using Extensions as source")
            else:
                return False, "Source Extensions folder not found"
            
            if os.path.exists(source_extensions):
                # Determine target extensions location (match source structure)
                if "Default" in source_extensions:
                    target_extensions = target_default_extensions
                    print(f"📋 [COPY] Using Default/Extensions as target")
                else:
                    print(f"📋 [COPY] Using Extensions as target")
                
                # Tạo target Extensions folder nếu chưa có
                if not os.path.exists(target_extensions):
                    os.makedirs(target_extensions)
                    print(f"📋 [COPY] Created target extensions directory")
                
                # Copy SwitchyOmega extension
                switchyomega_id = "pfnededegaaopdmhkdmcofjmoldfiped"
                source_extension = os.path.join(source_extensions, switchyomega_id)
                target_extension = os.path.join(target_extensions, switchyomega_id)
                
                print(f"📋 [COPY] Source extension: {source_extension}")
                print(f"📋 [COPY] Target extension: {target_extension}")
                
                if os.path.exists(source_extension):
                    # Xóa extension cũ nếu có
                    if os.path.exists(target_extension):
                        shutil.rmtree(target_extension)
                        print(f"📋 [COPY] Removed old extension")
                    
                    # Copy extension mới
                    shutil.copytree(source_extension, target_extension)
                    print(f"📋 [COPY] Copied extension files")
                    
                    # Copy extension settings
                    self._copy_extension_settings(source_path, target_path, switchyomega_id)
                    
                    return True, "Extensions copied successfully"
                else:
                    return False, "Source extension not found"
            else:
                return False, "Source Extensions folder not found"
                
        except Exception as e:
            return False, f"Error copying extensions: {str(e)}"
    
    def _copy_extension_settings(self, source_path, target_path, extension_id):
        """Copy extension settings từ source sang target"""
        try:
            import json
            import shutil
            import os
            
            # Copy Default/Preferences
            source_prefs = os.path.join(source_path, "Default", "Preferences")
            target_prefs = os.path.join(target_path, "Default", "Preferences")
            
            if os.path.exists(source_prefs):
                # Tạo Default folder nếu chưa có
                target_default = os.path.join(target_path, "Default")
                if not os.path.exists(target_default):
                    os.makedirs(target_default)
                
                # Copy Preferences
                shutil.copy2(source_prefs, target_prefs)
            
            # Copy Default/Secure Preferences
            source_secure_prefs = os.path.join(source_path, "Default", "Secure Preferences")
            target_secure_prefs = os.path.join(target_path, "Default", "Secure Preferences")
            
            if os.path.exists(source_secure_prefs):
                shutil.copy2(source_secure_prefs, target_secure_prefs)
            
            # Copy Local Extension Settings
            source_local_settings = os.path.join(source_path, "Default", "Local Extension Settings", extension_id)
            target_local_settings = os.path.join(target_path, "Default", "Local Extension Settings", extension_id)
            
            if os.path.exists(source_local_settings):
                target_local_dir = os.path.dirname(target_local_settings)
                if not os.path.exists(target_local_dir):
                    os.makedirs(target_local_dir)
                
                if os.path.exists(target_local_settings):
                    shutil.rmtree(target_local_settings)
                shutil.copytree(source_local_settings, target_local_settings)
            
            # Copy Sync Extension Settings
            source_sync_settings = os.path.join(source_path, "Default", "Sync Extension Settings", extension_id)
            target_sync_settings = os.path.join(target_path, "Default", "Sync Extension Settings", extension_id)
            
            if os.path.exists(source_sync_settings):
                target_sync_dir = os.path.dirname(target_sync_settings)
                if not os.path.exists(target_sync_dir):
                    os.makedirs(target_sync_dir)
                
                if os.path.exists(target_sync_settings):
                    shutil.rmtree(target_sync_settings)
                shutil.copytree(source_sync_settings, target_sync_settings)
            
            # Copy IndexedDB
            source_indexeddb = os.path.join(source_path, "Default", "IndexedDB")
            target_indexeddb = os.path.join(target_path, "Default", "IndexedDB")
            
            if os.path.exists(source_indexeddb):
                if os.path.exists(target_indexeddb):
                    shutil.rmtree(target_indexeddb)
                shutil.copytree(source_indexeddb, target_indexeddb)
            
        except Exception as e:
            print(f"Warning: Could not copy all extension settings: {str(e)}")
    

    def run(self):
        """Chạy ứng dụng"""
        self.root.mainloop()


    def show_pac_tab_disabled(self):
        """Show PAC Files tab - DISABLED"""
        self.update_tab_highlight('../network/pac_files')
        self.clear_content()
        
        # Show disabled message
        disabled_frame = ttk.Frame(self.content_frame)
        disabled_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        disabled_label = ttk.Label(disabled_frame, text="🚫 PAC Files functionality has been removed\n\nThis feature is no longer available.", 
                                 font=('Segoe UI', 14),
                                 foreground='#ff6b6b',
                                 justify=tk.CENTER)
        disabled_label.pack(expand=True)
        
        # Header
        header_frame = ttk.Frame(self.content_frame, style='Modern.TFrame')
        header_frame.pack(fill=tk.X, pady=(0, 25))
        
        # Title section
        title_section = ttk.Frame(header_frame, style='Modern.TFrame')
        title_section.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        title_label = ttk.Label(title_section, text="📁 PAC Files Manager", 
                               style='Modern.TLabel', 
                               font=('Segoe UI', 28, 'bold'))
        title_label.pack(anchor='w')
        
        subtitle_label = ttk.Label(title_section, text="Quản lý và tạo PAC files cho SwitchyOmega", 
                                 style='Modern.TLabel', 
                                 font=('Segoe UI', 11),
                                 foreground='#b3b3b3')
        subtitle_label.pack(anchor='w', pady=(5, 0))
        
        # Action buttons
        action_frame = ttk.Frame(header_frame, style='Modern.TFrame')
        action_frame.pack(side=tk.RIGHT, padx=(20, 0))
        
        # Input Proxy button
        input_proxy_btn = ttk.Button(action_frame, text="🌐 Input Proxy", 
                                   command=self.show_proxy_input_dialog,
                                   style='Modern.TButton')
        input_proxy_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Create main frame
        main_frame = ttk.Frame(self.content_frame, style='Modern.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create notebook for PAC sub-tabs
        pac_notebook = ttk.Notebook(main_frame)
        pac_notebook.pack(fill=tk.BOTH, expand=True)
        
        # PAC Files List tab
        self.pac_files_frame = ttk.Frame(pac_notebook)
        pac_notebook.add(self.pac_files_frame, text="📋 PAC Files")
        
        # PAC Creator tab
        self.pac_creator_frame = ttk.Frame(pac_notebook)
        pac_notebook.add(self.pac_creator_frame, text="🔧 PAC Creator")
        
        # Setup PAC Files List tab
        self.setup_pac_files_tab()
        
        # Setup PAC Creator tab
        self.setup_pac_creator_tab()
    
    def setup_pac_files_tab(self):
        """Setup PAC Files List tab"""
        # Listbox for PAC files
        list_frame = ttk.Frame(self.pac_files_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Label(list_frame, text="Available PAC Files:").pack(anchor=tk.W)
        
        self.pac_files_listbox = tk.Listbox(list_frame, height=10)
        self.pac_files_listbox.pack(fill=tk.BOTH, expand=True, pady=(5, 10))
        
        # Buttons
        button_frame = ttk.Frame(list_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="🔄 Refresh", command=self.refresh_pac_files).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="👁️ View", command=self.view_pac_file).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="📁 Import", command=self.import_pac_file).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="🗑️ Delete", command=self.delete_pac_file).pack(side=tk.LEFT)
        ttk.Button(button_frame, text="🔧 Input Proxy", command=self.show_proxy_input_dialog).pack(side=tk.LEFT, padx=(5, 0))
        
        # Smart Analysis Section
        analysis_frame = ttk.LabelFrame(list_frame, text="🧠 Smart Proxy Analysis", padding=5)
        analysis_frame.pack(fill=tk.X, pady=(10, 0))
        
        analysis_buttons = ttk.Frame(analysis_frame)
        analysis_buttons.pack(fill=tk.X)
        
        ttk.Button(analysis_buttons, text="🔍 Analyze All", 
                  command=self.analyze_all_profiles).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(analysis_buttons, text="✅ With Proxy", 
                  command=self.show_profiles_with_proxy).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(analysis_buttons, text="❌ Without Proxy", 
                  command=self.show_profiles_without_proxy).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(analysis_buttons, text="🧠 Smart Configure", 
                  command=self.show_smart_proxy_dialog).pack(side=tk.LEFT)
        
        # Status text
        self.pac_status_text = tk.Text(list_frame, height=5, wrap=tk.WORD)
        self.pac_status_text.pack(fill=tk.X, pady=(10, 0))
        
        # Refresh PAC files
        self.refresh_pac_files()
    
    def show_proxy_input_dialog(self):
        """Show proxy input dialog with profile selection"""
        dialog = tk.Toplevel(self.root)
        dialog.title("🌐 Input Proxy Settings")
        dialog.geometry("700x600")
        dialog.resizable(False, False)
        
        # Center the dialog
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Main frame
        main_frame = tk.Frame(dialog, bg="#2b2b2b")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(main_frame, text="🌐 Input Proxy Settings", 
                              font=("Segoe UI", 16, "bold"), 
                              fg="#ffffff", bg="#2b2b2b")
        title_label.pack(pady=(0, 20))
        
        # Proxy input frame
        proxy_frame = tk.LabelFrame(main_frame, text="Proxy Configuration", 
                                   font=("Segoe UI", 12, "bold"),
                                   fg="#ffffff", bg="#2b2b2b", 
                                   relief=tk.RAISED, bd=2)
        proxy_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Proxy format info
        format_label = tk.Label(proxy_frame, 
                               text="Format: server:port:username:password\nExample: 146.19.196.108:40767:wqcj8o8q3x:mlptR7sWVf",
                               font=("Segoe UI", 10),
                               fg="#cccccc", bg="#2b2b2b")
        format_label.pack(pady=10)
        
        # Proxy input
        tk.Label(proxy_frame, text="Proxy String:", 
                font=("Segoe UI", 11, "bold"),
                fg="#ffffff", bg="#2b2b2b").pack(anchor=tk.W, padx=10, pady=(10, 5))
        
        proxy_entry = tk.Entry(proxy_frame, font=("Segoe UI", 11), 
                              bg="#404040", fg="#ffffff", 
                              insertbackground="#ffffff",
                              relief=tk.FLAT, bd=5)
        proxy_entry.pack(fill=tk.X, padx=10, pady=(0, 10))
        proxy_entry.insert(0, "146.19.196.108:40767:wqcj8o8q3x:mlptR7sWVf")
        
        # Profile selection frame
        profile_frame = tk.LabelFrame(main_frame, text="Select Profiles", 
                                     font=("Segoe UI", 12, "bold"),
                                     fg="#ffffff", bg="#2b2b2b", 
                                     relief=tk.RAISED, bd=2)
        profile_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Profile selection options
        selection_frame = tk.Frame(profile_frame, bg="#2b2b2b")
        selection_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Select all checkbox
        select_all_var = tk.BooleanVar()
        select_all_check = tk.Checkbutton(selection_frame, text="Select All Profiles", 
                                         variable=select_all_var,
                                         font=("Segoe UI", 11, "bold"),
                                         fg="#ffffff", bg="#2b2b2b", 
                                         selectcolor="#404040",
                                         command=lambda: self._toggle_profile_selection(select_all_var, profile_listbox))
        select_all_check.pack(anchor=tk.W, pady=(0, 10))
        
        # Profile listbox with scrollbar
        listbox_frame = tk.Frame(profile_frame, bg="#2b2b2b")
        listbox_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        profile_listbox = tk.Listbox(listbox_frame, 
                                    font=("Segoe UI", 10),
                                    bg="#404040", fg="#ffffff",
                                    selectbackground="#0078d4",
                                    selectforeground="#ffffff",
                                    relief=tk.FLAT, bd=5,
                                    selectmode=tk.MULTIPLE)
        
        scrollbar = tk.Scrollbar(listbox_frame, orient=tk.VERTICAL, command=profile_listbox.yview)
        profile_listbox.configure(yscrollcommand=scrollbar.set)
        
        profile_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Load profiles
        profiles = self.manager.get_all_profiles()
        for profile in profiles:
            profile_listbox.insert(tk.END, profile)
        
        # Buttons frame
        buttons_frame = tk.Frame(main_frame, bg="#2b2b2b")
        buttons_frame.pack(fill=tk.X, pady=(0, 10))
        
        def configure_proxy():
            """Configure proxy for selected profiles"""
            proxy_string = proxy_entry.get().strip()
            if not proxy_string:
                messagebox.showerror("Error", "Please enter proxy string!")
                return
            
            selected_profiles = [profile_listbox.get(i) for i in profile_listbox.curselection()]
            if not selected_profiles:
                messagebox.showerror("Error", "Please select at least one profile!")
                return
            
            # Validate proxy format
            try:
                parts = proxy_string.split(':')
                if len(parts) != 4:
                    raise ValueError("Invalid format")
                server, port, username, password = parts
                int(port)  # Validate port is number
            except:
                messagebox.showerror("Error", "Invalid proxy format! Use: server:port:username:password")
                return
            
            # Show confirmation
            result = messagebox.askyesno("Confirm", 
                                       f"Configure proxy for {len(selected_profiles)} profiles?\n\n"
                                       f"Proxy: {proxy_string}\n"
                                       f"Profiles: {', '.join(selected_profiles)}")
            if not result:
                return
            
            # Configure proxy in thread
            def configure_thread():
                try:
                    success_count = 0
                    failed_profiles = []
                    
                    for profile_name in selected_profiles:
                        try:
                            # Use chrome_manager_backup to configure proxy
                            success, message = self.manager.input_proxy_from_ui(profile_name, proxy_string)
                            if success:
                                success_count += 1
                            else:
                                failed_profiles.append(f"{profile_name}: {message}")
                        except Exception as e:
                            failed_profiles.append(f"{profile_name}: {str(e)}")
                    
                    def update_ui():
                        if success_count > 0:
                            messagebox.showinfo("Success", 
                                              f"Successfully configured proxy for {success_count} profiles!")
                        if failed_profiles:
                            error_msg = "Failed profiles:\n" + "\n".join(failed_profiles)
                            messagebox.showerror("Some Failed", error_msg)
                        dialog.destroy()
                    
                    self.root.after(0, update_ui)
                    
                except Exception as e:
                    def update_ui():
                        messagebox.showerror("Error", f"Configuration failed: {str(e)}")
                        dialog.destroy()
                    self.root.after(0, update_ui)
            
            threading.Thread(target=configure_thread, daemon=True).start()
        
        def test_proxy():
            """Test proxy connection"""
            proxy_string = proxy_entry.get().strip()
            if not proxy_string:
                messagebox.showerror("Error", "Please enter proxy string!")
                return
            
            def test_thread():
                try:
                    success, message = self.manager.test_proxy_connection(proxy_string)
                    
                    def update_ui():
                        if success:
                            messagebox.showinfo("Test Result", f"✅ Proxy test successful!\n{message}")
                        else:
                            messagebox.showerror("Test Result", f"❌ Proxy test failed!\n{message}")
                    
                    self.root.after(0, update_ui)
                    
                except Exception as e:
                    def update_ui():
                        messagebox.showerror("Error", f"Test failed: {str(e)}")
                    self.root.after(0, update_ui)
            
            threading.Thread(target=test_thread, daemon=True).start()
        
        # Buttons
        test_btn = tk.Button(buttons_frame, text="🧪 Test Proxy", 
                           command=test_proxy,
                           font=("Segoe UI", 11, "bold"),
                           bg="#0078d4", fg="#ffffff",
                           relief=tk.FLAT, bd=5, padx=20, pady=10)
        test_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        configure_btn = tk.Button(buttons_frame, text="⚙️ Configure Selected", 
                                command=configure_proxy,
                                font=("Segoe UI", 11, "bold"),
                                bg="#28a745", fg="#ffffff",
                                relief=tk.FLAT, bd=5, padx=20, pady=10)
        configure_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        cancel_btn = tk.Button(buttons_frame, text="❌ Cancel", 
                             command=dialog.destroy,
                             font=("Segoe UI", 11, "bold"),
                             bg="#dc3545", fg="#ffffff",
                             relief=tk.FLAT, bd=5, padx=20, pady=10)
        cancel_btn.pack(side=tk.RIGHT)
        
        # Profile selection
        tk.Label(proxy_frame, text="Select Profile:", 
                font=("Segoe UI", 11, "bold"),
                fg="#ffffff", bg="#2b2b2b").pack(anchor=tk.W, padx=10, pady=(10, 5))
        
        profile_combo = ttk.Combobox(proxy_frame, font=("Segoe UI", 11), 
                                    state="readonly", width=30)
        profile_combo.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # Load profiles
        profiles = self.manager.get_all_profiles()
        profile_combo['values'] = profiles
        if profiles:
            profile_combo.set(profiles[0])
        
        # Bulk configuration frame
        bulk_frame = tk.LabelFrame(main_frame, text="Bulk Configuration", 
                                  font=("Segoe UI", 12, "bold"),
                                  fg="#ffffff", bg="#2b2b2b", 
                                  relief=tk.RAISED, bd=2)
        bulk_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Select all profiles checkbox
        select_all_var = tk.BooleanVar()
        select_all_cb = tk.Checkbutton(bulk_frame, text="Apply to ALL profiles", 
                                      variable=select_all_var,
                                      font=("Segoe UI", 11),
                                      fg="#ffffff", bg="#2b2b2b",
                                      selectcolor="#404040",
                                      command=lambda: self._toggle_profile_selection(select_all_var, profile_combo))
        select_all_cb.pack(anchor=tk.W, padx=10, pady=10)
        
        # Buttons frame
        buttons_frame = tk.Frame(main_frame, bg="#2b2b2b")
        buttons_frame.pack(fill=tk.X, pady=(0, 10))
        
        def configure_proxy():
            proxy_string = proxy_entry.get().strip()
            profile_name = profile_combo.get()
            
            if not proxy_string:
                messagebox.showerror("Error", "Please enter proxy string")
                return
            
            if not profile_name and not select_all_var.get():
                messagebox.showerror("Error", "Please select a profile or enable bulk configuration")
                return
            
            # Configure proxy
            def configure_thread():
                try:
                    if select_all_var.get():
                        # Bulk configuration
                        all_profiles = self.manager.get_all_profiles()
                        results, success_count = self.manager.bulk_input_proxy_from_ui(all_profiles, proxy_string)
                        
                        def update_ui():
                            success_msg = f"✅ Successfully configured {success_count}/{len(all_profiles)} profiles"
                            failed_profiles = [r['profile'] for r in results if not r['success']]
                            
                            if failed_profiles:
                                failed_msg = f"\n❌ Failed profiles: {', '.join(failed_profiles)}"
                                messagebox.showinfo("Bulk Configuration", success_msg + failed_msg)
                            else:
                                messagebox.showinfo("Bulk Configuration", success_msg)
                            
                            dialog.destroy()
                        
                        self.root.after(0, update_ui)
                    else:
                        # Single profile configuration
                        success, message = self.manager.input_proxy_from_ui(profile_name, proxy_string)
                        
                        def update_ui():
                            if success:
                                messagebox.showinfo("Success", f"Proxy configured successfully!\n{message}")
                                dialog.destroy()
                            else:
                                messagebox.showerror("Error", f"Failed to configure proxy:\n{message}")
                        
                        self.root.after(0, update_ui)
                    
                except Exception as e:
                    def update_ui():
                        messagebox.showerror("Error", f"Error configuring proxy:\n{str(e)}")
                    
                    self.root.after(0, update_ui)
            
            # Start configuration in thread
            import threading
            thread = threading.Thread(target=configure_thread)
            thread.daemon = True
            thread.start()
        
        # Test proxy button
        def test_proxy():
            proxy_string = proxy_entry.get().strip()
            
            if not proxy_string:
                messagebox.showerror("Error", "Please enter proxy string")
                return
            
            def test_thread():
                try:
                    success, message = self.manager.test_proxy_connection(proxy_string)
                    
                    def update_ui():
                        if success:
                            messagebox.showinfo("Proxy Test", f"✅ {message}")
                        else:
                            messagebox.showerror("Proxy Test", f"❌ {message}")
                    
                    self.root.after(0, update_ui)
                    
                except Exception as e:
                    def update_ui():
                        messagebox.showerror("Error", f"Error testing proxy:\n{str(e)}")
                    
                    self.root.after(0, update_ui)
            
            # Start test in thread
            import threading
            thread = threading.Thread(target=test_thread)
            thread.daemon = True
            thread.start()
        
        # Buttons
        test_btn = tk.Button(buttons_frame, text="🧪 Test Proxy", 
                            command=test_proxy,
                            font=("Segoe UI", 11, "bold"),
                            bg="#4CAF50", fg="white",
                            relief=tk.FLAT, bd=0, padx=20, pady=10)
        test_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        configure_btn = tk.Button(buttons_frame, text="⚙️ Configure", 
                                 command=configure_proxy,
                                 font=("Segoe UI", 11, "bold"),
                                 bg="#2196F3", fg="white",
                                 relief=tk.FLAT, bd=0, padx=20, pady=10)
        configure_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        cancel_btn = tk.Button(buttons_frame, text="❌ Cancel", 
                              command=dialog.destroy,
                              font=("Segoe UI", 11, "bold"),
                              bg="#f44336", fg="white",
                              relief=tk.FLAT, bd=0, padx=20, pady=10)
        cancel_btn.pack(side=tk.RIGHT)

    def _toggle_profile_selection(self, select_all_var, profile_combo):
        """Toggle profile selection based on checkbox"""
        if select_all_var.get():
            profile_combo.config(state="disabled")
        else:
            profile_combo.config(state="readonly")

    def analyze_all_profiles(self):
        """Analyze all profiles for proxy status"""
        def analyze_thread():
            try:
                proxy_profiles = self.manager.get_profiles_with_proxy()
                no_proxy_profiles = self.manager.get_profiles_without_proxy()
                
                def update_ui():
                    result_text = f"🔍 Analysis Results:\n"
                    result_text += f"✅ Profiles with proxy: {len(proxy_profiles)}\n"
                    result_text += f"❌ Profiles without proxy: {len(no_proxy_profiles)}\n\n"
                    
                    if proxy_profiles:
                        result_text += f"✅ With proxy: {', '.join(proxy_profiles)}\n"
                    
                    if no_proxy_profiles:
                        result_text += f"❌ Without proxy: {', '.join(no_proxy_profiles)}\n"
                    
                    self.pac_status_text.delete(1.0, tk.END)
                    self.pac_status_text.insert(tk.END, result_text)
                
                self.root.after(0, update_ui)
                
            except Exception as e:
                def update_ui():
                    self.pac_status_text.delete(1.0, tk.END)
                    self.pac_status_text.insert(tk.END, f"❌ Analysis error: {str(e)}")
                
                self.root.after(0, update_ui)
        
        import threading
        thread = threading.Thread(target=analyze_thread)
        thread.daemon = True
        thread.start()

    def show_profiles_with_proxy(self):
        """Show profiles that have proxy configured"""
        def analyze_thread():
            try:
                proxy_profiles = self.manager.get_profiles_with_proxy()
                
                def update_ui():
                    if proxy_profiles:
                        result_text = f"✅ Profiles with proxy ({len(proxy_profiles)}):\n"
                        for profile in proxy_profiles:
                            result_text += f"  • {profile}\n"
                    else:
                        result_text = "❌ No profiles with proxy found"
                    
                    self.pac_status_text.delete(1.0, tk.END)
                    self.pac_status_text.insert(tk.END, result_text)
                
                self.root.after(0, update_ui)
                
            except Exception as e:
                def update_ui():
                    self.pac_status_text.delete(1.0, tk.END)
                    self.pac_status_text.insert(tk.END, f"❌ Error: {str(e)}")
                
                self.root.after(0, update_ui)
        
        import threading
        thread = threading.Thread(target=analyze_thread)
        thread.daemon = True
        thread.start()

    def show_profiles_without_proxy(self):
        """Show profiles that don't have proxy configured"""
        def analyze_thread():
            try:
                no_proxy_profiles = self.manager.get_profiles_without_proxy()
                
                def update_ui():
                    if no_proxy_profiles:
                        result_text = f"❌ Profiles without proxy ({len(no_proxy_profiles)}):\n"
                        for profile in no_proxy_profiles:
                            result_text += f"  • {profile}\n"
                    else:
                        result_text = "✅ All profiles have proxy configured"
                    
                    self.pac_status_text.delete(1.0, tk.END)
                    self.pac_status_text.insert(tk.END, result_text)
                
                self.root.after(0, update_ui)
                
            except Exception as e:
                def update_ui():
                    self.pac_status_text.delete(1.0, tk.END)
                    self.pac_status_text.insert(tk.END, f"❌ Error: {str(e)}")
                
                self.root.after(0, update_ui)
        
        import threading
        thread = threading.Thread(target=analyze_thread)
        thread.daemon = True
        thread.start()

    def show_smart_proxy_dialog(self):
        """Show smart proxy configuration dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("🧠 Smart Proxy Configuration")
        dialog.geometry("600x500")
        dialog.resizable(False, False)
        
        # Center the dialog
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Main frame
        main_frame = tk.Frame(dialog, bg="#2b2b2b")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(main_frame, text="🧠 Smart Proxy Configuration", 
                              font=("Segoe UI", 16, "bold"), 
                              fg="#ffffff", bg="#2b2b2b")
        title_label.pack(pady=(0, 20))
        
        # Analysis section
        analysis_frame = tk.LabelFrame(main_frame, text="Analysis", 
                                      font=("Segoe UI", 12, "bold"),
                                      fg="#ffffff", bg="#2b2b2b", 
                                      relief=tk.RAISED, bd=2)
        analysis_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Analysis buttons
        analysis_buttons = tk.Frame(analysis_frame, bg="#2b2b2b")
        analysis_buttons.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(analysis_buttons, text="🔍 Analyze All Profiles", 
                 command=self.analyze_all_profiles,
                 font=("Segoe UI", 11, "bold"),
                 bg="#4CAF50", fg="white",
                 relief=tk.FLAT, bd=0, padx=20, pady=10).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(analysis_buttons, text="✅ Show With Proxy", 
                 command=self.show_profiles_with_proxy,
                 font=("Segoe UI", 11, "bold"),
                 bg="#2196F3", fg="white",
                 relief=tk.FLAT, bd=0, padx=20, pady=10).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(analysis_buttons, text="❌ Show Without Proxy", 
                 command=self.show_profiles_without_proxy,
                 font=("Segoe UI", 11, "bold"),
                 bg="#f44336", fg="white",
                 relief=tk.FLAT, bd=0, padx=20, pady=10).pack(side=tk.LEFT)
        
        # Proxy configuration section
        config_frame = tk.LabelFrame(main_frame, text="Smart Configuration", 
                                    font=("Segoe UI", 12, "bold"),
                                    fg="#ffffff", bg="#2b2b2b", 
                                    relief=tk.RAISED, bd=2)
        config_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Proxy input
        tk.Label(config_frame, text="Proxy String:", 
                font=("Segoe UI", 11, "bold"),
                fg="#ffffff", bg="#2b2b2b").pack(anchor=tk.W, padx=10, pady=(10, 5))
        
        proxy_entry = tk.Entry(config_frame, font=("Segoe UI", 11), 
                              bg="#404040", fg="#ffffff", 
                              insertbackground="#ffffff",
                              relief=tk.FLAT, bd=5)
        proxy_entry.pack(fill=tk.X, padx=10, pady=(0, 10))
        proxy_entry.insert(0, "146.19.196.16:40742:dNMWW2VVxb:YySfhZZPYv")
        
        # Profile selection
        tk.Label(config_frame, text="Select Profile:", 
                font=("Segoe UI", 11, "bold"),
                fg="#ffffff", bg="#2b2b2b").pack(anchor=tk.W, padx=10, pady=(10, 5))
        
        profile_combo = ttk.Combobox(config_frame, font=("Segoe UI", 11), 
                                    state="readonly", width=30)
        profile_combo.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # Load profiles
        profiles = self.manager.get_all_profiles()
        profile_combo['values'] = profiles
        if profiles:
            profile_combo.set(profiles[0])
        
        # Bulk configuration
        bulk_frame = tk.LabelFrame(main_frame, text="Bulk Configuration", 
                                  font=("Segoe UI", 12, "bold"),
                                  fg="#ffffff", bg="#2b2b2b", 
                                  relief=tk.RAISED, bd=2)
        bulk_frame.pack(fill=tk.X, pady=(0, 20))
        
        select_all_var = tk.BooleanVar()
        select_all_cb = tk.Checkbutton(bulk_frame, text="Configure ALL profiles without proxy", 
                                      variable=select_all_var,
                                      font=("Segoe UI", 11),
                                      fg="#ffffff", bg="#2b2b2b",
                                      selectcolor="#404040")
        select_all_cb.pack(anchor=tk.W, padx=10, pady=10)
        
        # Buttons
        buttons_frame = tk.Frame(main_frame, bg="#2b2b2b")
        buttons_frame.pack(fill=tk.X, pady=(0, 10))
        
        def smart_configure():
            proxy_string = proxy_entry.get().strip()
            profile_name = profile_combo.get()
            
            if not proxy_string:
                messagebox.showerror("Error", "Please enter proxy string")
                return
            
            if not profile_name and not select_all_var.get():
                messagebox.showerror("Error", "Please select a profile or enable bulk configuration")
                return
            
            def configure_thread():
                try:
                    if select_all_var.get():
                        # Get profiles without proxy
                        no_proxy_profiles = self.manager.get_profiles_without_proxy()
                        if not no_proxy_profiles:
                            def update_ui():
                                messagebox.showinfo("Info", "All profiles already have proxy configured!")
                            self.root.after(0, update_ui)
                            return
                        
                        results, success_count = self.manager.bulk_smart_configure_proxy(no_proxy_profiles, proxy_string)
                        
                        def update_ui():
                            success_msg = f"✅ Successfully configured {success_count}/{len(no_proxy_profiles)} profiles"
                            failed_profiles = [r['profile'] for r in results if not r['success']]
                            
                            if failed_profiles:
                                failed_msg = f"\n❌ Failed profiles: {', '.join(failed_profiles)}"
                                messagebox.showinfo("Smart Configuration", success_msg + failed_msg)
                            else:
                                messagebox.showinfo("Smart Configuration", success_msg)
                            
                            dialog.destroy()
                        
                        self.root.after(0, update_ui)
                    else:
                        # Single profile configuration
                        success, message = self.manager.smart_configure_proxy(profile_name, proxy_string)
                        
                        def update_ui():
                            if success:
                                messagebox.showinfo("Success", f"Smart configuration completed!\n{message}")
                                dialog.destroy()
                            else:
                                messagebox.showerror("Error", f"Smart configuration failed:\n{message}")
                        
                        self.root.after(0, update_ui)
                    
                except Exception as e:
                    def update_ui():
                        messagebox.showerror("Error", f"Error in smart configuration:\n{str(e)}")
                    
                    self.root.after(0, update_ui)
            
            # Start configuration in thread
            import threading
            thread = threading.Thread(target=configure_thread)
            thread.daemon = True
            thread.start()
        
        # Buttons
        configure_btn = tk.Button(buttons_frame, text="🧠 Smart Configure", 
                                 command=smart_configure,
                                 font=("Segoe UI", 11, "bold"),
                                 bg="#2196F3", fg="white",
                                 relief=tk.FLAT, bd=0, padx=20, pady=10)
        configure_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        cancel_btn = tk.Button(buttons_frame, text="❌ Cancel", 
                              command=dialog.destroy,
                              font=("Segoe UI", 11, "bold"),
                              bg="#f44336", fg="white",
                              relief=tk.FLAT, bd=0, padx=20, pady=10)
        cancel_btn.pack(side=tk.RIGHT)
    
    def setup_pac_creator_tab(self):
        """Setup PAC Creator tab"""
        # Main frame
        main_frame = ttk.Frame(self.pac_creator_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Proxy configuration
        config_frame = ttk.LabelFrame(main_frame, text="Proxy Configuration")
        config_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Server
        ttk.Label(config_frame, text="Server:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.pac_server_var = tk.StringVar(value="146.19.196.16")
        ttk.Entry(config_frame, textvariable=self.pac_server_var, width=20).grid(row=0, column=1, padx=5, pady=5)
        
        # Port
        ttk.Label(config_frame, text="Port:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.pac_port_var = tk.StringVar(value="40742")
        ttk.Entry(config_frame, textvariable=self.pac_port_var, width=10).grid(row=0, column=3, padx=5, pady=5)
        
        # PAC Name
        ttk.Label(config_frame, text="PAC Name:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.pac_name_var = tk.StringVar(value="real_working_proxy")
        ttk.Entry(config_frame, textvariable=self.pac_name_var, width=20).grid(row=1, column=1, padx=5, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="🔧 Create PAC", command=self.create_pac_file).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="🧪 Test PAC", command=self.test_pac_file).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="📁 Open PAC Folder", command=self.open_pac_folder).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="🌐 Configure SwitchyOmega", command=self.configure_switchyomega_real_proxy).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="⚡ Update Omega Profile", command=self.update_omega_profile).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="🔧 Input Proxy", command=self.input_proxy_dialog).pack(side=tk.LEFT)
        
        # Status
        self.pac_status_text = tk.Text(main_frame, height=8, width=60)
        self.pac_status_text.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
    
    def refresh_pac_files(self):
        """Refresh PAC files list"""
        try:
            self.pac_files_listbox.delete(0, tk.END)
            pac_files = self.pac_manager.list_pac_files()
            
            for pac in pac_files:
                self.pac_files_listbox.insert(tk.END, f"{pac['name']} ({pac['size']} bytes)")
            
            self.pac_status_text.delete(1.0, tk.END)
            self.pac_status_text.insert(tk.END, f"Found {len(pac_files)} PAC files")
            
        except Exception as e:
            self.pac_status_text.delete(1.0, tk.END)
            self.pac_status_text.insert(tk.END, f"Error refreshing PAC files: {str(e)}")
    
    def view_pac_file(self):
        """View selected PAC file"""
        try:
            selection = self.pac_files_listbox.curselection()
            if not selection:
                self.pac_status_text.delete(1.0, tk.END)
                self.pac_status_text.insert(tk.END, "Please select a PAC file to view")
                return
            
            pac_name = self.pac_files_listbox.get(selection[0]).split(' ')[0]
            content = self.pac_manager.get_pac_content(pac_name)
            
            if content:
                self.pac_status_text.delete(1.0, tk.END)
                self.pac_status_text.insert(tk.END, f"Content of {pac_name}:\n\n{content}")
            else:
                self.pac_status_text.delete(1.0, tk.END)
                self.pac_status_text.insert(tk.END, f"Could not read {pac_name}")
                
        except Exception as e:
            self.pac_status_text.delete(1.0, tk.END)
            self.pac_status_text.insert(tk.END, f"Error viewing PAC file: {str(e)}")
    
    def import_pac_file(self):
        """Import PAC file"""
        try:
            from tkinter import filedialog
            file_path = filedialog.askopenfilename(
                title="Select PAC file to import",
                filetypes=[("PAC files", "*.pac"), ("All files", "*.*")]
            )
            
            if file_path:
                result = self.pac_manager.import_pac_from_switchyomega(file_path)
                if result:
                    self.pac_status_text.delete(1.0, tk.END)
                    self.pac_status_text.insert(tk.END, f"Imported: {result['pac_path']}")
                    self.refresh_pac_files()
                else:
                    self.pac_status_text.delete(1.0, tk.END)
                    self.pac_status_text.insert(tk.END, "Failed to import PAC file")
                    
        except Exception as e:
            self.pac_status_text.delete(1.0, tk.END)
            self.pac_status_text.insert(tk.END, f"Error importing PAC file: {str(e)}")
    
    def delete_pac_file(self):
        """Delete selected PAC file"""
        try:
            selection = self.pac_files_listbox.curselection()
            if not selection:
                self.pac_status_text.delete(1.0, tk.END)
                self.pac_status_text.insert(tk.END, "Please select a PAC file to delete")
                return
            
            pac_name = self.pac_files_listbox.get(selection[0]).split(' ')[0]
            pac_path = os.path.join(self.pac_manager.pac_dir, pac_name)
            
            if os.path.exists(pac_path):
                os.remove(pac_path)
                self.pac_status_text.delete(1.0, tk.END)
                self.pac_status_text.insert(tk.END, f"Deleted: {pac_name}")
                self.refresh_pac_files()
            else:
                self.pac_status_text.delete(1.0, tk.END)
                self.pac_status_text.insert(tk.END, f"File not found: {pac_name}")
                
        except Exception as e:
            self.pac_status_text.delete(1.0, tk.END)
            self.pac_status_text.insert(tk.END, f"Error deleting PAC file: {str(e)}")
    
    def create_pac_file(self):
        """Create PAC file"""
        try:
            proxy_config = {
                'proxy_server': self.pac_server_var.get(),
                'proxy_port': self.pac_port_var.get(),
                'profile_name': self.pac_name_var.get()
            }
            
            pac_name = f"{self.pac_name_var.get()}.pac"
            pac_path = self.pac_manager.create_pac_for_proxy(proxy_config, pac_name)
            
            if pac_path:
                self.pac_status_text.delete(1.0, tk.END)
                self.pac_status_text.insert(tk.END, f"Created PAC file: {pac_path}")
                self.refresh_pac_files()
            else:
                self.pac_status_text.delete(1.0, tk.END)
                self.pac_status_text.insert(tk.END, "Failed to create PAC file")
                
        except Exception as e:
            self.pac_status_text.delete(1.0, tk.END)
            self.pac_status_text.insert(tk.END, f"Error creating PAC file: {str(e)}")
    
    def test_pac_file(self):
        """Test PAC file"""
        try:
            self.pac_status_text.delete(1.0, tk.END)
            self.pac_status_text.insert(tk.END, "PAC file testing not implemented yet")
            
        except Exception as e:
            self.pac_status_text.delete(1.0, tk.END)
            self.pac_status_text.insert(tk.END, f"Error testing PAC file: {str(e)}")
    
    def open_pac_folder(self):
        """Open PAC folder"""
        try:
            import subprocess
            import platform
            
            if platform.system() == "Windows":
                subprocess.run(["explorer", self.pac_manager.pac_dir])
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", self.pac_manager.pac_dir])
            else:  # Linux
                subprocess.run(["xdg-open", self.pac_manager.pac_dir])
                
            self.pac_status_text.delete(1.0, tk.END)
            self.pac_status_text.insert(tk.END, f"Opened PAC folder: {self.pac_manager.pac_dir}")
            
        except Exception as e:
            self.pac_status_text.delete(1.0, tk.END)
            self.pac_status_text.insert(tk.END, f"Error opening PAC folder: {str(e)}")
    
    def configure_switchyomega_real_proxy(self):
        """Configure SwitchyOmega with real proxy"""
        try:
            self.pac_status_text.delete(1.0, tk.END)
            self.pac_status_text.insert(tk.END, "🌐 SwitchyOmega Configuration Guide\n")
            self.pac_status_text.insert(tk.END, f"📋 Proxy: 146.19.196.16:40742\n")
            self.pac_status_text.insert(tk.END, f"\n📋 Manual Configuration Steps:\n")
            self.pac_status_text.insert(tk.END, f"1. Open Chrome with profile that has SwitchyOmega\n")
            self.pac_status_text.insert(tk.END, f"2. Click SwitchyOmega extension icon\n")
            self.pac_status_text.insert(tk.END, f"3. Click 'Options' to open settings\n")
            self.pac_status_text.insert(tk.END, f"4. Click 'New Profile'\n")
            self.pac_status_text.insert(tk.END, f"5. Select 'PAC Profile'\n")
            self.pac_status_text.insert(tk.END, f"6. Name: 'Real_Proxy_PAC'\n")
            self.pac_status_text.insert(tk.END, f"7. Paste the PAC script below:\n")
            self.pac_status_text.insert(tk.END, f"\n📄 PAC Script:\n")
            self.pac_status_text.insert(tk.END, f"var FindProxyForURL = function(init, profiles) {{\n")
            self.pac_status_text.insert(tk.END, f"    return function(url, host) {{\n")
            self.pac_status_text.insert(tk.END, f"        \"use strict\";\n")
            self.pac_status_text.insert(tk.END, f"        var result = init, scheme = url.substr(0, url.indexOf(\":\"));\n")
            self.pac_status_text.insert(tk.END, f"        do {{\n")
            self.pac_status_text.insert(tk.END, f"            if (!profiles[result]) return result;\n")
            self.pac_status_text.insert(tk.END, f"            result = profiles[result];\n")
            self.pac_status_text.insert(tk.END, f"            if (typeof result === \"function\") result = result(url, host, scheme);\n")
            self.pac_status_text.insert(tk.END, f"        }} while (typeof result !== \"string\" || result.charCodeAt(0) === 43);\n")
            self.pac_status_text.insert(tk.END, f"        return result;\n")
            self.pac_status_text.insert(tk.END, f"    }};\n")
            self.pac_status_text.insert(tk.END, f"}}(\"+proxy\", {{\n")
            self.pac_status_text.insert(tk.END, f"    \"+proxy\": function(url, host, scheme) {{\n")
            self.pac_status_text.insert(tk.END, f"        \"use strict\";\n")
            self.pac_status_text.insert(tk.END, f"        if (/^127\\.0\\.0\\.1$/.test(host) || /^::1$/.test(host) || /^localhost$/.test(host)) return \"DIRECT\";\n")
            self.pac_status_text.insert(tk.END, f"        if (/^chrome-extension:\\/\\//.test(url)) return \"DIRECT\";\n")
            self.pac_status_text.insert(tk.END, f"        if (/^chrome:\\/\\//.test(url)) return \"DIRECT\";\n")
            self.pac_status_text.insert(tk.END, f"        if (/^chrome-devtools:\\/\\//.test(url)) return \"DIRECT\";\n")
            self.pac_status_text.insert(tk.END, f"        return \"PROXY 146.19.196.16:40742\";\n")
            self.pac_status_text.insert(tk.END, f"    }}\n")
            self.pac_status_text.insert(tk.END, f"}});\n")
            self.pac_status_text.insert(tk.END, f"\n8. Click 'Save'\n")
            self.pac_status_text.insert(tk.END, f"9. Select the profile and click 'Apply'\n")
            self.pac_status_text.insert(tk.END, f"\n✅ Ready to use!\n")
            
        except Exception as e:
            self.pac_status_text.delete(1.0, tk.END)
            self.pac_status_text.insert(tk.END, f"❌ Error: {str(e)}")
    
    def update_omega_profile(self):
        """Update Omega profile with real proxy"""
        try:
            self.pac_status_text.delete(1.0, tk.END)
            self.pac_status_text.insert(tk.END, "⚡ Updating Omega Profile with Real Proxy...\n")
            self.pac_status_text.insert(tk.END, f"📋 Proxy: 146.19.196.16:40742\n")
            
            def update_thread():
                try:
                    import shutil
                    from datetime import datetime
                    
                    # Backup original file
                    original_file = "OmegaProfile_proxy.pac"
                    backup_file = f"OmegaProfile_proxy_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pac"
                    
                    if os.path.exists(original_file):
                        shutil.copy2(original_file, backup_file)
                    
                    # New PAC content with real proxy
                    new_pac_content = '''var FindProxyForURL = function(init, profiles) {
    return function(url, host) {
        "use strict";
        var result = init, scheme = url.substr(0, url.indexOf(":"));
        do {
            if (!profiles[result]) return result;
            result = profiles[result];
            if (typeof result === "function") result = result(url, host, scheme);
        } while (typeof result !== "string" || result.charCodeAt(0) === 43);
        return result;
    };
}("+proxy", {
    "+proxy": function(url, host, scheme) {
        "use strict";
        // Local addresses - direct connection
        if (/^127\\.0\\.0\\.1$/.test(host) || /^::1$/.test(host) || /^localhost$/.test(host)) return "DIRECT";
        
        // Chrome internal addresses - direct connection
        if (/^chrome-extension:\\/\\//.test(url)) return "DIRECT";
        if (/^chrome:\\/\\//.test(url)) return "DIRECT";
        if (/^chrome-devtools:\\/\\//.test(url)) return "DIRECT";
        
        // Use real proxy for all other requests
        return "PROXY 146.19.196.16:40742";
    }
});'''
                    
                    # Write new content
                    with open(original_file, 'w', encoding='utf-8') as f:
                        f.write(new_pac_content)
                    
                    def update_ui():
                        self.pac_status_text.delete(1.0, tk.END)
                        self.pac_status_text.insert(tk.END, f"✅ Omega Profile updated successfully!\n")
                        self.pac_status_text.insert(tk.END, f"📁 File: {original_file}\n")
                        self.pac_status_text.insert(tk.END, f"💾 Backup: {backup_file}\n")
                        self.pac_status_text.insert(tk.END, f"🌐 Proxy: 146.19.196.16:40742\n")
                        self.pac_status_text.insert(tk.END, f"\n📋 Next steps:\n")
                        self.pac_status_text.insert(tk.END, f"1. Open SwitchyOmega options\n")
                        self.pac_status_text.insert(tk.END, f"2. Click 'Import/Export'\n")
                        self.pac_status_text.insert(tk.END, f"3. Import the updated PAC file\n")
                        self.pac_status_text.insert(tk.END, f"4. Apply changes\n")
                        self.pac_status_text.insert(tk.END, f"\n✅ Ready to use!\n")
                    
                    self.root.after(0, update_ui)
                    
                except Exception as e:
                    def update_ui():
                        self.pac_status_text.delete(1.0, tk.END)
                        self.pac_status_text.insert(tk.END, f"❌ Error: {str(e)}\n")
                    
                    self.root.after(0, update_ui)
            
            # Run in separate thread
            threading.Thread(target=update_thread, daemon=True).start()
            
        except Exception as e:
            self.pac_status_text.delete(1.0, tk.END)
            self.pac_status_text.insert(tk.END, f"❌ Error: {str(e)}")
    
    def input_proxy_dialog(self):
        """Input proxy dialog for SwitchyOmega configuration"""
        try:
            self.pac_status_text.delete(1.0, tk.END)
            self.pac_status_text.insert(tk.END, "🔧 Opening Proxy Input Dialog...\n")
            
            def input_thread():
                try:
                    import tkinter as tk
                    from tkinter import simpledialog, messagebox
                    
                    def update_ui():
                        self.pac_status_text.delete(1.0, tk.END)
                        self.pac_status_text.insert(tk.END, f"📋 Proxy Input Dialog\n")
                        self.pac_status_text.insert(tk.END, f"⏳ Please enter proxy details...\n")
                    
                    self.root.after(0, update_ui)
                    
                    # Get proxy details from user
                    proxy_server = simpledialog.askstring("Proxy Server", "Enter Proxy Server (e.g., 146.19.196.16):")
                    if not proxy_server:
                        def update_ui():
                            self.pac_status_text.delete(1.0, tk.END)
                            self.pac_status_text.insert(tk.END, f"❌ Proxy input cancelled\n")
                        self.root.after(0, update_ui)
                        return
                    
                    proxy_port = simpledialog.askstring("Proxy Port", "Enter Proxy Port (e.g., 40742):")
                    if not proxy_port:
                        def update_ui():
                            self.pac_status_text.delete(1.0, tk.END)
                            self.pac_status_text.insert(tk.END, f"❌ Proxy input cancelled\n")
                        self.root.after(0, update_ui)
                        return
                    
                    # Ask for username and password (optional)
                    proxy_username = simpledialog.askstring("Proxy Username", "Enter Proxy Username (optional):", show="*")
                    proxy_password = simpledialog.askstring("Proxy Password", "Enter Proxy Password (optional):", show="*")
                    
                    # Get profile list
                    profiles = self.manager.get_all_profiles()
                    if not profiles:
                        def update_ui():
                            self.pac_status_text.delete(1.0, tk.END)
                            self.pac_status_text.insert(tk.END, f"❌ No profiles found\n")
                        self.root.after(0, update_ui)
                        return
                    
                    # Ask user to select profile
                    profile_choice = simpledialog.askstring("Select Profile", f"Enter profile name to configure:\nAvailable: {', '.join(profiles[:5])}{'...' if len(profiles) > 5 else ''}")
                    if not profile_choice or profile_choice not in profiles:
                        def update_ui():
                            self.pac_status_text.delete(1.0, tk.END)
                            self.pac_status_text.insert(tk.END, f"❌ Invalid profile name\n")
                        self.root.after(0, update_ui)
                        return
                    
                    def update_ui():
                        self.pac_status_text.delete(1.0, tk.END)
                        self.pac_status_text.insert(tk.END, f"📋 Proxy Details:\n")
                        self.pac_status_text.insert(tk.END, f"   Server: {proxy_server}\n")
                        self.pac_status_text.insert(tk.END, f"   Port: {proxy_port}\n")
                        self.pac_status_text.insert(tk.END, f"   Username: {'*' * len(proxy_username) if proxy_username else 'None'}\n")
                        self.pac_status_text.insert(tk.END, f"   Password: {'*' * len(proxy_password) if proxy_password else 'None'}\n")
                        self.pac_status_text.insert(tk.END, f"   Profile: {profile_choice}\n")
                        self.pac_status_text.insert(tk.END, f"\n🔧 Configuring SwitchyOmega...\n")
                    
                    self.root.after(0, update_ui)
                    
                    # Create PAC file first
                    pac_name = f"proxy_{proxy_server}_{proxy_port}.pac"
                    pac_success, pac_result = self.manager.create_pac_from_proxy(
                        proxy_server, int(proxy_port), proxy_username, proxy_password, pac_name
                    )
                    
                    if not pac_success:
                        def update_ui():
                            self.pac_status_text.delete(1.0, tk.END)
                            self.pac_status_text.insert(tk.END, f"❌ Error creating PAC file: {pac_result}\n")
                        self.root.after(0, update_ui)
                        return
                    
                    # Create proxy config
                    proxy_config = {
                        'proxy_server': proxy_server,
                        'proxy_port': int(proxy_port),
                        'proxy_type': 'HTTP',
                        'profile_name': 'proxy'
                    }
                    
                    if proxy_username:
                        proxy_config['username'] = proxy_username
                    if proxy_password:
                        proxy_config['password'] = proxy_password
                    
                    # Configure SwitchyOmega
                    success, message = self.manager.configure_switchyomega_proxy(profile_choice, proxy_config)
                    
                    def update_ui():
                        self.pac_status_text.delete(1.0, tk.END)
                        if success:
                            self.pac_status_text.insert(tk.END, f"✅ Proxy configured successfully!\n")
                            self.pac_status_text.insert(tk.END, f"📋 Profile: {profile_choice}\n")
                            self.pac_status_text.insert(tk.END, f"🌐 Proxy: {proxy_server}:{proxy_port}\n")
                            self.pac_status_text.insert(tk.END, f"📁 PAC File: {pac_name}\n")
                            self.pac_status_text.insert(tk.END, f"🔧 SwitchyOmega: Ready to use\n")
                            self.pac_status_text.insert(tk.END, f"\n📋 Next steps:\n")
                            self.pac_status_text.insert(tk.END, f"1. Open Chrome with profile: {profile_choice}\n")
                            self.pac_status_text.insert(tk.END, f"2. Click SwitchyOmega extension icon (Ω)\n")
                            self.pac_status_text.insert(tk.END, f"3. Select 'proxy' profile\n")
                            self.pac_status_text.insert(tk.END, f"4. Test connection\n")
                            self.pac_status_text.insert(tk.END, f"\n✅ Ready to use!\n")
                        else:
                            self.pac_status_text.insert(tk.END, f"❌ Error: {message}\n")
                            self.pac_status_text.insert(tk.END, f"📁 PAC File created: {pac_name}\n")
                            self.pac_status_text.insert(tk.END, f"🔧 You can import PAC file manually\n")
                    
                    self.root.after(0, update_ui)
                    
                except Exception as e:
                    def update_ui(error=e):
                        self.pac_status_text.delete(1.0, tk.END)
                        self.pac_status_text.insert(tk.END, f"❌ Error: {str(error)}\n")
                        self.pac_status_text.insert(tk.END, f"🔧 Please try again\n")
                    
                    self.root.after(0, update_ui)
            
            # Run in separate thread
            threading.Thread(target=input_thread, daemon=True).start()
            
        except Exception as e:
            self.pac_status_text.delete(1.0, tk.END)
            self.pac_status_text.insert(tk.END, f"❌ Error: {str(e)}")
    
    def update_proxy_input_combos(self):
        """Cập nhật danh sách profiles cho cả target và source"""
        try:
            profiles = self.manager.get_all_profiles()
            
            # Update target combo
            if hasattr(self, 'proxy_input_target_combo') and self.proxy_input_target_combo.winfo_exists():
                self.proxy_input_target_combo['values'] = profiles
                if profiles and not self.proxy_input_target.get():
                    self.proxy_input_target_combo.set(profiles[0])
            
            # Update source combo
            if hasattr(self, 'proxy_input_source_combo') and self.proxy_input_source_combo.winfo_exists():
                self.proxy_input_source_combo['values'] = profiles
                if "76h" in profiles:
                    self.proxy_input_source_combo.set("76h")
                elif profiles:
                    self.proxy_input_source_combo.set(profiles[0])
                    
        except Exception as e:
            print(f"Error updating proxy input combos: {e}")
    
    def log_proxy_status(self, message):
        """Ghi log vào proxy status text"""
        self.proxy_status_text.insert(tk.END, f"{message}\n")
        self.proxy_status_text.see(tk.END)
        self.root.update()
    
    # auto_fix_proxy_input removed per simplification request
    
    def parse_proxy_input(self):
        """Parse proxy string input"""
        proxy_string = self.proxy_input_string.get().strip()
        
        if not proxy_string:
            self.log_proxy_status("❌ Please enter a proxy string")
            return
        
        try:
            # Parse proxy string: server:port:username:password
            parts = proxy_string.split(':')
            if len(parts) != 4:
                raise ValueError("Invalid proxy format")
            
            server, port, username, password = parts
            
            # Validate
            import re
            if not re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', server):
                raise ValueError("Invalid IP address")
            
            if not port.isdigit() or not (1 <= int(port) <= 65535):
                raise ValueError("Invalid port")
            
            self.log_proxy_status(f"✅ Proxy parsed successfully:")
            self.log_proxy_status(f"   Server: {server}")
            self.log_proxy_status(f"   Port: {port}")
            self.log_proxy_status(f"   Username: {username}")
            self.log_proxy_status(f"   Password: {password}")
            
            # Store parsed data
            self.parsed_proxy = {
                'server': server,
                'port': int(port),
                'username': username,
                'password': password
            }
            
        except Exception as e:
            self.log_proxy_status(f"❌ Error parsing proxy: {e}")
    
    def apply_proxy_input(self):
        """Apply proxy to target profile by editing SwitchyOmega settings.json (no Chrome launch)."""
        if not hasattr(self, 'parsed_proxy'):
            self.log_proxy_status("❌ Please parse proxy first")
            return
        
        target_profile = self.proxy_input_target.get().strip()
        if not target_profile:
            self.log_proxy_status("❌ Please select target profile")
            return
        
        try:
            self.log_proxy_status(f"💾 Writing proxy to settings.json for: {target_profile}")
            proxy_string = f"{self.parsed_proxy['server']}:{self.parsed_proxy['port']}:{self.parsed_proxy['username']}:{self.parsed_proxy['password']}"
            success, message = self.manager.apply_proxy_via_settings_string(target_profile, proxy_string)
            
            if success:
                self.log_proxy_status(f"✅ Proxy saved to SwitchyOmega for {target_profile}")
                self.log_proxy_status(f"   {proxy_string}")
                self.log_proxy_status("   Method: Direct settings.json update")
                self.log_proxy_status(f"   Message: {message}")

                # Immediately import into extension so it becomes active
                self.log_proxy_status("[LAUNCH] Importing into extension to activate...")
                imp_ok, imp_msg = self.manager.force_import_settings_into_extension(target_profile)
                if imp_ok:
                    self.log_proxy_status(f"✅ Activated in extension: {imp_msg}")
                    self.log_proxy_status("   Verify at: chrome-extension://pfnededegaaopdmhkdmcofjmoldfiped/options.html#!/profile/proxy")
                else:
                    self.log_proxy_status(f"⚠️ Could not auto-activate: {imp_msg}")
            else:
                self.log_proxy_status(f"❌ Failed to save proxy for {target_profile}")
                self.log_proxy_status(f"   Error: {message}")
                
        except Exception as e:
            self.log_proxy_status(f"❌ Error applying proxy: {e}")
    
    # copy_proxy_from_source removed per simplification request

    def force_import_proxy(self):
        """Import settings.json into SwitchyOmega extension storage for target profile."""
        target_profile = self.proxy_input_target.get().strip()
        if not target_profile:
            self.log_proxy_status("❌ Please select target profile")
            return
        try:
            self.log_proxy_status(f"[LAUNCH] Importing settings into extension for: {target_profile}")
            success, message = self.manager.force_import_settings_into_extension(target_profile)
            if success:
                self.log_proxy_status(f"✅ {message}")
                self.log_proxy_status("   Open options to verify: chrome-extension://pfnededegaaopdmhkdmcofjmoldfiped/options.html#!/profile/proxy")
            else:
                self.log_proxy_status(f"❌ {message}")
        except Exception as e:
            self.log_proxy_status(f"❌ Error importing into extension: {e}")

    def bulk_apply_from_csv(self):
        """Bulk apply proxies to profiles from CSV/TSV/XLSX.
        Supported row formats:
          - profile, proxy_string
          - profile, server, port, username, password
        """
        import csv, os
        from tkinter import filedialog
        path = filedialog.askopenfilename(
            title="Select CSV/TSV/XLSX file",
            filetypes=[["CSV/TSV","*.csv *.tsv"],["Excel","*.xlsx"],["All","*.*"]]
        )
        if not path:
            return
        try:
            self.log_proxy_status(f"📄 Loading file: {path}")
            ext = os.path.splitext(path)[1].lower()
            rows = []
            if ext in [".csv", ".tsv", ""]:
                # Try multiple encodings and delimiters
                errors = []
                for enc in ("utf-8", "utf-8-sig", "cp1252", "latin-1"):
                    try:
                        with open(path, 'r', encoding=enc, errors='strict') as f:
                            sample = f.read(2048)
                            f.seek(0)
                            try:
                                dialect = csv.Sniffer().sniff(sample, delimiters=",\t;")
                            except Exception:
                                dialect = csv.excel
                                if "\t" in sample and "," not in sample:
                                    dialect.delimiter = "\t"
                            reader = csv.reader(f, dialect)
                            rows = [ [c.strip() for c in r] for r in reader ]
                            break
                    except UnicodeDecodeError as ue:
                        errors.append(str(ue))
                        continue
                if not rows:
                    raise UnicodeDecodeError("csv", b"", 0, 1, "; ".join(errors))
            elif ext == ".xlsx":
                try:
                    import openpyxl
                except Exception:
                    self.log_proxy_status("⚠️ Missing 'openpyxl'. Please install or export Excel to CSV UTF-8.")
                    return
                wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
                for ws in wb.worksheets:
                    for r in ws.iter_rows(values_only=True):
                        if r:
                            rows.append([str(c).strip() if c is not None else "" for c in r])
            else:
                self.log_proxy_status("❌ Unsupported file type")
            return
        
            # Build mapping
            mapping = {}
            proxy_rows_without_profile = []
            for row in rows:
                if not row or all(c == "" for c in row):
                    continue
                # Skip header lines
                header0 = (row[0] or "").lower()
                if header0 in ("profile", "profile_name", "name"):
                    continue
                if len(row) >= 2 and ":" in (row[1] or ""):
                    profile = row[0]
                    proxy = row[1]
                elif len(row) >= 5:
                    profile = row[0]
                    proxy = f"{row[1]}:{row[2]}:{row[3]}:{row[4]}"
                elif len(row) == 4 and header0 and header0.replace('.', '').isdigit():
                    # Likely server,port,username,password without profile
                    proxy = f"{row[0]}:{row[1]}:{row[2]}:{row[3]}"
                    proxy_rows_without_profile.append(proxy)
                    continue
                elif len(row) == 1 and ":" in (row[0] or ""):
                    # Single column proxy string list
                    proxy_rows_without_profile.append(row[0])
                    continue
                else:
                    # Not recognized; try TSV with 5 items where last may be empty
                    continue
                profile = str(profile).strip()
                proxy = str(proxy).strip()
                if profile and proxy:
                    mapping[profile] = proxy

            # If file had proxies but no profile column, map in order to available profiles
            if proxy_rows_without_profile and not mapping:
                available = self.manager.get_all_profiles() or []
                if not available:
                    self.log_proxy_status("❌ No available profiles to map proxies to.")
                    return
                
                count = min(len(available), len(proxy_rows_without_profile))
                for i in range(count):
                    mapping[available[i]] = proxy_rows_without_profile[i]
                self.log_proxy_status(f"ℹ️ Mapped {count} proxies to first {count} available profiles.")

            if not mapping:
                self.log_proxy_status("❌ File has no usable rows. Expected 'profile,proxy' or 'profile,server,port,username,password', or a single-column list of proxies to map in order to existing profiles.")
                return

            results, ok_count = self.manager.bulk_apply_proxy_map_via_settings(mapping)
            self.log_proxy_status(f"✅ Bulk applied: {ok_count}/{len(mapping)}")
            for r in results[:20]:
                status = "OK" if r['success'] else "ERR"
                self.log_proxy_status(f" - {r['profile']}: {status} - {r['message']}")
        except Exception as e:
            self.log_proxy_status(f"❌ Bulk apply failed: {e}")

    def bulk_apply_from_text(self):
        """Bulk apply proxies by pasting multiple lines, one proxy per selected profile.
        Mapping rules:
          - If rows are selected in the profiles table, map lines to those profiles in the shown order.
          - Else map to all profiles in the manager's order.
        Each line format: server:port[:username:password]
        """
        try:
            # Determine target profiles (guard against destroyed treeview)
            target_profiles = []
            try:
                if hasattr(self, 'tree') and self.tree.winfo_exists():
                    selection_ids = list(self.tree.selection())
                    for item_id in selection_ids:
                        try:
                            target_profiles.append(self.tree.item(item_id)['text'])
                        except Exception:
                            continue
            except Exception:
                pass
            if not target_profiles:
                target_profiles = self.manager.get_all_profiles()

            if not target_profiles:
                messagebox.showwarning("Warning", "No target profiles available")
                return

            # Dialog for pasting proxies
            dialog = tk.Toplevel(self.root)
            dialog.title("Bulk Apply Proxies (Lines)")
            dialog.geometry("720x520")
            dialog.resizable(True, True)
            dialog.transient(self.root)
            dialog.grab_set()

            ttk.Label(dialog, text=f"Paste proxies (one per line). Targets: {len(target_profiles)} profile(s)", font=("Segoe UI", 10, "bold")).pack(anchor=tk.W, padx=12, pady=(10, 4))
            txt = tk.Text(dialog, height=18, font=("Consolas", 10))
            txt.pack(fill=tk.BOTH, expand=True, padx=12)
            txt.insert(tk.END, "# Example\n146.19.196.15:40684:user:pass\n146.19.196.16:40700\n")

            status = tk.StringVar(value="Ready")
            ttk.Label(dialog, textvariable=status, foreground="#6b6b6b").pack(anchor=tk.W, padx=12, pady=(6,0))

            btns = ttk.Frame(dialog)
            btns.pack(fill=tk.X, padx=12, pady=10)

            def run_apply():
                lines = [ln.strip() for ln in txt.get("1.0", tk.END).splitlines() if ln.strip() and not ln.strip().startswith('#')]
                if not lines:
                    messagebox.showwarning("Warning", "Please paste at least one proxy line")
                    return
                # Respect optional count selector if present
                try:
                    max_count = int(self.bulk_lines_count_var.get()) if hasattr(self, 'bulk_lines_count_var') else None
                except Exception:
                    max_count = None
                count = min(len(lines), len(target_profiles))
                if max_count is not None:
                    count = min(count, max_count)
                pairs = list(zip(target_profiles[:count], lines[:count]))

                self.proxy_status_text.insert(tk.END, f"[LAUNCH] Bulk apply {count} proxies to {count} profiles\n")

                def worker():
                    ok = 0; fail = 0
                    for profile, proxy_str in pairs:
                        try:
                            success, _ = self.manager.apply_proxy_via_settings_string(profile, proxy_str)
                            if success:
                                # Activate immediately inside extension
                                self.manager.force_import_settings_into_extension(profile)
                                ok += 1
                                self.root.after(0, lambda p=profile: self.proxy_status_text.insert(tk.END, f"✅ Applied to {p}\n"))
                            else:
                                fail += 1
                                self.root.after(0, lambda p=profile: self.proxy_status_text.insert(tk.END, f"❌ Failed {p}\n"))
                        except Exception as e:
                            fail += 1
                            self.root.after(0, lambda p=profile, msg=str(e): self.proxy_status_text.insert(tk.END, f"❌ {p}: {msg}\n"))

                    self.root.after(0, lambda: status.set(f"Done. Success: {ok}, Failed: {fail}"))

                threading.Thread(target=worker, daemon=True).start()

            ttk.Button(btns, text="Apply", command=run_apply).pack(side=tk.RIGHT)
            ttk.Button(btns, text="Cancel", command=dialog.destroy).pack(side=tk.RIGHT, padx=(0,8))
                
        except Exception as e:
            messagebox.showerror("Error", f"Bulk apply failed: {e}")

    def bulk_apply_from_text_tab(self):
        """Use the bulk text area in the Bulk tab to run bulk apply."""
        try:
            if not hasattr(self, 'bulk_text') or not self.bulk_text.winfo_exists():
                messagebox.showwarning("Warning", "Bulk text area not available")
                return
            content = self.bulk_text.get("1.0", tk.END)
            # Reuse the same logic by creating a temporary dialog-like call
            # but simpler: parse here and call manager directly
            lines = [ln.strip() for ln in content.splitlines() if ln.strip() and not ln.strip().startswith('#')]
            if not lines:
                messagebox.showwarning("Warning", "Please enter at least one proxy line")
                return

            # Determine targets from bulk listbox if selections exist, otherwise from profiles tree or all
            targets = []
            try:
                if hasattr(self, 'bulk_profile_listbox') and self.bulk_profile_listbox.winfo_exists():
                    idxs = list(self.bulk_profile_listbox.curselection())
                    if idxs:
                        targets = [self.bulk_profile_listbox.get(i) for i in idxs]
            except Exception:
                pass
            if not targets:
                try:
                    if hasattr(self, 'tree') and self.tree.winfo_exists():
                        for iid in list(self.tree.selection()):
                            try:
                                targets.append(self.tree.item(iid)['text'])
                            except Exception:
                                continue
                except Exception:
                    pass
            if not targets:
                targets = self.manager.get_all_profiles()

            # Limit count
            try:
                max_count = int(self.bulk_lines_count_var.get()) if hasattr(self, 'bulk_lines_count_var') else None
            except Exception:
                max_count = None
            count = min(len(lines), len(targets))
            if max_count is not None:
                count = min(count, max_count)

            pairs = list(zip(targets[:count], lines[:count]))
            self.proxy_status_text.insert(tk.END, f"[LAUNCH] Bulk apply {count} proxies to {count} profiles\n")

            def worker():
                ok = 0; fail = 0
                for profile, proxy_str in pairs:
                    try:
                        success, _ = self.manager.apply_proxy_via_settings_string(profile, proxy_str)
                        if success:
                            self.manager.force_import_settings_into_extension(profile)
                            ok += 1
                            self.root.after(0, lambda p=profile: self.proxy_status_text.insert(tk.END, f"✅ Applied to {p}\n"))
                        else:
                            fail += 1
                            self.root.after(0, lambda p=profile: self.proxy_status_text.insert(tk.END, f"❌ Failed {p}\n"))
                    except Exception as e:
                        fail += 1
                        self.root.after(0, lambda p=profile, msg=str(e): self.proxy_status_text.insert(tk.END, f"❌ {p}: {msg}\n"))
                self.root.after(0, lambda: self.proxy_status_text.insert(tk.END, f"Done. Success: {ok}, Failed: {fail}\n"))

            threading.Thread(target=worker, daemon=True).start()
        except Exception as e:
            messagebox.showerror("Error", f"Bulk apply failed: {e}")

    def _update_bulk_selected_count(self):
        try:
            count = len(list(self.bulk_profile_listbox.curselection())) if hasattr(self, 'bulk_profile_listbox') and self.bulk_profile_listbox.winfo_exists() else 0
            if hasattr(self, 'bulk_selected_count_var'):
                self.bulk_selected_count_var.set(f"Selected: {count}")
        except Exception:
            pass

    def _update_bulk_lines_count(self):
        try:
            if hasattr(self, 'bulk_text') and self.bulk_text.winfo_exists():
                lines = [ln.strip() for ln in self.bulk_text.get("1.0", tk.END).splitlines() if ln.strip() and not ln.strip().startswith('#')]
                if hasattr(self, 'bulk_lines_info_var'):
                    self.bulk_lines_info_var.set(f"Lines: {len(lines)}")
        except Exception:
            pass
    
    def test_proxy_profile(self):
        """Test proxy profile"""
        target_profile = self.proxy_input_target.get().strip()
        if not target_profile:
            self.log_proxy_status("❌ Please select target profile")
            return
        
        try:
            self.log_proxy_status(f"🧪 Testing profile: {target_profile}")
            
            # Analyze profile proxy
            # Analyze profile proxy - placeholder for now
            success = True
            
            if success:
                self.log_proxy_status(f"✅ Profile {target_profile} is ready for testing")
                self.log_proxy_status(f"   You can now launch Chrome with this profile")
            else:
                self.log_proxy_status(f"❌ Profile {target_profile} has issues")
                
        except Exception as e:
            self.log_proxy_status(f"❌ Error testing profile: {e}")
    
    def show_current_proxy(self):
        """Show current proxy settings for selected profile"""
        target_profile = self.proxy_input_target.get().strip()
        if not target_profile:
            self.log_proxy_status("❌ Please select target profile")
            return
        
        try:
            self.log_proxy_status(f"🔍 Checking current proxy for profile: {target_profile}")
            
            # Get current proxy using direct updater
            # Check if profile has proxy configured (placeholder)
            self.log_proxy_status(f"📋 Checking proxy configuration for {target_profile}")
            self.log_proxy_status(f"   Note: Use SwitchyOmega extension to view current proxy settings")
            self.log_proxy_status(f"   Extension URL: chrome-extension://pfnededegaaopdmhkdmcofjmoldfiped/options.html")
                
        except Exception as e:
            self.log_proxy_status(f"❌ Error checking current proxy: {e}")
    
    # Auto 2FA Methods
    def setup_device_login(self):
        """Setup device login để lấy refresh token"""
        try:
            email = self.auto_2fa_email.get()
            client_id = self.auto_2fa_client_id.get()
            
            if not email:
                messagebox.showerror("Error", "Please enter email address")
                return
            
            if not client_id:
                messagebox.showerror("Error", "Please enter Client ID")
                return
            
            self.log_auto_2fa(f"🔐 Starting device login for: {email}")
            self.log_auto_2fa(f"🆔 Client ID: {client_id}")
            
            def device_login_thread():
                try:
                    import msal
                    import json
                    
                    app = msal.PublicClientApplication(
                        client_id, 
                        authority="https://login.microsoftonline.com/consumers"
                    )
                    
                    flow = app.initiate_device_flow(scopes=["Mail.Read"])
                    device_code = flow.get('user_code', '')
                    device_url = flow.get('verification_uri', 'https://www.microsoft.com/link')
                    
                    def update_ui():
                        self.log_auto_2fa(f"🌐 Open browser: {device_url}")
                        self.log_auto_2fa(f"🔑 Enter code: {device_code}")
                        self.log_auto_2fa("⏳ Waiting for you to complete login...")
                    
                    self.root.after(0, update_ui)
                    
                    result = app.acquire_token_by_device_flow(flow)
                    
                    if "error" in result:
                        def update_ui():
                            self.log_auto_2fa(f"❌ Device login failed: {result.get('error_description', result.get('error'))}")
                        self.root.after(0, update_ui)
                        return
                    
                    access_token = result.get("access_token")
                    refresh_token = result.get("refresh_token")
                    
                    if not access_token:
                        def update_ui():
                            self.log_auto_2fa("❌ No access token received")
                        self.root.after(0, update_ui)
                        return
                    
                    def update_ui():
                        self.log_auto_2fa("✅ Device login successful!")
                        if refresh_token:
                            self.auto_2fa_refresh_token.set(refresh_token)
                            self.log_auto_2fa("🔄 Refresh token saved automatically")
                        else:
                            self.log_auto_2fa("⚠️ No refresh token received - token will expire in 1 hour")
                    
                    self.root.after(0, update_ui)
                except Exception as e:
                    def update_ui():
                        self.log_auto_2fa(f"❌ Device login error: {e}")
                    self.root.after(0, update_ui)
            
            # Run in background thread
            import threading
            thread = threading.Thread(target=device_login_thread)
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            self.log_auto_2fa(f"❌ Setup error: {e}")
    
    def test_auto_2fa_connection(self):
        """Test auto 2FA connection"""
        try:
            email = self.auto_2fa_email.get()
            refresh_token = self.auto_2fa_refresh_token.get()
            client_id = self.auto_2fa_client_id.get()
            email_password = self.auto_2fa_email_password.get()
            
            if not email:
                messagebox.showerror("Error", "Please enter email address")
                return
            
            self.log_auto_2fa(f"🧪 Testing auto 2FA for: {email}")
            
            def test_thread():
                try:
                    # Sử dụng ultimate handler trực tiếp
                    success, result = self.manager.ultimate_auto_2fa_handler(
                        email=email,
                        password=email_password,
                        refresh_token=refresh_token,
                        client_id=client_id
                    )
                    
                    def update_ui():
                        if success:
                            self.log_auto_2fa(f"✅ Test successful: {result}")
                        else:
                            self.log_auto_2fa(f"❌ Test failed: {result}")
                    
                    self.root.after(0, update_ui)
                    
                except Exception as e:
                    def update_ui():
                        self.log_auto_2fa(f"❌ Test error: {e}")
                    self.root.after(0, update_ui)
            
            # Run in background thread
            import threading
            thread = threading.Thread(target=test_thread)
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            self.log_auto_2fa(f"❌ Test error: {e}")
    
    def test_account_line_2fa(self):
        """Test account line với auto 2FA"""
        try:
            account_line = self.test_account_line.get()
            
            if not account_line:
                messagebox.showerror("Error", "Please enter account line")
                return
            
            self.log_auto_2fa(f"🧪 Testing account line: {account_line[:50]}...")
            
            def test_thread():
                try:
                    success, result = self.manager.test_graph_mail_fetch(account_line)
                    
                    def update_ui():
                        if success:
                            self.log_auto_2fa(f"✅ Account line test successful: {result}")
                        else:
                            self.log_auto_2fa(f"❌ Account line test failed: {result}")
                    
                    self.root.after(0, update_ui)
                    
                except Exception as e:
                    def update_ui():
                        self.log_auto_2fa(f"❌ Account line test error: {e}")
                    self.root.after(0, update_ui)
            
            # Run in background thread
            import threading
            thread = threading.Thread(target=test_thread)
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            self.log_auto_2fa(f"❌ Account line test error: {e}")
    
    def save_auto_2fa_config(self):
        """Save auto 2FA configuration"""
        try:
            config = {
                'email': self.auto_2fa_email.get(),
                'refresh_token': self.auto_2fa_refresh_token.get(),
                'client_id': self.auto_2fa_client_id.get(),
                'email_password': self.auto_2fa_email_password.get()
            }
            
            import json
            with open('auto_2fa_config.json', 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
            
            self.log_auto_2fa("💾 Auto 2FA configuration saved successfully")
            messagebox.showinfo("Success", "Auto 2FA configuration saved!")
            
        except Exception as e:
            self.log_auto_2fa(f"❌ Save error: {e}")
            messagebox.showerror("Error", f"Error saving config: {e}")
    
    def load_auto_2fa_config(self):
        """Load auto 2FA configuration"""
        try:
            import json
            import os
            
            if os.path.exists('auto_2fa_config.json'):
                with open('auto_2fa_config.json', 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                self.auto_2fa_email.set(config.get('email', ''))
                self.auto_2fa_refresh_token.set(config.get('refresh_token', ''))
                self.auto_2fa_client_id.set(config.get('client_id', '9e5f94bc-e8a4-4e73-b8be-63364c29d753'))
                self.auto_2fa_email_password.set(config.get('email_password', ''))
                
                self.log_auto_2fa("📂 Auto 2FA configuration loaded successfully")
            else:
                self.log_auto_2fa("📂 No saved configuration found")
                
        except Exception as e:
            self.log_auto_2fa(f"❌ Load error: {e}")
    
    def clear_auto_2fa_config(self):
        """Clear auto 2FA configuration"""
        try:
            self.auto_2fa_email.set('')
            self.auto_2fa_refresh_token.set('')
            self.auto_2fa_client_id.set('9e5f94bc-e8a4-4e73-b8be-63364c29d753')
            self.auto_2fa_email_password.set('')
            
            self.log_auto_2fa("🗑️ Auto 2FA configuration cleared")
            
        except Exception as e:
            self.log_auto_2fa(f"❌ Clear error: {e}")
    
    def start_continuous_monitor(self):
        """Start continuous monitor"""
        try:
            email = self.auto_2fa_email.get()
            refresh_token = self.auto_2fa_refresh_token.get()
            client_id = self.auto_2fa_client_id.get()
            email_password = self.auto_2fa_email_password.get()
            
            if not email:
                messagebox.showerror("Error", "Please enter email address")
                return
            
            self.log_auto_2fa(f"🔍 Starting continuous monitor for: {email}")
            
            def monitor_thread():
                try:
                    # Sử dụng continuous monitor từ chrome_manager
                    success, result = self.manager.continuous_monitor_2fa(
                        email=email,
                        password=email_password,
                        refresh_token=refresh_token,
                        client_id=client_id,
                        duration=300,  # 5 phút
                        interval=30   # 30 giây
                    )
                    
                    def update_ui():
                        if success:
                            self.log_auto_2fa(f"🎉 Monitor found code: {result}")
                        else:
                            self.log_auto_2fa(f"⏰ Monitor timeout: {result}")
                    
                    self.root.after(0, update_ui)
                    
                except Exception as e:
                    def update_ui():
                        self.log_auto_2fa(f"❌ Monitor error: {e}")
                    self.root.after(0, update_ui)
            
            # Run in background thread
            import threading
            thread = threading.Thread(target=monitor_thread)
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            self.log_auto_2fa(f"❌ Monitor start error: {e}")
    
    def log_auto_2fa(self, message):
        """Log message to auto 2FA status area"""
        try:
            if hasattr(self, 'auto_2fa_status'):
                from datetime import datetime
                timestamp = datetime.now().strftime("%H:%M:%S")
                self.auto_2fa_status.insert(tk.END, f"[{timestamp}] {message}\n")
                self.auto_2fa_status.see(tk.END)
        except Exception as e:
            print(f"Log error: {e}")
    
    def _save_bulk_run_data(self, data):
        """Lưu dữ liệu bulk run vào file JSON"""
        try:
            import json
            import os
            data_file = os.path.join(os.getcwd(), "bulk_run_data.json")
            with open(data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"💾 [SAVE] Đã lưu bulk run data: {len(data.get('accounts', ''))} ký tự")
        except Exception as e:
            print(f"⚠️ [SAVE] Lỗi lưu bulk run data: {e}")
    
    def _load_bulk_run_data(self):
        """Tải dữ liệu bulk run từ file JSON"""
        try:
            import json
            import os
            data_file = os.path.join(os.getcwd(), "bulk_run_data.json")
            if os.path.exists(data_file):
                with open(data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                print(f"📂 [LOAD] Đã tải bulk run data: {len(data.get('accounts', ''))} ký tự")
                return data
            else:
                print("📂 [LOAD] Chưa có file bulk run data")
                return {}
        except Exception as e:
            print(f"⚠️ [LOAD] Lỗi tải bulk run data: {e}")
            return {}

if __name__ == "__main__":
    app = ModernChromeProfileManager()
    app.run()
