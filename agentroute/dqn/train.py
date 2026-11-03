"""Offline Double-DQN training in the simulator.

Each episode is one simulation run in a randomly drawn scenario (agent count,
mobility speed, load, failures, radius), so the shared network sees many
different situations. Training uses the *train* paraphrases only; the test
paraphrases are kept for the evaluation experiments.

Every `eval_every` episodes the greedy (epsilon = 0) policy is evaluated on
fixed validation scenarios and the best weights are kept.

Responsible: Bekir Göktepe
"""
import copy
import csv
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F

from agentroute.config import ROOT, deep_update, load_config, seed_everything
from agentroute.dqn.policy import DQNPolicy, build_model
from agentroute.dqn.replay import ReplayBuffer
from agentroute.forwarding import N_FEATURES, GreedyPolicy
from agentroute.sim.simulator import Simulator


class Learner:
    def __init__(self, model, dqn_cfg, rng):
        self.online = model
        self.target = copy.deepcopy(model)
        self.cfg = dqn_cfg
        self.opt = torch.optim.Adam(model.parameters(), lr=dqn_cfg["lr"])
        self.buffer = ReplayBuffer(dqn_cfg["buffer_size"], N_FEATURES, rng)
        self.pushed = 0
        self.steps = 0
        self.losses = []

    def push(self, x, a, r, x2, done):
        self.buffer.push(x, a, r, x2, done)
        self.pushed += 1
        if self.pushed % self.cfg["train_every"] == 0 and len(self.buffer) >= 4 * self.cfg["batch_size"]:
            self.train_step()

    def train_step(self):
        s, s_mask, a, r, s2, s2_mask, done = self.buffer.sample(self.cfg["batch_size"])
        q = self.online(s, s_mask).gather(1, a[:, None]).squeeze(1)
        with torch.no_grad():
            # Double DQN: the online net picks the next action, the target net values it
            a2 = self.online(s2, s2_mask).argmax(dim=1)
            q2 = self.target(s2, s2_mask).gather(1, a2[:, None]).squeeze(1)
            q2 = torch.where(done | ~s2_mask.any(dim=1), torch.zeros_like(q2), q2)
            y = r + self.cfg["gamma"] * q2
        loss = F.smooth_l1_loss(q, y)
        self.opt.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(self.online.parameters(), 1.0)
        self.opt.step()
        self.steps += 1
        self.losses.append(loss.item())
        if self.steps % self.cfg["target_update"] == 0:
            self.target.load_state_dict(self.online.state_dict())


def sample_scenario(rng):
    """A random training scenario, as config overrides (biased towards loaded networks)."""
    return {
        "agents": {"n_agents": int(rng.choice([300, 600, 1000, 2000])),
                   "speed_mps": float(rng.choice([0.0, 2.0, 5.0, 10.0, 20.0]))},
        "sim": {"duration_s": 20.0, "load": float(rng.choice([0.5, 1.0, 2.0, 3.0, 4.0])),
                "failure_fraction": float(rng.choice([0.0, 0.0, 0.1, 0.2]))},
        "sfib": {"radius": int(rng.choice([2, 3, 4]))},
    }


VALIDATION = [
    {"agents": {"n_agents": 1000, "speed_mps": 5.0}, "sim": {"duration_s": 20.0, "load": 2.0}},
    {"agents": {"n_agents": 1000, "speed_mps": 10.0}, "sim": {"duration_s": 20.0, "load": 3.0,
                                                               "failure_fraction": 0.1}},
    {"agents": {"n_agents": 2000, "speed_mps": 2.0}, "sim": {"duration_s": 20.0, "load": 1.0}},
]


def evaluate(policy, base_cfg, seeds=(9001, 9002)):
    """Validation on fixed scenarios (train intents).

    Returns (success rate, completion time in ms, return per request). The
    return is only defined for the DQN; for greedy it is NaN.
    """
    rates, times, returns = [], [], []
    for scen in VALIDATION:
        for seed in seeds:
            cfg = deep_update(copy.deepcopy(base_cfg), scen)
            method = "greedy" if isinstance(policy, GreedyPolicy) else "agentroute"
            if method == "agentroute":
                policy.episode_return = 0.0
            s = Simulator(cfg, method, seed=seed, policy=policy, intents="train").run()
            rates.append(s["success_rate"])
            times.append(s["time_ms"])
            if method == "agentroute":
                returns.append(policy.episode_return / max(s["n_queries"], 1))
    ret = float(np.mean(returns)) if returns else float("nan")
    return float(np.mean(rates)), float(np.nanmean(times)), ret


def train(kind="mlp", episodes=None, config_path=None, out_csv=None, verbose=True):
    base = load_config(config_path)
    dqn = base["dqn"]
    seed_everything(base["seed"])
    torch.set_num_threads(2)
    rng = np.random.default_rng(base["seed"])
    episodes = episodes or dqn["episodes"]
    model = build_model(kind, dqn["hidden"])
    learner = Learner(model, dqn, rng)
    policy = DQNPolicy(model, kind=kind, learner=learner, rng=rng, reward=dqn["reward"])
    model_path = ROOT / (dqn["gnn_model_path"] if kind == "gnn" else dqn["model_path"])
    out_csv = Path(out_csv or ROOT / "results" / "raw" / f"train_{kind}.csv")
    out_csv.parent.mkdir(parents=True, exist_ok=True)

    greedy_val = evaluate(GreedyPolicy(), base)
    best_val = -1e9
    rows = []
    decay_eps = max(1, int(dqn["eps_decay_frac"] * episodes))
    t_start = time.time()
    for ep in range(episodes):
        eps = max(dqn["eps_end"], dqn["eps_start"] - (dqn["eps_start"] - dqn["eps_end"]) * ep / decay_eps)
        cfg = deep_update(copy.deepcopy(base), sample_scenario(rng))
        policy.epsilon = eps
        policy.learner = learner
        policy.episode_return = 0.0
        n_losses = len(learner.losses)
        s = Simulator(cfg, "agentroute", seed=10_000 + ep, policy=policy, intents="train").run()
        row = {"episode": ep, "epsilon": round(eps, 3), "success_rate": s["success_rate"],
               "return_per_query": policy.episode_return / max(s["n_queries"], 1),
               "loss": float(np.mean(learner.losses[n_losses:])) if len(learner.losses) > n_losses else float("nan"),
               "n_agents": cfg["agents"]["n_agents"], "val_success": float("nan"),
               "val_time_ms": float("nan"), "val_return": float("nan"),
               "greedy_val_success": greedy_val[0],
               "greedy_val_time_ms": greedy_val[1]}
        if (ep + 1) % dqn["eval_every"] == 0 or ep == episodes - 1:
            policy.epsilon, policy.learner = 0.0, None
            val_rate, val_time, val_ret = evaluate(policy, base)
            row["val_success"], row["val_time_ms"], row["val_return"] = val_rate, val_time, val_ret
            if val_ret > best_val:      # keep the weights with the best validation return
                best_val = val_ret
                policy.save(model_path, dqn["hidden"])
        rows.append(row)
        if verbose:
            print(f"[{kind}] ep {ep:3d} eps={eps:.2f} succ={s['success_rate']:.3f} "
                  f"ret/q={row['return_per_query']:.3f} loss={row['loss']:.4f} "
                  f"val={row['val_success']:.3f}/{row['val_time_ms']:.1f}ms "
                  f"(greedy {greedy_val[0]:.3f}/{greedy_val[1]:.1f}ms) "
                  f"[{time.time() - t_start:.0f}s]", flush=True)
        with open(out_csv, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)
    return best_val, greedy_val
