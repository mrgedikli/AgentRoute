"""Scalability: number of agents (100 -> 10,000) vs success, overhead, hops, time.

Written with AI assistance (experiment tooling).
"""
from common import ALL_METHODS, describe, parse_args, seeds_for, sweep

if __name__ == "__main__":
    args = parse_args(__doc__)
    values = [100, 300] if args.quick else [100, 300, 1000, 3000, 10000]
    df = sweep("scale", values, "agents.n_agents", ALL_METHODS, seeds_for(args.quick),
               quick=args.quick, workers=args.workers, config=args.config, label="n_agents_param")
    describe(df, label="n_agents_param")
