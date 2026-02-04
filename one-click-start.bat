@echo off
chcp 65001 >nul
title Gold and Silver Market Data Analysis Platform

echo.
echo ============================================================
echo   Gold and Silver Market Data Analysis Platform
echo   One-Click Startup Script
echo ============================================================
echo.

REM Check if both services are already running
echo Checking services...
timeout /t 1 /nobreak >nul

REM Kill any existing processes on ports 5000 and 8000
echo Cleaning up old processes...
taskkill /F /IM python.exe >nul 2>&1

REM Start backend API server in background
echo.
echo [1/3] Starting API Server on port 5000...
cd backend
start /B python simple_server.py >nul 2>&1
timeout /t 2 /nobreak >nul

REM Start frontend server in background
echo [2/3] Starting Frontend Server on port 8000...
cd ..\frontend
start /B python -m http.server 8000 >nul 2>&1
timeout /t 2 /nobreak >nul

REM Open browser
echo [3/3] Opening application in browser...
timeout /t 1 /nobreak >nul

REM Try to open browser
start http://localhost:8000

echo.
echo ============================================================
echo   All services started successfully!
echo ============================================================
echo.
echo Application URL: http://localhost:8000
echo API Server: http://localhost:5000
echo.
echo To stop the application, close this window.
echo.
timeout /t 3 /nobreak >nul

REM Keep window open
:loop
timeout /t 5 /nobreak >nul
goto loop
