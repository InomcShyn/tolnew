@echo off
echo ========================================
echo    XEM KET QUA TEST CAPTCHA 3D
echo ========================================
echo.

cd captcha_test_results

echo Mo anh ket qua...
echo.

REM Tim file anh moi nhat
for /f "delims=" %%i in ('dir /b /od captcha_solution_*.png') do set LATEST=%%i

if "%LATEST%"=="" (
    echo Khong tim thay file ket qua!
    echo Hay chay: python test_3d_captcha_visual.py
    pause
    exit /b
)

echo File moi nhat: %LATEST%
echo.
echo Dang mo anh...
start %LATEST%

echo.
echo ========================================
echo HUONG DAN XEM:
echo ========================================
echo.
echo - Vong tron DO (A): Diem click thu nhat
echo - Vong tron XANH (B): Diem click thu hai
echo.
echo Kiem tra xem 2 diem co tro vao 2 vat the
echo CUNG HINH DANG khong?
echo.
echo Neu DUNG: API hoat dong tot!
echo Neu SAI: API tra ve sai, can thu lai
echo.
echo ========================================

cd ..
pause
