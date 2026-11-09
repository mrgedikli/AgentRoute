// Builds docs/slides/AgentRoute.pptx (English, ~15 minutes, three speakers).
//
//   cd docs/slides && npm install && npm run build
//
// Every number on the slides is read from results/summary.json, results/tau.json
// and the demo logs, and the verbs in result titles ("beats", "matches",
// "trails") are chosen from the data. Run the experiments and viz/plots.py first.
//
// Written with AI assistance (slide generation).
const fs = require("fs");
const path = require("path");
const pptxgen = require("pptxgenjs");

const ROOT = path.resolve(__dirname, "..", "..");
const OUT = path.join(__dirname, "AgentRoute.pptx");
const S = JSON.parse(fs.readFileSync(path.join(ROOT, "results", "summary.json"), "utf8"));
const TAU = JSON.parse(fs.readFileSync(path.join(ROOT, "results", "tau.json"), "utf8"));
const FIG = path.join(ROOT, "results", "figures");

// ---------------------------------------------------------------- style
const NAVY = "14213D";
const INK = "0B0B0B";
const INK2 = "52514E";
const MUTED = "6B6A66";
const PANEL = "F2F5F9";
const TINT = "E8F1FC";
const GRID = "E1E0D9";
const LIGHT = "CADCFC";
const WHITE = "FFFFFF";
const GOOD = "0A8A0A";
const CRIT = "D03B3B";
const M = {
  agentroute: { name: "AgentRoute (DQN)", color: "2A78D6" },
  agentroute_gnn: { name: "AgentRoute (GNN)", color: "EB6834" },
  greedy: { name: "Greedy semantic", color: "1BAF7A" },
  greedy_load: { name: "Load-aware greedy", color: "0F8A8A" },
  spfr: { name: "SPFR-style", color: "6250D6" },
  flooding: { name: "Flooding", color: "EDA100" },
  registry: { name: "Central registry", color: "E87BA4" },
  registry3: { name: "Registry (3 replicas)", color: "A8437A" },
  sdht: { name: "Semantic DHT", color: "7A6A5A" },
  chord: { name: "Chord (exact)", color: "008300" },
};
const ALL = Object.keys(M).filter((m) => m !== "agentroute_gnn");     // the GNN would only clutter the charts
const THEME = { name: "AgentRoute", colors: { dk1: INK, lt1: WHITE, dk2: NAVY, lt2: PANEL,
  accent1: "2A78D6", accent2: "EB6834", accent3: "1BAF7A", accent4: "EDA100", accent5: "E87BA4",
  accent6: "008300", hlink: "2A78D6", folHlink: "6250D6" } };

// ---------------------------------------------------------------- data helpers
function get(exp, method, metric, value) {
  const e = S[exp];
  if (!e || !e.methods[method]) return null;
  const i = value === undefined ? e.values.length - 1 : e.values.indexOf(value);
  return i < 0 ? null : e.methods[method][metric][i];
}
const pct = (x, d = 0) => (x == null ? "n/a" : `${(x * 100).toFixed(d)}%`);
const ms = (x) => (x == null ? "n/a" : `${x.toFixed(0)} ms`);
const num = (x) => (x == null ? "n/a" : Math.round(x).toLocaleString("en-US"));
function verb(a, b, tol = 0.01) {
  if (a == null || b == null) return "matches";
  if (a > b + tol) return "beats";
  if (a < b - tol) return "trails";
  return "matches";
}
function mean(xs) { const v = xs.filter((x) => x != null); return v.reduce((s, x) => s + x, 0) / v.length; }

// ---------------------------------------------------------------- deck + layouts
const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.33 x 7.5 in
pres.title = "AgentRoute";
pres.author = "Ömer Faruk Gedikli, Bekir Emre Sarıpınar, Bekir Göktepe";
pres.subject = "CSE 476/575 Mobile Communication Networks term project";
pres.theme = { headFontFace: "Cambria", bodyFontFace: "Calibri" };

pres.defineSlideMaster({
  title: "TITLE_DARK",
  background: { color: NAVY },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: 0.8, y: 1.9, w: 11.7, h: 1.3,
      fontFace: "Cambria", fontSize: 60, bold: true, color: WHITE, valign: "bottom", align: "left", margin: 0 }, text: "" } },
    { placeholder: { options: { name: "body", type: "body", x: 0.8, y: 3.35, w: 11.7, h: 1.0,
      fontSize: 24, color: LIGHT, valign: "top", align: "left", margin: 0 }, text: "" } },
    { placeholder: { options: { name: "team", type: "body", x: 0.8, y: 5.3, w: 11.7, h: 1.2,
      fontSize: 16, color: LIGHT, valign: "top", align: "left", margin: 0 }, text: "" } },
  ],
});
pres.defineSlideMaster({
  title: "CONTENT",
  background: { color: WHITE },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: 0.6, y: 0.35, w: 12.1, h: 0.85,
      fontFace: "Cambria", fontSize: 32, bold: true, color: INK, valign: "middle", align: "left", margin: 0 }, text: "" } },
    { placeholder: { options: { name: "speaker", type: "body", x: 6.6, y: 6.98, w: 5.4, h: 0.32,
      fontSize: 10, color: MUTED, align: "right", valign: "middle", margin: 0 }, text: "" } },
    { text: { text: "AgentRoute · CSE 476/575 · 11 November 2026",
      options: { x: 0.6, y: 6.98, w: 5.5, h: 0.32, fontSize: 10, color: MUTED, valign: "middle", margin: 0 } } },
  ],
  slideNumber: { x: 12.25, y: 6.98, w: 0.5, h: 0.32, fontSize: 10, color: MUTED, align: "right" },
});

const SPEAKERS = {
  omer: "Ömer Faruk Gedikli · problem and big picture",
  emre: "Bekir Emre Sarıpınar · addressing and S-FIB",
  goktepe: "Bekir Göktepe · learning, mobility, evaluation",
};

function content(section, title, speaker, notes) {
  const s = pres.addSlide({ masterName: "CONTENT", sectionTitle: section });
  s.addText(title, { placeholder: "title" });
  s.addText(SPEAKERS[speaker], { placeholder: "speaker" });
  if (notes) s.addNotes(notes);
  return s;
}

// ---------------------------------------------------------------- drawing helpers
function box(s, x, y, w, h, fill = PANEL, line = null, name = "card") {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.08, objectName: name,
    fill: { color: fill }, line: line ? { color: line, width: 1.5 } : { type: "none" } });
}
function text(s, t, x, y, w, h, o = {}) {
  s.addText(t, { x, y, w, h, isTextBox: true, margin: 0, valign: "top", fontSize: 15, color: INK, ...o });
}
function bullets(s, items, x, y, w, h, o = {}) {
  s.addText(items.map((t, i) => ({ text: t, options: { bullet: true, breakLine: i < items.length - 1 } })),
    { x, y, w, h, isTextBox: true, margin: 0, valign: "top", fontSize: 15, color: INK, paraSpaceAfter: 6, ...o });
}
function circleNum(s, n, x, y, color = "2A78D6", d = 0.5) {
  s.addShape(pres.shapes.OVAL, { x, y, w: d, h: d, fill: { color }, line: { type: "none" } });
  s.addText(String(n), { x, y, w: d, h: d, isTextBox: true, margin: 0, align: "center", valign: "middle",
    fontSize: 16, bold: true, color: WHITE });
}
function arrow(s, x1, y1, x2, y2, color = INK2, dash = "solid", width = 2) {
  s.addShape(pres.shapes.LINE, { x: Math.min(x1, x2), y: Math.min(y1, y2), w: Math.abs(x2 - x1) || 0.001,
    h: Math.abs(y2 - y1) || 0.001, flipH: x2 < x1, flipV: y2 < y1,
    line: { color, width, dashType: dash, endArrowType: "triangle" } });
}
function chipFlow(s, items, x, y, w, fill, line) {
  const gap = 0.32;
  const cw = (w - gap * (items.length - 1)) / items.length;
  items.forEach((t, i) => {
    const cx = x + i * (cw + gap);
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: cx, y, w: cw, h: 0.62, rectRadius: 0.08,
      fill: { color: fill }, line: { color: line, width: 1 } });
    s.addText(t, { x: cx, y, w: cw, h: 0.62, isTextBox: true, margin: 0.03, align: "center", valign: "middle",
      fontSize: 12, color: INK });
    if (i < items.length - 1) arrow(s, cx + cw + 0.04, y + 0.31, cx + cw + gap - 0.04, y + 0.31, INK2, "solid", 1.5);
  });
}
function stat(s, value, label, x, y, w, color = INK) {
  text(s, value, x, y, w, 0.75, { fontSize: 40, bold: true, color, fontFace: "Cambria" });
  text(s, label, x, y + 0.78, w, 0.6, { fontSize: 13, color: INK2 });
}

