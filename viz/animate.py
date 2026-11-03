"""Presentation animations (GIF + MP4) from the demo event logs.

    python viz/animate.py              # both videos
    python viz/animate.py --only demo

1. agentroute_demo: advertisements fill the S-FIBs, a request travels hop by
   hop to a capable agent, a phone changes cell (withdraw / announce).
2. greedy_vs_agentroute: the same request in the same scenario, routed by
   greedy forwarding and by the DQN side by side.

Every scene is built from real events of the log; nothing is staged. If the
log has no suitable event for a scene, the scene is skipped.

Written with AI assistance (visualisation).
"""
import argparse
import json
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib import animation  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
LOGS = ROOT / "results" / "logs" / "demo"
OUT = ROOT / "results" / "figures"

FPS = 20
SURFACE, INK, INK2, MUTED = "#fcfcfb", "#0b0b0b", "#52514e", "#898781"
LINK, GRID = "#c3c2b7", "#e1e0d9"
BLUE, AQUA = "#2a78d6", "#1baf7a"
GOOD, CRITICAL, SERIOUS = "#0ca30c", "#d03b3b", "#ec835a"
METHOD_COLOR = {"agentroute": BLUE, "agentroute_gnn": "#eb6834", "greedy": AQUA}
METHOD_LABEL = {"agentroute": "AgentRoute (DQN)", "agentroute_gnn": "AgentRoute (GNN)",
                "greedy": "Greedy semantic"}


# ---------------------------------------------------------------------------
class Run:
    """Parsed log of one demo run."""

    def __init__(self, method, log_dir=None):
        d = Path(log_dir) if log_dir else LOGS / method
        self.topo = json.loads((d / "topology.json").read_text())
        self.method = self.topo["meta"]["method"]
        self.events = [json.loads(line) for line in (d / "events.jsonl").read_text().splitlines() if line]
        self.pos = {n["id"]: (n["x"], n["y"]) for n in self.topo["nodes"]}
        self.kind = {n["id"]: n["kind"] for n in self.topo["nodes"]}
        self.agents = {a["id"]: a for a in self.topo["agents"]}
        self.queries, self.hops, self.outcome = {}, defaultdict(list), {}
        self.handovers, self.adverts = [], []
        self.moves = defaultdict(list)
        self.load = defaultdict(list)
        for e in self.events:
            t = e["type"]
            if t == "query":
                self.queries[e["pkt"]] = e
            elif t == "hop":
                self.hops[e["pkt"]].append(e)
            elif t in ("deliver", "drop"):
                self.outcome[e["pkt"]] = e
            elif t == "handover":
                self.handovers.append(e)
            elif t in ("adv", "withdraw"):
                self.adverts.append(e)
            elif t == "move":
                self.moves[e["agent"]].append((e["t"], e["x"], e["y"]))
            elif t == "load":
                self.load[e["node"]].append((e["t"], e["busy"]))
        self.classes = self.topo["meta"]["classes"]

    def agent_xy(self, a, t):
        tr = self.moves.get(a)
        if not tr:
            return self.agents[a]["x"], self.agents[a]["y"]
        ts = [p[0] for p in tr]
        if t <= ts[0]:
            return tr[0][1], tr[0][2]
        i = int(np.searchsorted(ts, t))
        if i >= len(tr):
            return tr[-1][1], tr[-1][2]
        (t0, x0, y0), (t1, x1, y1) = tr[i - 1], tr[i]
        f = (t - t0) / max(t1 - t0, 1e-9)
        return x0 + f * (x1 - x0), y0 + f * (y1 - y0)

    def busy(self, node, t):
        state = False
        for ts, b in self.load.get(node, []):
            if ts <= t:
                state = b
        return state

    def path(self, pid):
        hops = self.hops.get(pid, [])
        return [h["from"] for h in hops] + ([hops[-1]["to"]] if hops else [])


