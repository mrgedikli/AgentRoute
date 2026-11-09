"""Shared helpers for the experiment scripts.

A sweep runs every (parameter value, method, seed) combination in parallel
worker processes and writes one CSV row per run to results/raw/<name>.csv.

Written with AI assistance (experiment tooling).
"""
import argparse
import copy
import sys
import time
from multiprocessing import Pool
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import pandas as pd  # noqa: E402

from agentroute.config import RESULTS, deep_update, load_config, set_by_path  # noqa: E402

ALL_METHODS = ["agentroute", "agentroute_gnn", "greedy", "greedy_load", "spfr",
               "flooding", "registry", "registry3", "chord", "sdht"]
SEMANTIC_METHODS = ["agentroute", "agentroute_gnn", "greedy", "greedy_load", "spfr"]
SEEDS = list(range(1, 11))


def parse_args(description):
    p = argparse.ArgumentParser(description=description)
    p.add_argument("--quick", action="store_true", help="few values, one seed, short runs")
    p.add_argument("--workers", type=int, default=6)
    p.add_argument("--config", default=None)
    return p.parse_args()


def _run_one(job):
    import torch
    torch.set_num_threads(1)
    from agentroute.sim.simulator import Simulator
    cfg, method, seed, extra = job
    t0 = time.time()
    row = Simulator(cfg, method, seed=seed).run()
    row.update(extra)
    row["wall_s"] = round(time.time() - t0, 2)
    return row


def sweep(name, values, apply, methods, seeds, quick=False, workers=6, config=None,
          base=None, label="value"):
    """Run a parameter sweep.

    values  : list of parameter values
    apply   : dotted config key ("sfib.radius") or a function value -> overrides dict
    """
    jobs = []
    for v in values:
        for m in methods:
            for seed in seeds:
                cfg = load_config(config, base)
                if quick:
                    cfg["sim"]["duration_s"] = min(cfg["sim"]["duration_s"], 15.0)
                if callable(apply):
                    deep_update(cfg, apply(v))
                else:
                    set_by_path(cfg, apply, v)
                jobs.append((cfg, m, seed, {"experiment": name, label: v}))
    # heaviest runs first so that the workers stay busy until the end
    jobs.sort(key=lambda j: -j[0]["agents"]["n_agents"])
    t0 = time.time()
    rows = []
    with Pool(workers) as pool:
        for i, row in enumerate(pool.imap_unordered(_run_one, jobs), 1):
            rows.append(row)
            if i % 10 == 0 or i == len(jobs):
                print(f"[{name}] {i}/{len(jobs)} runs done ({time.time() - t0:.0f}s)", flush=True)
    df = pd.DataFrame(rows).sort_values([label, "method", "seed"])
    # quick runs never overwrite the full results that the report uses
    out = RESULTS / "raw" / (f"{name}_quick.csv" if quick else f"{name}.csv")
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    print(f"[{name}] wrote {out}")
    return df


def seeds_for(quick):
    return [1] if quick else SEEDS


def describe(df, label="value", cols=("success_rate", "time_ms", "hops", "msgs_per_query")):
    """Print a compact mean table (used at the end of each script)."""
    table = df.groupby([label, "method"])[list(cols)].mean().round(3)
    print(table.to_string())
    return table


__all__ = ["ALL_METHODS", "SEMANTIC_METHODS", "parse_args", "sweep", "seeds_for", "describe", "copy"]
