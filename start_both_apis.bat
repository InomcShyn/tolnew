@echo off
echo ========================================
echo Starting TikTok LIVE APIs
echo ========================================
echo.
echo Starting Metrics API (Port 8000)...
start "Metrics API" cmd /k python live_metrics_internal_api.py
timeout /t 3 /nobreak >nul
echo.
echo Starting Control API (Port 8001)...
start "Control API" cmd /k python live_control_api.py
echo.
echo ========================================
echo Both APIs started!
echo ========================================
echo.
echo Metrics API: http://127.0.0.1:8000
echo Control API: http://127.0.0.1:8001
echo.
echo Close the terminal windows to stop
echo ========================================
pause
