"""AgentRoute web console: one local page to run the whole project.

    .venv/bin/python viz/console/server.py            # then open http://localhost:8476

The page can
  - run the simulator for any set of methods and replay every packet on the map,
  - embed a free-text task request and show which capabilities it matches,
  - start every pipeline step (tau, training, experiments, figures, demo, tests)
    and stream its log,
  - browse the figures and videos in results/figures.

Only the Python standard library is used for the server. Simulations run in a
thread of this process; pipeline steps run as subprocesses of the project's
own scripts, so the console never duplicates their logic.

Written with AI assistance (visualisation tooling).
"""
import argparse
import json
import mimetypes
import os
import re
import subprocess
import sys
import threading
import time
import traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from agentroute.config import load_config  # noqa: E402
from agentroute.sim.simulator import METHODS, Simulator, dataset, load_tau  # noqa: E402

STATIC = Path(__file__).resolve().parent / "static"
FIGURES = ROOT / "results" / "figures"
LOGS = ROOT / "results" / "logs"
WEB_RUNS = LOGS / "web"
PY = sys.executable

# Pipeline steps in the order experiments/run_all.py runs them.
# "quick" is the extra argument list used when quick mode is on.
EXPERIMENTS = ["scale", "mobility", "failure", "radius", "load", "rate", "tau", "ablation",
               "matched", "handover_cost"]
STEPS = [
    {"id": "encoders", "group": "Prepare", "title": "Compare sentence encoders",
     "args": ["experiments/compare_encoders.py"], "quick": [],
     "note": "Downloads six encoders on the first run."},
    {"id": "tau", "group": "Prepare", "title": "Tune the acceptance threshold τ",
     "args": ["experiments/tune_tau.py"], "quick": [], "note": "Writes results/tau.json."},
    {"id": "train", "group": "Learn", "title": "Train the DQN and GNN policies",
     "args": ["experiments/run_train.py"], "quick": ["--episodes", "20"],
     "note": "Overwrites results/models/dqn.pt and gnn.pt."},
] + [
    {"id": f"run_{n}", "group": "Experiments", "title": f"Experiment: {n.replace('_', ' ')}",
     "args": [f"experiments/run_{n}.py"],
     "quick": ["--quick"], "note": "Writes results/raw."}
    for n in EXPERIMENTS
] + [
    {"id": "figures", "group": "Outputs", "title": "Draw the figures",
     "args": ["viz/plots.py"], "quick": [], "note": "Writes results/figures."},
    {"id": "demo", "group": "Outputs", "title": "Log the demo runs",
     "args": ["experiments/run_demo.py"], "quick": [], "note": "Writes results/logs/demo."},
    {"id": "animate", "group": "Outputs", "title": "Render the animations",
     "args": ["viz/animate.py"], "quick": [], "note": "GIF and MP4 in results/figures."},
    {"id": "export", "group": "Outputs", "title": "Export runs to the React player",
     "args": ["viz/export_web_data.py"], "quick": [], "note": ""},
    {"id": "tests", "group": "Check", "title": "Run the test suite",
     "args": ["-m", "pytest", "-q"], "quick": [], "note": ""},
    {"id": "all", "group": "Everything", "title": "Run the whole pipeline",
     "args": ["experiments/run_all.py"], "quick": ["--quick"],
     "note": "About an hour; quick mode takes a few minutes."},
]
STEP_BY_ID = {s["id"]: s for s in STEPS}

ANSI = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")

# --------------------------------------------------------------------- jobs
# A job is either a simulation (thread) or a pipeline step (subprocess).
# Only one job runs at a time, so two runs never write the same files.
JOBS = {}
LOCK = threading.Lock()
_next_id = [1]


def new_job(kind, title):
    with LOCK:
        running = [j for j in JOBS.values() if j["state"] == "running"]
        if running:
            return None, running[0]
        jid = str(_next_id[0])
        _next_id[0] += 1
        job = {"id": jid, "kind": kind, "title": title, "state": "running", "log": [],
               "progress": 0.0, "started": time.time(), "ended": None, "result": None,
               "proc": None}
        JOBS[jid] = job
        return job, None


def job_public(job, offset=0):
    return {k: v for k, v in job.items() if k not in ("log", "proc")} | {
        "log": job["log"][offset:], "offset": len(job["log"])}


