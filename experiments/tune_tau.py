"""Tune the acceptance threshold tau on the training paraphrases.

An agent accepts a task when cos(intent, capability) >= tau. v2 chooses tau
for the question the network really faces: "is the best agent I can see good
enough?". For every training intent we take sampled agents of all classes and
score each outcome the way the DQN reward does:

    +1  the best agent has the right class and passes tau
    -1  the best agent has the wrong class and passes tau
     0  nothing passes tau (the requester knows that nothing was found)

A capable agent exists with probability P_EXISTS; in the other case the
intent's class is removed and any accepted agent counts as wrong. tau maximises
the expected score. Results are written to results/tau.json and read by the
simulator.

Responsible: Bekir Emre Sarıpınar (v2 revision written with AI assistance)
"""
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from agentroute.config import RESULTS, load_config  # noqa: E402
from agentroute.embeddings import agent_vectors, load_dataset_vectors  # noqa: E402

AGENTS_PER_CLASS = 20
P_EXISTS = 0.9


def open_set_scores(intent_vecs, intent_class, agent_vecs, agent_class, tau):
    """Returns (success if capable agents exist, rejection rate if none exists, wrong accepts)."""
    sims = intent_vecs @ agent_vecs.T
    best = sims.argmax(axis=1)
    right = agent_class[best] == intent_class
    passes = sims.max(axis=1) >= tau
    other = np.where(agent_class[None, :] == intent_class[:, None], -2.0, sims)
    reject = other.max(axis=1) < tau
    return float((right & passes).mean()), float(reject.mean()), float((~right & passes).mean())


def main():
    cfg = load_config()
    data = load_dataset_vectors()
    n_cls = data["class_vecs"].shape[0]
    rng = np.random.default_rng(0)
    cls = np.repeat(np.arange(n_cls), AGENTS_PER_CLASS)
    vecs = agent_vectors(data["class_vecs"], cls, rng, cfg["agents"]["card_alpha"])
    best = (-1.0, 0.0)
    curve = []
    for tau in np.arange(0.10, 0.80, 0.005):
        acc, rej, wrong = open_set_scores(data["train_vecs"], data["train_class"], vecs, cls, tau)
        score = P_EXISTS * (acc - wrong) - (1 - P_EXISTS) * (1 - rej)
        curve.append({"tau": round(float(tau), 3), "accept_right": round(acc, 4),
                      "reject_when_absent": round(rej, 4), "wrong_accept": round(wrong, 4)})
        if score > best[0]:
            best = (score, float(tau))
    tau = round(best[1], 3)
    acc, rej, wrong = open_set_scores(data["test_vecs"], data["test_class"], vecs, cls, tau)
    tr_acc, tr_rej, tr_wrong = open_set_scores(data["train_vecs"], data["train_class"], vecs, cls, tau)
    top1 = float((cls[(data["test_vecs"] @ vecs.T).argmax(axis=1)] == data["test_class"]).mean())
    result = {"tau": tau, "train_score": round(best[0], 4),
              "train_accept_right": round(tr_acc, 4), "train_reject_when_absent": round(tr_rej, 4),
              "train_wrong_accept": round(tr_wrong, 4),
              "test_top1": round(top1, 4), "test_accept_right": round(acc, 4),
              "test_reject_when_absent": round(rej, 4), "test_wrong_accept": round(wrong, 4),
              "curve": curve}
    RESULTS.mkdir(exist_ok=True)
    with open(RESULTS / "tau.json", "w") as f:
        json.dump(result, f, indent=2)
    print(json.dumps({k: v for k, v in result.items() if k != "curve"}, indent=2))


if __name__ == "__main__":
    main()
