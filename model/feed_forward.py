import tensorflow as tf
from tensorflow import layers


class Model:

    def __init__(self, a_len, a_dimension, obs_dimension, is_continuous, a_bound):
        self.a_len = a_len
        self.a_bound = a_bound
        self.obs_dimension = obs_dimension
        self.a_dimension = a_dimension
        self.is_continuous = is_continuous
        self.num_unit = 100

    def discrete_policy_output_layer(self, fc1, train):
        return layers.dense(fc1, units=2, activation=tf.nn.softmax, trainable=train)

    def continuous_policy_output_layer(self, fc1, train):
        log_sigma = tf.get_variable(name="pi_sigma", shape=1, initializer=tf.zeros_initializer(), trainable=train)
        bound = (self.a_bound[1] - self.a_bound[0]) / 2
        mu = tf.layers.dense(fc1, units=1, activation=tf.nn.tanh, trainable=train) * bound
        policy_out = tf.contrib.distributions.Normal(loc=mu, scale=tf.maximum(tf.exp(log_sigma), 0.0))
        return policy_out

    def value_output_layer(self, fc1, train):
        value_out = layers.dense(fc1, units=1, trainable=train)
        return value_out

    def make_actor_network(self, input_opr, name, train=True):
        with tf.variable_scope(name):
            fc1 = layers.dense(input_opr, units=self.num_unit, activation=tf.nn.relu6,
                               trainable=train)
            if self.is_continuous:
                policy_out = self.continuous_policy_output_layer(fc1, train)
            else:
                policy_out = self.discrete_policy_output_layer(fc1, train)

        params = tf.get_collection(tf.GraphKeys.GLOBAL_VARIABLES, scope=name)
        return policy_out, params

    def make_critic_network(self, input_opr, name, train=True):
        with tf.variable_scope(name):
            fc1 = layers.dense(input_opr, units=self.num_unit, activation=tf.nn.relu6, trainable=train)
            value_out = self.value_output_layer(fc1, train)
        params = tf.get_collection(tf.GraphKeys.GLOBAL_VARIABLES, scope=name)
        return value_out, params
