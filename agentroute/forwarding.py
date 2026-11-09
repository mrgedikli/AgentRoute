"""Intent-based forwarding: the decision of a single node.

This module does not know about SimPy. A policy gets the local state of a
node (NodeView) and a packet, and decides whether to hand the task to a local
agent (accept) or which neighbour to forward it to (choose). The same code can
therefore be used by the SimPy simulator, the Streamlit app or, later, a real
overlay implementation.

v2 adds: an acceptance rule that compares the local agent with what the S-FIB
knows, a load-aware greedy heuristic and an SPFR-style potential policy, and
reward bookkeeping for every policy so that all of them can be compared on
the same return.

Responsible: Bekir Emre Sarıpınar (v2 revision written with AI assistance)
"""
from dataclasses import dataclass, field

import numpy as np

DEFAULT_REWARD = {"hop_cost": 0.05, "delay_scale_s": 0.1, "deliver_bonus": 1.0, "drop_penalty": 1.0}
LOCAL = -1      # pseudo neighbour: "hand the task to the best local agent"


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
    pending: object = None      # last decision waiting for its reward
    oracle_best: bool = False   # the globally best agent is correct and passes tau
    oracle_any: bool = False    # some correct agent passes tau


@dataclass
class NodeView:
    """Everything a router knows locally when it forwards a packet."""
    node: int
    neighbors: list             # alive neighbours (router ids)
    sfib: object                # agentroute.sfib.SFIB of this router
    local_agents: list          # agent ids attached to this router
    local_vecs: np.ndarray      # their capability vectors, shape (len(local_agents), dim)
    queue_occ: dict             # neighbour -> queue occupancy in [0, 1]
    link_quality: dict          # neighbour -> 1 - loss probability
    link_delay: dict            # neighbour -> one-way delay in seconds
    in_handover: dict           # neighbour -> 1 if that gNB had a recent handover
    kind: dict                  # neighbour -> "gnb" | "core" | "cloud"
    upstream: int               # default route (nearest core router), may be None
    tau: float
    radius: int
    now: float = 0.0            # local clock when the packet is processed
    accept_mode: str = "best_known"     # "first" | "best_known"
    omega: float = 0.08         # attenuation per hop of a remote candidate


def best_local_agent(view, pkt):
    """Best local agent with cos >= tau, or None."""
    if len(view.local_agents) == 0:
        return None
    sims = view.local_vecs @ pkt.intent
    j = int(np.argmax(sims))
    if sims[j] >= view.tau:
        return view.local_agents[j]
    return None


def accept_rule(view, pkt):
    """Hand the task to a local agent, or return None to keep forwarding.

    "first" takes the first agent on the path that passes tau (v1). "best_known"
    also requires that no unvisited neighbour advertises a better candidate,
    after attenuating that candidate by its distance.
    """
    agent = best_local_agent(view, pkt)
    if agent is None or view.accept_mode == "first" or pkt.ttl <= 0:
        return agent
    fresh = [n for n in view.neighbors if n != pkt.prev_hop and n not in pkt.visited]
    if not fresh:
        return agent
    local = float(view.local_vecs[view.local_agents.index(agent)] @ pkt.intent)
    max_sim, _, hops = view.sfib.scores(pkt.intent)
    idx = [view.sfib.index[n] for n in fresh]
    potential = max_sim[idx] * np.exp(-view.omega * hops[idx])
    return agent if local >= potential.max() else None


FEATURES = ["max_sim", "mean_sim", "sim_gap", "above_tau", "hops_norm", "has_entry",
            "queue_occ", "link_quality", "link_delay", "in_handover", "ttl_ratio",
            "visited", "is_core", "is_cloud", "is_local"]
N_FEATURES = len(FEATURES)


def candidates(view, pkt):
    """Neighbours a packet may go to: never straight back to the previous hop."""
    cands = [n for n in view.neighbors if n != pkt.prev_hop]
    if not cands and pkt.prev_hop in view.neighbors:
        cands = [pkt.prev_hop]      # dead end: going back is the only option
    return cands


def neighbor_features(view, pkt, with_local=False):
    """Features of every action. Returns (actions, X with shape (len(actions), N_FEATURES)).

    An action is a neighbour id, or LOCAL ("deliver here") if with_local is
    set and a local agent passes tau.
    """
    cands = candidates(view, pkt)
    max_sim, mean_sim, hops = view.sfib.scores(pkt.intent)
    idx = [view.sfib.index[n] for n in cands]
    mx = max_sim[idx]
    best = mx.max() if len(mx) else -1.0
    local_row = None
    if with_local and best_local_agent(view, pkt) is not None:
        sims = view.local_vecs @ pkt.intent
        local_sim = float(sims.max())
        local_row = [local_sim, float(sims.mean()), local_sim - best, 1.0, 0.0, 1.0,
                     0.0, 1.0, 0.0, 0.0, pkt.ttl / pkt.ttl_max, 0.0, 0.0, 0.0, 1.0]
        best = max(best, local_sim)
    visited = set(pkt.visited)
    rows = [] if local_row is None else [local_row]
    for n, i in zip(cands, idx):
        has = max_sim[i] > -1.0
        rows.append([
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
            0.0,
        ])
    actions = ([] if local_row is None else [LOCAL]) + cands
    return actions, np.array(rows, dtype=np.float32).reshape(len(actions), N_FEATURES)


