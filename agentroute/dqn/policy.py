"""DQN next-hop policy (AgentRoute).

At every router the shared Q-network scores each candidate neighbour and the
packet goes to the best one. During training the policy explores with
epsilon-greedy and hands every finished decision to the learner:

    reward per hop   = -(hop_cost + hop_delay / delay_scale)
    on delivery      = + deliver_bonus
    on any drop      = - drop_penalty   (TTL, queue, link loss, wrong agent ...)

The next-state value is the max Q over the neighbours of the next router,
which is the Q-routing update (Boyan & Littman, 1994) with a neural network.

Responsible: Bekir Göktepe
"""
from pathlib import Path

import numpy as np
import torch

from agentroute.dqn.gnn import GNNQNet
from agentroute.dqn.model import MAX_DEG, QNet
from agentroute.forwarding import N_FEATURES, Policy, neighbor_features

DEFAULT_REWARD = {"hop_cost": 0.05, "delay_scale_s": 0.1, "deliver_bonus": 1.0, "drop_penalty": 1.0}


def build_model(kind, hidden=64):
    if kind == "gnn":
        return GNNQNet(N_FEATURES, hidden)
    return QNet(N_FEATURES, hidden)


class DQNPolicy(Policy):
    def __init__(self, model, kind="mlp", epsilon=0.0, learner=None, rng=None, reward=None):
        self.model = model
        self.kind = kind
        self.name = "agentroute_gnn" if kind == "gnn" else "agentroute"
        self.epsilon = epsilon
        self.learner = learner
        self.rng = rng if rng is not None else np.random.default_rng(0)
        self.reward = reward or DEFAULT_REWARD
        self._cache = None
        self.episode_return = 0.0

    @classmethod
    def load(cls, path, kind="mlp"):
        ckpt = torch.load(Path(path), map_location="cpu", weights_only=True)
        model = build_model(kind, ckpt["hidden"])
        model.load_state_dict(ckpt["state_dict"])
        model.eval()
        return cls(model, kind=kind)

    def save(self, path, hidden):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        torch.save({"state_dict": self.model.state_dict(), "hidden": hidden, "kind": self.kind}, path)

    def q_values(self, X):
        d = min(len(X), MAX_DEG)
        x = torch.zeros((1, MAX_DEG, X.shape[1]))
        x[0, :d] = torch.from_numpy(X[:d])
        mask = torch.zeros((1, MAX_DEG), dtype=torch.bool)
        mask[0, :d] = True
        with torch.no_grad():
            return self.model(x, mask)[0, :d].numpy()

    def _features(self, view, pkt):
        if self._cache is not None and self._cache[0] is view and self._cache[1] == pkt.pid:
            return self._cache[2], self._cache[3]
        return neighbor_features(view, pkt)

    def choose(self, view, pkt):
        cands, X = self._features(view, pkt)
        self._cache = None
        if not cands:
            return None
        if self.epsilon > 0 and self.rng.random() < self.epsilon:
            a = int(self.rng.integers(len(cands)))
        else:
            a = int(np.argmax(self.q_values(X)))
        pkt.pending = (X, a, view.now)
        return cands[a]

    def observe(self, pkt, now, next_view, outcome):
        """Compute the reward of the last decision; store the transition when training."""
        if pkt.pending is None:
            return
        X, a, t0 = pkt.pending
        pkt.pending = None
        rw = self.reward
        r = -(rw["hop_cost"] + (now - t0) / rw["delay_scale_s"])
        if outcome is not None:
            r += rw["deliver_bonus"] if outcome == "deliver" else -rw["drop_penalty"]
        self.episode_return += r
        if self.learner is None:
            return
        if outcome is None:
            cands2, X2 = neighbor_features(next_view, pkt)
            self._cache = (next_view, pkt.pid, cands2, X2)
            self.learner.push(X, a, r, X2, False)
        else:
            self.learner.push(X, a, r, None, True)
