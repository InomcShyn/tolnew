# 📚 Tài liệu Hướng dẫn Sử dụng Chrome Profile Manager

## 📋 Mục lục
1. [Giới thiệu](#giới-thiệu)
2. [Cài đặt](#cài-đặt)
3. [Khởi động](#khởi-động)
4. [Quản lý Profiles](#quản-lý-profiles)
5. [Quản lý Extension](#quản-lý-extension)
6. [Cấu hình Proxy](#cấu-hình-proxy)
7. [OMOcaptcha - Giải Captcha Tự động](#omocaptcha---giải-captcha-tự-động)
8. [Microsoft Graph 2FA - Lấy mã xác thực từ Email](#microsoft-graph-2fa---lấy-mã-xác-thực-từ-email)
9. [Chạy Hàng loạt (Bulk Run)](#chạy-hàng-loạt-bulk-run)
10. [Tối ưu Chrome cho Bulk Operations](#tối-ưu-chrome-cho-bulk-operations)
11. [Cấu trúc Dự án](#cấu-trúc-dự-án)
12. [Troubleshooting](#troubleshooting)

---

## 🌟 Giới thiệu

**Chrome Profile Manager** là công cụ quản lý và tự động hóa Chrome profiles với các tính năng:

- ✅ **Tạo và quản lý Chrome profiles**: Tạo hàng loạt profiles độc lập
- ✅ **Cài đặt Extension tự động**: Quản lý extensions qua GUI, cài đặt cho nhiều profiles cùng lúc
- ✅ **Cấu hình Proxy**: Thiết lập proxy riêng cho từng profile
- ✅ **Tự động đăng nhập**: Đăng nhập TikTok với captcha solver và 2FA
- ✅ **Bulk Operations**: Chạy hàng loạt với tối ưu RAM/CPU
- ✅ **Chạy ẩn (Headless)**: Chạy Chrome ở chế độ ẩn để tiết kiệm tài nguyên

---

## 🔧 Cài đặt

### 1. Cài đặt Python dependencies

```bash
pip install -r core/requirements.txt
```

### 2. Cấu trúc thư mục

Tool tự động tạo các thư mục sau:
- `chrome_profiles/` - Nơi lưu tất cả Chrome profiles
- `chrome_data/` - Chrome User Data riêng (tránh xung đột với Chrome cá nhân)
- `extensions/` - Thư mục chứa extensions local
- `config/` - File cấu hình

---

## 🚀 Khởi động

### Khởi động GUI

```bash
python launcher.py
```

Hoặc:

```bash
python core/gui_manager_modern.py
```

---

## 👥 Quản lý Profiles

### Tạo Profile đơn lẻ

1. Click tab **"Profiles"**
2. Click **"Tạo Profile Mới"**
3. Nhập tên profile (ví dụ: `P-136960-0004`)
4. Chọn profile gốc (mặc định: `Default`)
5. Click **"Tạo Profile"**

### Tạo Profiles hàng loạt

1. Nhập **prefix** (ví dụ: `Account`)
2. Nhập **số lượng** (ví dụ: `10`)
3. Chọn **version format**: `P-XXXXXX-XXXX` hoặc random
4. Nhập danh sách **proxy** (mỗi dòng một proxy, format: `IP:Port:User:Pass`)
5. Tùy chọn:
   - ✅ **Random Hardware**: Random hardware fingerprint
   - ✅ **Random User Agent**: Random user agent
6. Click **"Tạo Profiles"**

**Kết quả**: Tạo 10 profiles: `Account1`, `Account2`, ..., `Account10`

### Xóa Profile

1. Chuột phải vào profile trong danh sách
2. Chọn **"Xóa Profile"**

### Khởi động Profile

**Các cách khởi động:**
- **Chuột phải → "Khởi động (Hiển thị)"**: Chrome hiển thị cửa sổ
- **Chuột phải → "Khởi động (Ẩn)"**: Chrome chạy ẩn (headless)
- **Chuột phải → "Khởi động (Mặc định)"**: Sử dụng cài đặt checkbox "Chế độ ẩn"

**Khởi động hàng loạt:**
- Click **"Khởi động tất cả"** - Khởi động tất cả profiles
- Click **"Dừng tất cả"** - Dừng tất cả profiles đang chạy

---

## 🔌 Quản lý Extension

### Cài đặt Extension (Modern Mode)

1. Click tab **"Extensions"**
2. Chọn **"Modern Mode"**
3. Click **"Chọn Folder Chrome Profile"** → Chọn profile nguồn (có extension sẵn)
4. Hệ thống tự động load danh sách extensions từ profile đó
5. **Bên trái**: Danh sách extensions (có checkbox)
6. **Bên phải**: Danh sách profiles đích (có checkbox)
7. Tick chọn extensions và profiles muốn cài
8. Click **"Cài đặt Extension"**

**Tính năng:**
- ✅ **Select All Extensions**: Chọn tất cả extensions
- ✅ **Select All Profiles**: Chọn tất cả profiles
- ✅ Hiển thị tên, ID, version, trạng thái (enabled/disabled) của extension
- ✅ Tự động enable extension sau khi cài

### Cài đặt Extension tùy chỉnh

1. Click **"Cài đặt Extension tùy chỉnh"**
2. Nhập **Extension ID** (ví dụ: `pfnededegaaopdmhkdmcofjmoldfiped`)
3. Nhập **Extension Name** (tùy chọn)
4. Chọn **Profile** (None = cài cho tất cả profiles)
5. Click **"Cài đặt"**

**3 phương pháp cài đặt (tự động fallback):**
- **Method 1: Direct Copy** - Copy từ local folder (`extensions/{extension_name}/`)
- **Method 2: Chrome WebStore** - Tự động cài từ Chrome Web Store qua Selenium
- **Method 3: CRX Download** - Tải CRX file và load unpacked

### Cài đặt Extension cho tất cả Profiles (Legacy Mode)

1. Chọn **"Legacy Mode"**
2. Click **"[LAUNCH] Install for All Profiles"**
3. Xác nhận cài đặt

**Lưu ý**: Legacy mode chỉ hỗ trợ Proxy SwitchyOmega extension.

---

## 🌐 Cấu hình Proxy

### Thiết lập Proxy qua GUI

1. Click tab **"📁 PAC Files"**
2. Click **"🔧 Input Proxy"**
3. Nhập **Proxy String** theo format: `server:port:username:password`
   - Ví dụ: `146.19.196.16:40742:dNMWW2VVxb:YySfhZZPYv`
   - Hoặc không có auth: `192.168.1.1:8080`
4. **Single Profile:**
   - Chọn profile từ dropdown
   - Click **"🧪 Test Proxy"** để kiểm tra
   - Click **"⚙️ Configure"** để áp dụng
5. **Bulk Configuration:**
   - Tick **"Apply to ALL profiles"**
   - Click **"⚙️ Configure"** để áp dụng cho tất cả profiles

### Thiết lập Proxy qua Context Menu

1. **Chuột phải vào profile** → **"Thiết lập Proxy"**
2. Nhập proxy theo định dạng:
   - `IP:Port:User:Pass` (VD: `127.0.0.1:8080:user:pass`)
   - `User:Pass@IP:Port` (VD: `user:pass@127.0.0.1:8080`)
   - `IP:Port` (VD: `127.0.0.1:8080`)
3. Chọn loại proxy: **HTTP/HTTPS/SOCKS4/SOCKS5**
4. Click **"🧪 Test Proxy"** (tùy chọn)
5. Click **"Lưu"**

### SwitchyOmega Integration

Tool tự động cấu hình **Proxy SwitchyOmega** extension khi thiết lập proxy:
- Tạo proxy profile trong SwitchyOmega
- Apply proxy settings cho tất cả protocols
- Tự động enable SwitchyOmega khi cần

---

## 🎯 OMOcaptcha - Giải Captcha Tự động

### ⚡ Cài đặt nhanh (5 phút)

#### Bước 1: Đăng ký OMOcaptcha
1. Truy cập: https://omocaptcha.com/
2. Đăng ký tài khoản
3. Nạp tối thiểu **$5** vào tài khoản
4. Copy **API Key** từ Dashboard

#### Bước 2: Cấu hình API Key
Mở file `config.ini`:

```ini
[CAPTCHA]
omocaptcha_api_key = YOUR_API_KEY_HERE  # ← Thay bằng API key thật của bạn
auto_solve_captcha = true
prefer_omocaptcha = true
```

#### Bước 3: Chạy thử
```bash
python launcher.py
```

**✅ Xong!** Tool sẽ tự động giải TikTok captcha khi đăng nhập.

### Các loại TikTok Captcha được hỗ trợ

| Loại | Mô tả | Giá |
|------|-------|-----|
| **TiktokRotateWebTask** | Xoay hình ảnh để đúng hướng | ~$0.01-0.03 |
| **TiktokSelectObjectWebTask** | Chọn 2 đối tượng trong câu hỏi | ~$0.01-0.03 |
| **Tiktok3DSelectObjectWebTask** | Chọn 2 đối tượng 3D | ~$0.01-0.03 |
| **TiktokSliderWebTask** | Kéo slider để khớp puzzle | ~$0.01-0.02 |

**Trung bình**: ~$0.02/captcha → 50 captchas = $1.00

### Tính năng

- ✅ **Auto-detect**: Tự động phát hiện loại captcha TikTok
- ✅ **Multiple types**: Hỗ trợ Rotate, Select Object, 3D, Slider
- ✅ **Fallback**: Tự động chuyển sang OpenCV nếu API lỗi
- ✅ **Fast solving**: Giải captcha trong 2-10 giây
- ✅ **High accuracy**: Độ chính xác ~95-98%

### Troubleshooting

**Lỗi: "errorId: 1" - Insufficient balance**
→ Nạp thêm tiền vào OMOcaptcha account

**Lỗi: "Time等待 so lon"**
→ Captcha phức tạp, tool sẽ tự động fallback về OpenCV

**OMOcaptcha không hoạt động**
→ Tool tự động fallback về OpenCV, không ảnh hưởng workflow

---

## 📧 Microsoft Graph 2FA - Lấy mã xác thực từ Email

### Tổng quan
Tính năng tự động lấy mã xác thực 2FA từ email Hotmail/Outlook thông qua Microsoft Graph API.

### Cách thiết lập

#### Phương pháp 1: Sử dụng Access Token (Đơn giản nhất)

1. **Lấy Access Token từ Microsoft Graph Explorer:**
   - Truy cập: https://developer.microsoft.com/en-us/graph/graph-explorer
   - Đăng nhập bằng tài khoản Microsoft
   - Chọn scope: `Mail.Read`
   - Click "Generate" để lấy access token
   - Copy access token

2. **Thiết lập Environment Variable:**
   ```bash
   # Windows PowerShell
   $env:MS_ACCESS_TOKEN="your_access_token_here"
   
   # Windows Command Prompt
   set MS_ACCESS_TOKEN=your_access_token_here
   ```

#### Phương pháp 2: Sử dụng Refresh Token + Client ID (Tự động hóa)

1. **Tạo Azure App Registration:**
   - Truy cập: https://portal.azure.com/#view/Microsoft_AAD_RegisteredApps/ApplicationsListBlade
   - Click "New registration"
   - Name: "TikTok 2FA Manager"
   - Account types: "Personal Microsoft accounts only"
   - Redirect URI: `http://localhost:8080`

2. **Cấu hình API Permissions:**
   - Vào "API permissions"
   - Add permission: "Microsoft Graph" > "Delegated permissions"
   - Chọn: `Mail.Read`, `User.Read`
   - Click "Grant admin consent"

3. **Lấy Client ID và Refresh Token:**
   ```bash
   python auth/get2fa/msgraph_reader.py --get-refresh-token --client-id YOUR_CLIENT_ID
   ```

4. **Thiết lập Environment Variables:**
   ```bash
   set MS_CLIENT_ID=your_client_id_here
   set MS_REFRESH_TOKEN=your_refresh_token_here
   ```

### Sử dụng trong Bulk Login

**Format dữ liệu tài khoản TikTok:**
```
username|password|hotmail_email|hotmail_password|ms_refresh_token|ms_client_id
```

**Ví dụ:**
```
tiktok_user123|password123|user@hotmail.com|hotmail_password|refresh_token_here|client_id_here
```

**Quy trình tự động:**
1. Nhập danh sách tài khoản vào Bulk Run với format trên
2. Chọn profiles muốn đăng nhập
3. Click "Bắt đầu" - hệ thống sẽ:
   - Mở Chrome profile
   - Điều hướng đến TikTok login
   - Nhập username/password
   - Khi cần 2FA, tự động:
     - Kết nối Microsoft Graph API
     - Tìm kiếm email từ TikTok
     - Lấy mã 6 chữ số
     - Nhập mã vào form
     - Hoàn thành đăng nhập

### Troubleshooting

**"Không có access token"**
→ Kiểm tra environment variable `MS_ACCESS_TOKEN`

**"Refresh token expired"**
→ Lấy refresh token mới từ Microsoft Graph Explorer

**"Không tìm thấy mã 2FA"**
→ Kiểm tra email có được gửi từ TikTok không, đảm bảo email chứa mã 6 chữ số

---

## 🚀 Chạy Hàng loạt (Bulk Run)

### Cách sử dụng

1. Click tab **"Bulk Run"** hoặc button **"Chạy hàng loạt"**
2. **Nhập URL**: URL đích (ví dụ: `https://www.tiktok.com/login`)
3. **Nhập danh sách tài khoản** (mỗi dòng một tài khoản):
   ```
   username1|password1
   username2|password2
   username3|password3
   ```
   
   **Hoặc với 2FA:**
   ```
   username1|password1|hotmail1@hotmail.com|hotmail_pass1|refresh_token1|client_id1
   username2|password2|hotmail2@hotmail.com|hotmail_pass2|refresh_token2|client_id2
   ```
4. **Nhập Delay**: Thời gian chờ giữa mỗi profile (giây)
5. **Nhập OMOcaptcha API Key**: API key để giải captcha tự động (tùy chọn)
6. **Chọn Profiles**: Tick chọn profiles muốn chạy
7. Click **"Bắt đầu"**

### Tính năng Bulk Run

- ✅ **Tự động đăng nhập**: Tự động nhập username/password
- ✅ **Giải captcha**: Sử dụng OMOcaptcha API nếu có
- ✅ **Lấy mã 2FA**: Tự động lấy mã từ email qua Microsoft Graph API
- ✅ **Chạy ẩn**: Có thể chạy ở chế độ ẩn để tiết kiệm RAM
- ✅ **Progress tracking**: Hiển thị tiến trình trong status area
- ✅ **Error handling**: Tự động skip profile lỗi, tiếp tục với profile khác

### Lưu ý

- Tool tự động lưu dữ liệu bulk run vào `config/bulk_run_data.json`
- Có thể load lại dữ liệu đã lưu bằng cách click **"Load"**
- Delay giữa các profiles giúp tránh rate limiting

---

## ⚡ Tối ưu Chrome cho Bulk Operations

### Các chế độ tối ưu

#### 1. Chế độ Tiêu chuẩn (Standard)
- **RAM sử dụng**: ~150-200MB/profile
- **Phù hợp**: 20-50 profiles
- **Tính năng**: Đầy đủ, ổn định

#### 2. Chế độ Tối ưu RAM (Optimized)
- **RAM sử dụng**: ~80-120MB/profile
- **Phù hợp**: 50-100 profiles
- **Tính năng**: Vô hiệu hóa một số tính năng không cần thiết

#### 3. Chế độ Siêu tiết kiệm (Ultra Low Memory)
- **RAM sử dụng**: ~50-80MB/profile
- **Phù hợp**: 100-200 profiles
- **Tính năng**: Tối thiểu, chỉ giữ lại chức năng cốt lõi

### Hiệu suất dự kiến

| Chế độ | RAM/Profile | Max Profiles (16GB) | Max Profiles (32GB) |
|--------|-------------|---------------------|---------------------|
| Standard | 150-200MB | 60-80 | 120-160 |
| Optimized | 80-120MB | 100-150 | 200-300 |
| Ultra Low | 50-80MB | 150-250 | 300-500 |

### Sử dụng

**Bulk Run với tối ưu tự động:**
- Chọn profiles trong Bulk Run
- Nhập danh sách tài khoản TikTok
- Click "Bắt đầu" - Hệ thống tự động sử dụng chế độ tối ưu

**Cấu hình thủ công:**
```python
success, driver = manager.launch_chrome_profile(
    profile_name="test_profile",
    hidden=True,
    optimized_mode=True,      # Bật chế độ tối ưu
    ultra_low_memory=True     # Bật chế độ siêu tiết kiệm
)
```

### Hệ thống yêu cầu

- **RAM tối thiểu**: 8GB (cho 50 profiles)
- **RAM khuyến nghị**: 16GB+ (cho 100+ profiles)
- **CPU**: Multi-core processor
- **Storage**: SSD (cho tốc độ I/O)

### Chrome Flags được áp dụng

**Memory Optimization:**
```bash
--memory-pressure-off
--max_old_space_size=512
--js-flags=--max-old-space-size=512
--aggressive-cache-discard
```

**Process Optimization:**
```bash
--single-process
--no-zygote
--disable-background-timer-throttling
```

**Media Optimization:**
```bash
--disable-audio-output
--disable-video
--mute-audio
```

---

## 📁 Cấu trúc Dự án

```
tolnew/
├── core/                          # Core application
│   ├── chrome_manager.py          # Main Chrome profile manager
│   ├── gui_manager_modern.py      # Modern GUI interface
│   ├── captcha_solver.py          # Captcha solver với OMOcaptcha
│   ├── omocaptcha_client.py       # OMOcaptcha API client
│   ├── native_omocaptcha_solver.py # Native OMOcaptcha integration
│   ├── requirements.txt           # Python dependencies
│   ├── config.ini                 # Main configuration file
│   └── tiles/                     # Modular tile functions
│       ├── tile_profile_management.py    # Profile creation logic
│       ├── tile_extension_management.py  # Extension installation logic
│       ├── tile_profile_path.py          # Profile path utilities
│       └── ...
│
├── launcher.py                    # Entry point (chỉ import và run)
│
├── chrome_profiles/               # Chrome profiles storage
│   └── P-XXXXXX-XXXX/            # Mỗi profile là một folder
│       └── Default/
│           ├── Extensions/       # Extensions của profile
│           ├── Preferences       # Chrome preferences
│           └── ...
│
├── chrome_data/                   # Chrome User Data riêng (tránh xung đột)
│   └── Local State
│
├── extensions/                    # Local extensions storage
│   ├── SwitchyOmega3_Real/      # Proxy switching extension
│   └── ProfileTitle_*/           # Profile title extensions
│
├── config/                        # Configuration files
│   ├── auto_2fa_config.json      # 2FA automation settings
│   ├── gpm_config.json           # GPM Login configuration
│   ├── bulk_run_data.json        # Bulk run data storage
│   └── ms_token_*.json           # Microsoft Graph tokens
│
├── auth/                          # Authentication modules
│   └── get2fa/
│       ├── msgraph_reader.py     # Microsoft Graph API reader
│       └── requirements.txt      # 2FA module dependencies
│
├── tools/                         # Utility tools
│   ├── convert_gpm_to_nkt.py     # GPM to NKT conversion tool
│   └── ...
│
├── network/                       # Network configuration
│   └── pac_files/                # Proxy Auto-Configuration files
│
├── backups/                       # Backup files
│
└── config.ini                     # Main configuration file (root)
```

### File cấu hình (config.ini)

```ini
[SETTINGS]
auto_start = false
hidden_mode = true
max_profiles = 10
startup_delay = 5

[CAPTCHA]
omocaptcha_api_key = YOUR_API_KEY_HERE
auto_solve_captcha = true
prefer_omocaptcha = true

[PROFILES]
Profile1 = C:\path\to\chrome_profiles\Profile1
Profile2 = C:\path\to\chrome_profiles\Profile2

[LOGIN_DATA]
Profile1 = {"login_url": "https://accounts.google.com", "email": "user1@gmail.com", "password": "password1"}

[PROXY_SETTINGS]
Profile1 = http://127.0.0.1:8080
Profile2 = socks5://user:pass@proxy.example.com:1080
```

---

## 🔍 Troubleshooting

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

### Extension không xuất hiện sau khi cài

1. Kiểm tra extension folder có trong `{profile_path}/Default/Extensions/{extension_id}/`
2. Kiểm tra file `Preferences` có chứa extension settings không
3. Restart Chrome và kiểm tra lại

### RAM cao khi chạy nhiều profiles

- Sử dụng chế độ **Optimized** hoặc **Ultra Low Memory**
- Tăng delay giữa các profiles
- Giảm số lượng profiles đồng thời
- Hệ thống tự động cleanup mỗi 10 profiles

### OMOcaptcha không hoạt động

1. Kiểm tra API key có đúng không trong `config.ini`
2. Kiểm tra số dư OMOcaptcha account
3. Kiểm tra kết nối internet
4. Tool sẽ tự động fallback về OpenCV nếu API lỗi

### Microsoft Graph 2FA không hoạt động

1. Kiểm tra environment variables (`MS_ACCESS_TOKEN` hoặc `MS_REFRESH_TOKEN`)
2. Kiểm tra Azure App permissions (`Mail.Read`)
3. Kiểm tra email có được gửi từ TikTok không
4. Xem log chi tiết trong console

### Profile được lưu vào Chrome User Data mặc định

**Đã sửa**: Code hiện tại chỉ lưu profiles vào `chrome_profiles/`, không còn lưu vào Chrome User Data mặc định.

Nếu vẫn thấy profile trong Chrome User Data mặc định:
- Có thể do profile được tạo trước khi sửa code
- Có thể xóa thủ công nếu không cần

---

## 📝 Lưu ý Bảo mật

⚠️ **Lưu ý quan trọng:**
- Mật khẩu được lưu dạng plain text trong `config.ini` và `bulk_run_data.json`
- Chỉ sử dụng trên máy tính cá nhân
- Không chia sẻ file cấu hình
- Sử dụng mật khẩu ứng dụng thay vì mật khẩu chính khi có thể
- API keys (OMOcaptcha, Microsoft Graph) là thông tin nhạy cảm, không commit vào Git

---

## 🎉 Kết luận

Tool này cung cấp đầy đủ tính năng để quản lý Chrome profiles, tự động hóa đăng nhập, và chạy hàng loạt với tối ưu hiệu suất. 

**Nếu gặp vấn đề:**
1. Kiểm tra log chi tiết trong console
2. Kiểm tra file cấu hình (`config.ini`)
3. Đảm bảo Python version >= 3.7
4. Đảm bảo Chrome browser đã cài đặt
5. Kiểm tra quyền Administrator (cho một số tính năng)

**Happy Automation! 🚀**

