// AgentRoute console. Talks to viz/console/server.py; no build step.

const LABEL = {
  agentroute: "AgentRoute (DQN)", agentroute_gnn: "AgentRoute (GNN)", greedy: "Greedy semantic",
  greedy_load: "Load-aware greedy", spfr: "SPFR-style", flooding: "Flooding",
  registry: "Central registry", registry3: "Registry, 3 replicas", chord: "Chord (exact)",
  sdht: "Semantic DHT",
};
const COLOR = {
  agentroute: "#2a78d6", agentroute_gnn: "#eb6834", greedy: "#1baf7a", greedy_load: "#0f8a8a",
  spfr: "#6250d6", flooding: "#eda100", registry: "#e87ba4", registry3: "#a8437a",
  chord: "#008300", sdht: "#7a6a5a",
};
const REASON = {
  ttl: "TTL expired", wrong_agent: "Wrong agent accepted", not_found: "No match found",
  queue: "Queue overflow", link: "Link loss", node_down: "Router down", handover: "Agent in handover",
  stale_location: "Stale location", registry_queue: "Registry overloaded", no_route: "No route",
};
const REASON_COLOR = {
  ttl: "#56627a", wrong_agent: "#c2372d", not_found: "#9aa6b8", queue: "#e39a2b", link: "#6c4bb4",
  node_down: "#2b2b2b", handover: "#1baf7a", stale_location: "#0f8a8a", registry_queue: "#e87ba4",
  no_route: "#b9a27a",
};
const DEFAULT_PICK = ["agentroute", "greedy", "flooding", "registry"];

const $ = (s) => document.querySelector(s);
const el = (tag, attrs = {}, ...kids) => {
  const n = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (k === "style") n.style.cssText = v;
    else if (k.startsWith("on")) n.addEventListener(k.slice(2), v);
    else if (v !== false && v != null) n.setAttribute(k, v === true ? "" : v);
  }
  for (const k of kids.flat()) if (k != null) n.append(k.nodeType ? k : String(k));
  return n;
};
const api = async (path, body) => {
  const r = await fetch(path, body === undefined ? {} : {
    method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
  const data = await r.json().catch(() => ({ error: `HTTP ${r.status}` }));
  if (!r.ok) throw new Error(data.error || `HTTP ${r.status}`);
  return data;
};
const pct = (x) => (x == null ? "–" : `${(x * 100).toFixed(1)}%`);
const fix = (x, d = 1) => (x == null || Number.isNaN(x) ? "–" : Number(x).toFixed(d));
const css = (name) => getComputedStyle(document.documentElement).getPropertyValue(name).trim();

const state = { meta: null, runsets: [], runset: null, method: null, run: null,
  t: 0, playing: true, speed: 0.05, selected: null, jobs: {} };

// ================================================================= routing
function showView() {
  const view = (location.hash || "#simulate").slice(1);
  const known = ["simulate", "ask", "pipeline", "figures"];
  const v = known.includes(view) ? view : "simulate";
  for (const k of known) $(`#view-${k}`).hidden = k !== v;
  document.querySelectorAll(".tabs a").forEach((a) => {
    if (a.dataset.view === v) a.setAttribute("aria-current", "page");
    else a.removeAttribute("aria-current");
  });
  if (v === "figures") loadFigures();
  if (v === "simulate") requestAnimationFrame(resizeMap);
}
window.addEventListener("hashchange", showView);

// ================================================================= simulate form
function initForm() {
  const form = $("#simForm");
  const outs = { n_agents: ["#o_agents", (v) => v], radius: ["#o_radius", (v) => v],
    speed: ["#o_speed", (v) => v], load: ["#o_load", (v) => v],
    failure: ["#o_failure", (v) => Math.round(v * 100)], duration: ["#o_duration", (v) => v] };
  const sync = () => {
    for (const [name, [sel, f]] of Object.entries(outs)) $(sel).textContent = f(form.elements[name].value);
  };
  form.addEventListener("input", sync);
  sync();

  const picks = $("#methodPicks");
  for (const m of state.meta.methods) {
    picks.append(el("label", { class: "pick", style: `--c:${COLOR[m.id]}`,
      title: m.available ? "" : "Train the DQN first (pipeline: Train the DQN and GNN policies)" },
    el("input", { type: "checkbox", name: "method", value: m.id,
      checked: m.available && DEFAULT_PICK.includes(m.id), disabled: !m.available }),
    el("span", {}, LABEL[m.id])));
  }

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const f = form.elements;
    const methods = [...form.querySelectorAll("input[name=method]:checked")].map((i) => i.value);
    if (!methods.length) { $("#simStatus").textContent = "Pick at least one method."; return; }
    const params = { methods, n_agents: +f.n_agents.value, radius: +f.radius.value,
      summary: f.summary.value, speed: +f.speed.value, load: +f.load.value, failure: +f.failure.value,
      duration: +f.duration.value, seed: +f.seed.value, log_events: f.log_events.checked };
    try {
      const job = await api("/api/simulate", params);
      $("#runBtn").disabled = true;
      $("#simStatus").textContent = `Simulating ${methods.length} method${methods.length > 1 ? "s" : ""} ...`;
      watchJob(job.id, async (j) => {
        $("#simStatus").textContent = j.log.at(-1) || "";
        if (j.state === "running") return;
        $("#runBtn").disabled = false;
        if (j.state === "done") {
          $("#simStatus").textContent = "Done. The new run is shown on the map.";
          await loadRunsets(j.result.id);
        } else {
          $("#simStatus").textContent = `The simulation failed: ${j.result?.error || "see the pipeline log"}`;
        }
      });
    } catch (err) {
      $("#simStatus").textContent = err.message;
    }
  });
}