function chartOpts(o) {
  return {
    x: o.x, y: o.y, w: o.w, h: o.h,
    chartColors: o.colors,
    lineSize: 2, lineDataSymbol: "circle", lineDataSymbolSize: 7,
    showTitle: !!o.title, title: o.title, titleFontSize: 14, titleColor: INK, titleFontFace: "+mn-lt",
    showLegend: o.legend !== false, legendPos: o.legendPos || "t", legendFontSize: 11,
    legendFontFace: "+mn-lt", legendColor: INK2,
    catAxisLabelColor: INK2, valAxisLabelColor: INK2, catAxisLabelFontSize: 11, valAxisLabelFontSize: 11,
    catAxisLabelFontFace: "+mn-lt", valAxisLabelFontFace: "+mn-lt",
    showCatAxisTitle: !!o.xTitle, catAxisTitle: o.xTitle, catAxisTitleColor: INK2, catAxisTitleFontSize: 11,
    showValAxisTitle: !!o.yTitle, valAxisTitle: o.yTitle, valAxisTitleColor: INK2, valAxisTitleFontSize: 11,
    catAxisTitleFontFace: "+mn-lt", valAxisTitleFontFace: "+mn-lt",
    valGridLine: { color: GRID, size: 0.75 }, catGridLine: { style: "none" },
    catAxisLineColor: "C3C2B7", valAxisLineShow: false,
    ...(o.log ? { valAxisLogScaleBase: 10 } : {}),
    ...(o.min !== undefined ? { valAxisMinVal: o.min } : {}),
    ...(o.max !== undefined ? { valAxisMaxVal: o.max } : {}),
    ...(o.fmt ? { valAxisLabelFormatCode: o.fmt } : {}),
    ...(o.extra || {}),
  };
}

// methods x values -> line chart (null values drop the whole series)
function methodLines(s, exp, metric, methods, o) {
  const e = S[exp];
  const labels = e.values.map((v) => (o.labelFn ? o.labelFn(v) : String(v)));
  const series = [];
  const colors = [];
  for (const m of methods) {
    if (!e.methods[m]) continue;
    const vals = e.methods[m][metric];
    if (vals.some((v) => v == null)) continue;
    series.push({ name: M[m].name, labels, values: vals.map((v) => (o.scale ? v * o.scale : v)) });
    colors.push(M[m].color);
  }
  s.addChart(pres.charts.LINE, series, chartOpts({ ...o, colors }));
}

// ---------------------------------------------------------------- numbers used in the story
const big = S.scale.values[S.scale.values.length - 1];
const mid = S.scale.values.includes(1000) ? 1000 : S.scale.values[Math.floor(S.scale.values.length / 2)];
const at = (method) => (metric, v = big) => get("scale", method, metric, v);
const ar = at("agentroute");
const gr = at("greedy");
const gl = at("greedy_load");
const sp = at("spfr");
const fl = at("flooding");
const rg = at("registry");
const r3 = at("registry3");
const dh = at("sdht");
const ch = at("chord");
const sim = S.similarity;
const train = S.train_mlp;
const bestIdx = train ? train.val_return.indexOf(Math.max(...train.val_return)) : -1;
const kb = (x) => (x == null ? "n/a" : x >= 1000 ? `${(x / 1000).toFixed(1)} MB` : `${x >= 10 ? Math.round(x) : x.toFixed(1)} kB`);
const signed = (x, d = 1) => `${x >= 0 ? "+" : "−"}${Math.abs(x).toFixed(d)}`;
const matched = S.matched || {};
const scen = (name, pair) => (matched[name] ? matched[name][pair] : null);
const pairTxt = (p) => (p ? `${signed(p.success_diff_points)} points (95% CI ${p.success_diff_ci95[0].toFixed(1)} to ${p.success_diff_ci95[1].toFixed(1)})` : "n/a");
function ciVerb(p) {     // "beats" only if the whole interval is on one side of zero
  if (!p) return "matches";
  if (p.success_diff_ci95[0] > 0) return "beats";
  if (p.success_diff_ci95[1] < 0) return "trails";
  return "matches";
}
const mainScen = `${big} agents, load 1`;
const dqnVsLoad = scen(mainScen, "agentroute vs greedy_load");
const dqnVsGreedy = scen(mainScen, "agentroute vs greedy");
const dqnVsSpfr = scen(mainScen, "agentroute vs spfr");
const lmaxAll = S.load.values[S.load.values.length - 1];

// methods x values, plus the matching ceiling as a dashed reference
function successWithCeiling(s, exp, methods, o) {
  const e = S[exp];
  const labels = e.values.map((v) => (o.labelFn ? o.labelFn(v) : String(v)));
  const series = [];
  const colors = [];
  for (const m of methods) {
    if (!e.methods[m]) continue;
    series.push({ name: M[m].name, labels, values: e.methods[m].success_rate.map((v) => v * 100) });
    colors.push(M[m].color);
  }
  series.push({ name: "Matching ceiling", labels, values: e.methods[methods[0]].oracle_best.map((v) => v * 100) });
  colors.push("0B0B0B");
  s.addChart(pres.charts.LINE, series, chartOpts({ ...o, colors, fmt: '0"%"', min: 0, yTitle: "success" }));
}

// ================================================================= slides
// 1 ---- title
pres.addSection({ title: "Problem and big picture" });
{
  const s = pres.addSlide({ masterName: "TITLE_DARK", sectionTitle: "Problem and big picture" });
  s.addText("AgentRoute", { placeholder: "title" });
  s.addText("Learning-based semantic capability routing for AI agents in mobile networks",
    { placeholder: "body" });
  s.addText([
    { text: "Ömer Faruk Gedikli · Bekir Emre Sarıpınar · Bekir Göktepe", options: { breakLine: true } },
    { text: "CSE 476/575 Mobile Communication Networks · 11 November 2026" },
  ], { placeholder: "team" });
  s.addNotes("OMER. One sentence: we route packets to a capability instead of an address, and we test whether routers should learn the next hop. Introduce the three parts: Omer - the problem, Bekir Emre - addressing and the semantic FIB, Bekir Goktepe - learning, mobility and the evaluation.");
}

