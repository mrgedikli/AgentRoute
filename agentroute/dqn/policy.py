"""DQN policy (AgentRoute): deliver here, or forward to which neighbour.

At every router the shared Q-network scores each possible action and takes the
best one. v2 adds "deliver to the best local agent" as an action, so the
network also decides whether a local match is good enough or a better one is
known further away. That decision is what the reward depends on most.

    reward per decision = -(hop_cost + delay / delay_scale)
    on correct delivery = + deliver_bonus
    on any drop         = - drop_penalty   (TTL, queue, link loss, wrong agent ...)

The next-state value is the max Q over the actions of the next router, which
is the Q-routing update (Boyan & Littman, 1994) with a neural network.

Responsible: Bekir Göktepe (v2 revision written with AI assistance)
"""
from pathlib import Path

import numpy as np
import torch

from agentroute.dqn.gnn import GNNQNet
from agentroute.dqn.model import MAX_DEG, QNet
from agentroute.forwarding import LOCAL, N_FEATURES, Policy, best_local_agent, neighbor_features


def build_model(kind, hidden=64):
    if kind == "gnn":
        return GNNQNet(N_FEATURES, hidden)
    return QNet(N_FEATURES, hidden)


class DQNPolicy(Policy):
    def __init__(self, model, kind="mlp", epsilon=0.0, learner=None, rng=None, reward=None):
        super().__init__(reward)
        self.model = model
        self.kind = kind
        self.name = "agentroute_gnn" if kind == "gnn" else "agentroute"
        self.epsilon = epsilon
        self.learner = learner
        self.rng = rng if rng is not None else np.random.default_rng(0)
        self._cache = None
        self._next = None

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
        return neighbor_features(view, pkt, with_local=True)

    def accept(self, view, pkt):
        """The one decision per router. Returns an agent, or None and remembers the next hop."""
        actions, X = self._features(view, pkt)
        self._cache = None
        self._next = None
        if not actions:
            return None
        if pkt.ttl <= 0:            # the hop budget is used up: delivering is the only option
            a = actions.index(LOCAL)
        elif self.epsilon > 0 and self.rng.random() < self.epsilon:
            a = int(self.rng.integers(len(actions)))
        else:
            a = int(np.argmax(self.q_values(X)))
        pkt.pending = (X, a, view.now)
        if actions[a] == LOCAL:
            return best_local_agent(view, pkt)
        self._next = actions[a]
        return None

    def choose(self, view, pkt):
        return self._next

    def learn(self, X, a, r, pkt, next_view, outcome):
        if self.learner is None:
            return
        if outcome is None:
            actions2, X2 = neighbor_features(next_view, pkt, with_local=True)
            self._cache = (next_view, pkt.pid, actions2, X2)
            self.learner.push(X, a, r, X2, False)
        else:
            self.learner.push(X, a, r, None, True)
