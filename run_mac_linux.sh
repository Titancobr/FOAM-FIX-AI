#!/usr/bin/env bash
set -e

echo "========================================================"
echo "    FORM-FIX AI Pose Trainer - Mac / Linux Launcher"
echo "========================================================"
echo ""

# Check Docker CLI
if ! command -v docker &> /dev/null; then
    echo "[ERROR] Docker is not installed or not in PATH."
    echo "Please install Docker from https://www.docker.com/"
    exit 1
fi

# Check Docker Engine
echo "[*] Checking Docker daemon status..."
if ! docker info &> /dev/null; then
    echo "[WARNING] Docker daemon is not running."
    echo "Please start Docker Desktop / daemon and re-run this script."
    exit 1
fi

echo "[OK] Docker daemon is active."
echo "[*] Building and starting FormFix containers..."
docker compose up --build -d

echo ""
echo "========================================================"
echo " [SUCCESS] FormFix AI Trainer is running!"
echo "========================================================"
echo " - Frontend Web App:  http://localhost:3000"
echo " - Backend API:       http://localhost:8000"
echo " - Interactive Docs:  http://localhost:8000/docs"
echo ""

# Open browser based on OS
sleep 4
if [[ "$OSTYPE" == "darwin"* ]]; then
    open "http://localhost:3000" || true
elif command -v xdg-open &> /dev/null; then
    xdg-open "http://localhost:3000" || true
fi

echo "To stop containers, run: docker compose down"
