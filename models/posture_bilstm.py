import tensorflow as tf
from tensorflow.keras.layers import (
    Bidirectional,
    Concatenate,
    Dense,
    Dropout,
    GlobalAveragePooling1D,
    GlobalMaxPooling1D,
    Input,
    LayerNormalization,
    LSTM,
)
from tensorflow.keras.models import Model


def build_bilstm(
    input_shape,
    num_classes,
    lstm_units_1=256,
    lstm_units_2=128,
    lstm_units_3=64,
    dropout_1=0.35,
    dropout_2=0.30,
    dropout_3=0.20,
    l2_reg=1e-4,
    learning_rate=5e-4,
):
    """
    Tuned 3-layer Bidirectional LSTM with dual pooling for exercise classification.

    Architecture:
    - Layer 1: BiLSTM (256 forward + 256 backward = 512) + LayerNorm + Dropout(0.35)
    - Layer 2: BiLSTM (128 forward + 128 backward = 256) + LayerNorm + Dropout(0.30)
    - Layer 3: BiLSTM (64 forward + 64 backward = 128) + LayerNorm + Dropout(0.20)
    - Dual Pooling: GlobalAveragePooling1D (motion context) + GlobalMaxPooling1D (peak contraction)
    - Wider head: 256 (GELU) -> 128 (GELU) -> num_classes (Softmax)
    """
    reg = tf.keras.regularizers.l2(l2_reg) if l2_reg > 0 else None

    inputs = Input(shape=input_shape)

    # BiLSTM Layer 1
    x = Bidirectional(
        LSTM(lstm_units_1, return_sequences=True, kernel_regularizer=reg)
    )(inputs)
    x = LayerNormalization()(x)
    x = Dropout(dropout_1)(x)

    # BiLSTM Layer 2
    x = Bidirectional(
        LSTM(lstm_units_2, return_sequences=True, kernel_regularizer=reg)
    )(x)
    x = LayerNormalization()(x)
    x = Dropout(dropout_2)(x)

    # BiLSTM Layer 3
    x = Bidirectional(
        LSTM(lstm_units_3, return_sequences=True)
    )(x)
    x = LayerNormalization()(x)
    x = Dropout(dropout_3)(x)

    # Dual temporal pooling: captures both global movement pattern and peak contraction points
    avg_pool = GlobalAveragePooling1D()(x)
    max_pool = GlobalMaxPooling1D()(x)
    pooled = Concatenate()([avg_pool, max_pool])

    # Classification head
    dense1 = Dense(256, activation="gelu")(pooled)
    norm1 = LayerNormalization()(dense1)
    drop1 = Dropout(0.20)(norm1)

    dense2 = Dense(128, activation="gelu")(drop1)
    drop2 = Dropout(0.15)(dense2)

    outputs = Dense(num_classes, activation="softmax")(drop2)

    model = Model(inputs=inputs, outputs=outputs, name="PostureBiLSTM")

    optimizer = tf.keras.optimizers.Adam(learning_rate=learning_rate, clipnorm=1.0)
    model.compile(
        optimizer=optimizer,
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model
