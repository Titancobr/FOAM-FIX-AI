import argparse
import math
from pathlib import Path

import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.utils.class_weight import compute_class_weight
import tensorflow as tf
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from tensorflow.keras.utils import to_categorical

from models.transformer_model import build_transformer
from utils.logger import get_logger


logger = get_logger("train_transformer")


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
    parser = argparse.ArgumentParser(description="Train Tuned Multi-Head Transformer exercise classifier.")
    parser.add_argument(
        "--dataset",
        default="dataset/processed/exercise_sequences.npz",
        help="Processed dataset path.",
    )
    parser.add_argument(
        "--epochs",
        type=int,
        default=60,
        help="Training epochs (default: 60).",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=64,
        help="Batch size (default: 64).",
    )
    parser.add_argument(
        "--output",
        default="models/posture_transformer.keras",
        help="Output path for Transformer model.",
    )
    return parser.parse_args()


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

    steps_per_epoch = max(len(X_train) // args.batch_size, 1)
    warmup_steps = 5 * steps_per_epoch
    total_steps = args.epochs * steps_per_epoch

    lr_schedule = WarmupCosineDecay(3e-4, warmup_steps, total_steps)
    optimizer = tf.keras.optimizers.Adam(learning_rate=lr_schedule, clipnorm=1.0)
    loss = tf.keras.losses.CategoricalCrossentropy(label_smoothing=0.1)

    model = build_transformer(input_shape, num_classes)
    model.compile(optimizer=optimizer, loss=loss, metrics=["accuracy"])

    callbacks = [
        EarlyStopping(monitor="val_accuracy", patience=15, restore_best_weights=True, verbose=1),
        ModelCheckpoint(args.output, monitor="val_accuracy", save_best_only=True, verbose=1),
    ]

    logger.info("=" * 50)
    logger.info("Training Tuned Transformer Model (%d epochs, batch=%d)...", args.epochs, args.batch_size)
    logger.info("=" * 50)

    history = model.fit(
        X_train,
        y_train_cat,
        epochs=args.epochs,
        batch_size=args.batch_size,
        validation_data=(X_test, y_test_cat),
        callbacks=callbacks,
        class_weight=class_weight_map,
        verbose=1,
    )

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    logger.info("Saved best Transformer model to %s", args.output)
    logger.info("Final validation accuracy: %.4f", max(history.history["val_accuracy"]))


if __name__ == "__main__":
    main()
