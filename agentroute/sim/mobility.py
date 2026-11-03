"""Random-waypoint mobility and handover decisions.

Random waypoint: a node picks a random destination in the area, moves there in
a straight line at its own speed, pauses, and repeats (Camp et al., 2002).

Handover: a UE is attached to the nearest gNB, but it only switches when the
new gNB is clearly closer (hysteresis), which avoids ping-pong at cell edges.

Responsible: Ömer Faruk Gedikli
"""
import numpy as np


class RandomWaypoint:
    def __init__(self, n, bounds, speed, pause, rng):
        xmin, ymin, xmax, ymax = bounds
        self.low = np.array([xmin, ymin])
        self.high = np.array([xmax, ymax])
        self.rng = rng
        self.pos = rng.uniform(self.low, self.high, size=(n, 2))
        self.dest = rng.uniform(self.low, self.high, size=(n, 2))
        self.speed = speed * rng.uniform(0.5, 1.5, size=n)
        self.pause = pause
        self.pause_left = np.zeros(n)

    def step(self, dt):
        moving = self.pause_left <= 0
        self.pause_left[~moving] -= dt
        delta = self.dest - self.pos
        dist = np.linalg.norm(delta, axis=1)
        travel = self.speed * dt
        arrive = moving & (dist <= travel)
        go = moving & ~arrive
        self.pos[go] += delta[go] / dist[go, None] * travel[go, None]
        self.pos[arrive] = self.dest[arrive]
        n_arrive = int(arrive.sum())
        if n_arrive:
            self.pause_left[arrive] = self.pause
            self.dest[arrive] = self.rng.uniform(self.low, self.high, size=(n_arrive, 2))


def nearest_cell(points, cell_xy, alive=None):
    d = np.linalg.norm(points[:, None, :] - cell_xy[None, :, :], axis=2)
    if alive is not None:
        d[:, ~alive] = np.inf
    return np.argmin(d, axis=1)


def handover_targets(points, current, cell_xy, alive, hysteresis):
    """Return the cell each UE should be attached to after this step."""
    d = np.linalg.norm(points[:, None, :] - cell_xy[None, :, :], axis=2)
    d[:, ~alive] = np.inf
    best = np.argmin(d, axis=1)
    rows = np.arange(len(points))
    d_best = d[rows, best]
    d_cur = d[rows, current]
    switch = (best != current) & (d_best < (1.0 - hysteresis) * d_cur)
    return np.where(switch, best, current)
