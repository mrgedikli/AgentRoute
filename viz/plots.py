"""All figures of the report and the slides, from results/raw/*.csv.

    python viz/plots.py

Style: one fixed colour per method (never re-ordered between charts), marker
shapes as a second identity channel, hairline grid, mean with a 95% CI band.

Written with AI assistance (plotting).
"""
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
RAW = ROOT / "results" / "raw"
FIG = ROOT / "results" / "figures"

# reference categorical palette, slots 1-6 in fixed order
METHODS = {
    "agentroute":     ("AgentRoute (DQN)", "#2a78d6", "o"),
    "agentroute_gnn": ("AgentRoute (GNN)", "#eb6834", "D"),
    "greedy":         ("Greedy semantic",  "#1baf7a", "s"),
    "flooding":       ("Flooding",         "#eda100", "^"),
    "registry":       ("Central registry", "#e87ba4", "v"),
    "chord":          ("Chord (exact)",    "#008300", "X"),
}
INK, INK2, MUTED = "#0b0b0b", "#52514e", "#898781"
GRID, AXIS, SURFACE = "#e1e0d9", "#c3c2b7", "#fcfcfb"

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Helvetica Neue", "Helvetica", "Arial", "DejaVu Sans"],
    "font.size": 10,
    "axes.edgecolor": AXIS,
    "axes.labelcolor": INK2,
    "axes.titlecolor": INK,
    "axes.titlesize": 11,
    "axes.titleweight": "bold",
    "axes.titlelocation": "left",
    "axes.facecolor": SURFACE,
    "figure.facecolor": SURFACE,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "xtick.labelcolor": INK2,
    "ytick.labelcolor": INK2,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "axes.grid.axis": "y",
    "grid.color": GRID,
    "grid.linewidth": 0.8,
    "legend.frameon": False,
    "legend.fontsize": 9,
    "lines.solid_capstyle": "round",
    "lines.solid_joinstyle": "round",
})


def save(fig, name):
    FIG.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG / f"{name}.png", dpi=200, bbox_inches="tight")
    fig.savefig(FIG / f"{name}.pdf", bbox_inches="tight")
    plt.close(fig)
    print("wrote", FIG / f"{name}.png")


def ci95(x):
    x = np.asarray(x, dtype=float)
    x = x[~np.isnan(x)]
    if len(x) < 2:
        return 0.0
    return 1.96 * x.std(ddof=1) / np.sqrt(len(x))


def agg(df, by, col):
    g = df.groupby([by, "method"])[col]
    out = g.mean().to_frame("mean")
    out["ci"] = g.apply(ci95)
    return out.reset_index()


def line_panel(ax, df, by, col, methods, ylabel, logx=False, logy=False, pct=False):
    data = agg(df, by, col)
    for m in methods:
        if m not in data["method"].values:
            continue
        label, color, marker = METHODS[m]
        d = data[data["method"] == m].sort_values(by)
        d = d[~d["mean"].isna()]
        if d.empty:
            continue
        y = d["mean"] * (100 if pct else 1)
        ci = d["ci"] * (100 if pct else 1)
        ax.fill_between(d[by], y - ci, y + ci, color=color, alpha=0.10, linewidth=0)
        ax.plot(d[by], y, color=color, linewidth=1.8, marker=marker, markersize=6,
                markeredgecolor=SURFACE, markeredgewidth=1.2, label=label)
    if logx:
        ax.set_xscale("log")
    if logy:
        ax.set_yscale("log")
    ax.set_ylabel(ylabel)
    if pct:
        ax.set_ylim(bottom=0)


def legend_above(fig, axes, n_cols=3):
    handles, labels = [], []
    for ax in np.atleast_1d(axes):
        for h, l in zip(*ax.get_legend_handles_labels()):
            if l not in labels:
                handles.append(h)
                labels.append(l)
    fig.legend(handles, labels, loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=n_cols,
               handlelength=2.2, columnspacing=1.6)


