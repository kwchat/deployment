import tensorflow as tf
import tensorflow_hub as hub
import kerastuner as kt

embedding_dim = 50

class ChatModel(tf.keras.Model):
  def __init__(self, vocab_size):
    super().__init__(self)
    self.embedding = hub.KerasLayer("https://tfhub.dev/google/nnlm-ko-dim50-with-normalization/2",
                           input_shape=[], dtype=tf.string)
    self.gru = tf.keras.layers.GRU(embedding_dim,
                                   return_sequences=True,
                                   return_state=True)
    self.dense = tf.keras.layers.Dense(vocab_size)

  def call(self, inputs, states=None, return_state=False, training=False):
    x = inputs
    x = self.embedding(x, training=training)
    if states is None:
      states = self.gru.get_initial_state(x)
    x, states = self.gru(x, initial_state=states, training=training)
    x = self.dense(x, training=training)

    if return_state:
      return x, states
    else:
      return x