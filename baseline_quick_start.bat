@echo off
REM Quick start for baseline collection
REM Run this to start interactive guide

echo ========================================================================
echo BASELINE COLLECTION - QUICK START
echo ========================================================================
echo.
echo This will start the interactive baseline collection guide.
echo.
echo REQUIREMENTS:
echo   - Profile already logged into TikTok
echo   - Know a TikTok username that is currently LIVE
echo   - launcher.py ready to run
echo.
echo PROCESS:
echo   1. This script will guide you through each stage
echo   2. You will manually operate the browser
echo   3. Data will be collected at each stage
echo   4. Results saved to baseline_data/ folder
echo.
pause

python baseline_manual_guide.py

echo.
echo ========================================================================
echo BASELINE COLLECTION COMPLETE
echo ========================================================================
echo.
echo Next steps:
echo   1. Review data in baseline_data/ folder
echo   2. Run another session with different settings
echo   3. Compare sessions: python baseline_compare.py session1 session2
echo.
pause
