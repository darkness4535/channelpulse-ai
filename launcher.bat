@echo off
chcp 65001 >nul
cd /d "%~dp0"
title ChannelPulse AI

echo ========================================
echo   ChannelPulse AI - Launcher
echo ========================================
echo.

if not exist ".venv\Scripts\python.exe" (
  echo Creating virtual environment...
  python -m venv .venv
  if errorlevel 1 (
    echo Python not found. Install Python 3.10+ from python.org
    pause
    exit /b 1
  )
)

call ".venv\Scripts\activate.bat"

echo Installing dependencies...
pip install -q -r requirements.txt
if errorlevel 1 (
  echo pip install failed
  pause
  exit /b 1
)

if not exist ".env" (
  if exist ".env.example" copy ".env.example" ".env" >nul
  echo Created .env from .env.example
)

set COMPANY_AUTONOMOUS=1
set COMPANY_MOCK=1

echo.
echo Starting control panel: http://127.0.0.1:8765
echo Close this window to stop the server.
echo.

start "" "http://127.0.0.1:8765"

python -m uvicorn dashboard.app:app --host 127.0.0.1 --port 8765

pause
