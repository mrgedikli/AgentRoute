"""Semantic FIB (S-FIB) and bounded-radius capability advertisements.

A normal FIB maps an IP prefix to an outgoing port. An S-FIB maps each
neighbour to a summary of the capabilities that can be reached through it.

v2: this is now a real distance-vector protocol on summaries. Every agent has
its own vector, so a router cannot keep one row per capability. What a router
u tells its neighbour w is at most k representative vectors (each with a hop
count and a weight), computed from u's own agents and from what u heard from
its other neighbours. Only those k vectors cross the link, so the size of a
message does not depend on the number of agents, and information is summarised
again at every hop. The "exact" mode keeps one row per agent, as SPFR does.

Advertisements stop after R hops. After a handover the agent's vector travels
as a withdraw or announce, and a router forwards it only if it moved one of
its representatives by more than a threshold. Small changes wait for the
periodic refresh, which recomputes every summary from the true state.

The refresh has two modes. "full" sends every table again. "incremental" keeps
the same soft state but sends only the rows that changed, plus a small digest
on links where nothing did.

Responsible: Bekir Emre Sarıpınar (v2 revision written with AI assistance)
"""
from collections import deque

import numpy as np

from agentroute.embeddings import header_bytes, quantize

MSG_OVERHEAD = 40       # bytes of headers in every control message
ROW_META = 8            # hop count and weight next to each vector
ROW_ID = 2              # incremental refresh: which row of the link is replaced or removed
DIGEST = 8              # incremental refresh: hash of the rows on a link, "nothing changed"


def kmeans_summary(vecs, weights, hops, k, iters=10, medoid=False, init=None):
    """Weighted spherical k-means. Returns (reps, rep_hops, rep_weights).

    Initialisation is deterministic (heaviest vector first, then farthest
    point), so the same input always gives the same summary. With medoid=True
    each centre is replaced by the closest real input vector.

    With `init` (the representatives the receiver already has) the clustering
    continues from there, so a few changed inputs move the centres only a
    little. A fresh start could pick entirely different centres.
    """
    n = len(vecs)
    if n <= k:
        return vecs.copy(), hops.copy(), weights.copy()
    if init is not None and len(init):
        reps = init[:k].copy()
        best_sim = (vecs @ reps.T).max(axis=1)
        while len(reps) < k:                    # clusters that emptied are seeded again
            nxt = int(np.argmin(best_sim))
            reps = np.vstack([reps, vecs[nxt]])
            best_sim = np.maximum(best_sim, vecs @ vecs[nxt])
    else:
        centers = [int(np.argmax(weights))]
        best_sim = vecs @ vecs[centers[0]]
        for _ in range(1, k):
            nxt = int(np.argmin(best_sim))
            centers.append(nxt)
            best_sim = np.maximum(best_sim, vecs @ vecs[nxt])
        reps = vecs[centers].copy()
    assign = None
    for _ in range(iters):
        new_assign = np.argmax(vecs @ reps.T, axis=1)
        if assign is not None and (new_assign == assign).all():
            break
        assign = new_assign
        c = np.zeros_like(reps)
        np.add.at(c, assign, vecs * weights[:, None])
        norm = np.linalg.norm(c, axis=1)
        ok = norm > 1e-9
        reps[ok] = c[ok] / norm[ok, None]
    sims = vecs @ reps.T
    assign = np.argmax(sims, axis=1)
    keep = np.unique(assign)
    if medoid:
        reps = np.stack([vecs[np.where(assign == j)[0][np.argmax(sims[assign == j, j])]] for j in keep])
    else:
        reps = reps[keep]
    rep_hops = np.array([hops[assign == j].min() for j in keep])
    rep_weights = np.array([weights[assign == j].sum() for j in keep], dtype=np.float32)
    return reps.astype(np.float32), rep_hops, rep_weights


def match_rows(new, new_hops, old, old_hops, threshold):
    """Pair new rows with the rows the receiver already holds, closest pairs first.

    Two rows are the same row if their hop counts agree and they differ by at
    most `threshold` (1 - cosine). Each old row is used once. Returns {new: old}.
    """
    if len(new) == 0 or len(old) == 0:
        return {}
    sims = new @ old.T
    sims[new_hops[:, None] != old_hops[None, :]] = -2.0
    cand = np.argwhere(sims >= 1.0 - threshold)
    cand = cand[np.argsort(-sims[cand[:, 0], cand[:, 1]], kind="stable")]
    pairs, used = {}, set()
    for i, j in cand:
        i, j = int(i), int(j)
        if i not in pairs and j not in used:
            pairs[i] = j
            used.add(j)
    return pairs


