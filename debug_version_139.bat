@echo off
chcp 65001 >nul
echo.
echo ================================================================================
echo TÌM LỖI: TẠI SAO CHROME VẪN LÀ 139 THAY VÌ 119?
echo ================================================================================
echo.
echo Tool này sẽ trace TỪNG BƯỚC để tìm lỗi
echo.
pause

python trace_version_detailed.py

echo.
echo ================================================================================
echo TRACE HOÀN TẤT
echo ================================================================================
echo.
echo Log file đã được tạo. Đọc file để xem chi tiết.
echo.
echo Tiếp theo:
echo 1. Đọc recommendations trong log file
echo 2. Fix theo hướng dẫn
echo 3. Restart app: restart_app.bat
echo 4. Test: python simple_profile_start.py
echo.
pause
