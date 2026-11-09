"""Sentence embeddings for capability addresses and intents.

We use the pre-trained all-MiniLM-L6-v2 encoder (384 dimensions). Vectors are
L2-normalised, so cosine similarity is a plain dot product. Embeddings are
computed once and cached as .npy files under results/cache/.

Responsible: Bekir Emre Sarıpınar
"""
import hashlib

import numpy as np

from agentroute.config import RESULTS
from agentroute.data.capabilities import capability_cards, class_sentences, split_intents

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
DIM = 384
CACHE_DIR = RESULTS / "cache"

_models = {}


def get_model(name=MODEL_NAME):
    if name not in _models:
        from sentence_transformers import SentenceTransformer
        _models[name] = SentenceTransformer(name, device="cpu")
    return _models[name]


def embed_texts(texts, name=MODEL_NAME):
    """Return an (n, dim) float32 array of normalised embeddings, using the cache."""
    key = hashlib.sha1((name + "\n" + "\n".join(texts)).encode()).hexdigest()[:16]
    path = CACHE_DIR / f"emb_{key}.npy"
    if path.exists():
        return np.load(path)
    vecs = get_model(name).encode(list(texts), batch_size=64, normalize_embeddings=True,
                                  show_progress_bar=False)
    vecs = np.asarray(vecs, dtype=np.float32)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    np.save(path, vecs)
    return vecs


def card_vector(sentence_vecs):
    """Capability address of one agent: normalised centroid of its card sentences."""
    v = sentence_vecs.mean(axis=0)
    return (v / np.linalg.norm(v)).astype(np.float32)


def agent_vectors(class_vecs, cls, rng, alpha=2.0):
    """Capability address of each agent (v2): its own random mix of its class's sentences.

    class_vecs has shape (n_classes, n_sentences, dim). The weights are drawn
    from a Dirichlet(alpha) distribution, so two providers of the same skill
    are close to each other but never identical.
    """
    n_sent = class_vecs.shape[1]
    weights = rng.dirichlet(alpha * np.ones(n_sent), size=len(cls))
    v = (weights[:, :, None] * class_vecs[cls]).sum(axis=1)
    return (v / np.linalg.norm(v, axis=1, keepdims=True)).astype(np.float32)


def load_dataset_vectors(split_seed=0):
    """Embed every capability card and every train/test intent.

    desc_* arrays have one row per (class, variant) card. desc_text is the
    card's description sentence (used as the Chord key and in plots).
    """
    cards = capability_cards()
    train, test = split_intents(seed=split_seed)
    data = {
        "desc_text": [c[2][0] for c in cards],
        "desc_card": [c[2] for c in cards],
        "desc_class": np.array([c[0] for c in cards]),
        "desc_variant": np.array([c[1] for c in cards]),
        "train_text": [t for _, t in train],
        "train_class": np.array([c for c, _ in train]),
        "test_text": [t for _, t in test],
        "test_class": np.array([c for c, _ in test]),
    }
    flat = [s for c in cards for s in c[2]]
    flat_vecs = embed_texts(flat)
    sizes = [len(c[2]) for c in cards]
    starts = np.cumsum([0] + sizes[:-1])
    data["desc_vecs"] = np.stack([card_vector(flat_vecs[s:s + n]) for s, n in zip(starts, sizes)])
    sentences = class_sentences()
    flat_class = embed_texts([s for row in sentences for s in row])
    data["class_vecs"] = flat_class.reshape(len(sentences), len(sentences[0]), -1)
    data["train_vecs"] = embed_texts(data["train_text"])
    data["test_vecs"] = embed_texts(data["test_text"])
    return data


def quantize(vec, header="float32"):
    """Simulate a compressed intent header.

    float32: 384 x 4 B = 1536 B (unchanged)
    int8:    384 x 1 B + 4 B scale = 388 B
    binary:  384 bits = 48 B (only the sign of each dimension is kept)
    """
    if header == "float32":
        return vec
    if header == "int8":
        scale = 127.0 / max(np.abs(vec).max(), 1e-8)
        q = np.round(vec * scale) / scale
    elif header == "binary":
        q = np.where(vec >= 0, 1.0, -1.0)
    else:
        raise ValueError(f"unknown header type {header}")
    q = q.astype(np.float32)
    return q / np.linalg.norm(q)


def header_bytes(header="float32", dim=DIM):
    return {"float32": dim * 4, "int8": dim + 4, "binary": dim // 8}[header]
