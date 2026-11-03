"""Cost of a handover in the control plane: incremental S-FIB update vs a full re-advertisement.

For each network size we count the S-FIB messages that handovers trigger
(withdraw at the old cell + announce at the new cell, only where a summary
changes) and compare them with one full advertisement round, i.e. what a
naive scheme would re-flood after every move.

Written with AI assistance (experiment tooling).
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from agentroute.config import RESULTS, load_config  # noqa: E402
from agentroute.sim.simulator import Simulator  # noqa: E402


def main():
    quick = "--quick" in sys.argv
    sizes = [1000] if quick else [1000, 3000, 10000]
    seeds = [1] if quick else [1, 2, 3]
    out = {}
    for n in sizes:
        rows = []
        for seed in seeds:
            cfg = load_config(overrides={"agents": {"n_agents": n, "speed_mps": 5.0}})
            sim = Simulator(cfg, "greedy", seed=seed)
            s = sim.run()
            full_round, _ = sim.adv.periodic_messages()
            rows.append({"handovers": s["handovers"], "update_msgs": s["update_msgs"],
                         "full_round": full_round, "routers": s["n_routers"]})
        ho = sum(r["handovers"] for r in rows)
        out[str(n)] = {
            "routers": rows[0]["routers"],
            "handovers_per_s": round(ho / len(rows) / cfg["sim"]["duration_s"], 1),
            "msgs_per_handover": round(sum(r["update_msgs"] for r in rows) / max(ho, 1), 1),
            "full_round_msgs": round(sum(r["full_round"] for r in rows) / len(rows)),
        }
        out[str(n)]["share_of_full_round"] = round(out[str(n)]["msgs_per_handover"] / out[str(n)]["full_round_msgs"], 4)
        print(n, out[str(n)], flush=True)
    path = RESULTS / "raw" / ("handover_cost_quick.json" if quick else "handover_cost.json")
    path.write_text(json.dumps(out, indent=2))
    print("wrote", path)


if __name__ == "__main__":
    main()
