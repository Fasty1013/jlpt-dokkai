#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Staging Review and Publication Workflow for PDF Imports.
Provides CLI interface to inspect, approve, edit, or reject imported drafts
before they are validated and published into the main application.
"""

import sys
import json
from pathlib import Path
from typing import List, Dict, Any, Optional

BASE_DIR = Path(__file__).resolve().parent.parent.parent
STAGING_DIR = BASE_DIR / "content" / "staging"
STAGING_DIR.mkdir(parents=True, exist_ok=True)

from database import SessionLocal
from models import Text, Question, Option
from validate_content import validate_text_record

def list_staging_drafts() -> List[Dict[str, Any]]:
    drafts = []
    for f in sorted(STAGING_DIR.glob("*.json")):
        try:
            with open(f, "r", encoding="utf-8") as fp:
                data = json.load(fp)
                drafts.append(data)
        except Exception:
            pass
    return drafts

def display_draft(draft: Dict[str, Any]):
    print("\n" + "=" * 65)
    print(f" ЧЕРНОВИК: {draft.get('slug')} | Уровень: {draft.get('level')} | Категория: {draft.get('category')}")
    print(f" Заголовок: {draft.get('title')}")
    print(f" Уверенность: {draft.get('confidence', 0.0):.0%} | Требует ревью: {draft.get('needs_review')}")
    if draft.get("level_warning"):
        print(f" \033[33mПредупреждение по уровню: {draft.get('level_warning')}\033[0m")
    if draft.get("needs_manual_review"):
        print(f" Замечания системы: {', '.join(draft.get('needs_manual_review'))}")
    print("=" * 65)

    print("\n--- [ТЕКСТ ДЛЯ ЧТЕНИЯ] ---")
    body = draft.get("body_html", "").replace("<ruby>", "").replace("</ruby>", "").replace("<rt>", "[").replace("</rt>", "]")
    print(body[:400] + ("..." if len(body) > 400 else ""))

    print("\n--- [ВОПРОСЫ И ВАРИАНТЫ] ---")
    for q in draft.get("questions", []):
        matched_str = "✓ Ключ сопоставлен" if q.get("answer_matched") else "✗ Ответ в ключе не найден"
        print(f"\nВопрос №{q['question_number']}: {q['prompt']} ({matched_str})")
        for opt in q.get("options", []):
            mark = "[✓]" if opt.get("is_correct") else "[ ]"
            print(f"  {mark} {opt['option_number']}. {opt['text']}")

    print("\n" + "-" * 65)

def publish_draft(slug: str) -> bool:
    """
    Публикует черновик в базу данных Dokkai Master после строгой валидации.
    """
    stage_file = STAGING_DIR / f"{slug}.json"
    if not stage_file.exists():
        print(f"\033[31mЧерновик {slug} не найден в staging.\033[0m")
        return False

    with open(stage_file, "r", encoding="utf-8") as f:
        draft = json.load(f)

    # 1. Валидация через существующий валидатор
    errors = validate_text_record(draft, stage_file.name, set())
    if errors:
        print(f"\033[31mОшибка валидации черновика перед публикацией:\033[0m")
        for err in errors:
            print(f"  • {err}")
        return False

    # 2. Сохранение в БД
    db = SessionLocal()
    try:
        # Проверяем, существует ли уже
        existing = db.query(Text).filter(Text.slug == slug).first()
        if existing:
            db.query(Question).filter(Question.text_id == existing.id).delete()
            text_obj = existing
            text_obj.title = draft["title"]
            text_obj.level = draft["level"]
            text_obj.category = draft["category"]
            text_obj.source_exam = draft.get("source_note")
            text_obj.content_html = draft["body_html"]
            text_obj.translation_ru = draft.get("translation_ru", "")
        else:
            text_obj = Text(
                slug=slug,
                title=draft["title"],
                level=draft["level"],
                category=draft["category"],
                source_exam=draft.get("source_note"),
                is_nhk=False,
                recommended_time_min=draft.get("recommended_time_min", 4),
                content_html=draft["body_html"],
                translation_ru=draft.get("translation_ru", ""),
                vocabulary_json=draft.get("vocabulary", [])
            )
            db.add(text_obj)
            db.flush()

        for q in draft.get("questions", []):
            q_obj = Question(
                text_id=text_obj.id,
                question_number=q["question_number"],
                question_text=q["prompt"],
                general_explanation=q.get("general_explanation", ""),
                evidence_span_id=q.get("evidence_span_id")
            )
            db.add(q_obj)
            db.flush()

            for opt in q.get("options", []):
                opt_obj = Option(
                    question_id=q_obj.id,
                    option_number=opt["option_number"],
                    option_text=opt["text"],
                    is_correct=opt.get("is_correct", False),
                    trap_type=opt.get("trap_type"),
                    option_explanation=opt.get("explanation_ru", "")
                )
                db.add(opt_obj)

        db.commit()
        # Удаляем черновик из staging после успешной публикации
        stage_file.unlink()
        print(f"\033[32m✓ Материал '{draft['title']}' ({slug}) успешно опубликован в тренажёр!\033[0m")
        return True
    except Exception as e:
        db.rollback()
        print(f"\033[31mОшибка публикации в БД: {e}\033[0m")
        return False
    finally:
        db.close()

def reject_draft(slug: str) -> bool:
    stage_file = STAGING_DIR / f"{slug}.json"
    if stage_file.exists():
        stage_file.unlink()
        print(f"Черновик {slug} отклонен и удален из staging.")
        return True
    print(f"Черновик {slug} не найден.")
    return False

