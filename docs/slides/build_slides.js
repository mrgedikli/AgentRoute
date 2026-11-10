// Builds docs/slides/AgentRoute.pptx (English slides, Turkish speaker notes, ~15 minutes, three speakers).
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
  emre: "Bekir Emre Sarıpınar · addressing, S-FIB and mobility",
  goktepe: "Bekir Göktepe · learning and evaluation",
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
// Turkish number formats, used only in the speaker notes
const tp = (x, d = 0) => (x == null ? "n/a" : `%${(x * 100).toFixed(d).replace(".", ",")}`);
const tn = (x) => (x == null ? "n/a" : Math.round(x).toLocaleString("tr-TR"));
const td = (x) => String(x).replace(".", ",");
const tk = (x) => kb(x).replace(".", ",");
const tabs = (p) => (p ? Math.abs(p.success_diff_points).toFixed(1).replace(".", ",") : "n/a");
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
  s.addNotes(`ÖMER. Herkese merhaba. Biz AgentRoute projemizi anlatacağız. Tek cümleyle: paketleri bir adrese değil, bir yeteneğe yönlendiriyoruz ve router'ların bu kararı öğrenmesinin işe yarayıp yaramadığını ölçüyoruz. Ben problemi ve genel resmi anlatacağım, Bekir Emre adresleme, S-FIB ve mobiliteyi, Bekir Göktepe de öğrenen kararı ve değerlendirmeyi anlatacak.`);
}

