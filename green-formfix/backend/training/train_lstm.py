import argparse
from pathlib import Path

import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.utils.class_weight import compute_class_weight
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau

from models.exercise_lstm import build_model
from models.posture_bilstm import build_bilstm
from utils.logger import get_logger


logger = get_logger("train_lstm")


def parse_args():
    parser = argparse.ArgumentParser(description="Train LSTM/BiLSTM exercise classifier.")
    parser.add_argument(
        "--dataset",
        default="dataset/processed/exercise_sequences.npz",
        help="Processed dataset path.",
    )
    parser.add_argument(
        "--epochs",
        type=int,
        default=30,
        help="Training epochs for BiLSTM model.",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=32,
        help="Batch size.",
    )
    parser.add_argument(
        "--output-bilstm",
        default="models/exercise_bilstm.keras",
        help="Output path for BiLSTM model.",
    )
    parser.add_argument(
        "--output-lstm",
        default="models/exercise_lstm.keras",
        help="Output path for baseline LSTM model.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    dataset_path = Path(args.dataset)
    if not dataset_path.exists():
        raise FileNotFoundError(
            "Processed dataset not found. Run training/preprocess_dataset.py first."
        )

    data = np.load(dataset_path, allow_pickle=True)
    X = data["X"]
    y = data["y"]
    label_names = [str(label) for label in data["label_names"]]

    if len(label_names) < 2:
        raise RuntimeError("Need at least 2 classes for multi-class training.")

    logger.info("Dataset shape X=%s y=%s classes=%s", X.shape, y.shape, len(label_names))
    counts = np.bincount(y, minlength=len(label_names))
    for idx, label in enumerate(label_names):
        logger.info("Class '%s': %s sequences", label, int(counts[idx]))

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    class_weights = compute_class_weight(
        class_weight="balanced",
        classes=np.arange(len(label_names)),
        y=y_train,
    )
    class_weight_map = {i: float(w) for i, w in enumerate(class_weights)}
    logger.info("Class weights: %s", class_weight_map)

    model = build_bilstm((X.shape[1], X.shape[2]), len(label_names))
    baseline_model = build_model((X.shape[1], X.shape[2]), len(label_names))
    callbacks = [
        EarlyStopping(monitor="val_accuracy", patience=8, restore_best_weights=True),
        ReduceLROnPlateau(monitor="val_loss", factor=0.5, patience=3, verbose=1),
    ]

    logger.info("Training BiLSTM model")
    history = model.fit(
        X_train,
        y_train,
        epochs=args.epochs,
        batch_size=args.batch_size,
        validation_data=(X_test, y_test),
        callbacks=callbacks,
        class_weight=class_weight_map,
        verbose=1,
    )

    logger.info("Training baseline LSTM model")
    baseline_model.fit(
        X_train,
        y_train,
        epochs=max(12, args.epochs - 8),
        batch_size=args.batch_size,
        validation_data=(X_test, y_test),
        callbacks=callbacks,
        class_weight=class_weight_map,
        verbose=1,
    )

    Path("models").mkdir(parents=True, exist_ok=True)
    model.save(args.output_bilstm)
    baseline_model.save(args.output_lstm)
    logger.info("Saved BiLSTM model to %s", args.output_bilstm)
    logger.info("Saved LSTM model to %s", args.output_lstm)
    logger.info("Final validation accuracy: %.4f", history.history["val_accuracy"][-1])


if __name__ == "__main__":
    main()
