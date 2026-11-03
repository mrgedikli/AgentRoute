import { useEffect, useMemo, useRef, useState } from "react";
import * as d3 from "d3";
import { agentPos, busyAt, packetPos } from "../data.js";

const LINK_STYLE = {
  xn: { w: 1, dash: null, cls: "link" },
  backhaul: { w: 0.8, dash: null, cls: "link" },
  core: { w: 1.8, dash: null, cls: "link-core" },
  cloud: { w: 1.8, dash: "5 4", cls: "link-core" },
};

// Network view: routers, links, agents, packets in flight, handovers.
// D3 provides the scales and the zoom behaviour; React renders the SVG.
export default function TopologyView({ run, t, color, selected, onSelect }) {
  const svgRef = useRef(null);
  const [transform, setTransform] = useState(d3.zoomIdentity);
  const width = 900;
  const height = 640;

  const { sx, sy, r } = useMemo(() => {
    const xs = run.topo.nodes.map((n) => n.x);
    const ys = run.topo.nodes.map((n) => n.y);
    const pad = 260;
    const dx = d3.max(xs) - d3.min(xs) + 2 * pad;
    const dy = d3.max(ys) - d3.min(ys) + 2 * pad;
    const k = Math.min(width / dx, height / dy);
    const ox = (width - dx * k) / 2;
    const oy = (height - dy * k) / 2;
    return {
      sx: (x) => ox + (x - d3.min(xs) + pad) * k,
      sy: (y) => height - (oy + (y - d3.min(ys) + pad) * k), // y axis up, like the plots
      r: k,
    };
  }, [run]);

  useEffect(() => {
    const zoom = d3.zoom().scaleExtent([0.5, 12]).on("zoom", (e) => setTransform(e.transform));
    const svg = d3.select(svgRef.current);
    svg.call(zoom);
    return () => svg.on(".zoom", null);
  }, []);

  const spacing = 500;
  const nodes = run.topo.nodes;
  const active = run.packets.filter((p) => t >= p.t0 && t <= p.t1 + 0.05);
  const sel = selected != null ? run.packets.find((p) => p.pid === selected) : null;
  const flashes = run.handovers.filter((h) => t >= h.t && t - h.t < 0.6);
  const agentList = [...run.agents.values()];

  return (
    <svg ref={svgRef} viewBox={`0 0 ${width} ${height}`} className="topology" role="img"
      aria-label="Network topology with packets in flight">
      <g transform={transform.toString()}>
        {nodes.filter((n) => n.kind === "gnb").map((n) => (
          <circle key={`cell${n.id}`} cx={sx(n.x)} cy={sy(n.y)} r={spacing * 0.56 * r} className="cell" />
        ))}
        {run.topo.links.map((l, i) => {
          const s = LINK_STYLE[l.kind];
          const [x1, y1] = run.pos.get(l.u);
          const [x2, y2] = run.pos.get(l.v);
          return (
            <line key={i} x1={sx(x1)} y1={sy(y1)} x2={sx(x2)} y2={sy(y2)} className={s.cls}
              strokeWidth={s.w} strokeDasharray={s.dash} />
          );
        })}
        {nodes.filter((n) => busyAt(run, n.id, t)).map((n) => (
          <circle key={`busy${n.id}`} cx={sx(n.x)} cy={sy(n.y)} r={22} className="busy" />
        ))}
        {sel && sel.segs.slice(1).map((s, i) => (
          <line key={`sel${i}`} x1={sx(s.a[0])} y1={sy(s.a[1])} x2={sx(s.b[0])} y2={sy(s.b[1])}
            stroke={color} strokeWidth={4} strokeLinecap="round" opacity={0.85} />
        ))}
        {nodes.map((n) => {
          const x = sx(n.x);
          const y = sy(n.y);
          if (n.kind === "gnb") {
            return <rect key={n.id} x={x - 7} y={y - 7} width={14} height={14} rx={2} className="gnb">
              <title>{`gNB + edge router ${n.id}`}</title></rect>;
          }
          if (n.kind === "core") {
            return <circle key={n.id} cx={x} cy={y} r={9} className="core">
              <title>{`core router ${n.id}`}</title></circle>;
          }
          const pts = d3.range(6).map((i) => {
            const a = (Math.PI / 3) * i + Math.PI / 6;
            return `${x + 13 * Math.cos(a)},${y + 13 * Math.sin(a)}`;
          }).join(" ");
          return <g key={n.id}><polygon points={pts} className="core"><title>cloud</title></polygon>
            <text x={x} y={y + 28} className="node-label" textAnchor="middle">Cloud</text></g>;
        })}
        {agentList.map((a) => {
          const [x, y] = agentPos(run, a.id, t);
          return <circle key={`a${a.id}`} cx={sx(x)} cy={sy(y)} r={2.6} className="agent">
            <title>{`agent ${a.id}: ${a.class_name} (${a.kind})`}</title></circle>;
        })}
        {flashes.map((h, i) => (
          <g key={`ho${i}`}>
            <circle cx={sx(run.pos.get(h.from_cell)[0])} cy={sy(run.pos.get(h.from_cell)[1])} r={20}
              className="ring-withdraw" />
            <circle cx={sx(run.pos.get(h.to_cell)[0])} cy={sy(run.pos.get(h.to_cell)[1])} r={20}
              className="ring-announce" />
          </g>
        ))}
        {active.map((p) => {
          const xy = packetPos(p, t);
          if (!xy) return null;
          return (
            <circle key={`p${p.pid}`} cx={sx(xy[0])} cy={sy(xy[1])} r={p.pid === selected ? 7 : 5}
              fill={color} className="packet" onClick={() => onSelect(p.pid)}>
              <title>{`request ${p.pid}: ${p.q.text}`}</title>
            </circle>
          );
        })}
        {sel && sel.ok && (() => {
          const [x, y] = agentPos(run, sel.out.agent, sel.out.t);
          return <circle cx={sx(x)} cy={sy(y)} r={11} className="ring-announce" />;
        })()}
      </g>
    </svg>
  );
}