// 2 ---- where vs who can
{
  const s = content("Problem and big picture", "The Internet asks where; agents ask who can", "omer",
    "Today's Internet answers 'where?': a host has an IP address, and people use DNS names they already know. A postman does not know who you are, he delivers to an address. AI agents ask a different question: 'who can do this task?' They do not know the name or the location of the helper, they ask at machine speed, and the population is large and keeps changing.");
  box(s, 0.6, 1.5, 5.85, 5.1, PANEL);
  text(s, "Today: routing to a location", 0.95, 1.8, 5.2, 0.5, { fontSize: 20, bold: true, fontFace: "Cambria" });
  text(s, "142.250.187.14", 0.95, 2.5, 5.2, 0.7, { fontSize: 30, fontFace: "Courier New", color: INK2 });
  bullets(s, ["A host has an IP address", "DNS maps names you already know to addresses",
    "Routers match address prefixes in their FIB", "The postman delivers to an address, not to someone who can help"],
  0.95, 3.45, 5.2, 2.0);
  chipFlow(s, ["name", "DNS lookup", "IP address", "that one host"], 0.95, 5.65, 5.2, WHITE, GRID);
  box(s, 6.88, 1.5, 5.85, 5.1, TINT);
  text(s, "Agents: routing to a capability", 7.23, 1.8, 5.2, 0.5, { fontSize: 20, bold: true, fontFace: "Cambria" });
  text(s, "“find the cars in this photo”", 7.23, 2.5, 5.2, 0.7, { fontSize: 24, italic: true, color: "1C5CAB" });
  bullets(s, ["Who can do this task? Name and location unknown", "Matching by meaning, not by exact strings",
    "Machine speed, large and changing populations", "Many agents run on phones, cars and drones that change cell"],
  7.23, 3.45, 5.2, 2.0);
  chipFlow(s, ["intent vector", "S-FIB hop", "S-FIB hop", "any capable agent"], 7.23, 5.65, 5.2, WHITE, "9EC5F4");
}

// 3 ---- two classic answers
{
  const regT = rg("time_ms"); const arT = gr("time_ms");
  const flK = fl("query_kB_per_query"); const arK = gr("query_kB_per_query");
  const hoPerS = gr("handovers") / 30;
  const s = content("Problem and big picture", "Two classic answers, and what they cost", "omer",
    `Option one is a registry, like DNS: agents register, a request goes to a server first. In our simulation with ${num(big)} agents a request through one central registry takes ${ms(regT)}, because it travels to the server, back, and only then to the agent; semantic forwarding takes ${ms(arT)}. If the server's router fails, discovery stops; replicas fix that part. Option two is flooding: no state at all, but at ${num(big)} agents every request costs ${kb(flK)} of traffic, against ${kb(arK)} for forwarding. And half of our agents move: about ${Math.round(hoPerS)} handovers per second.`);
  const cards = [
    { n: 1, head: "Registry", body: "Every request first goes to a server and back. One server is also a single point of failure.",
      value: ms(regT), label: `per request at ${num(big)} agents (semantic forwarding: ${ms(arT)})`, color: M.registry.color },
    { n: 2, head: "Flooding", body: "Ask every router within a TTL: no state, but the traffic grows with the network.",
      value: kb(flK), label: `of traffic per request at ${num(big)} agents (forwarding: ${kb(arK)})`, color: M.flooding.color },
    { n: 3, head: "Mobility", body: "Agents on phones, cars and drones keep changing cell, so location tables need constant updates.",
      value: `${Math.round(hoPerS)} / s`, label: `handovers with ${num(big)} agents, half of them mobile`, color: "6250D6" },
  ];
  cards.forEach((c, i) => {
    const x = 0.6 + i * 4.1;
    box(s, x, 1.5, 3.85, 4.15, PANEL);
    circleNum(s, c.n, x + 0.3, 1.8, c.color);
    text(s, c.head, x + 0.95, 1.83, 2.7, 0.5, { fontSize: 20, bold: true, fontFace: "Cambria" });
    text(s, c.body, x + 0.3, 2.55, 3.3, 1.3, { fontSize: 15, color: INK2 });
    stat(s, c.value, c.label, x + 0.3, 3.95, 3.3);
  });
  box(s, 0.6, 5.9, 12.13, 0.75, TINT);
  text(s, "Our question: can routers find a capable agent themselves, and does learning help them?",
    0.9, 5.9, 11.6, 0.75, { fontSize: 18, bold: true, color: "1C5CAB", valign: "middle", fontFace: "Cambria" });
}

// 4 ---- related work
{
  const s = content("Problem and big picture", "Where AgentRoute sits among related work", "omer",
    "Naming by intent is not new: INS did it at the application level in 1999, and pSearch ran semantic search over a DHT in 2003. Recent Internet-of-Agents work adds protocol layers above HTTP [1], or discovery services [3], [4]. An IETF draft [14] proposes a semantic forwarding table steered by a controller, without an evaluation. The closest work, SPFR [2], forwards hop by hop to the dominant executor with a hand-designed potential field and proves loop freedom; it keeps one table row per executor and is evaluated on wired topologies. We use a compressed two-tier table, test whether a learned policy helps, and evaluate in a mobile cellular topology against SPFR's rule. NDN routes by name as well, but by exact prefix.");
  const head = (t) => ({ text: t, options: { bold: true, color: WHITE, fill: { color: NAVY } } });
  const rows = [
    [head("Work"), head("Where it lives"), head("Matching"), head("Next hop"), head("Mobile evaluation")],
    ["INS: intentional naming (1999) · pSearch (2003)", "overlay, DHT", "attributes / semantic", "–", "–"],
    ["[1] Layered protocol for Internet of Agents (2025)", "above HTTP", "agent descriptions", "–", "–"],
    ["[3], [4] Agent discovery, IETF draft-wang-dmsc (2025–26)", "discovery service", "registry / search", "–", "–"],
    ["[14] IETF draft-li semantic routing (2025)", "network layer", "intent vectors", "controller policy", "–"],
    ["[2] SPFR: semantic potential field routing (2026)", "network layer", "semantic, per executor", "hand-designed", "–"],
  ].map((r, i) => (i === 0 ? r : r.map((c) => ({ text: c, options: { color: INK } }))));
  const ours = ["AgentRoute (ours)", "network layer", "semantic, two-tier S-FIB", "learned, and hand-written rivals", "cellular / edge, handovers"]
    .map((c) => ({ text: c, options: { bold: true, color: "1C5CAB", fill: { color: TINT } } }));
  rows.push(ours);
  s.addTable(rows, { x: 0.6, y: 1.55, w: 12.1, colW: [4.3, 1.7, 2.2, 2.0, 1.9], fontSize: 13, fontFace: "Calibri",
    border: { type: "solid", color: GRID, pt: 1 }, rowH: 0.56, valign: "middle", margin: 0.07 });
  text(s, "[1] Fleming et al., arXiv:2511.19699 · [2] Qin et al., arXiv:2608.25396 · [3] Guo et al., arXiv:2511.19113 · [4] draft-wang-dmsc-drisac-00 · [14] draft-li-semantic-routing-architecture-00",
    0.6, 6.2, 12.1, 0.4, { fontSize: 11, color: MUTED });
}

