# AI Trainer

AI Trainer is a seventh semester mini-project for real-time exercise pose detection, posture correction, rep counting, and dataset-driven exercise recognition.

## What the project does

- Detects a person in front of the webcam using MediaPipe pose landmarks
- Draws a real-time body skeleton on the detected user
- Tracks joint angles in real time
- Counts reps for exercises such as squats, push-ups, and bicep curls
- Speaks posture correction cues using voice feedback
- Shows on-screen exercise details like `8 reps done`, current stage, tracked angle, and coaching tip
- Supports training temporal deep-learning models on labeled exercise video datasets

## Recommended model choice

For this project, the best balance of accuracy and speed is:

1. MediaPipe Pose for landmark detection
2. BiLSTM for sequence classification on landmark data
3. Rule-based angle correction for real-time feedback

Why this is the best fit:

- Training directly on raw images usually needs a much bigger dataset and stronger hardware.
- Training on pose landmarks extracted from videos is much faster and still follows an industry-style pipeline.
- A BiLSTM is usually more stable than a Transformer on small or medium exercise datasets.
- A Transformer can still be tested for comparison when the dataset becomes large enough.

## Best exercise scope from your screenshots

Your screenshots include many gym exercises, but not all of them are equally good for one-camera real-time posture correction.

Best phase-1 exercises for `85%+` target accuracy:

- Barbell Squat / Squat
- Deadlift
- Romanian Deadlift
- Barbell Curl
- Hammer Curl
- Overhead Press / Military Press
- Lateral Raise
- Pull-Up
- Barbell Row

Good phase-2 additions after the first model is stable:

- Bench Press variants
- Bulgarian Split Squat
- Lat Pulldown
- Dips

Lower-confidence webcam classes that should be treated as advanced or optional:

- Cable Fly / Dumbbell Fly variations
- Tricep Pushdowns
- Skull Crushers
- Seated Cable Row
- Face Pulls
- Preacher Curls
- Calf Raises

Why this matters:

- machine-based exercises often hide joints
- lying exercises like bench press are harder from a normal webcam angle
- small ankle-only movements like calf raises are harder to score reliably
- if you try too many weak classes early, overall accuracy drops fast

The full dataset plan for the exercises from your screenshots is in:

- `dataset/annotations/exercise_dataset_plan.json`
- `dataset/annotations/final_public_7_class_plan.md`

## Project structure

- `main.py`: real-time webcam trainer
- `dashboard/streamlit_app.py`: lightweight project dashboard
- `core/`: pose detection, angle extraction, rep counting, voice engine, form analysis
- `models/`: LSTM, BiLSTM, and Transformer model definitions
- `training/`: preprocessing, training, and evaluation scripts
- `dataset/raw_videos/<label>/`: labeled training videos
- `dataset/processed/`: generated training sequences
- `dataset/annotations/exercise_dataset_plan.json`: screenshot-based dataset strategy

## Dataset workflow

Recommended public datasets for the report and model experiments:

- Kinetics-400: strong source for exercise action clips such as push-up, squat, jumping jack, lunges, sit-ups, and plank. Best for broader exercise classification experiments.
- NTU RGB+D: one of the strongest benchmark datasets for skeleton-based action recognition. Very suitable for LSTM, BiLSTM, and Transformer comparison.
- UCF101: classic action-recognition dataset that can help with baseline video classification experiments.
- Fitness-AQA: most relevant for posture quality and exercise scoring if you want to justify correction and quality assessment in the report.

Best practical project strategy:

1. Use MediaPipe to detect the person, draw the pose skeleton, and extract landmarks from exercise videos.
2. Train a BiLSTM on the landmark sequences for exercise recognition.
3. Use angle-based posture rules and voice feedback for real-time correction.
4. If time allows, compare BiLSTM with the Transformer model on the same processed dataset.

Add labeled videos like this:

```text
dataset/raw_videos/
  barbell_squat/
    sample1.mp4
    sample2.mp4
  overhead_press/
    sample1.mp4
  bicep_curl/
    sample1.mp4
```

Or create the screenshot-based folder structure automatically:

```bash
python training/setup_dataset_structure.py
```

Then run:

```bash
python training/preprocess_dataset.py
python training/train_lstm.py
python training/evaluate.py --model models/exercise_bilstm.keras
```

## Run the trainer

```bash
python main.py --exercise barbell_squat
```

If a trained model exists, the live app will also classify the current exercise from the pose sequence, draw the skeleton, and switch the coaching profile automatically when confidence is high enough.

Optional flags:

```bash
python main.py --exercise overhead_press --mute
python main.py --exercise bicep_curl --camera-index 0
python main.py --disable-classifier
```

## Accuracy note

This repo now gives you a strong project foundation, but final accuracy depends mainly on:

- dataset size and label quality
- multiple camera angles
- consistent exercise framing
- class balance
- model comparison on the same validation split

For the best report and demo quality, train BiLSTM and Transformer on the same processed dataset and compare validation accuracy, precision, recall, and inference speed.

For your Mac M2:

- prefer `tensorflow-macos` and `tensorflow-metal` for training speed
- keep real-time inference on landmark sequences, not raw video CNNs
- use 720p webcam input for a good speed/quality tradeoff
- start with 8 to 10 classes only, then expand after the first strong validation result

If you have no time to record custom videos, use the final public-data scope in:

- `dataset/annotations/final_public_7_class_plan.md`
# AI-FIT-COUCH
# AI-FIT-COUCH
