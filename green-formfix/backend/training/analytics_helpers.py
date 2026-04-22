import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import ConfusionMatrixDisplay, classification_report, confusion_matrix, top_k_accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.utils.class_weight import compute_class_weight
from tensorflow import keras
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau

from models.posture_bilstm import build_bilstm


def _to_jsonable(value):
    if isinstance(value, dict):
        return {key: _to_jsonable(val) for key, val in value.items()}
    if isinstance(value, (list, tuple)):
        return [_to_jsonable(item) for item in value]
    if isinstance(value, (np.floating, np.integer)):
        return value.item()
    return value


def load_dataset(dataset_path="dataset/processed/exercise_sequences.npz"):
    dataset = np.load(dataset_path, allow_pickle=True)
    X = np.asarray(dataset["X"], dtype=np.float32)
    y = np.asarray(dataset["y"], dtype=np.int32)
    label_names = [str(label) for label in dataset["label_names"]]
    return X, y, label_names


def split_dataset(X, y, test_size=0.2, random_state=42):
    return train_test_split(X, y, test_size=test_size, random_state=random_state, stratify=y)


def train_bilstm_with_history(
    dataset_path="dataset/processed/exercise_sequences.npz",
    epochs=30,
    batch_size=32,
    model_path="models/exercise_bilstm.keras",
    analytics_dir="reports/analytics",
):
    X, y, label_names = load_dataset(dataset_path)
    X_train, X_val, y_train, y_val = split_dataset(X, y)

    class_weights = compute_class_weight(
        class_weight="balanced",
        classes=np.arange(len(label_names)),
        y=y_train,
    )
    class_weight_map = {i: float(w) for i, w in enumerate(class_weights)}

    model = build_bilstm((X.shape[1], X.shape[2]), len(label_names))
    callbacks = [
        EarlyStopping(monitor="val_accuracy", patience=8, restore_best_weights=True),
        ReduceLROnPlateau(monitor="val_loss", factor=0.5, patience=3, verbose=1),
    ]

    history = model.fit(
        X_train,
        y_train,
        epochs=epochs,
        batch_size=batch_size,
        validation_data=(X_val, y_val),
        callbacks=callbacks,
        class_weight=class_weight_map,
        verbose=1,
    )

    Path(model_path).parent.mkdir(parents=True, exist_ok=True)
    model.save(model_path)

    analytics_path = Path(analytics_dir)
    analytics_path.mkdir(parents=True, exist_ok=True)
    history_path = analytics_path / "bilstm_history.json"
    history_path.write_text(json.dumps(_to_jsonable(history.history), indent=2))

    plot_training_curves(history.history, analytics_path)
    metrics = evaluate_model(model_path=model_path, dataset_path=dataset_path, analytics_dir=analytics_dir)
    return history.history, metrics, label_names


def evaluate_model(
    model_path="models/exercise_bilstm.keras",
    dataset_path="dataset/processed/exercise_sequences.npz",
    analytics_dir="reports/analytics",
):
    X, y, label_names = load_dataset(dataset_path)
    model = keras.models.load_model(model_path)
    predictions = model.predict(X, verbose=0)
    predicted_labels = np.argmax(predictions, axis=1)

    top1 = float(np.mean(predicted_labels == y))
    k = min(3, predictions.shape[1])
    top3 = float(top_k_accuracy_score(y, predictions, k=k, labels=list(range(predictions.shape[1]))))

    present_labels = sorted(np.unique(np.concatenate([y, predicted_labels])))
    present_target_names = [
        label_names[idx] if idx < len(label_names) else f"class_{idx}" for idx in present_labels
    ]

    report = classification_report(
        y,
        predicted_labels,
        labels=present_labels,
        target_names=present_target_names,
        zero_division=0,
        output_dict=True,
    )
    matrix = confusion_matrix(y, predicted_labels, labels=present_labels)

    analytics_path = Path(analytics_dir)
    analytics_path.mkdir(parents=True, exist_ok=True)
    plot_confusion_matrix(matrix, present_target_names, analytics_path / "confusion_matrix.png")

    metrics = {
        "top1_accuracy": round(top1 * 100, 2),
        "top3_accuracy": round(top3 * 100, 2),
        "classification_report": _to_jsonable(report),
        "labels": present_target_names,
        "confusion_matrix": matrix.tolist(),
    }
    (analytics_path / "metrics_summary.json").write_text(json.dumps(metrics, indent=2))
    return metrics


def plot_training_curves(history, output_dir):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    epochs = range(1, len(history.get("accuracy", [])) + 1)

    plt.figure(figsize=(10, 6))
    plt.plot(epochs, history.get("accuracy", []), label="Training Accuracy", linewidth=2)
    plt.plot(epochs, history.get("val_accuracy", []), label="Validation Accuracy", linewidth=2)
    plt.xlabel("Epoch")
    plt.ylabel("Accuracy")
    plt.title("Training vs Validation Accuracy")
    plt.legend()
    plt.grid(alpha=0.25)
    plt.tight_layout()
    plt.savefig(output_dir / "accuracy_vs_epoch.png", dpi=200)
    plt.close()

    plt.figure(figsize=(10, 6))
    plt.plot(epochs, history.get("loss", []), label="Training Loss", linewidth=2)
    plt.plot(epochs, history.get("val_loss", []), label="Validation Loss", linewidth=2)
    plt.xlabel("Epoch")
    plt.ylabel("Loss")
    plt.title("Training vs Validation Loss")
    plt.legend()
    plt.grid(alpha=0.25)
    plt.tight_layout()
    plt.savefig(output_dir / "loss_vs_epoch.png", dpi=200)
    plt.close()


def plot_confusion_matrix(matrix, labels, output_path):
    fig, ax = plt.subplots(figsize=(8, 6))
    disp = ConfusionMatrixDisplay(confusion_matrix=np.array(matrix), display_labels=labels)
    disp.plot(ax=ax, cmap="Greens", colorbar=False, xticks_rotation=30)
    plt.title("Confusion Matrix")
    plt.tight_layout()
    plt.savefig(output_path, dpi=220)
    plt.close(fig)
