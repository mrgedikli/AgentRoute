"""Baseline: capability registry (one central server, or several replicas).

The registry servers sit on core routers. Every agent registers its capability
vector and location at the nearest server, refreshes it periodically and
sends an update after every handover. A request travels to the nearest server,
the server returns the best matching agent, and the requester then sends the
task to that agent's last known cell.

With one server this is the DNS-like baseline of the proposal: its router is a
single point of failure and locations are stale for a while after a handover.
With three replicas it is what a real deployment would look like (v2): every
registration is copied to the other replicas, and a replica's failure only
sends its clients to the next one. A lookup (a vector search) and a
registration (a table write) have different service times.

Responsible: Ömer Faruk Gedikli (v2 revision written with AI assistance)
"""
import numpy as np
import simpy

SMALL_MSG = 64
TIE_BAND = 0.02     # agents this close to the best match count as equally good


class Registry:
    def __init__(self, sim, bcfg, n_replicas=1):
        self.sim = sim
        xy = np.array([[sim.G.nodes[c]["x"], sim.G.nodes[c]["y"]] for c in sim.cores])
        center = xy.mean(axis=0)
        # first server in the middle, then the core routers farthest from those chosen
        chosen = [int(np.argmin(np.linalg.norm(xy - center, axis=1)))]
        while len(chosen) < min(n_replicas, len(sim.cores)):
            dist = np.min(np.linalg.norm(xy[:, None] - xy[chosen][None], axis=2), axis=1)
            chosen.append(int(np.argmax(dist)))
        self.nodes = [sim.cores[i] for i in chosen]
        self.servers = {u: simpy.Resource(sim.env, capacity=1) for u in self.nodes}
        self.service = bcfg["registry_service_ms"] / 1000.0
        self.update_service = bcfg["registry_update_ms"] / 1000.0
        self.limit = bcfg["registry_queue_limit"]
        self.expiry = 3 * sim.cfg["sfib"]["refresh_s"]
        self.loc = np.full(sim.n_agents, -1)
        self.stamp = np.full(sim.n_agents, -1e9)
        self.size = sim.query_size

    def _alive_servers(self):
        return [u for u in self.nodes if u not in self.sim.known_dead]

    def nearest(self, u):
        """The closest server that is not known to be down, and the path to it."""
        best, best_path, best_delay = None, None, 1e9
        for s in self._alive_servers():
            path = self.sim.path(u, s)
            if path and self._path_delay(path) < best_delay:
                best, best_path, best_delay = s, path, self._path_delay(path)
        return best, best_path

    def _path_delay(self, path):
        return sum(self.sim.G.edges[a, b]["delay"] for a, b in zip(path, path[1:]))

    def _sync_cost(self, server):
        """A registration is copied from one replica to all the others."""
        msgs = 0
        for s in self._alive_servers():
            if s != server:
                path = self.sim.path(server, s)
                msgs += len(path) - 1 if path else 0
        return msgs

    def refresh(self, period, initial=False):
        """Soft-state registrations, spread uniformly over one refresh period."""
        sim = self.sim
        agents = [a for a in range(sim.n_agents) if sim.attached[a] >= 0]
        if initial:
            for a in agents:
                server, path = self.nearest(int(sim.attached[a]))
                if path:
                    sim.count_ctrl(len(path) - 1, (len(path) - 1) * self.size)
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
        server, path = self.nearest(u)
        if not path:
            return
        msgs = len(path) - 1 + self._sync_cost(server)
        sim.count_ctrl(msgs, msgs * SMALL_MSG)
        yield sim.env.timeout(self._path_delay(path))
        if not sim.routers[server].alive or len(self.servers[server].queue) >= self.limit:
            return
        with self.servers[server].request() as req:
            yield req
            yield sim.env.timeout(self.update_service)
        self.loc[a] = u
        self.stamp[a] = sim.env.now

    def lookup(self, pkt, start):
        sim = self.sim
        valid = (self.loc >= 0) & (sim.env.now - self.stamp <= self.expiry)
        valid[pkt.src_agent] = False
        if not valid.any():
            return None
        sims = sim.agent_vec @ pkt.intent
        sims[~valid] = -2.0
        best = sims.max()
        if best < sim.tau:
            return None
        ties = np.nonzero(sims >= best - TIE_BAND)[0]
        dist = sim.hop_distance(start)
        return int(min(ties, key=lambda a: (dist.get(int(self.loc[a]), 1e9), -sims[a], a)))

    def query(self, pkt, start):
        sim = self.sim
        reason = yield from sim.radio(pkt.src_agent)
        if reason:
            return sim.finish(pkt, False, reason, at=start)
        server, path = self.nearest(start)
        if not path:
            return sim.finish(pkt, False, "no_route", at=start)
        reason, at = yield from sim.traverse(pkt, path)
        if reason:
            return sim.finish(pkt, False, reason, at=at)
        if len(self.servers[server].queue) >= self.limit:
            return sim.finish(pkt, False, "registry_queue", at=server)
        with self.servers[server].request() as req:
            yield req
            yield sim.env.timeout(self.service)
        agent = self.lookup(pkt, start)
        # the answer goes back to the requester in any case
        reason, at = yield from sim.traverse(pkt, sim.path(server, start), size=SMALL_MSG)
        if reason:
            return sim.finish(pkt, False, reason, at=at)
        if agent is None:
            return sim.finish(pkt, False, "not_found", at=server)
        for _ in range(2):              # answer down to the UE, task back up
            reason = yield from sim.radio(pkt.src_agent)
            if reason:
                return sim.finish(pkt, False, reason, at=start)
        target = int(self.loc[agent])
        task_path = sim.path(start, target)
        if not task_path:
            return sim.finish(pkt, False, "no_route", at=start)
        reason, at = yield from sim.traverse(pkt, task_path, size=SMALL_MSG)
        if reason:
            return sim.finish(pkt, False, reason, at=at)
        reason = yield from sim.deliver_to(pkt, target, agent)
        if reason == "handover":
            reason = "stale_location"
        if reason:
            return sim.finish(pkt, False, reason, at=target)
        return sim.finish(pkt, True, None, agent=agent)
