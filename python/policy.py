import gym
import numpy as np
import mxnet as mx
from mxnet import nd
import time
import os
import sys
import random

# Create a Wrapper around the SAC algorithm and embed for policy inference
class FastCamPolicy:
  def __init__(self):
    self.ctx = mx.gpu(0)
    # need resnet18 and wavenet instances, tuned to the current environment
    self.embedding_net = ResNet18(shape=(640, 360), output_size=64, ctx=self.ctx)
    self.recurrent_net = Wavenet(input_size=66, timesteps=8, output_size=128, ctx=self.ctx)
    self.policy_net = SAC_v0(obs_size=128, action_size=2, batch_size=1, ctx=self.ctx)
    embed = self.embedding_net(nd.array(np.zeros((640, 360, 3)), self.ctx))
    action = nd.array(np.zeros((1, 2)), self.ctx)
    self.embed_queue = [(embed, action)]
    self.prev_action = action

  def __call__(self, color_frame):
    embed = self.embedding_net(color_frame)
    self.embed_queue = self.embed_queue[1:] + [(embed, self.prev_action)]
    sequence = [nd.concat(x[0], x[1], dim=-1) for x in self.embed_queue]
    encoding = self.recurrent_net(sequence)
    action = self.policy_net(encoding)
    return action.asnumpy()
