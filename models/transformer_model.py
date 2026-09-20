import tensorflow as tf
from tensorflow.keras.layers import (
    Dense,
    Dropout,
    GlobalAveragePooling1D,
    GlobalMaxPooling1D,
    Concatenate,
    Input,
    LayerNormalization,
    MultiHeadAttention,
)


class PositionalEncoding(tf.keras.layers.Layer):
    """Sinusoidal positional encoding for temporal landmark sequences."""

    def __init__(self, sequence_length, embed_dim, **kwargs):
        super().__init__(**kwargs)
        self.sequence_length = sequence_length
        self.embed_dim = embed_dim
        self.pos_encoding = self._positional_encoding(sequence_length, embed_dim)

    def _positional_encoding(self, seq_len, d_model):
        pos = tf.range(seq_len, dtype=tf.float32)[:, tf.newaxis]
        i = tf.range(d_model, dtype=tf.float32)[tf.newaxis, :]
        angle_rates = 1.0 / tf.pow(10000.0, (2.0 * (i // 2.0)) / tf.cast(d_model, tf.float32))
        angle_rads = pos * angle_rates

        sines = tf.math.sin(angle_rads[:, 0::2])
        cosines = tf.math.cos(angle_rads[:, 1::2])

        pos_encoding = tf.concat([sines, cosines], axis=-1)
        return tf.cast(pos_encoding[tf.newaxis, ...], dtype=tf.float32)

    def call(self, inputs):
        seq_len = tf.shape(inputs)[1]
        return inputs + self.pos_encoding[:, :seq_len, :]

    def get_config(self):
        config = super().get_config()
        config.update({
            "sequence_length": self.sequence_length,
            "embed_dim": self.embed_dim,
        })
        return config


class TransformerBlock(tf.keras.layers.Layer):
    """
    Pre-norm Transformer block with multi-head attention and two-layer feedforward network.
    Uses Pre-LN architecture for improved gradient stability in deep sequence models.
    """

    def __init__(self, embed_dim=128, num_heads=8, ff_dim=256, dropout_rate=0.20, **kwargs):
        super().__init__(**kwargs)
        self.embed_dim = embed_dim
        self.num_heads = num_heads
        self.ff_dim = ff_dim
        self.dropout_rate = dropout_rate

        self.att = MultiHeadAttention(
            num_heads=num_heads,
            key_dim=max(embed_dim // num_heads, 16),
            dropout=dropout_rate,
        )
        self.ffn = tf.keras.Sequential([
            Dense(ff_dim, activation="gelu"),
            Dropout(dropout_rate),
            Dense(embed_dim),
        ])
        self.norm1 = LayerNormalization(epsilon=1e-6)
        self.norm2 = LayerNormalization(epsilon=1e-6)
        self.dropout1 = Dropout(dropout_rate)
        self.dropout2 = Dropout(dropout_rate)

    def call(self, inputs, training=False):
        # Pre-LayerNormalization
        x_norm1 = self.norm1(inputs)
        attn_output = self.att(x_norm1, x_norm1, training=training)
        attn_output = self.dropout1(attn_output, training=training)
        out1 = inputs + attn_output

        x_norm2 = self.norm2(out1)
        ffn_output = self.ffn(x_norm2, training=training)
        ffn_output = self.dropout2(ffn_output, training=training)
        return out1 + ffn_output

    def get_config(self):
        config = super().get_config()
        config.update({
            "embed_dim": self.embed_dim,
            "num_heads": self.num_heads,
            "ff_dim": self.ff_dim,
            "dropout_rate": self.dropout_rate,
        })
        return config


def build_transformer(
    input_shape,
    num_classes,
    embed_dim=128,
    num_heads=8,
    ff_dim=256,
    num_blocks=4,
    dropout_rate=0.20,
    learning_rate=3e-4,
):
    """
    Tuned 4-block, 8-head Transformer for 26-class exercise classification.
    
    Features:
    - 128-dim linear projection from input landmark features
    - Sinusoidal positional encoding
    - 4 stacked Pre-LN Transformer blocks with 8 attention heads
    - Dual average + max pooling over time sequence
    - GELU activation in classification head
    """
    inputs = Input(shape=input_shape)

    # Linear projection to embedding space + positional encoding
    x = Dense(embed_dim)(inputs)
    x = PositionalEncoding(sequence_length=input_shape[0], embed_dim=embed_dim)(x)
    x = Dropout(0.15)(x)

    # Stacked Transformer blocks
    for _ in range(num_blocks):
        x = TransformerBlock(
            embed_dim=embed_dim,
            num_heads=num_heads,
            ff_dim=ff_dim,
            dropout_rate=dropout_rate,
        )(x)

    # Dual temporal pooling: aggregate sequence information
    avg_pool = GlobalAveragePooling1D()(x)
    max_pool = GlobalMaxPooling1D()(x)
    pooled = Concatenate()([avg_pool, max_pool])

    # Dense classification head
    dense1 = Dense(128, activation="gelu")(pooled)
    norm1 = LayerNormalization()(dense1)
    drop1 = Dropout(0.15)(norm1)

    dense2 = Dense(64, activation="gelu")(drop1)
    drop2 = Dropout(0.10)(dense2)

    outputs = Dense(num_classes, activation="softmax")(drop2)

    model = tf.keras.Model(inputs=inputs, outputs=outputs, name="PostureTransformer")
    optimizer = tf.keras.optimizers.Adam(learning_rate=learning_rate, clipnorm=1.0)
    model.compile(
        optimizer=optimizer,
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model