// ================================================================= run sets and replay data
async function loadRunsets(selectId) {
  state.runsets = await api("/api/runsets");
  const sel = $("#runsetSel");
  sel.replaceChildren(...state.runsets.map((r) => el("option", { value: r.id }, r.label)));
  if (!state.runsets.length) {
    sel.append(el("option", {}, "No runs yet"));
    renderResults(null);
    $("#mapEmpty").hidden = false;
    return;
  }
  // newest own run first; the demo scenario only when nothing else exists
  const id = selectId || (state.runsets.find((r) => r.id !== "demo") || state.runsets[0]).id;
  sel.value = id;
  await pickRunset(id);
}

async function pickRunset(id) {
  state.runset = state.runsets.find((r) => r.id === id);
  renderResults(state.runset);
  const tabs = $("#replayTabs");
  const methods = state.runset.replay || [];
  tabs.replaceChildren(...methods.map((m) => el("button", { role: "tab", style: `--c:${COLOR[m]}`,
    "aria-selected": "false", "data-m": m, onclick: () => pickMethod(m) }, LABEL[m] || m)));
  if (!methods.length) {
    state.run = null;
    state.selected = null;
    $("#mapEmpty").hidden = false;
    $("#clock").textContent = "";
    renderFeed();
    renderDetail();
    draw();
    return;
  }
  const keep = methods.includes(state.method) ? state.method : methods.includes("agentroute") ? "agentroute" : methods[0];
  await pickMethod(keep);
}

async function pickMethod(m) {
  state.method = m;
  document.querySelectorAll("#replayTabs button").forEach((b) =>
    b.setAttribute("aria-selected", String(b.dataset.m === m)));
  const base = `/api/run/${state.runset.id}/${m}`;
  try {
    const [topo, text] = await Promise.all([
      fetch(`${base}/topology.json`).then((r) => r.json()),
      fetch(`${base}/events.jsonl`).then((r) => r.text()),
    ]);
    const events = text.split("\n").filter((l) => l.trim()).map((l) => JSON.parse(l));
    const keepT = state.run ? state.t : null;
    state.run = buildRun(topo, events);
    state.selected = null;
    state.t = keepT != null && keepT < state.run.duration ? keepT : state.run.firstQuery;
    $("#mapEmpty").hidden = true;
    fitMap();
    renderDetail();
  } catch (err) {
    state.run = null;
    $("#mapEmpty").hidden = false;
  }
}

