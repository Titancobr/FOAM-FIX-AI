from pathlib import Path

import numpy as np
from tensorflow import keras

from models.transformer_model import TransformerBlock


class LiveExercisePredictor:
    def __init__(
        self,
        model_path="models/exercise_bilstm.keras",
        dataset_path="dataset/processed/exercise_sequences.npz",
        min_confidence=0.55,
        ema_alpha=0.45,
        switch_margin=0.06,
    ):
        self.model_path = Path(model_path)
        self.dataset_path = Path(dataset_path)
        if not self.model_path.exists():
            raise FileNotFoundError(f"Trained model not found at {self.model_path}")
        if not self.dataset_path.exists():
            raise FileNotFoundError(f"Processed dataset not found at {self.dataset_path}")

        dataset = np.load(self.dataset_path, allow_pickle=True)
        self.label_names = [str(label) for label in dataset["label_names"]]
        self.sequence_length = int(dataset["X"].shape[1])
        self.feature_dim = int(dataset["X"].shape[2])

        custom_objects = {}
        if "transformer" in self.model_path.stem:
            custom_objects["TransformerBlock"] = TransformerBlock
        self.model = keras.models.load_model(self.model_path, custom_objects=custom_objects)
        self.sequence_buffer = []
        self.ema_probs = None
        self.current_label = None
        self.current_confidence = 0.0

        self.min_confidence = min_confidence
        self.ema_alpha = ema_alpha
        self.switch_margin = switch_margin
        self.latest_probs = None

    def _flatten_landmarks(self, landmarks):
        flattened = []
        for landmark in landmarks:
            flattened.extend(landmark[:4])
        return flattened

    def _build_prediction(self, smoothed_probs, raw_probs):
        self.latest_probs = np.asarray(smoothed_probs, dtype=np.float32)

        top_idx = int(np.argmax(smoothed_probs))
        top_label = self.label_names[top_idx]
        top_conf = float(smoothed_probs[top_idx])

        # Hysteresis: switch class only if candidate is clearly better.
        if self.current_label is None:
            self.current_label = top_label
            self.current_confidence = top_conf
        elif top_label != self.current_label:
            current_idx = self.label_names.index(self.current_label)
            current_conf = float(smoothed_probs[current_idx])
            if (top_conf - current_conf) >= self.switch_margin:
                self.current_label = top_label
                self.current_confidence = top_conf
            else:
                top_label = self.current_label
                top_conf = current_conf
        else:
            self.current_confidence = top_conf

        top3_idx = np.argsort(smoothed_probs)[-3:][::-1]
        top3 = [
            {"label": self.label_names[int(i)], "confidence": float(smoothed_probs[int(i)])}
            for i in top3_idx
        ]

        accepted_label = top_label if top_conf >= self.min_confidence else None
        return {
            "label": accepted_label,
            "confidence": top_conf,
            "raw_label": self.label_names[int(np.argmax(raw_probs))],
            "top3": top3,
            "probs": [float(x) for x in smoothed_probs],
            "source": self.model_path.stem,
        }

    def add_landmarks(self, landmarks):
        flattened = self._flatten_landmarks(landmarks)
        if len(flattened) != self.feature_dim:
            return None

        self.sequence_buffer.append(flattened)
        if len(self.sequence_buffer) > self.sequence_length:
            self.sequence_buffer = self.sequence_buffer[-self.sequence_length :]
        if len(self.sequence_buffer) < self.sequence_length:
            return None

        sequence = np.asarray(self.sequence_buffer, dtype=np.float32)
        raw_probs = self.model.predict(sequence[None, ...], verbose=0)[0]

        if self.ema_probs is None:
            self.ema_probs = raw_probs.copy()
        else:
            self.ema_probs = (
                self.ema_alpha * raw_probs + (1.0 - self.ema_alpha) * self.ema_probs
            )

        # Normalize for numerical safety after EMA.
        probs_sum = float(np.sum(self.ema_probs))
        if probs_sum > 0.0:
            smoothed_probs = self.ema_probs / probs_sum
        else:
            smoothed_probs = raw_probs
        return self._build_prediction(smoothed_probs, raw_probs)


