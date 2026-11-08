"""Tests for the dataset, the S-FIB and greedy forwarding."""
import networkx as nx
import numpy as np

from agentroute.data.capabilities import CLASSES, EXAMPLES, capability_cards, split_intents
from agentroute.embeddings import agent_vectors, quantize
from agentroute.forwarding import (FEATURES, LOCAL, N_FEATURES, GreedyPolicy, LoadAwareGreedy, NodeView, Packet,
                                   SPFRPolicy, accept_rule, candidates, neighbor_features)
from agentroute.sfib import SFIB, Advertiser, kmeans_summary


def _norm(x):
    return (x / np.linalg.norm(x, axis=-1, keepdims=True)).astype(np.float32)


def test_dataset_shape():
    assert len(CLASSES) == 50
    for name, descs, intents in CLASSES:
        assert len(descs) == 2 and len(intents) == 10 and len(EXAMPLES[name]) == 3
    train, test = split_intents()
    assert len(train) == 350 and len(test) == 150
    assert not set(train) & set(test)


def test_intents_never_repeat_capability_text():
    card_sentences = [s.lower() for _, _, card in capability_cards() for s in card]
    for _, _, intents in CLASSES:
        for intent in intents:
            low = intent.lower()
            for s in card_sentences:
                assert low != s
                assert s not in low and low not in s


def test_quantize_keeps_unit_norm():
    v = _norm(np.random.default_rng(0).normal(size=384))
    for header in ("float32", "int8", "binary"):
        q = quantize(v, header)
        assert abs(np.linalg.norm(q) - 1) < 1e-4
        assert q @ v > 0.7


def test_kmeans_summary_small_input_is_exact():
    vecs = _norm(np.eye(3, 384))
    reps, hops, weights = kmeans_summary(vecs, np.ones(3), np.array([1, 2, 3]), k=4)
    assert np.allclose(reps, vecs) and list(hops) == [1, 2, 3] and list(weights) == [1, 1, 1]


def test_kmeans_summary_compresses_to_k():
    vecs = _norm(np.random.default_rng(0).normal(size=(50, 384)))
    reps, hops, weights = kmeans_summary(vecs, np.ones(50), np.ones(50, int), k=4)
    assert len(reps) <= 4 and weights.sum() == 50


def test_every_agent_has_its_own_vector():
    class_vecs = _norm(np.random.default_rng(1).normal(size=(3, 5, 384)))
    v = agent_vectors(class_vecs, np.array([0, 0, 1, 2]), np.random.default_rng(2))
    assert abs(np.linalg.norm(v, axis=1) - 1).max() < 1e-5
    assert v[0] @ v[1] < 0.9999 and v[0] @ v[1] > v[0] @ v[2]


def _vecs(n):
    return _norm(np.eye(n, 384))


def _adv(g, radius, summary="exact", k=8, exact_hops=0):
    return Advertiser(g, 384, radius, summary=summary, k=k, change_threshold=0.01,
                      encoding="float32", exact_hops=exact_hops)


def test_exact_table_respects_radius():
    # line 0-1-2-3-4, one agent at router 4, radius 2
    adv = _adv(nx.path_graph(5), radius=2)
    adv.local[4][7] = _vecs(1)[0]
    adv.build()
    assert list(adv.tables[3].rows[adv.tables[3].index[4]][1]) == [1]
    assert list(adv.tables[2].rows[adv.tables[2].index[3]][1]) == [2]
    assert len(adv.tables[1].entries()[0]) == 0         # 3 hops away: outside R


def test_summary_distance_vector_respects_radius():
    adv = _adv(nx.path_graph(5), radius=2, summary="kmeans", k=2)
    adv.local[4][7] = _vecs(1)[0]
    adv.build()
    assert list(adv.tables[3].rows[adv.tables[3].index[4]][1]) == [1]
    assert list(adv.tables[2].rows[adv.tables[2].index[3]][1]) == [2]
    assert len(adv.tables[1].entries()[0]) == 0


def test_summary_size_does_not_depend_on_agent_count():
    g = nx.path_graph(3)
    vecs = _norm(np.random.default_rng(0).normal(size=(200, 384)))
    sizes = []
    for n in (20, 200):
        adv = _adv(g, radius=2, summary="kmeans", k=4)
        for a in range(n):
            adv.local[0][a] = vecs[a]
        adv.build()
        sizes.append(adv.tables[1].n_vectors(0))
    assert sizes == [4, 4]


def test_two_tier_table_keeps_nearby_agents_exact():
    g = nx.path_graph(3)
    vecs = _norm(np.random.default_rng(0).normal(size=(10, 384)))
    adv = _adv(g, radius=2, summary="kmeans", k=2, exact_hops=1)
    for a in range(10):
        adv.local[0][a] = vecs[a]
    adv.build()
    assert adv.tables[1].n_vectors(0) == 10         # 1 hop: one row per agent
    assert adv.tables[2].n_vectors(1) == 2          # 2 hops: summarised


