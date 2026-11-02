#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Novelty and Anti-Duplication Checker for Dokkai Master.
Implements:
1. Exact hash duplication check (SHA-256)
2. 5-shingle character Jaccard similarity (threshold <= 0.20)
3. Recent topics repetition window (window = 5)
"""

import hashlib
from typing import Set, List, Dict, Any, Optional
from tools.level_check.analyzer import clean_japanese_html

DEFAULT_SHINGLE_N = 5
MAX_JACCARD_THRESHOLD = 0.20
RECENT_TOPICS_WINDOW = 5


def compute_content_hash(text: str) -> str:
    """Вычисляет SHA-256 хеш нормализованного текста."""
    clean = clean_japanese_html(text)
    return hashlib.sha256(clean.encode("utf-8")).hexdigest()


def get_character_shingles(text: str, n: int = DEFAULT_SHINGLE_N) -> Set[str]:
    """
    Разбивает нормализованный японский текст на n-грамные шинглы символов.
    """
    clean = clean_japanese_html(text)
    if len(clean) < n:
        return {clean} if clean else set()
    return {clean[i:i + n] for i in range(len(clean) - n + 1)}


def calculate_jaccard(set_a: Set[str], set_b: Set[str]) -> float:
    """Вычисляет коэффициент Жаккара между двумя множествами шинглов."""
    if not set_a or not set_b:
        return 0.0
    intersection = len(set_a & set_b)
    union = len(set_a | set_b)
    return round(intersection / union, 4) if union > 0 else 0.0


def check_text_novelty(
    candidate_html: str,
    reference_html_list: List[str],
    max_jaccard: float = MAX_JACCARD_THRESHOLD
) -> Dict[str, Any]:
    """
    Проверяет новизну текста относительно списка существующих текстов.
    Возвращает статус новизны и максимальный коэффициент сходства.
    """
    cand_hash = compute_content_hash(candidate_html)
    cand_shingles = get_character_shingles(candidate_html)

    max_sim = 0.0
    clash_idx = None

    for idx, ref_html in enumerate(reference_html_list):
        ref_hash = compute_content_hash(ref_html)
        if cand_hash == ref_hash:
            return {
                "is_novel": False,
                "reason": "exact_hash_duplicate",
                "max_jaccard": 1.0,
                "matched_index": idx
            }

        ref_shingles = get_character_shingles(ref_html)
        sim = calculate_jaccard(cand_shingles, ref_shingles)
        if sim > max_sim:
            max_sim = sim
            clash_idx = idx

    is_novel = (max_sim <= max_jaccard)
    return {
        "is_novel": is_novel,
        "reason": "ok" if is_novel else f"high_similarity (Jaccard {max_sim:.3f} > {max_jaccard})",
        "max_jaccard": max_sim,
        "matched_index": clash_idx if not is_novel else None
    }


def check_recent_topic_clash(
    candidate_topics: List[str],
    recent_tasks_topics: List[List[str]],
    window: int = RECENT_TOPICS_WINDOW
) -> bool:
    """
    Проверяет повторение тем в скользящем окне последних N заданий пользователя.
    Возвращает True, если есть нежелательное пересечение тем.
    """
    if not candidate_topics or not recent_tasks_topics:
        return False

    cand_set = {t.lower().strip() for t in candidate_topics if t.strip()}
    window_slice = recent_tasks_topics[-window:]

    for past_topics in window_slice:
        past_set = {t.lower().strip() for t in past_topics if t.strip()}
        if len(cand_set & past_set) >= 2:
            return True

    return False

