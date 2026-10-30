#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Content Validator for JLPT Dokkai Master.
Validates all content files in content/*.json before loading into the database.
Ensures strict schema compliance, Anti-Cheat isolation, furigana accuracy,
and inventory count targets.
"""

import os
import sys
import json
import re
from pathlib import Path
from typing import List, Dict, Any, Tuple

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent
CONTENT_DIR = BASE_DIR / "content"

VALID_LEVELS = {"N5", "N4", "N3", "N2", "N1"}
VALID_CATEGORIES = {"short", "medium", "long", "info_search", "article"}
VALID_SOURCE_TYPES = {"jlpt_official", "news_adapted", "original", "pdf_import"}
VALID_QUESTION_TYPES = {"claim", "detail", "reference", "inference", "integrated", "info_search"}
VALID_TRAP_TYPES = {
    "overgeneralization",
    "opposite_meaning",
    "not_mentioned",
    "partial_match",
    "extreme_condition",
    "subject_swap",
    "fact_opinion_confusion",
    "temporal_mismatch",
    "misinterpretation"
}

# Target inventory counts from Stage 0 reconnaissance
EXPECTED_INVENTORY = {
    "N5": {
        "short": {"texts": 12, "questions": 12},
        "medium": {"texts": 12, "questions": 24},
        "long": {"texts": 12, "questions": 36},
        "info_search": {"texts": 12, "questions": 24},
        "article": {"texts": 12, "questions": 36},
    },
    "N4": {
        "short": {"texts": 12, "questions": 12},
        "medium": {"texts": 12, "questions": 24},
        "long": {"texts": 12, "questions": 36},
        "info_search": {"texts": 12, "questions": 24},
        "article": {"texts": 12, "questions": 36},
    },
    "N3": {
        "short": {"texts": 12, "questions": 12},
        "medium": {"texts": 12, "questions": 24},
        "long": {"texts": 12, "questions": 36},
        "info_search": {"texts": 12, "questions": 24},
        "article": {"texts": 13, "questions": 38},
    },
    "N2": {
        "short": {"texts": 12, "questions": 12},
        "medium": {"texts": 12, "questions": 24},
        "long": {"texts": 12, "questions": 36},
        "info_search": {"texts": 12, "questions": 24},
        "article": {"texts": 13, "questions": 38},
    },
    "N1": {
        "short": {"texts": 12, "questions": 12},
        "medium": {"texts": 12, "questions": 24},
        "long": {"texts": 12, "questions": 36},
        "info_search": {"texts": 12, "questions": 24},
        "article": {"texts": 12, "questions": 36},
    }
}

def strip_html_tags(text: str) -> str:
    """Удаляет HTML теги для измерения чистого количества японских символов."""
    clean = re.sub(r"<rt>.*?</rt>", "", text)
    clean = re.sub(r"<[^>]+>", "", clean)
    clean = re.sub(r"\s+", "", clean)
    return clean

def validate_ruby_tags(html: str, slug: str) -> List[str]:
    """Проверяет корректность тегов <ruby> и <rt>."""
    errors = []
    # Проверка незакрытых тегов ruby
    ruby_open = len(re.findall(r"<ruby>", html))
    ruby_close = len(re.findall(r"</ruby>", html))
    if ruby_open != ruby_close:
        errors.append(f"[{slug}] Несовпадение тегов <ruby>: открыто {ruby_open}, закрыто {ruby_close}")

    # Проверка незакрытых тегов rt
    rt_open = len(re.findall(r"<rt>", html))
    rt_close = len(re.findall(r"</rt>", html))
    if rt_open != rt_close:
        errors.append(f"[{slug}] Несовпадение тегов <rt>: открыто {rt_open}, закрыто {rt_close}")

    # Проверка содержимого rt: должна быть только кана или дефис/знаки
    rt_matches = re.findall(r"<rt>(.*?)</rt>", html)
    for rt_content in rt_matches:
        if not rt_content:
            errors.append(f"[{slug}] Пустой тег <rt></rt>")
        elif any(ord(c) < 128 and c not in "-・ " for c in rt_content):
            errors.append(f"[{slug}] Подозрительный латинский символ в фуригане: '<rt>{rt_content}</rt>'")

    return errors

def validate_text_record(record: Dict[str, Any], file_name: str, all_slugs: set) -> List[str]:
    errors = []
    slug = record.get("slug", "")

    if not slug:
        errors.append(f"[{file_name}] Запись не имеет обязательного поля 'slug'")
        return errors

    if slug in all_slugs:
        errors.append(f"[{file_name}] Дубликат slug: '{slug}'")
    all_slugs.add(slug)

    # Level & Category
    level = record.get("level")
    if level not in VALID_LEVELS:
        errors.append(f"[{slug}] Недопустимый уровень: {level}")

    category = record.get("category")
    if category not in VALID_CATEGORIES:
        errors.append(f"[{slug}] Недопустимая категория: {category}")

    # Source Type
    source_type = record.get("source_type")
    if source_type not in VALID_SOURCE_TYPES:
        errors.append(f"[{slug}] Недопустимый source_type: {source_type}")
    
    source_note = record.get("source_note")
    if source_type == "original" and source_note is not None:
        errors.append(f"[{slug}] Для source_type='original' поле source_note обязано быть null")

    # Body HTML & Evidence
    body_html = record.get("body_html", "")
    if not body_html:
        errors.append(f"[{slug}] Пустое поле body_html")

    # Ruby checks
    errors.extend(validate_ruby_tags(body_html, slug))

    # Character count checks
    pure_len = len(strip_html_tags(body_html))
    if pure_len < 50:
        errors.append(f"[{slug}] Текст слишком короткий ({pure_len} символов)")

    # Translation
    trans = record.get("translation_ru", "")
    if not trans:
        errors.append(f"[{slug}] Отсутствует русский перевод (translation_ru)")

    # Questions validation
    questions = record.get("questions", [])
    if not questions:
        errors.append(f"[{slug}] Список вопросов пуст")

    correct_option_distribution = []

    for q_idx, q in enumerate(questions, start=1):
        q_slug = q.get("slug", f"{slug}-q{q_idx}")
        if q_slug in all_slugs:
            errors.append(f"[{slug}] Дубликат question slug: '{q_slug}'")
        all_slugs.add(q_slug)

        q_type = q.get("type")
        if q_type not in VALID_QUESTION_TYPES:
            errors.append(f"[{q_slug}] Недопустимый тип вопроса: {q_type}")

        prompt = q.get("prompt", "")
        if not prompt:
            errors.append(f"[{q_slug}] Пустой текст вопроса (prompt)")

        # Evidence span
        ev_id = q.get("evidence_span_id")
        if not ev_id:
            errors.append(f"[{q_slug}] Отсутствует evidence_span_id")
        else:
            # Check if ev_id exists in body_html
            has_id = f'id="{ev_id}"' in body_html or f"id='{ev_id}'" in body_html
            has_data = f'data-evidence="{ev_id}"' in body_html or f"data-evidence='{ev_id}'" in body_html
            if not (has_id or has_data):
                errors.append(f"[{q_slug}] evidence_span_id '{ev_id}' не найден в body_html!")

        # Options check
        options = q.get("options", [])
        if len(options) != 4:
            errors.append(f"[{q_slug}] Должно быть ровно 4 варианта ответа, получено: {len(options)}")

        correct_count = 0
        for opt in options:
            opt_num = opt.get("option_number")
            opt_text = opt.get("text", "")
            is_corr = opt.get("is_correct", False)
            trap = opt.get("trap_type")
            exp = opt.get("explanation_ru", "")

            if not opt_text:
                errors.append(f"[{q_slug}] Пустой текст варианта #{opt_num}")

            if not exp:
                errors.append(f"[{q_slug}] Отсутствует объяснение для варианта #{opt_num}")

            if is_corr:
                correct_count += 1
                correct_option_distribution.append(opt_num)
                if trap is not None:
                    errors.append(f"[{q_slug}] Для верного варианта #{opt_num} trap_type обязан быть null")
            else:
                if not trap or trap not in VALID_TRAP_TYPES:
                    errors.append(f"[{q_slug}] Неверный вариант #{opt_num} имеет недопустимый trap_type: '{trap}'")

        if correct_count != 1:
            errors.append(f"[{q_slug}] Вопрос должен иметь ровно 1 правильный ответ, найдено: {correct_count}")

    return errors

def validate_all_content(check_inventory_targets: bool = False) -> Tuple[bool, Dict[str, Any]]:
    """Проверяет все JSON файлы в директории content/."""
    all_slugs = set()
    total_errors = []
    stats = {}

    if not CONTENT_DIR.exists():
        print(f"Директория {CONTENT_DIR} не найдена.")
        return False, {}

    json_files = sorted(list(CONTENT_DIR.glob("*.json")))
    if not json_files:
        print(f"В директории {CONTENT_DIR} нет файлов JSON.")
        return False, {}

    for jpath in json_files:
        file_name = jpath.name
        try:
            with open(jpath, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            total_errors.append(f"[{file_name}] Ошибка парсинга JSON: {e}")
            continue

        if not isinstance(data, list):
            total_errors.append(f"[{file_name}] Корневой элемент должен быть списком объектов")
            continue

        file_stats = {
            "total_texts": len(data),
            "by_level_cat": {},
            "total_questions": 0
        }

        for rec in data:
            rec_errors = validate_text_record(rec, file_name, all_slugs)
            total_errors.extend(rec_errors)

            lvl = rec.get("level", "UNKNOWN")
            cat = rec.get("category", "UNKNOWN")
            key = f"{lvl}_{cat}"
            if key not in file_stats["by_level_cat"]:
                file_stats["by_level_cat"][key] = {"texts": 0, "questions": 0}
            file_stats["by_level_cat"][key]["texts"] += 1

            q_len = len(rec.get("questions", []))
            file_stats["by_level_cat"][key]["questions"] += q_len
            file_stats["total_questions"] += q_len

        stats[file_name] = file_stats

    # Check inventory targets if requested
    if check_inventory_targets:
        for lvl, cats in EXPECTED_INVENTORY.items():
            for cat, targets in cats.items():
                expected_texts = targets["texts"]
                expected_qs = targets["questions"]
                
                # Sum across all files
                actual_texts = 0
                actual_qs = 0
                for f_stats in stats.values():
                    key = f"{lvl}_{cat}"
                    if key in f_stats["by_level_cat"]:
                        actual_texts += f_stats["by_level_cat"][key]["texts"]
                        actual_qs += f_stats["by_level_cat"][key]["questions"]

                if actual_texts != expected_texts or actual_qs != expected_qs:
                    total_errors.append(
                        f"Несоответствие инвентаризации [{lvl} {cat}]: "
                        f"ожидалось текстов={expected_texts}, вопросов={expected_qs}; "
                        f"найдено текстов={actual_texts}, вопросов={actual_qs}"
                    )

    is_valid = (len(total_errors) == 0)
    return is_valid, {"errors": total_errors, "stats": stats}

def main():
    check_targets = "--check-targets" in sys.argv
    is_valid, result = validate_all_content(check_inventory_targets=check_targets)

    print("==================================================")
    print("      JLPT DOKKAI CONTENT VALIDATION REPORT       ")
    print("==================================================")

    for fname, fstat in result.get("stats", {}).items():
        print(f"\nФайл: {fname}")
        print(f"  Всего текстов: {fstat['total_texts']}, Всего вопросов: {fstat['total_questions']}")
        for k, v in fstat["by_level_cat"].items():
            print(f"    - {k}: {v['texts']} текстов, {v['questions']} вопросов")

    errors = result.get("errors", [])
    if errors:
        print(f"\n\033[31mОБНАРУЖЕНО ОШИБОК: {len(errors)}\033[0m")
        for err in errors[:20]:
            print(f"  • {err}")
        if len(errors) > 20:
            print(f"  ... и ещё {len(errors) - 20} ошибок")
        sys.exit(1)
    else:
        print(f"\n\033[32m✓ ВСЕ ПРОВЕРКИ УСПЕШНО ПРОЙДЕНЫ!\033[0m")
        sys.exit(0)

if __name__ == "__main__":
    main()

