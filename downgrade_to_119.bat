@echo off
chcp 65001 >nul
echo.
echo ╔══════════════════════════════════════════════════════════════════╗
echo ║  🔽 DOWNGRADE CHROME VERSION: 139 → 119                         ║
echo ╚══════════════════════════════════════════════════════════════════╝
echo.
echo Chọn phương án:
echo.
echo   1. Quick Downgrade (Nhanh - Tự động tất cả)
echo   2. Interactive Tool (Linh hoạt - Có menu)
echo   3. Kiểm tra version hiện tại
echo   4. Thoát
echo.
set /p choice="Chọn (1-4): "

if "%choice%"=="1" (
    echo.
    echo ⚡ Chạy Quick Downgrade...
    echo.
    python quick_downgrade_to_119.py
    goto end
)

if "%choice%"=="2" (
    echo.
    echo 🎯 Chạy Interactive Tool...
    echo.
    python downgrade_chrome_version.py
    goto end
)

if "%choice%"=="3" (
    echo.
    echo 🔍 Kiểm tra version...
    echo.
    python -c "from downgrade_chrome_version import check_profile_versions; check_profile_versions()"
    goto end
)

if "%choice%"=="4" (
    echo.
    echo 👋 Tạm biệt!
    goto end
)

echo.
echo ❌ Lựa chọn không hợp lệ!

:end
echo.
pause
