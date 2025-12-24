@echo off
REM Quick Test - Chạy browser diagnostics nhanh

echo ========================================
echo QUICK BROWSER DIAGNOSTICS TEST
echo ========================================
echo.

REM Get profile name from argument or use default
set PROFILE=%1
if "%PROFILE%"=="" set PROFILE=X-001

echo Testing profile: %PROFILE%
echo.

python test_browser_diagnostics.py %PROFILE%

echo.
echo ========================================
echo Test completed!
echo ========================================
pause
