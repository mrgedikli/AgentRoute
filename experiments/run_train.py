"""Train the DQN (and the GNN variant) and save the weights and learning curves.

    python experiments/run_train.py              # both models
    python experiments/run_train.py --kind mlp --episodes 30

Responsible: Bekir Göktepe
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from agentroute.dqn.train import train  # noqa: E402


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--kind", choices=["mlp", "gnn", "both"], default="both")
    p.add_argument("--episodes", type=int, default=None)
    p.add_argument("--config", default=None)
    args = p.parse_args()
    kinds = ["mlp", "gnn"] if args.kind == "both" else [args.kind]
    for kind in kinds:
        best, greedy = train(kind, episodes=args.episodes, config_path=args.config)
        print(f"{kind}: best validation return {best:.3f} (greedy success {greedy[0]:.3f})")


if __name__ == "__main__":
    main()