def run_simulation(job, params):
    try:
        methods = params["methods"]
        stamp = time.strftime("%Y%m%d-%H%M%S")
        out = WEB_RUNS / stamp
        overrides = {
            "agents": {"n_agents": int(params["n_agents"]), "speed_mps": float(params["speed"])},
            "sfib": {"radius": int(params["radius"]), "summary": params["summary"]},
            "sim": {"duration_s": float(params["duration"]), "load": float(params["load"]),
                    "failure_fraction": float(params["failure"])},
        }
        log_events = bool(params.get("log_events", True))
        rows = []
        for i, m in enumerate(methods):
            job["log"].append(f"{m}: simulating ...")
            t0 = time.time()
            cfg = load_config(overrides=overrides)
            s = Simulator(cfg, m, seed=int(params["seed"]),
                          log_dir=(out / m) if log_events else None).run()
            rows.append(s)
            job["log"].append(f"{m}: success {s['success_rate'] * 100:.1f}% in {time.time() - t0:.1f}s")
            job["progress"] = (i + 1) / len(methods)
        out.mkdir(parents=True, exist_ok=True)
        info = {"id": stamp, "params": params, "summaries": rows,
                "replay": methods if log_events else []}
        (out / "runset.json").write_text(json.dumps(info, indent=1))
        job["result"] = info
        job["state"] = "done"
    except Exception as e:  # report the error on the page instead of killing the server
        job["log"] += traceback.format_exc().splitlines()
        job["result"] = {"error": str(e)}
        job["state"] = "failed"
    job["ended"] = time.time()


def run_step(job, step, quick):
    args = [PY] + step["args"] + (step["quick"] if quick else [])
    job["log"].append("$ " + " ".join(a.replace(str(ROOT) + "/", "") for a in args))
    try:
        proc = subprocess.Popen(args, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                text=True, bufsize=1, env={**os.environ, "PYTHONUNBUFFERED": "1",
                                                           "MPLBACKEND": "Agg"})
        job["proc"] = proc
        for line in proc.stdout:
            job["log"].append(ANSI.sub("", line.rstrip("\n")).split("\r")[-1])
            if len(job["log"]) > 20000:
                del job["log"][:5000]
        code = proc.wait()
        if job["state"] == "running":
            job["state"] = "done" if code == 0 else "failed"
        job["log"].append(f"[exit code {code}]")
    except Exception as e:
        job["log"].append(f"could not start: {e}")
        job["state"] = "failed"
    job["ended"] = time.time()


# --------------------------------------------------------------------- data
def list_runsets():
    sets = []
    demo = LOGS / "demo"
    if demo.exists():
        methods = [d.name for d in sorted(demo.iterdir()) if (d / "events.jsonl").exists()]
        if methods:
            summaries = [json.loads((demo / m / "summary.json").read_text()) for m in methods
                         if (demo / m / "summary.json").exists()]
            sets.append({"id": "demo", "label": "Demo scenario (configs/demo.yaml)",
                         "params": {"n_agents": 100, "seed": 7}, "summaries": summaries,
                         "replay": methods})
    if WEB_RUNS.exists():
        for d in sorted(WEB_RUNS.iterdir(), reverse=True):
            f = d / "runset.json"
            if f.exists():
                info = json.loads(f.read_text())
                p = info["params"]
                info["label"] = (f"{d.name[:4]}-{d.name[4:6]}-{d.name[6:8]} {d.name[9:11]}:"
                                 f"{d.name[11:13]}, {p['n_agents']} agents")
                sets.append(info)
    return sets


def runset_dir(set_id):
    if set_id == "demo":
        return LOGS / "demo"
    return WEB_RUNS / set_id


def meta():
    cfg = load_config()
    avail = {"agentroute": (ROOT / cfg["dqn"]["model_path"]).exists(),
             "agentroute_gnn": (ROOT / cfg["dqn"]["gnn_model_path"]).exists()}
    return {"methods": [{"id": m, "available": avail.get(m, True)} for m in METHODS],
            "steps": [{k: s[k] for k in ("id", "group", "title", "note")} for s in STEPS],
            "tau": load_tau(cfg)}


_encoder = {}


def classify(text):
    """Cosine similarity of a free-text request to every capability class."""
    import numpy as np
    from agentroute.data.capabilities import CLASSES
    from agentroute.embeddings import get_model, header_bytes
    data = dataset()
    if "m" not in _encoder:
        _encoder["m"] = get_model()
    v = _encoder["m"].encode([text], normalize_embeddings=True)[0].astype(np.float32)
    sims = data["desc_vecs"] @ v
    best = {}
    for s, c in zip(sims, data["desc_class"]):
        best[int(c)] = max(best.get(int(c), -1.0), float(s))
    ranked = sorted(best.items(), key=lambda kv: -kv[1])[:10]
    tau = load_tau(load_config())
    return {"tau": tau, "header_bytes": {h: header_bytes(h) for h in ("float32", "int8", "binary")},
            "matches": [{"cls": c, "name": CLASSES[c][0], "card": CLASSES[c][1][0],
                         "score": s, "accept": s >= tau} for c, s in ranked]}


def example_intents():
    data = dataset()
    from agentroute.data.capabilities import CLASSES
    return [{"text": t, "name": CLASSES[int(c)][0]}
            for t, c in zip(data["test_text"][::7], data["test_class"][::7])]


