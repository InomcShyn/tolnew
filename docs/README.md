# Chrome Profile Manager

Tool tự động nhân bản và quản lý Chrome profiles với khả năng chạy ẩn và tự động khởi động.

## Tính năng chính

- ✅ **Nhân bản Chrome profiles**: Tạo nhiều profile Chrome từ profile gốc
- ✅ **Đăng nhập tự động**: Tự động đăng nhập vào các tài khoản
- ✅ **Chạy ẩn**: Khởi động Chrome ở chế độ ẩn (headless)
- ✅ **Tự động khởi động**: Khởi động cùng Windows
- ✅ **Giao diện GUI**: Quản lý dễ dàng qua giao diện đồ họa
- ✅ **Quản lý profiles**: Tạo, xóa, khởi động/dừng profiles
- ✅ **Tối ưu hóa dữ liệu**: Giảm thiểu dữ liệu Chrome để tiết kiệm dung lượng
- ✅ **Tạo hàng loạt**: Tạo nhiều profiles cùng lúc với preview
- ✅ **Hỗ trợ Proxy**: Thiết lập proxy riêng cho từng profile với nhiều định dạng

## Cài đặt

### 1. Cài đặt Python dependencies

```bash
pip install -r requirements.txt
```

### 2. Cài đặt ChromeDriver

Tool sẽ tự động tải ChromeDriver khi chạy lần đầu.

## Sử dụng

### Khởi động GUI

```bash
python gui_manager.py
```

### Sử dụng từ command line

```bash
# Khởi động Chrome Profile Manager
python launcher.py

# Quản lý tự động khởi động
python auto_start.py
```

## Hướng dẫn sử dụng chi tiết

### 1. Tạo Profile mới

**Tạo profile đơn lẻ:**
1. Mở GUI (`python gui_manager.py`)
2. Click "Tạo Profile Mới"
3. Nhập tên profile (prefix)
4. Nhập số lượng profiles (mặc định: 1)
5. Chọn profile gốc (mặc định: Default)
6. Click "Tạo Profiles"

**Tạo nhiều profiles cùng lúc:**
1. Nhập prefix (ví dụ: "Account")
2. Nhập số lượng (ví dụ: 5)
3. Sẽ tạo: Account 1, Account 2, Account 3, Account 4, Account 5

**Tùy chọn nâng cao:**
- ✅ **Khởi động profiles sau khi tạo** - Tự động khởi động tất cả profiles vừa tạo
- ✅ **Khởi động ở chế độ ẩn** - Chrome chạy ẩn (headless)
- ✅ **Cấu hình đăng nhập cho tất cả profiles** - Thiết lập thông tin đăng nhập chung

**Preview:** Xem trước danh sách profiles sẽ được tạo

**Tối ưu hóa dữ liệu:**
- Tự động xóa cache, history, bookmarks không cần thiết
- Tắt images, JavaScript, CSS để giảm băng thông
- Tắt extensions, plugins, notifications
- Giảm kích thước cửa sổ Chrome
- Tối ưu hóa bộ nhớ và CPU

### 2. Cấu hình đăng nhập tự động

