@echo off
setlocal enabledelayedexpansion

echo ========================================================
echo         FORM-FIX AI Pose Trainer - Windows Launcher
echo ========================================================
echo.

REM 1. Check if Docker is installed
where docker >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Docker was not found in your system PATH!
    echo Please install Docker Desktop for Windows:
    echo https://www.docker.com/products/docker-desktop/
    echo.
    pause
    exit /b 1
)

REM 2. Check if Docker Desktop engine is running
echo [*] Checking if Docker engine is running...
docker info >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [WARNING] Docker Desktop is installed but NOT currently running!
    echo.
    echo Please do the following:
    echo   1. Open "Docker Desktop" from your Windows Start Menu.
    echo   2. Wait until the whale icon in the bottom-right system tray shows "Engine running".
    echo   3. Run this script (run_windows.bat) again.
    echo.
    pause
    exit /b 1
)

echo [OK] Docker engine is running!
echo.
echo [*] Building and launching FormFix containers (Backend + Frontend)...
echo     (First run may take a couple of minutes to download base images and compile)
echo.

docker compose up --build -d

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Failed to start containers. Please check the logs above.
    pause
    exit /b 1
)

echo.
echo ========================================================
echo  [SUCCESS] FormFix AI Trainer is starting up!
echo ========================================================
echo.
echo  - Frontend Web App:  http://localhost:3000
echo  - Backend API:       http://localhost:8000
echo  - Interactive Docs:  http://localhost:8000/docs
echo.
echo [*] Waiting 5 seconds before opening browser...
timeout /t 5 /nobreak >nul

echo [*] Launching FormFix in your default web browser...
start http://localhost:3000

echo.
echo Cues for your friend:
echo  1. When your browser opens http://localhost:3000, allow camera access when prompted.
echo  2. If you don't have an account yet, click "Register" to create one.
echo  3. All trained AI models (.keras) are loaded and ready in the backend!
echo.
echo To STOP the application at any time, run: stop_windows.bat
echo or execute: docker compose down
echo.
pause
