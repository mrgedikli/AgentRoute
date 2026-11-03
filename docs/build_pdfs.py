"""Build the PDF versions of the documents with headless Chrome.

    python docs/build_pdfs.py

Markdown -> HTML (python-markdown + a print stylesheet) -> PDF (Chrome
--print-to-pdf). Also builds a code appendix with every source file of the
project, as promised in the proposal ("all code ... included in the final
report").

Written with AI assistance (document tooling).
"""
import html
import re
import shutil
import subprocess
import sys
from pathlib import Path

import markdown
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_for_filename

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "pdf"
BUILD = OUT / "_build"
CHROME_CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    shutil.which("google-chrome") or "",
    shutil.which("chromium") or "",
]

DOCS = [
    ("docs/report/FINAL_REPORT.md", "AgentRoute_Final_Report.pdf", "en"),
    ("docs/KULLANIM_KILAVUZU.md", "Kullanim_Kilavuzu.pdf", "tr"),
    ("docs/KIM_NE_YAPTI.md", "Kim_Ne_Yapti.pdf", "tr"),
    ("docs/NASIL_YAPTIK.md", "Nasil_Yaptik.pdf", "tr"),
]

CSS = """
@page { size: A4; margin: 18mm 17mm 18mm 17mm; }
body { font-family: -apple-system, "Helvetica Neue", Arial, sans-serif; font-size: 10.3pt;
       line-height: 1.45; color: #0b0b0b; }
h1 { font-size: 20pt; margin: 0 0 6pt; }
h2 { font-size: 14pt; margin: 18pt 0 6pt; border-bottom: 1px solid #e1e0d9; padding-bottom: 3pt; }
h3 { font-size: 11.5pt; margin: 12pt 0 4pt; }
p, li { orphans: 3; widows: 3; }
table { border-collapse: collapse; width: 100%; margin: 8pt 0; font-size: 9.2pt; page-break-inside: avoid; }
th, td { border: 1px solid #e1e0d9; padding: 3pt 5pt; text-align: left; vertical-align: top; }
th { background: #f3f2ee; }
code { font-family: Menlo, Consolas, monospace; font-size: 8.8pt; background: #f3f2ee; padding: 0 2pt;
       border-radius: 2pt; }
pre { background: #f6f5f1; padding: 6pt 8pt; border-radius: 4pt; overflow-x: hidden;
      white-space: pre-wrap; font-size: 8.4pt; page-break-inside: avoid; }
pre code { background: none; padding: 0; }
img { max-width: 100%; display: block; margin: 6pt auto; page-break-inside: avoid; }
figure { margin: 8pt 0; page-break-inside: avoid; }
blockquote { color: #52514e; border-left: 3px solid #e1e0d9; margin: 6pt 0; padding: 0 8pt; }
.title-block { text-align: center; margin-bottom: 14pt; }
.caption, em.caption { color: #52514e; font-size: 9pt; }
hr { border: 0; border-top: 1px solid #e1e0d9; margin: 12pt 0; }
"""


LIST_ITEM = re.compile(r"^( *)([-*]|\d+\.) ")


def normalise_lists(text):
    """Python-Markdown needs a blank line before a list and 4-space nesting;
    our documents use the GitHub style (no blank line, 2-space nesting)."""
    out = []
    in_code = False
    for line in text.split("\n"):
        if line.startswith("```"):
            in_code = not in_code
        m = None if in_code else LIST_ITEM.match(line)
        if m:
            indent = len(m.group(1))
            line = " " * (indent * 2) + line[indent:]
            prev = out[-1] if out else ""
            if prev.strip() and not LIST_ITEM.match(prev) and not prev.startswith("|"):
                out.append("")
        out.append(line)
    return "\n".join(out)


def find_chrome():
    for c in CHROME_CANDIDATES:
        if c and Path(c).exists():
            return c
    sys.exit("Chrome/Chromium not found: install Google Chrome to build the PDFs")


def to_pdf(chrome, html_path, pdf_path):
    subprocess.run([chrome, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                    "--run-all-compositor-stages-before-draw", "--virtual-time-budget=10000",
                    f"--print-to-pdf={pdf_path}", html_path.as_uri()],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def build_doc(chrome, src, out_name, lang):
    src = ROOT / src
    body = markdown.markdown(normalise_lists(src.read_text()), extensions=["tables", "fenced_code", "toc",
                                                         "attr_list", "md_in_html"])
    page = (f'<!doctype html><html lang="{lang}"><head><meta charset="utf-8">'
            f'<base href="{src.parent.as_uri()}/"><style>{CSS}</style></head>'
            f"<body>{body}</body></html>")
    html_path = BUILD / (out_name.replace(".pdf", ".html"))
    html_path.write_text(page)
    to_pdf(chrome, html_path, OUT / out_name)
    print("wrote", OUT / out_name)


def build_code_appendix(chrome):
    files = sorted((ROOT / "agentroute").rglob("*.py")) + sorted((ROOT / "experiments").glob("*.py")) \
        + sorted((ROOT / "viz").glob("*.py")) + sorted((ROOT / "tests").glob("*.py")) \
        + [ROOT / "docs" / "build_pdfs.py", ROOT / "configs" / "default.yaml", ROOT / "configs" / "demo.yaml"] \
        + sorted((ROOT / "viz" / "web" / "src").rglob("*.js*")) \
        + sorted((ROOT / "viz" / "web" / "src").rglob("*.css"))
    files = [f for f in files if f.name != "__init__.py"]
    fmt = HtmlFormatter(style="friendly", nowrap=False)
    parts = ["<h1>AgentRoute: Code Appendix</h1>",
             "<p>Complete source code of the project (simulator, protocols, DQN, experiments, "
             "visualisation). Each module header names the responsible team member; files written "
             "with AI assistance say so in their header.</p><ol>"]
    parts += [f"<li><code>{html.escape(str(f.relative_to(ROOT)))}</code></li>" for f in files]
    parts.append("</ol>")
    for f in files:
        rel = f.relative_to(ROOT)
        code = f.read_text()
        parts.append(f'<h2 style="page-break-before: always">{html.escape(str(rel))}</h2>')
        parts.append(highlight(code, get_lexer_for_filename(f.name), fmt))
    page = (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><style>{CSS}'
            f'{fmt.get_style_defs(".highlight")} .highlight pre {{ font-size: 7.6pt; '
            f'page-break-inside: auto; }}</style></head><body>{"".join(parts)}</body></html>')
    html_path = BUILD / "AgentRoute_Code_Appendix.html"
    html_path.write_text(page)
    to_pdf(chrome, html_path, OUT / "AgentRoute_Code_Appendix.pdf")
    print("wrote", OUT / "AgentRoute_Code_Appendix.pdf")


def main():
    chrome = find_chrome()
    BUILD.mkdir(parents=True, exist_ok=True)
    for src, out, lang in DOCS:
        if (ROOT / src).exists():
            build_doc(chrome, src, out, lang)
        else:
            print("skip (missing)", src)
    build_code_appendix(chrome)
    shutil.rmtree(BUILD)


if __name__ == "__main__":
    main()
