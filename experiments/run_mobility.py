"""Robustness to mobility: random-waypoint speed vs success (1,000 agents).

Two cell sizes: the default 500 m macro cells and 150 m small cells, where the
handover rate is more than three times higher.

Written with AI assistance (experiment tooling).
"""
from common import ALL_METHODS, describe, parse_args, seeds_for, sweep

if __name__ == "__main__":
    args = parse_args(__doc__)
    values = [0.0, 10.0] if args.quick else [0.0, 2.0, 5.0, 10.0, 20.0, 30.0]
    for name, spacing in (("mobility", 500), ("mobility_small", 150)):
        df = sweep(name, values, "agents.speed_mps", ALL_METHODS, seeds_for(args.quick),
                   quick=args.quick, workers=args.workers, config=args.config,
                   base={"agents": {"n_agents": 1000}, "topology": {"cell_spacing_m": spacing}},
                   label="speed")
        describe(df, label="speed", cols=("success_rate", "time_ms", "handovers", "ctrl_msgs_per_s", "ctrl_kB_per_s"))
