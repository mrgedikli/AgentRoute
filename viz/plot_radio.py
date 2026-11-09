"""Figures and tables of the Sionna radio experiments (new files only; plots.py is not touched).

    python viz/plot_radio.py

Writes results/figures/radio_*.png|pdf and results/radio_tables.md.

Written with AI assistance (plotting).
"""
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plots import FIG, INK2, METHODS, RAW, ROOT, ROUTED, save  # noqa: E402

TABLES = ROOT / "results" / "radio_tables.md"
RADIO = {"constant": ("Fixed radio", "#898781"), "sionna": ("Sionna radio", "#2a78d6"),
         "sionna_plus10db": ("Sionna radio, +10 dB", "#1baf7a")}
ORDER = [m for m in METHODS if m != "chord"]


def ci(s):
    return 1.96 * s.std(ddof=1) / np.sqrt(len(s)) if len(s) > 1 else 0.0


def fig_table():
    fig, ax = plt.subplots(1, 2, figsize=(9, 3.4))
    for name, label in (("radio_lut", "Sionna radio"), ("radio_lut_plus10db", "Sionna radio, +10 dB")):
        z = np.load(ROOT / "results" / f"{name}.npz")
        color = RADIO["sionna" if name == "radio_lut" else "sionna_plus10db"][1]
        ax[0].plot(z["distance_m"], z["bler"], color=color, label=label, lw=2)
        ax[1].plot(z["distance_m"], z["attempt_pmf"][:, -1], color=color, label=label, lw=2)
    for a, title in zip(ax, ("First-transmission block error rate", "Packet drop after 4 HARQ attempts")):
        a.set_title(title)
        a.set_xlabel("UE-gNB distance (m)")
        a.axvline(250, color=INK2, lw=0.8, ls=":")
        a.set_ylim(0, 0.7)
    ax[0].legend()
    ax[1].text(255, 0.62, "half cell spacing", color=INK2, fontsize=8)
    save(fig, "radio_bler")


def fig_compare(df):
    g = df.groupby(["radio", "method"])["success_rate"]
    fig, ax = plt.subplots(figsize=(8.4, 3.6))
    w = 0.26
    for i, r in enumerate(RADIO):
        mean = [g.mean().get((r, m), np.nan) * 100 for m in ROUTED]
        err = [ci(g.get_group((r, m))) * 100 for m in ROUTED]
        ax.bar(np.arange(len(ROUTED)) + (i - 1) * w, mean, w, yerr=err, color=RADIO[r][1], label=RADIO[r][0],
               error_kw={"lw": 0.8, "capsize": 2})
    ax.set_xticks(range(len(ROUTED)), [METHODS[m][0].replace(" (", "\n(").replace(" ", "\n", 1) if m in ("greedy", "greedy_load", "registry", "sdht") else METHODS[m][0].replace(" (", "\n(") for m in ROUTED])
    ax.set_ylabel("Discovery success (%)")
    ax.set_title("Success with a fixed and a Sionna-based radio (1,000 agents)")
    ax.legend(ncol=3, loc="upper center", bbox_to_anchor=(0.5, -0.12))
    save(fig, "radio_compare")


def fig_mobility(df, ref):
    fig, ax = plt.subplots(figsize=(6.2, 3.6))
    for m in ROUTED:
        label, color, marker = METHODS[m]
        for data, ls, tag in ((df, "-", "Sionna radio"), (ref, "--", "fixed radio")):
            d = data[data.method == m].groupby("speed")["success_rate"]
            ax.plot(d.mean().index, d.mean() * 100, color=color, marker=marker, ls=ls, ms=4,
                    lw=1.6 if ls == "-" else 1.0, alpha=1.0 if ls == "-" else 0.55,
                    label=label if ls == "-" else None)
    ax.set_xlabel("Mobile agent speed (m/s)")
    ax.set_ylabel("Discovery success (%)")
    ax.set_title("Mobility: Sionna radio (solid) vs fixed radio (dashed)")
    ax.legend(ncol=3, loc="upper center", bbox_to_anchor=(0.5, -0.2))
    save(fig, "radio_mobility")


def md(table):
    """Markdown table without the optional `tabulate` dependency."""
    head = "| " + " | ".join([str(table.index.name or "")] + [str(c) for c in table.columns]) + " |"
    rule = "|" + "---|" * (len(table.columns) + 1)
    rows = ["| " + " | ".join([str(i)] + [str(v) for v in r]) + " |" for i, r in zip(table.index, table.values)]
    return "\n".join([head, rule] + rows)


def tables(comp, mob):
    out = [f"### radio_compare (mean of {comp['seed'].nunique()} seeds, 1,000 agents)\n"]
    for col, name in (("success_rate", "success %"), ("time_ms", "time ms"), ("hops", "hops"),
                      ("msgs_per_query", "messages / request")):
        t = comp.groupby(["method", "radio"])[col].mean().unstack("radio")[list(RADIO)]
        t = t.loc[ORDER + ["chord"]] * (100 if col == "success_rate" else 1)
        out += [f"\n{name}\n", md(t.round(1 if col != "hops" else 2)), "\n"]
    drops = [c for c in comp.columns if c.startswith("drop_")]
    t = comp.groupby(["radio", "method"])[drops].mean().loc[list(RADIO)] * 100
    out += ["\ndrop reasons (% of all requests)\n", md(t.round(1)), "\n"]
    if mob is not None:
        t = mob.groupby(["method", "speed"])["success_rate"].mean().unstack("speed").loc[ORDER + ["chord"]] * 100
        out += ["\n### radio_mobility (success %, Sionna radio)\n", md(t.round(1)), "\n"]
    TABLES.write_text("\n".join(out))


if __name__ == "__main__":
    fig_table()
    comp = pd.read_csv(RAW / "radio_compare.csv")
    fig_compare(comp)
    mob = None
    if (RAW / "radio_mobility.csv").exists():
        mob = pd.read_csv(RAW / "radio_mobility.csv")
        fig_mobility(mob, pd.read_csv(RAW / "mobility.csv"))
    tables(comp, mob)
    print("wrote radio figures and", TABLES)
