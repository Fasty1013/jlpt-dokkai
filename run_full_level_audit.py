#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Full Database Level Audit Tool.
Audits all texts across N5, N4, N3, N2, N1 against the Level Check Analyzer.
Outputs summary counts, problematic slugs, and monotonicity report.
"""

import sys
from pathlib import Path
from collections import defaultdict

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent
from database import SessionLocal
import models
from models import Text
from tools.level_check.analyzer import analyze, check_corpus_monotonicity

def run_audit():
    db = SessionLocal()
    texts = db.query(Text).order_by(Text.id).all()

    print(f"Total texts in database to audit: {len(texts)}")

    verdicts_by_level = defaultdict(lambda: {"ok": 0, "too_easy": 0, "too_hard": 0, "uncertain": 0})
    texts_by_level = defaultdict(list)
    flagged_texts = []

    for t in texts:
        texts_by_level[t.level].append(t.content_html)
        rep = analyze(t.content_html, t.level)
        v = rep["verdict"]
        verdicts_by_level[t.level][v] += 1

        if v != "ok":
            flagged_texts.append({
                "id": t.id,
                "slug": t.slug or f"db-text-{t.id}",
                "level": t.level,
                "title": t.title,
                "verdict": v,
                "reasons": rep["reasons"],
                "metrics": rep["metrics"]
            })

    print("\n=======================================================")
    print("          JLPT LEVEL AUDIT VERDICTS SUMMARY           ")
    print("=======================================================")
    print(f"| Level | Total |   OK   | Too Easy | Too Hard | Uncertain |")
    print(f"| :---: | :---: | :----: | :------: | :------: | :-------: |")
    for lvl in ["N5", "N4", "N3", "N2", "N1"]:
        v_dict = verdicts_by_level[lvl]
        total = sum(v_dict.values())
        print(f"|  {lvl}   |  {total:3d}  |  {v_dict['ok']:4d}  |   {v_dict['too_easy']:4d}   |   {v_dict['too_hard']:4d}   |    {v_dict['uncertain']:4d}   |")

    # Monotonicity test
    mono = check_corpus_monotonicity(texts_by_level)
    print("\n=======================================================")
    print("              CORPUS MONOTONICITY REPORT              ")
    print("=======================================================")
    print(f"All metrics strictly increasing (N5 < N4 < N3 < N2 < N1): {mono['all_monotonic']}")
    for metric, data in mono["details"].items():
        status = "✓ MONOTONIC" if data["is_monotonic"] else "✗ NON-MONOTONIC"
        val_str = " -> ".join(f"{lvl}: {val}" for lvl, val in data["values"].items())
        print(f"  • {metric:<16}: {status} ({val_str})")

    db.close()
    return verdicts_by_level, mono, flagged_texts

if __name__ == "__main__":
    run_audit()

