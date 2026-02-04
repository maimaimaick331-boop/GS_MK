@echo off
chcp 65001 >nul
REM Start script for Gold and Silver Data Analysis Platform

echo ============================================
echo Gold and Silver Market Data Analysis Platform
echo ============================================
echo.

REM Check Python installation
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error: Python not found. Please install Python first.
    pause
    exit /b 1
)

REM Enter backend directory
echo [1/4] Entering backend directory...
cd backend

REM Install dependencies
echo [2/4] Installing Python dependencies...
pip install -r requirements.txt -q

REM Initialize database
echo [3/4] Initializing database...
python models.py

REM Start Flask application
echo [4/4] Starting Flask API Server (http://localhost:5000)...
echo.
echo Flask server started successfully!
echo.
echo Run in another terminal window:
echo   cd frontend
echo   python -m http.server 8000
echo.
echo Then visit in browser: http://localhost:8000
echo.

python app.py

pause
