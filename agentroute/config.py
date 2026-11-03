"""Config loading and seeding.

Every experiment starts from configs/default.yaml and overrides a few keys,
so all runs are reproducible from a YAML file plus a seed.

Responsible: Ömer Faruk Gedikli
"""
import copy
import random
from pathlib import Path

import numpy as np
import yaml

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG = ROOT / "configs" / "default.yaml"
RESULTS = ROOT / "results"


def deep_update(base, override):
    """Recursively merge `override` into `base` (in place) and return base."""
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            deep_update(base[key], value)
        else:
            base[key] = copy.deepcopy(value)
    return base


def load_config(path=None, overrides=None):
    """Load the default config, then an optional YAML file, then a dict of overrides."""
    with open(DEFAULT_CONFIG) as f:
        cfg = yaml.safe_load(f)
    if path is not None and Path(path).resolve() != DEFAULT_CONFIG:
        with open(path) as f:
            deep_update(cfg, yaml.safe_load(f) or {})
    if overrides:
        deep_update(cfg, overrides)
    return cfg


def set_by_path(cfg, dotted_key, value):
    """set_by_path(cfg, "sfib.radius", 3) sets cfg["sfib"]["radius"] = 3."""
    keys = dotted_key.split(".")
    node = cfg
    for key in keys[:-1]:
        node = node.setdefault(key, {})
    node[keys[-1]] = value


def seed_everything(seed):
    random.seed(seed)
    np.random.seed(seed)
    try:
        import torch
        torch.manual_seed(seed)
    except ImportError:
        pass
