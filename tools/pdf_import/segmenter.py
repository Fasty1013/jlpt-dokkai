#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF Text & Exam Segmentation Module.
Segments extracted document text into:
  - Reading Passages (Text blocks)
  - Questions (Prompt, Underlined evidence spans)
  - Options (4 choices with normalized numbers)
  - Answer Key matching (解答 / 正解 / Answer Key)
  - Explanations (解説)
"""

import re
from typing import Dict, Any, List, Optional, Tuple

# Patterns for question headers: 問1, 問題1, (1), 1.
QUESTION_HEADER_REGEX = re.compile(
    r"(?:(?:^|\n)\s*(?:\[問\s*([0-9]+)\]|問\s*([0-9]+)|問題\s*([0-9]+)|第\s*([0-9]+)\s*問))\s*(.*?)(?=(?:(?:^|\n)\s*(?:\[問\s*[0-9]+\]|問\s*[0-9]+|問題\s*[0-9]+|第\s*[0-9]+\s*問))|\Z)",
    re.DOTALL
)

# Patterns for option items: 1, 2, 3, 4 or ①, ②, ③, ④ or (1), (2) or ア, イ
OPTION_ITEM_REGEX = re.compile(
    r"(?:(?:^|\n|\s)\s*(?:[①②③④❶❷❸❹]|(?:\(([1-4])\))|([1-4])[\.．\s]|[アイウエ][\.．\s]|[ABCD][\.．\s]))\s*([^\n①②③④❶❷❸❹\(\)]+)"
)

# Answer key headers
ANSWER_KEY_HEADERS = ["解答", "正解", "答え", "Answer Key", "解答一覧", "正解表"]

def parse_answer_key(text: str) -> Dict[int, int]:
    """
    Парсит секцию ключей ответов из текста книги.
    Поддерживаемые форматы:
      - 1: 3, 2: 1, 3: 4
      - 問1: ③, 問2: ①
      - 1-3, 2-1, 3-2
      - Табличные строки: 1 ③ / 2 ①
    Возвращает словарь: {question_number: correct_option_number}.
    """
    key_map = {}
    if not text:
        return key_map

    # 1. Поиск блока ключа ответов
    answer_block = ""
    for hdr in ANSWER_KEY_HEADERS:
        if hdr in text:
            parts = text.split(hdr, 1)
            if len(parts) > 1:
                answer_block = parts[1][:2000]
                break

    if not answer_block:
        answer_block = text  # пробуем сканировать весь текст при отсутствии явного заголовка

    # Паттерн: [問] 1 [: = -] [①-④|1-4]
    matches = re.findall(
        r"(?:問\s*([0-9]+)|([0-9]+))\s*(?:[:：\-=ー\s]+)\s*([①②③④❶❷❸❹1-4アイウエABCD])",
        answer_block
    )

    opt_trans = {
        "①": 1, "②": 2, "③": 3, "④": 4,
        "❶": 1, "❷": 2, "❸": 3, "❹": 4,
        "1": 1, "2": 2, "3": 3, "4": 4,
        "ア": 1, "イ": 2, "ウ": 3, "エ": 4,
        "A": 1, "B": 2, "C": 3, "D": 4
    }

    for q_match1, q_match2, ans_char in matches:
        q_num_str = q_match1 or q_match2
        if q_num_str and ans_char in opt_trans:
            q_num = int(q_num_str)
            key_map[q_num] = opt_trans[ans_char]

    return key_map

def extract_options_from_block(block_text: str) -> List[Dict[str, Any]]:
    """
    Извлекает 4 варианта ответа из текстового блока вопроса.
    """
    options = []
    # Ищем строчные варианты
    lines = block_text.split("\n")
    cur_opt_num = 1

    opt_markers = [
        ("1", ["1.", "1 ", "①", "(1)", "ア", "A"]),
        ("2", ["2.", "2 ", "②", "(2)", "イ", "B"]),
        ("3", ["3.", "3 ", "③", "(3)", "ウ", "C"]),
        ("4", ["4.", "4 ", "④", "(4)", "エ", "D"])
    ]

    for line in lines:
        line_s = line.strip()
        if not line_s:
            continue
        # Проверяем маркеры вариантов
        for expected_num, markers in opt_markers:
            for m in markers:
                if line_s.startswith(m):
                    opt_body = line_s[len(m):].strip()
                    if opt_body:
                        options.append({
                            "option_number": int(expected_num),
                            "text": opt_body
                        })
                    break

    # Дедупликация по option_number
    seen = set()
    deduped = []
    for opt in options:
        num = opt["option_number"]
        if num not in seen and 1 <= num <= 4:
            seen.add(num)
            deduped.append(opt)

    return sorted(deduped, key=lambda x: x["option_number"])

def segment_passage_and_questions(full_text: str, html_text: str) -> Dict[str, Any]:
    """
    Сегментирует страницу или документ на текст для чтения и вопросы с вариантами.
    """
    # 1. Поиск границы между текстом для чтения и вопросами
    # Часто разделяется маркерами: 問題, 問1, 次の文章を読んで
    q_start_idx = -1
    for marker in ["問1", "問題1", "[問1]", "(1)"]:
        idx = full_text.find(marker)
        if idx != -1:
            if q_start_idx == -1 or idx < q_start_idx:
                q_start_idx = idx

    if q_start_idx != -1 and q_start_idx > 50:
        passage_raw = full_text[:q_start_idx].strip()
        passage_html = html_text[:q_start_idx].strip()
        questions_part = full_text[q_start_idx:].strip()
    else:
        passage_raw = full_text.strip()
        passage_html = html_text.strip()
        questions_part = ""

    # Обработка Underlined Spans: 下線部 -> <span id="ev-q{N}" data-evidence="ev-q{N}">
    # Ищем маркеры вида 【1】 или 下線部(1) в passage_html
    def replace_underline(match):
        q_n = match.group(1) or match.group(2) or "1"
        content = match.group(3) if len(match.groups()) >= 3 else match.group(0)
        return f'<span id="ev-q{q_n}" data-evidence="ev-q{q_n}" class="evidence-highlight">{content}</span>'

    passage_html = re.sub(r"【([0-9]+)】([^【】\n]+)", replace_underline, passage_html)

    # 2. Парсинг вопросов
    parsed_questions = []
    if questions_part:
        # Разбиваем строго по маркерам вопросов JLPT (問1, 問題1, 第1問)
        q_blocks = re.split(r"(?=(?:^|\n)\s*(?:\[問\s*[0-9]+\]|問\s*[0-9]+|問題\s*[0-9]+|第\s*[0-9]+\s*問))", questions_part)
        q_idx = 1
        for block in q_blocks:
            b_clean = block.strip()
            if not b_clean:
                continue

            lines = b_clean.split("\n")
            prompt_line = lines[0].strip()
            
            # Определяем номер вопроса из заголовка
            header_match = re.search(r"(?:\[問\s*([0-9]+)\]|問\s*([0-9]+)|問題\s*([0-9]+)|第\s*([0-9]+)\s*問)", prompt_line)
            if header_match:
                parsed_num = int(header_match.group(1) or header_match.group(2) or header_match.group(3) or header_match.group(4))
            else:
                parsed_num = q_idx

            # Очищаем маркер вопроса из промпта
            clean_prompt = re.sub(r"^(?:\[問\s*[0-9]+\]|問\s*[0-9]+|問題\s*[0-9]+|第\s*[0-9]+\s*問)\s*", "", prompt_line)

            options = extract_options_from_block(b_clean)

            if len(options) >= 2 or clean_prompt:
                parsed_questions.append({
                    "question_number": parsed_num,
                    "prompt": clean_prompt or f"問題 {parsed_num}",
                    "evidence_span_id": f"ev-q{parsed_num}",
                    "options": options,
                    "raw_block": b_clean
                })
                q_idx += 1

    return {
        "passage_text": passage_raw,
        "passage_html": passage_html,
        "questions": parsed_questions
    }
