import argparse
from collections import defaultdict
from pathlib import Path

import cv2
import mediapipe as mp
import numpy as np

from utils.config import DATASET_DIR, DEFAULT_SEQUENCE_LENGTH
from utils.logger import get_logger


logger = get_logger("preprocess_dataset")
mp_pose = mp.solutions.pose


def parse_args():
    parser = argparse.ArgumentParser(
        description="Convert labeled exercise videos into landmark sequences."
    )
    parser.add_argument(
        "--input-dir",
        default=str(DATASET_DIR / "raw_videos"),
        help="Directory containing one subfolder per exercise label.",
    )
    parser.add_argument(
        "--output",
        default=str(DATASET_DIR / "processed" / "exercise_sequences.npz"),
        help="Output npz file for training.",
    )
    parser.add_argument(
        "--sequence-length",
        type=int,
        default=DEFAULT_SEQUENCE_LENGTH,
        help="Number of frames per sequence window.",
    )
    parser.add_argument(
        "--include-labels",
        default="",
        help="Comma-separated labels to include for multi-class training (e.g., bicep_curl,push_up,pull_up,barbell_squat).",
    )
    parser.add_argument(
        "--max-sequences-per-class",
        type=int,
        default=0,
        help="Optional cap per class to reduce imbalance (0 disables cap).",
    )
    return parser.parse_args()


def extract_video_frames(video_path: Path, pose, sequence_length: int):
    cap = cv2.VideoCapture(str(video_path))
    frames = []

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = pose.process(rgb)

        if result.pose_landmarks:
            row = []
            for lm in result.pose_landmarks.landmark:
                row.extend([lm.x, lm.y, lm.z, lm.visibility])
            frames.append(row)

    cap.release()

    windows = []
    for start_idx in range(0, max(len(frames) - sequence_length + 1, 0), sequence_length):
        window = frames[start_idx : start_idx + sequence_length]
        if len(window) == sequence_length:
            windows.append(window)
    return windows


def main():
    args = parse_args()
    input_dir = Path(args.input_dir)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    include_labels = set()
    if args.include_labels.strip():
        include_labels = {label.strip() for label in args.include_labels.split(",") if label.strip()}
        logger.info("Filtering labels: %s", sorted(include_labels))

    class_sequences = defaultdict(list)

    with mp_pose.Pose(
        static_image_mode=False,
        model_complexity=1,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    ) as pose:
        for label_dir in sorted(path for path in input_dir.iterdir() if path.is_dir()):
            label = label_dir.name
            if include_labels and label not in include_labels:
                continue

            video_files = sorted(
                [
                    *label_dir.glob("*.mp4"),
                    *label_dir.glob("*.mov"),
                    *label_dir.glob("*.avi"),
                ]
            )

            if not video_files:
                logger.info("Skipping empty label folder '%s'", label)
                continue

            logger.info("Processing %s videos for label '%s'", len(video_files), label)

            label_windows = []
            for video_path in video_files:
                windows = extract_video_frames(video_path, pose, args.sequence_length)
                label_windows.extend(windows)

            if not label_windows:
                logger.warning("No usable windows for '%s'; skipping class.", label)
                continue

            if args.max_sequences_per_class > 0 and len(label_windows) > args.max_sequences_per_class:
                label_windows = label_windows[: args.max_sequences_per_class]

            class_sequences[label] = label_windows
            logger.info("Label '%s' usable sequences: %s", label, len(label_windows))

    if not class_sequences:
        raise RuntimeError(
            f"No sequences were created. Add videos under {input_dir}/<exercise_label>/ first."
        )

    label_names = sorted(class_sequences.keys())
    label_to_index = {label: idx for idx, label in enumerate(label_names)}

    X = []
    y = []
    for label in label_names:
        windows = class_sequences[label]
        X.extend(windows)
        y.extend([label_to_index[label]] * len(windows))

    X_array = np.asarray(X, dtype=np.float32)
    y_array = np.asarray(y, dtype=np.int64)

    np.savez_compressed(
        output_path,
        X=X_array,
        y=y_array,
        label_names=np.asarray(label_names),
    )
    logger.info("Saved %s total sequences to %s", len(X_array), output_path)
    logger.info("Final classes: %s", label_names)


if __name__ == "__main__":
    main()