function buildRun(topo, events) {
  const pos = new Map(topo.nodes.map((n) => [n.id, [n.x, n.y]]));
  const agents = new Map(topo.agents.map((a) => [a.id, a]));
  const queries = new Map(); const hops = new Map(); const outcome = new Map();
  const moves = new Map(); const load = new Map(); const handovers = [];
  events.sort((a, b) => a.t - b.t);
  for (const e of events) {
    if (e.type === "query") queries.set(e.pkt, e);
    else if (e.type === "hop") { if (!hops.has(e.pkt)) hops.set(e.pkt, []); hops.get(e.pkt).push(e); }
    else if (e.type === "deliver" || e.type === "drop") outcome.set(e.pkt, e);
    else if (e.type === "move") { if (!moves.has(e.agent)) moves.set(e.agent, []); moves.get(e.agent).push([e.t, e.x, e.y]); }
    else if (e.type === "load") { if (!load.has(e.node)) load.set(e.node, []); load.get(e.node).push([e.t, e.busy]); }
    else if (e.type === "handover") handovers.push(e);
  }
  const run = { topo, pos, agents, queries, hops, outcome, moves, load, handovers,
    classes: topo.meta.classes || [], duration: (topo.meta.duration || 30) + 2 };
  run.packets = [];
  for (const [pid, q] of queries) {
    const out = outcome.get(pid);
    if (!out) continue;
    const hs = hops.get(pid) || [];
    const segs = [];
    const firstT = hs.length ? hs[0].t : out.t;
    segs.push({ t0: q.t, t1: firstT, a: agentPos(run, q.agent, q.t), b: pos.get(q.router) });
    hs.forEach((h, i) => {
      const t1 = i + 1 < hs.length ? hs[i + 1].t : out.t;
      segs.push({ t0: h.t, t1, a: pos.get(h.from), b: pos.get(h.to) });
    });
    if (out.type === "deliver") {
      const last = hs.length ? pos.get(hs.at(-1).to) : pos.get(q.router);
      const tEnd = segs.at(-1).t1;
      segs.push({ t0: tEnd, t1: Math.max(out.t, tEnd + 1e-4), a: last, b: agentPos(run, out.agent, out.t) });
    }
    run.packets.push({ pid, q, out, hs, segs, t0: q.t, t1: Math.max(out.t, segs.at(-1).t1), ok: out.type === "deliver" });
  }
  run.packets.sort((a, b) => a.t0 - b.t0);
  run.firstQuery = run.packets.length ? Math.max(0, run.packets[0].t0 - 0.05) : 0;
  return run;
}

function bisect(arr, t) {
  let lo = 0; let hi = arr.length;
  while (lo < hi) { const mid = (lo + hi) >> 1; if (arr[mid][0] <= t) lo = mid + 1; else hi = mid; }
  return lo;
}
function agentPos(run, id, t) {
  const tr = run.moves.get(id); const a = run.agents.get(id);
  if (!tr || !tr.length) return [a.x, a.y];
  const i = bisect(tr, t);
  if (i === 0) return [tr[0][1], tr[0][2]];
  if (i >= tr.length) return [tr.at(-1)[1], tr.at(-1)[2]];
  const [t0, x0, y0] = tr[i - 1]; const [t1, x1, y1] = tr[i];
  const f = (t - t0) / Math.max(t1 - t0, 1e-9);
  return [x0 + f * (x1 - x0), y0 + f * (y1 - y0)];
}
function busyAt(run, node, t) {
  const tr = run.load.get(node);
  if (!tr) return false;
  const i = bisect(tr, t);
  return i > 0 ? tr[i - 1][1] : false;
}
function packetPos(p, t) {
  for (const s of p.segs) {
    if (t >= s.t0 && t <= s.t1) {
      const f = (t - s.t0) / Math.max(s.t1 - s.t0, 1e-9);
      return [s.a[0] + f * (s.b[0] - s.a[0]), s.a[1] + f * (s.b[1] - s.a[1])];
    }
  }
  return null;
}

// ================================================================= map drawing
const canvas = $("#map");
const ctx = canvas.getContext("2d");
const view = { w: 0, h: 0, k: 1, ox: 0, oy: 0, minX: 0, minY: 0 };

function resizeMap() {
  const r = canvas.getBoundingClientRect();
  if (!r.width) return;
  const dpr = window.devicePixelRatio || 1;
  canvas.width = Math.round(r.width * dpr);
  canvas.height = Math.round(r.height * dpr);
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  view.w = r.width; view.h = r.height;
  fitMap();
}
new ResizeObserver(resizeMap).observe(canvas);

function fitMap() {
  if (!state.run) return;
  const xs = state.run.topo.nodes.map((n) => n.x); const ys = state.run.topo.nodes.map((n) => n.y);
  const pad = 300;
  const minX = Math.min(...xs) - pad; const maxX = Math.max(...xs) + pad;
  const minY = Math.min(...ys) - pad; const maxY = Math.max(...ys) + pad;
  const k = Math.min(view.w / (maxX - minX), view.h / (maxY - minY));
  Object.assign(view, { k, minX, maxY, ox: (view.w - (maxX - minX) * k) / 2, oy: (view.h - (maxY - minY) * k) / 2 });
}
const sx = (x) => view.ox + (x - view.minX) * view.k;
const sy = (y) => view.oy + (view.maxY - y) * view.k; // y axis up

