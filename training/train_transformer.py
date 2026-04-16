from pathlib import Path

import numpy as np
from sklearn.model_selection import train_test_split

from models.transformer_model import build_transformer
from utils.logger import get_logger


logger = get_logger("train_transformer")

dataset_path = Path("dataset/processed/exercise_sequences.npz")
if not dataset_path.exists():
    raise FileNotFoundError(
        "Processed dataset not found. Run training/preprocess_dataset.py first."
    )

data = np.load(dataset_path, allow_pickle=True)
X = data["X"]
y = data["y"]
label_names = data["label_names"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

model = build_transformer((X.shape[1], X.shape[2]), len(label_names))

history = model.fit(
    X_train,
    y_train,
    epochs=30,
    batch_size=32,
    validation_data=(X_test, y_test),
)

Path("models").mkdir(parents=True, exist_ok=True)
model.save("models/posture_transformer.keras")
logger.info("Saved transformer model to models/posture_transformer.keras")
logger.info("Final validation accuracy: %.4f", history.history["val_accuracy"][-1])
