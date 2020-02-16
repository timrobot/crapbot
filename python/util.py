import os
import numpy as np
import time
import datetime
import math
import random
import matplotlib.pyplot as plt

class Log:
  VERBOSE = 5
  DEBUG = 4
  INFO = 3
  WARNING = 2
  ERROR = 1
  NONE = 0
  __log_level = VERBOSE
  __fp = None

  @staticmethod
  def setLevel(lvl):
    Log.__log_level = lvl

  @staticmethod
  def timestr():
    t = time.time()
    msec = str(int(t * 1000) % 1000)
    s = datetime.datetime.fromtimestamp(t).strftime("%Y-%m-%d::%H:%M:%S")
    m = "." + ("0" * (3 - len(msec))) + msec
    return s + m + (" " * (22 - len(s)))

  @staticmethod
  def __call__(s):
    print("\033[01;35m[V] %s[%s]  %s\x1b[0m" % (Log.timestr(), "log", str(s)))
    if Log.__fp:
      Log.__fp.write("%s\n" % s)

  @staticmethod
  def V(tag, s):
    if Log.__log_level >= Log.VERBOSE:
      print("\033[01;34m[V] %s[%s]  %s\x1b[0m" % (Log.timestr(), tag, str(s)))
      if Log.__fp:
        Log.__fp.write("%s\n" % s)

  @staticmethod
  def D(tag, s):
    if Log.__log_level >= Log.DEBUG:
      print("\033[01;36m[D] %s[%s]  %s\x1b[0m" % (Log.timestr(), tag, str(s)))
      if Log.__fp:
        Log.__fp.write("%s\n" % s)

  @staticmethod
  def I(tag, s):
    if Log.__log_level >= Log.INFO:
      print("\033[01;32m[I] %s[%s]  %s\x1b[0m" % (Log.timestr(), tag, str(s)))
      if Log.__fp:
        Log.__fp.write("%s\n" % s)

  @staticmethod
  def W(tag, s):
    if Log.__log_level >= Log.WARNING:
      print("\033[01;33m[W] %s[%s]  %s\x1b[0m" % (Log.timestr(), tag, str(s)))
      if Log.__fp:
        Log.__fp.write("%s\n" % s)

  @staticmethod
  def E(tag, s):
    if Log.__log_level >= Log.ERROR:
      print("\033[01;31m[E] %s[%s]  %s\x1b[0m" % (Log.timestr(), tag, str(s)))
      if Log.__fp:
        Log.__fp.write("%s\n" % s)

  @staticmethod
  def setFile(fname):
    Log.__fp = open(fname, "w")

class InlineProgressBar(object):
  def __init__(self, batch_size, num_data, length=80):
    self.bar_len = length
    self.total = int(num_data / batch_size)

  def __call__(self, param):
    """Callback to Show progress bar."""
    count = param.nbatch
    prefix = "" if (count == 0) else "\r\033[F"
    prefix += "\033[01;32mEpoch %d\x1b[0m: " % param.epoch
    filled_len = int(round(self.bar_len * count / float(self.total)))
    percents = math.ceil(100.0 * count / float(self.total))
    prog_bar = "=" * filled_len
    if filled_len != self.bar_len:
      prog_bar += ">"
    if filled_len < self.bar_len - 1:
      prog_bar += " " * (self.bar_len - filled_len - 1)
    print("%s[%s] %s%s\r" % (prefix, prog_bar, percents, "%"))

class ProgressBar:
  def __init__(self, units=30, maxval=100):
    self.units = units
    self.maxval = maxval
    print("")

  def printProgress(self, val, prefix="Progress", suffix=""):
    progress = (val + 1) * self.units // self.maxval
    progbar = "\r\033[F" + prefix + ": ["
    for i in range(progress):
      progbar += "="
    if progress != self.units:
      progbar += ">"
    for i in range(self.units - progress - 1):
      progbar += " "
    progbar += "] " + suffix
    print(progbar)

