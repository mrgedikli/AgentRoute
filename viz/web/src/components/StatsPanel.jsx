import { useState } from "react";
import * as d3 from "d3";
import { REASON_LABEL } from "../data.js";

// Headline numbers of the run + a D3 bar chart of why requests failed.
export default function StatsPanel({ run }) {
  const s = run.summary;
  const [hover, setHover] = useState(null);
  const reasons = Object.keys(REASON_LABEL)
    .map((k) => ({ key: k, label: REASON_LABEL[k], v: s[`drop_${k}`] || 0 }))
    .filter((d) => d.v > 0.001)
    .sort((a, b) => b.v - a.v);
  const w = 340;
  const rowH = 26;
  const h = reasons.length * rowH + 10;
  const x = d3.scaleLinear().domain([0, d3.max(reasons, (d) => d.v) || 1]).range([0, w - 190]);

  return (
    <div className="stats">
      <div className="tiles">
        <div className="tile"><span className="tile-label">Success</span>
          <span className="tile-value">{(s.success_rate * 100).toFixed(1)}%</span></div>
        <div className="tile"><span className="tile-label">Mean time</span>
          <span className="tile-value">{s.time_ms != null && !Number.isNaN(s.time_ms)
            ? `${s.time_ms.toFixed(1)} ms` : "–"}</span></div>
        <div className="tile"><span className="tile-label">Hops</span>
          <span className="tile-value">{s.hops != null && !Number.isNaN(s.hops) ? s.hops.toFixed(2) : "–"}</span></div>
        <div className="tile"><span className="tile-label">Requests</span>
          <span className="tile-value">{s.n_queries}</span></div>
      </div>
      <h3>Why requests fail</h3>
      <svg viewBox={`0 0 ${w} ${h}`} className="bars" role="img" aria-label="Failure reasons">
        {reasons.map((d, i) => (
          <g key={d.key} transform={`translate(0, ${i * rowH})`}
            onMouseEnter={() => setHover(d.key)} onMouseLeave={() => setHover(null)}>
            <rect x={0} y={0} width={w} height={rowH} fill="transparent" />
            <text x={0} y={rowH / 2 + 4} className="bar-label">{d.label}</text>
            <path d={roundedBar(150, 6, Math.max(x(d.v), 2), rowH - 12)}
              className={hover === d.key ? "bar hover" : "bar"} />
            <text x={150 + x(d.v) + 6} y={rowH / 2 + 4} className="bar-value">
              {(d.v * 100).toFixed(1)}%</text>
          </g>
        ))}
      </svg>
      {!reasons.length && <p className="muted">No failed requests.</p>}
    </div>
  );
}

// bar with a 4px rounded data end, square at the baseline
function roundedBar(x0, y0, w, h) {
  const r = Math.min(4, w / 2, h / 2);
  return `M${x0},${y0} H${x0 + w - r} Q${x0 + w},${y0} ${x0 + w},${y0 + r} V${y0 + h - r}
    Q${x0 + w},${y0 + h} ${x0 + w - r},${y0 + h} H${x0} Z`;
}
