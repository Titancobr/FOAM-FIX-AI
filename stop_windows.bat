@echo off
echo ========================================================
echo         Stopping FORM-FIX AI Trainer Containers
echo ========================================================
echo.

docker compose down

echo.
echo [OK] All FormFix containers have been cleanly stopped.
echo Your workout data and progress have been saved in the Docker volume.
echo.
pause