// 5 ---- one picture
{
  const s = content("Problem and big picture", "AgentRoute in one picture", "omer",
    "Two things happen. (1) Dashed: agents advertise their capabilities, and every router fills its semantic FIB - for each neighbour, which capabilities lie behind it. (2) Solid: a task packet carries an intent embedding instead of a destination address; each router either hands it to a local agent or forwards it to the best neighbour. Inside every node, the S-FIB match and the local network state go into the policy that takes this decision. Bekir Emre now explains the addressing and the S-FIB.");
  const nodes = [
    { t: "Requesting agent", b: "on a mobile UE,\nmoves between cells", hl: false },
    { t: "gNB + edge node", b: "AgentRoute node\nS-FIB + policy", hl: true },
    { t: "Core router", b: "AgentRoute node\nS-FIB + policy", hl: true },
    { t: "Serving agent", b: "capability:\nobject detection", hl: false },
  ];
  nodes.forEach((n, i) => {
    const x = 0.6 + i * 3.15;
    box(s, x, 2.0, 2.65, 1.35, n.hl ? TINT : PANEL, n.hl ? "2A78D6" : null);
    text(s, n.t, x + 0.15, 2.12, 2.35, 0.4, { fontSize: 16, bold: true, align: "center" });
    text(s, n.b, x + 0.15, 2.55, 2.35, 0.75, { fontSize: 13, color: INK2, align: "center" });
    if (i < 3) {
      arrow(s, x + 2.7, 2.95, x + 3.1, 2.95, "2A78D6", "solid", 2.5);
      arrow(s, x + 3.1, 2.4, x + 2.7, 2.4, MUTED, "dash", 1.5);
    }
  });
  text(s, "(1) dashed: capability advertisements fill every S-FIB", 0.6, 1.5, 6.5, 0.35, { fontSize: 13, color: MUTED });
  text(s, "(2) solid: a task packet with an intent embedding, hop by hop", 6.3, 1.5, 6.4, 0.35, { fontSize: 13, color: "1C5CAB", align: "right" });
  box(s, 0.6, 3.85, 12.1, 2.75, PANEL);
  text(s, "Inside an AgentRoute node", 0.9, 4.0, 6, 0.4, { fontSize: 16, bold: true, fontFace: "Cambria" });
  const steps = [
    ["Intent embedding", "carried in the packet\n(MiniLM, int8, 388 B)"],
    ["S-FIB match", "cosine similarity of the\nintent to each neighbour"],
    ["Local state", "queue load, link quality,\nhandovers, TTL"],
    ["Policy", "deliver here,\nor which neighbour next"],
  ];
  steps.forEach((st, i) => {
    const x = 0.9 + i * 2.95;
    box(s, x, 4.55, 2.55, 1.6, WHITE, i === 3 ? "2A78D6" : GRID);
    text(s, st[0], x + 0.12, 4.68, 2.3, 0.4, { fontSize: 15, bold: true, align: "center" });
    text(s, st[1], x + 0.12, 5.12, 2.3, 0.9, { fontSize: 13, color: INK2, align: "center" });
    if (i < 3) arrow(s, x + 2.6, 5.35, x + 2.9, 5.35, INK2);
  });
}

// 6 ---- capability address
pres.addSection({ title: "Addressing and S-FIB" });
{
  const encoders = JSON.parse(fs.readFileSync(path.join(ROOT, "results", "encoders.json"), "utf8"));
  const tops = Object.values(encoders).map((e) => e.test.top1);
  const encRange = `${Math.round(Math.min(...tops) * 100)}–${Math.round(Math.max(...tops) * 100)}%`;
  const s = content("Addressing and S-FIB", "A capability address is a vector, not a host", "emre",
    `BEKIR EMRE. Each provider describes its skill in its own words, so every agent gets its own vector: a random mix of the sentences of its capability. We encode the sentences with the pre-trained MiniLM encoder. Example: 'find the cars in this photo' has cosine ${sim.example[0].cos} with the object-detection card, but only ${sim.example[2].cos} with image classification. An agent accepts a task when the cosine is at least tau = ${TAU.tau}. We choose tau by expected value: plus one for the right agent, minus one for the wrong agent, zero for nothing. On unseen paraphrases the most similar agent is of the right class ${pct(TAU.test_top1)} of the time. We tried ${tops.length} pre-trained encoders: they all land at ${encRange} on the unseen paraphrases, so a bigger encoder does not fix this. The chart shows why: same-class and other-class similarities overlap.`);
  text(s, "Agent's sentences → MiniLM → its own weighted mix", 0.6, 1.5, 6.0, 0.4, { fontSize: 16, bold: true });
  box(s, 0.6, 2.0, 6.0, 1.45, PANEL);
  bullets(s, ["object detection in images", "box the vehicles in a traffic camera image",
    "show where each person stands in a crowd photo"], 0.9, 2.15, 5.5, 1.2, { fontSize: 14, color: INK2 });
  text(s, `Request “find the cars in this photo”  (accept if cos ≥ τ = ${TAU.tau})`, 0.6, 3.75, 6.0, 0.4, { fontSize: 15, bold: true });
  sim.example.forEach((e, i) => {
    const y = 4.25 + i * 0.62;
    const ok = e.cos >= TAU.tau;
    box(s, 0.6, y, 6.0, 0.5, ok ? TINT : PANEL);
    text(s, e.card, 0.8, y + 0.1, 4.3, 0.32, { fontSize: 13, color: INK });
    text(s, `${e.cos.toFixed(3)}  ${ok ? "✓ accept" : "✗ reject"}`, 5.0, y + 0.1, 1.5, 0.32,
      { fontSize: 13, bold: true, color: ok ? GOOD : CRIT, align: "right" });
  });
  s.addChart(pres.charts.BAR, [
    { name: "Request vs other-class cards", labels: sim.bins, values: sim.other_pct },
    { name: "Request vs same-class cards", labels: sim.bins, values: sim.same_pct },
  ], chartOpts({ x: 6.95, y: 1.45, w: 5.8, h: 4.55, colors: ["B4B2A9", "2A78D6"], title: "Cosine similarity, unseen paraphrases",
    xTitle: "cosine similarity", yTitle: "% of pairs", extra: { barDir: "col", barGapWidthPct: 20, barGrouping: "clustered" } }));
  text(s, `τ = ${TAU.tau} · best agent right ${pct(TAU.test_top1)} · ${tops.length} encoders: ${encRange}`,
    6.95, 6.1, 5.8, 0.4, { fontSize: 13, color: INK2, align: "center" });
}