1. Chuột phải vào profile trong danh sách
2. Chọn "Cấu hình đăng nhập"
3. Nhập thông tin:
   - URL đăng nhập (mặc định: https://accounts.google.com)
   - Email
   - Mật khẩu
4. Click "Lưu"

### 3. Thiết lập Proxy

**Các định dạng proxy được hỗ trợ:**
- `IP:Port:User:Pass` (VD: 127.0.0.1:8080:user:pass)
- `User:Pass@IP:Port` (VD: user:pass@127.0.0.1:8080)
- `IP:Port` (VD: 127.0.0.1:8080)
- `Hostname:Port` (VD: proxy.example.com:3128)
- `User:Pass@Hostname:Port` (VD: user:pass@proxy.example.com:3128)

**Cách thiết lập:**
1. Chuột phải vào profile trong danh sách
2. Chọn "Thiết lập Proxy"
3. Nhập proxy theo định dạng đơn giản trong ô "Proxy"
4. Chọn loại proxy (HTTP/HTTPS/SOCKS4/SOCKS5)
5. Có thể test proxy trước khi lưu
6. Click "Lưu"

**Menu chuột phải cho Proxy:**
- **Thiết lập Proxy** - Cấu hình proxy mới
- **Xóa Proxy** - Xóa cấu hình proxy hiện tại
- **Test Proxy** - Kiểm tra kết nối proxy

**Cột Proxy:** Hiển thị thông tin proxy của từng profile trong danh sách

### 4. Khởi động Profile

**Các cách khởi động:**
- **Chuột phải vào profile:**
  - "Khởi động (Hiển thị)" - Chrome hiển thị cửa sổ
  - "Khởi động (Ẩn)" - Chrome chạy ẩn (headless)
  - "Khởi động (Mặc định)" - Sử dụng cài đặt checkbox "Chế độ ẩn"

**Khởi động hàng loạt:**
- Click "Khởi động tất cả" - Khởi động tất cả profiles cùng lúc
- Click "Dừng tất cả" - Dừng tất cả profiles đang chạy

**Checkbox "Chế độ ẩn":**
- Bật/tắt chế độ ẩn mặc định cho tất cả profiles
- Khi bật, tất cả profiles mới sẽ chạy ở chế độ ẩn
- Có thể override bằng menu chuột phải

**Proxy tự động:** Chrome sẽ tự động sử dụng proxy đã cấu hình khi khởi động

### 5. Tự động khởi động cùng Windows

1. Trong GUI, tick vào "Tự động khởi động"
2. Hoặc chạy: `python auto_start.py` và chọn option 1

### 6. Cài đặt

1. Click "Cài đặt" trong GUI
2. Cấu hình:
   - **Chế độ ẩn mặc định**: Bật/tắt chế độ ẩn
   - **Số profile tối đa**: Giới hạn số profiles
   - **Delay khởi động**: Thời gian chờ trước khi khởi động (giây)

## Cấu trúc thư mục

```
chrome_profile_manager/
├── core/chrome_manager.py      # Core logic quản lý profiles
├── gui_manager.py         # Giao diện GUI
├── auto_start.py          # Quản lý tự động khởi động
├── startup_launcher.py    # Script khởi động tự động
├── requirements.txt       # Dependencies
├── config.ini            # File cấu hình (tự tạo)
├── chrome_profiles/      # Thư mục chứa profiles (tự tạo)
└── README.md             # Hướng dẫn này
```

## File cấu hình (config.ini)

```ini
[SETTINGS]
auto_start = false
hidden_mode = true
max_profiles = 10
startup_delay = 5

[PROFILES]
Profile1 = C:\path\to\chrome_profiles\Profile1
Profile2 = C:\path\to\chrome_profiles\Profile2

[LOGIN_DATA]
Profile1 = {"login_url": "https://accounts.google.com", "email": "user1@gmail.com", "password": "password1"}

[PROXY_SETTINGS]
Profile1 = http://127.0.0.1:8080
Profile2 = socks5://user:pass@proxy.example.com:1080
```

## Troubleshooting

### Lỗi ChromeDriver

```bash
# Xóa cache và tải lại
pip uninstall webdriver-manager
pip install webdriver-manager
```

### Lỗi quyền truy cập

- Chạy Command Prompt với quyền Administrator
- Kiểm tra antivirus có chặn không

### Profile không khởi động được

1. Kiểm tra Chrome có đang chạy không
2. Đóng tất cả Chrome instances
3. Thử tạo profile mới

### Tự động khởi động không hoạt động

1. Kiểm tra trong Task Manager → Startup
2. Chạy lại `python auto_start.py` và chọn option 1
3. Kiểm tra Windows Defender có chặn không

## Bảo mật

⚠️ **Lưu ý quan trọng:**
- Mật khẩu được lưu dạng plain text trong config.ini
- Chỉ sử dụng trên máy tính cá nhân
- Không chia sẻ file config.ini
- Sử dụng mật khẩu ứng dụng thay vì mật khẩu chính

## Hỗ trợ

Nếu gặp vấn đề, hãy kiểm tra:
1. Python version >= 3.7
2. Chrome browser đã cài đặt
3. Kết nối internet (để tải ChromeDriver)
4. Quyền Administrator (cho tự động khởi động)

## License

MIT License - Sử dụng tự do cho mục đích cá nhân và thương mại.
