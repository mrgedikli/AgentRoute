"""Advertisement radius R vs success and control overhead (semantic methods, 1,000 agents).

Written with AI assistance (experiment tooling).
"""
from common import describe, parse_args, seeds_for, sweep

METHODS = ["agentroute", "agentroute_gnn", "greedy", "greedy_load"]     # SPFR has its own horizon

if __name__ == "__main__":
    args = parse_args(__doc__)
    values = [1, 3] if args.quick else [1, 2, 3, 4, 5, 6]
    df = sweep("radius", values, "sfib.radius", METHODS, seeds_for(args.quick),
               quick=args.quick, workers=args.workers, config=args.config,
               base={"agents": {"n_agents": 1000}}, label="radius")
    describe(df, label="radius", cols=("success_rate", "time_ms", "ctrl_msgs_per_s", "ctrl_kB_per_s"))
