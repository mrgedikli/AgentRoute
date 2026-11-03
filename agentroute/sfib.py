"""Semantic FIB (S-FIB) and bounded-radius capability advertisements.

A normal FIB maps an IP prefix to an outgoing port. An S-FIB maps each
neighbour to a summary of the capabilities that can be reached through it.

Bookkeeping per router u:
    counts[i, c, d] = number of agents with capability card c that are d router
                      hops away and are reached through neighbour i.
The summary that a neighbour advertises is "which cards, at what minimum hop
distance". It is compressed into k representative vectors (k-means centroids)
so that the S-FIB size does not grow with the number of agents. A plain mean
(k = 1) and an exact table (no compression) are kept for comparison.

Advertisements are bounded by a radius R: an agent attached to router v is
visible only to routers at most R hops from v, and router u learns it through
every neighbour n that lies on a shortest path to v (dist(n, v) = dist(u, v) - 1).
This is the same result as a distance-vector protocol whose entries stop
propagating after R hops.

Responsible: Bekir Emre Sarıpınar
"""
from collections import deque

import numpy as np


def kmeans_summary(vecs, weights, hops, k, iters=10):
    """Spherical k-means on unit vectors. Returns (reps, rep_hops).

    Initialisation is deterministic (heaviest vector first, then farthest point),
    so the same S-FIB always gives the same summary.
    """
    n = len(vecs)
    if n <= k:
        return vecs.copy(), hops.copy()
    centers = [int(np.argmax(weights))]
    best_sim = vecs @ vecs[centers[0]]
    for _ in range(1, k):
        nxt = int(np.argmin(best_sim))
        centers.append(nxt)
        best_sim = np.maximum(best_sim, vecs @ vecs[nxt])
    reps = vecs[centers].copy()
    for _ in range(iters):
        assign = np.argmax(vecs @ reps.T, axis=1)
        for j in range(k):
            members = assign == j
            if members.any():
                c = (vecs[members] * weights[members, None]).sum(axis=0)
                reps[j] = c / max(np.linalg.norm(c), 1e-9)
    assign = np.argmax(vecs @ reps.T, axis=1)
    rep_hops = np.array([hops[assign == j].min() if (assign == j).any() else hops.max()
                         for j in range(k)])
    return reps.astype(np.float32), rep_hops


class SFIB:
    """S-FIB of a single router."""

    def __init__(self, node, neighbors, card_vecs, radius, summary="kmeans", k=4):
        self.node = node
        self.neighbors = list(neighbors)
        self.index = {n: i for i, n in enumerate(self.neighbors)}
        self.card_vecs = card_vecs
        self.radius = radius
        self.summary = summary
        self.k = k
        self.counts = np.zeros((len(self.neighbors), len(card_vecs), radius + 1), dtype=np.int32)
        self._dirty = set(range(len(self.neighbors)))
        self._reps = {}  # neighbour index -> (reps, rep_hops)
        self._matrix = None

    # ---- updates -------------------------------------------------------
    def present(self, i):
        """(card ids, min hops, agent counts) reachable via neighbour index i."""
        c = self.counts[i]
        total = c.sum(axis=1)
        cards = np.nonzero(total)[0]
        if len(cards) == 0:
            return cards, cards, cards
        min_hops = np.argmax(c[cards] > 0, axis=1)
        return cards, min_hops, total[cards]

    def change(self, neighbor, card, hops, delta):
        """Add or remove agents. Returns True if the advertised summary changed."""
        i = self.index[neighbor]
        if self.counts[i, card, hops] + delta < 0:
            return False    # update raced with a full rebuild after a failure
        before = self.counts[i, card]
        old_min = np.argmax(before > 0) if before.any() else -1
        self.counts[i, card, hops] += delta
        after = self.counts[i, card]
        new_min = np.argmax(after > 0) if after.any() else -1
        if new_min != old_min:
            self._dirty.add(i)
            self._matrix = None
            return True
        return False

    def add_block(self, neighbor, hops, card_counts):
        i = self.index[neighbor]
        self.counts[i, :, hops] += card_counts
        self._dirty.add(i)
        self._matrix = None

    def clear(self):
        self.counts[:] = 0
        self._dirty = set(range(len(self.neighbors)))
        self._reps = {}
        self._matrix = None

    # ---- summaries -----------------------------------------------------
    def _summarise(self, i):
        cards, min_hops, weights = self.present(i)
        if len(cards) == 0:
            return None
        vecs = self.card_vecs[cards]
        if self.summary == "exact":
            return vecs, min_hops
        if self.summary == "mean":
            m = (vecs * weights[:, None]).sum(axis=0)
            return (m / np.linalg.norm(m))[None, :].astype(np.float32), np.array([min_hops.min()])
        return kmeans_summary(vecs, weights.astype(np.float32), min_hops, self.k)

    def n_vectors(self, neighbor):
        rep = self.rep(self.index[neighbor])
        return 0 if rep is None else len(rep[0])

    def rep(self, i):
        if i in self._dirty:
            self._reps[i] = self._summarise(i)
            self._dirty.discard(i)
        return self._reps.get(i)

    def _build_matrix(self):
        rows, owner, hops = [], [], []
        for i in range(len(self.neighbors)):
            r = self.rep(i)
            if r is None:
                continue
            rows.append(r[0])
            owner.extend([i] * len(r[0]))
            hops.extend(r[1])
        if rows:
            self._matrix = (np.vstack(rows), np.array(owner), np.array(hops))
        else:
            self._matrix = (np.zeros((0, self.card_vecs.shape[1]), np.float32),
                            np.zeros(0, int), np.zeros(0, int))

    def scores(self, intent):
        """Per neighbour index: (max cos, mean cos, hops of the best representative).

        Neighbours without any entry get max = mean = -1 and hops = radius + 1.
        """
        if self._matrix is None or self._dirty:
            self._build_matrix()
        mat, owner, hops = self._matrix
        n = len(self.neighbors)
        max_sim = np.full(n, -1.0)
        mean_sim = np.full(n, -1.0)
        best_hops = np.full(n, self.radius + 1)
        if len(mat) == 0:
            return max_sim, mean_sim, best_hops
        sims = mat @ intent
        for i in np.unique(owner):
            sel = owner == i
            s = sims[sel]
            j = int(np.argmax(s))
            max_sim[i] = s[j]
            mean_sim[i] = s.mean()
            best_hops[i] = hops[sel][j]
        return max_sim, mean_sim, best_hops


