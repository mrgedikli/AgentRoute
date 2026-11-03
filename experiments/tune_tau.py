"""Tune the acceptance threshold tau on the training paraphrases.

An agent accepts a task when cos(intent, capability) >= tau. We pick the tau
that maximises F1 over all (intent, capability description) pairs of the
training set, where a pair is positive when both belong to the same class.
The result is written to results/tau.json and read by the simulator.

Responsible: Bekir Emre Sarıpınar
"""
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from agentroute.config import RESULTS  # noqa: E402
from agentroute.embeddings import load_dataset_vectors  # noqa: E402


def pair_scores(intent_vecs, intent_class, desc_vecs, desc_class):
    sims = intent_vecs @ desc_vecs.T
    same = intent_class[:, None] == desc_class[None, :]
    return sims[same], sims[~same], sims


def best_threshold(pos, neg):
    best = (0.0, 0.0, 0.0, 0.0)
    for tau in np.arange(0.05, 0.95, 0.005):
        tp = (pos >= tau).sum()
        fp = (neg >= tau).sum()
        fn = (pos < tau).sum()
        precision = tp / max(tp + fp, 1)
        recall = tp / max(tp + fn, 1)
        f1 = 2 * precision * recall / max(precision + recall, 1e-9)
        if f1 > best[0]:
            best = (f1, float(tau), float(precision), float(recall))
    return best


def top1_accuracy(sims, intent_class, desc_class):
    return float((desc_class[sims.argmax(axis=1)] == intent_class).mean())


def main():
    data = load_dataset_vectors()
    pos, neg, sims = pair_scores(data["train_vecs"], data["train_class"],
                                 data["desc_vecs"], data["desc_class"])
    f1, tau, precision, recall = best_threshold(pos, neg)

    test_pos, test_neg, test_sims = pair_scores(data["test_vecs"], data["test_class"],
                                                data["desc_vecs"], data["desc_class"])
    result = {
        "tau": round(tau, 3),
        "train_f1": round(f1, 4),
        "train_precision": round(precision, 4),
        "train_recall": round(recall, 4),
        "test_recall": round(float((test_pos >= tau).mean()), 4),
        "test_false_accept": round(float((test_neg >= tau).mean()), 4),
        "train_top1": round(top1_accuracy(sims, data["train_class"], data["desc_class"]), 4),
        "test_top1": round(top1_accuracy(test_sims, data["test_class"], data["desc_class"]), 4),
        "mean_pos_cos": round(float(pos.mean()), 4),
        "mean_neg_cos": round(float(neg.mean()), 4),
    }
    RESULTS.mkdir(exist_ok=True)
    with open(RESULTS / "tau.json", "w") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
