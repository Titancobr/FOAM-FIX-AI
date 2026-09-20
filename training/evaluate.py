import argparse
from pathlib import Path

import numpy as np
from sklearn.metrics import classification_report, confusion_matrix, f1_score, top_k_accuracy_score
from tensorflow import keras

from models.transformer_model import PositionalEncoding, TransformerBlock


def parse_args():
    parser = argparse.ArgumentParser(description="Evaluate a trained exercise classification model.")
    parser.add_argument(
        "--model",
        default="models/exercise_bilstm.keras",
        help="Path to the trained Keras model.",
    )
    parser.add_argument(
        "--dataset",
        default="dataset/processed/exercise_sequences.npz",
        help="Processed dataset path.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    dataset = np.load(args.dataset, allow_pickle=True)
    X = dataset["X"].astype(np.float32)
    y = dataset["y"].astype(np.int64)
    label_names = [str(label) for label in dataset["label_names"]]

    custom_objects = {
        "TransformerBlock": TransformerBlock,
        "PositionalEncoding": PositionalEncoding,
    }
    model = keras.models.load_model(args.model, custom_objects=custom_objects)
    predictions = model.predict(X, verbose=0)
    predicted_labels = np.argmax(predictions, axis=1)

    top1 = float(np.mean(predicted_labels == y))
    k = min(3, predictions.shape[1])
    top_k = float(top_k_accuracy_score(y, predictions, k=k, labels=list(range(predictions.shape[1]))))
    macro_f1 = f1_score(y, predicted_labels, average="macro", zero_division=0)
    weighted_f1 = f1_score(y, predicted_labels, average="weighted", zero_division=0)

    print("=" * 60)
    print(f"Evaluation Results for: {Path(args.model).name}")
    print("=" * 60)
    print(f"Top-1 Accuracy:     {top1:.4f} ({top1*100:.2f}%)")
    print(f"Top-{k} Accuracy:     {top_k:.4f} ({top_k*100:.2f}%)")
    print(f"Macro F1 Score:     {macro_f1:.4f}")
    print(f"Weighted F1 Score:  {weighted_f1:.4f}")
    print("=" * 60)
    print("\nClassification Report:")
    print(
        classification_report(
            y,
            predicted_labels,
            target_names=label_names,
            zero_division=0,
        )
    )
    print("\nConfusion Matrix:")
    print(confusion_matrix(y, predicted_labels))


if __name__ == "__main__":
    main()
