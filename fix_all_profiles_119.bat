@echo off
chcp 65001 >nul
echo.
echo ================================================================================
echo COMPLETE BULK CHROME 119 DOWNGRADE - ALL PROFILES
echo ================================================================================
echo.
echo This will downgrade ALL profiles from Chrome 139 to 119
echo while preserving TikTok login sessions.
echo.
echo Press Ctrl+C to cancel, or
pause
echo.

python fix_all_profiles_119_complete.py

echo.
pause