def figures():
    out = []
    if FIGURES.exists():
        for f in sorted(FIGURES.iterdir()):
            if f.suffix in (".png", ".mp4") and not f.stem.endswith("_poster"):
                out.append({"name": f.name, "stem": f.stem, "kind": f.suffix[1:],
                            "mtime": f.stat().st_mtime,
                            "poster": f"{f.stem}_poster.png"
                            if (FIGURES / f"{f.stem}_poster.png").exists() else None})
    return out


def clean(obj):
    """Replace NaN and infinity (no requests of that kind) with null, which JSON allows."""
    if isinstance(obj, float) and (obj != obj or obj in (float("inf"), float("-inf"))):
        return None
    if isinstance(obj, dict):
        return {k: clean(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [clean(v) for v in obj]
    return obj


def safe_path(base, rel):
    p = (base / rel).resolve()
    if base.resolve() not in p.parents and p != base.resolve():
        return None
    return p if p.is_file() else None


# --------------------------------------------------------------------- http
class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def send_json(self, obj, code=200):
        body = json.dumps(clean(obj)).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def send_file(self, path):
        if path is None:
            return self.send_json({"error": "not found"}, 404)
        data = path.read_bytes()
        ctype = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        if path.suffix == ".jsonl":
            ctype = "text/plain"
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-cache")  # edits to the page show up on reload
        self.end_headers()
        self.wfile.write(data)

    def body(self):
        n = int(self.headers.get("Content-Length") or 0)
        return json.loads(self.rfile.read(n) or b"{}")

    def do_GET(self):
        url = urlparse(self.path)
        path = unquote(url.path)
        try:
            if path == "/":
                return self.send_file(STATIC / "index.html")
            if path.startswith("/static/"):
                return self.send_file(safe_path(STATIC, path[len("/static/"):]))
            if path == "/api/meta":
                return self.send_json(meta())
            if path == "/api/runsets":
                return self.send_json(list_runsets())
            if path.startswith("/api/run/"):
                _, _, _, set_id, method, name = path.split("/", 5)
                if name not in ("topology.json", "events.jsonl", "summary.json"):
                    return self.send_json({"error": "not found"}, 404)
                return self.send_file(safe_path(runset_dir(set_id), f"{method}/{name}"))
            if path == "/api/examples":
                return self.send_json(example_intents())
            if path == "/api/figures":
                return self.send_json(figures())
            if path.startswith("/figures/"):
                return self.send_file(safe_path(FIGURES, path[len("/figures/"):]))
            if path == "/api/jobs":
                return self.send_json([job_public(j, len(j["log"])) for j in JOBS.values()])
            if path.startswith("/api/jobs/"):
                job = JOBS.get(path.split("/")[3])
                if job is None:
                    return self.send_json({"error": "no such job"}, 404)
                q = dict(p.split("=") for p in url.query.split("&") if "=" in p)
                return self.send_json(job_public(job, int(q.get("offset", 0))))
            return self.send_json({"error": "not found"}, 404)
        except Exception as e:
            return self.send_json({"error": str(e)}, 500)

    def do_POST(self):
        path = urlparse(self.path).path
        try:
            if path == "/api/simulate":
                params = self.body()
                if not params.get("methods"):
                    return self.send_json({"error": "Pick at least one method."}, 400)
                job, busy = new_job("simulate", f"Simulation, {params['n_agents']} agents")
                if job is None:
                    return self.send_json({"error": f"\"{busy['title']}\" is still running."}, 409)
                threading.Thread(target=run_simulation, args=(job, params), daemon=True).start()
                return self.send_json(job_public(job))
            if path == "/api/step":
                req = self.body()
                step = STEP_BY_ID.get(req.get("id"))
                if step is None:
                    return self.send_json({"error": "unknown step"}, 400)
                quick = bool(req.get("quick"))
                job, busy = new_job("step", step["title"] + (" (quick)" if quick and step["quick"] else ""))
                if job is None:
                    return self.send_json({"error": f"\"{busy['title']}\" is still running."}, 409)
                job["step"] = step["id"]
                threading.Thread(target=run_step, args=(job, step, quick), daemon=True).start()
                return self.send_json(job_public(job))
            if path.startswith("/api/jobs/") and path.endswith("/stop"):
                job = JOBS.get(path.split("/")[3])
                if job and job["state"] == "running" and job["proc"] is not None:
                    job["state"] = "stopped"
                    job["proc"].terminate()
                    return self.send_json(job_public(job, len(job["log"])))
                return self.send_json({"error": "This job cannot be stopped."}, 400)
            if path == "/api/classify":
                text = (self.body().get("text") or "").strip()
                if not text:
                    return self.send_json({"error": "Type a task request first."}, 400)
                return self.send_json(classify(text[:500]))
            return self.send_json({"error": "not found"}, 404)
        except Exception as e:
            traceback.print_exc()
            return self.send_json({"error": str(e)}, 500)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--port", type=int, default=8476)
    p.add_argument("--host", default="127.0.0.1")
    args = p.parse_args()
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"AgentRoute console on http://localhost:{args.port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
