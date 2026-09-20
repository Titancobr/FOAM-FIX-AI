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
        description="Convert labeled exercise videos into balanced landmark sequences for all 26 classes."
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
        help="Number of frames per sequence window (default: 30).",
    )
    parser.add_argument(
        "--stride",
        type=int,
        default=15,
        help="Sliding window stride in frames (default: 15 for 50%% overlap). Set 0 for adaptive.",
    )
    parser.add_argument(
        "--adaptive-stride",
        action="store_true",
        default=True,
        help="Automatically use smaller stride for minority classes to balance dataset.",
    )
    parser.add_argument(
        "--include-labels",
        default="",
        help="Optional comma-separated labels to filter (default: empty = include all non-empty folders, all 26).",
    )
    parser.add_argument(
        "--max-sequences-per-class",
        type=int,
        default=450,
        help="Cap sequences per class to prevent dominant classes from overpowering (default: 450, 0=no cap).",
    )
    return parser.parse_args()


def _normalize_landmarks(landmarks):
    """
    Normalizes 33 MediaPipe pose landmarks relative to the hip center
    and scaled by torso bounding distance.
    Returns flattened list of 132 features [x, y, z, visibility] * 33.
    """
    if len(landmarks) < 33:
        row = []
        for lm in landmarks:
            row.extend([lm.x, lm.y, lm.z, lm.visibility])
        return row

    # MediaPipe indices: 11: L_shoulder, 12: R_shoulder, 23: L_hip, 24: R_hip
    l_hip = landmarks[23]
    r_hip = landmarks[24]
    hip_center_x = (l_hip.x + r_hip.x) / 2.0
    hip_center_y = (l_hip.y + r_hip.y) / 2.0
    hip_center_z = (l_hip.z + r_hip.z) / 2.0

    l_sh = landmarks[11]
    r_sh = landmarks[12]
    sh_center_x = (l_sh.x + r_sh.x) / 2.0
    sh_center_y = (l_sh.y + r_sh.y) / 2.0
    sh_center_z = (l_sh.z + r_sh.z) / 2.0

    torso_size = np.sqrt(
        (sh_center_x - hip_center_x) ** 2
        + (sh_center_y - hip_center_y) ** 2
        + (sh_center_z - hip_center_z) ** 2
    )
    scale = torso_size if torso_size > 1e-4 else 1.0

    row = []
    for lm in landmarks:
        norm_x = (lm.x - hip_center_x) / scale
        norm_y = (lm.y - hip_center_y) / scale
        norm_z = (lm.z - hip_center_z) / scale
        row.extend([norm_x, norm_y, norm_z, lm.visibility])
    return row


def extract_video_frames(video_path: Path, pose, sequence_length: int, stride: int = 15):
    """Extract frames from video and slice into overlapping sequence windows."""
    cap = cv2.VideoCapture(str(video_path))
    frames = []

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = pose.process(rgb)

        if result.pose_landmarks:
            row = _normalize_landmarks(result.pose_landmarks.landmark)
            frames.append(row)

    cap.release()

    windows = []
    effective_stride = max(1, stride)
    total_frames = len(frames)

    for start_idx in range(0, max(total_frames - sequence_length + 1, 0), effective_stride):
        window = frames[start_idx : start_idx + sequence_length]
        if len(window) == sequence_length:
            windows.append(window)

    return windows


def get_class_stride(num_videos: int, base_stride: int = 15, adaptive: bool = True) -> int:
    """
    Adaptive stride logic:
    - Low-resource classes (<= 15 videos): dense stride (5 frames) -> 3x more sequences
    - Medium classes (16-35 videos): stride 12 frames
    - High-resource classes (> 35 videos): stride 20-25 frames
    """
    if not adaptive:
        return base_stride

    if num_videos <= 10:
        return 5
    elif num_videos <= 20:
        return 8
    elif num_videos <= 35:
        return 15
    else:
        return 22


def main():
    args = parse_args()
    input_dir = Path(args.input_dir)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    include_labels = set()
    if args.include_labels.strip():
        include_labels = {label.strip() for label in args.include_labels.split(",") if label.strip()}
        logger.info("Filtering specified labels (%d): %s", len(include_labels), sorted(include_labels))

    # Discover classes
    candidate_dirs = sorted(p for p in input_dir.iterdir() if p.is_dir())
    class_videos = {}

    for label_dir in candidate_dirs:
        label = label_dir.name
        if include_labels and label not in include_labels:
            continue

        vids = sorted([
            *label_dir.glob("*.mp4"),
            *label_dir.glob("*.mov"),
            *label_dir.glob("*.avi"),
        ])
        if vids:
            class_videos[label] = vids

    logger.info("Found %d exercise classes with video data.", len(class_videos))
    for label, vids in class_videos.items():
        logger.info("  %s: %d videos", label, len(vids))

    class_sequences = defaultdict(list)

    with mp_pose.Pose(
        static_image_mode=False,
        model_complexity=1,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    ) as pose:
        for label, video_files in class_videos.items():
            num_vids = len(video_files)
            stride = get_class_stride(num_vids, base_stride=args.stride, adaptive=args.adaptive_stride)
            logger.info("Processing '%s' (%d videos, stride=%d)...", label, num_vids, stride)

            label_windows = []
            for video_path in video_files:
                windows = extract_video_frames(video_path, pose, args.sequence_length, stride=stride)
                label_windows.extend(windows)

            if not label_windows:
                logger.warning("No usable windows for '%s'; skipping class.", label)
                continue

            # Balance: Cap if requested
            if args.max_sequences_per_class > 0 and len(label_windows) > args.max_sequences_per_class:
                # Subsample evenly across extracted sequences
                indices = np.linspace(0, len(label_windows) - 1, args.max_sequences_per_class, dtype=int)
                label_windows = [label_windows[i] for i in indices]

            class_sequences[label] = label_windows
            logger.info("Label '%s' final sequences: %d", label, len(label_windows))

    if not class_sequences:
        raise RuntimeError(
            f"No sequences were created. Check video files in {input_dir}"
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

    counts = [len(class_sequences[l]) for l in label_names]
    imbalance_ratio = max(counts) / max(min(counts), 1)

    np.savez_compressed(
        output_path,
        X=X_array,
        y=y_array,
        label_names=np.asarray(label_names),
    )

    logger.info("=" * 60)
    logger.info("Dataset Preprocessing Complete!")
    logger.info("Total Sequences: %d", len(X_array))
    logger.info("Sequence Shape: %s", X_array.shape[1:])
    logger.info("Number of Classes: %d", len(label_names))
    logger.info("Class Imbalance Ratio: %.2fx (Min: %d, Max: %d)", imbalance_ratio, min(counts), max(counts))
    logger.info("Saved to: %s", output_path)
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
