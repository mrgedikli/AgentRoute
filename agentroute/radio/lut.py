"""Radio hop model read from results/radio_lut.npz (built with Sionna by experiments/build_radio_lut.py).

The table holds, for a grid of UE-gNB distances, the probability that a packet
is delivered at HARQ attempt 1..max_tx, and the probability that it is dropped
after max_tx attempts. This module needs only numpy, not Sionna.

Written with AI assistance (Claude).
Responsible: Bekir Emre Sarıpınar
"""
import json

import numpy as np


class RadioLUT:
    def __init__(self, path):
        with np.load(path) as z:
            self.distance_m = z["distance_m"]
            self.pmf = z["attempt_pmf"]          # [n_distance, max_tx + 1], last column = dropped
            self.harq_rtt_s = float(z["harq_rtt_ms"]) / 1000.0
            self.meta = json.loads(str(z["meta"]))
        self.max_tx = self.pmf.shape[1] - 1

    def attempt_pmf(self, distance_m):
        """Distribution over [delivered at attempt 1, ..., attempt max_tx, dropped] at this distance."""
        d = min(max(float(distance_m), self.distance_m[0]), self.distance_m[-1])
        p = np.array([np.interp(d, self.distance_m, self.pmf[:, k]) for k in range(self.pmf.shape[1])])
        return p / p.sum()

    def drop_probability(self, distance_m):
        return float(self.attempt_pmf(distance_m)[-1])

    def sample(self, distance_m, u):
        """Outcome for a uniform random number u: (number of attempts used, dropped)."""
        cum = np.cumsum(self.attempt_pmf(distance_m))
        k = int(np.searchsorted(cum, u, side="right"))
        if k >= self.max_tx:
            return self.max_tx, True
        return k + 1, False
