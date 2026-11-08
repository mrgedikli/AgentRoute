"""Cost of mobility in the control plane.

For each network size we measure, per second and per handover, what the S-FIB
updates cost and put that next to two reference points: the periodic refresh
of the same network and the update traffic of a replicated registry.

Written with AI assistance (experiment tooling).
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from agentroute.config import RESULTS, load_config  # noqa: E402
from agentroute.sim.simulator import Simulator  # noqa: E402


def run(method, n, seed):
    cfg = load_config(overrides={"agents": {"n_agents": n, "speed_mps": 5.0}})
    sim = Simulator(cfg, method, seed=seed)
    s = sim.run()
    return sim, s, cfg["sim"]["duration_s"]


def main():
    quick = "--quick" in sys.argv
    sizes = [1000] if quick else [1000, 3000, 10000]
    seeds = [1] if quick else [1, 2, 3]
    out = {}
    for n in sizes:
        rows = []
        for seed in seeds:
            sim, s, dur = run("greedy", n, seed)
            full_msgs, full_bytes = sim.adv.round_cost()
            reg_sim, reg, _ = run("registry3", n, seed)
            rows.append({"ho": s["handovers"], "upd": s["update_msgs"], "routers": s["n_routers"],
                         "full_msgs": full_msgs, "full_kB": full_bytes / 1000.0, "dur": dur,
                         "delta_B": sim.adv.delta_bytes()})
        ho = sum(r["ho"] for r in rows)
        dur, period = rows[0]["dur"], 10.0
        upd_per_s = sum(r["upd"] for r in rows) / len(rows) / dur
        full_per_s = sum(r["full_msgs"] for r in rows) / len(rows) / period
        out[str(n)] = {
            "routers": rows[0]["routers"],
            "handovers_per_s": round(ho / len(rows) / dur, 1),
            "msgs_per_handover": round(sum(r["upd"] for r in rows) / max(ho, 1), 2),
            "handover_msgs_per_s": round(upd_per_s, 1),
            "handover_kB_per_s": round(upd_per_s * rows[0]["delta_B"] / 1000.0, 1),
            "refresh_msgs_per_s": round(full_per_s, 1),
            "refresh_kB_per_s": round(sum(r["full_kB"] for r in rows) / len(rows) / period, 1),
        }
        print(n, out[str(n)], flush=True)
    path = RESULTS / "raw" / ("handover_cost_quick.json" if quick else "handover_cost.json")
    path.write_text(json.dumps(out, indent=2))
    print("wrote", path)


if __name__ == "__main__":
    main()
