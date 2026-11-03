import { useState } from "react";
import * as d3 from "d3";

// Per-request delay waterfall: one row per hop, bar = time spent on that hop
// (link delay + queueing at the next router).
export default function Waterfall({ run, pid, color }) {
  const [hover, setHover] = useState(null);
  const p = run.packets.find((x) => x.pid === pid);
  if (!p) return <p className="muted">Select a request (click a packet or an event).</p>;
  const t0 = p.q.t;
  const rows = p.segs.map((s, i) => ({ i, label: s.label, start: (s.t0 - t0) * 1000,
    dur: Math.max((s.t1 - s.t0) * 1000, 0.05) }));
  const total = (p.t1 - t0) * 1000;
  const w = 380;
  const rowH = 22;
  const left = 96;
  const h = rows.length * rowH + 28;
  const x = d3.scaleLinear().domain([0, Math.max(total, 1)]).range([left, w - 12]);
  const ticks = x.ticks(4);
  const agent = p.ok ? run.agents.get(p.out.agent) : null;

  return (
    <div className="waterfall">
      <p className="intent">&ldquo;{p.q.text}&rdquo;</p>
      <p className="muted small">
        {p.ok ? `Delivered to agent ${agent.id} (${agent.class_name})`
          : `Dropped: ${p.out.reason}`} &middot; {total.toFixed(1)} ms &middot; {rows.length - 1} hops
      </p>
      <svg viewBox={`0 0 ${w} ${h}`} role="img" aria-label="Delay per hop">
        {ticks.map((tk) => (
          <g key={tk}>
            <line x1={x(tk)} x2={x(tk)} y1={0} y2={h - 20} className="grid" />
            <text x={x(tk)} y={h - 6} className="axis-label" textAnchor="middle">{tk} ms</text>
          </g>
        ))}
        {rows.map((r) => (
          <g key={r.i} transform={`translate(0, ${r.i * rowH})`}
            onMouseEnter={() => setHover(r.i)} onMouseLeave={() => setHover(null)}>
            <rect x={0} y={0} width={w} height={rowH} fill="transparent" />
            <text x={0} y={rowH / 2 + 4} className="bar-label">{r.label}</text>
            <rect x={x(r.start)} y={5} width={Math.max(x(r.start + r.dur) - x(r.start), 2)}
              height={rowH - 10} rx={3} fill={color} opacity={hover === r.i ? 1 : 0.8} />
            {hover === r.i && (
              <text x={Math.min(x(r.start + r.dur) + 4, w - 60)} y={rowH / 2 + 4} className="bar-value">
                {r.dur.toFixed(2)} ms</text>
            )}
          </g>
        ))}
      </svg>
    </div>
  );
}
