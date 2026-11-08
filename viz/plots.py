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
    "agentroute":     ("AgentRoute (DQN)",      "#2a78d6", "o"),
    "agentroute_gnn": ("AgentRoute (GNN)",      "#eb6834", "D"),
    "greedy":         ("Greedy semantic",       "#1baf7a", "s"),
    "greedy_load":    ("Load-aware greedy",     "#0f8a8a", "P"),
    "spfr":           ("SPFR-style",            "#6250d6", "*"),
    "flooding":       ("Flooding",              "#eda100", "^"),
    "registry":       ("Central registry",      "#e87ba4", "v"),
    "registry3":      ("Registry (3 replicas)", "#a8437a", "<"),
    "sdht":           ("Semantic DHT",          "#7a6a5a", "h"),
    "chord":          ("Chord (exact)",         "#008300", "X"),
}
# the GNN is close to the DQN and would only clutter the main charts
MAIN = [m for m in METHODS if m != "agentroute_gnn"]
ROUTED = [m for m in MAIN if m != "chord"]      # Chord never succeeds, no hop/time data
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
def oracle_line(ax, df, by, factor=1.0):
    """What a method with perfect knowledge of all attached agents could achieve."""
    g = df.groupby(by)["oracle_best"].mean() * 100
    ax.plot(np.asarray(g.index, dtype=float) * factor, g.values, color=INK, linewidth=1.1,
            linestyle=(0, (2, 2)), label="Matching ceiling (oracle)")


def fig_scale():
    df = load_csv("scale")
    if df is None:
        return
    by = "n_agents_param"
    values = sorted(df[by].unique())

    fig, ax = plt.subplots(figsize=(7.2, 4.0))
    line_panel(ax, df, by, "success_rate", MAIN, "Discovery success (%)", logx=True, pct=True)
    oracle_line(ax, df, by)
    agent_ticks(ax, values)
    ax.set_xlabel("Number of agents")
    ax.set_title("Success rate vs number of agents")
    legend_above(fig, ax, n_cols=4)
    save(fig, "scale_success")

    fig, axes = plt.subplots(1, 2, figsize=(9.6, 3.8))
    line_panel(axes[0], df, by, "ctrl_kB_per_s", [m for m in ROUTED if m != "flooding"],
               "Control traffic, whole network (kB/s, log)", logx=True, logy=True)
    line_panel(axes[1], df, by, "query_kB_per_query", ROUTED, "Query traffic per request (kB, log)",
               logx=True, logy=True)
    for ax, title in zip(axes, ["Paid per second (advertisements, registrations)",
                                "Paid per request (lookups, floods, forwarding)"]):
        agent_ticks(ax, values)
        ax.set_xlabel("Number of agents")
        ax.set_title(title)
    legend_above(fig, axes, n_cols=4)
    fig.tight_layout()
    save(fig, "scale_overhead")

    fig, axes = plt.subplots(1, 2, figsize=(9.6, 3.6))
    line_panel(axes[0], df, by, "hops", ROUTED, "Hops per delivered request", logx=True)
    line_panel(axes[1], df, by, "time_ms", [m for m in ROUTED if m != "flooding"],
               "Completion time (ms)", logx=True)
    for ax, title in zip(axes, ["Hop count", "Task completion time (flooding: 230+ ms, not shown)"]):
        agent_ticks(ax, values)
        ax.set_xlabel("Number of agents")
        ax.set_title(title)
        ax.set_ylim(bottom=0)
    legend_above(fig, axes, n_cols=4)
    fig.tight_layout()
    save(fig, "scale_hops_time")


def fig_simple(name, by, xlabel, title, fname, pct_x=False):
    df = load_csv(name)
    if df is None:
        return
    fig, ax = plt.subplots(figsize=(7.2, 4.0))
    x = df.copy()
    if pct_x:
        x[by] = x[by] * 100
    line_panel(ax, x, by, "success_rate", MAIN, "Discovery success (%)", pct=True)
    oracle_line(ax, x, by)
    ax.set_xlabel(xlabel)
    ax.set_title(title)
    legend_above(fig, ax, n_cols=4)
    save(fig, fname)


def fig_mobility_cost():
    a, b = load_csv("mobility"), load_csv("mobility_small")
    if a is None or b is None:
        return
    methods = ["agentroute", "greedy", "spfr", "registry3", "sdht"]
    fig, axes = plt.subplots(1, 2, figsize=(9.6, 3.6))
    for ax, df, title in zip(axes, (a, b), ("500 m cells", "150 m cells")):
        line_panel(ax, df, "speed", "ctrl_kB_per_s", methods, "Control traffic (kB/s, log)", logy=True)
        ax.set_xlabel("Mobile agent speed (m/s)")
        ax.set_title(f"Cost of mobility, {title}")
    legend_above(fig, axes, n_cols=5)
    fig.tight_layout()
    save(fig, "mobility_cost")