class LossWindow:
  def __init__(self, units=100, name="Loss Window"):
    self.units = units
    self.data = clist(maxlen=units)
    self.name = name

  def append(self, train_err, eval_err=0):
    self.data.append([train_err, eval_err])

  def render(self, pause=1e-4):
    err_curve = self.data.tail(self.units)
    train_err = [e[0] for e in err_curve]
    eval_err = [e[1] for e in err_curve]

    window = plt.figure(self.name)
    window.clear()
    plt.plot(np.array(range(len(train_err))), train_err, "r-",
             np.array(range(len(eval_err))), eval_err, "b-")
    plt.legend(["Train", "Eval"])
    if pause is not None:
      plt.pause(pause)

class SimpleReplayBuffer:
  def __init__(self, obs_size, action_size, maxlen=10):
    self.__D__ = [np.zeros([maxlen, s], dtype=np.float32) \
        for s in [obs_size, action_size, 1, obs_size, 1]]
    self.__idx__ = 0
    self.__size__ = 0
    self.__max_size__ = maxlen

  def store(self, obs, action, reward, next_obs, done):
    data = [obs, action, reward, next_obs, 1 - done]
    for i in range(len(data)):
      self.__D__[i][self.__idx__] = data[i]
    self.__idx__ = (self.__idx__ + 1) % self.__max_size__
    self.__size__ = min(self.__size__ + 1, self.__max_size__)

  def sample(self, n=1):
    idxs = np.random.randint(0, self.__size__, size=n)
    names = ["obs", "act", "rew", "next_obs", "nt"]
    return { k: self.__D__[i][idxs] for i, k in enumerate(names) }

class clist:
  def __init__(self, maxlen=16, fname=None):
    self.__D__ = [None] * maxlen
    self.__idx__ = 0
    self.__size__ = 0
    self.__max_size__ = maxlen

    self.__fp__ = None
    i = 0
    if fname:
      if not "clist" in os.listdir("."):
        os.mkdir("clist")
      filename = fname + "_0"
      while filename in os.listdir("./clist/"):
        i += 1
        filename = fname + "_" + str(i)
      self.__fp__ = open("./clist/" + filename, "w")

  def __del__(self):
    if self.__fp__:
      for i in range(self.__size__):
        j = (self.__idx__ + i) % self.__size__
        self.__fp__.write(str(self.__D__[j]) + "\n")
      self.__fp__.close()

  def __len__(self):
    return self.__size__

  def __getitem__(self, idx):
    if isinstance(idx, list):
      return [self.__D__[i] for i in idx]
    elif isinstance(idx, int):
      return self.__D__[idx]
    else:
      raise IOError("Bad argument")

  def append(self, x):
    if self.__size__ == self.__max_size__:
      if self.__fp__:
        self.__fp__.write(str(x) + "\n")
    else:
      self.__size__ += 1
    self.__D__[self.__idx__] = x
    self.__idx__ = (self.__idx__ + 1) % self.__max_size__

  def clear(self):
    self.__D__ = [None] * self.__max_size__
    self.__idx__ = 0
    self.__size__ = 0

  def sample(self, n, length=0):
    if length == 0:
      if n > self.__size__:
        return self.__D__[:self.__size__]
      else:
        return random.sample(self.__D__[:self.__size__], n)
    elif n > (self.__size__ - length + 1):
      # there is a bug here: what if the data rotates and the number of
      # particles is greater than max_size?
      m = max(0, self.__size__ - length + 1)
      return [self.__D__[s:self.__size__ - s + 1] for s in range(m)]
    else:
      return random.sample(self.__D__[:self.__size__], n)

  def tail(self, n):
    if n > self.__size__:
      return self.__D__[:self.__size__]
    elif self.__idx__ < n:
      items = self.__D__[self.__idx__ - n:]
      items += self.__D__[:n - len(items)]
      return items
    else:
      return self.__D__[self.__idx__ - n:self.__idx__]

def RotateX(v, degrees):
  """
  Rotate a vector around the x axis.

  Args:
    v: Source vector (3xn)
    degrees: The right-hand degrees to rotate by

  Returns:
    Rotated vector, same size as the input
  """
  r = math.radians(degrees)
  cr = math.cos(r)
  sr = math.sin(r)
  return np.array([
    [1, 0, 0],
    [0, cr, -sr],
    [0, sr, cr]])

def RotateY(v, degrees):
  """
  Rotate a vector around the y axis.

  Args:
    v: Source vector (3xn)
    degrees: The right-hand degrees to rotate by

  Returns:
    Rotated vector, same size as the input
  """
  r = math.radians(degrees)
  cr = math.cos(r)
  sr = math.sin(r)
  return np.array([
    [cr, 0, sr],
    [0, 1, 0],
    [-sr, 0, cr]])