def agent_ticks(ax, values):
    ax.set_xticks(values)
    ax.set_xticklabels([f"{v // 1000}K" if v >= 1000 else str(v) for v in values])
    ax.minorticks_off()


def load_csv(name):
    path = RAW / f"{name}.csv"
    if not path.exists():
        print("skip (missing)", path)
        return None
    return pd.read_csv(path)


# ---------------------------------------------------------------------------
def fig_scale():
    df = load_csv("scale")
    if df is None:
        return
    by = "n_agents_param"
    values = sorted(df[by].unique())
    methods = list(METHODS)

    fig, ax = plt.subplots(figsize=(6.4, 3.8))
    line_panel(ax, df, by, "success_rate", methods, "Discovery success (%)", logx=True, pct=True)
    agent_ticks(ax, values)
    ax.set_xlabel("Number of agents")
    ax.set_title("Success rate vs number of agents")
    legend_above(fig, ax)
    save(fig, "scale_success")

    fig, ax = plt.subplots(figsize=(6.4, 3.8))
    line_panel(ax, df, by, "msgs_per_query", methods, "Messages per request (log)", logx=True, logy=True)
    agent_ticks(ax, values)
    ax.set_xlabel("Number of agents")
    ax.set_title("Control + query overhead vs number of agents")
    legend_above(fig, ax)
    save(fig, "scale_overhead")

    fig, axes = plt.subplots(1, 2, figsize=(9.6, 3.6))
    useful = [m for m in methods if m != "chord"]   # Chord never succeeds, no hop/time data
    line_panel(axes[0], df, by, "hops", useful, "Hops per delivered request", logx=True)
    line_panel(axes[1], df, by, "time_ms", useful, "Completion time (ms)", logx=True)
    for ax, title in zip(axes, ["Hop count", "Task completion time"]):
        agent_ticks(ax, values)
        ax.set_xlabel("Number of agents")
        ax.set_title(title)
        ax.set_ylim(bottom=0)
    legend_above(fig, axes, n_cols=5)
    fig.tight_layout()
    save(fig, "scale_hops_time")


def fig_simple(name, by, xlabel, title, fname, pct_x=False):
    df = load_csv(name)
    if df is None:
        return
    fig, ax = plt.subplots(figsize=(6.4, 3.8))
    x = df.copy()
    if pct_x:
        x[by] = x[by] * 100
    line_panel(ax, x, by, "success_rate", list(METHODS), "Discovery success (%)", pct=True)
    ax.set_xlabel(xlabel)
    ax.set_title(title)
    legend_above(fig, ax)
    save(fig, fname)


def fig_radius():
    df = load_csv("radius")
    if df is None:
        return
    methods = ["agentroute", "agentroute_gnn", "greedy"]
    fig, axes = plt.subplots(1, 2, figsize=(9.6, 3.6))
    line_panel(axes[0], df, "radius", "success_rate", methods, "Discovery success (%)", pct=True)
    line_panel(axes[1], df, "radius", "ctrl_msgs", methods, "Control messages per run (log)", logy=True)
    for ax, title in zip(axes, ["Success vs advertisement radius R", "Control overhead vs R"]):
        ax.set_xlabel("Advertisement radius R (hops)")
        ax.set_title(title)
        ax.set_xticks(sorted(df["radius"].unique()))
    legend_above(fig, axes)
    fig.tight_layout()
    save(fig, "radius")


def fig_load():
    df = load_csv("load")
    if df is None:
        return
    fig, axes = plt.subplots(1, 2, figsize=(9.6, 3.6))
    line_panel(axes[0], df, "load", "success_rate", list(METHODS), "Discovery success (%)", pct=True)
    line_panel(axes[1], df, "load", "time_ms", [m for m in METHODS if m != "chord"],
               "Completion time (ms)")
    axes[1].set_ylim(bottom=0)
    for ax, title in zip(axes, ["Success vs network load", "Completion time vs network load"]):
        ax.set_xlabel("Load factor (requests and background traffic)")
        ax.set_title(title)
    legend_above(fig, axes)
    fig.tight_layout()
    save(fig, "load")


