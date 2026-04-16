import argparse
import json
from pathlib import Path
from typing import Optional

import cv2

from core.feature_extractor import FeatureExtractor
from core.live_predictor import LiveExercisePredictor, MultiModelExercisePredictor
from core.pose_estimator import PoseEstimator
from core.posture_rules import PostureAnalyzer
from core.rep_counter import RepCounter
from core.voice_engine import VoiceEngine
from core.workout_scorer import WorkoutScorer
from utils.config import (
    DEFAULT_MODEL_PATH,
    DEFAULT_PROCESSED_DATASET,
    EXERCISE_CONFIGS,
)
from utils.visualization import draw_panel, draw_status_line


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Real-time AI pose trainer with rep counting and voice feedback."
    )
    parser.add_argument(
        "--exercise",
        choices=sorted(EXERCISE_CONFIGS.keys()),
        default="squat",
        help="Exercise profile used for rep counting and posture guidance.",
    )
    parser.add_argument(
        "--camera-index",
        type=int,
        default=0,
        help="OpenCV camera index. Use 0 for the default webcam.",
    )
    parser.add_argument(
        "--mute",
        action="store_true",
        help="Disable voice feedback.",
    )
    parser.add_argument(
        "--model",
        default=str(DEFAULT_MODEL_PATH),
        help="Path to the trained exercise classification model used for live prediction.",
    )
    parser.add_argument(
        "--predictor-mode",
        choices=["single", "fast", "best", "hybrid", "ensemble"],
        default="single",
        help="Choose one model or a multi-model fusion strategy for live classification.",
    )
    parser.add_argument(
        "--fast-model",
        default="models/exercise_lstm.keras",
        help="Fast comparison model path used by hybrid or ensemble mode.",
    )
    parser.add_argument(
        "--best-model",
        default=str(DEFAULT_MODEL_PATH),
        help="Most accurate model path used by best, hybrid, or ensemble mode.",
    )
    parser.add_argument(
        "--transformer-model",
        default="models/posture_transformer.keras",
        help="Transformer model path used by ensemble or hybrid mode when available.",
    )
    parser.add_argument(
        "--best-interval",
        type=int,
        default=2,
        help="Run the best model every N classifier ticks in hybrid mode.",
    )
    parser.add_argument(
        "--transformer-interval",
        type=int,
        default=3,
        help="Run the transformer every N classifier ticks in hybrid mode.",
    )
    parser.add_argument(
        "--fast-weight",
        type=float,
        default=0.15,
        help="Fusion weight for the fast model in hybrid or ensemble mode.",
    )
    parser.add_argument(
        "--best-weight",
        type=float,
        default=0.70,
        help="Fusion weight for the best model in hybrid or ensemble mode.",
    )
    parser.add_argument(
        "--transformer-weight",
        type=float,
        default=0.15,
        help="Fusion weight for the transformer model in hybrid or ensemble mode.",
    )
    parser.add_argument(
        "--dataset",
        default=str(DEFAULT_PROCESSED_DATASET),
        help="Processed dataset path used to load label names and sequence length.",
    )
    parser.add_argument(
        "--disable-classifier",
        action="store_true",
        help="Disable the trained classifier and use only the selected exercise profile.",
    )
    parser.add_argument(
        "--classifier-min-confidence",
        type=float,
        default=0.55,
        help="Minimum confidence to accept predicted class in multi-class mode.",
    )
    parser.add_argument(
        "--classifier-switch-margin",
        type=float,
        default=0.06,
        help="Confidence margin required before switching to a new predicted class.",
    )
    parser.add_argument(
        "--classifier-interval",
        type=int,
        default=4,
        help="Run classifier every N pose frames to improve FPS (default: 4).",
    )
    parser.add_argument(
        "--model-complexity",
        type=int,
        choices=[0, 1, 2],
        default=0,
        help="MediaPipe pose model complexity. 0 is fastest.",
    )
    parser.add_argument(
        "--input-width",
        type=int,
        default=960,
        help="Resize camera frames to this width before inference (0 disables).",
    )
    parser.add_argument(
        "--report-path",
        default="reports/session_report.json",
        help="JSON path for final workout score report.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    exercise = EXERCISE_CONFIGS[args.exercise]

    pose = PoseEstimator(model_complexity=args.model_complexity)
    extractor = FeatureExtractor()
    analyzer = PostureAnalyzer()
    counter = RepCounter(exercise)
    voice = VoiceEngine(enabled=not args.mute)
    scorer = WorkoutScorer()
    predictor = None

    if not args.disable_classifier:
        try:
            if args.predictor_mode == "single":
                predictor = LiveExercisePredictor(
                    model_path=args.model,
                    dataset_path=args.dataset,
                    min_confidence=args.classifier_min_confidence,
                    switch_margin=args.classifier_switch_margin,
                )
            else:
                predictor = MultiModelExercisePredictor(
                    dataset_path=args.dataset,
                    mode=args.predictor_mode,
                    min_confidence=args.classifier_min_confidence,
                    switch_margin=args.classifier_switch_margin,
                    fast_model_path=args.fast_model,
                    best_model_path=args.best_model,
                    transformer_model_path=args.transformer_model,
                    fast_weight=args.fast_weight,
                    best_weight=args.best_weight,
                    transformer_weight=args.transformer_weight,
                    best_interval=args.best_interval,
                    transformer_interval=args.transformer_interval,
                )
        except FileNotFoundError:
            predictor = None

    cap = cv2.VideoCapture(args.camera_index)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    if not cap.isOpened():
        raise RuntimeError("Unable to open the camera. Check webcam permissions and index.")

    last_spoken_message: Optional[str] = None
    predicted_exercise_name: Optional[str] = None
    prediction_confidence = 0.0
    prediction_source = "profile_only"
    frame_idx = 0
    last_milestone_spoken = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if args.input_width and frame.shape[1] > args.input_width:
            new_height = int((args.input_width / frame.shape[1]) * frame.shape[0])
            frame = cv2.resize(frame, (args.input_width, new_height), interpolation=cv2.INTER_AREA)

        frame = cv2.flip(frame, 1)
        landmarks, results = pose.detect(frame)

        posture_message = "Align yourself inside the camera frame."
        stage = counter.stage or "ready"
        reps = counter.counter
        primary_metric = 0.0

        if landmarks:
            pose.draw_pose(frame, results)
            if predictor is not None:
                if frame_idx % max(1, args.classifier_interval) == 0:
                    prediction = predictor.add_landmarks(landmarks)
                    if prediction and prediction["label"] in EXERCISE_CONFIGS:
                        if prediction["label"] != predicted_exercise_name:
                            predicted_exercise_name = prediction["label"]
                            exercise = EXERCISE_CONFIGS[predicted_exercise_name]
                            counter = RepCounter(exercise)
                            last_spoken_message = None
                            last_milestone_spoken = 0
                        prediction_confidence = prediction["confidence"]
                        prediction_source = prediction.get("source", args.predictor_mode)

            angles = extractor.extract_angles(landmarks)
            reps, stage, primary_metric = counter.update(angles)
            posture_result = analyzer.analyze(exercise, angles)
            posture_message = posture_result["message"]
            scorer.update(exercise.name, reps, posture_result)

            if posture_message != "Good form" and posture_message != last_spoken_message:
                voice.speak(posture_message)
                last_spoken_message = posture_message
            elif posture_message == "Good form":
                last_spoken_message = None

            for milestone in (8, 12, 15):
                if reps >= milestone and last_milestone_spoken < milestone:
                    voice.speak(f"{milestone} reps done")
                    last_milestone_spoken = milestone
                    break

        draw_panel(
            frame,
            title="AI Personal Trainer",
            lines=[
                f"Exercise: {exercise.display_name}",
                f"Model prediction: {EXERCISE_CONFIGS[predicted_exercise_name].display_name if predicted_exercise_name in EXERCISE_CONFIGS else exercise.display_name}",
                f"Prediction confidence: {prediction_confidence:.2f}",
                f"Prediction mode: {prediction_source}",
                f"Target muscle groups: {exercise.muscle_groups}",
                f"Rep count: {reps} reps done",
                f"Stage: {stage}",
                f"{exercise.tracked_angle_label}: {primary_metric:.1f} deg",
                f"Coach cue: {posture_message}",
            ],
        )

        draw_status_line(
            frame,
            text=f"Skeleton detected | Press Q to quit | Exercise tips: {exercise.tips}",
        )

        cv2.imshow("AI Trainer", frame)
        if cv2.waitKey(1) & 0xFF in (ord("q"), 27):
            break
        frame_idx += 1

    cap.release()
    cv2.destroyAllWindows()

    report = scorer.build_report()
    report_path = Path(args.report_path)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    print(f"Workout report saved to: {report_path}")


if __name__ == "__main__":
    main()
