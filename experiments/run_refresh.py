"""Full vs incremental soft-state refresh of the S-FIBs.

Variants of the control plane (forwarding is the same in all of them):
  full              every table is sent again each period (what the report uses)
  full_fixed        same, with the handover update restricted to rows of its own tier
  incremental       only changed rows are sent, a digest on quiet links
  incremental_cold  same, but k-means starts from scratch instead of the old centres

Writes results/raw/refresh_<scenario>.csv and results/raw/refresh.json (paired
differences over seeds with bootstrap 95% intervals).

Written with AI assistance (experiment tooling).
"""
import json

import numpy as np
import pandas as pd
from common import RESULTS, parse_args, sweep

METHODS = ["agentroute", "agentroute_gnn", "greedy", "greedy_load", "spfr"]
CORE = ["agentroute", "greedy", "spfr"]
VARIANTS = {
    "full": {"sfib": {"refresh_mode": "full", "tier_aware_delta": False}},
    "full_fixed": {"sfib": {"refresh_mode": "full", "tier_aware_delta": True}},
    "incremental": {"sfib": {"refresh_mode": "incremental", "tier_aware_delta": True}},
    "incremental_cold": {"sfib": {"refresh_mode": "incremental", "tier_aware_delta": True,
                                  "warm_start": False}},
}
MAIN = ["full", "full_fixed", "incremental"]
ONE_K = {"agents": {"n_agents": 1000}}


def ci(x, rng):
    if len(x) < 2:
        return [float(x.mean()), float(x.mean())]
    boot = rng.choice(x, size=(4000, len(x))).mean(axis=1)
    return [float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))]


def paired(df, a, b, label, rng):
    """Mean of variant b minus variant a, seed by seed, for every method."""
    out = {}
    for m in sorted(df["method"].unique()):
        x = df[(df["method"] == m) & (df[label] == a)].set_index("seed")
        y = df[(df["method"] == m) & (df[label] == b)].set_index("seed")
        seeds = x.index.intersection(y.index)
        d = (y.loc[seeds, "success_rate"] - x.loc[seeds, "success_rate"]).to_numpy() * 100
        out[m] = {"success_diff_pts": round(float(d.mean()), 2),
                  "ci95": [round(v, 2) for v in ci(d, rng)],
                  "a_kB_s": round(float(x.loc[seeds, "ctrl_kB_per_s_steady"].mean()), 1),
                  "b_kB_s": round(float(y.loc[seeds, "ctrl_kB_per_s_steady"].mean()), 1)}
    return out


def table(df, label):
    cols = ["success_rate", "precision", "time_ms", "hops", "ctrl_kB_per_s_steady",
            "refresh_kB_per_s_steady", "update_kB_per_s_steady"]
    t = df.groupby([label, "method"])[cols].mean().round(3)
    print(t.to_string(), flush=True)
    return {f"{k[0]}|{k[1]}": v for k, v in t.to_dict("index").items()}


def main():
    args = parse_args(__doc__)
    seeds10 = [1] if args.quick else list(range(1, 11))
    seeds5 = [1] if args.quick else list(range(1, 6))
    rng = np.random.default_rng(0)
    out = {}
    scenarios = [
        ("base", list(VARIANTS), METHODS, seeds10, ONE_K),
        ("fast", MAIN, CORE, seeds10, {"agents": {"n_agents": 1000, "speed_mps": 30.0},
                                       "topology": {"cell_spacing_m": 150}}),
        ("failure", MAIN, CORE, seeds10, {"agents": {"n_agents": 1000}, "sim": {"failure_fraction": 0.3}}),
        ("long", MAIN, CORE, seeds5, {"agents": {"n_agents": 1000}, "sim": {"duration_s": 150.0}}),
        ("n10000", MAIN, CORE, seeds5, {"agents": {"n_agents": 10000 if not args.quick else 3000}}),
    ]
    for name, variants, methods, seeds, base in scenarios:
        df = sweep(f"refresh_{name}", variants, VARIANTS.__getitem__, methods, seeds, quick=args.quick,
                   workers=args.workers, config=args.config, base=base, label="variant")
        out[name] = {"means": table(df, "variant"),
                     "fix_vs_old": paired(df, "full", "full_fixed", "variant", rng),
                     "incremental_vs_fixed": paired(df, "full_fixed", "incremental", "variant", rng)}
        print(json.dumps({k: out[name][k] for k in ("fix_vs_old", "incremental_vs_fixed")}, indent=1), flush=True)

    # how much may a representative drift before it is sent?
    thresholds = [0.0, 0.003, 0.01, 0.03, 0.1]
    df = sweep("refresh_threshold", thresholds,
               lambda v: {"sfib": {"refresh_mode": "incremental", "tier_aware_delta": True,
                                   "change_threshold": v}},
               ["agentroute", "greedy"], seeds10, quick=args.quick, workers=args.workers,
               config=args.config, base=ONE_K, label="threshold")
    out["threshold"] = {"means": table(df, "threshold")}

    path = RESULTS / "raw" / ("refresh_quick.json" if args.quick else "refresh.json")
    path.write_text(json.dumps(out, indent=1))
    print("wrote", path)


if __name__ == "__main__":
    main()
