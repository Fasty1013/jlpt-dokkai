#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Idempotent Content Loader for JLPT Dokkai Master.
Loads content from content/*.json into SQLite database.
- Safely handles N3, N2, N1 replacement while preserving N5 and N4.
- Verifies database backup before any destructive operations.
- Performs idempotent upsert using stable slugs.
"""

import os
import sys
import json
import shutil
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "dokkai.db"
BACKUP_PATH = BASE_DIR / "dokkai.db.bak"
CONTENT_DIR = BASE_DIR / "content"

from database import SessionLocal, engine, Base
import models
from models import Text, Question, Option
from validate_content import validate_all_content

def backup_database():
    """Создает резервную копию базы данных перед выполнением миграций."""
    if DB_PATH.exists():
        shutil.copy2(DB_PATH, BACKUP_PATH)
        size_bytes = os.path.getsize(BACKUP_PATH)
        print(f"✓ Резервная копия БД создана: {BACKUP_PATH.name} ({size_bytes} байт)")
    else:
        print(f"! База данных {DB_PATH.name} пока не существует. Создание новой.")

def load_content(force_replace_n3_n1: bool = True):
    """
    Загружает контент из content/n3.json, content/n2.json, content/n1.json.
    N5 и N4 сохраняются без изменений.
    """
    print("\n--- [Запуск валидатора контента перед импортом] ---")
    is_valid, report = validate_all_content(check_inventory_targets=True)
    if not is_valid:
        print("\033[31mОШИБКА: Контент не прошел предварительную валидацию!\033[0m")
        for err in report.get("errors", []):
            print(f"  • {err}")
        sys.exit(1)
    print("\033[32m✓ Контент проверен и готов к импорту.\033[0m\n")

    backup_database()

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        if force_replace_n3_n1:
            print("Удаление устаревших текстов уровней N3, N2, N1 (каскадное удаление зависимостей)...")
            deleted_q = db.query(Text).filter(Text.level.in_(["N3", "N2", "N1"])).delete(synchronize_session="fetch")
            db.commit()
            print(f"✓ Удалено устаревших текстов N3-N1: {deleted_q}")

        # Проверяем сохранность N5 и N4
        n5_count = db.query(Text).filter(Text.level == "N5").count()
        n4_count = db.query(Text).filter(Text.level == "N4").count()
        print(f"✓ Проверка сохранности: текстов N5 в базе: {n5_count}, N4 в базе: {n4_count}")

        # Загружаем файлы JSON
        json_files = ["n3.json", "n2.json", "n1.json"]
        total_texts_loaded = 0
        total_questions_loaded = 0

        for jname in json_files:
            jpath = CONTENT_DIR / jname
            if not jpath.exists():
                print(f"Файл {jpath} не найден, пропускаем.")
                continue

            with open(jpath, "r", encoding="utf-8") as f:
                records = json.load(f)

            print(f"\nЗагрузка {jname} ({len(records)} текстов)...")

            for rec in records:
                slug = rec["slug"]
                level = rec["level"]
                category = rec["category"]
                title = rec["title"]
                source_note = rec.get("source_note")
                is_nhk = (rec.get("source_type") == "news_adapted") or ("NHK" in title)
                rec_time = rec.get("recommended_time_min", 4)
                body_html = rec["body_html"]
                trans = rec["translation_ru"]
                vocab = rec.get("vocabulary", [])

                # Upsert Text
                text_obj = db.query(Text).filter(Text.slug == slug).first()
                if not text_obj:
                    text_obj = Text(
                        slug=slug,
                        title=title,
                        level=level,
                        category=category,
                        source_exam=source_note or f"JLPT {level} 精選教材",
                        is_nhk=is_nhk,
                        recommended_time_min=rec_time,
                        content_html=body_html,
                        translation_ru=trans,
                        vocabulary_json=vocab
                    )
                    db.add(text_obj)
                    db.flush()  # получаем text_obj.id
                else:
                    text_obj.title = title
                    text_obj.level = level
                    text_obj.category = category
                    text_obj.source_exam = source_note or text_obj.source_exam
                    text_obj.is_nhk = is_nhk
                    text_obj.recommended_time_min = rec_time
                    text_obj.content_html = body_html
                    text_obj.translation_ru = trans
                    text_obj.vocabulary_json = vocab
                    # Удаляем старые вопросы для перезаписи
                    db.query(Question).filter(Question.text_id == text_obj.id).delete()
                    db.flush()

                # Добавляем вопросы и опции
                for q_data in rec.get("questions", []):
                    q_num = q_data["question_number"]
                    q_text = q_data["prompt"]
                    gen_exp = q_data.get("general_explanation", "")
                    ev_id = q_data.get("evidence_span_id")

                    q_obj = Question(
                        text_id=text_obj.id,
                        question_number=q_num,
                        question_text=q_text,
                        general_explanation=gen_exp,
                        evidence_span_id=ev_id
                    )
                    db.add(q_obj)
                    db.flush()

                    for opt_data in q_data.get("options", []):
                        opt_obj = Option(
                            question_id=q_obj.id,
                            option_number=opt_data["option_number"],
                            option_text=opt_data["text"],
                            is_correct=opt_data["is_correct"],
                            trap_type=opt_data.get("trap_type"),
                            option_explanation=opt_data["explanation_ru"]
                        )
                        db.add(opt_obj)

                    total_questions_loaded += 1

                total_texts_loaded += 1

            db.commit()

        print(f"\n\033[32m✓ ИМПОРТ ЗАВЕРШЕН УСПЕШНО!\033[0m")
        print(f"  Всего импортировано текстов N3-N1: {total_texts_loaded}")
        print(f"  Всего импортировано вопросов: {total_questions_loaded}")

        # Финальная статистика в БД
        total_in_db = db.query(Text).count()
        print(f"  Всего текстов в базе данных (N5-N1): {total_in_db}")

    except Exception as e:
        db.rollback()
        print(f"\033[31mОшибка при загрузке данных: {e}\033[0m")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    load_content(force_replace_n3_n1=True)
