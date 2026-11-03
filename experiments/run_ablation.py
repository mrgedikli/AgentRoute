"""Ablations on the semantic methods (1,000 agents):
  1. S-FIB summary: mean / k-means k=2,4,8 / exact table
  2. intent header compression: float32 / int8 / binary

Written with AI assistance (experiment tooling).
"""
from common import SEMANTIC_METHODS, describe, parse_args, seeds_for, sweep

SUMMARIES = {
    "mean": {"sfib": {"summary": "mean"}},
    "k=2": {"sfib": {"summary": "kmeans", "k": 2}},
    "k=4": {"sfib": {"summary": "kmeans", "k": 4}},
    "k=8": {"sfib": {"summary": "kmeans", "k": 8}},
    "exact": {"sfib": {"summary": "exact"}},
}

if __name__ == "__main__":
    args = parse_args(__doc__)
    base = {"agents": {"n_agents": 1000}}
    names = ["mean", "k=4"] if args.quick else list(SUMMARIES)
    df = sweep("ablation_summary", names, lambda v: SUMMARIES[v], ["agentroute", "greedy"],
               seeds_for(args.quick), quick=args.quick, workers=args.workers,
               config=args.config, base=base, label="summary")
    describe(df, label="summary", cols=("success_rate", "time_ms", "hops"))
    headers = ["float32", "binary"] if args.quick else ["float32", "int8", "binary"]
    df = sweep("ablation_header", headers, "forwarding.header", ["agentroute", "greedy"],
               seeds_for(args.quick), quick=args.quick, workers=args.workers,
               config=args.config, base=base, label="header")
    describe(df, label="header", cols=("success_rate", "time_ms", "hops"))