def test_handover_withdraw_and_announce():
    v = _vecs(2)
    adv = _adv(nx.path_graph(5), radius=4)
    adv.local[0][5] = v[1]
    adv.build()
    # the agent moves from router 0 to router 4
    adv.local[0].pop(5)
    changed_w = []
    for d in range(1, 5):
        changed, _ = adv.spread(0, [0], {0}, 5, v[1], -1, d)
        changed_w += changed
    adv.local[4][5] = v[1]
    changed_a = []
    for d in range(1, 5):
        changed, _ = adv.spread(4, [4], {4}, 5, v[1], +1, d)
        changed_a += changed
    assert changed_w and changed_a
    assert len(adv.tables[2].rows[adv.tables[2].index[1]][0]) == 0
    assert len(adv.tables[2].rows[adv.tables[2].index[3]][0]) == 1


def test_small_changes_are_suppressed():
    vecs = _norm(np.random.default_rng(0).normal(size=(2, 384)))
    t = SFIB(0, [1], 384, 2, k=1)
    t.set_row(0, vecs[:1].copy(), np.array([1]), np.array([1000.0], np.float32))
    before = t.rows[0][0].copy()
    assert t.apply_delta(0, vecs[1], +1, 1, threshold=0.01) is False    # heavy summary hardly moves
    assert np.allclose(t.rows[0][0], before)
    t.set_row(0, vecs[:1].copy(), np.array([1]), np.array([1.0], np.float32))
    assert t.apply_delta(0, vecs[1], +1, 1, threshold=0.01) is True     # a rare capability does


def _view(adv, node, tau=0.5, accept_mode="best_known", local=None):
    nbrs = sorted(adv.graph.neighbors(node))
    ids = list(local) if local else []
    vecs = np.stack([local[a] for a in ids]) if local else np.zeros((0, 384), np.float32)
    return NodeView(node=node, neighbors=nbrs, sfib=adv.tables[node], local_agents=ids,
                    local_vecs=vecs,
                    queue_occ={n: 0.0 for n in nbrs}, link_quality={n: 1.0 for n in nbrs},
                    link_delay={n: 0.002 for n in nbrs}, in_handover={n: 0 for n in nbrs},
                    kind={n: "gnb" for n in nbrs}, upstream=None, tau=tau, radius=adv.radius,
                    accept_mode=accept_mode, omega=0.0)


def _pkt(intent, ttl=5):
    return Packet(pid=0, intent=intent, intent_class=1, ttl=ttl, ttl_max=5, src_agent=0,
                  created=0.0, method="greedy")


def _star():
    # router 0 with neighbours 1 and 2; agent 10 behind 1, agent 11 behind 2
    v = _vecs(2)
    adv = _adv(nx.Graph([(0, 1), (0, 2)]), radius=2)
    adv.local[1][10] = v[0]
    adv.local[2][11] = v[1]
    adv.build()
    return adv, v


def test_greedy_follows_similarity_and_never_goes_back():
    adv, v = _star()
    pkt = _pkt(v[1])
    view = _view(adv, 0)
    assert GreedyPolicy().choose(view, pkt) == 2
    pkt.prev_hop = 2
    assert 2 not in candidates(view, pkt)
    cands, X = neighbor_features(view, pkt)
    assert X.shape == (len(cands), N_FEATURES)


def test_best_known_keeps_going_past_a_weak_local_match():
    adv, v = _star()
    intent = _norm(0.9 * v[1] + 0.3 * v[0])
    weak = {5: _norm(0.3 * v[1] + 0.9 * _vecs(3)[2])}
    assert accept_rule(_view(adv, 0, tau=0.1, accept_mode="first", local=weak), _pkt(intent)) == 5
    assert accept_rule(_view(adv, 0, tau=0.1, accept_mode="best_known", local=weak), _pkt(intent)) is None


def test_load_aware_greedy_avoids_the_busy_neighbour():
    v = _vecs(1)
    adv = _adv(nx.Graph([(0, 1), (0, 2)]), radius=2)
    adv.local[1][10] = v[0]
    adv.local[2][11] = v[0]
    adv.build()
    view = _view(adv, 0)
    view.queue_occ[1] = 0.9
    assert LoadAwareGreedy().choose(view, _pkt(v[0])) == 2


def test_spfr_goes_to_the_dominant_executor_and_executes_locally():
    adv, v = _star()
    policy = SPFRPolicy(omega=0.08)
    assert policy.accept(_view(adv, 0, tau=0.1), _pkt(v[1])) is None
    assert policy.choose(_view(adv, 0, tau=0.1), _pkt(v[1])) == 2
    assert policy.accept(_view(adv, 0, tau=0.1, local={5: v[1]}), _pkt(v[1])) == 5


def test_local_action_is_offered_only_above_tau():
    adv, v = _star()
    actions, X = neighbor_features(_view(adv, 0, tau=0.5, local={5: v[1]}), _pkt(v[1]), with_local=True)
    assert actions[0] == LOCAL and X[0, FEATURES.index("is_local")] == 1.0
    actions, _ = neighbor_features(_view(adv, 0, tau=0.5, local={5: v[0]}), _pkt(v[1]), with_local=True)
    assert LOCAL not in actions
