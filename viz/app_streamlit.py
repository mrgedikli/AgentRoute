"""Interactive AgentRoute simulator (Streamlit).

    streamlit run viz/app_streamlit.py

Pick the scenario in the sidebar, run the simulation for several methods,
then compare the results, replay single requests on the network, browse the
experiment figures, or export the run to the React log player.

Written with AI assistance (visualisation).
"""
import json
import sys
from pathlib import Path

import altair as alt
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402
import streamlit as st  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "viz"))

from agentroute.config import load_config  # noqa: E402
from agentroute.sim.simulator import Simulator  # noqa: E402
from animate import BLUE, CRITICAL, GOOD, SERIOUS, Run, draw_static  # noqa: E402
from export_web_data import export_run, write_index  # noqa: E402

LOG_ROOT = ROOT / "results" / "logs" / "streamlit"
FIGURES = ROOT / "results" / "figures"
LABELS = {"agentroute": "AgentRoute (DQN)", "agentroute_gnn": "AgentRoute (GNN)",
          "greedy": "Greedy semantic", "flooding": "Flooding", "registry": "Central registry",
          "chord": "Chord (exact)"}
COLORS = {"agentroute": "#2a78d6", "agentroute_gnn": "#eb6834", "greedy": "#1baf7a",
          "flooding": "#eda100", "registry": "#e87ba4", "chord": "#008300"}
REASONS = ["wrong_agent", "not_found", "ttl", "queue", "link", "node_down", "handover",
           "stale_location", "registry_queue", "no_route"]

st.set_page_config(page_title="AgentRoute simulator", layout="wide")


def models_available():
    cfg = load_config()
    return {"agentroute": (ROOT / cfg["dqn"]["model_path"]).exists(),
            "agentroute_gnn": (ROOT / cfg["dqn"]["gnn_model_path"]).exists()}


# ---------------------------------------------------------------- sidebar
st.sidebar.header("Scenario")
n_agents = st.sidebar.slider("Number of agents", 100, 3000, 300, step=100)
avail = models_available()
options = [m for m in LABELS if avail.get(m, True)]
methods = st.sidebar.multiselect("Methods", options, default=[m for m in
                                 ["agentroute", "greedy", "flooding", "registry"] if m in options],
                                 format_func=LABELS.get)
if not all(avail.values()):
    st.sidebar.caption("Train the DQN first (experiments/run_train.py) to enable AgentRoute.")
radius = st.sidebar.slider("Advertisement radius R (hops)", 1, 6, 3)
summary = st.sidebar.selectbox("S-FIB summary", ["kmeans", "mean", "exact"])
speed = st.sidebar.slider("Mobile agent speed (m/s)", 0.0, 30.0, 5.0, step=1.0)
load = st.sidebar.slider("Network load factor", 0.5, 4.0, 1.0, step=0.5)
failure = st.sidebar.slider("Failed routers (fraction)", 0.0, 0.3, 0.0, step=0.05)
duration = st.sidebar.slider("Simulated time (s)", 10, 60, 20, step=5)
seed = st.sidebar.number_input("Seed", 1, 9999, 1)
log_events = st.sidebar.checkbox("Log every event (needed for the replay)", value=n_agents <= 1000)
run_clicked = st.sidebar.button("Run simulation", type="primary", use_container_width=True)

st.title("AgentRoute: routing packets to capabilities")
st.caption("Packets are addressed to what an agent can do; routers learn the next hop. "
           "Each run uses the same topology, mobility and requests for every method.")

if run_clicked and methods:
    overrides = {"agents": {"n_agents": n_agents, "speed_mps": speed},
                 "sfib": {"radius": radius, "summary": summary},
                 "sim": {"duration_s": float(duration), "load": load, "failure_fraction": failure}}
    rows = []
    progress = st.progress(0.0, text="Simulating ...")
    for i, m in enumerate(methods):
        cfg = load_config(overrides=overrides)
        log_dir = LOG_ROOT / m if log_events else None
        rows.append(Simulator(cfg, m, seed=int(seed), log_dir=log_dir).run())
        progress.progress((i + 1) / len(methods), text=f"{LABELS[m]} done")
    progress.empty()
    st.session_state["results"] = pd.DataFrame(rows)
    st.session_state["logged"] = methods if log_events else []

res = st.session_state.get("results")
tab_res, tab_net, tab_fig, tab_web = st.tabs(["Results", "Network replay", "Experiment figures",
                                              "Web player"])