# ---------------------------------------------------------------------------
def draw_static(ax, run, title=None):
    ax.set_facecolor(SURFACE)
    xs = [p[0] for p in run.pos.values()]
    ys = [p[1] for p in run.pos.values()]
    pad = 320
    ax.set_xlim(min(xs) - pad, max(xs) + pad)
    ax.set_ylim(min(ys) - pad, max(ys) + pad)
    ax.set_aspect("equal")
    ax.axis("off")
    spacing = 500
    for n, (x, y) in run.pos.items():
        if run.kind[n] == "gnb":
            ax.add_patch(plt.Circle((x, y), spacing * 0.56, color="#eef3fb", zorder=0, lw=0))
    style = {"xn": (LINK, 1.0, "-"), "backhaul": (LINK, 0.8, "-"), "core": ("#898781", 1.6, "-"),
             "cloud": ("#898781", 1.6, (0, (4, 3)))}
    for l in run.topo["links"]:
        c, w, ls = style[l["kind"]]
        (x1, y1), (x2, y2) = run.pos[l["u"]], run.pos[l["v"]]
        ax.plot([x1, x2], [y1, y2], color=c, lw=w, ls=ls, zorder=1)
    for n, (x, y) in run.pos.items():
        k = run.kind[n]
        if k == "gnb":
            ax.scatter(x, y, s=150, marker="s", color="#ffffff", edgecolor=INK2, lw=1.4, zorder=4)
        elif k == "core":
            ax.scatter(x, y, s=230, marker="o", color="#52514e", edgecolor=SURFACE, lw=1.5, zorder=4)
        else:
            ax.scatter(x, y, s=420, marker="h", color="#52514e", edgecolor=SURFACE, lw=1.5, zorder=4)
            ax.text(x, y - 150, "Cloud", ha="center", va="top", color=INK2, fontsize=9)
    if title:
        ax.set_title(title, color=INK, fontsize=12, fontweight="bold", loc="left")


def draw_legend(ax):
    ax.axis("off")
    items = [
        ("s", "#ffffff", INK2, 120, "gNB + edge router (AgentRoute node)"),
        ("o", "#52514e", SURFACE, 160, "Core router (AgentRoute node)"),
        ("h", "#52514e", SURFACE, 220, "Cloud data centre"),
        ("o", MUTED, MUTED, 30, "Agent (fixed or mobile)"),
        ("o", BLUE, SURFACE, 90, "Task packet / tracked phone"),
    ]
    for i, (marker, fc, ec, size, label) in enumerate(items):
        y = 0.97 - i * 0.065
        ax.scatter([0.03], [y], marker=marker, s=size, color=fc, edgecolor=ec, lw=1.4,
                   transform=ax.transAxes, clip_on=False)
        ax.text(0.09, y, label, fontsize=11, color=INK2, va="center", transform=ax.transAxes)
    rings = [(GOOD, "Serving agent / announce"), (CRITICAL, "Withdraw (old cell)")]
    for i, (color, label) in enumerate(rings):
        y = 0.97 - (len(items) + i) * 0.065
        ax.scatter([0.03], [y], s=110, facecolor="none", edgecolor=color, lw=2.2,
                   transform=ax.transAxes, clip_on=False)
        ax.text(0.09, y, label, fontsize=11, color=INK2, va="center", transform=ax.transAxes)
    ax.plot([0.0, 0.06], [0.97 - 7 * 0.065] * 2, color=BLUE, lw=2, ls=(0, (3, 2)),
            transform=ax.transAxes, clip_on=False)
    ax.text(0.09, 0.97 - 7 * 0.065, "Capability advertisement", fontsize=11, color=INK2,
            va="center", transform=ax.transAxes)


def lerp(a, b, f):
    return a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f


