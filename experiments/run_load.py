"""Network load vs success and completion time (1,000 agents).

The load factor scales both the task request rate and the background
utilisation of every router.

Written with AI assistance (experiment tooling).
"""
from common import ALL_METHODS, describe, parse_args, seeds_for, sweep

if __name__ == "__main__":
    args = parse_args(__doc__)
    values = [1.0, 4.0] if args.quick else [0.5, 1.0, 2.0, 3.0, 4.0]
    df = sweep("load", values, "sim.load", ALL_METHODS, seeds_for(args.quick),
               quick=args.quick, workers=args.workers, config=args.config,
               base={"agents": {"n_agents": 1000}}, label="load")
    describe(df, label="load")
