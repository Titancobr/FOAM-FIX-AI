# FORM-FIX

A real-time system for exercise detection, posture correction, and rep tracking using pose-based machine learning.

---

## What it does

- Detects a person using webcam input via MediaPipe pose landmarks
- Draws a real-time skeletal overlay
- Tracks joint angles continuously
- Counts repetitions for exercises like squats, push-ups, and curls
- Provides posture correction through voice feedback
- Displays live metrics such as reps, movement stage, and coaching cues
- Supports training sequence-based models on labeled exercise data    

---

## Approach

The system combines pose estimation, sequence modeling, and rule-based correction:

1. MediaPipe Pose for extracting body landmarks
2. BiLSTM for sequence-based exercise classification
3. Angle-based rules for real-time posture feedback

Why this setup:

- Pose-based training is faster and more efficient than raw video models
- Sequence models capture motion over time instead of single frames
- BiLSTM performs well on moderate-sized datasets
- Transformers can be explored later for comparison    

---

## Exercise Scope

Not all exercises are equally suitable for single-camera tracking.

### Strong candidates (high reliability)

- Squat
- Barbell Curl
- Hammer Curl
- Lateral Raise
- Pull-Up
- Push-Up

### Can be added later

- Deadlift variants
- Overhead Press
- Rows

### Lower reliability (camera limitations)

- Cable-based movements
- Bench press variations
- Calf raises
- Isolation movements with limited visible motion

Reason:

- Occlusions (hidden joints)
- Limited camera angles
- Small or subtle movements    

---

## System Structure

- `main.py` — real-time webcam pipeline
- `core/` — pose processing, angle tracking, rep counting, feedback
- `models/` — sequence models (LSTM, BiLSTM, Transformer)
- `training/` — preprocessing, training, evaluation scripts
- `dataset/` — raw videos, processed sequences, annotations    

---

## Dataset Workflow

The system uses pose-sequence data instead of raw video.
### Pipeline

1. Extract pose landmarks from videos
2. Convert to angle-based features
3. Create fixed-length sequences
4. Train sequence models for classification    

### Example structure

```
dataset/raw_videos/
  squat/
  bicep_curl/
  pull_up/
```

---

## Training

```bash
python training/preprocess_dataset.py
python training/train_lstm.py
python training/evaluate.py --model models/exercise_bilstm.keras
```

---

## Running the system

```bash
python main.py --exercise squat
```

Optional:

```bash
python main.py --mute
python main.py --camera-index 0
python main.py --disable-classifier
```

---

## Notes on Performance

Accuracy depends on:
- dataset quality and size
- class balance
- camera angle and visibility
- consistency of movement

For best results:
- use pose-based input instead of raw video
- keep exercise set limited initially
- compare models on the same validation split    

---

## Future Improvements

- Expand and balance dataset across exercises
- Define a proper train/validation/test split
- Improve per-rep quality scoring
- Add per-user calibration
- Optimize real-time performance in the browser
- Package the system for deployment (cloud + API-based inference)
- Explore lightweight model versions for broader device support    

---
## Deployment (Docker & Cross-Platform)

The full platform (React frontend + FastAPI backend + MediaPipe/TensorFlow AI engine) is fully containerized.

### Running on Windows (1-Click)

1. Ensure **Docker Desktop** is installed and running.
2. Double-click **`run_windows.bat`** (or execute `./run_windows.ps1` in PowerShell).
3. The script will build and launch containers, then automatically open **`http://localhost:3000`** in your browser.
4. Allow webcam access in your browser and start working out!
5. To stop, run **`stop_windows.bat`** or `docker compose down`.

For detailed Windows setup steps and troubleshooting, see [WINDOWS_SETUP.md](file:///Users/syedahmed/AI-Trainer/WINDOWS_SETUP.md).

### Running on Mac / Linux

```bash
# Start all services with 1 command:
./run_mac_linux.sh

# Or directly with Docker Compose:
docker compose up --build -d
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Key Endpoints
- **Frontend App**: `http://localhost:3000`
- **Backend API**: `http://localhost:8000`
- **Swagger Docs**: `http://localhost:8000/docs`
- **Health Check**: `http://localhost:8000/health`