class Animator:
    """Turns a list of frame specs into matplotlib artists."""

    def __init__(self, fig, axes, runs, info_ax=None, steps=None):
        self.fig, self.axes, self.runs = fig, axes, runs
        self.info = info_ax
        self.dynamic = []
        self.agent_sc = []
        for ax, run in zip(axes, runs):
            ids = sorted(run.agents)
            xy = np.array([run.agent_xy(a, 0) for a in ids])
            self.agent_sc.append((ids, ax.scatter(xy[:, 0], xy[:, 1], s=12, color=MUTED,
                                                  alpha=0.65, lw=0, zorder=3)))
        self.header = fig.text(0.03, 0.955, "", fontsize=17, fontweight="bold", color=INK, va="top")
        self.sub = fig.text(0.03, 0.905, "", fontsize=12, color=INK2, va="top")
        self.footer = fig.text(0.03, 0.03, "", fontsize=11, color=INK2, va="bottom")
        self.step_texts = []
        if info_ax is not None:
            draw_legend(info_ax)
            for i, step in enumerate(steps or []):
                self.step_texts.append(info_ax.text(0.0, 0.40 - i * 0.075, step, fontsize=12,
                                                    transform=info_ax.transAxes, color=MUTED))
            self.caption = info_ax.text(0.0, 0.10, "", fontsize=12, color=INK, wrap=True,
                                        transform=info_ax.transAxes, va="top")

    def clear(self):
        for a in self.dynamic:
            a.remove()
        self.dynamic = []

    def update(self, spec):
        self.clear()
        self.header.set_text(spec.get("title", ""))
        self.sub.set_text(spec.get("subtitle", ""))
        self.footer.set_text(spec.get("footer", ""))
        for i, t in enumerate(self.step_texts):
            current = spec.get("scene") == i + 1
            t.set_color(INK if current else MUTED)
            t.set_fontweight("bold" if current else "normal")
        if self.info is not None:
            self.caption.set_text(spec.get("caption", ""))
        for i, (ax, run) in enumerate(zip(self.axes, self.runs)):
            p = spec["panels"][i] if "panels" in spec else spec
            ids, sc = self.agent_sc[i]
            t = p.get("t", 0.0)
            sc.set_offsets(np.array([run.agent_xy(a, t) for a in ids]))
            for node in p.get("busy", []):
                x, y = run.pos[node]
                self.dynamic.append(ax.scatter(x, y, s=600, color=SERIOUS, alpha=0.35, lw=0, zorder=2))
                self.dynamic.append(ax.text(x + 60, y + 60, "busy", color=INK2, fontsize=8, zorder=6))
            for (a, b, alpha, color) in p.get("lines", []):
                self.dynamic += ax.plot([a[0], b[0]], [a[1], b[1]], color=color, lw=2.2, alpha=alpha,
                                        ls=(0, (3, 2)), zorder=5)
            for seg, color in p.get("trail", []):
                self.dynamic += ax.plot([seg[0][0], seg[1][0]], [seg[0][1], seg[1][1]], color=color,
                                        lw=3.0, zorder=6, solid_capstyle="round")
            for (x, y, color, size) in p.get("rings", []):
                self.dynamic.append(ax.scatter(x, y, s=size, facecolor="none", edgecolor=color,
                                               lw=2.5, zorder=7))
            for (x, y, color) in p.get("dots", []):
                self.dynamic.append(ax.scatter(x, y, s=110, color=color, edgecolor=SURFACE, lw=2,
                                               zorder=8))
            for (x, y, text) in p.get("labels", []):
                self.dynamic.append(ax.text(x, y, text, fontsize=9, color=INK, zorder=9,
                                            bbox=dict(boxstyle="round,pad=0.3", fc="#ffffff",
                                                      ec=GRID, lw=0.8)))
            if p.get("caption") and self.info is None:
                self.dynamic.append(ax.text(0.02, 0.02, p["caption"], transform=ax.transAxes,
                                            fontsize=10.5, color=INK, va="bottom",
                                            bbox=dict(boxstyle="round,pad=0.4", fc="#ffffff",
                                                      ec=GRID, lw=0.8)))
        return []


def packet_frames(run, pid, n_per_hop, color, t_agents, title, subtitle, hold=20):
    """Frames of one packet moving along its real path."""
    path = run.path(pid)
    out = run.outcome.get(pid, {})
    q = run.queries[pid]
    frames = []
    src = run.agent_xy(q["agent"], q["t"])
    start = run.pos[q["router"]]
    legs = [(src, start)] + [(run.pos[a], run.pos[b]) for a, b in zip(path, path[1:])]
    final = None
    if out.get("type") == "deliver":
        final = run.agent_xy(out["agent"], out["t"])
        legs.append((run.pos[path[-1]] if path else start, final))
    trail = []
    for a, b in legs:
        for k in range(n_per_hop):
            f = (k + 1) / n_per_hop
            frames.append({"t": t_agents,
                           "trail": [(s, color) for s in trail] + [((a, lerp(a, b, f)), color)],
                           "dots": [(*lerp(a, b, f), color)],
                           "rings": [(*src, color, 160)], "title": title, "subtitle": subtitle,
                           "caption": "Each router scores its neighbours\nwith its S-FIB and forwards the\npacket to the best one"})
        trail.append((a, b))
    end = {"t": t_agents, "trail": [(s, color) for s in trail], "rings": [(*src, color, 160)],
           "title": title, "subtitle": subtitle}
    if out.get("type") == "deliver":
        ag = run.agents[out["agent"]]
        end["rings"].append((*final, GOOD, 260))
        end["labels"] = [(final[0] + 70, final[1] + 70, f"agent {ag['id']}: {ag['class_name']}")]
        end["caption"] = (f"Delivered to a capable agent\nin {out['hops']} hops, "
                          f"{(out['t'] - q['t']) * 1000:.0f} ms")
    else:
        where = out.get("at")
        if where is not None:
            end["rings"].append((*run.pos[where], CRITICAL, 300))
        end["caption"] = f"Dropped ({out.get('reason', 'unknown')})"
    frames += [dict(end) for _ in range(hold)]
    return frames


