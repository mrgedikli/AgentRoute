"""SimPy discrete-event simulator for AgentRoute and the baselines.

What is modelled
  - routers: one SimPy server each (service time + queue limit) plus bursty
    background traffic (M/M/1 waiting time; some routers are "hotspots"),
  - links: propagation delay and loss probability,
  - agents: fixed edge agents, cloud agents and random-waypoint mobile agents,
  - handovers with a short interruption, node failures with detection delay,
  - ten discovery methods: AgentRoute (DQN and GNN), greedy and load-aware
    greedy forwarding, SPFR-style forwarding, TTL-limited flooding, a central
    and a replicated registry, Chord and a semantic DHT.

Every method sees the same topology, mobility and query sequence for a given
seed, because each kind of randomness has its own random stream.

Responsible: Ömer Faruk Gedikli (v2 revision written with AI assistance)
"""
import json
import math
from collections import Counter

import networkx as nx
import numpy as np
import simpy

from agentroute.config import RESULTS, ROOT
from agentroute.data.capabilities import class_names
from agentroute.embeddings import agent_vectors, header_bytes, load_dataset_vectors, quantize
from agentroute.forwarding import GreedyPolicy, LoadAwareGreedy, NodeView, Packet, SPFRPolicy, best_local_agent
from agentroute.radio import RadioLUT
from agentroute.sfib import MSG_OVERHEAD, Advertiser
from agentroute.sim.events import EventLog
from agentroute.sim.mobility import RandomWaypoint, handover_targets, nearest_cell
from agentroute.sim.topology import area_bounds, build_topology

METHODS = ["agentroute", "agentroute_gnn", "greedy", "greedy_load", "spfr",
           "flooding", "registry", "registry3", "chord", "sdht"]
SEMANTIC = ("agentroute", "agentroute_gnn", "greedy", "greedy_load", "spfr")
ADV_HOP_DELAY = 0.005   # an advertisement needs about 5 ms per hop
SMALL_MSG = 64          # bytes of a heartbeat, location update or answer

_DATA = None


def dataset():
    global _DATA
    if _DATA is None:
        _DATA = load_dataset_vectors()
    return _DATA


def load_tau(cfg):
    tau = cfg["forwarding"]["tau"]
    if tau is None:
        with open(RESULTS / "tau.json") as f:
            tau = json.load(f)["tau"]
    return float(tau)


def make_policy(method, cfg):
    if method == "greedy":
        return GreedyPolicy()
    if method == "greedy_load":
        return LoadAwareGreedy(cfg["forwarding"]["load_band"])
    if method == "spfr":
        return SPFRPolicy(cfg["forwarding"]["omega"])
    from agentroute.dqn.policy import DQNPolicy
    kind = "gnn" if method == "agentroute_gnn" else "mlp"
    key = "gnn_model_path" if kind == "gnn" else "model_path"
    return DQNPolicy.load(ROOT / cfg["dqn"][key], kind=kind)


class Router:
    def __init__(self, env, kind):
        self.kind = kind
        self.res = simpy.Resource(env, capacity=1)
        self.alive = True
        self.hotspot = False
        self.busy = False
        self.last_handover = -1e9
        self.occ = 0.0