class MultiModelExercisePredictor:
    def __init__(
        self,
        dataset_path="dataset/processed/exercise_sequences.npz",
        mode="hybrid",
        min_confidence=0.55,
        switch_margin=0.06,
        fast_model_path="models/exercise_lstm.keras",
        best_model_path="models/exercise_bilstm.keras",
        transformer_model_path="models/posture_transformer.keras",
        fast_weight=0.25,
        best_weight=0.55,
        transformer_weight=0.20,
        best_interval=2,
        transformer_interval=3,
    ):
        self.mode = mode
        self.min_confidence = min_confidence
        self.switch_margin = switch_margin
        self.best_interval = max(1, int(best_interval))
        self.transformer_interval = max(1, int(transformer_interval))
        self.tick = 0

        self.predictors = {}
        self.weights = {}
        predictor_specs = [
            ("fast", fast_model_path, fast_weight),
            ("best", best_model_path, best_weight),
            ("transformer", transformer_model_path, transformer_weight),
        ]

        for key, model_path, weight in predictor_specs:
            model_file = Path(model_path)
            if not model_file.exists():
                continue
            predictor = LiveExercisePredictor(
                model_path=model_file,
                dataset_path=dataset_path,
                min_confidence=min_confidence,
                switch_margin=switch_margin,
            )
            self.predictors[key] = predictor
            self.weights[key] = float(weight)

        if not self.predictors:
            raise FileNotFoundError("No live classification models were found for multi-model mode.")

        reference = next(iter(self.predictors.values()))
        self.label_names = reference.label_names
        self.current_label = None
        self.current_confidence = 0.0

    def _should_run(self, key):
        if self.mode in {"ensemble", "best"}:
            return key in self.predictors
        if self.mode == "fast":
            return key == "fast"
        if key == "fast":
            return True
        if key == "best":
            return (self.tick % self.best_interval) == 0
        if key == "transformer":
            return (self.tick % self.transformer_interval) == 0
        return False

    def _apply_hysteresis(self, probs):
        top_idx = int(np.argmax(probs))
        top_label = self.label_names[top_idx]
        top_conf = float(probs[top_idx])

        if self.current_label is None:
            self.current_label = top_label
            self.current_confidence = top_conf
        elif top_label != self.current_label:
            current_idx = self.label_names.index(self.current_label)
            current_conf = float(probs[current_idx])
            if (top_conf - current_conf) >= self.switch_margin:
                self.current_label = top_label
                self.current_confidence = top_conf
            else:
                top_label = self.current_label
                top_conf = current_conf
        else:
            self.current_confidence = top_conf

        return top_label, top_conf

    def add_landmarks(self, landmarks):
        self.tick += 1
        raw_results = {}

        for key, predictor in self.predictors.items():
            if self._should_run(key):
                result = predictor.add_landmarks(landmarks)
                if result is not None:
                    raw_results[key] = result

        weighted_probs = None
        total_weight = 0.0
        contributors = []

        for key, predictor in self.predictors.items():
            if predictor.latest_probs is None:
                continue
            weight = self.weights.get(key, 0.0)
            if weight <= 0.0:
                continue
            if weighted_probs is None:
                weighted_probs = np.asarray(predictor.latest_probs, dtype=np.float32) * weight
            else:
                weighted_probs += np.asarray(predictor.latest_probs, dtype=np.float32) * weight
            total_weight += weight
            contributors.append(key)

        if weighted_probs is None or total_weight == 0.0:
            return None

        fused_probs = weighted_probs / total_weight
        fused_probs_sum = float(np.sum(fused_probs))
        if fused_probs_sum > 0.0:
            fused_probs = fused_probs / fused_probs_sum

        top_label, top_conf = self._apply_hysteresis(fused_probs)
        top3_idx = np.argsort(fused_probs)[-3:][::-1]
        top3 = [
            {"label": self.label_names[int(i)], "confidence": float(fused_probs[int(i)])}
            for i in top3_idx
        ]

        return {
            "label": top_label if top_conf >= self.min_confidence else None,
            "confidence": top_conf,
            "raw_label": self.label_names[int(np.argmax(fused_probs))],
            "top3": top3,
            "probs": [float(x) for x in fused_probs],
            "source": f"{self.mode}:{'+'.join(contributors)}",
            "contributors": contributors,
            "models": raw_results,
        }
