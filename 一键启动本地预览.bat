@echo off
setlocal
chcp 65001 >nul
title "Gold & Silver Monitor - One Click Start (V2.0)"
cd /d "%~dp0."

if /i "%1"=="--check" goto check

echo ==========================================
echo    Gold & Silver Monitor - Local Start
echo ==========================================
echo.

:check
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python and add it to PATH.
    if /i "%1"=="--check" exit /b 1
    pause
    exit /b 1
)
if /i "%1"=="--check" exit /b 0

echo [1/2] Starting backend API (Port: 5000)...
start "" /b cmd /c "python backend/app.py"

timeout /t 3 /nobreak >nul

echo [2/2] Starting frontend server (Port: 8000)...
echo Opening: http://localhost:8000/index.html
start "" /b cmd /c "python -m http.server 8000 --directory frontend"

timeout /t 1 /nobreak >nul
start "" "http://localhost:8000/index.html"

echo.
echo ==========================================
echo    Startup complete
echo    - Frontend: http://localhost:8000
echo    - Backend:  http://localhost:5000
echo    Keep this window open to keep services running.
echo ==========================================
echo.
pause
