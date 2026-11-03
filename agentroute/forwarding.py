"""Intent-based forwarding: the next-hop decision of a single node.

This module does not know about SimPy. A policy gets the local state of a
node (NodeView) and a packet, and returns the neighbour to forward to. The
same code can therefore be used by the SimPy simulator, the Streamlit app or,
later, a real overlay implementation.

Responsible: Bekir Emre Sarıpınar
"""
from dataclasses import dataclass, field

import numpy as np


@dataclass
class Packet:
    pid: int
    intent: np.ndarray          # normalised intent embedding carried in the header
    intent_class: int           # ground truth, only used for evaluation
    ttl: int
    ttl_max: int
    src_agent: int
    created: float
    method: str
    prev_hop: int = None
    visited: list = field(default_factory=list)
    hops: int = 0
    text: str = ""              # request text, only used by the Chord baseline (exact match)
    pending: object = None      # DQN bookkeeping: decision waiting for its reward


@dataclass
class NodeView:
    """Everything a router knows locally when it forwards a packet."""
    node: int
    neighbors: list             # alive neighbours (router ids)
    sfib: object                # agentroute.sfib.SFIB of this router
    local_agents: list          # agent ids attached to this router
    local_vecs: np.ndarray      # their capability vectors, shape (len(local_agents), 384)
    queue_occ: dict             # neighbour -> queue occupancy in [0, 1]
    link_quality: dict          # neighbour -> 1 - loss probability
    link_delay: dict            # neighbour -> one-way delay in seconds
    in_handover: dict           # neighbour -> 1 if that gNB had a recent handover
    kind: dict                  # neighbour -> "gnb" | "core" | "cloud"
    upstream: int               # default route (nearest core router), may be None
    tau: float
    radius: int
    now: float = 0.0            # local clock when the packet is processed


def best_local_agent(view, pkt):
    """Agent acceptance rule: deliver to the best local agent with cos >= tau."""
    if len(view.local_agents) == 0:
        return None
    sims = view.local_vecs @ pkt.intent
    j = int(np.argmax(sims))
    if sims[j] >= view.tau:
        return view.local_agents[j]
    return None


FEATURES = ["max_sim", "mean_sim", "sim_gap", "above_tau", "hops_norm", "has_entry",
            "queue_occ", "link_quality", "link_delay", "in_handover", "ttl_ratio",
            "visited", "is_core", "is_cloud"]
N_FEATURES = len(FEATURES)


def candidates(view, pkt):
    """Neighbours a packet may go to: never straight back to the previous hop."""
    cands = [n for n in view.neighbors if n != pkt.prev_hop]
    if not cands and pkt.prev_hop in view.neighbors:
        cands = [pkt.prev_hop]      # dead end: going back is the only option
    return cands


def neighbor_features(view, pkt, cands=None):
    """Feature vector of every candidate neighbour, shape (len(cands), N_FEATURES)."""
    if cands is None:
        cands = candidates(view, pkt)
    max_sim, mean_sim, hops = view.sfib.scores(pkt.intent)
    idx = [view.sfib.index[n] for n in cands]
    mx = max_sim[idx]
    best = mx.max() if len(mx) else 0.0
    visited = set(pkt.visited)
    X = np.zeros((len(cands), N_FEATURES), dtype=np.float32)
    for row, (n, i) in enumerate(zip(cands, idx)):
        has = max_sim[i] > -1.0
        X[row] = [
            max_sim[i] if has else 0.0,
            mean_sim[i] if has else 0.0,
            (max_sim[i] - best) if has else -1.0,
            1.0 if max_sim[i] >= view.tau else 0.0,
            min(hops[i], view.radius + 1) / (view.radius + 1),
            1.0 if has else 0.0,
            view.queue_occ[n],
            view.link_quality[n],
            min(view.link_delay[n] / 0.02, 1.0),
            view.in_handover[n],
            pkt.ttl / pkt.ttl_max,
            1.0 if n in visited else 0.0,
            1.0 if view.kind[n] == "core" else 0.0,
            1.0 if view.kind[n] == "cloud" else 0.0,
        ]
    return cands, X


class Policy:
    """Interface. Learning policies also override observe()."""
    name = "policy"

    def choose(self, view, pkt):
        raise NotImplementedError

    def observe(self, pkt, now, next_view, outcome):
        """Called by the simulator when the result of the last decision is known.

        outcome is None when the packet reached the next router (next_view is
        that router's NodeView), "deliver" when it reached a correct agent, and
        "drop" for any failure (TTL, queue, link loss, wrong agent, ...).
        """
        pass


class GreedyPolicy(Policy):
    """Forward to the neighbour whose S-FIB summary is most similar to the intent.

    Unvisited neighbours are preferred (loop avoidance). If no neighbour has
    any S-FIB entry, the packet follows the default route towards the core.
    """
    name = "greedy"

    def choose(self, view, pkt):
        cands = candidates(view, pkt)
        if not cands:
            return None
        visited = set(pkt.visited)
        fresh = [n for n in cands if n not in visited]
        pool = fresh if fresh else cands
        max_sim, _, hops = view.sfib.scores(pkt.intent)
        best, best_key = None, None
        for n in pool:
            i = view.sfib.index[n]
            if max_sim[i] <= -1.0:
                continue
            key = (max_sim[i], -hops[i], -n)
            if best_key is None or key > best_key:
                best, best_key = n, key
        if best is not None:
            return best
        # no semantic information: default route, else any unvisited neighbour
        if view.upstream in pool:
            return view.upstream
        cores = [n for n in pool if view.kind[n] != "gnb"]
        return min(cores) if cores else min(pool)
