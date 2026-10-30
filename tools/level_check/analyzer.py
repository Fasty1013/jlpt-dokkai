#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JLPT Level Analyzer Module.
Evaluates Japanese reading texts against JLPT level benchmarks (N5 - N1).
Computes structural, lexical, and grammatical metrics, and renders verdicts:
  - ok
  - too_easy
  - too_hard
  - uncertain
"""

import re
import json
from pathlib import Path
from typing import Dict, Any, List, Set, Tuple

BASE_DIR = Path(__file__).resolve().parent.parent.parent
REFS_DIR = BASE_DIR / "content" / "level_refs"

LEVEL_ORDER = ["N5", "N4", "N3", "N2", "N1"]
LEVEL_INDEX = {lvl: idx for idx, lvl in enumerate(LEVEL_ORDER)}

_CACHED_REFS: Dict[str, Dict[str, Any]] = {}

def get_level_ref(level: str) -> Dict[str, Any]:
    level = level.upper()
    if level in _CACHED_REFS:
        return _CACHED_REFS[level]

    ref_file = REFS_DIR / f"{level.lower()}.json"
    if not ref_file.exists():
        # Fallback default
        return {
            "benchmark_kanji": [],
            "grammar_patterns": [],
            "metric_thresholds": {
                "max_sentence_len": 60,
                "avg_sentence_len_target": 30,
                "kanji_ratio_max": 0.35,
                "text_len_range": (150, 600)
            }
        }

    with open(ref_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    data["kanji_set"] = set(data.get("benchmark_kanji", []))
    _CACHED_REFS[level] = data
    return data

def clean_japanese_html(html: str) -> str:
    """
    Очищает HTML разметку, сохраняя кандзи (основы ruby), удаляя <rt> фуригану,
    теги доказательств и форматирования.
    """
    if not html:
        return ""
    # Удаляем содержимое <rt>...</rt>
    text = re.sub(r"<rt>.*?</rt>", "", html, flags=re.DOTALL)
    # Удаляем любые другие HTML теги
    text = re.sub(r"<[^>]+>", "", text)
    # Удаляем HTML сущности
    text = text.replace("&nbsp;", " ").replace("&quot;", '"').replace("&amp;", "&")
    # Удаляем лишние пробелы и переносы
    text = re.sub(r"\s+", " ", text).strip()
    return text

def is_cjk_kanji(ch: str) -> bool:
    """Проверяет, является ли символ кандзи (иероглифом CJK Unified Ideograph)."""
    code = ord(ch)
    return (0x4E00 <= code <= 0x9FFF) or (0x3400 <= code <= 0x4DBF)

def split_sentences(text: str) -> List[str]:
    """Разбивает японский текст на предложения по знакам пунктуации."""
    raw = re.split(r"[。！？!?\n]+", text)
    sentences = [s.strip() for s in raw if s.strip()]
    return sentences if sentences else [text]

def analyze(text_html: str, target_level: str) -> Dict[str, Any]:
    """
    Анализирует текст и возвращает подробный отчёт с метриками и вердиктом.
    Вердикты: 'ok', 'too_easy', 'too_hard', 'uncertain'.
    """
    target_level = target_level.upper()
    if target_level not in LEVEL_INDEX:
        raise ValueError(f"Неизвестный уровень JLPT: {target_level}")

    clean = clean_japanese_html(text_html)
    total_chars = len(clean.replace(" ", ""))

    if total_chars == 0:
        return {
            "verdict": "too_easy",
            "reasons": ["Текст пуст"],
            "metrics": {"total_chars": 0}
        }

    sentences = split_sentences(clean)
    sentence_count = len(sentences)
    avg_sentence_len = total_chars / sentence_count if sentence_count else 0
    max_sentence_len = max(len(s.replace(" ", "")) for s in sentences) if sentences else 0

    # Kanji analysis
    kanji_chars = [ch for ch in clean if is_cjk_kanji(ch)]
    kanji_count = len(kanji_chars)
    kanji_ratio = kanji_count / total_chars if total_chars else 0

    ref = get_level_ref(target_level)
    target_kanji_set = ref.get("kanji_set", set())

    # Кандзи выше заявленного уровня
    higher_kanji = [ch for ch in kanji_chars if ch not in target_kanji_set]
    higher_kanji_unique = sorted(list(set(higher_kanji)))
    higher_kanji_ratio = len(higher_kanji) / kanji_count if kanji_count else 0

    # Grammar pattern analysis: ищем грамматические конструкции из более высоких уровней
    curr_idx = LEVEL_INDEX[target_level]
    higher_grammar_detected = []
    for higher_lvl in LEVEL_ORDER[curr_idx + 1:]:
        higher_ref = get_level_ref(higher_lvl)
        patterns = higher_ref.get("grammar_patterns", [])
        for pat in patterns:
            # Убираем тильду
            clean_pat = pat.replace("〜", "")
            if len(clean_pat) >= 2 and clean_pat in clean:
                higher_grammar_detected.append(f"{higher_lvl}:{pat}")

    # Thresholds
    thresholds = ref.get("metric_thresholds", {
        "max_sentence_len": 60,
        "avg_sentence_len_target": 30,
        "kanji_ratio_max": 0.35,
        "text_len_range": (150, 600)
    })

    t_max_sent = thresholds["max_sentence_len"]
    t_avg_sent = thresholds["avg_sentence_len_target"]
    t_kanji_ratio = thresholds["kanji_ratio_max"]
    min_len, max_len = thresholds["text_len_range"]

    reasons = []
    hard_points = 0
    easy_points = 0

    # Оценка сложности по предложениям
    if max_sentence_len > t_max_sent * 1.3:
        hard_points += 2
        reasons.append(f"Длинные предложения: макс. {max_sentence_len} зн. (норматив до {t_max_sent})")
    elif max_sentence_len < t_max_sent * 0.4 and curr_idx >= 2:
        easy_points += 1
        reasons.append(f"Слишком простые короткие предложения для уровня {target_level}")

    # Оценка плотности кандзи
    if kanji_ratio > t_kanji_ratio * 1.35 and curr_idx <= 2:
        hard_points += 2
        reasons.append(f"Высокая доля кандзи: {kanji_ratio:.1%} (порог {t_kanji_ratio:.1%})")
    elif kanji_ratio < t_kanji_ratio * 0.4 and curr_idx >= 2:
        easy_points += 2
        reasons.append(f"Низкая доля кандзи: {kanji_ratio:.1%} (типично для N4/N5)")

    # Кандзи выше уровня
    if curr_idx <= 1 and higher_kanji_ratio > 0.35:
        hard_points += 2
        reasons.append(f"Доля кандзи выше уровня: {higher_kanji_ratio:.1%} ({len(higher_kanji_unique)} редких знаков)")

    # Грамматика выше уровня
    if higher_grammar_detected:
        if curr_idx <= 1 and len(higher_grammar_detected) >= 2:
            hard_points += 2
            reasons.append(f"Обнаружены конструкции высших уровней: {', '.join(higher_grammar_detected[:3])}")
        elif curr_idx == 2 and any(p.startswith("N1") for p in higher_grammar_detected):
            hard_points += 1
            reasons.append(f"Конструкции N1 в тексте N3: {', '.join(higher_grammar_detected[:2])}")

    # Длина текста
    if total_chars < min_len * 0.5:
        easy_points += 1
        reasons.append(f"Текст короче норматива: {total_chars} зн. (мин. {min_len})")
    elif total_chars > max_len * 1.6 and curr_idx <= 1:
        hard_points += 1
        reasons.append(f"Текст длиннее норматива для {target_level}: {total_chars} зн.")

    # Вынесение вердикта
    if hard_points >= 3 and hard_points > easy_points:
        verdict = "too_hard"
    elif easy_points >= 3 and easy_points > hard_points:
        verdict = "too_easy"
    elif hard_points >= 2 or easy_points >= 2:
        verdict = "uncertain"
    else:
        verdict = "ok"

    return {
        "target_level": target_level,
        "verdict": verdict,
        "reasons": reasons if reasons else ["Параметры текста соответствуют уровню"],
        "metrics": {
            "total_chars": total_chars,
            "sentence_count": sentence_count,
            "avg_sentence_len": round(avg_sentence_len, 1),
            "max_sentence_len": max_sentence_len,
            "kanji_count": kanji_count,
            "kanji_ratio": round(kanji_ratio, 3),
            "higher_kanji_count": len(higher_kanji),
            "higher_kanji_ratio": round(higher_kanji_ratio, 3),
            "higher_grammar_count": len(higher_grammar_detected),
            "higher_grammar_samples": higher_grammar_detected[:5]
        }
    }

def check_corpus_monotonicity(records_by_level: Dict[str, List[str]]) -> Dict[str, Any]:
    """
    Проверяет монотонное возрастание метрик сложности:
    N5 < N4 < N3 < N2 < N1.
    """
    stats = {}
    for lvl in LEVEL_ORDER:
        htmls = records_by_level.get(lvl, [])
        if not htmls:
            continue
        analyzed = [analyze(h, lvl)["metrics"] for h in htmls]
        count = len(analyzed)
        stats[lvl] = {
            "count": count,
            "mean_chars": sum(m["total_chars"] for m in analyzed) / count,
            "mean_sent_len": sum(m["avg_sentence_len"] for m in analyzed) / count,
            "mean_max_sent_len": sum(m["max_sentence_len"] for m in analyzed) / count,
            "mean_kanji_ratio": sum(m["kanji_ratio"] for m in analyzed) / count
        }

    # Проверка монотонности
    monotonicity_report = {}
    metrics_to_check = ["mean_chars", "mean_sent_len", "mean_kanji_ratio"]
    all_monotonic = True

    for m in metrics_to_check:
        values = [stats[lvl][m] for lvl in LEVEL_ORDER if lvl in stats]
        is_strictly_increasing = all(x < y for x, y in zip(values, values[1:]))
        monotonicity_report[m] = {
            "values": {lvl: round(stats[lvl][m], 3) for lvl in LEVEL_ORDER if lvl in stats},
            "is_monotonic": is_strictly_increasing
        }
        if not is_strictly_increasing:
            all_monotonic = False

    return {
        "all_monotonic": all_monotonic,
        "stats_by_level": stats,
        "details": monotonicity_report
    }

if __name__ == "__main__":
    test_sample = "<ruby>図書館<rt>としょかん</rt></ruby>は<ruby>午前<rt>ごぜん</rt></ruby>9時に開きます。"
    res = analyze(test_sample, "N5")
    print("Test N5 Analysis:", res)