function draw() {
  const run = state.run;
  ctx.clearRect(0, 0, view.w, view.h);
  if (!run) return;
  const t = state.t;
  const ink = css("--ink"); const ink2 = css("--ink-2"); const rule = css("--rule");
  const signal = css("--signal"); const busy = css("--busy"); const sheet = css("--sheet");
  const good = css("--good"); const bad = css("--bad");
  const mc = COLOR[state.method] || signal;
  const nodes = run.topo.nodes;
  // marks shrink when many cells share the map (large runs)
  const z = Math.min(1, Math.max(0.35, view.k * 500 / 70));

  // coverage rings of the gNBs
  ctx.setLineDash([4, 5]);
  ctx.lineWidth = 1;
  ctx.strokeStyle = rule;
  for (const n of nodes) {
    if (n.kind !== "gnb") continue;
    ctx.beginPath(); ctx.arc(sx(n.x), sy(n.y), 280 * view.k, 0, Math.PI * 2); ctx.stroke();
  }
  ctx.setLineDash([]);

  // links
  for (const l of run.topo.links) {
    const [x1, y1] = run.pos.get(l.u); const [x2, y2] = run.pos.get(l.v);
    ctx.strokeStyle = l.kind === "core" || l.kind === "cloud" ? ink2 : rule;
    ctx.lineWidth = l.kind === "core" || l.kind === "cloud" ? 1.6 : 1;
    ctx.setLineDash(l.kind === "cloud" ? [6, 4] : l.loss > 0.01 ? [2, 3] : []);
    ctx.beginPath(); ctx.moveTo(sx(x1), sy(y1)); ctx.lineTo(sx(x2), sy(y2)); ctx.stroke();
  }
  ctx.setLineDash([]);

  // busy routers
  for (const n of nodes) {
    if (!busyAt(run, n.id, t)) continue;
    ctx.fillStyle = busy; ctx.globalAlpha = 0.35;
    ctx.beginPath(); ctx.arc(sx(n.x), sy(n.y), 20 * z, 0, Math.PI * 2); ctx.fill();
    ctx.globalAlpha = 1;
  }

  // paths of requests that finished in the last 0.25 s fade out
  for (const p of run.packets) {
    if (p.t0 > t) break;
    const age = t - p.t1;
    if (age < 0 || age > 0.25 || p.pid === state.selected) continue;
    ctx.globalAlpha = 0.5 * (1 - age / 0.25);
    ctx.strokeStyle = p.ok ? mc : bad; ctx.lineWidth = 2;
    ctx.beginPath();
    p.segs.forEach((s, i) => { if (i === 0) ctx.moveTo(sx(s.a[0]), sy(s.a[1])); ctx.lineTo(sx(s.b[0]), sy(s.b[1])); });
    ctx.stroke();
  }
  ctx.globalAlpha = 1;

  // selected request: full path
  const sel = state.selected != null ? run.packets.find((p) => p.pid === state.selected) : null;
  if (sel) {
    ctx.strokeStyle = mc; ctx.lineWidth = 4; ctx.lineCap = "round"; ctx.globalAlpha = 0.9;
    ctx.beginPath();
    sel.segs.forEach((s, i) => { if (i === 0) ctx.moveTo(sx(s.a[0]), sy(s.a[1])); ctx.lineTo(sx(s.b[0]), sy(s.b[1])); });
    ctx.stroke(); ctx.globalAlpha = 1; ctx.lineCap = "butt";
  }

  // routers
  for (const n of nodes) {
    const x = sx(n.x); const y = sy(n.y);
    ctx.fillStyle = ink; ctx.strokeStyle = ink; ctx.lineWidth = 2;
    if (n.kind === "gnb") {
      ctx.fillRect(x - 6 * z, y - 6 * z, 12 * z, 12 * z);
    } else if (n.kind === "core") {
      ctx.fillStyle = sheet; ctx.beginPath(); ctx.arc(x, y, Math.max(4, 8 * z), 0, Math.PI * 2); ctx.fill(); ctx.stroke();
    } else {
      ctx.fillStyle = sheet; ctx.beginPath();
      for (let i = 0; i < 6; i++) { const a = Math.PI / 3 * i + Math.PI / 6; ctx[i ? "lineTo" : "moveTo"](x + 13 * Math.cos(a), y + 13 * Math.sin(a)); }
      ctx.closePath(); ctx.fill(); ctx.stroke();
      ctx.fillStyle = ink2; ctx.font = "600 11px Archivo, sans-serif"; ctx.textAlign = "center";
      ctx.fillText("Cloud", x, y + 28);
    }
  }

  // agents
  ctx.fillStyle = ink2;
  for (const a of run.agents.values()) {
    const [x, y] = agentPos(run, a.id, t);
    ctx.globalAlpha = (a.kind === "mobile" ? 0.95 : 0.55) * (z < 0.6 ? 0.6 : 1);
    ctx.beginPath(); ctx.arc(sx(x), sy(y), (a.kind === "mobile" ? 2.8 : 2.2) * z, 0, Math.PI * 2); ctx.fill();
  }
  ctx.globalAlpha = 1;

  // handovers: red ring at the old cell, green ring at the new one
  for (const h of run.handovers) {
    const age = t - h.t;
    if (age < 0 || age > 0.8) continue;
    const r = (14 + age * 30) * z;
    ctx.globalAlpha = 1 - age / 0.8; ctx.lineWidth = 2;
    const [fx, fy] = run.pos.get(h.from_cell); const [tx, ty] = run.pos.get(h.to_cell);
    ctx.strokeStyle = bad; ctx.beginPath(); ctx.arc(sx(fx), sy(fy), r, 0, Math.PI * 2); ctx.stroke();
    ctx.strokeStyle = good; ctx.beginPath(); ctx.arc(sx(tx), sy(ty), r, 0, Math.PI * 2); ctx.stroke();
  }
  ctx.globalAlpha = 1;

  // packets in flight
  state.visible = [];
  for (const p of run.packets) {
    if (p.t0 > t) break;
    if (t > p.t1) continue;
    const xy = packetPos(p, t);
    if (!xy) continue;
    const X = sx(xy[0]); const Y = sy(xy[1]);
    state.visible.push([p.pid, X, Y]);
    ctx.fillStyle = mc; ctx.strokeStyle = sheet; ctx.lineWidth = 1.5;
    ctx.beginPath(); ctx.arc(X, Y, p.pid === state.selected ? 7 : 5, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
  }

  // requester and serving agent of the selected request
  if (sel) {
    const [qx, qy] = agentPos(run, sel.q.agent, t);
    ctx.strokeStyle = mc; ctx.lineWidth = 2.5;
    ctx.beginPath(); ctx.arc(sx(qx), sy(qy), 9, 0, Math.PI * 2); ctx.stroke();
    if (sel.ok) {
      const [ax, ay] = agentPos(run, sel.out.agent, t);
      ctx.strokeStyle = good; ctx.beginPath(); ctx.arc(sx(ax), sy(ay), 12, 0, Math.PI * 2); ctx.stroke();
    } else if (sel.out.at != null && run.pos.has(sel.out.at)) {
      const [dx, dy] = run.pos.get(sel.out.at);
      ctx.strokeStyle = bad; ctx.beginPath(); ctx.arc(sx(dx), sy(dy), 14, 0, Math.PI * 2); ctx.stroke();
    }
  }
}

canvas.addEventListener("click", (e) => {
  const r = canvas.getBoundingClientRect();
  const x = e.clientX - r.left; const y = e.clientY - r.top;
  let best = null; let bd = 14;
  for (const [pid, X, Y] of state.visible || []) {
    const d = Math.hypot(X - x, Y - y);
    if (d < bd) { bd = d; best = pid; }
  }
  if (best != null) selectPacket(best);
});

// ================================================================= playback
let last = performance.now();
let lastFeed = 0;
function frame(now) {
  const dt = Math.min(0.1, (now - last) / 1000);
  last = now;
  if (state.run && state.playing) {
    state.t += dt * state.speed;
    if (state.t > state.run.duration) state.t = state.run.firstQuery;
  }
  if (state.run && !$("#view-simulate").hidden) {
    draw();
    $("#clock").textContent = `${state.t.toFixed(3)} s`;
    $("#scrub").value = Math.round((state.t / state.run.duration) * 1000);
    if (now - lastFeed > 300) { renderFeed(); lastFeed = now; }
  }
  requestAnimationFrame(frame);
}

function setPlaying(on) {
  state.playing = on;
  $("#playBtn").setAttribute("aria-label", on ? "Pause" : "Play");
  $("#playIcon").setAttribute("d", on ? "M6 4h3v12H6zM11 4h3v12h-3z" : "M6 4l10 6-10 6z");
}

function initTransport() {
  $("#playBtn").addEventListener("click", () => setPlaying(!state.playing));
  $("#scrub").addEventListener("input", (e) => {
    if (!state.run) return;
    state.t = (e.target.value / 1000) * state.run.duration;
    renderFeed();
  });
  $("#speedSel").addEventListener("change", (e) => { state.speed = +e.target.value; });
  $("#runsetSel").addEventListener("change", (e) => pickRunset(e.target.value));
  if (matchMedia("(prefers-reduced-motion: reduce)").matches) setPlaying(false);
}

// ================================================================= request feed and detail
function renderFeed() {
  const ol = $("#feed");
  const run = state.run;
  if (!run) { ol.replaceChildren(); return; }
  const t = state.t;
  // the 12 requests that started closest before the current time
  let i = run.packets.findIndex((p) => p.t0 > t);
  if (i < 0) i = run.packets.length;
  const list = run.packets.slice(Math.max(0, i - 12), i).reverse();
  ol.replaceChildren(...list.map((p) => el("li", {}, el("button", {
    "aria-pressed": String(p.pid === state.selected), onclick: () => selectPacket(p.pid) },
  el("span", { class: "t" }, `${p.t0.toFixed(2)} s`),
  el("span", { class: "txt" }, p.q.text),
  el("span", { class: p.ok ? "ok" : "ko" }, p.ok ? "delivered" : "dropped")))));
}

function selectPacket(pid) {
  state.selected = pid;
  const p = state.run.packets.find((x) => x.pid === pid);
  if (p && (state.t < p.t0 || state.t > p.t1 + 0.3)) state.t = p.t0;
  renderDetail();
  renderFeed();
}

function renderDetail() {
  const box = $("#detail");
  const run = state.run;
  const p = run && state.selected != null ? run.packets.find((x) => x.pid === state.selected) : null;
  if (!p) {
    box.replaceChildren(el("p", { class: "hint" }, "Pick a request above, or click a packet on the map, to trace its path."));
    return;
  }
  const route = [p.q.router, ...p.hs.map((h) => h.to)];
  const nodeName = (id) => { const n = run.topo.nodes.find((x) => x.id === id); return n ? `${n.kind === "gnb" ? "gNB" : n.kind} ${id}` : id; };
  const served = p.ok ? run.agents.get(p.out.agent) : null;
  box.replaceChildren(
    el("p", { class: "quote" }, `“${p.q.text}”`),
    el("dl", {},
      el("dt", {}, "Asked for"), el("dd", {}, (run.classes[p.q.cls] || "").replaceAll("_", " ")),
      el("dt", {}, "From"), el("dd", {}, `agent ${p.q.agent}, cell ${p.q.router}`),
      el("dt", {}, "Outcome"), el("dd", { class: p.ok ? "ok" : "ko" }, p.ok
        ? `Delivered to agent ${p.out.agent} (${served ? served.class_name.replaceAll("_", " ") : "?"})`
        : `Dropped: ${REASON[p.out.reason] || p.out.reason}${p.out.at != null ? ` at router ${p.out.at}` : ""}`),
      el("dt", {}, "Time"), el("dd", {}, `${((p.out.t - p.q.t) * 1000).toFixed(1)} ms, ${p.hs.length} hops`),
      el("dt", {}, "Path"), el("dd", { class: "path" }, route.flatMap((r, i) => i ? [el("i", {}, "›"), el("b", {}, nodeName(r))] : [el("b", {}, nodeName(r))])),
    ),
  );
}

// ================================================================= results
function renderResults(rs) {
  const tb = $("#resTable tbody");
  const drops = $("#drops"); const leg = $("#dropLegend");
  if (!rs || !rs.summaries?.length) {
    tb.replaceChildren(el("tr", {}, el("td", { colspan: 7, class: "hint" }, "Run a scenario to see the numbers.")));
    drops.replaceChildren(); leg.replaceChildren();
    return;
  }
  const rows = [...rs.summaries].sort((a, b) => b.success_rate - a.success_rate);
  tb.replaceChildren(...rows.map((s) => el("tr", { style: `--c:${COLOR[s.method]}` },
    el("td", {}, el("span", { class: "mname" }, LABEL[s.method] || s.method)),
    el("td", {}, el("div", { class: "sbar" },
      el("div", { class: "track" },
        el("div", { class: "fill", style: `width:${s.success_rate * 100}%` }),
        s.oracle_best != null ? el("div", { class: "tick", style: `left:${s.oracle_best * 100}%`, title: `Oracle ceiling ${pct(s.oracle_best)}` }) : null),
      el("b", {}, pct(s.success_rate)))),
    el("td", { class: "num" }, pct(s.precision)),
    el("td", { class: "num" }, fix(s.time_ms)),
    el("td", { class: "num" }, fix(s.hops, 2)),
    el("td", { class: "num" }, fix(s.query_kB_per_query, 2)),
    el("td", { class: "num" }, fix(s.ctrl_kB_per_s, 1)))));

  const used = Object.keys(REASON).filter((r) => rows.some((s) => (s[`drop_${r}`] || 0) > 0.001));
  drops.replaceChildren(...rows.map((s) => el("div", { class: "drop-row" },
    el("span", { class: "mname", style: `--c:${COLOR[s.method]}` }, LABEL[s.method] || s.method),
    el("div", { class: "drop-bar", title: used.map((r) => `${REASON[r]}: ${pct(s[`drop_${r}`] || 0)}`).join("\n") },
      used.map((r) => el("span", { style: `width:${(s[`drop_${r}`] || 0) * 100}%;background:${REASON_COLOR[r]}` }))))));
  leg.replaceChildren(...used.map((r) => el("span", {}, el("i", { style: `background:${REASON_COLOR[r]}` }), REASON[r])));
}

// ================================================================= ask the network
async function initAsk() {
  $("#askForm").addEventListener("submit", (e) => { e.preventDefault(); ask(); });
  $("#askText").addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); ask(); }
  });
  try {
    const ex = await api("/api/examples");
    $("#examples").replaceChildren(...ex.slice(0, 10).map((x) => el("button", { type: "button",
      title: `Test intent of class ${x.name}`, onclick: () => { $("#askText").value = x.text; ask(); } }, x.text)));
  } catch { /* examples are optional */ }
}

