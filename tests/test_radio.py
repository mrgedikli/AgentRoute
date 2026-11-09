"""Tests for the radio link table and the radio.model switch.

Written with AI assistance (Claude).
"""
import json
from pathlib import Path

import numpy as np

from agentroute.config import ROOT, load_config
from agentroute.radio import RadioLUT
from agentroute.sim.simulator import Simulator

LUT = ROOT / "results" / "radio_lut.npz"
REFERENCE = Path(__file__).parent / "data" / "constant_radio_reference.json"


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


def test_constant_model_reproduces_the_previous_results_exactly():
    reference = json.loads(REFERENCE.read_text())
    for key, expected in reference.items():
        method, seed = key.rsplit("-", 1)
        got = Simulator(small_cfg("constant"), method, seed=int(seed)).run()
        assert json.loads(json.dumps(got, sort_keys=True, default=str)) == expected


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