// 7 ---- S-FIB
{
  const v = (name, metric) => get("ablation_summary", "greedy", metric, name);
  const s = content("Addressing and S-FIB", "The S-FIB: what lies behind each neighbour", "emre",
    `A normal router says 'for this IP range, use that port'. Our router says 'behind this neighbour there are these capabilities' - like the sign at a mall corridor. Routers exchange only what fits in a message. Agents attached to a neighbour keep their own row; everything further away is compressed at every hop into k = 8 representative vectors, so a message does not grow with the number of agents. In the ablation, greedy forwarding reaches ${pct(v("k=8, no tier", "success_rate"))} with summaries only, ${pct(v("k=8", "success_rate"))} with the two-tier table and ${pct(v("exact", "success_rate"))} with one row per agent, which costs ${kb(v("exact", "ctrl_kB_per_s"))} per second instead of ${kb(v("k=8", "ctrl_kB_per_s"))}. Under this table we also changed the delivery rule: a router keeps forwarding when a neighbour advertises a clearly better candidate.`);
  const head = (t) => ({ text: t, options: { bold: true, color: WHITE, fill: { color: NAVY } } });
  const rows = [
    [head("Behind neighbour"), head("What the table holds"), head("Hops")],
    ["agents attached to it", "one row per agent (their real vectors)", "1"],
    ["everything further", "k = 8 representatives, recomputed at every hop", "2 … R"],
    ["size of a message", "attached agents + 8 rows × 396 B, no matter how many agents", "–"],
  ].map((r, i) => (i === 0 ? r : r.map((c) => ({ text: c, options: { color: INK } }))));
  s.addTable(rows, { x: 0.6, y: 1.6, w: 7.3, colW: [2.1, 4.3, 0.9], fontSize: 14, fontFace: "Calibri",
    border: { type: "solid", color: GRID, pt: 1 }, rowH: 0.72, valign: "middle", margin: 0.08 });
  box(s, 8.3, 1.6, 4.43, 4.9, TINT);
  text(s, "IP FIB vs S-FIB", 8.6, 1.8, 3.9, 0.45, { fontSize: 18, bold: true, fontFace: "Cambria" });
  bullets(s, ["IP: prefix → output port", "S-FIB: neighbour → capability summary",
    "Score of a neighbour = best cosine with its rows",
    "A router only ever receives what its neighbours send: summaries of summaries",
    "Handover: withdraw and announce, forwarded only if a summary moves"],
  8.6, 2.35, 3.9, 4.0, { fontSize: 14 });
  stat(s, pct(v("k=8, no tier", "success_rate")), `summaries only · ${kb(v("k=8, no tier", "ctrl_kB_per_s"))}/s`, 0.6, 5.05, 2.3, M.greedy.color);
  stat(s, pct(v("k=8", "success_rate")), `two-tier · ${kb(v("k=8", "ctrl_kB_per_s"))}/s`, 3.1, 5.05, 2.3, M.greedy.color);
  stat(s, pct(v("exact", "success_rate")), `one row per agent · ${kb(v("exact", "ctrl_kB_per_s"))}/s`, 5.6, 5.05, 2.3, M.greedy.color);
}

// 8 ---- radius
{
  const r = S.radius.values;
  const methods = ["agentroute", "greedy", "greedy_load"];
  const s = content("Addressing and S-FIB", "Advertisements reach R hops, not the whole network", "emre",
    `Agents do not advertise to the whole network, only R hops away. With ${num(1000)} agents, going from R = ${r[0]} to R = ${r[r.length - 1]} moves greedy from ${pct(get("radius", "greedy", "success_rate", r[0]))} to ${pct(get("radius", "greedy", "success_rate", r[r.length - 1]))} success, and control traffic from ${kb(get("radius", "greedy", "ctrl_kB_per_s", r[0]))} to ${kb(get("radius", "greedy", "ctrl_kB_per_s", r[r.length - 1]))} per second. Success peaks at R = 2 (${pct(get("radius", "greedy", "success_rate", 2))}): beyond it nothing improves, and control traffic hardly grows because every link carries the same few representatives. So we use R = 2, which is also SPFR's control horizon.`);
  methodLines(s, "radius", "success_rate", methods, { x: 0.6, y: 1.45, w: 6.0, h: 5.0, scale: 100, fmt: '0"%"', min: 0,
    title: "Success rate", xTitle: "advertisement radius R (hops)", yTitle: "success" });
  s.addChart(pres.charts.LINE, [{ name: "Same S-FIB for all these methods", labels: r.map(String),
    values: S.radius.methods.greedy.ctrl_kB_per_s }], chartOpts({ x: 6.75, y: 1.45, w: 6.0, h: 5.0, colors: [INK2], min: 0,
    title: "Control traffic (kB/s)", xTitle: "advertisement radius R (hops)", yTitle: "kB/s" }));
}

// 9 ---- what limits success
{
  const d = S.scale.drops || {};
  const oracle = gr("oracle_best", mid);
  const s = content("Addressing and S-FIB", "Most failures come from matching, not routing", "emre",
    `With ${num(mid)} agents, a method that knows every attached agent would still only succeed on ${pct(oracle)} of requests: for the rest, the most similar agent is of the wrong class or nothing passes tau. That is the dashed ceiling on the later charts. Greedy forwarding delivers ${pct(gr("success_rate", mid))}, the central registry ${pct(rg("success_rate", mid))}, flooding ${pct(fl("success_rate", mid))}. The remaining failures are wrong matches, and packets that never find a match and run out of TTL. So the next question: what if the most similar neighbour is congested, or a better match is one hop away? Bekir Goktepe continues.`);
  stat(s, pct(oracle), `matching ceiling with ${num(mid)} agents`, 0.6, 1.6, 3.6, INK);
  stat(s, pct(gr("success_rate", mid)), "greedy semantic forwarding", 0.6, 3.15, 3.6, M.greedy.color);
  const reasons = [["wrong_agent", "Wrong agent"], ["not_found", "No match found"], ["ttl", "TTL expired"],
    ["queue", "Queue overflow"], ["link", "Link loss"], ["handover", "Agent in handover"], ["stale_location", "Stale location"],
    ["registry_queue", "Registry overloaded"], ["node_down", "Node down"]];
  const methods = ["agentroute", "greedy", "greedy_load", "spfr", "flooding", "registry"].filter((m) => d[m]);
  const palette = ["8A8984", "B4B2A9", "6250D6", "D03B3B", "EB6834", "EDA100", "E87BA4", "1C5CAB", "3B3A37"];
  const series = [];
  const colors = [];
  reasons.forEach(([k, label], i) => {
    const vals = methods.map((m) => (d[m][k] || 0) * 100);
    if (Math.max(...vals) > 0.3) { series.push({ name: label, labels: methods.map((m) => M[m].name), values: vals }); colors.push(palette[i]); }
  });
  s.addChart(pres.charts.BAR, series, chartOpts({ x: 4.5, y: 1.45, w: 8.25, h: 3.9, colors,
    title: `Why requests fail (${num(mid)} agents, % of requests)`, legendPos: "b", fmt: '0"%"',
    extra: { barDir: "bar", barGrouping: "stacked", barGapWidthPct: 60 } }));
  box(s, 0.6, 5.55, 12.13, 0.95, TINT);
  text(s, "What if the most similar neighbour is congested, or a better match is one hop away?",
    0.9, 5.7, 11.6, 0.65, { fontSize: 20, bold: true, fontFace: "Cambria", color: "1C5CAB", valign: "middle" });
}

