# FormFix AI Pose Trainer - Windows Setup Guide

This guide makes it super easy to run FormFix on Windows with full AI posture tracking, rep counting, workouts, and nutrition features.

---

## Prerequisites (One-Time Setup)

1. **Install Docker Desktop for Windows**:
   - Download from: [https://www.docker.com/products/docker-desktop/](https://www.docker.com/products/docker-desktop/)
   - During installation, make sure the checkbox **"Use WSL 2 instead of Hyper-V"** is checked (recommended default).
   - Once installed, open **Docker Desktop** from your Start Menu.
   - Wait until the whale icon in your taskbar / system tray turns solid and says **"Engine running"**.

2. **Webcam**:
   - A built-in laptop camera or any USB webcam.
   - You do NOT need any special USB passthrough or drivers because the camera feed is captured directly in your Windows web browser!

---

## How to Run FormFix (1-Click)

1. **Double-click** `run_windows.bat` in the project root folder.
   *(Alternatively, right click `run_windows.ps1` and select "Run with PowerShell")*
2. The script will automatically:
   - Check that Docker is running.
   - Build and start the backend and frontend containers.
   - Keep all trained AI models (`exercise_bilstm.keras`, `exercise_lstm.keras`, `posture_transformer.keras`) ready in memory.
   - Automatically launch your web browser to **`http://localhost:3000`**.

---

## Using the Application

1. **Camera Permission**:
   - When the browser opens `http://localhost:3000`, your browser will ask for **Camera permission**.
   - Click **Allow**.
2. **Account**:
   - Click **Register** to create a local user account, then **Login**.
3. **Start Training**:
   - Navigate to **Workouts** or **Camera**.
   - Stand back so the camera sees your full body landmarks.
   - Perform your exercise (e.g. Squats, Bicep Curls, Lateral Raises, Push-Ups).
   - FormFix will automatically track your joint angles, count reps, and display real-time form corrections!

---

## Useful URLs & Ports

| Service | URL | Description |
| :--- | :--- | :--- |
| **Frontend Web App** | [http://localhost:3000](http://localhost:3000) | Main UI (Workouts, Live Camera, Analytics) |
| **Backend API** | [http://localhost:8000](http://localhost:8000) | FastAPI server |
| **API Documentation** | [http://localhost:8000/docs](http://localhost:8000/docs) | Interactive Swagger UI |
| **Health Check** | [http://localhost:8000/health](http://localhost:8000/health) | Container health status |

---

## How to Stop the App

When you're finished with your workout:
- Double-click **`stop_windows.bat`**
- OR open Command Prompt in the folder and type:
  ```cmd
  docker compose down
  ```
All your workout stats, accounts, and progress are safely saved in a persistent Docker volume and will be there next time you start!

---

## Troubleshooting

- **"Docker Desktop is installed but not running"**:
  Open Docker Desktop from the Windows Start menu and wait ~30 seconds for it to start up, then double-click `run_windows.bat` again.
- **Camera is not appearing in browser**:
  Check your Windows Settings: `Settings > Privacy & security > Camera` and ensure "Let desktop apps access your camera" and your browser (Chrome/Edge) have permission. Also make sure no other program (like Zoom or Teams) is using the webcam.
- **Port 3000 or 8000 is already in use**:
  If another app is using port 3000 or 8000, you can edit `docker-compose.yml` to change the host ports (e.g. `3001:80` or `8001:8000`).