def RotateZ(v, degrees):
  """
  Rotate a vector around the z axis.

  Args:
    v: Source vector (3xn)
    degrees: The right-hand degrees to rotate by

  Returns:
    Rotated vector, same size as the input
  """
  r = math.radians(degrees)
  cr = math.cos(r)
  sr = math.sin(r)
  return np.array([
    [cr, 0, sr],
    [0, 1, 0],
    [-sr, 0, cr]])

def Rotate(v, degreesList, axisList):
  """
  Rotate a vector around the x, y, and z axes, which are provided on the axes
  list.

  Args:
    v: Source vector (3xn)
    degrees: The right-hand degrees to rotate by, provided as a list
    axisList: The axis on which to apply the rotations on

  Returns:
    Rotated vector, same size as the input
  """
  for i in range(len(axisList) - 1, -1, -1):
    if axisList[i] == "x":
      v = RotateX(v, degreesList[i])
    elif axisList[i] == "y":
      v = RotateY(v, degreesList[i])
    elif axisList[i] == "z":
      v = RotateZ(v, degreesList[i])
  return v

def Transform(v, degreesList, axisList, translations):
  """
  Rotate a vector around the x, y, and z axes, which are provided on the axes
  list. Each rotation is subsequently followed by a given translation respective
  to their frame of reference.

  Args:
    v: Source vector (3xn)
    degrees: The right-hand degrees to rotate by, provided as a list
    axisList: The axis on which to apply the rotations on
    translations: The translation of the vector on the frame of reference

  Returns:
    Transformed vector, same size as the input
  """
  for i in range(len(axisList) - 1, -1, -1):
    if axisList[i] == "x":
      v = RotateX(v, degreesList[i])
    elif axisList[i] == "y":
      v = RotateY(v, degreesList[i])
    elif axisList[i] == "z":
      v = RotateZ(v, degreesList[i])
    v += translations[i]
  return v

class DiscreteSpace:
  def __init__(self, ranges=[], intervals=[]):
    self.ranges = np.array(ranges, dtype=np.float32)
    self.diff = self.ranges[:, 1] - self.ranges[:, 0]
    self.intervals = np.array(intervals, dtype=np.float32)
    assert len(self.ranges.shape) == 2
    assert len(self.intervals.shape) == 1
    assert self.ranges.shape[0] == self.intervals.shape[0]
    self.bins = ((self.ranges[:,1] - self.ranges[:,0]) / self.intervals)\
        .astype(np.int) + 1
    self.d = len(self.bins)
    self.n = np.prod(self.bins)
    self.all = self.permutate()

  def permutate(self):
    idx = np.array(np.meshgrid(*[range(i) for i in self.bins])).T\
        .reshape(-1, self.d)
    return np.multiply(idx, self.intervals) + self.ranges[:,0]

  def __call__(self, idx):
    return self.all[idx]

  def continuous(self, value):
    v = self.all[value]
    v = (v - self.ranges[:, 0]) / self.diff * 2.0 - 1.0
    return v

class ContinuousSpace:
  def __init__(self, ranges=[]):
    self.ranges = np.array(ranges, dtype=np.float32)
    assert len(self.ranges.shape) == 2
    self.diff = self.ranges[:, 1] - self.ranges[:, 0]
    self.d = len(self.ranges)
    self.n = self.d
  
  def __call__(self, v): # map from [-1, 1]
    return (v + 1.0) / 2.0 * self.diff + self.ranges[:, 0]

  def continuous(self, value):
    return value

  def sample(self):
    return self.__call__(np.random.rand(self.n) * 2 - 1)

class CosineLearningRate:
  def __init__(self, lr_min=1e-7, lr_max=1e-7, T_interval=100):
    self.lr_min = lr_min
    self.lr_max = lr_max
    self.T_interval = T_interval
    self.steps = 0

  def __call__(self, steps=None):
    lr = self.lr_min + 0.5 * (self.lr_max - self.lr_min) \
        * (1 + np.cos(self.steps / self.T_interval * np.pi))
    if steps is None:
      self.steps += 1
    else:
      self.steps = steps
    return lr