def pick_packet(run, after=3.0, min_hops=2, max_hops=5):
    best = None
    for pid, q in run.queries.items():
        out = run.outcome.get(pid)
        if q["t"] < after or not out or out["type"] != "deliver":
            continue
        n = len(run.hops.get(pid, []))
        if min_hops <= n <= max_hops and any(run.kind[h["to"]] == "core" for h in run.hops[pid]):
            if best is None or n > len(run.hops[best]):
                best = pid
    return best


def demo_frames(run):
    color = METHOD_COLOR.get(run.method, BLUE)
    frames = []
    # scene 1: advertisements at t = 0
    initial = [e for e in run.adverts if e["t"] == 0.0 and e["type"] == "adv"]
    n = 50
    for k in range(n):
        f = (k + 1) / n
        lines = [(run.pos[e["from"]], lerp(run.pos[e["from"]], run.pos[e["to"]], f), 0.55, BLUE)
                 for e in initial]
        frames.append({"t": 0.0, "lines": lines, "scene": 1,
                       "title": "1. Agents advertise their capabilities",
                       "subtitle": f"Each router learns, per neighbour, which capabilities lie behind it "
                                   f"(radius R = {run.topo['meta']['radius']}, k-means summary)"})
    frames += [dict(frames[-1]) for _ in range(10)]
    # scene 2: one request, hop by hop
    pid = pick_packet(run)
    if pid is not None:
        q = run.queries[pid]
        scene = packet_frames(run, pid, 12, color, q["t"],
                              "2. A request is routed by meaning, hop by hop",
                              f"Intent: \"{q['text']}\"  (class: {run.classes[q['cls']]})")
        for f in scene:
            f["scene"] = 2
        frames += scene
    # scene 3: a phone changes cell
    ho = next((h for h in run.handovers if 6.0 < h["t"] < run.topo["meta"]["duration"] - 3
               and h["agent"] in run.moves), None)
    if ho is not None:
        a = ho["agent"]
        t0, t1 = ho["t"] - 3.0, ho["t"] + 1.0
        after = [e for e in run.adverts if ho["t"] <= e["t"] <= ho["t"] + 0.1]
        n = 80
        for k in range(n):
            t = t0 + (t1 - t0) * k / (n - 1)
            xy = run.agent_xy(a, t)
            spec = {"t": t, "dots": [(*xy, BLUE)], "scene": 3,
                    "title": "3. A phone changes cell",
                    "subtitle": f"Agent {a} ({run.agents[a]['class_name']}) moves; only nearby "
                                f"S-FIB entries are updated, nothing is re-flooded"}
            if t >= ho["t"]:
                spec["rings"] = [(*run.pos[ho["from_cell"]], CRITICAL, 900),
                                 (*run.pos[ho["to_cell"]], GOOD, 900)]
                spec["lines"] = [(run.pos[e["from"]], run.pos[e["to"]], 0.8,
                                  CRITICAL if e["type"] == "withdraw" else GOOD) for e in after]
                spec["caption"] = (f"Handover: cell {ho['from_cell']} -> {ho['to_cell']}\n"
                                   f"{len(after)} S-FIB update messages\n(withdraw + announce)")
            frames.append(spec)
        frames += [dict(frames[-1]) for _ in range(20)]
    return frames


def pick_comparison(a_run, b_run):
    """A request that both runs saw, where the paths differ and B (DQN) does better."""
    best, best_key = None, None
    for pid, qa in a_run.queries.items():
        if pid not in b_run.queries or qa["t"] < 3.0:
            continue
        oa, ob = a_run.outcome.get(pid), b_run.outcome.get(pid)
        if not oa or not ob or a_run.path(pid) == b_run.path(pid):
            continue
        if len(a_run.hops.get(pid, [])) < 1 or len(b_run.hops.get(pid, [])) < 1:
            continue
        a_ok, b_ok = oa["type"] == "deliver", ob["type"] == "deliver"
        if b_ok and not a_ok:
            key = (2, -len(b_run.hops[pid]))
        elif a_ok and b_ok and ob["t"] < oa["t"]:
            key = (1, (oa["t"] - qa["t"]) - (ob["t"] - qa["t"]))
        else:
            continue
        if best_key is None or key > best_key:
            best, best_key = pid, key
    return best


