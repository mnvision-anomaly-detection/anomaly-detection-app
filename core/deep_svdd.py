import tensorflow as tf
import numpy as np
from math import ceil
from tensorflow import keras
from tqdm import tqdm
import h5py

class DeepSVDD:
    def __init__(self, keras_model=None, input_shape=(128, 128, 3), objective='one-class',
                 nu=0.1, representation_dim=32, batch_size=128, lr=1e-3):
        self.nu = nu
        self.representation_dim = representation_dim
        self.R = tf.Variable(0.0, dtype=tf.float32, trainable=False, name='R')
        self.c = tf.Variable(tf.zeros([self.representation_dim], dtype=tf.float32), trainable=False, name='c')
        self.batch_size = batch_size
        self.lr = lr
        self.objective = objective

        if keras_model is None:
            self.keras_model = self._build_model(input_shape)
        else:
            self.keras_model = keras_model

        self.keras_model.compile(optimizer=keras.optimizers.Adam(learning_rate=lr), loss='mse')

    def fit(self, X_train, epochs=10, verbose=True, batch_size=None, learning_rate=None, nu=None):
        if batch_size is not None:
            self.batch_size = batch_size
        if learning_rate is not None:
            self.lr = learning_rate
        if nu is not None:
            self.nu = nu

        N = X_train.shape[0]
        BS = self.batch_size
        BN = int(ceil(N / BS))

        self._init_c(X_train)

        self.keras_model.compile(optimizer=keras.optimizers.Adam(learning_rate=self.lr), loss='mse')

        for i_epoch in range(epochs):
            ind = np.random.permutation(N)
            x_train = X_train[ind]
            g_batch = tqdm(range(BN)) if verbose else range(BN)

            for i_batch in g_batch:
                x_batch = x_train[i_batch * BS: (i_batch + 1) * BS]

                with tf.GradientTape() as tape:
                    latent_outputs = self.keras_model(x_batch, training=True)
                    dist = tf.reduce_sum(tf.square(latent_outputs - self.c), axis=-1)

                    if self.objective == 'soft-boundary':
                        score = dist - self.R ** 2
                        penalty = tf.maximum(score, 0.0)
                        loss = self.R ** 2 + (1 / self.nu) * tf.reduce_mean(penalty)
                    else:
                        loss = tf.reduce_mean(dist)

                grads = tape.gradient(loss, self.keras_model.trainable_variables)
                self.keras_model.optimizer.apply_gradients(zip(grads, self.keras_model.trainable_variables))

                if self.objective == 'soft-boundary':
                    self.R.assign(self._get_R(dist.numpy(), self.nu))

            if verbose:
                print(f"Epoch: {i_epoch:3d} Loss: {loss.numpy():.4f}")

    def predict(self, X):
        latent_outputs = self.keras_model.predict(X, batch_size=self.batch_size)
        scores = np.sum((latent_outputs - self.c) ** 2, axis=1)
        return scores

    def _init_c(self, X, eps=1e-3):
        latent_outputs = self.keras_model.predict(X, batch_size=self.batch_size)
        c = np.mean(latent_outputs, axis=0)
        c[(np.abs(c) < eps) & (c < 0)] = -eps
        c[(np.abs(c) < eps) & (c > 0)] = eps
        self.c = tf.Variable(c, dtype=tf.float32)

    def _get_R(self, dist, nu):
        return np.quantile(np.sqrt(dist), 1 - nu)

    def save_model(self, filepath):
        self.keras_model.save(filepath)
        with h5py.File(filepath, 'a') as f:
            if 'R' in f:
                del f['R']
            if 'c' in f:
                del f['c']
            f.create_dataset('R', data=self.R.numpy())
            f.create_dataset('c', data=self.c.numpy())

    