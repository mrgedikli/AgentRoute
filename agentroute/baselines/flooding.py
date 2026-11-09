"""Baseline: TTL-limited flooding.

The request is copied to every neighbour until its TTL runs out. Each router
handles a request only once (duplicate suppression by packet id) and
broadcasts it to its attached agents. A router whose best agent has
cos >= tau sends an answer back to the requester. The requester collects
answers for a fixed window, picks the most similar one and sends the task
there. The window, the answers and the task are part of the cost (v2).

Responsible: Ömer Faruk Gedikli (v2 revision written with AI assistance)
"""
SMALL_MSG = 64


class Flooding:
    def __init__(self, sim, ttl, window_s=0.2):
        self.sim = sim
        self.ttl = ttl
        self.window = window_s    # how long the requester collects answers
        self.copies = 0           # router-to-router copies of the request

    def query(self, pkt, start):
        sim = self.sim
        reason = yield from sim.radio(pkt.src_agent)
        if reason:
            return sim.finish(pkt, False, reason, at=start)
        state = {"seen": set(), "answers": [], "closed": False}
        sim.env.process(self.copy(pkt, state, start, start, self.ttl, None))
        yield sim.env.timeout(self.window)
        state["closed"] = True
        if not state["answers"]:
            return sim.finish(pkt, False, "not_found", at=start)
        _, agent, u = max(state["answers"])
        pkt.hops = 0
        reason = yield from sim.radio(pkt.src_agent)    # the task goes from the UE back to its router
        if reason:
            return sim.finish(pkt, False, reason, at=start)
        reason, at = yield from sim.traverse(pkt, sim.path(start, u), log_hops=False, size=SMALL_MSG)
        if reason:
            return sim.finish(pkt, False, reason, at=at)
        reason = yield from sim.deliver_to(pkt, u, agent)
        if reason == "handover":
            reason = "stale_location"
        if reason:
            return sim.finish(pkt, False, reason, at=u)
        return sim.finish(pkt, True, None, agent=agent)

    def copy(self, pkt, state, start, u, ttl, prev):
        sim = self.sim
        if u in state["seen"]:
            return
        state["seen"].add(u)
        reason = yield from sim.transit(u)
        if reason:
            return
        ids = [a for a in sim.at_router[u] if a != pkt.src_agent]
        if ids:
            sim.count_query()                      # one broadcast to the local agents
            sims = sim.agent_vec[ids] @ pkt.intent
            j = int(sims.argmax())
            if sims[j] >= sim.tau:
                sim.env.process(self.answer(pkt, state, start, u, ids[j], float(sims[j])))
        if ttl == 0:
            return
        for v in sim.G.adj[u]:
            if v == prev or v in sim.known_dead:
                continue
            sim.count_query()
            self.copies += 1
            sim.log.log(t=sim.env.now, type="hop", pkt=pkt.pid, method=sim.method,
                        **{"from": int(u), "to": int(v)})
            sim.env.process(self.forward(pkt, state, start, u, v, ttl - 1))

    def forward(self, pkt, state, start, u, v, ttl):
        reason = yield from self.sim.link(u, v)
        if reason:
            return
        yield from self.copy(pkt, state, start, v, ttl, u)

    def answer(self, pkt, state, start, u, agent, similarity):
        """The answer travels back to the requester and is real traffic."""
        sim = self.sim
        reason = yield from sim.radio(agent)            # agent -> its router
        if reason:
            return
        back = sim.path(u, start)
        if not back:
            return
        hops_before = pkt.hops
        reason, _ = yield from sim.traverse(pkt, back, log_hops=False, size=SMALL_MSG)
        pkt.hops = hops_before
        if reason:
            return
        reason = yield from sim.radio(pkt.src_agent)    # router -> requesting UE
        if reason or state["closed"]:
            return
        state["answers"].append((similarity, agent, u))
