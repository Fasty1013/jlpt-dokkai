#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF Text & Layout Extractor Module.
Extracts structured text from PDF pages, handles multi-column / vertical text (縦書き),
and detects ruby furigana representations.
"""

import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import pypdf

# Regex for kanji followed by furigana in parentheses
# e.g., 漢字（かんじ） or 漢字(かんじ) or 図書館（としょかん）
RUBY_PAREN_REGEX = re.compile(r"([一-龯々仝〆〇]+)[（\(]([ぁ-んァ-ヶー]+)[）\)]")

# Circled numbers mapping
CIRCLED_NUMS = {
    "①": "1", "②": "2", "③": "3", "④": "4",
    "❶": "1", "❷": "2", "❸": "3", "❹": "4",
    "一": "1", "二": "2", "三": "3", "四": "4",
    "ア": "1", "イ": "2", "ウ": "3", "エ": "4",
    "A": "1", "B": "2", "C": "3", "D": "4",
    "a": "1", "b": "2", "c": "3", "d": "4"
}

def normalize_japanese_text(text: str) -> str:
    """Нормализует пробелы, полноширинные цифры и символы."""
    if not text:
        return ""
    # Заменяем полноширинные цифры ０-９ на 0-9
    text = text.translate(str.maketrans("０１２３４５６７８９", "0123456789"))
    # Заменяем полноширинные латинские буквы Ａ-Ｚ на A-Z
    text = text.translate(str.maketrans("ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ", "ABCDEFGHIJKLMNOPQRSTUVWXYZ"))
    # Заменяем полноширинные пробелы
    text = text.replace("　", " ")
    return text

def convert_inline_furigana_to_ruby(text: str) -> Tuple[str, bool]:
    """
    Преобразует инлайновые чтения кандзи в круглых скобках в HTML5 <ruby> теги.
    Пример: 図書館（としょかん） -> <ruby>図書館<rt>としょかん</rt></ruby>
    Возвращает (преобразованный текст, флаг надежности).
    """
    if not text:
        return "", True

    has_matches = bool(RUBY_PAREN_REGEX.search(text))
    converted = RUBY_PAREN_REGEX.sub(r"<ruby>\1<rt>\2</rt></ruby>", text)

    # Проверяем, нет ли подозрительных пустых скобок
    unreliable = bool(re.search(r"[一-龯々][（\(]\s*[）\)]", converted))
    return converted, not unreliable

def detect_vertical_writing(text: str) -> bool:
    """
    Эвристически определяет, сверстан ли текст в вертикальном формате (縦書き):
    высокая частота одиночных символов на строку при переносах строк.
    """
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    if len(lines) < 6:
        return False
    single_char_lines = sum(1 for line in lines if len(line) <= 2)
    return (single_char_lines / len(lines)) > 0.45

def reassemble_vertical_text(text: str) -> str:
    """
    Восстанавливает вертикальный текст (колонки справа налево) в горизонтальный абзац.
    """
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    # Объединяем последовательные короткие строки в связный текст
    return "".join(lines)

def extract_pdf_pages(file_path: Path) -> List[Dict[str, Any]]:
    """
    Извлекает текст постранично с метаданными и определением вертикальной вёрстки.
    """
    reader = pypdf.PdfReader(str(file_path))
    pages_data = []

    for idx, page in enumerate(reader.pages, start=1):
        raw_text = page.extract_text() or ""
        norm_text = normalize_japanese_text(raw_text)

        is_vertical = detect_vertical_writing(norm_text)
        if is_vertical:
            processed_text = reassemble_vertical_text(norm_text)
        else:
            processed_text = norm_text

        ruby_html, furigana_reliable = convert_inline_furigana_to_ruby(processed_text)

        pages_data.append({
            "page_number": idx,
            "raw_text": raw_text,
            "text": processed_text,
            "html_with_ruby": ruby_html,
            "is_vertical": is_vertical,
            "furigana_reliable": furigana_reliable,
            "char_count": len(processed_text.replace(" ", ""))
        })

    return pages_data
