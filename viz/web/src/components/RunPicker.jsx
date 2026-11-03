import { useState } from "react";
import { METHOD_LABEL } from "../data.js";

// Choose one of the exported runs, or drop topology.json + events.jsonl files.
export default function RunPicker({ runs, current, onPick, onFiles }) {
  const [over, setOver] = useState(false);
  return (
    <div className="picker">
      <label>
        Run
        <select value={current || ""} onChange={(e) => onPick(e.target.value)}>
          {!runs.length && <option value="">no exported runs</option>}
          {runs.map((r) => (
            <option key={r.name} value={r.name}>
              {r.name} - {METHOD_LABEL[r.method] || r.method}
              {r.success_rate != null ? ` (${(r.success_rate * 100).toFixed(0)}%)` : ""}
            </option>
          ))}
        </select>
      </label>
      <div className={`drop ${over ? "over" : ""}`}
        onDragOver={(e) => { e.preventDefault(); setOver(true); }}
        onDragLeave={() => setOver(false)}
        onDrop={(e) => { e.preventDefault(); setOver(false); onFiles([...e.dataTransfer.files]); }}>
        or drop <code>topology.json</code> + <code>events.jsonl</code> here
      </div>
    </div>
  );
}
