@echo off
chcp 65001 >nul
echo.
echo ================================================================================
echo XÓA LAST VERSION FILE - FORCE CODE ĐỌC TỪ PROFILE_SETTINGS.JSON
echo ================================================================================
echo.
echo Profile: P-434933-0299
echo File: chrome_profiles\P-434933-0299\Last Version
echo.
echo File này đang chứa: 139.0.7258.139
echo Cần xóa để force code đọc chrome_version: 119.0.6045.199
echo.
pause

if exist "chrome_profiles\P-434933-0299\Last Version" (
    del "chrome_profiles\P-434933-0299\Last Version"
    echo.
    echo ✅ Đã xóa Last Version file
    echo.
) else (
    echo.
    echo ⚠️  File không tồn tại
    echo.
)

echo ================================================================================
echo TIẾP THEO
echo ================================================================================
echo.
echo 1. Restart app: restart_app.bat
echo 2. Test launch: python simple_profile_start.py
echo.
echo Logs nên hiển thị:
echo [BROWSER] Profile requests Chrome version: 119.0.6045.199
echo [BROWSER] ✅ Using GPM Chrome: C:\Users\gpm_browser\gpm_browser_chromium_core_119\chrome.exe
echo.
pause
