"""Ablations (1,000 agents):
  1. S-FIB content: mean / k = 2..32 / two-tier off / exact table
  2. intent header compression: float32 / int8 / binary
  3. acceptance rule: first agent above tau (v1) / best known candidate
  4. handover suppression threshold
  5. flooding collection window

Written with AI assistance (experiment tooling).
"""
from common import describe, parse_args, seeds_for, sweep

SUMMARIES = {
    "mean": {"sfib": {"summary": "mean", "exact_hops": 0}},
    "k=8, no tier": {"sfib": {"k": 8, "exact_hops": 0}},
    "k=2": {"sfib": {"k": 2}},
    "k=4": {"sfib": {"k": 4}},
    "k=8": {"sfib": {"k": 8}},
    "k=16": {"sfib": {"k": 16}},
    "k=32": {"sfib": {"k": 32}},
    "exact": {"sfib": {"summary": "exact"}},
}
METHODS = ["agentroute", "greedy", "greedy_load"]

if __name__ == "__main__":
    args = parse_args(__doc__)
    base = {"agents": {"n_agents": 1000}}
    seeds = seeds_for(args.quick)
    common = dict(quick=args.quick, workers=args.workers, config=args.config, base=base)

    names = ["mean", "k=8"] if args.quick else list(SUMMARIES)
    df = sweep("ablation_summary", names, lambda v: SUMMARIES[v], METHODS, seeds, label="summary", **common)
    describe(df, label="summary", cols=("success_rate", "time_ms", "hops", "ctrl_kB_per_s"))

    headers = ["float32", "binary"] if args.quick else ["float32", "int8", "binary"]
    df = sweep("ablation_header", headers, "forwarding.header", METHODS, seeds, label="header", **common)
    describe(df, label="header", cols=("success_rate", "time_ms", "hops", "query_kB_per_query"))

    df = sweep("ablation_accept", ["first", "best_known"], "forwarding.accept", ["greedy", "greedy_load"],
               seeds, label="accept", **common)
    describe(df, label="accept", cols=("success_rate", "precision", "time_ms", "hops"))

    thresholds = [0.0, 0.01] if args.quick else [0.0, 0.001, 0.01, 0.05, 0.2]
    df = sweep("ablation_threshold", thresholds, "sfib.change_threshold", ["greedy"], seeds,
               label="threshold", **common)
    describe(df, label="threshold", cols=("success_rate", "update_msgs", "ctrl_kB_per_s"))

    windows = [0.05, 0.2] if args.quick else [0.02, 0.05, 0.1, 0.2, 0.5, 1.0]
    df = sweep("ablation_window", windows, "baselines.flood_window_s", ["flooding"], seeds,
               label="window", **common)
    describe(df, label="window", cols=("success_rate", "time_ms"))
