"""Radio model experiments: fixed radio vs the Sionna-based radio table (1,000 agents).

  compare   : constant, sionna, and sionna with +10 dB link budget (sensitivity)
  mobility  : speed sweep with the sionna radio (the constant-radio sweep is mobility.csv)

Written with AI assistance (experiment tooling).
"""
import sys

from common import ALL_METHODS, describe, parse_args, seeds_for, sweep

SETTINGS = {
    "constant": {"radio": {"model": "constant"}},
    "sionna": {"radio": {"model": "sionna"}},
    "sionna_plus10db": {"radio": {"model": "sionna", "lut_path": "results/radio_lut_plus10db.npz"}},
}

if __name__ == "__main__":
    part = sys.argv.pop(1) if len(sys.argv) > 1 and not sys.argv[1].startswith("-") else "compare"
    args = parse_args(__doc__)
    if part == "compare":
        df = sweep("radio_compare", list(SETTINGS), lambda v: SETTINGS[v], ALL_METHODS, seeds_for(args.quick),
                   quick=args.quick, workers=args.workers, config=args.config,
                   base={"agents": {"n_agents": 1000}}, label="radio")
        describe(df, label="radio")
    else:
        values = [0.0, 10.0] if args.quick else [0.0, 2.0, 5.0, 10.0, 20.0, 30.0]
        df = sweep("radio_mobility", values, "agents.speed_mps", ALL_METHODS, seeds_for(args.quick),
                   quick=args.quick, workers=args.workers, config=args.config,
                   base={"agents": {"n_agents": 1000}, "radio": {"model": "sionna"}}, label="speed")
        describe(df, label="speed")