class SFIB:
    """S-FIB of a single router: per neighbour index, (reps, hops, weights)."""

    def __init__(self, node, neighbors, dim, radius, k, exact_hops=0, tier_aware=False):
        self.node = node
        self.neighbors = list(neighbors)
        self.index = {n: i for i, n in enumerate(self.neighbors)}
        self.dim = dim
        self.radius = radius
        self.k = k
        self.exact_hops = exact_hops
        self.tier_aware = tier_aware    # a delta may only touch rows of its own tier
        self.rows = [self._empty() for _ in self.neighbors]
        self.exact = [{} for _ in self.neighbors]   # agent -> (vector, hops), exact mode only
        self._matrix = None

    def _empty(self):
        return (np.zeros((0, self.dim), np.float32), np.zeros(0, int), np.zeros(0, np.float32))

    def clear(self):
        self.rows = [self._empty() for _ in self.neighbors]
        self.exact = [{} for _ in self.neighbors]
        self._matrix = None

    def set_row(self, i, reps, hops, weights):
        self.rows[i] = (reps, hops, weights)
        self._matrix = None

    def set_from_exact(self, i):
        """Rebuild the row of neighbour i from its per-agent entries (exact mode)."""
        e = self.exact[i]
        if not e:
            self.rows[i] = self._empty()
        else:
            self.rows[i] = (np.stack([v for v, _ in e.values()]),
                            np.array([h for _, h in e.values()]),
                            np.ones(len(e), np.float32))
        self._matrix = None

    def n_vectors(self, neighbor):
        return len(self.rows[self.index[neighbor]][0])

    def apply_delta(self, i, vec, delta, hop, threshold):
        """One agent arrives (+1) or leaves (-1) behind neighbour i.

        Returns True if a representative moved by more than `threshold` (and
        changes it). False means the change is too small to be worth a message.
        """
        reps, hops, weights = self.rows[i]
        if len(reps) == 0:
            if delta < 0:
                return False
            self.set_row(i, vec[None, :].copy(), np.array([hop]), np.ones(1, np.float32))
            return True
        pick = np.arange(len(reps))
        if self.tier_aware:         # a far agent must not change the row of a nearby one
            pick = np.nonzero((hops <= self.exact_hops) == (hop <= self.exact_hops))[0]
            if len(pick) == 0:
                if delta < 0:
                    return False
                self.set_row(i, np.vstack([reps, vec]), np.append(hops, hop), np.append(weights, 1.0))
                return True
        sims = reps[pick] @ vec
        best = int(np.argmax(sims))
        j = int(pick[best])
        if delta > 0 and hop <= self.exact_hops:      # per-agent row of a nearby agent
            self.set_row(i, np.vstack([reps, vec]), np.append(hops, hop), np.append(weights, 1.0))
            return True
        if delta > 0 and len(pick) < self.k and sims[best] < 0.95:
            self.set_row(i, np.vstack([reps, vec]), np.append(hops, hop), np.append(weights, 1.0))
            return True
        new_weight = weights[j] + delta
        if new_weight <= 0:
            keep = np.arange(len(reps)) != j
            self.set_row(i, reps[keep], hops[keep], weights[keep])
            return True
        c = reps[j] * weights[j] + delta * vec
        norm = np.linalg.norm(c)
        if norm < 1e-6:
            return False
        c = c / norm
        if 1.0 - float(c @ reps[j]) <= threshold:
            return False
        reps = reps.copy()
        hops = hops.copy()
        weights = weights.copy()
        reps[j] = c
        weights[j] = new_weight
        if delta > 0:
            hops[j] = min(hops[j], hop)
        self.set_row(i, reps, hops, weights)
        return True

    def entries(self):
        """All rows of the table: (vectors, neighbour index of each, hops of each)."""
        if self._matrix is None:
            rows = [r for r in self.rows if len(r[0])]
            owner = [np.full(len(r[0]), i) for i, r in enumerate(self.rows) if len(r[0])]
            if rows:
                self._matrix = (np.vstack([r[0] for r in rows]), np.concatenate(owner),
                                np.concatenate([r[1] for r in rows]))
            else:
                self._matrix = (np.zeros((0, self.dim), np.float32), np.zeros(0, int), np.zeros(0, int))
        return self._matrix

    def scores(self, intent):
        """Per neighbour index: (max cos, mean cos, hops of the best representative).

        Neighbours without any entry get max = mean = -1 and hops = radius + 1.
        """
        mat, owner, hops = self.entries()
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
    """Builds and maintains the S-FIBs of all routers and counts the control traffic."""

    def __init__(self, graph, dim, radius, summary="kmeans", k=8, change_threshold=0.01,
                 encoding="int8", exact_hops=1, tier_aware=False, warm_start=True):
        self.graph = graph
        self.dim = dim
        self.radius = radius
        self.summary = summary
        self.k = 1 if summary == "mean" else k
        self.change_threshold = change_threshold
        self.encoding = encoding
        self.exact_hops = exact_hops    # agents this close keep their own row (two-tier table)
        self.warm_start = warm_start    # incremental refresh continues k-means from the old centres
        self.alive = set(graph.nodes)
        self.tables = {u: SFIB(u, sorted(graph.neighbors(u)), dim, radius, self.k, exact_hops, tier_aware)
                       for u in graph.nodes}
        self.local = {u: {} for u in graph.nodes}       # router -> {agent id: vector}
        self.row_bytes = header_bytes(encoding, dim) + ROW_META
        self._dag_cache = {}

    def delta_bytes(self):
        """Size of one withdraw or announce message."""
        return MSG_OVERHEAD + self.row_bytes

    # ---- full rebuild --------------------------------------------------
    def _encode(self, reps):
        if self.encoding == "float32":
            return reps
        return np.stack([quantize(r, self.encoding) for r in reps]).astype(np.float32)

    def _advert(self, u, w, warm=None):
        """The summary that router u sends to neighbour w, or None if it knows nothing."""
        vecs, hops, weights = [], [], []
        keep = None                     # rows that are sent as they are
        if self.local[u]:
            v = np.stack(list(self.local[u].values()))
            if self.exact_hops >= 1:
                keep = v
            else:
                vecs.append(v)
                hops.append(np.ones(len(v), int))
                weights.append(np.ones(len(v), np.float32))
        t = self.tables[u]
        for i, n in enumerate(t.neighbors):
            if n == w or n not in self.alive:
                continue
            reps, h, wt = t.rows[i]
            near = h + 1 <= self.radius
            if near.any():
                vecs.append(reps[near])
                hops.append(h[near] + 1)
                weights.append(wt[near])
        rows = []
        if keep is not None:
            rows.append((self._encode(keep), np.ones(len(keep), int), np.ones(len(keep), np.float32)))
        if vecs:
            reps, h, wt = kmeans_summary(np.vstack(vecs), np.concatenate(weights), np.concatenate(hops),
                                         self.k, medoid=self.summary == "medoid", init=warm)
            rows.append((self._encode(reps), h, wt))
        if not rows:
            return None
        return (np.vstack([r[0] for r in rows]), np.concatenate([r[1] for r in rows]),
                np.concatenate([r[2] for r in rows]))

    def _build_summaries(self):
        for t in self.tables.values():
            t.clear()
        for _ in range(self.radius):
            adverts = []
            for u in self.alive:
                for w in self.tables[u].neighbors:
                    if w in self.alive:
                        adv = self._advert(u, w)
                        if adv is not None:
                            adverts.append((u, w, adv))
            for u, w, (reps, h, wt) in adverts:
                t = self.tables[w]
                t.set_row(t.index[u], reps, h, wt)

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

    def _build_exact(self):
        for t in self.tables.values():
            t.clear()
        for v, agents in self.local.items():
            if v not in self.alive or not agents:
                continue
            for d, u, n in self.dag(v):
                t = self.tables[u]
                i = t.index[n]
                for a, vec in agents.items():
                    t.exact[i][a] = (vec, d)
        for t in self.tables.values():
            for i in range(len(t.neighbors)):
                t.set_from_exact(i)

    def build(self):
        """Recompute every table from the true state. Returns (messages, bytes) of one full round."""
        if self.summary == "exact":
            self._build_exact()
        else:
            self._build_summaries()
        return self.round_cost()

    def round_cost(self):
        """One advertisement per (neighbour -> router) pair that has entries."""
        msgs, n_bytes = 0, 0
        for u in self.alive:
            t = self.tables[u]
            for i, n in enumerate(t.neighbors):
                if n in self.alive and len(t.rows[i][0]):
                    msgs += 1
                    n_bytes += MSG_OVERHEAD + len(t.rows[i][0]) * self.row_bytes
        return msgs, n_bytes

    # ---- incremental refresh ----------------------------------------------
    def _diff_link(self, u, w):
        """What u has to tell w to bring w's row about u up to date.

        Returns None if nothing needs to be sent, else (new row, rows sent,
        rows withdrawn). The comparison is against what w actually holds, so
        small changes add up until they cross the threshold.
        """
        t = self.tables[w]
        old, old_hops, old_wt = t.rows[t.index[u]]
        warm = old[old_hops > self.exact_hops] if self.warm_start else None
        adv = self._advert(u, w, warm)
        if adv is None:
            return None if len(old) == 0 else (t._empty(), 0, len(old))
        new, new_hops, new_wt = adv
        pairs = match_rows(new, new_hops, old, old_hops, self.change_threshold)
        fresh = np.array([i for i in range(len(new)) if i not in pairs], dtype=int)
        n_gone = max(0, len(old) - len(pairs) - len(fresh))
        if len(fresh) == 0 and n_gone == 0:
            return None
        kept = np.array(sorted(pairs.values()), dtype=int)
        row = (np.vstack([old[kept], new[fresh]]), np.concatenate([old_hops[kept], new_hops[fresh]]),
               np.concatenate([old_wt[kept], new_wt[fresh]]))
        return row, len(fresh), n_gone

    def _link_cost(self, n_sent, n_gone):
        return MSG_OVERHEAD + n_sent * (self.row_bytes + ROW_ID) + n_gone * ROW_ID

    def refresh_incremental(self, digests=True):
        """A soft-state round that sends only the rows that changed.

        Links with nothing to report carry a digest, so the receiver can still
        tell that its rows are alive. Returns (messages, bytes).
        """
        if self.summary == "exact":
            return self._refresh_exact(digests)
        links = [(u, w) for u in self.alive for w in self.tables[u].neighbors if w in self.alive]
        msgs, n_bytes, touched = 0, 0, set()
        for _ in range(self.radius):
            updates = [(u, w, self._diff_link(u, w)) for u, w in links]
            updates = [x for x in updates if x[2] is not None]
            if not updates:
                break
            for u, w, (row, n_sent, n_gone) in updates:
                t = self.tables[w]
                t.set_row(t.index[u], *row)
                msgs += 1
                n_bytes += self._link_cost(n_sent, n_gone)
                touched.add((u, w))
        if digests:
            for u, w in links:
                t = self.tables[w]
                if (u, w) not in touched and len(t.rows[t.index[u]][0]):
                    msgs += 1
                    n_bytes += MSG_OVERHEAD + DIGEST
        return msgs, n_bytes

    def _refresh_exact(self, digests=True):
        """Same idea for per-agent tables: count only agents that were added or removed."""
        before = {u: [dict(e) for e in self.tables[u].exact] for u in self.alive}
        self._build_exact()
        msgs, n_bytes = 0, 0
        for u in self.alive:
            t = self.tables[u]
            for i, n in enumerate(t.neighbors):
                if n not in self.alive:
                    continue
                old, new = before[u][i], t.exact[i]
                n_sent = sum(1 for a, (_, h) in new.items() if a not in old or old[a][1] != h)
                n_gone = sum(1 for a in old if a not in new)
                if n_sent or n_gone:
                    msgs += 1
                    n_bytes += self._link_cost(n_sent, n_gone)
                elif digests and new:
                    msgs += 1
                    n_bytes += MSG_OVERHEAD + DIGEST
        return msgs, n_bytes

    # ---- incremental updates (handover) -----------------------------------
    def spread(self, v, frontier, seen, agent, vec, delta, d):
        """Move a withdraw/announce one hop further.

        Returns (changed links as (sender, receiver), next frontier).
        """
        changed = []
        if self.summary == "exact":
            for dist, u, n in self.dag(v):
                if dist != d:
                    continue
                t = self.tables[u]
                i = t.index[n]
                if delta > 0:
                    t.exact[i][agent] = (vec, d)
                else:
                    t.exact[i].pop(agent, None)
                t.set_from_exact(i)
                changed.append((n, u))
            return changed, frontier
        next_frontier = []
        for x in frontier:
            for w in self.graph.neighbors(x):
                if w in seen or w not in self.alive:
                    continue
                t = self.tables[w]
                if t.apply_delta(t.index[x], vec, delta, d, self.change_threshold):
                    changed.append((x, w))
                    seen.add(w)
                    next_frontier.append(w)
        return changed, next_frontier

    # ---- failures --------------------------------------------------------
    def fail(self, nodes):
        """Remove failed routers and rebuild. Returns (messages, bytes) of the changed adverts."""
        before = self._snapshot()
        self.alive -= set(nodes)
        for v in nodes:
            self.local[v] = {}
        self._dag_cache = {}
        self.build()
        after = self._snapshot()
        msgs, n_bytes = 0, 0
        for key, value in after.items():
            if before.get(key) != value[0]:
                msgs += 1
                n_bytes += MSG_OVERHEAD + value[1] * self.row_bytes
        return msgs, n_bytes

    def fail_incremental(self, nodes):
        """Failure without a rebuild: forget the dead neighbours, then resynchronise."""
        self.alive -= set(nodes)
        for v in nodes:
            self.local[v] = {}
        self._dag_cache = {}
        for u in self.alive:
            t = self.tables[u]
            for v in nodes:
                if v in t.index:
                    t.set_row(t.index[v], *t._empty())
                    t.exact[t.index[v]] = {}
        return self.refresh_incremental(digests=False)

    def _snapshot(self):
        snap = {}
        for u in self.alive:
            t = self.tables[u]
            for i, n in enumerate(t.neighbors):
                reps = t.rows[i][0]
                if n in self.alive and len(reps):
                    snap[(n, u)] = (reps.tobytes(), len(reps))
        return {k: v for k, v in snap.items()}