class Advertiser:
    """Builds and maintains the S-FIBs of all routers.

    `agents_at[v]` is a vector of agent counts per card for router v. The
    advertiser keeps every S-FIB consistent with it and counts the control
    messages a distance-vector protocol would send.
    """

    def __init__(self, graph, card_vecs, radius, summary="kmeans", k=4):
        self.graph = graph
        self.card_vecs = card_vecs
        self.radius = radius
        self.alive = set(graph.nodes)
        self.tables = {u: SFIB(u, sorted(graph.neighbors(u)), card_vecs, radius, summary, k)
                       for u in graph.nodes}
        self.agents_at = {u: np.zeros(len(card_vecs), dtype=np.int32) for u in graph.nodes}
        self._dag_cache = {}

    def dag(self, v):
        """All (d, u, n): router u is d hops from v and learns v's agents via neighbour n."""
        if v in self._dag_cache:
            return self._dag_cache[v]
        dist = {v: 0}
        queue = deque([v])
        while queue:
            x = queue.popleft()
            if dist[x] == self.radius:
                continue
            for y in self.graph.neighbors(x):
                if y in self.alive and y not in dist:
                    dist[y] = dist[x] + 1
                    queue.append(y)
        out = []
        for u, d in dist.items():
            if d == 0:
                continue
            for n in self.graph.neighbors(u):
                if n in dist and dist[n] == d - 1:
                    out.append((d, u, n))
        out.sort()
        self._dag_cache[v] = out
        return out

    def build(self):
        """Fill every S-FIB from scratch. Returns the number of advert messages."""
        for t in self.tables.values():
            t.clear()
        for v, card_counts in self.agents_at.items():
            if v not in self.alive or not card_counts.any():
                continue
            for d, u, n in self.dag(v):
                self.tables[u].add_block(n, d, card_counts)
        return self.periodic_messages()

    def periodic_messages(self):
        """One refresh message per (neighbour -> router) pair that has entries."""
        msgs, vectors = 0, 0
        for u in self.alive:
            t = self.tables[u]
            for n in t.neighbors:
                if n in self.alive:
                    nv = t.n_vectors(n)
                    if nv:
                        msgs += 1
                        vectors += nv
        return msgs, vectors

    def updates_for(self, v):
        """Updates caused by a change at router v, grouped by hop distance."""
        return self.dag(v)

    def apply(self, updates, card, delta):
        """Apply a list of (d, u, n) updates for one card. Returns the changed (n -> u) links."""
        changed = []
        for d, u, n in updates:
            if self.tables[u].change(n, card, d, delta):
                changed.append((n, u))
        return changed

    def fail(self, nodes):
        """Remove failed routers and rebuild. Returns the number of changed (n -> u) links."""
        before = self._snapshot()
        self.alive -= set(nodes)
        for v in nodes:
            self.agents_at[v][:] = 0
        self._dag_cache = {}
        self.build()
        after = self._snapshot()
        return sum(1 for key in after if after[key] != before.get(key)) + \
            sum(1 for key in before if key not in after)

    def _snapshot(self):
        snap = {}
        for u in self.alive:
            t = self.tables[u]
            for i, n in enumerate(t.neighbors):
                cards, hops, _ = t.present(i)
                if len(cards):
                    snap[(n, u)] = (tuple(cards), tuple(hops))
        return snap
