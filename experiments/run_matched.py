"""Paired comparisons on the same requests.

Mean completion time over successful requests is biased: a method that gives up
on slow requests looks fast. Here two methods are compared only on the requests
that both delivered. Differences in success are computed per seed and given
with a bootstrap 95% interval. Writes results/raw/matched.json.

Written with AI assistance (experiment tooling).
"""
import json
import sys
from multiprocessing import Pool
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import numpy as np  # noqa: E402

from agentroute.config import RESULTS, load_config  # noqa: E402
from common import SEEDS, parse_args  # noqa: E402

SCENARIOS = {
    "1000 agents, load 1": {"agents": {"n_agents": 1000}},
    "1000 agents, load 4": {"agents": {"n_agents": 1000}, "sim": {"load": 4.0}},
    "10000 agents, load 1": {"agents": {"n_agents": 10000}},
}
METHODS = ["agentroute", "agentroute_gnn", "greedy", "greedy_load", "spfr"]
PAIRS = [("agentroute", "greedy"), ("agentroute", "greedy_load"), ("agentroute", "spfr"),
         ("agentroute_gnn", "agentroute"), ("greedy_load", "greedy")]


def run(job):
    import torch
    torch.set_num_threads(1)
    from agentroute.sim.simulator import Simulator
    name, over, method, seed = job
    sim = Simulator(load_config(overrides=over), method, seed=seed)
    sim.run()
    return name, method, seed, {r["pid"]: (r["success"], r["time"] * 1000.0, r["hops"]) for r in sim.results}


def bootstrap_ci(x, rng, n=2000):
    means = [np.mean(rng.choice(x, size=len(x))) for _ in range(n)]
    return float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))


def main():
    args = parse_args(__doc__)
    seeds = SEEDS[:2] if args.quick else SEEDS
    scenarios = dict(list(SCENARIOS.items())[:1]) if args.quick else SCENARIOS
    jobs = [(name, over, m, s) for name, over in scenarios.items() for m in METHODS for s in seeds]
    with Pool(args.workers) as pool:
        rows = pool.map(run, jobs)
    res = {(n, m, s): r for n, m, s, r in rows}
    rng = np.random.default_rng(0)
    out = {}
    for name in scenarios:
        out[name] = {}
        for a, b in PAIRS:
            ta, tb, ha, hb, diff, only_a, only_b = [], [], [], [], [], 0, 0
            for s in seeds:
                ra, rb = res[(name, a, s)], res[(name, b, s)]
                common = sorted(set(ra) & set(rb))
                diff.append(np.mean([ra[p][0] for p in common]) - np.mean([rb[p][0] for p in common]))
                for p in common:
                    if ra[p][0] and rb[p][0]:
                        ta.append(ra[p][1])
                        tb.append(rb[p][1])
                        ha.append(ra[p][2])
                        hb.append(rb[p][2])
                    elif ra[p][0]:
                        only_a += 1
                    elif rb[p][0]:
                        only_b += 1
            low, high = bootstrap_ci(np.array(diff) * 100, rng)
            out[name][f"{a} vs {b}"] = {
                "both_delivered": len(ta),
                "time_ms": [round(float(np.mean(ta)), 2), round(float(np.mean(tb)), 2)],
                "hops": [round(float(np.mean(ha)), 2), round(float(np.mean(hb)), 2)],
                "median_time_diff_ms": round(float(np.median(np.array(ta) - np.array(tb))), 2),
                "only_first_delivered": only_a, "only_second_delivered": only_b,
                "success_diff_points": round(float(np.mean(diff)) * 100, 2),
                "success_diff_ci95": [round(low, 2), round(high, 2)],
            }
            print(name, a, "vs", b, out[name][f"{a} vs {b}"], flush=True)
    path = RESULTS / "raw" / ("matched_quick.json" if args.quick else "matched.json")
    path.write_text(json.dumps(out, indent=2))
    print("wrote", path)


if __name__ == "__main__":
    main()
