"""Baseline: central (DNS-like) capability registry.

One registry server sits on the most central core router. Every agent
registers its capability vector and location there, refreshes it periodically
and sends an update after every handover. A request travels to the registry,
the registry returns the best matching agent (semantic match, nearest copy),
and the requester then sends the task to that agent's last known cell.

Weak points that the experiments show: the server is a queue that every
registration and every request must pass (bottleneck), its router is a single
point of failure, and locations are stale for a while after a handover.

Responsible: Ömer Faruk Gedikli
"""
import networkx as nx
import numpy as np
import simpy


class Registry:
    def __init__(self, sim, bcfg):
        self.sim = sim
        xy = np.array([[sim.G.nodes[c]["x"], sim.G.nodes[c]["y"]] for c in sim.cores])
        center = xy.mean(axis=0)
        self.node = sim.cores[int(np.argmin(np.linalg.norm(xy - center, axis=1)))]
        self.server = simpy.Resource(sim.env, capacity=1)
        self.service = bcfg["registry_service_ms"] / 1000.0
        self.limit = bcfg["registry_queue_limit"]
        self.expiry = 3 * sim.cfg["sfib"]["refresh_s"]
        self.loc = np.full(sim.n_agents, -1)
        self.stamp = np.full(sim.n_agents, -1e9)

    def _path_delay(self, path):
        return sum(self.sim.G.edges[a, b]["delay"] for a, b in zip(path, path[1:]))

    def refresh(self, period, initial=False):
        """Soft-state registrations, spread uniformly over one refresh period."""
        sim = self.sim
        agents = [a for a in range(sim.n_agents) if sim.attached[a] >= 0]
        if initial:
            for a in agents:
                path = sim.path(int(sim.attached[a]), self.node)
                if path:
                    sim.ctrl_msgs += len(path) - 1
                    self.loc[a] = sim.attached[a]
                    self.stamp[a] = 0.0
            return
        gap = period / max(len(agents), 1)
        for a in agents:
            yield sim.env.timeout(gap)
            sim.env.process(self.update(a))

    def update(self, a):
        """Agent a tells the registry where it is now."""
        sim = self.sim
        u = int(sim.attached[a])
        if u < 0:
            return
        path = sim.path(u, self.node)
        if not path:
            return
        sim.ctrl_msgs += len(path) - 1
        yield sim.env.timeout(self._path_delay(path))
        if not sim.routers[self.node].alive or len(self.server.queue) >= self.limit:
            return
        with self.server.request() as req:
            yield req
            yield sim.env.timeout(self.service)
        self.loc[a] = u
        self.stamp[a] = sim.env.now

    def lookup(self, pkt, start):
        sim = self.sim
        valid = (self.loc >= 0) & (sim.env.now - self.stamp <= self.expiry)
        valid[pkt.src_agent] = False
        if not valid.any():
            return None
        sims = (sim.card_vecs @ pkt.intent)[sim.agent_card]
        sims[~valid] = -2.0
        best = sims.max()
        if best < sim.tau:
            return None
        ties = np.nonzero(sims == best)[0]
        dist = nx.single_source_shortest_path_length(sim.live, start)
        return int(min(ties, key=lambda a: (dist.get(int(self.loc[a]), 1e9), a)))

    def query(self, pkt, start):
        sim = self.sim
        reason = yield from sim.radio(pkt.src_agent)
        if reason:
            return sim.finish(pkt, False, reason, at=start)
        path = sim.path(start, self.node)
        if not path:
            return sim.finish(pkt, False, "no_route", at=start)
        reason, at = yield from sim.traverse(pkt, path)
        if reason:
            return sim.finish(pkt, False, reason, at=at)
        if len(self.server.queue) >= self.limit:
            return sim.finish(pkt, False, "registry_queue", at=self.node)
        with self.server.request() as req:
            yield req
            yield sim.env.timeout(self.service)
        agent = self.lookup(pkt, start)
        # the answer goes back to the requester in any case
        reason, at = yield from sim.traverse(pkt, sim.path(self.node, start))
        if reason:
            return sim.finish(pkt, False, reason, at=at)
        if agent is None:
            return sim.finish(pkt, False, "not_found", at=self.node)
        for _ in range(2):              # answer down to the UE, task back up
            reason = yield from sim.radio(pkt.src_agent)
            if reason:
                return sim.finish(pkt, False, reason, at=start)
        target = int(self.loc[agent])
        task_path = sim.path(start, target)
        if not task_path:
            return sim.finish(pkt, False, "no_route", at=start)
        reason, at = yield from sim.traverse(pkt, task_path)
        if reason:
            return sim.finish(pkt, False, reason, at=at)
        reason = yield from sim.deliver_to(pkt, target, agent)
        if reason == "handover":
            reason = "stale_location"
        if reason:
            return sim.finish(pkt, False, reason, at=target)
        return sim.finish(pkt, True, None, agent=agent)
