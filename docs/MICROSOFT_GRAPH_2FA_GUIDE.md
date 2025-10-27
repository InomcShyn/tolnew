# Hướng dẫn sử dụng Microsoft Graph API cho 2FA TikTok

## Tổng quan
Tính năng này cho phép tự động lấy mã xác thực 2FA từ email Hotmail/Outlook thông qua Microsoft Graph API, giúp tự động hóa quá trình đăng nhập TikTok hàng loạt.

## Cách thiết lập

### Phương pháp 1: Sử dụng Access Token (Đơn giản nhất)

1. **Lấy Access Token từ Microsoft Graph Explorer:**
   - Truy cập: https://developer.microsoft.com/en-us/graph/graph-explorer
   - Đăng nhập bằng tài khoản Microsoft của bạn
   - Chọn scope: `Mail.Read`
   - Click "Generate" để lấy access token
   - Copy access token

2. **Thiết lập Environment Variable:**
   ```bash
   # Windows PowerShell
   $env:MS_ACCESS_TOKEN="your_access_token_here"
   
   # Windows Command Prompt
   set MS_ACCESS_TOKEN=your_access_token_here
   
   # Linux/Mac
   export MS_ACCESS_TOKEN="your_access_token_here"
   ```

### Phương pháp 2: Sử dụng Refresh Token + Client ID (Tự động hóa)

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

3. **Lấy Client ID:**
   - Copy "Application (client) ID" từ Overview

4. **Lấy Refresh Token:**
   ```python
   # Chạy script này để lấy refresh token
   python get2fa/msgraph_reader.py --get-refresh-token --client-id YOUR_CLIENT_ID
   ```

5. **Thiết lập Environment Variables:**
   ```bash
   set MS_CLIENT_ID=your_client_id_here
   set MS_REFRESH_TOKEN=your_refresh_token_here
   ```

## Cách sử dụng trong Bulk Login

### Format dữ liệu tài khoản TikTok

Sử dụng format pipe-separated với thông tin Microsoft Graph:

```
username|password|hotmail_email|hotmail_password|ms_refresh_token|ms_client_id
```

**Ví dụ:**
```
tiktok_user123|password123|user@hotmail.com|hotmail_password|refresh_token_here|client_id_here
```

### Quy trình tự động

1. **Nhập danh sách tài khoản** vào Bulk Run với format trên
2. **Chọn profiles** muốn đăng nhập
3. **Click "Bắt đầu"** - hệ thống sẽ:
   - Mở Chrome profile
   - Điều hướng đến TikTok login
   - Nhập username/password
   - Khi cần 2FA, tự động:
     - Kết nối Microsoft Graph API
     - Tìm kiếm email từ TikTok
     - Lấy mã 6 chữ số
     - Nhập mã vào form
     - Hoàn thành đăng nhập

## Tính năng tìm kiếm email

Hệ thống sẽ tìm kiếm email với các từ khóa:
- `from:tik tok OR from:"no-reply@account.tiktok.com" OR subject: TikTok`
- `subject: verification OR subject: code OR subject: "security code"`
- `from:security@outlook.com OR from:noreply@outlook.com`

## Xử lý lỗi

### Lỗi thường gặp:

1. **"Không có access token"**
   - Kiểm tra environment variable `MS_ACCESS_TOKEN`
   - Hoặc cung cấp `ms_refresh_token` và `ms_client_id` trong dữ liệu tài khoản

2. **"Refresh token expired"**
   - Lấy refresh token mới từ Microsoft Graph Explorer
   - Hoặc sử dụng access token trực tiếp

3. **"Không tìm thấy mã 2FA"**
   - Kiểm tra email có được gửi từ TikTok không
   - Đảm bảo email chứa mã 6 chữ số
   - Kiểm tra quyền `Mail.Read` trong Azure App

## Log và Debug

Hệ thống sẽ hiển thị log chi tiết:
```
🔍 [GRAPH] Đang tìm mã 2FA từ Hotmail...
📧 [GRAPH] Email: user@hotmail.com
🔑 [GRAPH] Sử dụng access token từ environment
🔍 [GRAPH] Tìm kiếm: from:tik tok OR from:"no-reply@account.tiktok.com" OR subject: TikTok
📬 [GRAPH] Tìm thấy 3 email(s)
📧 [GRAPH] Email từ: no-reply@account.tiktok.com
📧 [GRAPH] Tiêu đề: Your TikTok verification code
✅ [GRAPH] Tìm thấy mã 2FA: 123456
```

## Lưu ý bảo mật

- **Không chia sẻ** access token hoặc refresh token
- **Sử dụng HTTPS** khi truyền dữ liệu
- **Xóa token** sau khi sử dụng xong
- **Giới hạn quyền** chỉ cần thiết (`Mail.Read`)

## Troubleshooting

### Test Microsoft Graph API:
```python
# Test kết nối
python get2fa/msgraph_reader.py --top 5 --search "from:tik tok"
```

### Kiểm tra permissions:
- Đảm bảo Azure App có quyền `Mail.Read`
- Kiểm tra admin consent đã được grant

### Debug email search:
- Kiểm tra email có thực sự được gửi từ TikTok
- Xem log để biết từ khóa tìm kiếm nào được sử dụng
- Kiểm tra format mã 2FA (phải là 6 chữ số)

## Hỗ trợ

Nếu gặp vấn đề:
1. Kiểm tra log chi tiết trong console
2. Test Microsoft Graph API riêng biệt
3. Kiểm tra permissions và tokens
4. Đảm bảo email TikTok có mã 6 chữ số