// 2 ---- where vs who can
{
  const s = content("Problem and big picture", "The Internet asks where; agents ask who can", "omer",
    `Bugünkü internet "nerede?" sorusuna göre çalışıyor. Bir sunucunun IP adresi var, biz de zaten bildiğimiz alan adlarını DNS ile bu adrese çeviriyoruz. Router'lar paketin içeriğine bakmaz, sadece adres önekine bakar. Postacı gibi düşünebiliriz: postacı size kimin yardım edebileceğini bilmez, sadece adrese götürür. AI agent'lar ise farklı bir soru soruyor: "bu işi kim yapabilir?" Sağdaki örnekte bir agent "bu fotoğraftaki arabaları bul" diyor. Bu işi yapacak agent'ın adını da yerini de bilmiyor. Üstelik bu sorular makine hızında soruluyor, agent sayısı çok büyük ve sürekli değişiyor. Agent'ların birçoğu telefon, araç ya da drone üstünde çalıştığı için bağlandıkları hücre de değişiyor.`);
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
    `Bu soruya bugün iki klasik cevap var. Birincisi registry, yani DNS benzeri bir kayıt sunucusu. Agent'lar sunucuya kayıt olur, her istek önce sunucuya gidip döner, ancak ondan sonra agent'a ulaşır. Simülasyonumuzda ${tn(big)} agent'ta bu ${ms(regT)} sürüyor, semantik yönlendirmede ise ${ms(arT)}. Sunucunun bulunduğu router düşerse keşif durur. Gerçi replika kullanmak bu sorunu büyük ölçüde çözüyor, bunu baştan söyleyelim. İkinci cevap flooding: hiç tablo tutmaz, isteği çevresindeki herkese sorar. Ama aynı ölçekte istek başına ${tk(flK)} trafik üretiyor, yönlendirmede bu ${tk(arK)}. Üçüncü zorluk mobilite: agent'larımızın yarısı hareket ediyor ve bu ölçekte saniyede yaklaşık ${Math.round(hoPerS)} handover oluyor. Bizim sorumuz şu: router'lar yetenekli agent'ı merkezi bir sunucu olmadan kendileri bulabilir mi, ve bu kararı öğrenmek işe yarar mı?`);
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
    `Fikir yeni değil, bunu baştan söyleyelim. 1999'da INS, niyete göre isimlendirmeyi uygulama seviyesinde yaptı. 2003'te pSearch, DHT üzerinde semantik arama yaptı. Son dönemdeki Internet of Agents çalışmaları ya HTTP üstüne yeni protokol katmanları ekliyor ya da keşif servisleri öneriyor. Bir IETF taslağı router'lara semantik yönlendirme tablosu koymayı öneriyor ama değerlendirme sunmuyor. Bize en yakın çalışma SPFR. SPFR paketi hop hop en baskın agent'a doğru yönlendiriyor, ama kuralı elle tasarlanmış, her agent için tabloda ayrı satır tutuyor ve kablolu topolojilerde değerlendirilmiş. Biz ise sıkıştırılmış, iki katmanlı bir tablo kullanıyoruz, kuralı öğrenmenin işe yarayıp yaramadığını test ediyoruz ve hücresel mobil bir ağda SPFR'nin kuralıyla karşılaştırıyoruz. NDN de isimle yönlendirir ama tam önek eşleşmesi ister, farklı kelimelerle sorulan bir istek orada bulunamaz.`);
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
    `Sistemi tek resimde görelim. İki şey oluyor. Birincisi kesikli oklar: agent'lar yeteneklerini duyuruyor, her router da kendi semantik tablosunu, yani S-FIB'ini dolduruyor. Bu tabloda her komşu için, o komşunun arkasında hangi yeteneklerin olduğu yazıyor. İkincisi düz oklar: görev paketi hedef adres yerine, isteğin anlamını temsil eden bir vektör taşıyor. Her router ya paketi yanındaki bir agent'a teslim ediyor ya da en uygun komşuya iletiyor. Alttaki kısım bir düğümün içini gösteriyor: paketteki vektör S-FIB ile karşılaştırılıyor, buna kuyruk doluluğu, link kalitesi, handover ve kalan TTL gibi yerel bilgiler ekleniyor, sonunda policy "burada teslim et" ya da "şu komşuya gönder" kararını veriyor. Yani karar yalnızca yerel bilgiyle veriliyor, merkezde kimse yok. Şimdi Bekir Emre adreslemeyi ve tabloyu anlatacak.`);
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
    `BEKİR EMRE. Önce adres. Her sağlayıcı yeteneğini kendi kelimeleriyle anlatıyor, bu yüzden her agent'ın kendine ait bir vektörü var. Bu vektör, o yeteneği anlatan cümlelerin MiniLM ile çıkarılan vektörlerinin rastgele ağırlıklı karışımı. Örneğin "find the cars in this photo" isteğinin nesne tespiti kartıyla benzerliği ${td(sim.example[0].cos)}, görüntü sınıflandırmayla ${td(sim.example[2].cos)}. Agent, benzerlik tau eşiğini, yani ${td(TAU.tau)} değerini geçerse işi kabul ediyor. Eşiği beklenen değere göre seçtik: doğru agent artı bir, yanlış agent eksi bir, kabul yoksa sıfır. Görülmemiş cümlelerde en benzer agent ${tp(TAU.test_top1)} oranında doğru sınıftan. ${tops.length} farklı encoder denedik, hepsi ${encRange} bandında kaldı, yani daha büyük bir model bunu çözmüyor. Sağdaki grafik nedenini gösteriyor: aynı sınıf ve farklı sınıf benzerlikleri üst üste biniyor.`);
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
    `Normal bir router "bu IP aralığı için şu kapıdan çık" der. Bizim router ise "bu komşunun arkasında şu yetenekler var" diyor. AVM'lerdeki koridor tabelası gibi düşünebilirsiniz. Tabloyu iki katmanlı yaptık. Bir komşuya doğrudan bağlı agent'lar için tek tek satır tutuyoruz. Daha uzaktakileri ise her hop'ta en fazla sekiz temsilci vektöre sıkıştırıyoruz, böylece mesaj boyutu agent sayısıyla büyümüyor. Bedelini ölçtük: greedy yönlendirme sadece özetlerle ${tp(v("k=8, no tier", "success_rate"))}, iki katmanlı tabloyla ${tp(v("k=8", "success_rate"))}, her agent için tam satırla ${tp(v("exact", "success_rate"))} başarı veriyor. Ama tam tablo saniyede ${tk(v("exact", "ctrl_kB_per_s"))} trafik istiyor, iki katmanlı tablo ise ${tk(v("k=8", "ctrl_kB_per_s"))}. Bir de teslim kuralı var: bir komşu açıkça daha iyi bir aday duyuruyorsa router paketi teslim etmeyip iletmeye devam ediyor.`);
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
    `Agent'lar bütün ağa değil, yalnızca R hop uzağa duyuru yapıyor. ${tn(1000)} agent'ta R eşittir ${r[0]} iken greedy başarısı ${tp(get("radius", "greedy", "success_rate", r[0]))} ve kontrol trafiği saniyede ${tk(get("radius", "greedy", "ctrl_kB_per_s", r[0]))}. R eşittir ${r[r.length - 1]} iken başarı ${tp(get("radius", "greedy", "success_rate", r[r.length - 1]))}, trafik ${tk(get("radius", "greedy", "ctrl_kB_per_s", r[r.length - 1]))}. En iyi nokta R eşittir 2, başarı ${tp(get("radius", "greedy", "success_rate", 2))}. Bunun ötesinde başarı artmıyor, trafik de neredeyse sabit kalıyor, çünkü her link aynı az sayıda temsilci vektörü taşıyor. Bu yüzden R eşittir 2 kullandık, SPFR'nin kontrol ufku da aynı.`);
  methodLines(s, "radius", "success_rate", methods, { x: 0.6, y: 1.45, w: 6.0, h: 5.0, scale: 100, fmt: '0"%"', min: 0,
    title: "Success rate", xTitle: "advertisement radius R (hops)", yTitle: "success" });
  s.addChart(pres.charts.LINE, [{ name: "Same S-FIB for all these methods", labels: r.map(String),
    values: S.radius.methods.greedy.ctrl_kB_per_s }], chartOpts({ x: 6.75, y: 1.45, w: 6.0, h: 5.0, colors: [INK2], min: 0,
    title: "Control traffic (kB/s)", xTitle: "advertisement radius R (hops)", yTitle: "kB/s" }));
}

