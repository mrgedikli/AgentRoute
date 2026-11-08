"""Compare pre-trained sentence encoders on the capability dataset.

The encoder sets the ceiling of every semantic method, so it is chosen first.
For each candidate we build the capability cards, then measure on the *train*
paraphrases (the choice) and report the *test* paraphrases next to them:

    top1     : the most similar card is of the right class
    f1_tau   : acceptance threshold that maximises F1 of "accept the best card"
    ceiling  : best card is of the right class and passes tau

Writes results/encoders.json.

Written with AI assistance (experiment tooling).
"""
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from agentroute.config import RESULTS  # noqa: E402
from agentroute.data.capabilities import capability_cards, split_intents  # noqa: E402
from agentroute.embeddings import embed_texts  # noqa: E402

# (model name, prefix of a query, prefix of a capability sentence)
CANDIDATES = [
    ("sentence-transformers/all-MiniLM-L6-v2", "", ""),
    ("sentence-transformers/multi-qa-MiniLM-L6-cos-v1", "", ""),
    ("sentence-transformers/all-mpnet-base-v2", "", ""),
    ("BAAI/bge-small-en-v1.5", "Represent this sentence for searching relevant passages: ", ""),
    ("BAAI/bge-base-en-v1.5", "Represent this sentence for searching relevant passages: ", ""),
    ("intfloat/e5-small-v2", "query: ", "passage: "),
]


def score(intent_vecs, intent_class, card_vecs, card_class, tau):
    sims = intent_vecs @ card_vecs.T
    best = sims.argmax(axis=1)
    right = card_class[best] == intent_class
    passes = sims.max(axis=1) >= tau
    return {"top1": float(right.mean()),
            "ceiling": float((right & passes).mean()),
            "wrong_accept": float((~right & passes).mean())}


def best_tau(intent_vecs, intent_class, card_vecs, card_class):
    """Tau that maximises F1 of the decision "accept the most similar card"."""
    sims = intent_vecs @ card_vecs.T
    best = sims.argmax(axis=1)
    right = card_class[best] == intent_class
    top = sims.max(axis=1)
    out = (0.0, 0.0)
    for tau in np.arange(0.05, 0.95, 0.005):
        tp = (right & (top >= tau)).sum()
        fp = (~right & (top >= tau)).sum()
        fn = (right & (top < tau)).sum()
        f1 = 2 * tp / max(2 * tp + fp + fn, 1)
        if f1 > out[0]:
            out = (float(f1), float(tau))
    return out[1]


def main():
    cards = capability_cards()
    train, test = split_intents()
    card_class = np.array([c[0] for c in cards])
    out = {}
    for name, q_prefix, doc_prefix in CANDIDATES:
        flat = [doc_prefix + s for c in cards for s in c[2]]
        v = embed_texts(flat, name)
        card_vecs = np.stack([v[i:i + 3].mean(axis=0) for i in range(0, len(v), 3)])
        card_vecs = card_vecs / np.linalg.norm(card_vecs, axis=1, keepdims=True)
        tr_vecs = embed_texts([q_prefix + t for _, t in train], name)
        te_vecs = embed_texts([q_prefix + t for _, t in test], name)
        tr_y = np.array([c for c, _ in train])
        te_y = np.array([c for c, _ in test])
        tau = best_tau(tr_vecs, tr_y, card_vecs, card_class)
        out[name] = {"dim": int(card_vecs.shape[1]), "tau": round(tau, 3),
                     "train": score(tr_vecs, tr_y, card_vecs, card_class, tau),
                     "test": score(te_vecs, te_y, card_vecs, card_class, tau)}
        print(name, json.dumps(out[name]), flush=True)
    with open(RESULTS / "encoders.json", "w") as f:
        json.dump(out, f, indent=2)


if __name__ == "__main__":
    main()
