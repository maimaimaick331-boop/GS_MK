@echo off
chcp 65001 >nul
REM Frontend server startup script

echo Starting frontend server...
echo Access address: http://localhost:8000
echo.

cd frontend

REM Try to start Python HTTP server
python -m http.server 8000

if %ERRORLEVEL% NEQ 0 (
    echo Python HTTP server startup failed
    pause
    exit /b 1
)

pause
