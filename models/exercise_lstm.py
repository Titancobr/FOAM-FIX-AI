import tensorflow as tf
from tensorflow.keras.layers import Dense, Dropout, LSTM, LayerNormalization, InputLayer
from tensorflow.keras.models import Sequential


def build_model(
    input_shape,
    num_classes,
    units_1=256,
    units_2=128,
    units_3=64,
    dropout_1=0.30,
    dropout_2=0.25,
    dropout_3=0.20,
    l2_reg=1e-4,
    learning_rate=5e-4,
):
    """
    Tuned 3-layer LSTM for multi-class exercise classification.
    
    Architecture:
    - Layer 1 (256 units): Wide temporal representation with L2 kernel regularization
    - Layer 2 (128 units): Mid-level sequential feature extraction
    - Layer 3 (64 units): Compressed temporal bottleneck
    - Graduated dropout (0.30 -> 0.25 -> 0.20) + LayerNormalization
    - 2-stage Dense classification head (128 -> 64 -> num_classes) with GELU activation
    """
    reg = tf.keras.regularizers.l2(l2_reg) if l2_reg > 0 else None

    model = Sequential([
        InputLayer(input_shape=input_shape),

        # Block 1: Coarse temporal features
        LSTM(units_1, return_sequences=True, kernel_regularizer=reg),
        LayerNormalization(),
        Dropout(dropout_1),

        # Block 2: Mid-level sequential features
        LSTM(units_2, return_sequences=True, kernel_regularizer=reg),
        LayerNormalization(),
        Dropout(dropout_2),

        # Block 3: Compressed sequence representation
        LSTM(units_3, return_sequences=False),
        LayerNormalization(),
        Dropout(dropout_3),

        # Dense classification head with GELU activations
        Dense(128, activation="gelu"),
        LayerNormalization(),
        Dropout(0.15),
        Dense(64, activation="gelu"),
        Dropout(0.10),
        Dense(num_classes, activation="softmax"),
    ], name="ExerciseLSTM")

    optimizer = tf.keras.optimizers.Adam(learning_rate=learning_rate, clipnorm=1.0)
    model.compile(
        optimizer=optimizer,
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model
