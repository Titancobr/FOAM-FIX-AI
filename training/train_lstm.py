import argparse
import math
from pathlib import Path

import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.utils.class_weight import compute_class_weight
import tensorflow as tf
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from tensorflow.keras.utils import to_categorical

from models.exercise_lstm import build_model
from models.posture_bilstm import build_bilstm
from utils.logger import get_logger


logger = get_logger("train_lstm")


class WarmupCosineDecay(tf.keras.optimizers.schedules.LearningRateSchedule):
    """Linear warmup followed by cosine annealing."""

    def __init__(self, base_lr, warmup_steps, total_steps, min_lr=1e-6):
        super().__init__()
        self.base_lr = float(base_lr)
        self.warmup_steps = int(warmup_steps)
        self.total_steps = int(total_steps)
        self.min_lr = float(min_lr)

    def __call__(self, step):
        step = tf.cast(step, tf.float32)
        warmup_pct = tf.minimum(
            step / tf.maximum(tf.cast(self.warmup_steps, tf.float32), 1.0), 1.0
        )
        decay_steps = tf.cast(self.total_steps - self.warmup_steps, tf.float32)
        decay_pct = tf.minimum(
            (step - tf.cast(self.warmup_steps, tf.float32)) / tf.maximum(decay_steps, 1.0),
            1.0,
        )
        decay_pct = tf.maximum(decay_pct, 0.0)
        cosine = 0.5 * (1.0 + tf.cos(np.float32(math.pi) * decay_pct))
        lr = self.min_lr + (self.base_lr - self.min_lr) * cosine
        return lr * warmup_pct

    def get_config(self):
        return {
            "base_lr": self.base_lr,
            "warmup_steps": self.warmup_steps,
            "total_steps": self.total_steps,
            "min_lr": self.min_lr,
        }


def parse_args():
    parser = argparse.ArgumentParser(description="Train Tuned LSTM and BiLSTM exercise classifiers.")
    parser.add_argument(
        "--dataset",
        default="dataset/processed/exercise_sequences.npz",
        help="Processed dataset path.",
    )
    parser.add_argument(
        "--bilstm-epochs",
        type=int,
        default=50,
        help="Training epochs for BiLSTM model (default: 50).",
    )
    parser.add_argument(
        "--lstm-epochs",
        type=int,
        default=40,
        help="Training epochs for LSTM model (default: 40).",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=32,
        help="Batch size (default: 32).",
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


def compile_tuned_model(model, base_lr, warmup_epochs, total_epochs, batch_size, num_train, label_smoothing=0.1):
    steps_per_epoch = max(num_train // batch_size, 1)
    warmup_steps = warmup_epochs * steps_per_epoch
    total_steps = total_epochs * steps_per_epoch

    lr_schedule = WarmupCosineDecay(base_lr, warmup_steps, total_steps)
    optimizer = tf.keras.optimizers.Adam(learning_rate=lr_schedule, clipnorm=1.0)
    loss = tf.keras.losses.CategoricalCrossentropy(label_smoothing=label_smoothing)
    model.compile(optimizer=optimizer, loss=loss, metrics=["accuracy"])
    return model


def main():
    args = parse_args()
    dataset_path = Path(args.dataset)
    if not dataset_path.exists():
        raise FileNotFoundError(
            f"Processed dataset not found at {dataset_path}. Run training/preprocess_dataset.py first."
        )

    data = np.load(dataset_path, allow_pickle=True)
    X = data["X"].astype(np.float32)
    y = data["y"].astype(np.int64)
    label_names = [str(label) for label in data["label_names"]]
    num_classes = len(label_names)

    logger.info("Loaded dataset: %d sequences, %d classes: %s", len(X), num_classes, label_names)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    class_weights = compute_class_weight(
        class_weight="balanced",
        classes=np.arange(num_classes),
        y=y_train,
    )
    class_weight_map = {i: float(w) for i, w in enumerate(class_weights)}

    y_train_cat = to_categorical(y_train, num_classes)
    y_test_cat = to_categorical(y_test, num_classes)
    input_shape = (X.shape[1], X.shape[2])

    Path("models").mkdir(parents=True, exist_ok=True)

    # 1. Train Tuned BiLSTM
    logger.info("=" * 50)
    logger.info("Training Tuned BiLSTM Model (%d epochs)...", args.bilstm_epochs)
    logger.info("=" * 50)
    bilstm_model = build_bilstm(input_shape, num_classes)
    bilstm_model = compile_tuned_model(
        bilstm_model,
        base_lr=5e-4,
        warmup_epochs=3,
        total_epochs=args.bilstm_epochs,
        batch_size=args.batch_size,
        num_train=len(X_train),
        label_smoothing=0.1,
    )

    bilstm_callbacks = [
        EarlyStopping(monitor="val_accuracy", patience=12, restore_best_weights=True, verbose=1),
        ModelCheckpoint(args.output_bilstm, monitor="val_accuracy", save_best_only=True, verbose=1),
    ]

    bilstm_model.fit(
        X_train,
        y_train_cat,
        epochs=args.bilstm_epochs,
        batch_size=args.batch_size,
        validation_data=(X_test, y_test_cat),
        callbacks=bilstm_callbacks,
        class_weight=class_weight_map,
        verbose=1,
    )

    # 2. Train Tuned LSTM
    logger.info("=" * 50)
    logger.info("Training Tuned LSTM Model (%d epochs)...", args.lstm_epochs)
    logger.info("=" * 50)
    lstm_model = build_model(input_shape, num_classes)
    lstm_model = compile_tuned_model(
        lstm_model,
        base_lr=5e-4,
        warmup_epochs=3,
        total_epochs=args.lstm_epochs,
        batch_size=args.batch_size,
        num_train=len(X_train),
        label_smoothing=0.1,
    )

    lstm_callbacks = [
        EarlyStopping(monitor="val_accuracy", patience=10, restore_best_weights=True, verbose=1),
        ModelCheckpoint(args.output_lstm, monitor="val_accuracy", save_best_only=True, verbose=1),
    ]

    lstm_model.fit(
        X_train,
        y_train_cat,
        epochs=args.lstm_epochs,
        batch_size=args.batch_size,
        validation_data=(X_test, y_test_cat),
        callbacks=lstm_callbacks,
        class_weight=class_weight_map,
        verbose=1,
    )

    logger.info("Completed training for BiLSTM and LSTM models.")


if __name__ == "__main__":
    main()
