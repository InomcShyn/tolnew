@echo off
chcp 65001 >nul
echo.
echo ================================================================================
echo COMPLETE CHROME 119 DOWNGRADE - PREVENT PROFILE MIGRATION
echo ================================================================================
echo.
echo This will patch 4 files per profile:
echo   1. profile_settings.json
echo   2. Local State (Chrome ROOT)
echo   3. Preferences
echo   4. Secure Preferences
echo.
echo Result:
echo   ✅ Chrome 119 launches normally
echo   ✅ TikTok login preserved
echo   ✅ NO profile migration
echo.
pause

python downgrade_chrome_119_complete.py

echo.
pause
