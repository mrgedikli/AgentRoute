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
  flooding: { name: "Flooding", color: "EDA100" },
  registry: { name: "Central registry", color: "E87BA4" },
  chord: { name: "Chord (exact)", color: "008300" },
};
const ALL = Object.keys(M);
const SEM = ["agentroute", "agentroute_gnn", "greedy"];
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
const ar = (metric, v = big) => get("scale", "agentroute", metric, v);
const gr = (metric, v = big) => get("scale", "greedy", metric, v);
const fl = (metric, v = big) => get("scale", "flooding", metric, v);
const rg = (metric, v = big) => get("scale", "registry", metric, v);
const ch = (metric, v = big) => get("scale", "chord", metric, v);
const sim = S.similarity;
const train = S.train_mlp;
const bestIdx = train ? train.val_return.indexOf(Math.max(...train.val_return)) : -1;
const speedups = S.scale.values.filter((v) => v >= 300)
  .map((v) => 1 - get("scale", "agentroute", "time_ms", v) / get("scale", "greedy", "time_ms", v));
const speedRange = `${Math.round(Math.min(...speedups) * 100)}\u2013${Math.round(Math.max(...speedups) * 100)}%`;
const lmaxAll = S.load.values[S.load.values.length - 1];
const heavyVerb = verb(get("load", "agentroute", "success_rate", lmaxAll), get("load", "greedy", "success_rate", lmaxAll));

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
  s.addNotes("OMER. One sentence: we route packets to a capability instead of an address, and every router learns the best next hop by itself. Introduce the three parts: Omer - the problem, Bekir Emre - addressing and the semantic FIB, Bekir Goktepe - learning, mobility and the evaluation.");
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
  const regT = rg("time_ms"); const arT = ar("time_ms");
  const flM = fl("msgs_per_query"); const arM = ar("msgs_per_query");
  const hoPerS = ar("handovers") / 30;
  const s = content("Problem and big picture", "Two classic answers break at scale", "omer",
    `Option one is a central registry, like DNS: every agent registers, every request goes to one server. In our simulation with ${num(big)} agents a request through the registry needs ${ms(regT)} on average, against ${ms(arT)} for AgentRoute, because registrations and requests queue at one server - and if its router fails, discovery stops. Option two is flooding: fine in a small network, but at ${num(big)} agents it costs ${num(flM)} messages per request. And on top of that, half of our agents move: about ${Math.round(hoPerS)} handovers per second.`);
  const cards = [
    { n: 1, head: "Central registry", body: "Every registration and request passes one server: a bottleneck and a single point of failure.",
      value: ms(regT), label: `per request at ${num(big)} agents (AgentRoute: ${ms(arT)})`, color: M.registry.color },
    { n: 2, head: "Flooding", body: "Ask every router within a TTL: works in small networks, explodes in large ones.",
      value: num(flM), label: `messages per request at ${num(big)} agents (AgentRoute: ${num(arM)})`, color: M.flooding.color },
    { n: 3, head: "Mobility", body: "Agents on phones, cars and drones keep changing cell, so any location table is soon stale.",
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
  text(s, "AgentRoute: no central server, no flooding, and a handover only updates its neighbourhood",
    0.9, 5.9, 11.6, 0.75, { fontSize: 18, bold: true, color: "1C5CAB", valign: "middle", fontFace: "Cambria" });
}

// 4 ---- related work
{
  const s = content("Problem and big picture", "Related work stays above the network layer", "omer",
    "Recent proposals add an agent-specific protocol layer above HTTP [1], or capability discovery services and registries [3], [4]. The closest work, SPFR [2], forwards hop by hop with a hand-designed potential field. We change the network layer itself: the address of a destination is what it can do, the next hop is learned, and we evaluate it in a mobile cellular / edge topology with handovers.");
  const head = (t) => ({ text: t, options: { bold: true, color: WHITE, fill: { color: NAVY } } });
  const rows = [
    [head("Work"), head("Where it lives"), head("Matching"), head("Next hop"), head("Mobile evaluation")],
    ["[1] Layered protocol for the Internet of Agents (2025)", "above HTTP", "agent descriptions", "–", "–"],
    ["[3] Agent discovery in the Internet of Agents (2025)", "discovery service", "registry / search", "–", "–"],
    ["[4] IETF draft-wang-dmsc-drisac (2026)", "registration service", "semantic discovery", "–", "–"],
    ["[2] SPFR: semantic potential field routing (2026)", "network layer", "semantic", "heuristic", "–"],
  ].map((r, i) => (i === 0 ? r : r.map((c) => ({ text: c, options: { color: INK } }))));
  const ours = ["AgentRoute (ours)", "network layer", "semantic S-FIB", "learned (DQN, GNN)", "cellular / edge, handovers"]
    .map((c) => ({ text: c, options: { bold: true, color: "1C5CAB", fill: { color: TINT } } }));
  rows.push(ours);
  s.addTable(rows, { x: 0.6, y: 1.6, w: 12.1, colW: [4.3, 2.0, 2.1, 1.75, 1.95], fontSize: 14, fontFace: "Calibri",
    border: { type: "solid", color: GRID, pt: 1 }, rowH: 0.62, valign: "middle", margin: 0.08 });
  text(s, "References: [1] Fleming et al., arXiv:2511.19699 · [2] arXiv:2608.25396 · [3] Guo et al., arXiv:2511.19113 · [4] IETF draft, Aug. 2026",
    0.6, 6.1, 12.1, 0.4, { fontSize: 11, color: MUTED });
}

// 5 ---- one picture
{
  const s = content("Problem and big picture", "AgentRoute in one picture", "omer",
    "Two things happen. (1) Dashed: agents advertise their capabilities, and every router fills its semantic FIB - for each neighbour, which capabilities lie behind it. (2) Solid: a task packet carries an intent embedding instead of a destination address; each router forwards it to the best neighbour until an agent that can do the task accepts it. Inside every node, the S-FIB match and the local network state go into a DQN that picks the next hop. Bekir Emre now explains the addressing and the S-FIB.");
  const nodes = [
    { t: "Requesting agent", b: "on a mobile UE,\nmoves between cells", hl: false },
    { t: "gNB + edge node", b: "AgentRoute node\nS-FIB + DQN", hl: true },
    { t: "Core router", b: "AgentRoute node\nS-FIB + DQN", hl: true },
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
    ["Intent embedding", "carried in the packet\n(MiniLM, 384-d)"],
    ["S-FIB match", "cosine similarity of the\nintent to each neighbour"],
    ["Local state", "queue load, link quality,\nhandovers, TTL"],
    ["DQN policy", "one Q-value per neighbour,\npicks the next hop"],
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
  const s = content("Addressing and S-FIB", "A capability address is a vector, not a host", "emre",
    `BEKIR EMRE. Each agent has a capability card: a description and two example requests. We encode every sentence with the pre-trained MiniLM sentence encoder and average them: that 384-dimensional vector plus the agent ID is the address. Sentences with similar meaning get similar vectors. Example: 'find the cars in this photo' has cosine ${sim.example[0].cos} with the object-detection card, but only ${sim.example[2].cos} with image classification. An agent accepts a task when the cosine is at least tau = ${TAU.tau}, tuned on training paraphrases. On unseen test paraphrases the right class is the most similar one ${pct(TAU.test_top1)} of the time. The chart shows why this is hard: same-class and other-class similarities overlap.`);
  text(s, "Agent card → MiniLM → mean of the sentence vectors", 0.6, 1.5, 6.0, 0.4, { fontSize: 16, bold: true });
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
  text(s, `τ = ${TAU.tau} · top-1 class accuracy ${pct(TAU.test_top1)} · false accept ${pct(TAU.test_false_accept, 1)}`,
    6.95, 6.1, 5.8, 0.4, { fontSize: 13, color: INK2, align: "center" });
}

// 7 ---- S-FIB
{
  const mean_ = get("ablation_summary", "greedy", "success_rate", "mean");
  const k4 = get("ablation_summary", "greedy", "success_rate", "k=4");
  const exact = get("ablation_summary", "greedy", "success_rate", "exact");
  const s = content("Addressing and S-FIB", "The S-FIB: what lies behind each neighbour", "emre",
    `A normal router says 'for this IP range, use that port'. Our router says 'behind this neighbour there are these kinds of capabilities' - like the sign at a mall corridor: 'electronics and books this way'. Averaging all vectors behind a neighbour blurs different capabilities, so we keep k = 4 representative vectors per neighbour (k-means) and score a neighbour by its best representative. The table has a fixed size per neighbour: it does not grow with the number of agents. In the ablation, greedy forwarding reaches ${pct(mean_)} with a plain mean, ${pct(k4)} with k = 4 and ${pct(exact)} with the uncompressed table.`);
  const head = (t) => ({ text: t, options: { bold: true, color: WHITE, fill: { color: NAVY } } });
  const rows = [
    [head("Neighbour"), head("k = 4 representative capabilities"), head("Min hops")],
    ["gNB 7 (Xn)", "object detection · OCR · face recognition · image captioning", "1"],
    ["gNB 9 (Xn)", "translation · summarization · speech-to-text · grammar", "2"],
    ["Core 12 (backhaul)", "cluster centres of everything within R hops, incl. the cloud", "2"],
  ].map((r, i) => (i === 0 ? r : r.map((c) => ({ text: c, options: { color: INK } }))));
  s.addTable(rows, { x: 0.6, y: 1.6, w: 7.3, colW: [1.8, 4.4, 1.1], fontSize: 14, fontFace: "Calibri",
    border: { type: "solid", color: GRID, pt: 1 }, rowH: 0.72, valign: "middle", margin: 0.08 });
  text(s, "Illustrative S-FIB of one gNB + edge router", 0.6, 4.6, 7.3, 0.35, { fontSize: 12, color: MUTED });
  box(s, 8.3, 1.6, 4.43, 4.9, TINT);
  text(s, "IP FIB vs S-FIB", 8.6, 1.8, 3.9, 0.45, { fontSize: 18, bold: true, fontFace: "Cambria" });
  bullets(s, ["IP: prefix → output port", "S-FIB: neighbour → capability summary",
    "Score of a neighbour = best cosine with its representatives",
    "k-means keeps distinct capabilities apart; a mean blurs them", "Fixed size per neighbour, independent of the agent count"],
  8.6, 2.35, 3.9, 4.0, { fontSize: 14 });
  stat(s, pct(mean_), "greedy success with a mean summary", 0.6, 5.05, 2.3, M.greedy.color);
  stat(s, pct(k4), "with k = 4 representatives", 3.1, 5.05, 2.3, M.greedy.color);
  stat(s, pct(exact), "with the full table", 5.6, 5.05, 2.3, M.greedy.color);
}

// 8 ---- radius
{
  const r = S.radius.values;
  const s = content("Addressing and S-FIB", "Advertisements reach R hops, not the whole network", "emre",
    `Agents do not advertise to the whole network, only R hops away. Larger R means better information but more control messages. With ${num(1000)} agents, going from R = ${r[0]} to R = ${r[r.length - 1]} moves greedy from ${pct(get("radius", "greedy", "success_rate", r[0]))} to ${pct(get("radius", "greedy", "success_rate", r[r.length - 1]))} success, while control messages grow from ${num(get("radius", "greedy", "ctrl_msgs", r[0]))} to ${num(get("radius", "greedy", "ctrl_msgs", r[r.length - 1]))} per run. We use R = 3 as the default.`);
  methodLines(s, "radius", "success_rate", SEM, { x: 0.6, y: 1.45, w: 6.0, h: 5.0, scale: 100, fmt: '0"%"', min: 0,
    title: "Success rate", xTitle: "advertisement radius R (hops)", yTitle: "success" });
  s.addChart(pres.charts.LINE, [{ name: "Same S-FIB for all semantic methods", labels: r.map(String),
    values: S.radius.methods.greedy.ctrl_msgs }], chartOpts({ x: 6.75, y: 1.45, w: 6.0, h: 5.0, colors: [INK2], min: 0,
    title: "Control messages per run", xTitle: "advertisement radius R (hops)", yTitle: "messages" }));
}

// 9 ---- greedy limits
{
  const d = S.scale.drops || {};
  const g = d.greedy || {};
  const s = content("Addressing and S-FIB", "Greedy works until the best neighbour is busy", "emre",
    `Greedy forwarding sends the packet to the most similar neighbour at every hop. It works: with ${num(mid)} agents it delivers ${pct(gr("success_rate", mid))} of requests, close to the central registry (${pct(rg("success_rate", mid))}) without any central server. But greedy only looks at similarity. In the same runs ${pct(g.queue, 1)} of its requests are lost in overflowing queues of busy routers and ${pct(g.link, 1)} on bad links. So the question is: what if the most similar neighbour is congested, or the device is in the middle of a handover? Bekir Goktepe continues.`);
  stat(s, pct(gr("success_rate", mid)), `greedy success with ${num(mid)} agents`, 0.6, 1.6, 3.6, M.greedy.color);
  stat(s, pct(rg("success_rate", mid)), "central registry, same runs", 0.6, 3.15, 3.6, M.registry.color);
  const reasons = [["wrong_agent", "Wrong agent accepted"], ["not_found", "No match found"], ["ttl", "TTL expired"],
    ["queue", "Queue overflow"], ["link", "Link loss"], ["handover", "Agent in handover"], ["stale_location", "Stale location"],
    ["registry_queue", "Registry overloaded"], ["node_down", "Node down"]];
  const methods = ["agentroute", "greedy", "flooding", "registry"].filter((m) => d[m]);
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
  text(s, "What if the most similar neighbour is congested, or the device is in the middle of a handover?",
    0.9, 5.7, 11.6, 0.65, { fontSize: 20, bold: true, fontFace: "Cambria", color: "1C5CAB", valign: "middle" });
}

// 10 ---- DQN
pres.addSection({ title: "Learning, mobility, evaluation" });
{
  const s = content("Learning, mobility, evaluation", "One shared DQN scores every neighbour", "goktepe",
    "BEKIR GOKTEPE. The DQN replaces the greedy rule. Because routers have different numbers of neighbours, the network does not output one value per action: it scores each neighbour separately - input is that neighbour's feature vector, output is one Q-value - and the packet goes to the highest. All routers share one network, trained offline in the simulator and copied to every node. Reward per hop is minus the normalised delay, plus a bonus on delivery and a penalty on any drop; the scales are normalised so that the agent neither drops packets early nor wanders forever. Training is Double DQN with replay and a target network; the next-state value is the max Q over the next router's neighbours, which is Q-routing with a neural network. Like navigation apps: the straight line is not always the fastest road.");
  text(s, "Features of one neighbour (14)", 0.6, 1.5, 4.2, 0.4, { fontSize: 16, bold: true });
  const feats = ["S-FIB similarity: max, mean, gap to best", "match above τ, hop distance", "queue occupancy (hello)",
    "link quality and delay", "neighbour in handover", "TTL left, already visited", "node type: gNB / core / cloud"];
  feats.forEach((f, i) => {
    box(s, 0.6, 2.0 + i * 0.56, 4.2, 0.46, PANEL);
    text(s, f, 0.78, 2.07 + i * 0.56, 3.9, 0.34, { fontSize: 13, color: INK });
  });
  arrow(s, 4.9, 3.9, 5.5, 3.9, INK2);
  box(s, 5.55, 2.85, 2.6, 2.1, TINT, "2A78D6");
  text(s, "Shared MLP", 5.7, 3.05, 2.3, 0.45, { fontSize: 18, bold: true, align: "center", fontFace: "Cambria" });
  text(s, "14 → 64 → 64 → 1\nsame weights in\nevery router", 5.7, 3.55, 2.3, 1.2, { fontSize: 13, color: INK2, align: "center" });
  arrow(s, 8.2, 3.9, 8.8, 3.9, INK2);
  const qs = [0.55, 0.9, 0.35];
  qs.forEach((q, i) => {
    const y = 2.95 + i * 0.62;
    text(s, `Q(n${i + 1})`, 8.9, y + 0.05, 0.8, 0.36, { fontSize: 13, color: INK2 });
    s.addShape(pres.shapes.RECTANGLE, { x: 9.7, y: y + 0.08, w: 2.2 * q, h: 0.32,
      fill: { color: i === 1 ? "2A78D6" : "B4B2A9" }, line: { type: "none" } });
  });
  text(s, "argmax → next hop n2", 8.9, 4.85, 3.8, 0.4, { fontSize: 14, bold: true, color: "1C5CAB" });
  box(s, 5.55, 5.45, 7.18, 1.2, PANEL);
  text(s, [
    { text: "Reward  ", options: { bold: true } },
    { text: "per hop −(0.05 + delay / 100 ms) · delivered +1 · dropped −1", options: { breakLine: true } },
    { text: "Training  ", options: { bold: true } },
    { text: "Double DQN, replay 50k, target net, ε 1 → 0.05, 300 random scenarios" },
  ], 5.75, 5.6, 6.9, 0.95, { fontSize: 13, color: INK });
}

// 11 ---- learning curve
if (train) {
  const g = S.train_gnn;
  const best = train.val_success[bestIdx];
  const bestT = train.val_time_ms[bestIdx];
  const v = verb(best, train.greedy_val_success, 0.005);
  const faster = bestT < train.greedy_val_time_ms - 0.5;
  const title = `Training: the DQN ${v} greedy${faster ? " and delivers faster" : ""}`;
  const s = content("Learning, mobility, evaluation", title, "goktepe",
    `Training curve on fixed validation scenarios, measured every 10 episodes with exploration switched off. The greedy line is the reference. We keep the weights with the best validation return, at episode ${train.episode[bestIdx]}: success ${pct(best, 1)} versus ${pct(train.greedy_val_success, 1)} for greedy, and ${bestT.toFixed(1)} ms versus ${train.greedy_val_time_ms.toFixed(1)} ms completion time. Honest reading: the learned policy does not find many more agents - matching quality limits that - but it routes around busy routers and bad links, which shows up as time.`);
  const labels = train.episode.map(String);
  const series = [{ name: M.agentroute.name, labels, values: train.val_success.map((x) => x * 100) }];
  const colors = [M.agentroute.color];
  if (g && g.episode.length === train.episode.length) { series.push({ name: M.agentroute_gnn.name, labels, values: g.val_success.map((x) => x * 100) }); colors.push(M.agentroute_gnn.color); }
  series.push({ name: "Greedy (reference)", labels, values: labels.map(() => train.greedy_val_success * 100) });
  colors.push(M.greedy.color);
  s.addChart(pres.charts.LINE, series, chartOpts({ x: 0.6, y: 1.45, w: 6.0, h: 5.0, colors, fmt: '0"%"',
    title: "Validation success", xTitle: "training episode", yTitle: "success", extra: { lineDataSymbolSize: 5 } }));
  const tseries = [{ name: M.agentroute.name, labels, values: train.val_time_ms }];
  const tcolors = [M.agentroute.color];
  if (g && g.episode.length === train.episode.length) { tseries.push({ name: M.agentroute_gnn.name, labels, values: g.val_time_ms }); tcolors.push(M.agentroute_gnn.color); }
  tseries.push({ name: "Greedy (reference)", labels, values: labels.map(() => train.greedy_val_time_ms) });
  tcolors.push(M.greedy.color);
  s.addChart(pres.charts.LINE, tseries, chartOpts({ x: 6.75, y: 1.45, w: 6.0, h: 5.0, colors: tcolors, min: 0,
    title: "Validation completion time (ms)", xTitle: "training episode", yTitle: "ms", extra: { lineDataSymbolSize: 5 } }));
}

// 12 ---- mobility
{
  const sp = S.mobility.values;
  const hi = sp[sp.length - 1];
  const hc = JSON.parse(fs.readFileSync(path.join(ROOT, "results", "raw", "handover_cost.json"), "utf8"));
  const sizes = Object.keys(hc).map(Number).sort((a, b) => a - b);
  const top = hc[String(sizes[sizes.length - 1])];
  const s = content("Learning, mobility, evaluation", "A handover only updates its neighbourhood", "goktepe",
    `When a phone changes cell, the old gNB withdraws its entries and the new gNB announces them, only within R hops, and a message is sent only where an advertised summary really changes; the whole network is not re-flooded. Measured: one handover costs ${sizes.map((n) => `${hc[n].msgs_per_handover} messages at ${num(n)} agents`).join(", ")} - roughly constant - while one full advertisement round grows from ${num(hc[sizes[0]].full_round_msgs)} to ${num(top.full_round_msgs)} messages. At ${num(sizes[sizes.length - 1])} agents a handover costs ${pct(top.share_of_full_round, 1)} of a full round, with ${top.handovers_per_s} handovers per second. The chart: success as agents move faster; at ${hi} m/s AgentRoute delivers ${pct(get("mobility", "agentroute", "success_rate", hi))}, greedy ${pct(get("mobility", "greedy", "success_rate", hi))}, the registry ${pct(get("mobility", "registry", "success_rate", hi))}. Mobility costs every method only 1-2 points because handovers take 50 ms and the updates spread within milliseconds.`);
  box(s, 0.6, 1.5, 4.6, 5.0, PANEL);
  text(s, "Incremental S-FIB update", 0.9, 1.7, 4.0, 0.45, { fontSize: 18, bold: true, fontFace: "Cambria" });
  circleNum(s, 1, 0.9, 2.35, CRIT, 0.42);
  text(s, "Old cell withdraws the agent within R hops", 1.45, 2.38, 3.6, 0.6, { fontSize: 14 });
  circleNum(s, 2, 0.9, 3.05, GOOD, 0.42);
  text(s, "New cell announces it within R hops", 1.45, 3.08, 3.6, 0.6, { fontSize: 14 });
  circleNum(s, 3, 0.9, 3.75, "6B6A66", 0.42);
  text(s, "Messages only where a summary really changes", 1.45, 3.78, 3.6, 0.6, { fontSize: 14 });
  stat(s, String(top.msgs_per_handover), `messages per handover at ${num(sizes[sizes.length - 1])} agents`, 0.9, 4.6, 2.0, "1C5CAB");
  stat(s, pct(top.share_of_full_round, 1), `of a full re-advertisement (${num(top.full_round_msgs)} messages)`, 3.0, 4.6, 2.1, INK2);
  methodLines(s, "mobility", "success_rate", ALL, { x: 5.45, y: 1.45, w: 7.3, h: 5.05, scale: 100, fmt: '0"%"', min: 0,
    title: `Success vs speed (${num(1000)} agents)`, xTitle: "mobile agent speed (m/s)", yTitle: "success" });
}

// 13 ---- setup
{
  const s = content("Learning, mobility, evaluation", "Evaluation setup", "goktepe",
    "Discrete-event simulator in Python with SimPy and NetworkX. gNB + edge routers on a cell grid, a core network and a cloud; the number of cells grows with the number of agents, up to 450 routers. Agents: 40 percent fixed edge agents, 50 percent mobile with random waypoint, 10 percent in the cloud. Capability supply is long-tailed (Zipf): a few capabilities are common, most are rare. Requests use 150 paraphrases never seen in training. Five methods plus the GNN variant, five seeds per point, 95 percent confidence intervals. Everything runs on a laptop CPU.");
  const cards = [
    ["Topology", "gNB + edge cells, core grid, cloud; 9 → 400 cells, up to 450 routers; queues, bursty hotspots, lossy links"],
    ["Agents", "40% fixed edge, 50% mobile (random waypoint, handover with hysteresis), 10% cloud; Zipf capability supply"],
    ["Requests", "150 unseen paraphrases of 50 capability classes, 10 requests/s, TTL 16"],
    ["Baselines", "central registry (DNS-like), TTL-limited flooding, Chord exact match, greedy semantic (same S-FIB)"],
    ["Metrics", "discovery success, completion time, hops, control + query messages"],
    ["Runs", "SimPy + NetworkX, 5 seeds per point, 95% CI, 100 → 10,000 agents, laptop CPU"],
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
  const v = verb(ar("success_rate"), gr("success_rate"));
  const s = content("Learning, mobility, evaluation", `Scaling to ${num(big)} agents`, "goktepe",
    `Left: success rate from 100 to ${num(big)} agents. At ${num(big)} agents AgentRoute delivers ${pct(ar("success_rate"))} (it ${v} greedy at ${pct(gr("success_rate"))}), flooding ${pct(fl("success_rate"))}, the registry ${pct(rg("success_rate"))}, and Chord finds nothing, because a paraphrase hashes to a different key - that is the reference that shows why semantic matching is needed. Right: messages per request on a log scale. Flooding grows to ${num(fl("msgs_per_query"))} messages per request; AgentRoute needs ${num(ar("msgs_per_query"))}, most of it periodic advertisements. Completion time: AgentRoute ${ms(ar("time_ms"))}, registry ${ms(rg("time_ms"))}.`);
  const lab = (x) => (x >= 1000 ? `${x / 1000}K` : String(x));
  methodLines(s, "scale", "success_rate", ALL, { x: 0.6, y: 1.45, w: 6.0, h: 5.05, scale: 100, fmt: '0"%"', min: 0,
    labelFn: lab, title: "Discovery success", xTitle: "number of agents", yTitle: "success" });
  methodLines(s, "scale", "msgs_per_query", ALL, { x: 6.75, y: 1.45, w: 6.0, h: 5.05, log: true, labelFn: lab,
    title: "Messages per request (log scale)", xTitle: "number of agents", yTitle: "messages", legend: false });
}

// 15 ---- robustness
{
  const fv = S.failure.values;
  const fmax = fv[fv.length - 1];
  const lv = S.load.values;
  const lmax = lv[lv.length - 1];
  const s = content("Learning, mobility, evaluation", "Robustness: failures and load", "goktepe",
    `Left: a fraction of routers fails at one third of the run. With ${pct(fmax)} failed routers AgentRoute delivers ${pct(get("failure", "agentroute", "success_rate", fmax))}, greedy ${pct(get("failure", "greedy", "success_rate", fmax))}, the registry ${pct(get("failure", "registry", "success_rate", fmax))} - it is a single point of failure, and in some seeds its router is among the failed ones. Right: the load factor scales both requests and background traffic. At load ${lmax} AgentRoute delivers ${pct(get("load", "agentroute", "success_rate", lmax))} versus ${pct(get("load", "greedy", "success_rate", lmax))} for greedy and ${pct(get("load", "registry", "success_rate", lmax))} for the registry: under the heaviest load the learned policy ${heavyVerb} greedy, because its detours around busy routers get long and more packets run out of TTL. This is our main open issue.`);
  methodLines(s, "failure", "success_rate", ALL, { x: 0.6, y: 1.45, w: 6.0, h: 5.05, scale: 100, fmt: '0"%"', min: 0,
    labelFn: (x) => `${Math.round(x * 100)}%`, title: "Success vs failed routers", xTitle: "failed routers", yTitle: "success" });
  methodLines(s, "load", "success_rate", ALL, { x: 6.75, y: 1.45, w: 6.0, h: 5.05, scale: 100, fmt: '0"%"', min: 0,
    title: "Success vs network load", xTitle: "load factor", yTitle: "success", legend: false });
}

// 16 ---- demo video(s)
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
    videoSlide("greedy_vs_agentroute", "Same request: greedy vs learned next hop",
      `Same network, same moment, same request ('${c.text}'), taken from the two demo logs. Orange halos are routers busy with background traffic at that moment. With greedy forwarding the request ${say(c.greedy)}; with the learned next hop it ${say(c.agentroute)}. This is one real example, not an average - the averages are on the previous slides.`);
  }
}

// 17 ---- takeaways
{
  const s = pres.addSlide({ masterName: "TITLE_DARK", sectionTitle: "Learning, mobility, evaluation" });
  s.addText("Takeaways", { placeholder: "title" });
  const items = [
    `Capability addresses + S-FIB find agents by meaning: ${pct(ar("success_rate"))} at ${num(big)} agents, where exact-match Chord finds ${pct(ch("success_rate"))}`,
    `No central server and no flood: ${num(ar("msgs_per_query"))} messages per request vs ${num(fl("msgs_per_query"))} for flooding; ${ms(ar("time_ms"))} vs ${ms(rg("time_ms"))} for the registry`,
    `One shared DQN learns the next hop: as successful as greedy and ${speedRange} faster, but it ${heavyVerb} greedy under the heaviest load`,
  ];
  items.forEach((t, i) => {
    circleNum(s, i + 1, 0.8, 3.45 + i * 0.85, "2A78D6", 0.5);
    s.addText(t, { x: 1.5, y: 3.43 + i * 0.85, w: 11.0, h: 0.6, isTextBox: true, margin: 0, fontSize: 17,
      color: WHITE, valign: "middle" });
  });
  s.addText("Future work: on-device fine-tuning · signed capability advertisements · UDP overlay prototype · better encoders", {
    x: 0.8, y: 6.2, w: 11.7, h: 0.5, isTextBox: true, margin: 0, fontSize: 14, color: LIGHT });
  s.addNotes("Close with the one sentence: packets are addressed to what an agent can do, and routers learn where to send them. Then future work: fine-tune the shared model on each router, signed advertisements against agents that lie about their capabilities, an overlay implementation over UDP like early IPv6 tunnels, and better sentence encoders - matching quality is the main limit today. Thank you, questions.");
}

// 18 ---- backup: ablations
if (S.ablation_summary && S.ablation_header) {
  pres.addSection({ title: "Backup" });
  const s = content("Backup", "Backup: S-FIB summary and header size", "goktepe",
    "Backup slide. Left: what the per-neighbour summary costs in success. Right: compressing the intent header from 1,536 bytes (float32) to 388 bytes (int8) or 48 bytes (binary signs).");
  const ORDER = { ablation_summary: ["mean", "k=2", "k=4", "k=8", "exact"], ablation_header: ["float32", "int8", "binary"] };
  const mk = (exp, methods) => methods.map((m) => {
    const vals = S[exp].values;
    const order = ORDER[exp].filter((v) => vals.includes(v));
    return { name: M[m].name, labels: order.map(String),
      values: order.map((v) => S[exp].methods[m].success_rate[vals.indexOf(v)] * 100) };
  });
  s.addChart(pres.charts.BAR, mk("ablation_summary", ["agentroute", "greedy"]), chartOpts({ x: 0.6, y: 1.45, w: 6.0, h: 5.05,
    colors: [M.agentroute.color, M.greedy.color], fmt: '0"%"', min: 0, title: "S-FIB summary per neighbour",
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
