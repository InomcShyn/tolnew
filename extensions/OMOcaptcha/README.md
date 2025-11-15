# OMOcaptcha Extension

Extension OMOcaptcha đã được extract từ profile P-419619-0001.

## Thông tin Extension

- **Extension ID**: `dfjghhjachoacpgpkmbpdlpppeagojhe`
- **Version**: 1.3.1
- **Name**: OMOcaptcha: Auto solve captcha
- **Description**: OMOcaptcha: Auto solve captcha

## Cấu trúc Extension

Extension này hỗ trợ giải nhiều loại captcha:
- reCAPTCHA v2
- hCaptcha
- FunCaptcha
- Geetest
- Shopee captcha
- TikTok captcha
- Zalo captcha
- Discord captcha
- Amazon captcha
- Image to Text
- Slide captcha

## Cách sử dụng

### 1. Tự động cài khi chạy hàng loạt

Extension này sẽ tự động được cài đặt khi:
- Sử dụng chức năng "Test cài OMOcaptcha + lưu API key"
- Chạy hàng loạt với OMOcaptcha được bật
- Sử dụng `install_omocaptcha_extension_local()` function

### 2. Extract từ profile khác

Nếu muốn extract extension từ profile khác:

```bash
python tools/extract_omocaptcha_from_profile.py <profile_name>
```

Ví dụ:
```bash
python tools/extract_omocaptcha_from_profile.py P-419619-0001
```

### 3. Vị trí Extension

Extension được lưu tại:
- `extensions/OMOcaptcha/` (tên thư mục)
- `extensions/dfjghhjachoacpgpkmbpdlpppeagojhe/` (theo extension ID)
- `extensions/omocaptcha/` (tên viết thường)

Hệ thống sẽ tự động tìm extension trong các thư mục này.

## Lưu ý

1. Extension này cần API key để hoạt động
2. API key sẽ được lưu vào `config.ini` trong section `[CAPTCHA]`
3. Khi cài extension, hệ thống sẽ tự động inject API key vào extension storage

## Files quan trọng

- `manifest.json`: Thông tin extension và cấu hình
- `contents/`: Các script xử lý captcha
- `icons/`: Icons của extension
- `configs.json`: Cấu hình extension

