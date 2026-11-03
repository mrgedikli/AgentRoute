"""Tests for the dataset, the S-FIB and greedy forwarding."""
import networkx as nx
import numpy as np

from agentroute.data.capabilities import CLASSES, EXAMPLES, capability_cards, split_intents
from agentroute.embeddings import quantize
from agentroute.forwarding import GreedyPolicy, NodeView, Packet, candidates, neighbor_features, N_FEATURES
from agentroute.sfib import Advertiser, kmeans_summary


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
    reps, hops = kmeans_summary(vecs, np.ones(3), np.array([1, 2, 3]), k=4)
    assert np.allclose(reps, vecs) and list(hops) == [1, 2, 3]


def _line_graph(n):
    g = nx.path_graph(n)
    return g


def test_advertisement_radius_and_next_hop():
    # line 0-1-2-3-4, one agent with card 0 at router 4, radius 2
    cards = _norm(np.eye(2, 384))
    adv = Advertiser(_line_graph(5), cards, radius=2)
    adv.agents_at[4][0] = 1
    adv.build()
    assert adv.tables[3].counts[adv.tables[3].index[4], 0, 1] == 1
    assert adv.tables[2].counts[adv.tables[2].index[3], 0, 2] == 1
    assert adv.tables[1].counts.sum() == 0          # 3 hops away: outside R


def test_handover_withdraw_and_announce():
    cards = _norm(np.eye(2, 384))
    adv = Advertiser(_line_graph(5), cards, radius=4)
    adv.agents_at[0][1] = 1
    adv.build()
    # the agent moves from router 0 to router 4
    changed_w = adv.apply(adv.updates_for(0), card=1, delta=-1)
    adv.agents_at[0][1] -= 1
    changed_a = adv.apply(adv.updates_for(4), card=1, delta=+1)
    adv.agents_at[4][1] += 1
    assert changed_w and changed_a
    assert adv.tables[2].counts[adv.tables[2].index[1], 1].sum() == 0
    assert adv.tables[2].counts[adv.tables[2].index[3], 1].sum() == 1


def _view(adv, node, tau=0.5):
    nbrs = sorted(adv.graph.neighbors(node))
    return NodeView(node=node, neighbors=nbrs, sfib=adv.tables[node], local_agents=[],
                    local_vecs=np.zeros((0, 384), np.float32),
                    queue_occ={n: 0.0 for n in nbrs}, link_quality={n: 1.0 for n in nbrs},
                    link_delay={n: 0.002 for n in nbrs}, in_handover={n: 0 for n in nbrs},
                    kind={n: "gnb" for n in nbrs}, upstream=None, tau=tau, radius=adv.radius)


def test_greedy_follows_similarity_and_never_goes_back():
    # star: router 0 with neighbours 1 and 2; card 0 behind 1, card 1 behind 2
    g = nx.Graph([(0, 1), (0, 2)])
    cards = _norm(np.eye(2, 384))
    adv = Advertiser(g, cards, radius=2)
    adv.agents_at[1][0] = 1
    adv.agents_at[2][1] = 1
    adv.build()
    pkt = Packet(pid=0, intent=cards[1], intent_class=1, ttl=5, ttl_max=5, src_agent=0,
                 created=0.0, method="greedy")
    view = _view(adv, 0)
    assert GreedyPolicy().choose(view, pkt) == 2
    pkt.prev_hop = 2
    assert 2 not in candidates(view, pkt)
    cands, X = neighbor_features(view, pkt)
    assert X.shape == (len(cands), N_FEATURES)
