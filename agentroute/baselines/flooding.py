"""Baseline: TTL-limited flooding.

The request is copied to every neighbour until its TTL runs out. Each router
handles a request only once (duplicate suppression by packet id) and
broadcasts it to its attached agents. Every agent with cos >= tau answers; the
requester picks the most similar answer. Simple and robust, but the number of
messages grows with the size of the network.

Responsible: Ömer Faruk Gedikli
"""


class Flooding:
    def __init__(self, sim, ttl, window_s=1.0):
        self.sim = sim
        self.ttl = ttl
        self.window = window_s    # how long the requester collects answers

    def query(self, pkt, start):
        sim = self.sim
        reason = yield from sim.radio()
        if reason:
            return sim.finish(pkt, False, reason, at=start)
        state = {"seen": set(), "answers": []}
        sim.env.process(self.copy(pkt, state, start, self.ttl, None, 0))
        yield sim.env.timeout(self.window)
        if not state["answers"]:
            return sim.finish(pkt, False, "not_found")
        _, arrival, agent, hops, u = max(state["answers"])
        pkt.hops = hops
        if sim.agent_class[agent] != pkt.intent_class:
            return sim.finish(pkt, False, "wrong_agent", at=u)
        return sim.finish(pkt, True, None, agent=agent, time=arrival - pkt.created)

    def copy(self, pkt, state, u, ttl, prev, hops):
        sim = self.sim
        if u in state["seen"]:
            return
        state["seen"].add(u)
        reason = yield from sim.transit(u)
        if reason:
            return
        ids = [a for a in sim.at_router[u] if a != pkt.src_agent]
        if ids:
            sim.query_msgs += 1                    # one broadcast to the local agents
            sims = sim.agent_vec[ids] @ pkt.intent
            j = int(sims.argmax())
            if sims[j] >= sim.tau:
                radio = sim.cfg["topology"]["delay_ms"]["radio"] / 1000.0
                state["answers"].append((float(sims[j]), sim.env.now + radio, ids[j], hops, u))
        if ttl == 0:
            return
        for v in sim.G.adj[u]:
            if v == prev or v in sim.known_dead:
                continue
            sim.query_msgs += 1
            sim.log.log(t=sim.env.now, type="hop", pkt=pkt.pid, method=sim.method,
                        **{"from": int(u), "to": int(v)})
            sim.env.process(self.forward(pkt, state, u, v, ttl - 1, hops + 1))

    def forward(self, pkt, state, u, v, ttl, hops):
        reason = yield from self.sim.link(u, v)
        if reason:
            return
        yield from self.copy(pkt, state, v, ttl, u, hops)