async function ask() {
  const text = $("#askText").value.trim();
  if (!text) { $("#askStatus").textContent = "Type a task request first."; return; }
  $("#askBtn").disabled = true;
  $("#askStatus").textContent = "Encoding the request (the first one loads the encoder) ...";
  try {
    const r = await api("/api/classify", { text });
    $("#askStatus").textContent = "";
    const top = r.matches[0];
    const max = Math.max(0.8, top.score);
    const verdict = top.accept
      ? `An agent offering ${top.name.replaceAll("_", " ")} would accept this request (similarity ${top.score.toFixed(3)} ≥ τ = ${r.tau}).`
      : `No capability reaches τ = ${r.tau}. The closest is ${top.name.replaceAll("_", " ")} at ${top.score.toFixed(3)}, so every agent would refuse and the request would be dropped.`;
    $("#askOut").replaceChildren(
      el("p", { class: "verdict" }, verdict),
      ...r.matches.map((m, i) => el("div", { class: `match${m.accept ? " yes" : ""}${i === 0 ? " top" : ""}` },
        el("span", { class: "nm" }, m.name.replaceAll("_", " "), el("small", {}, m.card)),
        el("div", { class: "track" },
          el("div", { class: "fill", style: `width:${Math.max(0, m.score) / max * 100}%` }),
          el("div", { class: "tau", style: `left:${r.tau / max * 100}%`, title: `τ = ${r.tau}` })),
        el("b", {}, m.score.toFixed(3)),
        el("span", { class: m.accept ? "ok" : "hint" }, m.accept ? "accepts" : "refuses"))),
      el("p", { class: "header-note" }, `The intent header is ${r.header_bytes.float32} B as float32, ${r.header_bytes.int8} B as int8 (used in the simulator) and ${r.header_bytes.binary} B as a binary code. The dashed line marks τ.`),
    );
  } catch (err) {
    $("#askStatus").textContent = `Could not encode the request: ${err.message}`;
  }
  $("#askBtn").disabled = false;
}

