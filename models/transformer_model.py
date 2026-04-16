import tensorflow as tf
from tensorflow.keras.layers import Dense, Dropout, LayerNormalization, MultiHeadAttention


class TransformerBlock(tf.keras.layers.Layer):
    def __init__(self, embed_dim, num_heads, ff_dim):
        super().__init__()
        self.att = MultiHeadAttention(num_heads=num_heads, key_dim=embed_dim)
        self.ffn = tf.keras.Sequential([
            Dense(ff_dim, activation="relu"),
            Dropout(0.2),
            Dense(embed_dim),
        ])
        self.norm1 = LayerNormalization()
        self.norm2 = LayerNormalization()

    def call(self, inputs):
        attn_output = self.att(inputs, inputs)
        out1 = self.norm1(inputs + attn_output)
        ffn_output = self.ffn(out1)
        return self.norm2(out1 + ffn_output)


def build_transformer(input_shape, num_classes):
    inputs = tf.keras.Input(shape=input_shape)
    # Project raw pose-angle features to the transformer embedding size
    # before applying residual attention blocks.
    x = Dense(64)(inputs)
    x = TransformerBlock(64, 4, 128)(x)
    x = Dropout(0.2)(x)
    x = tf.keras.layers.GlobalAveragePooling1D()(x)
    outputs = Dense(num_classes, activation="softmax")(x)
    model = tf.keras.Model(inputs, outputs)
    model.compile(
        optimizer="adam",
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model
