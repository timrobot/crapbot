import mxnet as mx
from mxnet import nd, autograd
if mx.__version__[:3] == "1.4":
  from mxnet.optimizer.optimizer import adam_update
else:
  from mxnet.optimizer import adam_update
import numpy as np

from util import SimpleReplayBuffer, Log
from mlp import MLP

LOG_STD_MAX = 2.0
LOG_STD_MIN = -20.0

class SAC_v0(object):
  def __init__(self, obs_size=1, action_size=1, batch_size=100,
      hidden=[300], activation=nd.relu, output_activation=None,
      ctx=mx.cpu(), replay_size=int(1e6), lr=lambda t: 1.0, lrmult=1e-3,
      alpha=0.2, gamma=0.99, polyak=0.995):
    """
    Constructor for the SAC algorithm

    Args:
      obs_size: the size of the input observation
      action_size: the size of the input/output action
      batch_size: the size of a batch (only internal)
      hidden: the size of the hidden layers
      activation: the standard activation for the layers
      output_activation: the activation on the policy
      ctx: mx.cpu() or mx.gpu(id)
      replay_size: the amount of steps to store in memory
      lr: the learning rate of the neural network
      lrmult: the initial coefficient
      alpha: the entropy coefficient (higher means more exploration)
      gamma: the discount factor for future rewards
      polyak: the target network learning coefficient
    """
    self.ctx = ctx
    self.obs_size = obs_size
    self.action_size = action_size
    self.batch_size = batch_size
    self.memory = SimpleReplayBuffer(obs_size, action_size, maxlen=replay_size)
    self.lr = lr
    self.lrmult = lrmult
    self.alpha = alpha
    self.gamma = gamma
    self.polyak = polyak
    self.steps = 0

    self.policy_base = MLP(obs_size, hidden, self.ctx,
        [activation for h in hidden])
    self.mu = MLP(obs_size if len(hidden) == 0 else hidden[-1],
        [action_size], self.ctx, [output_activation])
    self.logstd = MLP(obs_size if len(hidden) == 0 else hidden[-1],
        [action_size], self.ctx, [nd.tanh])

    def neglogp(action, mean, logstd):
      assert(mean.shape[-1] == logstd.shape[-1])
      std = nd.exp(logstd) + 1e-8
      return 0.5 * nd.sum(nd.square((action - mean) / std), axis=-1) \
          + 0.5 * np.log(2.0 * np.pi) * action.shape[-1] \
          + nd.sum(logstd, axis=-1)
    self.neglogp = neglogp

    def squash_policy(mu, pi, logp_pi):
      def clip_pass_gradient(x, l=-1., u=1.):
        clip_up = nd.cast(x > u, "float32")
        clip_low = nd.cast(x < l, "float32")
        return x + nd.stop_gradient((u - x) * clip_up +
            (l - x) * clip_low)
      mu = nd.tanh(mu)
      pi = nd.tanh(pi)
      # avoid machine precision error, clip 1-pi**2 to [0, 1]
      logp_pi = logp_pi - nd.sum(nd.log(
        clip_pass_gradient(1 - nd.square(pi), l=0, u=1) + 1e-6), axis=1)
      return mu, pi, logp_pi

    def policy(obs):
      hid = self.policy_base(obs)
      mu = self.mu(hid)
      log_std = self.logstd(hid)
      log_std = LOG_STD_MIN + 0.5 * (LOG_STD_MAX - LOG_STD_MIN) * (log_std + 1)
      std = nd.exp(log_std)
      pi = mu + nd.random.normal(shape=mu.shape, ctx=self.ctx) * std
      logp_pi = -neglogp(pi, mu, log_std)

      mu, pi, logp_pi = squash_policy(mu, pi, logp_pi)
      return mu, pi, logp_pi
    self.policy = policy

    self.vfn = MLP(obs_size, hidden + [1], self.ctx,
        [activation for h in hidden] + [None])
    self.vfn_targ = self.vfn.copy()

    self.qfn1 = MLP(obs_size + action_size, hidden + [1], self.ctx,
        [activation for h in hidden] + [None])
    self.qfn2 = MLP(obs_size + action_size, hidden + [1], self.ctx,
        [activation for h in hidden] + [None])

  def __call__(self, obs, stochastic=True):
    """
    Call the actor on the observation, optionally with some additional noise

    Args:
      obs: the observation
      stochastic: whether or not to return a noisy action

    Returns:
      a (potentially noisy) action
    """
    self.steps += 1
    obs = nd.array(np.expand_dims(obs, 0), self.ctx)
    mu, pi, _ = self.policy(obs)
    action = pi if stochastic else mu
    action = action.asnumpy()[0]
    return np.clip(action, -1, 1)

  def remember(self, obs, action, reward, nextobs, terminal):
    """
    Remember a segment
    
    Args:
      obs: the observation
      action: the committed action
      reward: the reward from doing the action
      nextobs: the observation from doing the action
      terminal: whether or not the episode ended
    """
    self.memory.store(obs, action, reward, nextobs, terminal)

  def fit(self, num_steps=1):
    """
    Fit the models

    Returns:
      Loss Functions (Q1-mse, Q2-mse, alpha-entropy, Policy-kl)
    """
    logger_data = {k: [] for k in ["LossPi", "LossQ1", "LossQ2", "LossV"]}
    for step in range(num_steps):
      # sample a batch from memory
      minibatch = self.memory.sample(self.batch_size)
      obs = nd.array(minibatch["obs"], self.ctx)
      acts = nd.array(minibatch["act"], self.ctx)
      rewards = nd.array(minibatch["rew"], self.ctx)
      next_obs = nd.array(minibatch["next_obs"], self.ctx)
      nonterm = nd.array(minibatch["nt"], self.ctx)

      lr = self.lr(self.steps) * self.lrmult

      # update the policy function
      with autograd.record():
        _mu, _pi, _logp_pi = self.policy(obs)
        _obspi = nd.concat(obs, _pi, dim=-1)
        _q1_pi = self.qfn1(_obspi)
        pi_loss = nd.mean(self.alpha * _logp_pi - _q1_pi)
        pi_loss.backward()
      self.mu.update(lr)
      self.logstd.update(lr)
      self.policy_base.update(lr)

      # update the value functions
      logp_pi = nd.stop_gradient(_logp_pi)
      obspi = nd.stop_gradient(_obspi)
      obsact = nd.concat(obs, acts, dim=-1)
      q1_pi = self.qfn1(obspi)
      q2_pi = self.qfn2(obspi)
      min_q_pi = nd.minimum(q1_pi, q2_pi)
      v_targ = self.vfn_targ(next_obs)
      q_backup = nd.stop_gradient(rewards + self.gamma * nonterm * v_targ)
      v_backup = nd.stop_gradient(min_q_pi - self.alpha * logp_pi)
      with autograd.record():
        _q1 = self.qfn1(obsact)
        _q2 = self.qfn2(obsact)
        _v = self.vfn(obs)

        q1_loss = 0.5 * nd.mean(nd.square(q_backup - _q1))
        q2_loss = 0.5 * nd.mean(nd.square(q_backup - _q2))
        v_loss = 0.5 * nd.mean(nd.square(v_backup - _v))
        total_loss = q1_loss + q2_loss + v_loss
        total_loss.backward()
      self.qfn1.update(lr)
      self.qfn2.update(lr)
      self.vfn.update(lr)

      # update the target network
      for i in range(len(self.vfn.weights)):
        self.vfn_targ.weights[i][:] = \
            self.polyak * self.vfn_targ.weights[i][:] + \
            (1 - self.polyak) * self.vfn.weights[i][:]

      logger_data["LossPi"].append(pi_loss.asnumpy()[0])
      logger_data["LossQ1"].append(q1_loss.asnumpy()[0])
      logger_data["LossQ2"].append(q2_loss.asnumpy()[0])
      logger_data["LossV"].append(v_loss.asnumpy()[0])
    return logger_data

  def save(self, envname):
    self.policy_base.save("models/SAC-v0_" + str(envname) + "/policy_base")
    self.mu.save("models/SAC-v0_" + str(envname) + "/mu")
    self.logstd.save("models/SAC-v0_" + str(envname) + "/logstd")
    self.qfn1.save("models/SAC-v0_" + str(envname) + "/qfn1")
    self.qfn2.save("models/SAC-v0_" + str(envname) + "/qfn2")
    self.vfn.save("models/SAC-v0_" + str(envname) + "/vfn")
    self.vfn_targ.save("models/SAC-v0_" + str(envname) + "/vfn_targ")

  def load(self, envname):
    self.policy_base.load("models/SAC-v0_" + str(envname) + "/policy_base")
    self.mu.load("models/SAC-v0_" + str(envname) + "/mu")
    self.logstd.load("models/SAC-v0_" + str(envname) + "/logstd")
    self.qfn1.load("models/SAC-v0_" + str(envname) + "/qfn1")
    self.qfn2.load("models/SAC-v0_" + str(envname) + "/qfn2")
    self.vfn.load("models/SAC-v0_" + str(envname) + "/vfn")
    self.vfn_targ.load("models/SAC-v0_" + str(envname) + "/vfn_targ")