// ================================================================= pipeline
let logJob = null;

function initPipeline() {
  const list = $("#stepList");
  const groups = {};
  let n = 0;
  for (const s of state.meta.steps) {
    if (!groups[s.group]) {
      groups[s.group] = el("div", { class: "group" }, el("h3", {}, s.group));
      list.append(groups[s.group]);
    }
    const everything = s.id === "all";
    if (!everything && s.id !== "tests") n += 1;
    groups[s.group].append(el("div", { class: `step${everything ? " everything" : ""}` },
      el("span", { class: "n" }, everything || s.id === "tests" ? "" : n),
      el("span", { class: "tt" }, s.title, s.note ? el("small", {}, s.note) : null),
      el("button", { class: "ghost", type: "button", onclick: () => runStep(s.id) }, "Run")));
  }
  $("#stopBtn").addEventListener("click", async () => {
    if (!logJob) return;
    try { await api(`/api/jobs/${logJob}/stop`, {}); } catch (err) { $("#logState").textContent = err.message; }
  });
}

async function runStep(id) {
  try {
    const job = await api("/api/step", { id, quick: $("#quickMode").checked });
    showLog(job.id, true);
  } catch (err) {
    $("#logState").className = "state failed";
    $("#logState").textContent = err.message;
  }
}

function showLog(id, fresh) {
  logJob = id;
  const pre = $("#log");
  pre.textContent = "";
  watchJob(id, (j) => {
    if (logJob !== id) return false;
    $("#logTitle").textContent = j.title;
    $("#logState").className = `state ${j.state}`;
    $("#logState").textContent = { running: "Running", done: "Finished", failed: "Failed", stopped: "Stopped" }[j.state];
    $("#stopBtn").hidden = !(j.state === "running" && j.kind === "step");
    if (j.log.length) {
      const atBottom = pre.scrollHeight - pre.scrollTop - pre.clientHeight < 40;
      pre.textContent += (pre.textContent ? "\n" : "") + j.log.join("\n");
      if (atBottom) pre.scrollTop = pre.scrollHeight;
    }
    if (j.state !== "running") { refreshJobs(); if (j.step === "train") refreshMeta(); }
  }, true);
}

