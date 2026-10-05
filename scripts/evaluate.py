#!/usr/bin/env python3
"""Evaluation script that logs metrics to MLflow and creates DVC metric file.
It loads the saved Keras models, evaluates on the test split of the selected dataset,
and writes a JSON file (metrics/eval.json) used by DVC.
"""
import argparse
import json
from pathlib import Path
import numpy as np
import tensorflow as tf
import mlflow
import mlflow.keras

def load_dataset(npz_path):
    data = np.load(npz_path, allow_pickle=True)
    X = data["X"].astype(np.float32)
    y = data["y"].astype(np.int64)
    label_names = data["label_names"]
    num_classes = len(label_names)
    y_cat = tf.keras.utils.to_categorical(y, num_classes)
    return X, y_cat, num_classes

def main():
    parser = argparse.ArgumentParser(description="Evaluate LSTM/BiLSTM models and log to MLflow")
    parser.add_argument("--lstm", required=True, help="Path to LSTM .keras file")
    parser.add_argument("--bilstm", required=True, help="Path to BiLSTM .keras file")
    parser.add_argument("--test-data", required=True, help="Processed .npz dataset for testing")
    parser.add_argument("--mlflow-dir", default="mlruns", help="MLflow tracking directory")
    args = parser.parse_args()

    mlflow.set_tracking_uri(f"file://{Path(args.mlflow_dir).absolute()}")
    mlflow.set_experiment("ai_trainer_exercise_classification")

    X_test, y_test, num_classes = load_dataset(args.test_data)

    with mlflow.start_run(run_name="evaluation"):
        # LSTM
        lstm = tf.keras.models.load_model(args.lstm)
        lstm_loss, lstm_acc = lstm.evaluate(X_test, y_test, verbose=0)
        mlflow.log_metric("lstm_accuracy", float(lstm_acc))
        mlflow.log_metric("lstm_loss", float(lstm_loss))
        mlflow.keras.log_model(lstm, artifact_path="lstm_model")
        # BiLSTM
        bilstm = tf.keras.models.load_model(args.bilstm)
        bilstm_loss, bilstm_acc = bilstm.evaluate(X_test, y_test, verbose=0)
        mlflow.log_metric("bilstm_accuracy", float(bilstm_acc))
        mlflow.log_metric("bilstm_loss", float(bilstm_loss))
        mlflow.keras.log_model(bilstm, artifact_path="bilstm_model")

        # write DVC metrics JSON
        metrics = {
            "lstm_accuracy": float(lstm_acc),
            "bilstm_accuracy": float(bilstm_acc),
            "lstm_loss": float(lstm_loss),
            "bilstm_loss": float(bilstm_loss),
        }
        out_path = Path("metrics/eval.json")
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(metrics, indent=2))
        mlflow.log_artifact(str(out_path))
        print("✅ Evaluation completed and logged to MLflow")

if __name__ == "__main__":
    main()
