"""Robustness to node failures: fraction of failed routers vs success (1,000 agents).

Routers fail at one third of the run; neighbours notice after the detection delay.

Written with AI assistance (experiment tooling).
"""
from common import ALL_METHODS, describe, parse_args, seeds_for, sweep

if __name__ == "__main__":
    args = parse_args(__doc__)
    values = [0.0, 0.2] if args.quick else [0.0, 0.05, 0.1, 0.2, 0.3]
    df = sweep("failure", values, "sim.failure_fraction", ALL_METHODS, seeds_for(args.quick),
               quick=args.quick, workers=args.workers, config=args.config,
               base={"agents": {"n_agents": 1000}}, label="failure")
    describe(df, label="failure")
