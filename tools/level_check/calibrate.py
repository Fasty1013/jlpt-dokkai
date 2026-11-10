#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Calibration Script for Difficulty Bands [p10, p90].
Scans all texts in dokkai.db, calculates percentiles per difficulty profile,
and generates content/difficulty_bands.yaml.
"""

import os
import sys
import json
from pathlib import Path
from collections import defaultdict
from typing import Dict, Any, List

# Ensure UTF-8 on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.core.database import SessionLocal
from app import models
from tools.level_check.difficulty import calculate_difficulty_vector

OUTPUT_FILE = PROJECT_ROOT / "content" / "difficulty_bands.yaml"
MIN_REFERENCE_ITEMS = 8

EXPERT_FALLBACKS = {
    "N5": {"char_count": [60, 260], "avg_sentence_len": [12.0, 32.0], "max_sentence_len": [20, 50], "kanji_ratio": [0.08, 0.32]},
    "N4": {"char_count": [120, 420], "avg_sentence_len": [16.0, 42.0], "max_sentence_len": [28, 65], "kanji_ratio": [0.12, 0.36]},
    "N3": {"char_count": [220, 680], "avg_sentence_len": [22.0, 55.0], "max_sentence_len": [40, 85], "kanji_ratio": [0.18, 0.42]},
    "N2": {"char_count": [380, 950], "avg_sentence_len": [28.0, 70.0], "max_sentence_len": [55, 115], "kanji_ratio": [0.22, 0.46]},
    "N1": {"char_count": [550, 1450], "avg_sentence_len": [32.0, 85.0], "max_sentence_len": [65, 145], "kanji_ratio": [0.26, 0.52]},
}


def compute_percentile(sorted_list: List[float], p: float) -> float:
    """Вычисляет p-й процентиль (p от 0.0 до 1.0)."""
    if not sorted_list:
        return 0.0
    k = (len(sorted_list) - 1) * p
    f = int(k)
    c = min(f + 1, len(sorted_list) - 1)
    d = k - f
    return round(sorted_list[f] + d * (sorted_list[c] - sorted_list[f]), 2)


def dump_simple_yaml(data: Any, indent: int = 0) -> str:
    """Сериализует словарь в валидный YAML без внешних зависимостей."""
    lines = []
    prefix = "  " * indent
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, dict):
                lines.append(f"{prefix}{k}:")
                lines.append(dump_simple_yaml(v, indent + 1))
            elif isinstance(v, list):
                if all(not isinstance(x, (dict, list)) for x in v):
                    lines.append(f"{prefix}{k}: {v}")
                else:
                    lines.append(f"{prefix}{k}:")
                    lines.append(dump_simple_yaml(v, indent + 1))
            elif isinstance(v, bool):
                lines.append(f"{prefix}{k}: {'true' if v else 'false'}")
            else:
                lines.append(f"{prefix}{k}: {v}")
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, (dict, list)):
                lines.append(f"{prefix}-")
                lines.append(dump_simple_yaml(item, indent + 1))
            else:
                lines.append(f"{prefix}- {item}")
    return "\n".join(lines)


def run_calibration():
    db = SessionLocal()
    try:
        texts = db.query(models.Text).filter(models.Text.is_active == True).all()
        print(f"Calibrating difficulty bands across {len(texts)} active texts...")

        profile_data = defaultdict(lambda: defaultdict(list))

        for t in texts:
            pkey = t.profile_key
            if not pkey:
                continue

            vec = t.difficulty_vector
            if not vec or "char_count" not in vec:
                questions_data = [{"options": [{"trap_type": opt.trap_type} for opt in q.options]} for q in t.questions]
                vec = calculate_difficulty_vector(t.content_html, questions_data)
                t.difficulty_vector = vec

            for k in ["char_count", "avg_sentence_len", "max_sentence_len", "kanji_ratio"]:
                if k in vec:
                    profile_data[pkey][k].append(vec[k])

        db.commit()

        bands_output: Dict[str, Any] = {
            "version": "1.0",
            "min_reference_items": MIN_REFERENCE_ITEMS,
            "profiles": {}
        }

        calibrated_count = 0
        fallback_count = 0

        for pkey, metrics in sorted(profile_data.items()):
            n_items = len(metrics["char_count"])
            lvl = pkey.split(":")[0] if ":" in pkey else "N3"
            expert_fallback = EXPERT_FALLBACKS.get(lvl, EXPERT_FALLBACKS["N3"])

            profile_entry = {
                "sample_size": n_items,
                "is_expert_fallback": (n_items < MIN_REFERENCE_ITEMS),
                "metrics": {}
            }

            if n_items >= MIN_REFERENCE_ITEMS:
                calibrated_count += 1
                for m_name in ["char_count", "avg_sentence_len", "max_sentence_len", "kanji_ratio"]:
                    vals = sorted(metrics[m_name])
                    p10 = compute_percentile(vals, 0.10)
                    p90 = compute_percentile(vals, 0.90)
                    profile_entry["metrics"][m_name] = [p10, p90]
            else:
                fallback_count += 1
                # Используем экспертные допуски с адаптацией под длину band
                length_band = pkey.split(":")[-1] if len(pkey.split(":")) >= 5 else "M"
                band_scale = {"XS": 0.5, "S": 0.75, "M": 1.0, "L": 1.4, "XL": 2.0}.get(length_band, 1.0)
                
                for m_name, (fb_min, fb_max) in expert_fallback.items():
                    if m_name == "char_count":
                        profile_entry["metrics"][m_name] = [round(fb_min * band_scale), round(fb_max * band_scale)]
                    else:
                        profile_entry["metrics"][m_name] = [fb_min, fb_max]

            bands_output["profiles"][pkey] = profile_entry

        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
        yaml_content = dump_simple_yaml(bands_output)
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(yaml_content)

        json_file = OUTPUT_FILE.with_suffix(".json")
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(bands_output, f, ensure_ascii=False, indent=2)

        print(f"Calibration finished!")
        print(f"Total profiles: {len(bands_output['profiles'])}")
        print(f"Empirically calibrated (>= {MIN_REFERENCE_ITEMS} items): {calibrated_count}")
        print(f"Expert fallback calibrated (< {MIN_REFERENCE_ITEMS} items): {fallback_count}")
        print(f"Saved to: {OUTPUT_FILE} and {json_file}")

    finally:
        db.close()


if __name__ == "__main__":
    run_calibration()
