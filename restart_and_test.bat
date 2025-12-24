@echo off
echo ========================================
echo RESTARTING APP TO CLEAR PYTHON CACHE
echo ========================================
echo.

REM Kill all Python processes
echo Killing Python processes...
taskkill /F /IM python.exe /T 2>nul
taskkill /F /IM pythonw.exe /T 2>nul
timeout /t 2 /nobreak >nul

echo.
echo ========================================
echo TESTING CAPTCHA DETECTION
echo ========================================
echo.

REM Test with fresh import
python test_fresh_import.py

echo.
echo ========================================
echo DONE! Now you can run bulk_run again
echo ========================================
pause
