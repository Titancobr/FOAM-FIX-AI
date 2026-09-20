# Final Public 7-Class Plan

This is the fastest realistic mostly-public-data scope for the mini-project.

## Final classes

1. Barbell Squat
2. Overhead Press
3. Barbell Row
4. Bench Press
5. Pull-Up
6. Lunges
7. Bicep Curl

## Exact dataset mapping

### Fitness-AQA

Use these directly from Fitness-AQA:

- `barbell_squat` -> BackSquat
- `overhead_press` -> OverheadPress
- `barbell_row` -> BarbellRow

Why these matter:

- They are gym-specific
- They include form-focused labels
- They match your screenshot exercises closely

Source:

- https://github.com/ParitoshParmar/Fitness-AQA

### UCF101

Use these directly from UCF101:

- `barbell_bench_press` -> Bench Press
- `pull_up` -> Pull Ups
- `lunges` -> Lunges

Source:

- https://www.crcv.ucf.edu/research/data-sets/ucf101/

### Bicep Curl

`bicep_curl` is included as an extra final class because you asked for it, but it is not as strongly supported by the benchmark datasets you originally listed.

Use it only if you can quickly source clean public clips from secondary public sources or project-ready open datasets. Treat it as the weakest-supported class in the final set.

## What to drop completely for phase 1

Drop these because the datasets you named do not cover them strongly enough for a fast, accurate public-data-only build:

- Incline Bench Press
- Incline Dumbbell Fly
- Cable Flyes
- Dumbbell Flyes
- Lateral Raises
- Tricep Pushdowns
- Dips
- Deadlift
- Romanian Deadlift
- Lat Pulldowns
- Seated Cable Row
- Face Pulls
- Barbell Curls
- Hammer Curls
- Preacher Curls
- Skull Crushers
- Overhead Tricep Extension
- Leg Press
- Leg Extensions
- Leg Curls
- Bulgarian Split Squats
- Calf Raises

## Why this 7-class set is still workable

- It uses classes that are actually present in the public datasets you selected.
- It covers push, pull, and legs.
- It keeps the class count low enough to improve accuracy, even with one weaker class.
- It avoids the machine-heavy and occlusion-heavy exercises that usually lower performance in webcam setups.

## Best training strategy for 85%+ target

### Model

Use:

- MediaPipe Pose landmarks
- BiLSTM classifier on landmark sequences

Do not use raw-video CNN training as the main system if time is short.

### Input representation

For each frame:

- 33 MediaPipe landmarks
- each with `x, y, z, visibility`

For each sample:

- 30 to 45 frame sequence window

### Dataset balancing

Target:

- at least 250 to 400 usable sequences per class after preprocessing

Keep:

- similar sequence count per class
- similar camera-distance distribution per class
- similar front/side angle mix per class

### Split

Recommended split:

- 70% train
- 15% validation
- 15% test

Keep source leakage low:

- clips from the same original video should stay in only one split

### Augmentation

For landmark sequences:

- small Gaussian noise
- temporal jitter
- slight horizontal scaling and translation
- frame dropout of 5% to 10%

Do not apply aggressive augmentation.

### Training recipe on Mac M2

- use `tensorflow-macos`
- use `tensorflow-metal`
- batch size: `32`
- epochs: `30` to `50`
- early stopping patience: `6`
- learning rate: `1e-3`, reduce on plateau

### Best chance of crossing 85%

To maximize the chance:

1. Train the core 6 benchmark-backed classes first
2. Add `bicep_curl` only after the 6-class model is stable
3. Use BiLSTM as the main model
4. Keep sequences clean and balanced
5. Ignore weak screenshot classes in phase 1
6. Report top-1 accuracy plus per-class precision/recall

## Important caution

An `85%+` result is realistic for the core 6-class setup, but adding `bicep_curl` makes the result a bit less certain. It still cannot be guaranteed in advance. It depends on:

- final downloaded clip quality
- label cleaning
- class balance
- split hygiene
- how well the public clips match your webcam deployment view
