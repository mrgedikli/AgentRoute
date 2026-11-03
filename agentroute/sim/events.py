"""JSONL event log and topology snapshot.

The simulator writes every event as one JSON line; the visualisations only
read these files. Example lines:
    {"t": 12.3, "type": "hop", "pkt": 7, "from": 3, "to": 5, "method": "agentroute"}
    {"t": 14.1, "type": "deliver", "pkt": 7, "agent": 42, "hops": 4, "method": "agentroute"}
    {"t": 15.0, "type": "drop", "pkt": 9, "at": 11, "reason": "ttl", "method": "greedy"}
    {"t": 20.0, "type": "handover", "agent": 42, "from_cell": 2, "to_cell": 3}
    {"t": 0.5, "type": "adv", "from": 3, "to": 5, "n_vectors": 4}

Responsible: Ömer Faruk Gedikli
"""
import json
from pathlib import Path


class EventLog:
    def __init__(self, log_dir=None):
        self.dir = Path(log_dir) if log_dir else None
        self.enabled = self.dir is not None
        self.lines = []

    def log(self, **event):
        if not self.enabled:
            return
        if "t" in event:
            event["t"] = round(float(event["t"]), 5)
        self.lines.append(json.dumps(event, separators=(",", ":")))

    def write_topology(self, snapshot):
        if not self.enabled:
            return
        self.dir.mkdir(parents=True, exist_ok=True)
        with open(self.dir / "topology.json", "w") as f:
            json.dump(snapshot, f)

    def close(self, summary=None):
        if not self.enabled:
            return
        self.dir.mkdir(parents=True, exist_ok=True)
        with open(self.dir / "events.jsonl", "w") as f:
            f.write("\n".join(self.lines))
            f.write("\n")
        if summary is not None:
            with open(self.dir / "summary.json", "w") as f:
                json.dump(summary, f, indent=2)