// 10 ---- DQN
pres.addSection({ title: "Learning, mobility, evaluation" });
{
  const s = content("Learning, mobility, evaluation", "One shared DQN: deliver here, or forward where?", "goktepe",
    "BEKIR GOKTEPE. The DQN takes the routing decision. Because routers have different numbers of neighbours, the network does not output one value per action: it scores each action separately - input is that action's feature vector, output is one Q-value. The actions are the neighbours, plus 'deliver to the best local agent', so the network also decides whether a local match is good enough. All routers share one network, trained offline in the simulator. Reward per decision is minus the normalised delay, plus one on correct delivery, minus one on a drop or a wrong agent. Training is Double DQN with replay and a target network; the next-state value is the max Q over the next router's actions, which is Q-routing with a neural network.");
  text(s, "Features of one action (15)", 0.6, 1.5, 4.2, 0.4, { fontSize: 16, bold: true });
  const feats = ["S-FIB similarity: max, mean, gap to best", "match above τ, hop distance", "queue occupancy (hello)",
    "link quality and delay", "neighbour in handover", "TTL left, already visited", "type: gNB / core / cloud / deliver here"];
  feats.forEach((f, i) => {
    box(s, 0.6, 2.0 + i * 0.56, 4.2, 0.46, PANEL);
    text(s, f, 0.78, 2.07 + i * 0.56, 3.9, 0.34, { fontSize: 13, color: INK });
  });
  arrow(s, 4.9, 3.9, 5.5, 3.9, INK2);
  box(s, 5.55, 2.85, 2.6, 2.1, TINT, "2A78D6");
  text(s, "Shared MLP", 5.7, 3.05, 2.3, 0.45, { fontSize: 18, bold: true, align: "center", fontFace: "Cambria" });
  text(s, "15 → 64 → 64 → 1\nsame weights in\nevery router", 5.7, 3.55, 2.3, 1.2, { fontSize: 13, color: INK2, align: "center" });
  arrow(s, 8.2, 3.9, 8.8, 3.9, INK2);
  const qs = [["here", 0.45], ["n1", 0.9], ["n2", 0.35]];
  qs.forEach(([n, q], i) => {
    const y = 2.95 + i * 0.62;
    text(s, `Q(${n})`, 8.9, y + 0.05, 0.8, 0.36, { fontSize: 13, color: INK2 });
    s.addShape(pres.shapes.RECTANGLE, { x: 9.7, y: y + 0.08, w: 2.2 * q, h: 0.32,
      fill: { color: i === 1 ? "2A78D6" : "B4B2A9" }, line: { type: "none" } });
  });
  text(s, "argmax → forward to n1", 8.9, 4.85, 3.8, 0.4, { fontSize: 14, bold: true, color: "1C5CAB" });
  box(s, 5.55, 5.45, 7.18, 1.2, PANEL);
  text(s, [
    { text: "Reward  ", options: { bold: true } },
    { text: "per decision −(0.05 + delay / 100 ms) · right agent +1 · drop or wrong agent −1", options: { breakLine: true } },
    { text: "Training  ", options: { bold: true } },
    { text: "Double DQN, replay 50k, target net, ε 1 → 0.05, 300 random scenarios" },
  ], 5.75, 5.6, 6.9, 0.95, { fontSize: 13, color: INK });
}

// 11 ---- learning curve
if (train) {
  const best = train.val_success[bestIdx];
  const bestRet = train.val_return[bestIdx];
  const v = verb(bestRet, Math.max(train.greedy_val_return, train.load_val_return), 0.01);
  const first = train.val_return[0];
  const s = content("Learning, mobility, evaluation", `Validation: the DQN ${v} both same-table rules`, "goktepe",
    `Everything here is measured with exploration switched off, on fixed validation scenarios. We do not show the training return, because that one rises anyway as exploration falls. The dashed lines are greedy and load-aware greedy, measured with the same reward. Validation return of the DQN starts at ${first.toFixed(2)} and its best is ${bestRet.toFixed(2)} at episode ${train.episode[bestIdx]}. Greedy has ${train.greedy_val_return.toFixed(2)}, load-aware greedy ${train.load_val_return.toFixed(2)}. Success: DQN ${pct(best, 1)}, greedy ${pct(train.greedy_val_success, 1)}, load-aware ${pct(train.load_val_success, 1)}.`);
  const labels = train.episode.map(String);
  const series = (key, loadKey, greedyKey, f) => [
    { name: M.agentroute.name, labels, values: train[key].map(f) },
    ...(S.train_gnn && S.train_gnn.episode.length === train.episode.length ? [{ name: M.agentroute_gnn.name, labels, values: S.train_gnn[key].map(f) }] : []),
    { name: "Greedy (reference)", labels, values: labels.map(() => f(train[greedyKey])) },
    { name: "Load-aware greedy (reference)", labels, values: labels.map(() => f(train[loadKey])) },
  ];
  const colors = S.train_gnn && S.train_gnn.episode.length === train.episode.length
    ? [M.agentroute.color, M.agentroute_gnn.color, M.greedy.color, M.greedy_load.color]
    : [M.agentroute.color, M.greedy.color, M.greedy_load.color];
  s.addChart(pres.charts.LINE, series("val_return", "load_val_return", "greedy_val_return", (x) => x),
    chartOpts({ x: 0.6, y: 1.45, w: 6.0, h: 5.0, colors, title: "Validation return per request", xTitle: "training episode",
      yTitle: "return", extra: { lineDataSymbolSize: 5 } }));
  s.addChart(pres.charts.LINE, series("val_success", "load_val_success", "greedy_val_success", (x) => x * 100),
    chartOpts({ x: 6.75, y: 1.45, w: 6.0, h: 5.0, colors, fmt: '0"%"', title: "Validation success", xTitle: "training episode",
      yTitle: "success", legend: false, extra: { lineDataSymbolSize: 5 } }));
}

// 12 ---- mobility
{
  const sp_ = S.mobility.values;
  const hi = sp_[sp_.length - 1];
  const hc = S.handover_cost;
  const sizes = Object.keys(hc).map(Number).sort((a, b) => a - b);
  const n = sizes[sizes.length - 1];
  const top = hc[String(n)];
  const lo = get("mobility", "greedy", "ctrl_kB_per_s", 0.0);
  const up = get("mobility", "greedy", "ctrl_kB_per_s", hi);
  const rlo = get("mobility", "registry3", "ctrl_kB_per_s", 0.0);
  const rup = get("mobility", "registry3", "ctrl_kB_per_s", hi);
  const s = content("Learning, mobility, evaluation", "Mobility costs messages, not success", "goktepe",
    `When a phone changes cell, the old gNB withdraws it and the new gNB announces it within R hops, and a router passes the update on only if one of its summaries really moves. Measured at ${num(n)} agents: ${top.msgs_per_handover} messages per handover, ${top.handover_msgs_per_s} messages per second in total, ${top.handover_kB_per_s} kB/s, next to ${top.refresh_kB_per_s} kB/s of periodic refresh. Success barely depends on speed for any method - at ${hi} m/s greedy delivers ${pct(get("mobility", "greedy", "success_rate", hi))} and a three-replica registry ${pct(get("mobility", "registry3", "success_rate", hi))}, and with 150 metre cells ${pct(get("mobility_small", "greedy", "success_rate", hi))} and ${pct(get("mobility_small", "registry3", "success_rate", hi))} - because an agent is in handover for only 50 ms. So mobility is a cost problem, not a reachability problem: from 0 to ${hi} m/s, control traffic goes from ${kb(lo)} to ${kb(up)} per second for the S-FIB, and from ${kb(rlo)} to ${kb(rup)} for the registry.`);
  box(s, 0.6, 1.5, 4.6, 5.0, PANEL);
  text(s, "Incremental S-FIB update", 0.9, 1.7, 4.0, 0.45, { fontSize: 18, bold: true, fontFace: "Cambria" });
  circleNum(s, 1, 0.9, 2.35, CRIT, 0.42);
  text(s, "Old cell withdraws the agent within R hops", 1.45, 2.38, 3.6, 0.6, { fontSize: 14 });
  circleNum(s, 2, 0.9, 3.05, GOOD, 0.42);
  text(s, "New cell announces it within R hops", 1.45, 3.08, 3.6, 0.6, { fontSize: 14 });
  circleNum(s, 3, 0.9, 3.75, "6B6A66", 0.42);
  text(s, "A router forwards it only if a summary moves", 1.45, 3.78, 3.6, 0.6, { fontSize: 14 });
  stat(s, String(top.msgs_per_handover), `messages per handover at ${num(n)} agents`, 0.9, 4.6, 2.0, "1C5CAB");
  stat(s, `${kb(top.handover_kB_per_s)}/s`, `handovers, next to ${kb(top.refresh_kB_per_s)}/s of refresh`, 3.0, 4.6, 2.1, INK2);
  successWithCeiling(s, "mobility_small", ALL, { x: 5.45, y: 1.45, w: 7.3, h: 5.05,
    title: `Success vs speed (${num(1000)} agents, 150 m cells)`, xTitle: "mobile agent speed (m/s)" });
}

