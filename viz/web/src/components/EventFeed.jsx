import { eventIndexAt } from "../data.js";

const SHOWN = new Set(["query", "hop", "deliver", "drop", "handover", "fail", "withdraw"]);

function describe(e) {
  switch (e.type) {
    case "query": return `request ${e.pkt} from agent ${e.agent}: "${e.text}"`;
    case "hop": return `request ${e.pkt}: ${e.from} → ${e.to}`;
    case "deliver": return `request ${e.pkt} delivered to agent ${e.agent} (${e.hops} hops)`;
    case "drop": return `request ${e.pkt} dropped at ${e.at ?? "-"} (${e.reason})`;
    case "handover": return `agent ${e.agent}: cell ${e.from_cell} → ${e.to_cell}`;
    case "fail": return `router ${e.node} failed`;
    case "withdraw": return `withdraw ${e.from} → ${e.to}`;
    default: return e.type;
  }
}

// The last events before the current time; click a request to follow it.
export default function EventFeed({ run, t, onSelect }) {
  const end = eventIndexAt(run.events, t);
  const rows = [];
  for (let i = end - 1; i >= 0 && rows.length < 40; i--) {
    const e = run.events[i];
    if (SHOWN.has(e.type)) rows.push(e);
  }
  return (
    <div className="feed">
      {rows.map((e, i) => (
        <button key={`${e.t}-${i}`} className={`feed-row ${e.type}`}
          onClick={() => e.pkt != null && onSelect(e.pkt)} disabled={e.pkt == null}>
          <span className="feed-t">{e.t.toFixed(3)}</span>
          <span className={`tag ${e.type}`}>{e.type}</span>
          <span className="feed-text">{describe(e)}</span>
        </button>
      ))}
      {!rows.length && <p className="muted">No events yet - press play.</p>}
    </div>
  );
}
