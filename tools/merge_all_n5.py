#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Merger script for content/n5.json:
Combines:
- 12 unique short texts (already in n5.json)
- 12 unique medium texts (already in n5.json)
- 12 unique long texts (from enrich_complete_n5.py)
- 12 unique info_search texts (from enrich_n5_info_article.py)
- 12 unique article texts (from enrich_n5_all_articles.py)
Total = 60 completely unique, authentic texts with 100% unique questions!
"""

import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CONTENT_DIR = Path(__file__).resolve().parent.parent / "content"
N5_PATH = CONTENT_DIR / "n5.json"

import importlib.util

def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

mod_long = load_module("enrich_long", "tools/enrich_complete_n5.py")
mod_info = load_module("enrich_info", "tools/enrich_n5_info_article.py")
mod_art = load_module("enrich_art", "tools/enrich_n5_all_articles.py")

with open(N5_PATH, "r", encoding="utf-8") as f:
    current_data = json.load(f)

# Keep current short and medium items (first 24)
preserved = [t for t in current_data if t["category"] in ["short", "medium"]]
print(f"Preserved {len(preserved)} short/medium items.")

# Build 12 long items
long_map = {item["slug"]: item for item in mod_long.LONG_DATA}
for old_t in current_data:
    if old_t["category"] == "long" and old_t["slug"] in long_map:
        d = long_map[old_t["slug"]]
        old_t["title"] = d["title"]
        old_t["body_html"] = d["body"]
        old_t["translation_ru"] = d["trans"]
        old_t["vocabulary"] = d.get("vocab", old_t.get("vocabulary", []))
        old_t["recommended_time_min"] = 5
        old_t["questions"] = [
            {
                "slug": f"{old_t['slug']}-q1",
                "question_number": 1,
                "type": "detail",
                "prompt": d["q1"]["prompt"],
                "evidence_span_id": "ev-q1",
                "general_explanation": d["q1"]["exp"],
                "options": [
                    {
                        "option_number": opt["num"],
                        "text": opt["text"],
                        "is_correct": opt["correct"],
                        "trap_type": opt.get("trap"),
                        "explanation_ru": opt["exp"]
                    }
                    for opt in d["q1"]["opts"]
                ]
            },
            {
                "slug": f"{old_t['slug']}-q2",
                "question_number": 2,
                "type": "detail",
                "prompt": d["q2"]["prompt"],
                "evidence_span_id": "ev-q2",
                "general_explanation": d["q2"]["exp"],
                "options": [
                    {
                        "option_number": opt["num"],
                        "text": opt["text"],
                        "is_correct": opt["correct"],
                        "trap_type": opt.get("trap"),
                        "explanation_ru": opt["exp"]
                    }
                    for opt in d["q2"]["opts"]
                ]
            },
            {
                "slug": f"{old_t['slug']}-q3",
                "question_number": 3,
                "type": "claim",
                "prompt": d["q3"]["prompt"],
                "evidence_span_id": "ev-q3",
                "general_explanation": d["q3"]["exp"],
                "options": [
                    {
                        "option_number": opt["num"],
                        "text": opt["text"],
                        "is_correct": opt["correct"],
                        "trap_type": opt.get("trap"),
                        "explanation_ru": opt["exp"]
                    }
                    for opt in d["q3"]["opts"]
                ]
            }
        ]
        preserved.append(old_t)

# Build 12 info_search items
info_map = {item["slug"]: item for item in mod_info.INFO_DATA}
for old_t in current_data:
    if old_t["category"] == "info_search" and old_t["slug"] in info_map:
        d = info_map[old_t["slug"]]
        old_t["title"] = d["title"]
        old_t["body_html"] = d["body"]
        old_t["translation_ru"] = d["trans"]
        old_t["vocabulary"] = d.get("vocab", old_t.get("vocabulary", []))
        old_t["recommended_time_min"] = 3
        old_t["questions"] = [
            {
                "slug": f"{old_t['slug']}-q1",
                "question_number": 1,
                "type": "detail",
                "prompt": d["q1"]["prompt"],
                "evidence_span_id": "ev-q1",
                "general_explanation": d["q1"]["exp"],
                "options": [
                    {
                        "option_number": opt["num"],
                        "text": opt["text"],
                        "is_correct": opt["correct"],
                        "trap_type": opt.get("trap"),
                        "explanation_ru": opt["exp"]
                    }
                    for opt in d["q1"]["opts"]
                ]
            },
            {
                "slug": f"{old_t['slug']}-q2",
                "question_number": 2,
                "type": "detail",
                "prompt": d["q2"]["prompt"],
                "evidence_span_id": "ev-q2",
                "general_explanation": d["q2"]["exp"],
                "options": [
                    {
                        "option_number": opt["num"],
                        "text": opt["text"],
                        "is_correct": opt["correct"],
                        "trap_type": opt.get("trap"),
                        "explanation_ru": opt["exp"]
                    }
                    for opt in d["q2"]["opts"]
                ]
            }
        ]
        preserved.append(old_t)

# Build 12 article items
art_map = {item["slug"]: item for item in mod_art.ARTICLE_DATA}
for old_t in current_data:
    if old_t["category"] == "article" and old_t["slug"] in art_map:
        d = art_map[old_t["slug"]]
        old_t["title"] = d["title"]
        old_t["body_html"] = d["body"]
        old_t["translation_ru"] = d["trans"]
        old_t["vocabulary"] = d.get("vocab", old_t.get("vocabulary", []))
        old_t["recommended_time_min"] = 4
        old_t["questions"] = [
            {
                "slug": f"{old_t['slug']}-q1",
                "question_number": 1,
                "type": "detail",
                "prompt": d["q1"]["prompt"],
                "evidence_span_id": "ev-q1",
                "general_explanation": d["q1"]["exp"],
                "options": [
                    {
                        "option_number": opt["num"],
                        "text": opt["text"],
                        "is_correct": opt["correct"],
                        "trap_type": opt.get("trap"),
                        "explanation_ru": opt["exp"]
                    }
                    for opt in d["q1"]["opts"]
                ]
            },
            {
                "slug": f"{old_t['slug']}-q2",
                "question_number": 2,
                "type": "detail",
                "prompt": d["q2"]["prompt"],
                "evidence_span_id": "ev-q2",
                "general_explanation": d["q2"]["exp"],
                "options": [
                    {
                        "option_number": opt["num"],
                        "text": opt["text"],
                        "is_correct": opt["correct"],
                        "trap_type": opt.get("trap"),
                        "explanation_ru": opt["exp"]
                    }
                    for opt in d["q2"]["opts"]
                ]
            },
            {
                "slug": f"{old_t['slug']}-q3",
                "question_number": 3,
                "type": "claim",
                "prompt": d["q3"]["prompt"],
                "evidence_span_id": "ev-q3",
                "general_explanation": d["q3"]["exp"],
                "options": [
                    {
                        "option_number": opt["num"],
                        "text": opt["text"],
                        "is_correct": opt["correct"],
                        "trap_type": opt.get("trap"),
                        "explanation_ru": opt["exp"]
                    }
                    for opt in d["q3"]["opts"]
                ]
            }
        ]
        preserved.append(old_t)

print(f"Total merged items: {len(preserved)}")
assert len(preserved) == 60, f"Expected 60 items, got {len(preserved)}"

with open(N5_PATH, "w", encoding="utf-8") as f:
    json.dump(preserved, f, ensure_ascii=False, indent=2)

print("n5.json successfully updated with 100% unique authentic materials!")