// 13 ---- setup
{
  const s = content("Learning, mobility, evaluation", "Evaluation setup", "goktepe",
    "Discrete-event simulator in Python with SimPy and NetworkX. gNB + edge routers on a cell grid, a core network and a cloud; the number of cells grows with the number of agents, up to 450 routers. Agents: 40 percent fixed edge agents, 50 percent mobile with random waypoint, 10 percent in the cloud. Requests use 150 paraphrases never seen in training. We deliberately added strong rivals: a load-aware heuristic, SPFR's rule, a replicated registry and a semantic DHT at the application layer. Chord with exact keys finds nothing by construction, because our requests never repeat a capability text; it is only a cost reference. Ten seeds per point, 95 percent confidence intervals. Times include everything a method must do, including the flooding window and the answer traffic.");
  const cards = [
    ["Topology", "gNB + edge cells, core grid, cloud; 9 → 400 cells, up to 450 routers; queues, bursty hotspots, lossy links"],
    ["Agents", "40% fixed edge, 50% mobile (random waypoint, handover with hysteresis), 10% cloud; every agent has its own vector"],
    ["Requests", "150 unseen paraphrases of 50 capability classes, 10 requests/s (rate swept 1–300/s), TTL 16"],
    ["Rivals", "greedy, load-aware greedy, SPFR-style · flooding · registry (1 and 3 replicas) · semantic DHT · Chord exact"],
    ["Metrics", "success vs matching ceiling, time on requests both delivered, hops, control kB/s, query kB/request"],
    ["Runs", "SimPy + NetworkX, 10 seeds per point, paired 95% CI, 100 → 10,000 agents, laptop CPU"],
  ];
  cards.forEach((c, i) => {
    const x = 0.6 + (i % 3) * 4.1;
    const y = 1.55 + Math.floor(i / 3) * 2.55;
    box(s, x, y, 3.85, 2.3, i === 3 ? TINT : PANEL);
    text(s, c[0], x + 0.3, y + 0.25, 3.3, 0.45, { fontSize: 18, bold: true, fontFace: "Cambria" });
    text(s, c[1], x + 0.3, y + 0.8, 3.3, 1.4, { fontSize: 14, color: INK2 });
  });
}

// 14 ---- scale
{
  const s = content("Learning, mobility, evaluation", `Scaling to ${num(big)} agents`, "goktepe",
    `Left: success from 100 to ${num(big)} agents, with the matching ceiling as a dashed line. At ${num(big)} agents the ceiling is ${pct(gr("oracle_best"))}. Greedy delivers ${pct(gr("success_rate"))}, the DQN ${pct(ar("success_rate"))}, load-aware greedy ${pct(gl("success_rate"))}, SPFR-style ${pct(sp("success_rate"))}, flooding ${pct(fl("success_rate"))}, the central registry ${pct(rg("success_rate"))}, three replicas ${pct(r3("success_rate"))}, the semantic DHT ${pct(dh("success_rate"))}. Chord is zero by construction. Right: control traffic for the whole network. Times at ${num(big)} agents: forwarding ${ms(gr("time_ms"))}, registry ${ms(rg("time_ms"))}, DHT ${ms(dh("time_ms"))}, flooding ${ms(fl("time_ms"))}.`);
  const lab = (x) => (x >= 1000 ? `${x / 1000}K` : String(x));
  successWithCeiling(s, "scale", ALL, { x: 0.6, y: 1.45, w: 6.0, h: 5.05, labelFn: lab, title: "Discovery success", xTitle: "number of agents" });
  methodLines(s, "scale", "ctrl_kB_per_s", ALL.filter((m) => m !== "flooding"), { x: 6.75, y: 1.45, w: 6.0, h: 5.05, log: true, labelFn: lab,
    title: "Control traffic, whole network (kB/s, log)", xTitle: "number of agents", yTitle: "kB/s", legend: false });
}

// 15 ---- traffic vs request rate
{
  const e = S.rate;
  const labels = e.values.map(String);
  const methods = ["agentroute", "spfr", "flooding", "registry3", "sdht"].filter((m) => e.methods[m]);
  const total = (m, i) => e.methods[m].ctrl_kB_per_s[i] + e.methods[m].query_kB_per_query[i] * e.values[i];
  const series = methods.map((m) => ({ name: M[m].name, labels, values: e.values.map((_, i) => total(m, i)) }));
  const cross = e.values.find((_, i) => total("flooding", i) > total("agentroute", i));
  const s = content("Learning, mobility, evaluation", "Who is cheaper depends on the request rate", "goktepe",
    `Control traffic is paid per second, query traffic per request, so 'messages per request' depends on the rate one assumes. This chart shows the total traffic for ${num(1000)} agents. Flooding has no control traffic, so it wins when requests are rare. ${cross ? `From about ${cross} requests per second flooding costs more than semantic forwarding.` : "In the range we tested flooding stays cheaper."} A registry is the cheapest at any rate, because it sends small messages; what it pays is the extra latency and the dependence on its servers.`);
  s.addChart(pres.charts.LINE, series, chartOpts({ x: 0.6, y: 1.45, w: 8.0, h: 5.05, log: true,
    colors: methods.map((m) => M[m].color), title: `Total traffic, ${num(1000)} agents (kB/s, log)`, xTitle: "requests per second, whole network", yTitle: "kB/s" }));
  box(s, 8.9, 1.6, 3.83, 4.9, PANEL);
  text(s, "How to read this", 9.15, 1.8, 3.4, 0.45, { fontSize: 18, bold: true, fontFace: "Cambria" });
  bullets(s, ["Flat part = control traffic, paid every second", "Rising part = traffic per request",
    cross ? `Flooding overtakes forwarding at about ${cross} requests/s` : "Flooding stays below forwarding here",
    "Registry: cheapest bytes, slower requests"], 9.15, 2.4, 3.4, 3.9, { fontSize: 14 });
}

// 16 ---- robustness
{
  const fv = S.failure.values;
  const fmax = fv[fv.length - 1];
  const lv = S.load.values;
  const lmax = lv[lv.length - 1];
  const heavy = scen(`1000 agents, load 4`, "agentroute vs greedy_load");
  const rb = S.failure.registry_by_server[String(fmax)];
  const regCase = `${pct(rb.up)} when its server survives (${rb.n_up} of ${rb.n_up + rb.n_down} seeds) and ${pct(rb.down)} when it does not`;
  const s = content("Learning, mobility, evaluation", "Robustness: failures and load", "goktepe",
    `Left: a fraction of routers fails at one third of the run. With ${pct(fmax)} failed routers greedy delivers ${pct(get("failure", "greedy", "success_rate", fmax))}, the central registry ${pct(get("failure", "registry", "success_rate", fmax))}, three replicas ${pct(get("failure", "registry3", "success_rate", fmax))}. The registry's mean hides two cases: ${regCase}. Replicas fix most of this. Right: the load factor scales both requests and background traffic. At load ${lmax}: DQN ${pct(get("load", "agentroute", "success_rate", lmax))}, greedy ${pct(get("load", "greedy", "success_rate", lmax))}, load-aware greedy ${pct(get("load", "greedy_load", "success_rate", lmax))}, flooding ${pct(get("load", "flooding", "success_rate", lmax))}.${heavy ? ` Paired on the same requests at load 4, DQN minus load-aware greedy is ${pairTxt(heavy)}.` : ""}`);
  successWithCeiling(s, "failure", ALL, { x: 0.6, y: 1.45, w: 6.0, h: 5.05,
    labelFn: (x) => `${Math.round(x * 100)}%`, title: "Success vs failed routers", xTitle: "failed routers" });
  successWithCeiling(s, "load", ALL, { x: 6.75, y: 1.45, w: 6.0, h: 5.05, title: "Success vs network load", xTitle: "load factor", legend: false });
}