// 9 ---- mobility
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
  const s = content("Addressing and S-FIB", "Mobility costs messages, not success", "emre",
    `Mobilite de tam bu tabloyla ilgili. Bir telefon hücre değiştirince eski gNB onu siliyor, yeni gNB R hop içinde duyuruyor. Bir router bu güncellemeyi ancak kendi özetlerinden biri gerçekten değişiyorsa ileri aktarıyor, yani bütün ağ yeniden flood edilmiyor. ${tn(n)} agent'ta handover başına yaklaşık ${Math.round(top.msgs_per_handover)} mesaj gidiyor. Handover trafiği saniyede ${tk(top.handover_kB_per_s)}, periyodik yenileme ise ${tk(top.refresh_kB_per_s)}. Başarı ise hıza neredeyse hiç bağlı değil. Saniyede ${hi} metre hızda, 150 metrelik küçük hücrelerde bile greedy ${tp(get("mobility_small", "greedy", "success_rate", hi))}, üç replikalı registry ${tp(get("mobility_small", "registry3", "success_rate", hi))}, çünkü bir agent sadece 50 milisaniye kesinti yaşıyor. Yani modelimizde mobilite bir ulaşılabilirlik değil, maliyet sorunu. 500 metrelik hücrelerde, durağandan saniyede ${hi} metreye çıkınca S-FIB'in kontrol trafiği ${tk(lo)} değerinden ${tk(up)} değerine, üç replikalı registry'ninki ${tk(rlo)} değerinden ${tk(rup)} değerine çıkıyor.`);
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