class Policy:
    """Interface. Every policy keeps the same return so that they can be compared."""
    name = "policy"

    def __init__(self, reward=None):
        self.reward = reward or DEFAULT_REWARD
        self.episode_return = 0.0

    def accept(self, view, pkt):
        agent = accept_rule(view, pkt)
        if agent is not None:
            pkt.pending = (None, None, view.now)
        return agent

    def choose(self, view, pkt):
        raise NotImplementedError

    def observe(self, pkt, now, next_view, outcome):
        """Called by the simulator when the result of the last decision is known.

        outcome is None when the packet reached the next router (next_view is
        that router's NodeView), "deliver" when it reached a correct agent, and
        "drop" for any failure (TTL, queue, link loss, wrong agent, ...).
        """
        if pkt.pending is None:
            return
        X, a, t0 = pkt.pending
        pkt.pending = None
        rw = self.reward
        r = -(rw["hop_cost"] + (now - t0) / rw["delay_scale_s"])
        if outcome is not None:
            r += rw["deliver_bonus"] if outcome == "deliver" else -rw["drop_penalty"]
        self.episode_return += r
        self.learn(X, a, r, pkt, next_view, outcome)

    def learn(self, X, a, r, pkt, next_view, outcome):
        pass


class GreedyPolicy(Policy):
    """Forward to the neighbour whose S-FIB summary is most similar to the intent.

    Unvisited neighbours are preferred (loop avoidance). If no neighbour has
    any S-FIB entry, the packet follows the default route towards the core.
    """
    name = "greedy"

    def _pool(self, view, pkt):
        cands = candidates(view, pkt)
        visited = set(pkt.visited)
        fresh = [n for n in cands if n not in visited]
        return fresh if fresh else cands

    def _default_route(self, view, pool):
        if view.upstream in pool:
            return view.upstream
        cores = [n for n in pool if view.kind[n] != "gnb"]
        return min(cores) if cores else min(pool)

    def choose(self, view, pkt):
        pool = self._pool(view, pkt)
        if not pool:
            return None
        pkt.pending = (None, None, view.now)
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
        return self._default_route(view, pool)


class LoadAwareGreedy(GreedyPolicy):
    """Hand-written load balancing: among the neighbours within `band` of the
    best S-FIB score, take the least loaded one. This is the heuristic that a
    learned policy has to beat."""
    name = "greedy_load"

    def __init__(self, band=0.05, reward=None):
        super().__init__(reward)
        self.band = band

    def choose(self, view, pkt):
        pool = self._pool(view, pkt)
        if not pool:
            return None
        pkt.pending = (None, None, view.now)
        max_sim, _, hops = view.sfib.scores(pkt.intent)
        known = [n for n in pool if max_sim[view.sfib.index[n]] > -1.0]
        if not known:
            return self._default_route(view, pool)
        best = max(max_sim[view.sfib.index[n]] for n in known)
        near = [n for n in known if max_sim[view.sfib.index[n]] >= best - self.band]
        return min(near, key=lambda n: (round(view.queue_occ[n], 2), hops[view.sfib.index[n]], n))


class SPFRPolicy(GreedyPolicy):
    """SPFR-style forwarding (Qin et al., 2026), used with an exact S-FIB.

    Every visible executor is a potential source: phi = similarity * exp(-omega * hops),
    gated by tau. The task goes one hop towards the dominant executor and is
    executed locally if that executor is attached here. Executor load and
    price are not modelled in this simulator, so the utility is the similarity.
    If no executor is visible, the packet takes the default route to the core.
    """
    name = "spfr"

    def __init__(self, omega=0.08, reward=None):
        super().__init__(reward)
        self.omega = omega
        self._next = None

    def _dominant(self, view, pkt):
        """(potential, next hop) of the best remote executor, or (-1, None)."""
        mat, owner, hops = view.sfib.entries()
        if len(mat) == 0:
            return -1.0, None
        sims = mat @ pkt.intent
        alive = np.array([view.sfib.neighbors[i] in view.queue_occ for i in owner])
        ok = (sims >= view.tau) & alive
        if not ok.any():
            return -1.0, None
        phi = sims * np.exp(-self.omega * hops)
        phi[~ok] = -1.0
        j = int(np.argmax(phi))
        return float(phi[j]), view.sfib.neighbors[owner[j]]

    def accept(self, view, pkt):
        agent = best_local_agent(view, pkt)
        remote, nxt = self._dominant(view, pkt)
        self._next = nxt
        if agent is None:
            return None
        local = float(view.local_vecs[view.local_agents.index(agent)] @ pkt.intent)
        if local >= remote or pkt.ttl <= 0:
            pkt.pending = (None, None, view.now)
            return agent
        return None

    def choose(self, view, pkt):
        if self._next is not None:
            pkt.pending = (None, None, view.now)
            return self._next
        pool = self._pool(view, pkt)
        if not pool:
            return None
        pkt.pending = (None, None, view.now)
        return self._default_route(view, pool)
