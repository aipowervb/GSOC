from functools import partial
import tensorflow as tf
from lib import utils


class RRDBNet(tf.keras.Model):
  def __init__(
          self,
          out_channel,
          num_features=32,
          trunk_size=3,
          growth_channel=32,
          use_bias=True):
    super(RRDBNet, self).__init__()
    self.rrdb_block = partial(utils.RRDB, growth_channel)
    conv = partial(tf.keras.layers.Conv2D, kernel_size=[3, 3],
                   strides=[1, 1],
                   padding="same",
                   use_bias=use_bias)
    self.conv_first = conv(filters=num_features)
    self.rdb_trunk = tf.keras.Sequential(
        [self.rrdb_block() for _ in range(trunk_size)])
    self.conv_trunk = conv(filters=num_features)
    # Upsample
    self.upsample1 = conv(filters=num_features)
    self.upsample2 = conv(filters=num_features)
    self.conv_last_1 = conv(filters=num_features)
    self.conv_last_2 = conv(filters=out_channel)

    self.lrelu = tf.keras.layers.LeakyReLU(alpha=0.2)

  def call(self, input_):
    feature = self.conv_first(input_)
    trunk = self.conv_trunk(self.rdb_trunk(feature))
    feature = trunk + feature
    feature = self.lrelu(
        self.upsample1(
            tf.nn.depth_to_space(
                feature,
                block_size=2)))
    feature = self.lrelu(
        self.upsample2(
            tf.nn.depth_to_space(
                feature,
                block_size=2)))
    feature = self.lrelu(self.conv_last_1(feature))
    out = self.conv_last_2(feature)
    return out


class VGGArch(tf.keras.Model):
  def __init__(self, output_shape=1, num_features=64, use_bias=True):

    super(VGGArch, self).__init__()
    self.conv = lambda n, s, x: tf.keras.layers.Conv2D(
        n, kernel_size=[3, 3], strides=[s, s], use_bias=use_bias)(x)
    self.num_features = num_features
    self.lrelu = tf.keras.layers.LeakyReLU(alpha=0.2)
    self.batch_norm = lambda x: tf.keras.layers.BatchNormalization()(x)
    self.dense = tf.keras.layers.Dense
    self._output_shape = output_shape
  def call(self, input_):

    features = self.lrelu(self.conv(self.num_features, 1, input_))
    features = self.lrelu(self.batch_norm(self.conv(self.num_features, 2, features)))
    # VGG Trunk
    for i in range(1, 4):
      for j in range(1, 3):
        features = self.lrelu(
            self.batch_norm(
                self.conv(2**i * self.num_features, j, features)))

    flattened = tf.keras.layers.Flatten()(features)
    dense = self.lrelu(self.dense(1024)(flattened))
    out = self.dense(self._output_shape)(dense)
    return out