def comparison_frames(runs, pid):
    per = []
    for run in runs:
        q = run.queries[pid]
        color = METHOD_COLOR.get(run.method, BLUE)
        fr = packet_frames(run, pid, 24, color, q["t"], "", "", hold=1)
        busy_nodes = [n for n in run.pos if run.busy(n, q["t"])]
        for f in fr:
            f["busy"] = busy_nodes
        per.append(fr)
    n = max(len(f) for f in per)
    frames = []
    q = runs[0].queries[pid]
    for k in range(n + 60):
        panels = [fr[min(k, len(fr) - 1)] for fr in per]
        frames.append({"panels": panels,
                       "title": "Same request, same network: greedy vs learned next hop",
                       "subtitle": f"Intent: \"{q['text']}\"   (orange = busy router at that moment)"})
    return frames


def render(fig, animator, frames, name, gif_dpi=60):
    anim = animation.FuncAnimation(fig, lambda i: animator.update(frames[i]), frames=len(frames),
                                   interval=1000 / FPS, blit=False)
    OUT.mkdir(parents=True, exist_ok=True)
    try:
        import imageio_ffmpeg
        plt.rcParams["animation.ffmpeg_path"] = imageio_ffmpeg.get_ffmpeg_exe()
        anim.save(OUT / f"{name}.mp4", writer=animation.FFMpegWriter(fps=FPS, bitrate=2400), dpi=100)
        print("wrote", OUT / f"{name}.mp4")
    except Exception as exc:  # ffmpeg missing: GIF only
        print("mp4 skipped:", exc)
    anim.save(OUT / f"{name}.gif", writer=animation.PillowWriter(fps=FPS), dpi=gif_dpi)
    print("wrote", OUT / f"{name}.gif", f"({len(frames) / FPS:.1f} s)")
    # poster frame for the slides: the most informative frame (end of the request scene)
    if "panels" in frames[0]:
        poster = len(frames) - 1
    else:
        delivered = [i for i, f in enumerate(frames) if f.get("labels")]
        poster = delivered[0] if delivered else len(frames) // 2
    animator.update(frames[poster])
    fig.savefig(OUT / f"{name}_poster.png", dpi=100)


def make_demo(method):
    run = Run(method)
    fig = plt.figure(figsize=(12.8, 7.2))
    fig.patch.set_facecolor(SURFACE)
    ax = fig.add_axes([0.0, 0.03, 0.60, 0.82])
    info = fig.add_axes([0.62, 0.06, 0.36, 0.78])
    draw_static(ax, run)
    steps = ["1  Advertise capabilities", "2  Route the request by meaning", "3  Handover: local update"]
    animator = Animator(fig, [ax], [run], info_ax=info, steps=steps)
    render(fig, animator, demo_frames(run), "agentroute_demo")
    plt.close(fig)


def make_comparison(baseline, learned):
    a, b = Run(baseline), Run(learned)
    pid = pick_comparison(a, b)
    if pid is None:
        print("no request where the learned policy beats greedy in the demo log; comparison skipped")
        return None
    fig, axes = plt.subplots(1, 2, figsize=(12.8, 7.2))
    fig.patch.set_facecolor(SURFACE)
    fig.subplots_adjust(left=0.01, right=0.99, top=0.84, bottom=0.08, wspace=0.03)
    for ax, run in zip(axes, (a, b)):
        draw_static(ax, run, METHOD_LABEL.get(run.method, run.method))
    animator = Animator(fig, list(axes), [a, b])
    render(fig, animator, comparison_frames([a, b], pid), "greedy_vs_agentroute")
    plt.close(fig)
    # what the video shows, for the slide notes
    info = {"pid": pid, "text": a.queries[pid]["text"]}
    for run in (a, b):
        out, q = run.outcome[pid], run.queries[pid]
        info[run.method] = {"type": out["type"], "reason": out.get("reason"),
                            "hops": len(run.hops.get(pid, [])),
                            "time_ms": round((out["t"] - q["t"]) * 1000, 1),
                            "agent_class": run.agents[out["agent"]]["class_name"] if out["type"] == "deliver" else None}
    (OUT / "greedy_vs_agentroute.json").write_text(json.dumps(info, indent=2))
    return pid


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--only", choices=["demo", "compare"], default=None)
    p.add_argument("--method", default="agentroute")
    args = p.parse_args()
    if args.only in (None, "demo"):
        make_demo(args.method)
    if args.only in (None, "compare"):
        pid = make_comparison("greedy", args.method)
        if pid is not None:
            print("comparison uses request", pid)


if __name__ == "__main__":
    main()
