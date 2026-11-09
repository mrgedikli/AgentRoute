import { useCallback, useEffect, useRef, useState } from "react";
import EventFeed from "./components/EventFeed.jsx";
import RunPicker from "./components/RunPicker.jsx";
import StatsPanel from "./components/StatsPanel.jsx";
import Timeline from "./components/Timeline.jsx";
import TopologyView from "./components/TopologyView.jsx";
import Waterfall from "./components/Waterfall.jsx";
import { METHOD_LABEL, buildRun, loadIndex, loadRun, parseJsonl } from "./data.js";

const METHOD_COLOR = {
  agentroute: "#2a78d6",
  agentroute_gnn: "#eb6834",
  greedy: "#1baf7a",
  greedy_load: "#0f8a8a",
  spfr: "#6250d6",
  flooding: "#eda100",
  registry: "#e87ba4",
  registry3: "#a8437a",
  chord: "#008300",
  sdht: "#7a6a5a",
};

export default function App() {
  const [runs, setRuns] = useState([]);
  const [runName, setRunName] = useState(null);
  const [run, setRun] = useState(null);
  const [error, setError] = useState(null);
  const [t, setT] = useState(0);
  const [playing, setPlaying] = useState(false);
  const [speed, setSpeed] = useState(0.05);
  const [direction, setDirection] = useState(1);
  const [selected, setSelected] = useState(null);
  const [onlyDelivered, setOnlyDelivered] = useState(false);
  const last = useRef(null);

  useEffect(() => {
    loadIndex().then((idx) => {
      setRuns(idx.runs || []);
      const first = (idx.runs || []).find((r) => r.method === "agentroute") || (idx.runs || [])[0];
      if (first) setRunName(first.name);
    });
  }, []);

  useEffect(() => {
    if (!runName) return;
    setError(null);
    loadRun(runName)
      .then((r) => { setRun(r); setT(0); setSelected(null); })
      .catch((e) => setError(`Could not load ${runName}: ${e.message}`));
  }, [runName]);

  // playback loop: simulated time advances by real time x speed
  useEffect(() => {
    if (!playing || !run) return undefined;
    let id;
    const step = (now) => {
      if (last.current != null) {
        const dt = (now - last.current) / 1000;
        setT((old) => {
          const next = old + direction * dt * speed;
          if (next <= 0 || next >= run.duration) {
            setPlaying(false);
            return Math.min(Math.max(next, 0), run.duration);
          }
          return next;
        });
      }
      last.current = now;
      id = requestAnimationFrame(step);
    };
    id = requestAnimationFrame(step);
    return () => { cancelAnimationFrame(id); last.current = null; };
  }, [playing, speed, direction, run]);

  const onFiles = useCallback(async (files) => {
    const byName = Object.fromEntries(files.map((f) => [f.name, f]));
    if (!byName["topology.json"] || !byName["events.jsonl"]) {
      setError("Please drop both topology.json and events.jsonl.");
      return;
    }
    const topo = JSON.parse(await byName["topology.json"].text());
    const events = parseJsonl(await byName["events.jsonl"].text());
    const summary = byName["summary.json"] ? JSON.parse(await byName["summary.json"].text()) : null;
    setRun(buildRun(topo, events, summary, "dropped files"));
    setRunName(null);
    setT(0);
    setSelected(null);
    setError(null);
  }, []);

  const followPacket = (pid) => {
    const p = run.packets.find((x) => x.pid === pid);
    setSelected(pid);
    if (p) {
      setT(Math.max(p.t0 - 0.002, 0));
      setSpeed(0.01);
      setDirection(1);
      setPlaying(true);
    }
  };

  const color = run ? METHOD_COLOR[run.method] || "#2a78d6" : "#2a78d6";
  const packetList = run ? run.packets.filter((p) => !onlyDelivered || p.ok) : [];

  return (
    <div className="app">
      <header>
        <div>
          <h1>AgentRoute log player</h1>
          <p className="muted">Replays a simulation log: packets addressed to capabilities, hop by hop.</p>
        </div>
        <RunPicker runs={runs} current={runName} onPick={setRunName} onFiles={onFiles} />
      </header>
      {error && <p className="error">{error}</p>}
      {!run && !error && (
        <p className="muted">Export a run first: <code>python viz/export_web_data.py</code></p>
      )}
      {run && (
        <main>
          <section className="left">
            <div className="panel-title">
              <span className="swatch" style={{ background: color }} />
              {METHOD_LABEL[run.method] || run.method} &middot; {run.topo.meta.n_agents} agents
              &middot; R = {run.topo.meta.radius}
            </div>
            <TopologyView run={run} t={t} color={color} selected={selected} onSelect={followPacket} />
            <Timeline t={t} duration={run.duration} playing={playing} speed={speed}
              direction={direction} onTime={(v) => { setT(v); setPlaying(false); }}
              onPlay={setPlaying} onSpeed={setSpeed} onDirection={setDirection} />
            <p className="legend muted small">
              <span className="key gnb" /> gNB + edge router <span className="key core" /> core router
              <span className="key agent" /> agent <span className="key busy" /> busy router
              <span className="key ring-g" /> announce / serving agent <span className="key ring-r" /> withdraw
              &nbsp;&middot; scroll to zoom, drag to pan
            </p>
          </section>
          <section className="right">
            <div className="card">
              <h2>Run summary</h2>
              <StatsPanel run={run} />
            </div>
            <div className="card">
              <h2>Request</h2>
              <div className="row">
                <select value={selected ?? ""} onChange={(e) => followPacket(Number(e.target.value))}>
                  <option value="">choose a request...</option>
                  {packetList.map((p) => (
                    <option key={p.pid} value={p.pid}>
                      #{p.pid} {p.ok ? "✓" : "✗"} {p.q.text.slice(0, 48)}
                    </option>
                  ))}
                </select>
                <label className="small">
                  <input type="checkbox" checked={onlyDelivered}
                    onChange={(e) => setOnlyDelivered(e.target.checked)} /> delivered only
                </label>
              </div>
              <Waterfall run={run} pid={selected} color={color} />
            </div>
            <div className="card">
              <h2>Events</h2>
              <EventFeed run={run} t={t} onSelect={followPacket} />
            </div>
          </section>
        </main>
      )}
    </div>
  );
}
