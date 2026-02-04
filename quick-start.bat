@echo off
chcp 65001 >nul
REM Simplified startup - No external dependencies required

echo ============================================
echo Gold and Silver Market Data Analysis Platform
echo Quick Start Version
echo ============================================
echo.

REM Check Python installation
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error: Python not found. Please install Python 3.7+
    pause
    exit /b 1
)

echo [1/2] Starting API Server (standard library version)...
echo Server will run on: http://localhost:5000
echo.

cd backend

python simple_server.py

pause