def fig_radius():
    df = load_csv("radius")
    if df is None:
        return
    methods = ["agentroute", "greedy", "greedy_load"]
    fig, axes = plt.subplots(1, 2, figsize=(9.6, 3.6))
    line_panel(axes[0], df, "radius", "success_rate", methods, "Discovery success (%)", pct=True)
    oracle_line(axes[0], df, "radius")
    line_panel(axes[1], df, "radius", "ctrl_kB_per_s", methods, "Control traffic (kB/s, log)", logy=True)
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
    line_panel(axes[0], df, "load", "success_rate", MAIN, "Discovery success (%)", pct=True)
    oracle_line(axes[0], df, "load")
    line_panel(axes[1], df, "load", "time_ms", [m for m in ROUTED if m != "flooding"],
               "Completion time (ms)")
    axes[1].set_ylim(bottom=0)
    for ax, title in zip(axes, ["Success vs network load", "Completion time vs network load"]):
        ax.set_xlabel("Load factor (requests and background traffic)")
        ax.set_title(title)
    legend_above(fig, axes, n_cols=4)
    fig.tight_layout()
    save(fig, "load")


def fig_rate():
    df = load_csv("rate")
    if df is None:
        return
    df = df.copy()
    df["total_kB_per_s"] = df["ctrl_kB_per_s"] + df["query_kB_per_query"] * df["rate"]
    methods = [m for m in MAIN if m in df["method"].unique()]
    fig, ax = plt.subplots(figsize=(7.2, 4.0))
    line_panel(ax, df, "rate", "total_kB_per_s", methods, "Total traffic, whole network (kB/s, log)",
               logx=True, logy=True)
    ax.set_xlabel("Requests per second in the whole network (log)")
    ax.set_title("Total traffic vs request rate (1,000 agents)")
    ax.set_xticks(sorted(df["rate"].unique()))
    ax.set_xticklabels([f"{v:g}" for v in sorted(df["rate"].unique())])
    ax.minorticks_off()
    legend_above(fig, ax, n_cols=4)
    save(fig, "rate_crossover")


def fig_tau():
    df = load_csv("tau")
    if df is None:
        return
    fig, ax = plt.subplots(figsize=(7.2, 4.0))
    for m in [m for m in MAIN if m in df["method"].unique()]:
        label, color, marker = METHODS[m]
        d = df[df["method"] == m].groupby("tau")[["success_rate", "precision"]].mean().sort_index()
        ax.plot((1 - d["precision"]) * 100, d["success_rate"] * 100, color=color, linewidth=1.6,
                marker=marker, markersize=6, markeredgecolor=SURFACE, markeredgewidth=1.0, label=label)
    tau = json.loads((ROOT / "results" / "tau.json").read_text())["tau"]
    ax.set_xlabel("Wrong deliveries among all deliveries (%)")
    ax.set_ylabel("Discovery success (%)")
    ax.set_title(f"Threshold tau: more success costs more wrong deliveries (we use tau = {tau})")
    ax.grid(axis="x")
    legend_above(fig, ax, n_cols=3)
    save(fig, "tau_tradeoff")


def fig_matched():
    path = RAW / "matched.json"
    if not path.exists():
        return
    data = json.loads(path.read_text())
    pairs = [("agentroute vs greedy", "DQN vs greedy"), ("agentroute vs greedy_load", "DQN vs load-aware"),
             ("agentroute vs spfr", "DQN vs SPFR-style")]
    names = list(data)
    fig, axes = plt.subplots(1, 2, figsize=(9.6, 3.6))
    width = 0.8 / len(pairs)
    colors = ["#1baf7a", "#0f8a8a", "#6250d6"]
    for i, ((key, label), color) in enumerate(zip(pairs, colors)):
        x = np.arange(len(names)) + (i - (len(pairs) - 1) / 2) * width
        diff = [data[n][key]["success_diff_points"] for n in names]
        lo = [data[n][key]["success_diff_ci95"][0] for n in names]
        hi = [data[n][key]["success_diff_ci95"][1] for n in names]
        err = [np.array(diff) - np.array(lo), np.array(hi) - np.array(diff)]
        axes[0].bar(x, diff, width=width * 0.92, color=color, label=label, yerr=err,
                    error_kw={"ecolor": INK2, "elinewidth": 0.8, "capsize": 2})
        t = [data[n][key]["time_ms"][0] - data[n][key]["time_ms"][1] for n in names]
        axes[1].bar(x, t, width=width * 0.92, color=color)
    for ax in axes:
        ax.axhline(0, color=AXIS, linewidth=1.0)
        ax.set_xticks(np.arange(len(names)))
        ax.set_xticklabels([n.replace(", ", "\n") for n in names])
    axes[0].set_ylabel("Success difference (points)")
    axes[0].set_title("Success: DQN minus the other method (95% CI)")
    axes[1].set_ylabel("Time difference (ms)")
    axes[1].set_title("Time on requests both delivered (negative = DQN faster)")
    legend_above(fig, axes, n_cols=3)
    fig.tight_layout()
    save(fig, "matched")


