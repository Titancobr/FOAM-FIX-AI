#!/usr/bin/env bash
set -Eeuo pipefail

echo "========================================================"
echo "    FORM-FIX AI Pose Trainer - Mac / Linux Launcher"
echo "========================================================"
echo ""

# Check Docker CLI
if ! command -v docker >/dev/null 2>&1; then
    echo "[ERROR] Docker is not installed or not in PATH."
    echo "Install Docker Desktop from:"
    echo "https://www.docker.com/products/docker-desktop/"
    exit 1
fi

# Detect Docker Compose command
if docker compose version >/dev/null 2>&1; then
    COMPOSE_CMD=(docker compose)
elif command -v docker-compose >/dev/null 2>&1; then
    COMPOSE_CMD=(docker-compose)
else
    echo "[ERROR] Docker Compose is not installed."
    echo "Install Docker Desktop or the Docker Compose plugin."
    exit 1
fi

# Check Docker daemon
echo "[*] Checking Docker daemon status..."

if ! docker info >/dev/null 2>&1; then
    echo "[ERROR] Docker daemon is not running."

    case "$(uname -s)" in
        Darwin)
            echo "Start Docker Desktop and run this script again."
            ;;
        Linux)
            echo "Start Docker with:"
            echo "  sudo systemctl enable --now docker"
            ;;
        *)
            echo "Start Docker and run this script again."
            ;;
    esac

    exit 1
fi

echo "[OK] Docker daemon is active."
echo "[OK] Compose command: ${COMPOSE_CMD[*]}"

echo "[*] Building and starting FormFix containers..."
"${COMPOSE_CMD[@]}" up --build -d

echo ""
echo "========================================================"
echo " [SUCCESS] FormFix AI Trainer is running!"
echo "========================================================"
echo " - Frontend Web App:  http://localhost:3000"
echo " - Backend API:       http://localhost:8000"
echo " - Interactive Docs:  http://localhost:8000/docs"
echo ""

# Give the frontend a moment to start
sleep 4

# Open the frontend in the default browser
if [[ "$(uname -s)" == "Darwin" ]]; then
    open "http://localhost:3000" >/dev/null 2>&1 || true
elif command -v xdg-open >/dev/null 2>&1; then
    xdg-open "http://localhost:3000" >/dev/null 2>&1 || true
elif command -v gio >/dev/null 2>&1; then
    gio open "http://localhost:3000" >/dev/null 2>&1 || true
else
    echo "Open http://localhost:3000 in your browser."
fi

echo ""
echo "To stop the containers, run:"
echo "  ${COMPOSE_CMD[*]} down"
