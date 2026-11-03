"""Experience replay buffer for per-neighbour DQN transitions.

A transition is (state, action, reward, next state, done) where a state is
the padded feature matrix of the candidate neighbours of one router.

Responsible: Bekir Göktepe
"""
import numpy as np
import torch

from agentroute.dqn.model import MAX_DEG


class ReplayBuffer:
    def __init__(self, capacity, n_features, rng):
        self.capacity = capacity
        self.rng = rng
        self.s = np.zeros((capacity, MAX_DEG, n_features), np.float32)
        self.s_mask = np.zeros((capacity, MAX_DEG), bool)
        self.a = np.zeros(capacity, np.int64)
        self.r = np.zeros(capacity, np.float32)
        self.s2 = np.zeros((capacity, MAX_DEG, n_features), np.float32)
        self.s2_mask = np.zeros((capacity, MAX_DEG), bool)
        self.done = np.zeros(capacity, bool)
        self.size = 0
        self.pos = 0

    def push(self, x, a, r, x2, done):
        i = self.pos
        d = min(len(x), MAX_DEG)
        self.s[i] = 0
        self.s[i, :d] = x[:d]
        self.s_mask[i] = False
        self.s_mask[i, :d] = True
        self.a[i] = a
        self.r[i] = r
        self.s2[i] = 0
        self.s2_mask[i] = False
        if x2 is not None and len(x2):
            d2 = min(len(x2), MAX_DEG)
            self.s2[i, :d2] = x2[:d2]
            self.s2_mask[i, :d2] = True
        self.done[i] = done or x2 is None or len(x2) == 0
        self.pos = (self.pos + 1) % self.capacity
        self.size = min(self.size + 1, self.capacity)

    def __len__(self):
        return self.size

    def sample(self, batch):
        idx = self.rng.integers(self.size, size=batch)
        return (torch.from_numpy(self.s[idx]), torch.from_numpy(self.s_mask[idx]),
                torch.from_numpy(self.a[idx]), torch.from_numpy(self.r[idx]),
                torch.from_numpy(self.s2[idx]), torch.from_numpy(self.s2_mask[idx]),
                torch.from_numpy(self.done[idx]))
