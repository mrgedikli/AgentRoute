"""Tests for the radio link table and the radio.model switch.

Written with AI assistance (Claude).
"""
import json

import numpy as np

from agentroute.config import ROOT, load_config
from agentroute.radio import RadioLUT
from agentroute.sim.simulator import Simulator

LUT = ROOT / "results" / "radio_lut.npz"


def small_cfg(model):
    return load_config(overrides={"agents": {"n_agents": 100}, "sim": {"duration_s": 8.0},
                                  "radio": {"model": model}})


def test_lut_drop_probability_never_improves_with_distance():
    lut = RadioLUT(LUT)
    d = np.linspace(0, 600, 200)
    drop = np.array([lut.drop_probability(x) for x in d])
    assert np.all(np.diff(drop) >= -1e-12)
    assert drop[0] < 0.01 and drop[-1] > 0.3


def test_lut_is_defined_at_the_edges_and_sums_to_one():
    lut = RadioLUT(LUT)
    for d in (0.0, 1.0, 1e5):
        p = lut.attempt_pmf(d)
        assert len(p) == lut.max_tx + 1
        assert abs(p.sum() - 1.0) < 1e-9 and (p >= 0).all()


def test_lut_sampling_matches_the_table():
    lut = RadioLUT(LUT)
    u = (np.arange(20000) + 0.5) / 20000
    for d in (50.0, 250.0, 450.0):
        outcomes = [lut.sample(d, x) for x in u]
        drops = np.mean([o[1] for o in outcomes])
        assert abs(drops - lut.drop_probability(d)) < 0.01
        assert all(1 <= k <= lut.max_tx for k, _ in outcomes)


def _fixed_radio(self, agent=None):
    """The radio hop as it was before the Sionna model existed: fixed delay and loss."""
    topo = self.cfg["topology"]
    yield self.env.timeout(topo["delay_ms"]["radio"] / 1000.0)
    if self.rng_net.random() < topo["loss"]["radio"]:
        return "link"
    return None


def test_constant_model_is_identical_to_the_original_fixed_radio(monkeypatch):
    """Compared on the same machine, so the check does not depend on platform-specific float results."""
    methods = ("agentroute", "agentroute_gnn", "greedy", "greedy_load", "spfr", "flooding",
               "registry", "registry3", "chord", "sdht")
    current = {m: json.loads(json.dumps(Simulator(small_cfg("constant"), m, seed=1).run(), default=str))
               for m in methods}
    monkeypatch.setattr(Simulator, "radio", _fixed_radio)
    for m in methods:
        original = json.loads(json.dumps(Simulator(small_cfg("constant"), m, seed=1).run(), default=str))
        assert current[m] == original, m


def test_sionna_model_is_deterministic_and_differs_from_constant():
    a = Simulator(small_cfg("sionna"), "greedy", seed=2).run()
    b = Simulator(small_cfg("sionna"), "greedy", seed=2).run()
    assert a == b
    assert a != Simulator(small_cfg("constant"), "greedy", seed=2).run()


def test_cloud_agents_have_no_radio_hop_in_sionna_mode():
    sim = Simulator(small_cfg("sionna"), "greedy", seed=1)
    cloud = int(np.nonzero(sim.agent_kind == "cloud")[0][0])

    def run():
        t0 = sim.env.now
        reason = yield from sim.radio(cloud)
        return reason, sim.env.now - t0

    proc = sim.env.process(run())
    sim.env.run(until=proc)
    assert proc.value == (None, 0.0)
