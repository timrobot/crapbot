import logging
logger = logging.getLogger()
logger.propagate = False
logger.setLevel(logging.ERROR)
import numpy as np
import mxnet as mx
from mxnet import nd
if mx.__version__[:3] == "1.4":
  from mxnet.optimizer.optimizer import adam_update
else:
  from mxnet.optimizer import adam_update
import os
from util import Log

# Input format for MLP is the following:
# [batch id, samples, input vec]

def create_weight(shape, ctx=None, weight=None, mean=None, var=None):
  #w = nd.random.normal(scale=0.01, shape=shape, ctx=ctx)
  lim = np.sqrt(6 / (shape[0] + shape[1]))
  w = nd.random.uniform(-lim, lim, shape, "float32", ctx)
  w.attach_grad()
  if weight is not None:
    weight.append(w)
  if mean is not None:
    mean.append(nd.zeros(shape, ctx))
  if var is not None:
    var.append(nd.zeros(shape, ctx))
  return w

class MLP:
  def __init__(self, input_size, hidden=[1], ctx=None, act_type=[None]):
    self.ctx = ctx if ctx is not None else mx.cpu()
    self.input_size = input_size
    self.hidden = [i for i in hidden]
    self.act_type = act_type

    self.weights = []
    self.means = []
    self.vars = []

    for i, size in enumerate(self.hidden):
      w = create_weight([input_size, size], self.ctx, self.weights,
          self.means, self.vars)
      b = create_weight([1, size], self.ctx, self.weights,
          self.means, self.vars)
      input_size = size

  def __call__(self, x):
    theta = self.weights
    idx = 0
    for i in range(len(self.act_type)):
      w = theta[idx * 2]
      b = theta[idx * 2 + 1]
      x = nd.dot(x, w) + b
      if self.act_type[i] is not None:
        x = self.act_type[i](x)
      idx += 1
    return x

  def update(self, lr=3e-4):
    for i in range(len(self.weights)):
      adam_update(weight=self.weights[i], grad=self.weights[i].grad,
          mean=self.means[i], var=self.vars[i], epsilon=1e-5,
          out=self.weights[i], lr=lr, wd=1e-8)

  def copy(self):
    other = MLP(self.input_size, self.hidden, self.ctx, self.act_type)
    for i in range(len(self.weights)):
      other.weights[i][:] = self.weights[i][:]
    return other

  def copy_from(self, other):
    for i in range(len(self.weights)):
      self.weights[i][:] = other.weights[i][:]

  def save(self, fmt):
    fmt = os.path.join(fmt, "%s.npy")
    idx = 0
    for j in range(len(self.weights)):
      fname = (fmt % idx)
      dirs = fname.split("/")
      for i in range(len(dirs)-1):
        fullpath = os.path.join(*dirs[:i+1])
        if not os.path.exists(fullpath):
          os.mkdir(fullpath)
      with open(fname, "wb") as fp:
        np.save(fp, self.weights[j].asnumpy())
      idx += 1

  def load(self, fmt):
    fmt = os.path.join(fmt, "%s.npy")
    idx = 0
    for j in range(len(self.weights)):
      fname = (fmt % idx)
      with open(fname, "rb") as fp:
        try:
          self.weights[j][:] = nd.array(np.load(fp), self.ctx)
        except:
          Log.W("mlp", "Could not load matrix %s" % fname)
      idx += 1