# ---------------------------------------------------------------- results
with tab_res:
    if res is None:
        st.info("Choose a scenario in the sidebar and press **Run simulation**.")
    else:
        df = res.copy()
        df["Method"] = df["method"].map(LABELS)
        cols = st.columns(len(df))
        for col, (_, r) in zip(cols, df.iterrows()):
            col.metric(r["Method"], f"{r['success_rate'] * 100:.1f}%",
                       help="Discovery success rate (request delivered to a capable agent)")
        table = df[["Method", "n_queries", "success_rate", "time_ms", "hops", "msgs_per_query",
                    "handovers"]].rename(columns={
                        "n_queries": "Requests", "success_rate": "Success", "time_ms": "Time (ms)",
                        "hops": "Hops", "msgs_per_query": "Messages / request",
                        "handovers": "Handovers"})
        st.dataframe(table.style.format({"Success": "{:.1%}", "Time (ms)": "{:.1f}", "Hops": "{:.2f}",
                                         "Messages / request": "{:.0f}"}),
                     hide_index=True, use_container_width=True)
        scale = alt.Scale(domain=[LABELS[m] for m in COLORS], range=list(COLORS.values()))
        c1, c2 = st.columns(2)
        base = alt.Chart(df).encode(
            y=alt.Y("Method:N", sort=list(df["Method"]), title=None),
            color=alt.Color("Method:N", scale=scale, legend=None))
        c1.altair_chart(base.mark_bar(cornerRadiusEnd=4, size=18).encode(
            x=alt.X("success_rate:Q", title="Success rate", axis=alt.Axis(format="%")),
            tooltip=["Method", alt.Tooltip("success_rate:Q", format=".1%")]).properties(
            title="Discovery success"), use_container_width=True)
        c2.altair_chart(base.mark_bar(cornerRadiusEnd=4, size=18).encode(
            x=alt.X("time_ms:Q", title="Completion time (ms)"),
            tooltip=["Method", alt.Tooltip("time_ms:Q", format=".1f")]).properties(
            title="Task completion time"), use_container_width=True)
        long = df.melt(id_vars=["Method"], value_vars=[f"drop_{r}" for r in REASONS if f"drop_{r}" in df],
                       var_name="reason", value_name="share")
        long = long[long["share"] > 0]
        long["reason"] = long["reason"].str.replace("drop_", "").str.replace("_", " ")
        st.altair_chart(alt.Chart(long).mark_bar(size=18).encode(
            y=alt.Y("Method:N", title=None), x=alt.X("share:Q", title="Share of requests",
                                                      axis=alt.Axis(format="%")),
            color=alt.Color("reason:N", title="Failure reason"),
            tooltip=["Method", "reason", alt.Tooltip("share:Q", format=".1%")]).properties(
            title="Why requests fail"), use_container_width=True)

# ---------------------------------------------------------------- replay
with tab_net:
    logged = st.session_state.get("logged", [])
    if not logged:
        st.info("Run a simulation with event logging to replay single requests here.")
    else:
        m = st.selectbox("Method", logged, format_func=LABELS.get, key="replay_method")
        run = Run(m, LOG_ROOT / m)
        pids = [p for p in run.queries if p in run.outcome]
        only_ok = st.checkbox("Only delivered requests", value=True)
        if only_ok:
            pids = [p for p in pids if run.outcome[p]["type"] == "deliver"]
        if pids:
            pid = st.select_slider("Request id", options=pids, value=pids[min(10, len(pids) - 1)])
            q, out = run.queries[pid], run.outcome[pid]
            st.write(f"**Intent:** \"{q['text']}\" (class `{run.classes[q['cls']]}`) - "
                     f"**{out['type']}**" + (f" to agent {out['agent']} "
                                            f"({run.agents[out['agent']]['class_name']})"
                                            if out["type"] == "deliver" else f" ({out['reason']})") +
                     f", {(out['t'] - q['t']) * 1000:.1f} ms, {len(run.hops.get(pid, []))} hops")
            fig, ax = plt.subplots(figsize=(8, 6))
            draw_static(ax, run)
            for a in run.agents:
                x, y = run.agent_xy(a, q["t"])
                ax.scatter(x, y, s=8, color="#898781", alpha=0.6, lw=0, zorder=3)
            for node in run.pos:
                if run.busy(node, q["t"]):
                    ax.scatter(*run.pos[node], s=600, color=SERIOUS, alpha=0.35, lw=0, zorder=2)
            path = run.path(pid)
            for a, b in zip(path, path[1:]):
                (x1, y1), (x2, y2) = run.pos[a], run.pos[b]
                ax.annotate("", xy=(x2, y2), xytext=(x1, y1), zorder=6,
                            arrowprops=dict(arrowstyle="-|>", color=COLORS.get(m, BLUE), lw=2.5))
            ax.scatter(*run.agent_xy(q["agent"], q["t"]), s=160, facecolor="none",
                       edgecolor=COLORS.get(m, BLUE), lw=2.5, zorder=7)
            if out["type"] == "deliver":
                ax.scatter(*run.agent_xy(out["agent"], out["t"]), s=260, facecolor="none",
                           edgecolor=GOOD, lw=2.5, zorder=7)
            elif out.get("at") is not None:
                ax.scatter(*run.pos[out["at"]], s=300, facecolor="none", edgecolor=CRITICAL, lw=2.5,
                           zorder=7)
            st.pyplot(fig, use_container_width=True)
            st.caption("Ring = requester; green ring = serving agent; red ring = where it was dropped; "
                       "orange halo = router busy with background traffic at that moment.")
        else:
            st.warning("No matching requests in this run.")

# ---------------------------------------------------------------- figures
with tab_fig:
    figs = sorted(FIGURES.glob("*.png"))
    if not figs:
        st.info("Run the experiments and viz/plots.py to create the figures.")
    for i in range(0, len(figs), 2):
        cols = st.columns(2)
        for col, f in zip(cols, figs[i:i + 2]):
            col.image(str(f), caption=f.stem.replace("_", " "), use_container_width=True)

# ---------------------------------------------------------------- web player
with tab_web:
    st.write("The React + D3 player (viz/web) replays any logged run in the browser, "
             "with timeline controls and per-request delay waterfalls.")
    logged = st.session_state.get("logged", [])
    if logged and st.button("Export this run to the web player"):
        for m in logged:
            export_run(LOG_ROOT / m, f"streamlit_{m}")
        runs = write_index()
        st.success(f"Exported. The player now lists {len(runs)} runs.")
    st.code("cd viz/web\nnpm install\nnpm run dev", language="bash")
    index = ROOT / "viz" / "web" / "public" / "data" / "index.json"
    if index.exists():
        st.json(json.loads(index.read_text()), expanded=False)
