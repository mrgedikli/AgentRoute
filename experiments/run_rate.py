"""Request rate vs traffic (1,000 agents).

Control traffic is paid per second, query traffic per request, so "messages
per request" depends on the request rate that was assumed. This sweep shows
the total traffic of every method at each rate and where the curves cross.

Written with AI assistance (experiment tooling).
"""
from common import describe, parse_args, seeds_for, sweep

METHODS = ["agentroute", "greedy", "greedy_load", "spfr", "flooding", "registry", "registry3", "sdht"]

if __name__ == "__main__":
    args = parse_args(__doc__)
    values = [1.0, 30.0] if args.quick else [1.0, 3.0, 10.0, 30.0, 100.0, 300.0]
    df = sweep("rate", values, "sim.query_rate", METHODS, seeds_for(args.quick),
               quick=args.quick, workers=args.workers, config=args.config,
               base={"agents": {"n_agents": 1000}}, label="rate")
    describe(df, label="rate", cols=("success_rate", "time_ms", "ctrl_kB_per_s", "query_kB_per_query"))
