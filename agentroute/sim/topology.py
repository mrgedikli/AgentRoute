"""Mobile cellular / edge topology.

Layout
  - gNB + edge routers on a square grid of cells, neighbouring gNBs joined by
    Xn links,
  - core routers on a coarser grid, joined to each other in a grid mesh,
  - every gNB has a backhaul link to its nearest core router; half of them
    also to the second nearest (redundancy for the failure experiments),
  - one cloud node attached to two core routers.

The number of cells grows with the number of agents (20 agents per cell, at
most 400 cells), so the 10,000-agent scenario has 400 cells, 49 core routers
and one cloud node (450 routers).

Responsible: Ömer Faruk Gedikli
"""
import math

import networkx as nx
import numpy as np


def grid_side(n_agents, topo):
    cells = math.ceil(n_agents / topo["agents_per_cell"])
    cells = min(max(cells, topo["min_cells"]), topo["max_cells"])
    return math.ceil(math.sqrt(cells))


def _add_link(g, u, v, kind, topo):
    loss = topo["loss"]["radio"] if kind == "radio" else topo["loss"]["wired"]
    g.add_edge(u, v, kind=kind, delay=topo["delay_ms"][kind] / 1000.0, loss=loss)


def build_topology(cfg, rng):
    topo = cfg["topology"]
    side = grid_side(cfg["agents"]["n_agents"], topo)
    spacing = topo["cell_spacing_m"]
    g = nx.Graph()
    g.graph["side"] = side
    g.graph["spacing"] = spacing

    # gNB + edge routers
    for i in range(side):
        for j in range(side):
            g.add_node(i * side + j, kind="gnb", x=float(j * spacing), y=float(i * spacing))
    n_cells = side * side
    for i in range(side):
        for j in range(side):
            u = i * side + j
            if j + 1 < side:
                _add_link(g, u, u + 1, "xn", topo)
            if i + 1 < side:
                _add_link(g, u, u + side, "xn", topo)

    # core routers on a coarse grid over the same area
    core_side = max(2, round(math.sqrt(n_cells / topo["cells_per_core"])))
    extent = (side - 1) * spacing
    cores = []
    for i in range(core_side):
        for j in range(core_side):
            cid = n_cells + len(cores)
            x = (j + 0.5) * extent / core_side if side > 1 else 0.0
            y = (i + 0.5) * extent / core_side if side > 1 else 0.0
            g.add_node(cid, kind="core", x=float(x), y=float(y))
            cores.append(cid)
    for i in range(core_side):
        for j in range(core_side):
            c = cores[i * core_side + j]
            if j + 1 < core_side:
                _add_link(g, c, cores[i * core_side + j + 1], "core", topo)
            if i + 1 < core_side:
                _add_link(g, c, cores[(i + 1) * core_side + j], "core", topo)

    # backhaul: nearest core, plus the second nearest for a checkerboard half of the cells
    core_xy = np.array([[g.nodes[c]["x"], g.nodes[c]["y"]] for c in cores])
    for u in range(n_cells):
        xy = np.array([g.nodes[u]["x"], g.nodes[u]["y"]])
        order = np.argsort(np.linalg.norm(core_xy - xy, axis=1), kind="stable")
        _add_link(g, u, cores[order[0]], "backhaul", topo)
        i, j = divmod(u, side)
        if (i + j) % 2 == 0:
            _add_link(g, u, cores[order[1]], "backhaul", topo)

    # cloud data centre, attached to two opposite core routers
    cloud = n_cells + len(cores)
    g.add_node(cloud, kind="cloud", x=extent / 2, y=-1.2 * spacing)
    _add_link(g, cloud, cores[0], "cloud", topo)
    _add_link(g, cloud, cores[-1], "cloud", topo)

    # a few bad wired links with higher loss
    wired = [(u, v) for u, v, d in g.edges(data=True) if d["kind"] in ("xn", "backhaul", "core")]
    n_bad = int(round(topo["bad_link_fraction"] * len(wired)))
    for idx in rng.choice(len(wired), size=n_bad, replace=False):
        u, v = wired[idx]
        g.edges[u, v]["loss"] = topo["loss"]["bad"]
    return g


def area_bounds(g):
    """Rectangle covered by the cells: (xmin, ymin, xmax, ymax)."""
    side, spacing = g.graph["side"], g.graph["spacing"]
    half = spacing / 2
    return -half, -half, (side - 1) * spacing + half, (side - 1) * spacing + half
