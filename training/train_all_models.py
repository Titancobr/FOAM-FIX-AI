import argparse
import subprocess
import sys
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(
        description="Train Tuned BiLSTM, LSTM, and Transformer models sequentially."
    )
    parser.add_argument(
        "--dataset",
        default="dataset/processed/exercise_sequences.npz",
        help="Processed dataset path.",
    )
    parser.add_argument(
        "--epochs",
        type=int,
        default=50,
        help="Epoch count for the models (default: 50).",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=32,
        help="Batch size (default: 32).",
    )
    parser.add_argument(
        "--skip-preprocess",
        action="store_true",
        help="Skip preprocessing if the dataset is already processed.",
    )
    return parser.parse_args()


def run_step(command):
    print(f"\n>> Running: {' '.join(command)}")
    subprocess.run(command, check=True)


def main():
    args = parse_args()
    project_root = Path(__file__).resolve().parent.parent
    dataset_path = project_root / args.dataset

    if not args.skip_preprocess:
        run_step([sys.executable, "-m", "training.preprocess_dataset"])

    if not dataset_path.exists():
        raise FileNotFoundError(
            f"Processed dataset not found at {dataset_path}. Run preprocessing first."
        )

    # 1. Train BiLSTM and LSTM
    run_step([
        sys.executable,
        "-m",
        "training.train_lstm",
        "--dataset",
        args.dataset,
        "--bilstm-epochs",
        str(args.epochs),
        "--lstm-epochs",
        str(max(30, args.epochs - 10)),
        "--batch-size",
        str(args.batch_size),
        "--output-bilstm",
        "models/exercise_bilstm.keras",
        "--output-lstm",
        "models/exercise_lstm.keras",
    ])

    # 2. Train Transformer
    run_step([
        sys.executable,
        "-m",
        "training.train_transformer",
        "--dataset",
        args.dataset,
        "--epochs",
        str(args.epochs + 10),
        "--batch-size",
        str(max(args.batch_size, 32)),
        "--output",
        "models/posture_transformer.keras",
    ])

    print("\n=======================================================")
    print(" Finished retraining all three tuned models!")
    print(" Models saved in: models/")
    print("   - models/exercise_lstm.keras")
    print("   - models/exercise_bilstm.keras")
    print("   - models/posture_transformer.keras")
    print("=======================================================")


if __name__ == "__main__":
    main()
