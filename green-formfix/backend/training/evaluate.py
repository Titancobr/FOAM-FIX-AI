import argparse

import numpy as np
from sklearn.metrics import classification_report, confusion_matrix, top_k_accuracy_score
from tensorflow import keras

from models.transformer_model import TransformerBlock


def parse_args():
    parser = argparse.ArgumentParser(description="Evaluate a trained exercise model.")
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
    X = dataset["X"]
    y = dataset["y"]
    label_names = [str(label) for label in dataset["label_names"]]

    custom_objects = {}
    if "transformer" in str(args.model):
        custom_objects["TransformerBlock"] = TransformerBlock
    model = keras.models.load_model(args.model, custom_objects=custom_objects)
    predictions = model.predict(X, verbose=0)
    predicted_labels = np.argmax(predictions, axis=1)

    present_labels = sorted(np.unique(np.concatenate([y, predicted_labels])))
    present_target_names = [
        label_names[idx] if idx < len(label_names) else f"class_{idx}" for idx in present_labels
    ]

    top1 = float(np.mean(predicted_labels == y))
    k = min(3, predictions.shape[1])
    top3 = float(top_k_accuracy_score(y, predictions, k=k, labels=list(range(predictions.shape[1]))))

    print(f"Top-1 Accuracy: {top1:.4f}")
    print(f"Top-{k} Accuracy: {top3:.4f}")
    print("Classification Report")
    print(
        classification_report(
            y,
            predicted_labels,
            labels=present_labels,
            target_names=present_target_names,
            zero_division=0,
        )
    )
    print("Confusion Matrix")
    print(confusion_matrix(y, predicted_labels, labels=present_labels))


if __name__ == "__main__":
    main()
