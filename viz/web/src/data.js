// Loading and indexing of simulation logs (topology.json + events.jsonl).
// The player never talks to the simulator; it only reads these files.

export const METHOD_LABEL = {
  agentroute: "AgentRoute (DQN)",
  agentroute_gnn: "AgentRoute (GNN)",
  greedy: "Greedy semantic",
  greedy_load: "Load-aware greedy",
  spfr: "SPFR-style",
  flooding: "Flooding",
  registry: "Central registry",
  registry3: "Registry (3 replicas)",
  chord: "Chord (exact)",
  sdht: "Semantic DHT",
};

export const REASON_LABEL = {
  wrong_agent: "Wrong agent accepted",
  not_found: "No match found",
  ttl: "TTL expired",
  queue: "Queue overflow",
  link: "Link loss",
  node_down: "Node down",
  handover: "Agent in handover",
  stale_location: "Stale location",
  registry_queue: "Registry overloaded",
  no_route: "No route",
};

export async function loadIndex() {
  try {
    const r = await fetch("data/index.json");
    if (!r.ok) return { runs: [] };
    return await r.json();
  } catch {
    return { runs: [] };
  }
}

export async function loadRun(name) {
  const base = `data/${name}`;
  const [topo, text, summary] = await Promise.all([
    fetch(`${base}/topology.json`).then((r) => r.json()),
    fetch(`${base}/events.jsonl`).then((r) => r.text()),
    fetch(`${base}/summary.json`)
      .then((r) => (r.ok ? r.json() : null))
      .catch(() => null),
  ]);
  return buildRun(topo, parseJsonl(text), summary, name);
}

export function parseJsonl(text) {
  return text
    .split("\n")
    .filter((line) => line.trim())
    .map((line) => JSON.parse(line));
}

// Turns the flat event list into lookup tables used by the views.
export function buildRun(topo, events, summary, name) {
  const pos = new Map(topo.nodes.map((n) => [n.id, [n.x, n.y]]));
  const kind = new Map(topo.nodes.map((n) => [n.id, n.kind]));
  const agents = new Map(topo.agents.map((a) => [a.id, a]));
  const queries = new Map();
  const hops = new Map();
  const outcome = new Map();
  const moves = new Map();
  const load = new Map();
  const handovers = [];
  const adverts = [];
  events.sort((a, b) => a.t - b.t);
  for (const e of events) {
    switch (e.type) {
      case "query":
        queries.set(e.pkt, e);
        break;
      case "hop":
        if (!hops.has(e.pkt)) hops.set(e.pkt, []);
        hops.get(e.pkt).push(e);
        break;
      case "deliver":
      case "drop":
        outcome.set(e.pkt, e);
        break;
      case "move":
        if (!moves.has(e.agent)) moves.set(e.agent, []);
        moves.get(e.agent).push([e.t, e.x, e.y]);
        break;
      case "load":
        if (!load.has(e.node)) load.set(e.node, []);
        load.get(e.node).push([e.t, e.busy]);
        break;
      case "handover":
        handovers.push(e);
        break;
      case "adv":
      case "withdraw":
        adverts.push(e);
        break;
      default:
        break;
    }
  }
  const run = { name, topo, events, pos, kind, agents, queries, hops, outcome, moves, load,
    handovers, adverts, method: topo.meta.method, duration: topo.meta.duration + 3 };
  run.packets = buildPackets(run);
  run.summary = summary || summarise(run);
  return run;
}

// Every packet becomes a list of timed segments (uplink, hops, delivery).
function buildPackets(run) {
  const packets = [];
  for (const [pid, q] of run.queries) {
    const out = run.outcome.get(pid);
    if (!out) continue;
    const hs = run.hops.get(pid) || [];
    const segs = [];
    const start = agentPos(run, q.agent, q.t);
    const firstT = hs.length ? hs[0].t : out.t;
    segs.push({ t0: q.t, t1: firstT, a: start, b: run.pos.get(q.router), label: "uplink" });
    hs.forEach((h, i) => {
      const t1 = i + 1 < hs.length ? hs[i + 1].t : out.t;
      segs.push({ t0: h.t, t1, a: run.pos.get(h.from), b: run.pos.get(h.to),
        label: `${h.from} → ${h.to}`, from: h.from, to: h.to });
    });
    if (out.type === "deliver") {
      const last = hs.length ? run.pos.get(hs[hs.length - 1].to) : run.pos.get(q.router);
      const dst = agentPos(run, out.agent, out.t);
      const tEnd = segs[segs.length - 1].t1;
      segs.push({ t0: tEnd, t1: Math.max(out.t, tEnd + 1e-4), a: last, b: dst, label: "to agent" });
    }
    packets.push({ pid, q, out, segs, t0: q.t, t1: out.t, ok: out.type === "deliver" });
  }
  return packets;
}

function summarise(run) {
  const all = [...run.outcome.values()];
  const ok = all.filter((o) => o.type === "deliver");
  const s = { method: run.method, n_queries: all.length,
    success_rate: all.length ? ok.length / all.length : 0 };
  for (const o of all) {
    if (o.type === "drop") s[`drop_${o.reason}`] = (s[`drop_${o.reason}`] || 0) + 1 / all.length;
  }
  return s;
}

function bisect(arr, t) {
  let lo = 0;
  let hi = arr.length;
  while (lo < hi) {
    const mid = (lo + hi) >> 1;
    if (arr[mid][0] <= t) lo = mid + 1;
    else hi = mid;
  }
  return lo;
}

export function agentPos(run, id, t) {
  const tr = run.moves.get(id);
  const a = run.agents.get(id);
  if (!tr || !tr.length) return [a.x, a.y];
  const i = bisect(tr, t);
  if (i === 0) return [tr[0][1], tr[0][2]];
  if (i >= tr.length) return [tr[tr.length - 1][1], tr[tr.length - 1][2]];
  const [t0, x0, y0] = tr[i - 1];
  const [t1, x1, y1] = tr[i];
  const f = (t - t0) / Math.max(t1 - t0, 1e-9);
  return [x0 + f * (x1 - x0), y0 + f * (y1 - y0)];
}

export function busyAt(run, node, t) {
  const tr = run.load.get(node);
  if (!tr) return false;
  const i = bisect(tr, t);
  return i > 0 ? tr[i - 1][1] : false;
}

export function packetPos(p, t) {
  for (const s of p.segs) {
    if (t >= s.t0 && t <= s.t1) {
      const f = (t - s.t0) / Math.max(s.t1 - s.t0, 1e-9);
      return [s.a[0] + f * (s.b[0] - s.a[0]), s.a[1] + f * (s.b[1] - s.a[1])];
    }
  }
  return null;
}

// index of the first event with time > t (events are sorted)
export function eventIndexAt(events, t) {
  let lo = 0;
  let hi = events.length;
  while (lo < hi) {
    const mid = (lo + hi) >> 1;
    if (events[mid].t <= t) lo = mid + 1;
    else hi = mid;
  }
  return lo;
}
