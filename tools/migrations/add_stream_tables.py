#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Idempotent Database Migration: Stream Tables, User States, Slots & Profile Keys.
Ensures zero data loss, safe rollback capability, and idempotent schema upgrades.
"""

import sys
import os
import re
import json
import hashlib
import shutil
from pathlib import Path
from collections import Counter

# Set project root in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
os.chdir(PROJECT_ROOT)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from database import engine, Base, SessionLocal
from models import Text, Question, Option, TaskSlot, UserTextState, Attempt, GenerationJob

BACKUP_PATH = PROJECT_ROOT / "dokkai.db.pre_stream_backup"


def clean_text_for_hash(html: str) -> str:
    """Нормализует японский текст для дедупликации и хэширования."""
    t = re.sub(r'<rt>.*?</rt>', '', html or '', flags=re.DOTALL)
    t = re.sub(r'<[^>]+>', '', t)
    t = t.replace('&nbsp;', ' ').replace('&quot;', '"').replace('&amp;', '&')
    return re.sub(r'\s+', '', t)


def determine_length_band(char_len: int) -> str:
    if char_len < 120:
        return "XS"
    elif char_len < 250:
        return "S"
    elif char_len <= 450:
        return "M"
    elif char_len <= 700:
        return "L"
    return "XL"


def migrate():
    print("=" * 65)
    print("► Запуск миграции схемы базы данных (Stream & Slots)...")
    print("=" * 65)

    # 1. Проверяем наличие бэкапа
    db_file = PROJECT_ROOT / "dokkai.db"
    if db_file.exists() and not BACKUP_PATH.exists():
        shutil.copy2(db_file, BACKUP_PATH)
        print(f"✓ Создана резервная копия: {BACKUP_PATH.name}")
    else:
        print(f"✓ Резервная копия уже существует: {BACKUP_PATH.name}")

    # 2. Добавляем недостающие колонки в texts через ALTER TABLE (кроссплатформенно)
    from sqlalchemy import inspect
    inspector = inspect(engine)
    if "texts" in inspector.get_table_names():
        existing_cols = {col["name"] for col in inspector.get_columns("texts")}

        new_columns = [
            ("origin", "VARCHAR(30) DEFAULT 'archive'"),
            ("verification_status", "VARCHAR(30) DEFAULT 'expert_reviewed'"),
            ("profile_key", "VARCHAR(80)"),
            ("topic_tags", "JSON DEFAULT '[]'"),
            ("content_hash", "VARCHAR(64)"),
            ("difficulty_vector", "JSON DEFAULT '{}'"),
            ("novelty_report", "JSON DEFAULT '{}'"),
            ("report_count", "INTEGER DEFAULT 0"),
            ("is_active", "BOOLEAN DEFAULT TRUE")
        ]

        with engine.connect() as conn:
            for col_name, col_def in new_columns:
                if col_name not in existing_cols:
                    print(f"  + Добавление колонки texts.{col_name}...")
                    conn.exec_driver_sql(f"ALTER TABLE texts ADD COLUMN {col_name} {col_def}")
                    conn.commit()

    # 3. Создаем новые таблицы
    Base.metadata.create_all(bind=engine)
    print("✓ Созданы/проверены таблицы task_slots, user_text_states, attempts, generation_jobs")

    # 4. Бэкфилл данных существующих текстов
    db = SessionLocal()
    try:
        texts = db.query(Text).all()
        print(f"► Бэкфилл атрибутов сложности и профилей для {len(texts)} текстов...")

        # Загрузка метаданных вопросов из content JSONs
        slug_meta = {}
        for jf in PROJECT_ROOT.glob("content/n*.json"):
            try:
                with open(jf, "r", encoding="utf-8") as fp:
                    for r in json.load(fp):
                        slug_meta[r.get("slug")] = {
                            "q_types": [q.get("type", "detail") for q in r.get("questions", [])],
                            "topic_tags": r.get("topic_tags", [])
                        }
            except Exception:
                pass

        updated_count = 0
        for t in texts:
            clean_str = clean_text_for_hash(t.content_html)
            chash = hashlib.sha256(clean_str.encode("utf-8")).hexdigest()
            t.content_hash = chash

            qs = t.questions
            nq = len(qs)
            meta = slug_meta.get(t.slug, {})
            q_types = meta.get("q_types", [])
            if q_types:
                primary_type = Counter(q_types).most_common(1)[0][0]
            else:
                primary_type = "info_search" if t.category == "info_search" else ("claim" if t.category in ["short", "article"] else "detail")

            lband = determine_length_band(len(clean_str))
            prof_key = f"{t.level.upper()}:{t.category}:{primary_type}:{nq}:{lband}"
            t.profile_key = prof_key

            if not t.origin:
                t.origin = "archive"
            if not t.verification_status:
                t.verification_status = "expert_reviewed"
            if t.is_active is None:
                t.is_active = True
            if not t.topic_tags:
                t.topic_tags = meta.get("topic_tags", [t.category])

            # Базовый вектор сложности
            sentences = [s for s in re.split(r'[。！？\n]', clean_str) if s.strip()]
            num_sentences = max(1, len(sentences))
            kanji_chars = len(re.findall(r'[\u4e00-\u9fff]', clean_str))
            kanji_ratio = round(kanji_chars / max(1, len(clean_str)), 3)

            traps_count = len({opt.trap_type for q in qs for opt in q.options if opt.trap_type})

            t.difficulty_vector = {
                "char_count": len(clean_str),
                "sentence_count": num_sentences,
                "avg_sentence_len": round(len(clean_str) / num_sentences, 1),
                "max_sentence_len": max((len(s) for s in sentences), default=0),
                "kanji_ratio": kanji_ratio,
                "num_questions": nq,
                "distinct_traps": traps_count
            }

            updated_count += 1

        db.commit()
        print(f"✓ Успешно обновлено и откалибровано записей: {updated_count}")

    except Exception as e:
        db.rollback()
        print(f"✗ Ошибка при бэкфилле: {e}")
        raise
    finally:
        db.close()

    print("=" * 65)
    print("✓ Миграция завершена успешно и идемпотентно!")
    print("=" * 65)


def rollback():
    """Откат к состоянию до миграции."""
    db_file = PROJECT_ROOT / "dokkai.db"
    if BACKUP_PATH.exists():
        shutil.copy2(BACKUP_PATH, db_file)
        print(f"✓ База данных dokkai.db восстановлена из {BACKUP_PATH.name}")
    else:
        print("✗ Файл бэкапа не найден для отката.")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--rollback":
        rollback()
    else:
        migrate()

