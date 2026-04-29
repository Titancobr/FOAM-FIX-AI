import argparse
import subprocess
import sys
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(
        description="Retrain BiLSTM, baseline LSTM, and Transformer models sequentially."
    )
    parser.add_argument(
        "--dataset",
        default="dataset/processed/exercise_sequences.npz",
        help="Processed dataset path.",
    )
    parser.add_argument(
        "--epochs",
        type=int,
        default=30,
        help="Epoch count for the BiLSTM/LSTM training script.",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=32,
        help="Batch size for all models.",
    )
    parser.add_argument(
        "--skip-preprocess",
        action="store_true",
        help="Skip preprocessing if the processed dataset is already up to date.",
    )
    return parser.parse_args()


def run_step(command):
    print(f"Running: {' '.join(command)}")
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

    run_step(
        [
            sys.executable,
            "-m",
            "training.train_lstm",
            "--dataset",
            args.dataset,
            "--epochs",
            str(args.epochs),
            "--batch-size",
            str(args.batch_size),
            "--output-bilstm",
            "models/exercise_bilstm.keras",
            "--output-lstm",
            "models/exercise_lstm.keras",
        ]
    )

    run_step([sys.executable, "-m", "training.train_transformer"])

    print("Finished retraining all three models.")


if __name__ == "__main__":
    main()