def smooth(y, w=15):
    y = np.asarray(y, dtype=float)
    if len(y) < w:
        return y
    k = np.ones(w) / w
    pad = np.concatenate([np.full(w // 2, y[0]), y, np.full(w - 1 - w // 2, y[-1])])
    return np.convolve(pad, k, mode="valid")


def fig_learning():
    curves = {k: load_csv(f"train_{k}") for k in ("mlp", "gnn")}
    curves = {k: v for k, v in curves.items() if v is not None}
    if not curves:
        return
    fig, axes = plt.subplots(1, 2, figsize=(9.6, 3.6))
    keys = {"mlp": "agentroute", "gnn": "agentroute_gnn"}
    for kind, df in curves.items():
        label, color, marker = METHODS[keys[kind]]
        axes[0].plot(df["episode"], smooth(df["return_per_query"]), color=color, linewidth=1.8,
                     label=label)
        val = df.dropna(subset=["val_success"])
        axes[1].plot(val["episode"], val["val_success"] * 100, color=color, linewidth=1.8,
                     marker=marker, markersize=6, markeredgecolor=SURFACE, markeredgewidth=1.2,
                     label=label)
    g = next(iter(curves.values()))
    label, color, _ = METHODS["greedy"]
    axes[1].axhline(g["greedy_val_success"].iloc[0] * 100, color=color, linewidth=1.8,
                    linestyle=(0, (4, 3)), label=f"{label} (reference)")
    axes[0].set_title("Training return per request (smoothed)")
    axes[0].set_xlabel("Episode")
    axes[0].set_ylabel("Return per request")
    axes[1].set_title("Validation success (epsilon = 0)")
    axes[1].set_xlabel("Episode")
    axes[1].set_ylabel("Discovery success (%)")
    legend_above(fig, axes)
    fig.tight_layout()
    save(fig, "learning_curve")


def bar_groups(ax, df, by, order, methods, col="success_rate"):
    data = agg(df, by, col)
    width = min(0.8 / len(methods), 0.3)
    for i, m in enumerate(methods):
        label, color, _ = METHODS[m]
        d = data[data["method"] == m].set_index(by).reindex(order)
        x = np.arange(len(order)) + (i - (len(methods) - 1) / 2) * (width + 0.02)
        ax.bar(x, d["mean"] * 100, width=width, color=color, label=label, edgecolor=SURFACE,
               linewidth=1.0, yerr=d["ci"] * 100, error_kw={"ecolor": INK2, "elinewidth": 0.8,
                                                            "capsize": 2})
    ax.set_xticks(np.arange(len(order)))
    ax.set_xticklabels(order)
    ax.set_ylabel("Discovery success (%)")


def fig_ablation():
    df = load_csv("ablation_summary")
    if df is not None:
        order = [s for s in ["mean", "k=2", "k=4", "k=8", "exact"] if s in df["summary"].unique()]
        fig, ax = plt.subplots(figsize=(6.4, 3.6))
        bar_groups(ax, df, "summary", order, ["agentroute", "greedy"])
        ax.set_xlabel("S-FIB summary per neighbour")
        ax.set_title("Effect of the S-FIB summary")
        legend_above(fig, ax, n_cols=2)
        save(fig, "ablation_summary")
    df = load_csv("ablation_header")
    if df is not None:
        order = [h for h in ["float32", "int8", "binary"] if h in df["header"].unique()]
        fig, ax = plt.subplots(figsize=(5.6, 3.6))
        bar_groups(ax, df, "header", order, ["agentroute", "greedy"])
        sizes = {"float32": "1536 B", "int8": "388 B", "binary": "48 B"}
        ax.set_xticklabels([f"{h}\n{sizes[h]}" for h in order])
        ax.set_xlabel("Intent header encoding")
        ax.set_title("Effect of compressing the intent header")
        legend_above(fig, ax, n_cols=2)
        save(fig, "ablation_header")


def fig_drop_reasons():
    df = load_csv("scale")
    if df is None:
        return
    d = df[df["n_agents_param"] == 1000]
    if d.empty:
        return
    reasons = {"wrong_agent": "Wrong agent accepted", "not_found": "No match found",
               "ttl": "TTL expired", "queue": "Queue overflow", "link": "Link loss",
               "stale_location": "Stale location", "handover": "Agent in handover",
               "node_down": "Node down", "registry_queue": "Registry overloaded",
               "no_route": "No route"}
    present = [r for r in reasons if f"drop_{r}" in d and d[f"drop_{r}"].mean() > 0.002]
    palette = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]
    methods = list(METHODS)
    means = d.groupby("method")[[f"drop_{r}" for r in present] + ["success_rate"]].mean().reindex(methods)
    fig, ax = plt.subplots(figsize=(7.2, 3.8))
    y = np.arange(len(methods))
    left = np.zeros(len(methods))
    for i, r in enumerate(present[:8]):
        vals = means[f"drop_{r}"].values * 100
        ax.barh(y, vals, left=left, height=0.55, color=palette[i], label=reasons[r],
                edgecolor=SURFACE, linewidth=1.0)
        left += vals
    ax.set_yticks(y)
    ax.set_yticklabels([f"{METHODS[m][0]}  ({s * 100:.0f}% success)"
                        for m, s in zip(methods, means["success_rate"].values)])
    ax.invert_yaxis()
    ax.grid(axis="x")
    ax.grid(axis="y", visible=False)
    ax.set_xlabel("Share of requests (%)")
    ax.set_title("Why requests fail (1,000 agents)")
    ax.set_xlim(0, 100)
    legend_above(fig, ax, n_cols=3)
    save(fig, "drop_reasons")


def fig_similarity():
    tau_path = ROOT / "results" / "tau.json"
    if not tau_path.exists():
        return
    from agentroute.embeddings import load_dataset_vectors
    data = load_dataset_vectors()
    sims = data["test_vecs"] @ data["desc_vecs"].T
    same = data["test_class"][:, None] == data["desc_class"][None, :]
    tau = json.loads(tau_path.read_text())["tau"]
    fig, ax = plt.subplots(figsize=(6.4, 3.4))
    bins = np.linspace(-0.2, 0.9, 45)
    ax.hist(sims[~same], bins=bins, density=True, color="#898781", alpha=0.45,
            label="Request vs other-class capability", edgecolor=SURFACE, linewidth=0.6)
    ax.hist(sims[same], bins=bins, density=True, color="#2a78d6", alpha=0.75,
            label="Request vs same-class capability", edgecolor=SURFACE, linewidth=0.6)
    ax.axvline(tau, color=INK, linewidth=1.2)
    ax.text(tau + 0.01, ax.get_ylim()[1] * 0.92, f"tau = {tau:.3f}", color=INK, fontsize=9)
    ax.set_xlabel("Cosine similarity (MiniLM, test paraphrases)")
    ax.set_ylabel("Density")
    ax.set_title("Paraphrased requests vs capability cards")
    legend_above(fig, ax, n_cols=2)
    save(fig, "similarity")


EXPERIMENTS = [("scale", "n_agents_param"), ("mobility", "speed"), ("failure", "failure"),
               ("radius", "radius"), ("load", "load"), ("ablation_summary", "summary"),
               ("ablation_header", "header")]
METRICS = ["success_rate", "time_ms", "hops", "msgs_per_query", "ctrl_msgs", "handovers"]


def export_tables():
    """Mean of every metric per (value, method): results/summary.json + results/tables.md.

    The report and the slides take their numbers from these files.
    """
    out, md = {}, []
    for name, by in EXPERIMENTS:
        df = load_csv(name)
        if df is None:
            continue
        values = list(dict.fromkeys(df.sort_values(by)[by].tolist()))
        methods = [m for m in METHODS if m in df["method"].unique()]
        g = df.groupby([by, "method"])[METRICS].mean()
        entry = {"param": by, "values": values, "methods": {}}
        for m in methods:
            entry["methods"][m] = {k: [None if pd.isna(g.loc[(v, m), k]) else round(float(g.loc[(v, m), k]), 4)
                                       for v in values] for k in METRICS}
        drop_cols = [c for c in df.columns if c.startswith("drop_")]
        if name == "scale":
            ref = 1000 if 1000 in values else values[len(values) // 2]
            d = df[df[by] == ref].groupby("method")[drop_cols].mean()
            entry["drops_at"] = ref
            entry["drops"] = {m: {c[5:]: round(float(d.loc[m, c]), 4) for c in drop_cols}
                              for m in methods if m in d.index}
        out[name] = entry
        md.append(f"\n### {name} (success %, mean of {df['seed'].nunique()} seeds)\n")
        md.append("| method | " + " | ".join(str(v) for v in values) + " |")
        md.append("|---" * (len(values) + 1) + "|")
        for m in methods:
            row = [f"{x * 100:.1f}" for x in entry["methods"][m]["success_rate"]]
            md.append(f"| {METHODS[m][0]} | " + " | ".join(row) + " |")
        for metric, label, fmt in (("time_ms", "time ms", "{:.1f}"), ("hops", "hops", "{:.2f}"),
                                   ("msgs_per_query", "messages / request", "{:.0f}")):
            md.append(f"\n{name}: {label}\n")
            md.append("| method | " + " | ".join(str(v) for v in values) + " |")
            md.append("|---" * (len(values) + 1) + "|")
            for m in methods:
                row = ["-" if x is None else fmt.format(x) for x in entry["methods"][m][metric]]
                md.append(f"| {METHODS[m][0]} | " + " | ".join(row) + " |")
    for kind in ("mlp", "gnn"):
        df = load_csv(f"train_{kind}")
        if df is not None:
            val = df.dropna(subset=["val_success"])
            out[f"train_{kind}"] = {
                "episode": val["episode"].tolist(),
                "val_success": val["val_success"].round(4).tolist(),
                "val_time_ms": val["val_time_ms"].round(2).tolist(),
                "val_return": val["val_return"].round(4).tolist(),
                "greedy_val_success": float(df["greedy_val_success"].iloc[0]),
                "greedy_val_time_ms": float(df["greedy_val_time_ms"].iloc[0]),
            }
    tau_path = ROOT / "results" / "tau.json"
    if tau_path.exists():
        from agentroute.embeddings import embed_texts, load_dataset_vectors
        data = load_dataset_vectors()
        sims = data["test_vecs"] @ data["desc_vecs"].T
        same = data["test_class"][:, None] == data["desc_class"][None, :]
        edges = np.round(np.arange(-0.2, 0.901, 0.05), 3)
        h_same, _ = np.histogram(sims[same], bins=edges)
        h_other, _ = np.histogram(sims[~same], bins=edges)
        example = embed_texts(["find the cars in this photo"])[0]
        card_sims = data["desc_vecs"] @ example
        order = np.argsort(-card_sims)[:3]
        out["similarity"] = {
            "tau": json.loads(tau_path.read_text()),
            "bins": [f"{0.0 if abs(a) < 1e-9 else a:.2f}" for a in edges[:-1]],
            "same_pct": (100 * h_same / h_same.sum()).round(2).tolist(),
            "other_pct": (100 * h_other / h_other.sum()).round(2).tolist(),
            "example": [{"card": data["desc_text"][i], "cos": round(float(card_sims[i]), 3)} for i in order],
        }
    (ROOT / "results" / "summary.json").write_text(json.dumps(out, indent=1))
    (ROOT / "results" / "tables.md").write_text("\n".join(md) + "\n")
    print("wrote results/summary.json and results/tables.md")


def main():
    export_tables()
    fig_similarity()
    fig_scale()
    fig_simple("mobility", "speed", "Mobile agent speed (m/s)", "Success rate vs mobility",
               "mobility_success")
    fig_simple("failure", "failure", "Failed routers (%)", "Success rate vs node failures",
               "failure_success", pct_x=True)
    fig_radius()
    fig_load()
    fig_learning()
    fig_ablation()
    fig_drop_reasons()


if __name__ == "__main__":
    main()