class Simulator:
    def __init__(self, cfg, method, seed=None, policy=None, intents="test", log_dir=None):
        assert method in METHODS, method
        self.cfg = cfg
        self.method = method
        self.seed = cfg["seed"] if seed is None else seed
        self.semantic = method in SEMANTIC
        self.env = simpy.Environment()
        # separate random streams -> identical scenario for every method
        self.rng_topo = np.random.default_rng([self.seed, 1])
        self.rng_mob = np.random.default_rng([self.seed, 2])
        self.rng_traffic = np.random.default_rng([self.seed, 3])
        self.rng_net = np.random.default_rng([self.seed, 4])
        self.rng_fail = np.random.default_rng([self.seed, 5])

        sim, rt = cfg["sim"], cfg["routers"]
        self.duration = sim["duration_s"]
        self.warmup = sim["warmup_s"]
        self.load = sim["load"]
        self.tau = load_tau(cfg)
        self.accept_mode = cfg["forwarding"]["accept"]
        self.omega = cfg["forwarding"]["omega"]
        self.ttl = cfg["forwarding"]["ttl"]
        self.header = cfg["forwarding"]["header"]
        self.radius = cfg["sfib"]["radius"]
        self.service = rt["service_ms"] / 1000.0
        self.queue_limit = rt["queue_limit"]
        self.bg_service = rt["bg_service_ms"] / 1000.0
        self.bg_limit = rt["bg_queue_limit"]
        self.ho_window = cfg["sfib"]["handover_window_s"]

        data = dataset()
        self.card_vecs = data["desc_vecs"]
        self.card_class = data["desc_class"]
        self.class_vecs = data["class_vecs"]
        self.dim = self.card_vecs.shape[1]
        self.card_text = data["desc_text"]
        split = "test" if intents == "test" else "train"
        self.intent_vecs = data[f"{split}_vecs"]
        self.intent_class = data[f"{split}_class"]
        self.intent_text = data[f"{split}_text"]

        self.G = build_topology(cfg, self.rng_topo)
        self.kind = {u: self.G.nodes[u]["kind"] for u in self.G.nodes}
        self.gnbs = [u for u in self.G.nodes if self.kind[u] == "gnb"]
        self.cores = [u for u in self.G.nodes if self.kind[u] == "core"]
        self.cloud = next(u for u in self.G.nodes if self.kind[u] == "cloud")
        self.cell_xy = np.array([[self.G.nodes[u]["x"], self.G.nodes[u]["y"]] for u in self.gnbs])
        self.cell_of = {u: i for i, u in enumerate(self.gnbs)}
        radio_cfg = cfg["radio"]
        self.radio_lut = RadioLUT(ROOT / radio_cfg["lut_path"]) if radio_cfg["model"] == "sionna" else None
        self.routers = {u: Router(self.env, self.kind[u]) for u in self.G.nodes}
        n_hot = int(round(rt["hotspot_fraction"] * (len(self.gnbs) + len(self.cores))))
        self.hotspots = sorted(int(u) for u in self.rng_topo.choice(self.gnbs + self.cores, n_hot, replace=False))
        for u in self.hotspots:
            self.routers[u].hotspot = True
        self.known_dead = set()
        self.live = self.G.copy()
        self._paths = {}
        self._dist = {}
        self._compute_upstream()

        self.log = EventLog(log_dir)
        self.results = []
        self.ctrl_msgs = 0
        self.ctrl_bytes = 0
        self.query_msgs = 0
        self.query_bytes = 0
        self.query_size = header_bytes(self.header, self.dim) + MSG_OVERHEAD
        self.update_msgs = 0        # S-FIB messages triggered by handovers
        self.update_bytes = 0
        self.boot_bytes = 0         # the first control round, when every table is new
        self._steady_start = None   # (ctrl, update) bytes where the steady window opens
        self._steady_end = None
        self.handovers = 0
        self._init_agents()

        self.policy = None
        self.adv = None
        if self.semantic:
            self.policy = policy if policy is not None else make_policy(method, cfg)
            sf = cfg["sfib"]
            summary = "exact" if method == "spfr" else sf["summary"]
            if method == "spfr":
                self.radius = cfg["baselines"]["spfr_radius"]
            self.adv = Advertiser(self.G, self.dim, self.radius, summary, sf["k"],
                                  sf["change_threshold"], sf["encoding"], sf["exact_hops"],
                                  sf["tier_aware_delta"], sf["warm_start"])
            self.incremental = sf["refresh_mode"] == "incremental"
            for a in range(self.n_agents):
                if self.attached[a] >= 0:
                    self.adv.local[self.attached[a]][a] = self.agent_vec[a]
            self.adv.build()
        elif method == "flooding":
            from agentroute.baselines.flooding import Flooding
            self.flood = Flooding(self, cfg["baselines"]["flood_ttl"], cfg["baselines"]["flood_window_s"])
        elif method in ("registry", "registry3"):
            from agentroute.baselines.registry import Registry
            replicas = 1 if method == "registry" else cfg["baselines"]["registry3_replicas"]
            self.registry = Registry(self, cfg["baselines"], replicas)
        elif method == "chord":
            from agentroute.baselines.chord import Chord
            self.chord = Chord(self, cfg["baselines"]["chord_bits"])
        elif method == "sdht":
            from agentroute.baselines.chord import SemanticDHT
            self.chord = SemanticDHT(self, cfg["baselines"])
        self.log.write_topology(self.snapshot())

    # ------------------------------------------------------------------
    # agents
    def _init_agents(self):
        ag = self.cfg["agents"]
        n = ag["n_agents"]
        n_cloud = int(round(n * ag["cloud_fraction"]))
        n_mobile = int(round(n * ag["mobile_fraction"]))
        n_edge = n - n_cloud - n_mobile
        self.n_agents = n
        self.agent_kind = np.array(["edge"] * n_edge + ["mobile"] * n_mobile + ["cloud"] * n_cloud)
        # capability supply is long-tailed: a few classes are offered by many
        # agents, most by few (Zipf over a random ranking of the classes)
        n_cls = len(class_names())
        rank = self.rng_topo.permutation(n_cls)
        weights = 1.0 / (np.arange(1, n_cls + 1) ** ag["class_zipf"])
        cls = rank[self.rng_topo.choice(n_cls, size=n, p=weights / weights.sum())]
        var = self.rng_topo.integers(2, size=n)
        self.agent_card = 2 * cls + var
        assert (self.card_class[self.agent_card] == cls).all()
        self.agent_class = cls
        self.agent_vec = agent_vectors(self.class_vecs, cls, self.rng_topo, ag["card_alpha"])
        bounds = area_bounds(self.G)
        self.agent_xy = np.zeros((n, 2))
        self.agent_xy[:n_edge] = self.rng_topo.uniform(bounds[:2], bounds[2:], size=(n_edge, 2))
        self.agent_xy[n_edge + n_mobile:] = [self.G.nodes[self.cloud]["x"], self.G.nodes[self.cloud]["y"]]
        self.mobile_idx = np.arange(n_edge, n_edge + n_mobile)
        self.rwp = RandomWaypoint(n_mobile, bounds, ag["speed_mps"], ag["pause_s"], self.rng_mob)
        self.agent_xy[self.mobile_idx] = self.rwp.pos
        self.attached = np.full(n, -1)
        self.down = np.zeros(n, dtype=bool)
        self.ho_pending = np.zeros(n, dtype=bool)
        self.at_router = {u: [] for u in self.G.nodes}
        cells = nearest_cell(self.agent_xy[:n_edge + n_mobile], self.cell_xy)
        for a in range(n_edge + n_mobile):
            self._attach(a, self.gnbs[cells[a]])
        for a in range(n_edge + n_mobile, n):
            self._attach(a, self.cloud)
        self.requesters = np.arange(n_edge + n_mobile)  # cloud agents only serve

    def _attach(self, a, u):
        self.attached[a] = u
        self.at_router[u].append(int(a))

    def _detach(self, a):
        u = self.attached[a]
        if u >= 0:
            self.at_router[u].remove(int(a))
        self.attached[a] = -1
        return u

    # ------------------------------------------------------------------
    # routers and links
    def rho(self, r):
        base = self.cfg["routers"]["rho_busy"] if r.busy else self.cfg["routers"]["rho_base"]
        return min(0.97, base * self.load)

    def transit(self, u):
        """Queue and process a packet at router u. Returns a drop reason or None."""
        r = self.routers[u]
        if not r.alive:
            return "node_down"
        if len(r.res.queue) >= self.queue_limit:
            return "queue"
        with r.res.request() as req:
            yield req
            yield self.env.timeout(self.service)
        # waiting behind background traffic: number in system of an M/M/1 queue
        rho = self.rho(r)
        n_bg = int(math.log(1.0 - self.rng_net.random()) / math.log(rho))
        if n_bg >= self.bg_limit:
            return "queue"
        if n_bg > 0:
            yield self.env.timeout(self.rng_net.gamma(n_bg, self.bg_service))
        return None

    def link(self, u, v):
        e = self.G.edges[u, v]
        yield self.env.timeout(e["delay"])
        if self.rng_net.random() < e["loss"]:
            return "link"
        if not self.routers[v].alive:
            return "node_down"
        return None

    def radio(self, agent=None):
        """One radio hop between `agent` and its serving gNB.

        constant: fixed delay and loss. sionna: the loss and the HARQ delay depend on the
        UE-gNB distance (table built with Sionna); cloud agents have no radio hop."""
        topo = self.cfg["topology"]
        if self.radio_lut is None or agent is None:
            yield self.env.timeout(topo["delay_ms"]["radio"] / 1000.0)
            if self.rng_net.random() < topo["loss"]["radio"]:
                return "link"
            return None
        u = int(self.attached[agent])
        if u not in self.cell_of:
            return None
        distance = float(np.hypot(*(self.agent_xy[agent] - self.cell_xy[self.cell_of[u]])))
        attempts, dropped = self.radio_lut.sample(distance, self.rng_net.random())
        yield self.env.timeout(topo["delay_ms"]["radio"] / 1000.0 + (attempts - 1) * self.radio_lut.harq_rtt_s)
        return "link" if dropped else None

    def count_query(self, msgs=1, size=None):
        self.query_msgs += msgs
        self.query_bytes += msgs * (self.query_size if size is None else size)

    def count_ctrl(self, msgs, n_bytes):
        self.ctrl_msgs += msgs
        self.ctrl_bytes += n_bytes

    def traverse(self, pkt, path, log_hops=True, size=None):
        """Send a packet along a router path (used by the baselines).

        Returns (drop reason or None, router where it stopped)."""
        if not path:
            return "no_route", None     # failures partitioned the network
        for u, v in zip(path, path[1:]):
            reason = yield from self.transit(u)
            if reason:
                return reason, u
            self.count_query(1, size)
            pkt.hops += 1
            if log_hops:
                self.log.log(t=self.env.now, type="hop", pkt=pkt.pid, method=self.method,
                             **{"from": int(u), "to": int(v)})
            reason = yield from self.link(u, v)
            if reason:
                return reason, v
        reason = yield from self.transit(path[-1])
        return reason, path[-1]

    def hop_distance(self, a):
        """Hop count from router a to every router of the live graph (cached)."""
        if a not in self._dist:
            self._dist[a] = nx.single_source_shortest_path_length(self.live, a)
        return self._dist[a]

    def path(self, a, b):
        if a not in self._paths:
            self._paths[a] = nx.single_source_dijkstra_path(self.live, a, weight="delay")
        return self._paths[a].get(b)

    def _compute_upstream(self):
        self.upstream = {}
        for u in self.G.nodes:
            ups = [n for n in self.G.adj[u] if self.kind[n] != "gnb" and n not in self.known_dead]
            if self.kind[u] == "gnb" and ups:
                self.upstream[u] = min(ups, key=lambda n: (self.G.edges[u, n]["delay"], n))
            else:
                self.upstream[u] = None

    def view(self, u, pkt):
        now = self.env.now
        nbrs = [n for n in self.G.adj[u] if n not in self.known_dead]
        ids = [a for a in self.at_router[u] if a != pkt.src_agent]
        vecs = self.agent_vec[ids] if ids else np.zeros((0, self.card_vecs.shape[1]), np.float32)
        return NodeView(
            node=u, neighbors=nbrs, sfib=self.adv.tables[u] if self.adv else None,
            local_agents=ids, local_vecs=vecs,
            queue_occ={n: self.routers[n].occ for n in nbrs},
            link_quality={n: 1.0 - self.G.edges[u, n]["loss"] for n in nbrs},
            link_delay={n: self.G.edges[u, n]["delay"] for n in nbrs},
            in_handover={n: 1.0 if now - self.routers[n].last_handover < self.ho_window else 0.0
                         for n in nbrs},
            kind=self.kind, upstream=self.upstream.get(u), tau=self.tau, radius=self.radius,
            now=now, accept_mode=self.accept_mode, omega=self.omega)

    # ------------------------------------------------------------------
    # results
    def finish(self, pkt, success, reason, at=None, agent=None, time=None):
        now = self.env.now
        elapsed = now - pkt.created if time is None else time
        self.results.append({"pid": pkt.pid, "success": success, "reason": reason,
                             "time": elapsed, "hops": pkt.hops, "cls": pkt.intent_class,
                             "oracle_best": pkt.oracle_best, "oracle_any": pkt.oracle_any})
        if success:
            self.log.log(t=now, type="deliver", pkt=pkt.pid, agent=int(agent), hops=pkt.hops,
                         method=self.method)
        else:
            self.log.log(t=now, type="drop", pkt=pkt.pid, at=None if at is None else int(at),
                         reason=reason, method=self.method)

    def deliver_to(self, pkt, u, agent):
        """Last radio hop from router u to the chosen agent. Returns a drop reason or None."""
        reason = yield from self.radio(agent)
        if reason:
            return reason
        if self.attached[agent] != u:
            return "handover"
        if self.agent_class[agent] != pkt.intent_class:
            return "wrong_agent"
        return None

    # ------------------------------------------------------------------
    # semantic forwarding (AgentRoute and greedy)
    def semantic_query(self, pkt, start):
        reason = yield from self.radio(pkt.src_agent)
        if reason:
            return self.finish(pkt, False, reason, at=start)
        u = start
        while True:
            reason = yield from self.transit(u)
            if reason:
                self.policy.observe(pkt, self.env.now, None, "drop")
                return self.finish(pkt, False, reason, at=u)
            view = self.view(u, pkt)
            if pkt.ttl <= 0 and best_local_agent(view, pkt) is None:
                self.policy.observe(pkt, self.env.now, None, "drop")
                return self.finish(pkt, False, "ttl", at=u)
            if pkt.pending is not None:
                self.policy.observe(pkt, self.env.now, view, None)
            agent = self.policy.accept(view, pkt)
            if agent is not None:
                reason = yield from self.deliver_to(pkt, u, agent)
                self.policy.observe(pkt, self.env.now, None, "drop" if reason else "deliver")
                if reason:
                    return self.finish(pkt, False, reason, at=u)
                return self.finish(pkt, True, None, agent=agent)
            nxt = self.policy.choose(view, pkt)
            if nxt is None:
                self.policy.observe(pkt, self.env.now, None, "drop")
                return self.finish(pkt, False, "no_route", at=u)
            pkt.ttl -= 1
            pkt.prev_hop = u
            pkt.visited.append(u)
            pkt.hops += 1
            self.count_query()
            self.log.log(t=self.env.now, type="hop", pkt=pkt.pid, method=self.method,
                         **{"from": int(u), "to": int(nxt)})
            reason = yield from self.link(u, nxt)
            if reason:
                self.policy.observe(pkt, self.env.now, None, "drop")
                return self.finish(pkt, False, reason, at=nxt)
            u = nxt

    def propagate(self, v, agent, delta):
        """Withdraw (delta=-1) or announce (+1) one agent at router v, hop by hop."""
        if v not in self.adv.alive:
            return
        vec = self.agent_vec[agent]
        if delta > 0:
            self.adv.local[v][agent] = vec
        else:
            self.adv.local[v].pop(agent, None)
        kind = "adv" if delta > 0 else "withdraw"
        frontier, seen = [v], {v}
        for d in range(1, self.radius + 1):
            yield self.env.timeout(ADV_HOP_DELAY)
            changed, frontier = self.adv.spread(v, frontier, seen, agent, vec, delta, d)
            self.count_ctrl(len(changed), len(changed) * self.adv.delta_bytes())
            self.update_msgs += len(changed)
            self.update_bytes += len(changed) * self.adv.delta_bytes()
            if self.log.enabled:
                for n, u in changed:
                    nv = self.adv.tables[u].n_vectors(n) if kind == "adv" else 0
                    self.log.log(t=self.env.now, type=kind, agent=int(agent), n_vectors=nv,
                                 **{"from": int(n), "to": int(u)})
            if not changed and self.adv.summary != "exact":
                break

    # ------------------------------------------------------------------
    # processes
    def query_source(self):
        rate = self.cfg["sim"]["query_rate"] * self.load
        yield self.env.timeout(self.warmup)
        pid = 0
        while True:
            yield self.env.timeout(self.rng_traffic.exponential(1.0 / rate))
            if self.env.now >= self.duration:
                return
            a = int(self.rng_traffic.choice(self.requesters))
            k = int(self.rng_traffic.integers(len(self.intent_class)))
            if self.attached[a] < 0:
                continue        # requester is in the middle of a handover
            start = int(self.attached[a])
            pkt = Packet(pid=pid, intent=quantize(self.intent_vecs[k], self.header),
                         intent_class=int(self.intent_class[k]), ttl=self.ttl, ttl_max=self.ttl,
                         src_agent=a, created=self.env.now, method=self.method,
                         text=self.intent_text[k])
            self._set_oracle(pkt, a)
            self.log.log(t=self.env.now, type="query", pkt=pid, agent=a, router=start,
                         cls=pkt.intent_class, text=pkt.text, method=self.method)
            pid += 1
            if self.semantic:
                self.env.process(self.semantic_query(pkt, start))
            elif self.method == "flooding":
                self.env.process(self.flood.query(pkt, start))
            elif self.method in ("registry", "registry3"):
                self.env.process(self.registry.query(pkt, start))
            else:
                self.env.process(self.chord.query(pkt, start))

    def _set_oracle(self, pkt, src):
        """What a method with perfect knowledge of all attached agents could achieve."""
        on = self.attached >= 0
        on[src] = False
        if not on.any():
            return
        sims = self.agent_vec @ pkt.intent
        sims[~on] = -2.0
        best = int(np.argmax(sims))
        right = self.agent_class == pkt.intent_class
        pkt.oracle_best = bool(sims[best] >= self.tau and right[best])
        pkt.oracle_any = bool(((sims >= self.tau) & right).any())

    def mobility(self):
        ag = self.cfg["agents"]
        dt = ag["mobility_dt_s"]
        mob = self.mobile_idx
        if len(mob) == 0:
            return
        while True:
            yield self.env.timeout(dt)
            self.rwp.step(dt)
            self.agent_xy[mob] = self.rwp.pos
            if self.log.enabled:
                for a in mob:
                    self.log.log(t=self.env.now, type="move", agent=int(a),
                                 x=round(float(self.agent_xy[a, 0]), 1),
                                 y=round(float(self.agent_xy[a, 1]), 1))
            alive = np.array([self.routers[u].alive for u in self.gnbs])
            cur = self.attached[mob]
            cur_cell = np.where(cur >= 0, cur, 0)
            target = handover_targets(self.rwp.pos, cur_cell, self.cell_xy, alive, ag["hysteresis"])
            nearest = nearest_cell(self.rwp.pos, self.cell_xy, alive)
            for k in np.nonzero((target != cur) | (cur < 0))[0]:
                a = mob[k]
                if self.ho_pending[a]:
                    continue
                self.ho_pending[a] = True
                if cur[k] < 0:
                    self.env.process(self.handover(a, None, self.gnbs[nearest[k]]))
                else:
                    self.env.process(self.handover(a, int(cur[k]), self.gnbs[target[k]]))

    def handover(self, a, old, new):
        now = self.env.now
        if old is not None:
            self._detach(a)
            self.routers[old].last_handover = now
            self.handovers += 1
            self.log.log(t=now, type="handover", agent=int(a), from_cell=int(old), to_cell=int(new))
            if self.semantic:
                self.env.process(self.propagate(old, a, -1))
            elif self.method in ("chord", "sdht"):
                self.chord.on_move(a)
        self.routers[new].last_handover = now
        yield self.env.timeout(self.cfg["agents"]["handover_interrupt_s"])
        self.ho_pending[a] = False
        if not self.routers[new].alive:
            return              # the target died meanwhile; mobility will try again
        self._attach(a, new)
        if self.semantic:
            self.env.process(self.propagate(new, a, +1))
        elif self.method in ("registry", "registry3"):
            self.env.process(self.registry.update(a))
        elif self.method in ("chord", "sdht"):
            self.chord.on_move(a)

    def hello(self):
        """Neighbours learn each other's queue occupancy every hello period."""
        hello_s = self.cfg["routers"]["hello_s"]
        while True:
            for r in self.routers.values():
                rho = self.rho(r)
                bg = min(1.0, rho / (1.0 - rho) / self.bg_limit)
                r.occ = max(len(r.res.queue) / self.queue_limit, bg)
            yield self.env.timeout(hello_s)

    def hotspot(self, u):
        r = self.routers[u]
        r.busy = bool(self.rng_topo.random() < 0.5)
        mean = self.cfg["routers"]["busy_mean_s"]
        while True:
            self.log.log(t=self.env.now, type="load", node=int(u), busy=r.busy)
            yield self.env.timeout(self.rng_topo.exponential(mean))
            r.busy = not r.busy

    def refresh(self):
        """Periodic soft-state refresh of the control plane."""
        period = self.cfg["sfib"]["refresh_s"]
        first = True
        while True:
            if self.semantic:
                if first or not self.incremental:
                    msgs, n_bytes = self.adv.build()    # recompute every summary (soft state)
                else:
                    msgs, n_bytes = self.adv.refresh_incremental()
                n_reg = int((self.attached >= 0).sum())
                self.count_ctrl(msgs + n_reg, n_bytes + n_reg * SMALL_MSG)
                if first and self.log.enabled:
                    for u in self.adv.alive:
                        t = self.adv.tables[u]
                        for n in t.neighbors:
                            nv = t.n_vectors(n)
                            if nv:
                                self.log.log(t=0.0, type="adv", n_vectors=nv,
                                             **{"from": int(n), "to": int(u)})
            elif self.method in ("registry", "registry3"):
                self.env.process(self.registry.refresh(period, initial=first))
            elif self.method in ("chord", "sdht"):
                self.chord.refresh()
            first = False
            yield self.env.timeout(period)

    def failures(self):
        frac = self.cfg["sim"]["failure_fraction"]
        if frac <= 0:
            return
        yield self.env.timeout(self.cfg["sim"]["failure_time_frac"] * self.duration)
        pool = self.gnbs + self.cores
        k = int(round(frac * len(pool)))
        failed = [int(u) for u in self.rng_fail.choice(pool, size=k, replace=False)]
        for u in failed:
            self.routers[u].alive = False
            self.log.log(t=self.env.now, type="fail", node=u)
            for a in list(self.at_router[u]):
                if self.agent_kind[a] == "edge":
                    self._detach(a)
                    self.down[a] = True
        yield self.env.timeout(self.cfg["sfib"]["failure_detect_s"])
        self.known_dead |= set(failed)
        self.live = self.G.subgraph([u for u in self.G.nodes if u not in self.known_dead]).copy()
        self._paths = {}
        self._compute_upstream()
        self._dist = {}
        if self.semantic:
            fail = self.adv.fail_incremental if self.incremental else self.adv.fail
            self.count_ctrl(*fail(failed))
        elif self.method in ("chord", "sdht"):
            self.chord.rebuild()

    def control_window(self):
        """Mark the control bytes of the steady part of the run.

        The window opens after the first full period and closes at the end of
        the traffic, so it holds whole refresh rounds and no start-up.
        """
        period = self.cfg["sfib"]["refresh_s"]
        yield self.env.timeout(1e-3)
        self.boot_bytes = self.ctrl_bytes
        if self.duration <= period:
            return
        yield self.env.timeout(period)
        self._steady_start = (self.ctrl_bytes, self.update_bytes)
        yield self.env.timeout(self.duration - period)
        self._steady_end = (self.ctrl_bytes, self.update_bytes)

    # ------------------------------------------------------------------
    def run(self):
        self.env.process(self.control_window())
        self.env.process(self.query_source())
        self.env.process(self.mobility())
        self.env.process(self.hello())
        self.env.process(self.refresh())
        self.env.process(self.failures())
        for u in self.hotspots:
            self.env.process(self.hotspot(u))
        self.env.run(until=self.duration + 3.0)
        summary = self.summary()
        self.log.close(summary)
        return summary

    def summary(self):
        res = self.results
        n = len(res)
        ok = [r for r in res if r["success"]]
        reasons = Counter(r["reason"] for r in res if not r["success"])
        times = np.array([r["time"] for r in ok]) * 1000.0
        out = {
            "method": self.method,
            "seed": self.seed,
            "n_agents": self.n_agents,
            "n_routers": self.G.number_of_nodes(),
            "n_queries": n,
            "success_rate": len(ok) / n if n else 0.0,
            "time_ms": float(times.mean()) if len(ok) else float("nan"),
            "time_ms_p95": float(np.percentile(times, 95)) if len(ok) else float("nan"),
            "hops": float(np.mean([r["hops"] for r in ok])) if ok else float("nan"),
            "ctrl_msgs": self.ctrl_msgs,
            "query_msgs": self.query_msgs,
            "msgs_per_query": (self.ctrl_msgs + self.query_msgs) / max(n, 1),
            "ctrl_msgs_per_s": self.ctrl_msgs / self.duration,
            "ctrl_kB_per_s": self.ctrl_bytes / self.duration / 1000.0,
            "boot_kB": self.boot_bytes / 1000.0,
            "query_msgs_per_query": self.query_msgs / max(n, 1),
            "query_kB_per_query": self.query_bytes / max(n, 1) / 1000.0,
            "oracle_best": float(np.mean([r["oracle_best"] for r in res])) if n else 0.0,
            "oracle_any": float(np.mean([r["oracle_any"] for r in res])) if n else 0.0,
            "success_solvable": float(np.mean([r["success"] for r in res if r["oracle_best"]]))
            if any(r["oracle_best"] for r in res) else float("nan"),
            "precision": len(ok) / max(len(ok) + reasons.get("wrong_agent", 0), 1),
            "handovers": self.handovers,
            "update_msgs": self.update_msgs,
        }
        if self._steady_end is not None:
            span = self.duration - self.cfg["sfib"]["refresh_s"]
            ctrl = self._steady_end[0] - self._steady_start[0]
            update = self._steady_end[1] - self._steady_start[1]
            out["ctrl_kB_per_s_steady"] = ctrl / span / 1000.0
            out["update_kB_per_s_steady"] = update / span / 1000.0
            out["refresh_kB_per_s_steady"] = (ctrl - update) / span / 1000.0
        if self.method in ("registry", "registry3"):
            out["servers_alive"] = sum(self.routers[u].alive for u in self.registry.nodes)
        for reason in ["ttl", "queue", "link", "node_down", "no_route", "wrong_agent", "handover",
                       "not_found", "stale_location", "registry_queue"]:
            out[f"drop_{reason}"] = reasons.get(reason, 0) / n if n else 0.0
        return out

    def snapshot(self):
        names = class_names()
        return {
            "meta": {"method": self.method, "seed": self.seed, "n_agents": self.n_agents,
                     "radius": self.radius, "tau": self.tau, "duration": self.duration,
                     "classes": names},
            "nodes": [{"id": int(u), "kind": self.kind[u], "x": self.G.nodes[u]["x"],
                       "y": self.G.nodes[u]["y"], "hotspot": u in self.hotspots}
                      for u in self.G.nodes],
            "links": [{"u": int(u), "v": int(v), "kind": d["kind"],
                       "delay_ms": d["delay"] * 1000.0, "loss": d["loss"]}
                      for u, v, d in self.G.edges(data=True)],
            "agents": [{"id": a, "kind": str(self.agent_kind[a]), "cls": int(self.agent_class[a]),
                        "class_name": names[self.agent_class[a]],
                        "card": self.card_text[self.agent_card[a]],
                        "x": round(float(self.agent_xy[a, 0]), 1),
                        "y": round(float(self.agent_xy[a, 1]), 1),
                        "router": int(self.attached[a])}
                       for a in range(self.n_agents)],
        }
