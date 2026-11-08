"""Acceptance threshold tau vs success and wrong deliveries (1,000 agents).

A low tau finds more agents but hands more tasks to the wrong one. Every point
of this sweep is an operating point; tau = results/tau.json is the one we use.

Written with AI assistance (experiment tooling).
"""
from common import describe, parse_args, seeds_for, sweep

METHODS = ["agentroute", "greedy", "greedy_load", "spfr", "flooding", "registry"]

if __name__ == "__main__":
    args = parse_args(__doc__)
    values = [0.3, 0.45] if args.quick else [0.25, 0.30, 0.355, 0.40, 0.45, 0.50]
    df = sweep("tau", values, "forwarding.tau", METHODS, seeds_for(args.quick),
               quick=args.quick, workers=args.workers, config=args.config,
               base={"agents": {"n_agents": 1000}}, label="tau")
    describe(df, label="tau", cols=("success_rate", "precision", "oracle_best"))
