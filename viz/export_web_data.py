"""Copy simulation logs into the React player's public/data folder.

    python viz/export_web_data.py                 # every run under results/logs/demo
    python viz/export_web_data.py --src results/logs/streamlit --name my_run

Each run becomes public/data/<name>/{topology.json, events.jsonl, summary.json}
and is listed in public/data/index.json.

Written with AI assistance (visualisation tooling).
"""
import argparse
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WEB_DATA = ROOT / "viz" / "web" / "public" / "data"


def export_run(src, name):
    dst = WEB_DATA / name
    dst.mkdir(parents=True, exist_ok=True)
    for f in ("topology.json", "events.jsonl", "summary.json"):
        if (src / f).exists():
            shutil.copy(src / f, dst / f)
    summary = json.loads((src / "summary.json").read_text()) if (src / "summary.json").exists() else {}
    return {"name": name, "method": summary.get("method", name),
            "n_agents": summary.get("n_agents"), "success_rate": summary.get("success_rate")}


def write_index():
    runs = []
    for d in sorted(WEB_DATA.iterdir()) if WEB_DATA.exists() else []:
        if d.is_dir() and (d / "events.jsonl").exists():
            s = json.loads((d / "summary.json").read_text()) if (d / "summary.json").exists() else {}
            runs.append({"name": d.name, "method": s.get("method", d.name),
                         "n_agents": s.get("n_agents"), "success_rate": s.get("success_rate")})
    (WEB_DATA / "index.json").write_text(json.dumps({"runs": runs}, indent=2))
    return runs


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--src", default=str(ROOT / "results" / "logs" / "demo"))
    p.add_argument("--name", default=None, help="export a single run directory under this name")
    args = p.parse_args()
    src = Path(args.src)
    WEB_DATA.mkdir(parents=True, exist_ok=True)
    if args.name:
        export_run(src, args.name)
    else:
        for d in sorted(src.iterdir()):
            if d.is_dir() and (d / "events.jsonl").exists():
                export_run(d, f"demo_{d.name}")
    runs = write_index()
    print(f"{len(runs)} runs in {WEB_DATA / 'index.json'}")


if __name__ == "__main__":
    main()
