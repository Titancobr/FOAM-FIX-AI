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


def extract_video_frames(
    video_path: Path,
    pose,
    sequence_length: int,
    stride: int = 15,
    max_windows: int = 0,
    max_dimension: int = 480,
):
    """Extract frames from video and slice into overlapping sequence windows."""
    cap = cv2.VideoCapture(str(video_path))
    frames = []
    windows = []
    effective_stride = max(1, stride)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Downscale large frames for faster decoding and MediaPipe inference
        h, w = frame.shape[:2]
        if max(h, w) > max_dimension:
            scale = max_dimension / float(max(h, w))
            frame = cv2.resize(frame, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = pose.process(rgb)

        if result.pose_landmarks:
            row = _normalize_landmarks(result.pose_landmarks.landmark)
            frames.append(row)

            # Check if a new sequence window can be formed
            if len(frames) >= sequence_length:
                offset = len(frames) - sequence_length
                if offset % effective_stride == 0:
                    windows.append(frames[-sequence_length:])
                    if max_windows > 0 and len(windows) >= max_windows:
                        break

    cap.release()
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
    cache_dir = output_path.parent / ".class_cache"
    cache_dir.mkdir(parents=True, exist_ok=True)

    include_labels = set()
    if args.include_labels.strip():
        include_labels = {label.strip() for label in args.include_labels.split(",") if label.strip()}
        logger.info("Filtering specified labels (%d): %s", len(include_labels), sorted(include_labels))

    # Discover classes and all video files case-insensitively (.mp4, .mov, .avi)
    candidate_dirs = sorted(p for p in input_dir.iterdir() if p.is_dir())
    class_videos = {}

    for label_dir in candidate_dirs:
        label = label_dir.name
        if include_labels and label not in include_labels:
            continue

        vids = sorted([
            p for p in label_dir.iterdir()
            if p.is_file() and p.suffix.lower() in {".mp4", ".mov", ".avi"}
        ])
        if vids:
            class_videos[label] = vids

    logger.info("Found %d exercise classes with video data.", len(class_videos))
    for label, vids in class_videos.items():
        logger.info("  %s: %d videos", label, len(vids))

    class_sequences = defaultdict(list)
    total_classes = len(class_videos)

    with mp_pose.Pose(
        static_image_mode=False,
        model_complexity=1,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    ) as pose:
        for idx, (label, video_files) in enumerate(class_videos.items(), start=1):
            cache_file = cache_dir / f"{label}.npy"
            if cache_file.exists():
                cached_data = np.load(cache_file, allow_pickle=True)
                class_sequences[label] = list(cached_data)
                logger.info(
                    "[%d/%d] '%s': Loaded %d sequences from cache.",
                    idx, total_classes, label, len(class_sequences[label])
                )
                continue

            num_vids = len(video_files)
            stride = get_class_stride(num_vids, base_stride=args.stride, adaptive=args.adaptive_stride)
            max_windows_per_video = (
                max(args.max_sequences_per_class // num_vids + 5, 20)
                if (args.max_sequences_per_class > 0 and num_vids > 6)
                else 0
            )

            logger.info(
                "[%d/%d] Processing '%s' (%d videos, stride=%d, max_win/vid=%s)...",
                idx, total_classes, label, num_vids, stride,
                str(max_windows_per_video) if max_windows_per_video else "all"
            )

            label_windows = []
            for v_idx, video_path in enumerate(video_files, start=1):
                windows = extract_video_frames(
                    video_path,
                    pose,
                    args.sequence_length,
                    stride=stride,
                    max_windows=max_windows_per_video,
                )
                label_windows.extend(windows)

            if not label_windows:
                logger.warning("No usable windows for '%s'; skipping class.", label)
                continue

            # Balance: Cap if requested
            if args.max_sequences_per_class > 0 and len(label_windows) > args.max_sequences_per_class:
                indices = np.linspace(0, len(label_windows) - 1, args.max_sequences_per_class, dtype=int)
                label_windows = [label_windows[i] for i in indices]

            class_sequences[label] = label_windows
            # Save to class cache
            np.save(cache_file, np.asarray(label_windows, dtype=np.float32))
            logger.info("  -> '%s' complete: %d sequences cached.", label, len(label_windows))

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

    import json
    models_dir = Path("models")
    models_dir.mkdir(parents=True, exist_ok=True)
    with open(models_dir / "label_names.json", "w") as f:
        json.dump(label_names, f, indent=2)

    logger.info("=" * 60)
    logger.info("Dataset Preprocessing Complete!")
    logger.info("Total Sequences: %d", len(X_array))
    logger.info("Sequence Shape: %s", X_array.shape[1:])
    logger.info("Number of Classes: %d", len(label_names))
    logger.info("Class Imbalance Ratio: %.2fx (Min: %d, Max: %d)", imbalance_ratio, min(counts), max(counts))
    logger.info("Saved to: %s", output_path)
    logger.info("Saved label names to: %s", models_dir / "label_names.json")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