// 17 ---- demo video(s)
function videoSlide(file, title, notes) {
  const video = path.join(FIG, `${file}.mp4`);
  const poster = path.join(FIG, `${file}_poster.png`);
  if (!fs.existsSync(video)) return;
  const s = content("Learning, mobility, evaluation", title, "goktepe", notes);
  const cover = fs.existsSync(poster) ? `data:image/png;base64,${fs.readFileSync(poster).toString("base64")}` : undefined;
  s.addMedia({ type: "video", path: video, x: 1.0, y: 1.4, w: 11.33, h: 5.35, ...(cover ? { cover } : {}) });
}
videoSlide("agentroute_demo", "Demo: a request routed by meaning",
  "Recorded animation from a real simulation log (no live demo). First the advertisements fill the S-FIBs, then one request travels hop by hop to an agent that can serve it, then a phone changes cell and only the nearby entries are updated.");
{
  const f = path.join(FIG, "greedy_vs_agentroute.json");
  if (fs.existsSync(f)) {
    const c = JSON.parse(fs.readFileSync(f, "utf8"));
    const say = (o) => (o.type === "deliver"
      ? `is delivered to a ${o.agent_class} agent in ${o.hops} hops, ${o.time_ms} ms`
      : `fails after ${o.hops} hops (${o.reason.replace("_", " ")})`);
    videoSlide("greedy_vs_agentroute", "One selected example: greedy vs learned",
      `Say this clearly: this is one hand-picked request, chosen because the two paths differ and the learned one does better. It only illustrates what a different decision looks like; the averages are on the other slides. Request: '${c.text}'. Orange halos are routers busy with background traffic. With greedy the request ${say(c.greedy)}; with the learned policy it ${say(c.agentroute)}.`);
  }
}

// 18 ---- takeaways
{
  const s = pres.addSlide({ masterName: "TITLE_DARK", sectionTitle: "Learning, mobility, evaluation" });
  s.addText("Takeaways", { placeholder: "title" });
  const load = ciVerb(dqnVsLoad);
  const items = [
    `Routing by meaning works without a server: at ${num(big)} agents greedy delivers ${pct(gr("success_rate"))} and the DQN ${pct(get("scale", "agentroute", "success_rate", big))} (ceiling ${pct(gr("oracle_best"))}), in ${ms(gr("time_ms"))} against ${ms(rg("time_ms"))} via a registry`,
    `It is not free: a two-tier S-FIB costs ${kb(gr("ctrl_kB_per_s"))}/s, one row per agent (SPFR-style) ${kb(sp("ctrl_kB_per_s"))}/s for ${signed((sp("success_rate") - gr("success_rate")) * 100)} points, a registry only ${kb(rg("ctrl_kB_per_s"))}/s`,
    `Learning: the DQN ${load} load-aware greedy at ${num(big)} agents (${pairTxt(dqnVsLoad)}). Matching quality, not routing, sets the ceiling`,
  ];
  items.forEach((t, i) => {
    circleNum(s, i + 1, 0.8, 3.45 + i * 0.85, "2A78D6", 0.5);
    s.addText(t, { x: 1.5, y: 3.43 + i * 0.85, w: 11.0, h: 0.72, isTextBox: true, margin: 0, fontSize: 16,
      color: WHITE, valign: "middle" });
  });
  s.addText("Future work: agent-side verification · learned capability representations · signed advertisements · UDP overlay prototype", {
    x: 0.8, y: 6.2, w: 11.7, h: 0.5, isTextBox: true, margin: 0, fontSize: 14, color: LIGHT });
  s.addNotes(`Close with the honest summary. Routing by meaning works without a server and is fast. The compressed table is much cheaper than one row per agent and loses little. Learning: compared with a one-line load-balancing rule on the same requests, the DQN ${load} it: ${pairTxt(dqnVsLoad)}; against plain greedy ${pairTxt(dqnVsGreedy)}; against the SPFR-style rule ${pairTxt(dqnVsSpfr)}. The ceiling comes from the matching. If there is time: we also replaced the fixed radio hop by a distance-dependent link model computed with NVIDIA Sionna (3GPP TR 38.901 channel, 5G NR block error rates, HARQ). Success falls by 8 to 21 points, the registries fall the most because they cross the radio four times, and the DQN keeps its lead over greedy. Details are in the final report. Thank you, questions.`);
}

// 19 ---- backup: ablations
if (S.ablation_summary && S.ablation_header) {
  pres.addSection({ title: "Backup" });
  const s = content("Backup", "Backup: S-FIB content and header size", "goktepe",
    "Backup slide. Left: what the table content costs in success. Right: compressing the intent header from 1,536 bytes (float32) to 388 bytes (int8) or 48 bytes (binary signs).");
  const ORDER = { ablation_summary: ["mean", "k=8, no tier", "k=4", "k=8", "k=16", "exact"], ablation_header: ["float32", "int8", "binary"] };
  const mk = (exp, methods) => methods.map((m) => {
    const vals = S[exp].values;
    const order = ORDER[exp].filter((v) => vals.includes(v));
    return { name: M[m].name, labels: order.map(String),
      values: order.map((v) => S[exp].methods[m].success_rate[vals.indexOf(v)] * 100) };
  });
  s.addChart(pres.charts.BAR, mk("ablation_summary", ["agentroute", "greedy"]), chartOpts({ x: 0.6, y: 1.45, w: 6.0, h: 5.05,
    colors: [M.agentroute.color, M.greedy.color], fmt: '0"%"', min: 0, title: "S-FIB content per neighbour",
    yTitle: "success", extra: { barDir: "col", barGapWidthPct: 60 } }));
  const hdr = mk("ablation_header", ["agentroute", "greedy"]);
  const names = { float32: "float32 (1,536 B)", int8: "int8 (388 B)", binary: "binary (48 B)" };
  hdr.forEach((h) => { h.labels = h.labels.map((v) => names[v] || v); });
  s.addChart(pres.charts.BAR, hdr, chartOpts({ x: 6.75, y: 1.45, w: 6.0, h: 5.05, colors: [M.agentroute.color, M.greedy.color],
    fmt: '0"%"', min: 0, title: "Intent header encoding", yTitle: "success", extra: { barDir: "col", barGapWidthPct: 60 } }));
}

// ---------------------------------------------------------------- write + theme
async function writeTheme(file) {
  const JSZip = require(require.resolve("jszip", { paths: [require.resolve("pptxgenjs")] }));
  const zip = await JSZip.loadAsync(fs.readFileSync(file));
  const part = "ppt/theme/theme1.xml";
  let xml = await zip.file(part).async("string");
  for (const [slot, hex] of Object.entries(THEME.colors)) {
    xml = xml.replace(new RegExp(`<a:${slot}>[\\s\\S]*?</a:${slot}>`), `<a:${slot}><a:srgbClr val="${hex}"/></a:${slot}>`);
  }
  xml = xml.replace(/<a:clrScheme name="[^"]*"/, `<a:clrScheme name="${THEME.name}"`);
  zip.file(part, xml);
  fs.writeFileSync(file, await zip.generateAsync({ type: "nodebuffer", compression: "DEFLATE" }));
}

pres.writeFile({ fileName: OUT }).then(async () => {
  await writeTheme(OUT);
  console.log("wrote", OUT);
});