// 10 ---- what limits success
{
  const d = S.scale.drops || {};
  const oracle = gr("oracle_best", mid);
  const s = content("Addressing and S-FIB", "Most failures come from matching, not routing", "emre",
    `Peki başarıyı ne sınırlıyor? ${tn(mid)} agent'ta her agent'ı bilen bir yöntem bile isteklerin ancak ${tp(oracle)} kadarını çözebilir, çünkü geri kalanında en benzer agent yanlış sınıftan ya da kimse eşiği geçmiyor. İleride grafiklerde göreceğiniz kesikli tavan çizgisi bu. Greedy ${tp(gr("success_rate", mid))}, merkezi registry ${tp(rg("success_rate", mid))}, flooding ${tp(fl("success_rate", mid))} başarı veriyor. Kalan hatalar yanlış eşleşmeler ve TTL bitene kadar eşleşme bulamayan paketler. Greedy kuralının da bir sınırı var: en benzer komşu tıkalıysa ya da bir hop ötede daha iyisi varsa ne olacak? Burada teslim mi edelim, devam mı edelim? Bu kararı Bekir Göktepe anlatacak.`);
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

// 11 ---- DQN
pres.addSection({ title: "Learning and evaluation" });
{
  const s = content("Learning and evaluation", "One shared DQN: deliver here, or forward where?", "goktepe",
    `BEKİR GÖKTEPE. Bu kararı bir DQN veriyor. Router'ların komşu sayısı farklı olduğu için ağ her seçeneği ayrı ayrı puanlıyor: girdi o seçeneğin 15 özelliği, çıktı tek bir Q değeri. Seçenekler komşular ve "burada teslim et", yani ağ durup durmayacağına da karar veriyor. Tüm router'lar aynı ağı paylaşıyor, eğitim simülasyonda offline yapılıyor. Ödül her kararda gecikmeye bağlı küçük bir ceza, doğru teslimde artı bir, düşme ya da yanlış agent'ta eksi bir. Eğitimde Double DQN, replay buffer ve target network kullandık.`);
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

// 12 ---- learning curve
if (train) {
  const best = train.val_success[bestIdx];
  const bestRet = train.val_return[bestIdx];
  const v = verb(bestRet, Math.max(train.greedy_val_return, train.load_val_return), 0.01);
  const first = train.val_return[0];
  const s = content("Learning and evaluation", `Validation: the DQN ${v} both same-table rules`, "goktepe",
    `Bu eğri, doğrulama senaryolarında keşif kapalıyken ölçüldü. Eğitim getirisini göstermiyoruz, çünkü keşif azaldıkça o zaten yükselir. DQN'in getirisi ${td(first.toFixed(2))} ile başlıyor, en iyi değeri ${td(bestRet.toFixed(2))}. Aynı ödülle greedy ${td(train.greedy_val_return.toFixed(2))}, yük duyarlı greedy ${td(train.load_val_return.toFixed(2))}. Yani aynı tabloyu kullanan iki kuralı da geçiyor.`);
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

// 13 ---- setup
{
  const s = content("Learning and evaluation", "Evaluation setup", "goktepe",
    `Sonuçlar SimPy ile yazdığımız simülatörden geliyor: hücreler, core ağ ve cloud, en fazla 450 router. İstekler eğitimde hiç görülmemiş 150 cümle. Bilerek güçlü rakipler ekledik: yük duyarlı kural, SPFR tarzı kural, üç replikalı registry ve semantik DHT. Chord tanım gereği hiçbir şey bulamıyor, onu sadece referans olarak tutuyoruz. Her nokta 10 seed'in ortalaması.`);
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
  const s = content("Learning and evaluation", `Scaling to ${num(big)} agents`, "goktepe",
    `Solda başarı var. ${tn(big)} agent'ta eşleşme tavanı ${tp(gr("oracle_best"))}, DQN ${tp(ar("success_rate"))}, greedy ${tp(gr("success_rate"))}, SPFR tarzı ${tp(sp("success_rate"))}, flooding ${tp(fl("success_rate"))}, merkezi registry ${tp(rg("success_rate"))}. Sağda kontrol trafiği var. Sürelere bakarsak bu ölçekte yönlendirme ${ms(gr("time_ms"))}, registry ${ms(rg("time_ms"))}, flooding ${ms(fl("time_ms"))}.`);
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
  const s = content("Learning and evaluation", "Who is cheaper depends on the request rate", "goktepe",
    `Kontrol trafiği saniye başına, sorgu trafiği istek başına ödeniyor, bu yüzden toplam maliyet istek hızına bağlı. Flooding'in kontrol trafiği olmadığı için istekler seyrekken o kazanıyor. ${cross ? `Saniyede yaklaşık ${cross} istekten sonra yönlendirmeden pahalıya geliyor.` : "Denediğimiz aralıkta flooding daha ucuz kalıyor."} Registry ise her hızda en ucuz, bunu açıkça söyleyelim. Onun ödediği bedel gecikme ve sunuculara bağımlılık.`);
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
  const s = content("Learning and evaluation", "Robustness: failures and load", "goktepe",
    `Router'ların ${tp(fmax)} kadarı düştüğünde greedy ${tp(get("failure", "greedy", "success_rate", fmax))}, üç replikalı registry ${tp(get("failure", "registry3", "success_rate", fmax))} başarı veriyor, bu ortalamada on denemenin birinde üç replika birden düşüyor. Tek sunuculu registry, sunucu ayaktaysa ${tp(rb.up)}, düşerse ${tp(rb.down)}. Replika bunu büyük ölçüde çözüyor. Sağda yük artışı var: en yüksek yükte DQN ${tp(get("load", "agentroute", "success_rate", lmax))}, greedy ${tp(get("load", "greedy", "success_rate", lmax))}, flooding ${tp(get("load", "flooding", "success_rate", lmax))}.`);
  successWithCeiling(s, "failure", ALL, { x: 0.6, y: 1.45, w: 6.0, h: 5.05,
    labelFn: (x) => `${Math.round(x * 100)}%`, title: "Success vs failed routers", xTitle: "failed routers" });
  successWithCeiling(s, "load", ALL, { x: 6.75, y: 1.45, w: 6.0, h: 5.05, title: "Success vs network load", xTitle: "load factor", legend: false });
}

// 17 ---- demo video(s)
function videoSlide(file, title, notes) {
  const video = path.join(FIG, `${file}.mp4`);
  const poster = path.join(FIG, `${file}_poster.png`);
  if (!fs.existsSync(video)) return;
  const s = content("Learning and evaluation", title, "goktepe", notes);
  const cover = fs.existsSync(poster) ? `data:image/png;base64,${fs.readFileSync(poster).toString("base64")}` : undefined;
  s.addMedia({ type: "video", path: video, x: 1.0, y: 1.4, w: 11.33, h: 5.35, ...(cover ? { cover } : {}) });
}
videoSlide("agentroute_demo", "Demo: a request routed by meaning",
  `Bu kayıt gerçek bir simülasyon logundan üretildi. Önce duyurular tabloları dolduruyor, sonra bir istek hop hop uygun agent'a gidiyor, sonra bir telefon hücre değiştiriyor ve sadece yakındaki girdiler güncelleniyor.`);
{
  const f = path.join(FIG, "greedy_vs_agentroute.json");
  if (fs.existsSync(f)) {
    const c = JSON.parse(fs.readFileSync(f, "utf8"));
    const say = (o) => (o.type === "deliver"
      ? `${o.hops} hop'ta ve ${td(o.time_ms)} ms içinde ${o.agent_class} agent'ına teslim ediliyor`
      : `${o.hops} hop sonra başarısız oluyor (${o.reason.replace("_", " ")})`);
    videoSlide("greedy_vs_agentroute", "One selected example: greedy vs learned",
      `Şunu açıkça söyleyelim: bu tek bir seçilmiş örnek, ortalama değil. Turuncu halkalar yoğun router'lar. "${c.text}" isteği greedy ile ${say(c.greedy)}, öğrenen politikayla ${say(c.agentroute)}.`);
  }
}

// 19 ---- takeaways
{
  const s = pres.addSlide({ masterName: "TITLE_DARK", sectionTitle: "Learning and evaluation" });
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
  s.addNotes(`Özetle üç şey söyleyebiliriz. Birincisi, anlama göre yönlendirme merkezi sunucu olmadan çalışıyor. İkincisi, bedava değil: registry bayt olarak her zaman daha ucuz, trafik en önemli ölçütse registry seçilmeli. Üçüncüsü, öğrenmenin katkısı küçük ama ölçülebilir: ${tn(big)} agent'ta aynı tabloda DQN, greedy'den ${tabs(dqnVsGreedy)} puan, yük duyarlı kuraldan ${tabs(dqnVsLoad)} puan iyi, tam tablolu SPFR tarzı kuralın ise ${tabs(dqnVsSpfr)} puan gerisinde. Gecikmede anlamlı bir fark yok. Asıl tavanı yönlendirme değil, anlamsal eşleşme belirliyor. Gerçekçi radyo modeliyle başarı 8 ila 21 puan düşüyor, ayrıntısı raporda. Teşekkür ederiz, sorularınızı alalım.`);
}

// 20 ---- backup: ablations
if (S.ablation_summary && S.ablation_header) {
  pres.addSection({ title: "Backup" });
  const s = content("Backup", "Backup: S-FIB content and header size", "goktepe",
    `Yedek slayt. Solda tablo içeriğinin başarıya etkisi, sağda intent başlığının 1.536 bayttan (float32) 388 bayta (int8) ya da 48 bayta (binary) sıkıştırılması var.`);
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
