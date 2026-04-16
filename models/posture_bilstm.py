from tensorflow.keras.layers import Bidirectional, Dense, Dropout, LSTM
from tensorflow.keras.models import Sequential


def build_bilstm(input_shape, num_classes):
    model = Sequential(
        [
            Bidirectional(LSTM(128, return_sequences=True), input_shape=input_shape),
            Dropout(0.3),
            Bidirectional(LSTM(64)),
            Dropout(0.3),
            Dense(64, activation="relu"),
            Dense(num_classes, activation="softmax"),
        ]
    )

    model.compile(
        optimizer="adam",
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model
