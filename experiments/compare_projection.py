"""Would a small trained layer on top of the encoder help?

A linear map W, initialised to the identity, is trained on the train
paraphrases with a contrastive loss and a penalty that keeps it close to the
identity. It is tested twice on the held-out paraphrases: for classes it has
seen, and (5 folds of 10 classes) for classes left out of training, which is
the case that matters if new capabilities appear. Writes results/projection.json.

Written with AI assistance (experiment tooling).
"""
import json
import sys
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from agentroute.config import RESULTS  # noqa: E402
from agentroute.data.capabilities import capability_cards, split_intents  # noqa: E402
from agentroute.embeddings import MODEL_NAME, embed_texts  # noqa: E402

ENCODERS = [(MODEL_NAME, ""),
            ("BAAI/bge-small-en-v1.5", "Represent this sentence for searching relevant passages: ")]
PENALTIES = [0.3, 0.1, 0.03]


def load(name, prefix):
    cards = capability_cards()
    train, test = split_intents()
    card_class = np.array([c[0] for c in cards])
    v = embed_texts([s for c in cards for s in c[2]], name)
    C = np.stack([v[i:i + 3].mean(axis=0) for i in range(0, len(v), 3)])
    C = C / np.linalg.norm(C, axis=1, keepdims=True)
    Xtr = embed_texts([prefix + t for _, t in train], name)
    Xte = embed_texts([prefix + t for _, t in test], name)
    return C, card_class, Xtr, np.array([c for c, _ in train]), Xte, np.array([c for c, _ in test])


def fit(C, card_class, X, y, classes, penalty, steps=400, temperature=0.05):
    torch.manual_seed(0)
    d = C.shape[1]
    W = torch.nn.Parameter(torch.eye(d))
    opt = torch.optim.Adam([W], lr=1e-3)
    keep = np.isin(card_class, classes)
    cards = torch.tensor(C[keep])
    index = {c: i for i, c in enumerate(sorted(set(card_class[keep].tolist())))}
    labels = torch.tensor([index[c] for c in card_class[keep].tolist()])
    use = np.isin(y, classes)
    Xt = torch.tensor(X[use])
    yt = torch.tensor([index[c] for c in y[use].tolist()])
    for _ in range(steps):
        zc = F.normalize(cards @ W.T, dim=1)
        zx = F.normalize(Xt @ W.T, dim=1)
        s = zx @ zc.T / temperature
        per_class = torch.stack([s[:, labels == k].max(dim=1).values for k in range(len(index))], dim=1)
        loss = F.cross_entropy(per_class, yt) + penalty * ((W - torch.eye(d)) ** 2).sum()
        opt.zero_grad()
        loss.backward()
        opt.step()
    return W.detach().numpy()


def top1(C, card_class, X, y, W=None):
    if W is not None:
        C = C @ W.T
        X = X @ W.T
        C = C / np.linalg.norm(C, axis=1, keepdims=True)
        X = X / np.linalg.norm(X, axis=1, keepdims=True)
    return float((card_class[(X @ C.T).argmax(axis=1)] == y).mean())


def main():
    torch.set_num_threads(2)
    out = {}
    for name, prefix in ENCODERS:
        C, cc, Xtr, ytr, Xte, yte = load(name, prefix)
        row = {"base_test_top1": round(top1(C, cc, Xte, yte), 4), "penalty": {}}
        perm = np.random.default_rng(0).permutation(50)
        for penalty in PENALTIES:
            seen = top1(C, cc, Xte, yte, fit(C, cc, Xtr, ytr, np.arange(50), penalty))
            unseen = []
            for f in range(5):
                out_cls = perm[f * 10:(f + 1) * 10]
                W = fit(C, cc, Xtr, ytr, np.setdiff1d(np.arange(50), out_cls), penalty, steps=300)
                mask = np.isin(yte, out_cls)
                unseen.append(top1(C, cc, Xte[mask], yte[mask], W))
            row["penalty"][str(penalty)] = {"seen_classes": round(seen, 4), "unseen_classes": round(float(np.mean(unseen)), 4)}
        out[name] = row
        print(name, json.dumps(row), flush=True)
    with open(RESULTS / "projection.json", "w") as f:
        json.dump(out, f, indent=2)


if __name__ == "__main__":
    main()
