"""GNN variant of the Q-network.

The plain QNet scores every neighbour in isolation. Here each neighbour is
first embedded, then the embeddings of all neighbours are pooled (mean and
max) into a context vector, i.e. one round of message passing on the local
star graph "router <-> its neighbours". The score of a neighbour can then
depend on the alternatives (e.g. "this path is congested, but so are all the
others").

Responsible: Bekir Göktepe
"""
import torch
from torch import nn

from agentroute.dqn.model import NEG


class GNNQNet(nn.Module):
    def __init__(self, n_features, hidden=64):
        super().__init__()
        self.encode = nn.Sequential(nn.Linear(n_features, hidden), nn.ReLU(),
                                    nn.Linear(hidden, hidden), nn.ReLU())
        self.score = nn.Sequential(nn.Linear(3 * hidden, hidden), nn.ReLU(),
                                   nn.Linear(hidden, 1))

    def forward(self, x, mask):
        h = self.encode(x)                                     # (B, D, H)
        m = mask.unsqueeze(-1).float()
        mean = (h * m).sum(dim=1) / m.sum(dim=1).clamp(min=1.0)
        mx = h.masked_fill(~mask.unsqueeze(-1), NEG).max(dim=1).values
        mx = torch.where(mask.any(dim=1, keepdim=True), mx, torch.zeros_like(mx))
        ctx = torch.cat([mean, mx], dim=-1).unsqueeze(1).expand(-1, h.shape[1], -1)
        q = self.score(torch.cat([h, ctx], dim=-1)).squeeze(-1)
        return q.masked_fill(~mask, NEG)