async function refreshMeta() {
  state.meta = await api("/api/meta");
  for (const m of state.meta.methods) {
    const box = document.querySelector(`#methodPicks input[value=${m.id}]`);
    if (box) box.disabled = !m.available;
  }
}

// Polls a job; the callback gets only the new log lines since the last call.
const watchers = {};
function watchJob(id, cb, incremental = false) {
  const key = `${id}:${incremental}`;
  if (watchers[key]) return;
  let offset = 0;
  watchers[key] = true;
  const tick = async () => {
    try {
      const j = await api(`/api/jobs/${id}?offset=${incremental ? offset : 0}`);
      offset = j.offset;
      const keep = cb(j);
      if (j.state === "running" && keep !== false) { setTimeout(tick, 700); return; }
    } catch { /* server went away; stop polling */ }
    delete watchers[key];
  };
  tick();
}

async function refreshJobs() {
  const jobs = await api("/api/jobs").catch(() => []);
  const running = jobs.find((j) => j.state === "running");
  const pill = $("#jobPill");
  pill.hidden = !running;
  if (running) pill.textContent = running.title;
  const ul = $("#jobList");
  ul.replaceChildren(...jobs.slice().reverse().map((j) => el("li", {}, el("button", { onclick: () => showLog(j.id) },
    el("span", { class: `state ${j.state}` }, { running: "Running", done: "Finished", failed: "Failed", stopped: "Stopped" }[j.state]),
    el("span", {}, j.title),
    el("span", { class: "hint", style: "margin:0 0 0 auto" }, new Date(j.started * 1000).toLocaleTimeString())))));
  if (!jobs.length) ul.append(el("li", { class: "hint" }, "No jobs yet in this session."));
}

