"""Robustness to mobility: random-waypoint speed vs success (1,000 agents).

Written with AI assistance (experiment tooling).
"""
from common import ALL_METHODS, describe, parse_args, seeds_for, sweep

if __name__ == "__main__":
    args = parse_args(__doc__)
    values = [0.0, 10.0] if args.quick else [0.0, 2.0, 5.0, 10.0, 20.0, 30.0]
    df = sweep("mobility", values, "agents.speed_mps", ALL_METHODS, seeds_for(args.quick),
               quick=args.quick, workers=args.workers, config=args.config,
               base={"agents": {"n_agents": 1000}}, label="speed")
    describe(df, label="speed")
