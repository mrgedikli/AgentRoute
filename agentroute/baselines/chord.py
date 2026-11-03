"""Baseline: Chord DHT with exact-match keys.

Routers form a Chord ring (SHA-1 identifiers, finger tables, O(log N)
lookups). An agent stores its capability name under key = SHA-1(name). A
request is looked up under SHA-1(request text). This is how exact-match
discovery works today; it is efficient, but a paraphrased request hashes to a
different key and is almost never found. We keep it as a reference point that
shows why semantic matching is needed, not as a serious competitor.

Responsible: Ömer Faruk Gedikli
"""
import bisect
import hashlib
import re


def normalize(text):
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", " ", text.lower())).strip()


def chash(text, bits):
    return int(hashlib.sha1(text.encode()).hexdigest(), 16) % (1 << bits)


class Chord:
    def __init__(self, sim, bits):
        self.sim = sim
        self.bits = bits
        self.M = 1 << bits
        self.agent_key = [chash(normalize(sim.card_text[sim.agent_card[a]]), bits)
                          for a in range(sim.n_agents)]
        self.rebuild(count=False)

    # ---- ring ---------------------------------------------------------
    def rebuild(self, count=True):
        sim = self.sim
        nodes = [u for u in sim.G.nodes if u not in sim.known_dead]
        pairs = sorted((chash(f"router-{u}", self.bits), u) for u in nodes)
        self.ring = [i for i, _ in pairs]
        self.ring_nodes = [u for _, u in pairs]
        self.id_of = {u: i for i, u in pairs}
        self.fingers = {u: [self.successor((self.id_of[u] + (1 << k)) % self.M)
                            for k in range(self.bits)] for u in nodes}
        self._cost = {}
        self.store = {}
        self.loc = {}
        for a in range(sim.n_agents):
            if sim.attached[a] >= 0:
                self.put(a, count=count)

    def successor(self, key):
        idx = bisect.bisect_left(self.ring, key) % len(self.ring)
        return self.ring_nodes[idx]

    def _between(self, x, a, b, inclusive=True):
        """x in (a, b] on the ring (or (a, b) if not inclusive)."""
        if a < b:
            return a < x <= b if inclusive else a < x < b
        return (x > a or x <= b) if inclusive else (x > a or x < b)

    def route(self, start, key):
        """Overlay path [start, ..., responsible node] of a Chord lookup."""
        n = start
        path = [n]
        for _ in range(2 * self.bits):
            succ = self.fingers[n][0]
            if self._between(key, self.id_of[n], self.id_of[succ]):
                if succ != n:
                    path.append(succ)
                return path
            nxt = n
            for f in reversed(self.fingers[n]):
                if self._between(self.id_of[f], self.id_of[n], key, inclusive=False):
                    nxt = f
                    break
            if nxt == n:
                path.append(succ)
                return path
            path.append(nxt)
            n = nxt
        return path

    def cost(self, start, key):
        """Underlay messages of one lookup (cached)."""
        if (start, key) not in self._cost:
            route = self.route(start, key)
            hops = 0
            for a, b in zip(route, route[1:]):
                p = self.sim.path(a, b)
                hops += len(p) - 1 if p else 0
            self._cost[(start, key)] = hops
        return self._cost[(start, key)]

    # ---- storage ------------------------------------------------------
    def put(self, a, count=True):
        u = int(self.sim.attached[a])
        if u < 0 or u not in self.id_of:
            return
        key = self.agent_key[a]
        self.store.setdefault(self.successor(key), {}).setdefault(key, set()).add(a)
        self.loc[a] = u
        if count:
            self.sim.ctrl_msgs += self.cost(u, key)

    def on_move(self, a):
        self.put(a)

    def refresh(self):
        sim = self.sim
        for a in range(sim.n_agents):
            u = int(sim.attached[a])
            if u >= 0 and u in self.id_of:
                sim.ctrl_msgs += self.cost(u, self.agent_key[a])

    # ---- lookup -------------------------------------------------------
    def query(self, pkt, start):
        sim = self.sim
        reason = yield from sim.radio()
        if reason:
            return sim.finish(pkt, False, reason, at=start)
        key = chash(normalize(pkt.text), self.bits)
        route = self.route(start, key)
        for a, b in zip(route, route[1:]):
            reason, at = yield from sim.traverse(pkt, sim.path(a, b))
            if reason:
                return sim.finish(pkt, False, reason, at=at)
        resp = route[-1]
        agents = [a for a in self.store.get(resp, {}).get(key, set()) if a != pkt.src_agent]
        back = sim.path(resp, start)
        if back:
            reason, at = yield from sim.traverse(pkt, back)
            if reason:
                return sim.finish(pkt, False, reason, at=at)
        if not agents:
            return sim.finish(pkt, False, "not_found", at=resp)
        agent = min(agents)
        target = self.loc[agent]
        reason, at = yield from sim.traverse(pkt, sim.path(start, target))
        if reason:
            return sim.finish(pkt, False, reason, at=at)
        reason = yield from sim.deliver_to(pkt, target, agent)
        if reason == "handover":
            reason = "stale_location"
        if reason:
            return sim.finish(pkt, False, reason, at=target)
        return sim.finish(pkt, True, None, agent=agent)