// ================================================================= figures
async function loadFigures() {
  const grid = $("#figGrid");
  const figs = await api("/api/figures").catch(() => []);
  if (!figs.length) {
    grid.replaceChildren(el("p", { class: "hint" }, "No figures yet. Run “Draw the figures” in the pipeline."));
    return;
  }
  const v = Math.round(Math.max(...figs.map((f) => f.mtime)));
  grid.replaceChildren(...figs.map((f) => {
    const cap = el("figcaption", {}, el("b", {}, f.stem.replaceAll("_", " ")), f.kind === "mp4" ? " (video)" : "");
    if (f.kind === "mp4") {
      return el("figure", { class: "fig" }, el("video", { src: `/figures/${f.name}?v=${v}`, controls: true, preload: "none",
        poster: f.poster ? `/figures/${f.poster}?v=${v}` : null, muted: true, playsinline: true }), cap);
    }
    return el("figure", { class: "fig" }, el("button", { type: "button", "aria-label": `Enlarge ${f.stem}`,
      onclick: () => { $("#figBig").src = `/figures/${f.name}?v=${v}`; $("#figBig").alt = f.stem; $("#figCap").textContent = f.stem.replaceAll("_", " "); $("#figDialog").showModal(); } },
    el("img", { src: `/figures/${f.name}?v=${v}`, alt: f.stem.replaceAll("_", " "), loading: "lazy" })), cap);
  }));
}

// ================================================================= start
async function start() {
  state.meta = await api("/api/meta");
  initForm();
  initTransport();
  initPipeline();
  initAsk();
  showView();
  await loadRunsets();
  refreshJobs();
  setInterval(refreshJobs, 4000);
  requestAnimationFrame(frame);
}
start().catch((err) => {
  document.body.prepend(el("p", { class: "hint", style: "padding:1rem" }, `The console could not reach the server: ${err.message}`));
});
