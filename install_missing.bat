@echo off
chcp 65001 >nul
echo.
echo ╔══════════════════════════════════════════════════════════════════╗
echo ║  📦 INSTALL MISSING PACKAGES                                    ║
echo ╚══════════════════════════════════════════════════════════════════╝
echo.
echo Installing missing packages...
echo.

REM Install nest-asyncio
echo [1/3] Installing nest-asyncio...
pip install nest-asyncio==1.6.0
echo.

REM Install playwright
echo [2/3] Installing playwright...
pip install playwright==1.40.0
echo.

REM Install pyperclip
echo [3/3] Installing pyperclip...
pip install pyperclip==1.8.2
echo.

REM Install playwright browsers
echo ╔══════════════════════════════════════════════════════════════════╗
echo ║  🎭 Installing Playwright Browsers                              ║
echo ╚══════════════════════════════════════════════════════════════════╝
echo.
echo This may take a few minutes...
echo.
playwright install chromium
echo.

echo ╔══════════════════════════════════════════════════════════════════╗
echo ║  ✅ INSTALLATION COMPLETE                                       ║
echo ╚══════════════════════════════════════════════════════════════════╝
echo.
pause
