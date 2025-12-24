@echo off
chcp 65001 >nul
echo.
echo ================================================================================
echo SAFE CHROME 119 DOWNGRADE - PRESERVE TIKTOK LOGIN
echo ================================================================================
echo.
echo This script will:
echo   ✅ Create automatic backups of critical files
echo   ✅ Fix ALL profiles to Chrome 119
echo   ✅ PRESERVE TikTok login (cookies/sessions untouched)
echo   ✅ Validate no forbidden fields are modified
echo.
pause

python fix_all_profiles_119_safe.py

echo.
pause
