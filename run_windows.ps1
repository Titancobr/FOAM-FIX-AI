# FormFix AI Trainer - Windows PowerShell Launcher
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "        FORM-FIX AI Pose Trainer - PowerShell Launcher" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

# Check Docker CLI
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "[ERROR] Docker CLI was not found in PATH." -ForegroundColor Red
    Write-Host "Please download and install Docker Desktop for Windows:"
    Write-Host "https://www.docker.com/products/docker-desktop/"
    Read-Host -Prompt "Press Enter to exit"
    exit 1
}

# Check Docker Engine
Write-Host "[*] Checking if Docker engine is running..." -ForegroundColor Yellow
$dockerInfo = docker info 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "[WARNING] Docker Desktop is installed but not running." -ForegroundColor Red
    Write-Host "Please launch Docker Desktop from the Start Menu, wait until the engine is running, and re-run this script."
    Read-Host -Prompt "Press Enter to exit"
    exit 1
}

Write-Host "[OK] Docker engine is active." -ForegroundColor Green
Write-Host "[*] Building and starting FormFix services (Backend + Frontend)..." -ForegroundColor Yellow

docker compose up --build -d

if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Failed to start Docker services." -ForegroundColor Red
    Read-Host -Prompt "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "========================================================" -ForegroundColor Green
Write-Host " [SUCCESS] FormFix AI Trainer is running!" -ForegroundColor Green
Write-Host "========================================================" -ForegroundColor Green
Write-Host " - Frontend Web App:  http://localhost:3000" -ForegroundColor White
Write-Host " - Backend API:       http://localhost:8000" -ForegroundColor White
Write-Host " - Interactive Docs:  http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "[*] Waiting 5 seconds before launching browser..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

Start-Process "http://localhost:3000"

Write-Host ""
Write-Host "To stop FormFix, run: docker compose down" -ForegroundColor Cyan
Write-Host ""
Read-Host -Prompt "Press Enter to close this window"
