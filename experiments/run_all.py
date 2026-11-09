"""Run the whole pipeline: tau -> training -> experiments -> figures -> demo -> animations.

    python experiments/run_all.py            # full run (about 1 hour on a MacBook Air)
    python experiments/run_all.py --quick    # smoke test (a few minutes)
    python experiments/run_all.py --skip-train

Written with AI assistance (experiment tooling).
"""
import argparse
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PY = sys.executable


def step(name, args):
    print(f"\n=== {name} ===", flush=True)
    t0 = time.time()
    subprocess.run([PY] + args, cwd=ROOT, check=True)
    print(f"=== {name} done in {time.time() - t0:.0f}s ===", flush=True)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--quick", action="store_true")
    p.add_argument("--skip-train", action="store_true")
    p.add_argument("--workers", default="6")
    args = p.parse_args()
    quick = ["--quick"] if args.quick else []
    workers = ["--workers", args.workers]

    step("compare encoders", ["experiments/compare_encoders.py"])
    step("tune tau", ["experiments/tune_tau.py"])
    models = [ROOT / "results" / "models" / "dqn.pt", ROOT / "results" / "models" / "gnn.pt"]
    if not args.skip_train and not all(m.exists() for m in models):
        step("train DQN + GNN", ["experiments/run_train.py"] + (["--episodes", "20"] if args.quick else []))
    for name in ["scale", "mobility", "failure", "radius", "load", "rate", "tau", "ablation",
                 "matched", "handover_cost"]:
        step(name, [f"experiments/run_{name}.py"] + quick + (workers if name != "handover_cost" else []))
    step("figures", ["viz/plots.py"])
    step("demo runs", ["experiments/run_demo.py"])
    step("animations", ["viz/animate.py"])
    step("export to web player", ["viz/export_web_data.py"])


if __name__ == "__main__":
    main()
