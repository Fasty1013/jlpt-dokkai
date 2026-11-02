#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Difficulty Vector Calculation and Tolerance Checker.
Computes structural, lexical, and distractor metrics for JLPT reading texts.
"""

import re
from typing import Dict, Any, List, Optional, Tuple
from tools.level_check.analyzer import clean_japanese_html, is_cjk_kanji


def split_sentences(text: str) -> List[str]:
    """Разбивает японский текст на предложения по пунктуации."""
    if not text:
        return []
    # Разделяем по японским и европейским знакам препинания
    raw_sentences = re.split(r"[。\n！？!?]", text)
    sentences = [s.strip() for s in raw_sentences if s.strip()]
    return sentences if sentences else [text.strip()]


def calculate_difficulty_vector(
    content_html: str,
    questions: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Рассчитывает многомерный вектор сложности текста и сопутствующих вопросов.
    Метрики:
    - char_count: количество символов
    - sentence_count: количество предложений
    - avg_sentence_len: средняя длина предложения
    - max_sentence_len: максимальная длина предложения
    - kanji_ratio: доля кандзи в тексте
    - num_questions: число вопросов
    - distinct_traps: количество уникальных типов ловушек
    """
    plain = clean_japanese_html(content_html)
    char_count = len(plain)
    if char_count == 0:
        return {
            "char_count": 0,
            "sentence_count": 0,
            "avg_sentence_len": 0.0,
            "max_sentence_len": 0,
            "kanji_ratio": 0.0,
            "num_questions": len(questions or []),
            "distinct_traps": 0
        }

    sentences = split_sentences(plain)
    sentence_count = max(1, len(sentences))
    sent_lens = [len(s) for s in sentences]
    avg_sentence_len = round(char_count / sentence_count, 1)
    max_sentence_len = max(sent_lens) if sent_lens else char_count

    kanji_count = sum(1 for ch in plain if is_cjk_kanji(ch))
    kanji_ratio = round(kanji_count / char_count, 3)

    trap_types = set()
    num_questions = 0
    if questions:
        num_questions = len(questions)
        for q in questions:
            opts = q.get("options", [])
            for opt in opts:
                ttype = opt.get("trap_type")
                if ttype:
                    trap_types.add(ttype)

    return {
        "char_count": char_count,
        "sentence_count": sentence_count,
        "avg_sentence_len": avg_sentence_len,
        "max_sentence_len": max_sentence_len,
        "kanji_ratio": kanji_ratio,
        "num_questions": num_questions,
        "distinct_traps": len(trap_types)
    }


def is_within_difficulty_tolerance(
    vector: Dict[str, Any],
    band: Dict[str, Any]
) -> Tuple[bool, List[str]]:
    """
    Проверяет, укладывается ли вектор сложности в допустимые границы [p10, p90].
    """
    violations = []
    for metric in ["char_count", "avg_sentence_len", "max_sentence_len", "kanji_ratio"]:
        if metric in band and metric in vector:
            min_val, max_val = band[metric]
            val = vector[metric]
            if val < min_val:
                violations.append(f"{metric} {val} < min {min_val}")
            elif val > max_val:
                violations.append(f"{metric} {val} > max {max_val}")

    return len(violations) == 0, violations