def smooth(y, w=15):
    y = np.asarray(y, dtype=float)
    if len(y) < w:
        return y
    k = np.ones(w) / w
    pad = np.concatenate([np.full(w // 2, y[0]), y, np.full(w - 1 - w // 2, y[-1])])
    return np.convolve(pad, k, mode="valid")


def fig_learning():
    """Validation only (no exploration). The training return would rise anyway as epsilon falls."""
    curves = {k: load_csv(f"train_{k}") for k in ("mlp", "gnn")}
    curves = {k: v for k, v in curves.items() if v is not None}
    if not curves:
        return
    fig, axes = plt.subplots(1, 2, figsize=(9.6, 3.6))
    keys = {"mlp": "agentroute", "gnn": "agentroute_gnn"}
    for kind, df in curves.items():
        label, color, marker = METHODS[keys[kind]]
        val = df.dropna(subset=["val_success"])
        for ax, col, factor in zip(axes, ("val_return", "val_success"), (1, 100)):
            ax.plot(val["episode"], val[col] * factor, color=color, linewidth=1.8, marker=marker,
                    markersize=5, markeredgecolor=SURFACE, markeredgewidth=1.0, label=label)
    g = next(iter(curves.values()))
    for method, ret, succ in (("greedy", "greedy_val_return", "greedy_val_success"),
                              ("greedy_load", "load_val_return", "load_val_success")):
        label, color, _ = METHODS[method]
        axes[0].axhline(g[ret].iloc[0], color=color, linewidth=1.8, linestyle=(0, (4, 3)), label=f"{label} (reference)")
        axes[1].axhline(g[succ].iloc[0] * 100, color=color, linewidth=1.8, linestyle=(0, (4, 3)))
    axes[0].set_title("Validation return per request")
    axes[0].set_ylabel("Return per request")
    axes[1].set_title("Validation success")
    axes[1].set_ylabel("Discovery success (%)")
    for ax in axes:
        ax.set_xlabel("Episode")
    legend_above(fig, axes, n_cols=4)
    fig.tight_layout()
    save(fig, "learning_curve")


def bar_groups(ax, df, by, order, methods, col="success_rate", pct=True):
    data = agg(df, by, col)
    width = min(0.8 / len(methods), 0.3)
    for i, m in enumerate(methods):
        label, color, _ = METHODS[m]
        d = data[data["method"] == m].set_index(by).reindex(order)
        x = np.arange(len(order)) + (i - (len(methods) - 1) / 2) * (width + 0.02)
        factor = 100 if pct else 1
        ax.bar(x, d["mean"] * factor, width=width, color=color, label=label, edgecolor=SURFACE,
               linewidth=1.0, yerr=d["ci"] * factor, error_kw={"ecolor": INK2, "elinewidth": 0.8,
                                                               "capsize": 2})
    ax.set_xticks(np.arange(len(order)))
    ax.set_xticklabels(order)
    if pct:
        ax.set_ylabel("Discovery success (%)")


def fig_ablation():
    df = load_csv("ablation_summary")
    if df is not None:
        order = [x for x in ["mean", "k=8, no tier", "k=2", "k=4", "k=8", "k=16", "k=32", "exact"]
                 if x in df["summary"].unique()]
        methods = ["agentroute", "greedy", "greedy_load"]
        fig, axes = plt.subplots(1, 2, figsize=(10.4, 3.8))
        bar_groups(axes[0], df, "summary", order, methods)
        axes[0].set_title("S-FIB content vs success")
        axes[0].tick_params(axis="x", labelrotation=30)
        bar_groups(axes[1], df, "summary", order, methods, col="ctrl_kB_per_s", pct=False)
        axes[1].set_ylabel("Control traffic (kB/s, log)")
        axes[1].set_yscale("log")
        axes[1].set_title("S-FIB content vs control traffic")
        axes[1].tick_params(axis="x", labelrotation=30)
        legend_above(fig, axes, n_cols=3)
        fig.tight_layout()
        save(fig, "ablation_summary")
    df = load_csv("ablation_header")
    if df is not None:
        order = [h for h in ["float32", "int8", "binary"] if h in df["header"].unique()]
        fig, ax = plt.subplots(figsize=(5.6, 3.6))
        bar_groups(ax, df, "header", order, ["agentroute", "greedy", "greedy_load"])
        sizes = {"float32": "1536 B", "int8": "388 B", "binary": "48 B"}
        ax.set_xticklabels([f"{h}\n{sizes[h]}" for h in order])
        ax.set_xlabel("Intent header encoding")
        ax.set_title("Effect of compressing the intent header")
        legend_above(fig, ax, n_cols=3)
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
    methods = MAIN
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


EXPERIMENTS = [("scale", "n_agents_param"), ("mobility", "speed"), ("mobility_small", "speed"),
               ("failure", "failure"), ("radius", "radius"), ("load", "load"), ("rate", "rate"),
               ("tau", "tau"), ("ablation_summary", "summary"), ("ablation_header", "header"),
               ("ablation_accept", "accept"), ("ablation_threshold", "threshold"), ("ablation_window", "window")]
METRICS = ["success_rate", "oracle_best", "success_solvable", "precision", "time_ms", "hops",
           "msgs_per_query", "ctrl_msgs_per_s", "ctrl_kB_per_s", "query_msgs_per_query",
           "query_kB_per_query", "handovers", "update_msgs"]


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
        if name == "failure":
            # the registry's mean hides whether its server happened to be among the failed routers
            entry["registry_by_server"] = {}
            for v in values:
                r = df[(df[by] == v) & (df["method"] == "registry")]
                up, down = r[r["servers_alive"] > 0], r[r["servers_alive"] == 0]
                entry["registry_by_server"][str(v)] = {
                    "up": None if up.empty else round(float(up["success_rate"].mean()), 4), "n_up": len(up),
                    "down": None if down.empty else round(float(down["success_rate"].mean()), 4), "n_down": len(down)}
        out[name] = entry
        md.append(f"\n### {name} (success %, mean of {df['seed'].nunique()} seeds)\n")
        md.append("| method | " + " | ".join(str(v) for v in values) + " |")
        md.append("|---" * (len(values) + 1) + "|")
        for m in methods:
            row = [f"{x * 100:.1f}" for x in entry["methods"][m]["success_rate"]]
            md.append(f"| {METHODS[m][0]} | " + " | ".join(row) + " |")
        for metric, label, fmt in (("oracle_best", "matching ceiling (fraction)", "{:.3f}"),
                                   ("precision", "precision (right / delivered)", "{:.3f}"),
                                   ("time_ms", "time ms", "{:.1f}"), ("hops", "hops", "{:.2f}"),
                                   ("ctrl_kB_per_s", "control kB/s", "{:.0f}"),
                                   ("query_kB_per_query", "query kB / request", "{:.1f}")):
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
                "greedy_val_return": float(df["greedy_val_return"].iloc[0]),
                "load_val_success": float(df["load_val_success"].iloc[0]),
                "load_val_time_ms": float(df["load_val_time_ms"].iloc[0]),
                "load_val_return": float(df["load_val_return"].iloc[0]),
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
    for name in ("handover_cost", "matched"):
        path = RAW / f"{name}.json"
        if path.exists():
            out[name] = json.loads(path.read_text())
    (ROOT / "results" / "summary.json").write_text(json.dumps(out, indent=1))
    (ROOT / "results" / "tables.md").write_text("\n".join(md) + "\n")
    print("wrote results/summary.json and results/tables.md")


def main():
    export_tables()
    fig_similarity()
    fig_scale()
    fig_simple("mobility", "speed", "Mobile agent speed (m/s)", "Success rate vs mobility (500 m cells)",
               "mobility_success")
    fig_simple("mobility_small", "speed", "Mobile agent speed (m/s)", "Success rate vs mobility (150 m cells)",
               "mobility_small_success")
    fig_mobility_cost()
    fig_simple("failure", "failure", "Failed routers (%)", "Success rate vs node failures",
               "failure_success", pct_x=True)
    fig_radius()
    fig_load()
    fig_rate()
    fig_tau()
    fig_matched()
    fig_learning()
    fig_ablation()
    fig_drop_reasons()


if __name__ == "__main__":
    main()
