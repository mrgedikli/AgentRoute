"""Q-network shared by all routers.

The number of neighbours differs from router to router, so the network does
not output one Q-value per action. Instead it scores each action on its own:
input = the feature vector of one action (a neighbour, or "deliver here"),
output = one Q-value. The action with the highest score is taken.

Batches are padded to a fixed maximum degree; `mask` marks real neighbours.

Responsible: Bekir Göktepe
"""
import torch
from torch import nn

MAX_DEG = 32
NEG = -1e9


class QNet(nn.Module):
    def __init__(self, n_features, hidden=64):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(n_features, hidden), nn.ReLU(),
            nn.Linear(hidden, hidden), nn.ReLU(),
            nn.Linear(hidden, 1),
        )

    def forward(self, x, mask):
        """x: (B, D, F) neighbour features, mask: (B, D) bool -> Q: (B, D)."""
        q = self.net(x).squeeze(-1)
        return q.masked_fill(~mask, NEG)
