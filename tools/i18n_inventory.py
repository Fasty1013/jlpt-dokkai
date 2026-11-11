"""
i18n inventory (feat/i18n-switcher, sub-iteration 1).

Scans the repository for Cyrillic user-facing strings and writes:
  docs/i18n/inventory.json  - every string with file, line, kind, category
  docs/i18n/INVENTORY.md    - human-readable summary

Read-only with respect to the code base. Usage:  python tools/i18n_inventory.py
Comment lines (//, /*, *, #, <!-- -->) are excluded; docstrings are excluded heuristically.
"""
import json
import os
import re
import sys
from collections import Counter, defaultdict
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CYR = re.compile(r"[Ѐ-ӿ]")
OUT_DIR = os.path.join(ROOT, "docs", "i18n")

SCAN_DIRS = ["static", "app"]
SCAN_FILES = ["main.py"]
EXTS = (".js", ".html", ".py", ".json", ".css")
SKIP_PARTS = ("__pycache__", "node_modules", os.sep + "locales" + os.sep, os.sep + "i18n" + os.sep)


def category(path: str) -> str:
    p = path.replace("\\", "/")
    if p == "static/index.html":
        return "html"
    if p.startswith("static/js/content/") or p.endswith("constants/labels.js"):
        return "js-dictionary-like"
    if p.startswith("static/js/"):
        return "js-ui"
    if p.startswith("static/"):
        return "static-other"
    if p == "app/services/dictionary_service.py":
        return "server-dictionary-data"
    if p.startswith("app/"):
        return "server-text"
    return "other"


VOID = {"br", "img", "input", "meta", "link", "hr", "source", "col", "area", "base", "wbr"}


class HtmlScan(HTMLParser):
    """Collects Cyrillic text/attributes in index.html that are NOT covered by data-i18n / data-i18n-attr.
    Covered strings are translated through the dictionaries; what remains are JS-owned placeholders
    (overwritten by JS at run time, which uses t()) and the language names in the switcher."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.items = []
        self._skip = 0
        self._stack = []  # True when the element carries data-i18n

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if tag in ("script", "style"):
            self._skip += 1
        covered_attrs = set()
        if d.get("data-i18n-attr"):
            covered_attrs = {p.split(":")[0].strip() for p in d["data-i18n-attr"].split(";")}
        for name, val in attrs:
            if val and CYR.search(val) and name in ("title", "placeholder", "aria-label", "alt", "content"):
                if name not in covered_attrs:
                    self.items.append((self.getpos()[0], "attr:" + name, val.strip()))
        if tag not in VOID:
            self._stack.append("data-i18n" in d or "data-i18n-html" in d)

    def handle_endtag(self, tag):
        if tag in ("script", "style") and self._skip:
            self._skip -= 1
        if tag not in VOID and self._stack:
            self._stack.pop()

    def handle_data(self, data):
        if self._skip or any(self._stack):
            return
        if CYR.search(data):
            self.items.append((self.getpos()[0], "text", " ".join(data.split())))


def scan_html(text):
    p = HtmlScan()
    p.feed(text)
    return p.items


def scan_lines(text, is_py):
    items = []
    in_doc = False
    in_block = False
    for n, line in enumerate(text.split("\n"), 1):
        s = line.strip()
        if is_py:
            if s.count('"""') == 1 or s.count("'''") == 1:
                in_doc = not in_doc
                continue
            if in_doc or s.startswith("#"):
                continue
        else:
            if in_block:
                if "*/" in s:
                    in_block = False
                continue
            if s.startswith("/*"):
                if "*/" not in s:
                    in_block = True
                continue
            if s.startswith("//") or s.startswith("*"):
                continue
        if not CYR.search(line):
            continue
        # strip trailing line comment (rough)
        code = re.sub(r"\s//.*$", "", line) if not is_py else re.sub(r"\s#.*$", "", line)
        if not CYR.search(code):
            continue
        items.append((n, "string", s))
    return items


def main():
    paths = []
    for d in SCAN_DIRS:
        for dp, _, fs in os.walk(os.path.join(ROOT, d)):
            for f in fs:
                if f.endswith(EXTS):
                    paths.append(os.path.join(dp, f))
    for f in SCAN_FILES:
        paths.append(os.path.join(ROOT, f))

    rows = []
    for p in sorted(paths):
        if any(part in p for part in SKIP_PARTS):
            continue
        rel = os.path.relpath(p, ROOT).replace("\\", "/")
        try:
            text = open(p, encoding="utf-8").read()
        except (OSError, UnicodeDecodeError):
            continue
        if p.endswith(".html"):
            found = scan_html(text)
        elif p.endswith((".js", ".py", ".css")):
            found = scan_lines(text, p.endswith(".py"))
        else:
            found = [(n, "string", l.strip()) for n, l in enumerate(text.split("\n"), 1) if CYR.search(l)]
        for line, kind, s in found:
            rows.append({"file": rel, "line": line, "kind": kind, "category": category(rel), "text": s})

    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, "inventory.json"), "w", encoding="utf-8") as fh:
        json.dump(rows, fh, ensure_ascii=False, indent=1)

    by_cat = Counter(r["category"] for r in rows)
    by_file = defaultdict(int)
    for r in rows:
        by_file[r["file"]] += 1

    lines = [
        "# i18n inventory (generated by `tools/i18n_inventory.py`)",
        "",
        "Cyrillic user-facing strings found in `static/` and `app/`. Comments and docstrings are excluded.",
        "In `index.html` only strings NOT covered by `data-i18n` are listed (JS-owned placeholders, language names).",
        "Re-run the script to refresh. Full list with line numbers: `inventory.json`.",
        "",
        f"**Total entries: {len(rows)}** in {len(by_file)} files.",
        "",
        "## By category",
        "",
        "| Category | Entries |",
        "| :-- | --: |",
    ]
    for c, n in by_cat.most_common():
        lines.append(f"| {c} | {n} |")
    lines += ["", "## By file", "", "| File | Category | Entries |", "| :-- | :-- | --: |"]
    for f, n in sorted(by_file.items(), key=lambda kv: (-kv[1], kv[0])):
        lines.append(f"| `{f}` | {category(f)} | {n} |")
    with open(os.path.join(OUT_DIR, "INVENTORY.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    print(f"{len(rows)} entries in {len(by_file)} files")
    for c, n in by_cat.most_common():
        print(f"  {c}: {n}")


if __name__ == "__main__":
    sys.exit(main())
