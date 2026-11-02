#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Japanese Furigana Tokenizer Module for Dokkai Master.
Uses pykakasi / janome to deterministically tokenize Japanese text and generate ruby markup.
"""

from typing import List, Dict, Any
import pykakasi


_k = None


def get_kakasi():
    global _k
    if _k is None:
        _k = pykakasi.kakasi()
    return _k


def is_has_kanji(text: str) -> bool:
    """Проверяет, содержит ли строка кандзи."""
    return any('\u4e00' <= ch <= '\u9faf' or '\u3400' <= ch <= '\u4dbf' for ch in text)


def add_furigana_to_japanese_text(text: str) -> str:
    """
    Преобразует японский текст в HTML с тегами <ruby> для кандзи.
    Текст без кандзи остаётся без тегов.
    """
    if not text:
        return ""

    kakasi_inst = get_kakasi()
    tokens = kakasi_inst.convert(text)
    output_parts: List[str] = []

    for item in tokens:
        orig = item.get("orig", "")
        hira = item.get("hira", "")
        if is_has_kanji(orig) and hira and orig != hira:
            output_parts.append(f"<ruby>{orig}<rt>{hira}</rt></ruby>")
        else:
            output_parts.append(orig)

    return "".join(output_parts)


def extract_vocabulary_with_readings(text: str) -> List[Dict[str, str]]:
    """
    Извлекает список слов с чтениями хираганой.
    """
    if not text:
        return []

    kakasi_inst = get_kakasi()
    tokens = kakasi_inst.convert(text)
    vocab = []
    seen = set()

    for item in tokens:
        orig = item.get("orig", "").strip()
        hira = item.get("hira", "").strip()
        if is_has_kanji(orig) and len(orig) >= 1 and orig not in seen:
            seen.add(orig)
            vocab.append({
                "word": orig,
                "furigana": hira,
                "translation": ""
            })

    return vocab

