"""Run the small demo scenario once per method with full event logging.

Writes results/logs/demo/<method>/{topology.json, events.jsonl, summary.json},
which the animation, the Streamlit app and the React player read.

Written with AI assistance (experiment tooling).
"""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from agentroute.config import load_config  # noqa: E402
from agentroute.sim.simulator import METHODS, Simulator  # noqa: E402


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--config", default=str(ROOT / "configs" / "demo.yaml"))
    p.add_argument("--methods", nargs="*", default=METHODS)
    p.add_argument("--out", default=str(ROOT / "results" / "logs" / "demo"))
    args = p.parse_args()
    for method in args.methods:
        cfg = load_config(args.config)
        s = Simulator(cfg, method, log_dir=Path(args.out) / method).run()
        print(f"{method:15s} queries={s['n_queries']:4d} success={s['success_rate']:.3f} "
              f"time={s['time_ms']:.1f} ms hops={s['hops']:.2f}")


if __name__ == "__main__":
    main()
