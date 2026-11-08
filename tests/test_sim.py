"""Tests for the simulator, the baselines and the DQN pieces."""
import numpy as np
import torch

from agentroute.baselines.chord import chash, normalize
from agentroute.config import load_config
from agentroute.dqn.model import MAX_DEG
from agentroute.dqn.policy import DQNPolicy, build_model
from agentroute.forwarding import N_FEATURES
from agentroute.sim.simulator import Simulator


def small_cfg(**sim):
    cfg = load_config(overrides={"agents": {"n_agents": 100}, "sim": {"duration_s": 8.0, **sim}})
    return cfg


def test_same_seed_same_result():
    a = Simulator(small_cfg(), "greedy", seed=3).run()
    b = Simulator(small_cfg(), "greedy", seed=3).run()
    assert a == b


def test_all_methods_see_the_same_queries():
    counts = set()
    for m in ("greedy", "greedy_load", "spfr", "flooding", "registry", "registry3", "chord", "sdht"):
        counts.add(Simulator(small_cfg(), m, seed=2).run()["n_queries"])
    assert len(counts) == 1


def test_chord_fails_on_paraphrases():
    s = Simulator(small_cfg(), "chord", seed=1).run()
    assert s["success_rate"] == 0.0
    assert s["drop_not_found"] > 0.5
    assert normalize("Object  detection, in images!") == "object detection in images"
    assert chash("a", 32) != chash("b", 32)


def test_flooding_is_bounded_by_dedup():
    sim = Simulator(small_cfg(), "flooding", seed=1)
    s = sim.run()
    assert sim.flood.copies / s["n_queries"] <= 2 * sim.G.number_of_edges()


def test_flooding_time_includes_the_collection_window():
    cfg = small_cfg()
    s = Simulator(cfg, "flooding", seed=1).run()
    assert s["time_ms"] >= 1000.0 * cfg["baselines"]["flood_window_s"]


def test_semantic_dht_finds_paraphrases_that_chord_cannot():
    a = Simulator(small_cfg(), "sdht", seed=1).run()
    b = Simulator(small_cfg(), "chord", seed=1).run()
    assert a["success_rate"] > 0.0 and b["success_rate"] == 0.0


def test_replicated_registry_survives_when_the_central_one_is_lost():
    sim = Simulator(small_cfg(), "registry3", seed=1)
    assert len(sim.registry.nodes) == 3
    sim.known_dead.add(sim.registry.nodes[0])
    server, path = sim.registry.nearest(sim.gnbs[0])
    assert server in sim.registry.nodes[1:] and path


def test_oracle_bounds_are_consistent():
    s = Simulator(small_cfg(), "registry", seed=1).run()
    assert 0.0 <= s["oracle_best"] <= s["oracle_any"] <= 1.0
    assert s["ctrl_kB_per_s"] > 0 and s["query_kB_per_query"] > 0


def test_node_failures_are_applied():
    sim = Simulator(small_cfg(failure_fraction=0.3), "greedy", seed=1)
    sim.run()
    assert sum(not r.alive for r in sim.routers.values()) > 0
    assert sim.known_dead


def test_baselines_survive_heavy_failures():
    # 30% failed routers can partition the network; lookups must fail cleanly, not crash
    for m in ("chord", "sdht", "registry", "registry3", "flooding"):
        for seed in (1, 2, 3):
            s = Simulator(small_cfg(failure_fraction=0.3), m, seed=seed).run()
            assert s["n_queries"] > 0


def test_models_score_each_neighbour():
    for kind in ("mlp", "gnn"):
        model = build_model(kind, hidden=16)
        x = torch.randn(4, MAX_DEG, N_FEATURES)
        mask = torch.zeros(4, MAX_DEG, dtype=torch.bool)
        mask[:, :3] = True
        q = model(x, mask)
        assert q.shape == (4, MAX_DEG)
        assert (q[:, 3:] < -1e8).all()


def test_dqn_policy_runs_and_saves(tmp_path):
    policy = DQNPolicy(build_model("mlp", hidden=16))
    s = Simulator(small_cfg(), "agentroute", seed=1, policy=policy).run()
    assert s["n_queries"] > 0
    path = tmp_path / "m.pt"
    policy.save(path, hidden=16)
    loaded = DQNPolicy.load(path)
    X = np.random.rand(5, N_FEATURES).astype(np.float32)
    assert np.allclose(loaded.q_values(X), policy.q_values(X), atol=1e-6)


def test_every_policy_gets_a_return():
    for m in ("greedy", "greedy_load", "spfr"):
        sim = Simulator(small_cfg(), m, seed=1)
        sim.run()
        assert sim.policy.episode_return != 0.0
