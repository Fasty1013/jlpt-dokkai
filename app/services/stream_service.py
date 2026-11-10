#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Stream Service: Slot Management, Task Replacement, and Completion Lifecycle.
Implements atomic transactions, idempotency, Anti-Cheat isolation, and dynamic replenishment.
"""

from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple, Set
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func

from app.models import Text, Question, Option, TaskSlot, UserTextState, Attempt
from tools.param_gen.generator import generate_parametric_text

ACTIVE_SLOTS_PER_PROFILE = 3
DEFAULT_SOLVED_WHEN = "all_questions_answered"  # or "all_correct"
ALL_CORRECT_MAX_ATTEMPTS = 2


def get_default_profile_for_level(level: str, category: str = "short") -> str:
    level = level.upper()
    if level in ["N5", "N4"]:
        return f"{level}:{category}:detail:1:XS" if category == "short" else f"{level}:{category}:detail:2:S"
    return f"{level}:{category}:detail:1:S" if category == "short" else f"{level}:{category}:detail:2:M"


def get_or_create_slots(
    db: Session,
    user_id: str,
    profile_key: str
) -> List[Dict[str, Any]]:
    """
    Возвращает 3 активных слота для данного профиля сложности и пользователя.
    Если слотов меньше 3, атомарно дозаполняет их новыми непройденными заданиями.
    """
    slots = (
        db.query(TaskSlot)
        .options(joinedload(TaskSlot.text).joinedload(Text.questions).joinedload(Question.options))
        .filter(TaskSlot.user_id == user_id, TaskSlot.profile_key == profile_key)
        .order_by(TaskSlot.position.asc())
        .all()
    )

    slot_positions = {s.position: s for s in slots}
    active_text_ids = {s.text_id for s in slots if s.text_id is not None}

    updated = False
    for pos in range(1, ACTIVE_SLOTS_PER_PROFILE + 1):
        if pos not in slot_positions:
            # Подбираем задание
            next_text = pick_next(db, user_id, profile_key, exclude_text_ids=active_text_ids)
            slot = TaskSlot(
                user_id=user_id,
                profile_key=profile_key,
                position=pos,
                text_id=next_text.id if next_text else None,
                state="active" if next_text else "placeholder",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(slot)
            if next_text:
                active_text_ids.add(next_text.id)
            updated = True
        elif slot_positions[pos].text_id is None and slot_positions[pos].state == "active":
            # Слот пуст, но помечен активным - пробуем пополнить
            next_text = pick_next(db, user_id, profile_key, exclude_text_ids=active_text_ids)
            if next_text:
                slot_positions[pos].text_id = next_text.id
                slot_positions[pos].state = "active"
                active_text_ids.add(next_text.id)
                updated = True
            else:
                slot_positions[pos].state = "placeholder"
                updated = True

    if updated:
        db.commit()
        # Перезагружаем слоты со связанными объектами
        slots = (
            db.query(TaskSlot)
            .options(joinedload(TaskSlot.text).joinedload(Text.questions).joinedload(Question.options))
            .filter(TaskSlot.user_id == user_id, TaskSlot.profile_key == profile_key)
            .order_by(TaskSlot.position.asc())
            .all()
        )

    # Сериализация с Anti-Cheat защитой (до сдачи правильные ответы скрыты)
    serialized_slots = []
    for s in slots:
        slot_data = {
            "id": s.id,
            "position": s.position,
            "profile_key": s.profile_key,
            "state": s.state,
            "updated_at": s.updated_at.isoformat() if s.updated_at else None,
            "text": None
        }

        if s.text and s.state != "placeholder":
            slot_data["text"] = {
                "id": s.text.id,
                "slug": s.text.slug,
                "title": s.text.title,
                "level": s.text.level,
                "category": s.text.category,
                "recommended_time_min": s.text.recommended_time_min,
                "content_html": s.text.content_html,
                "origin": s.text.origin,
                "verification_status": s.text.verification_status,
                "question_count": len(s.text.questions),
                "questions": [
                    {
                        "id": q.id,
                        "question_number": q.question_number,
                        "question_text": q.question_text,
                        "options": [
                            {
                                "id": opt.id,
                                "option_number": opt.option_number,
                                "option_text": opt.option_text
                                # Anti-Cheat: is_correct, trap_type, explanation НЕ передаются!
                            }
                            for opt in sorted(q.options, key=lambda o: o.option_number)
                        ]
                    }
                    for q in sorted(s.text.questions, key=lambda x: x.question_number)
                ]
            }
        serialized_slots.append(slot_data)

    return serialized_slots


def pick_next(
    db: Session,
    user_id: str,
    profile_key: str,
    exclude_text_ids: Optional[Set[int]] = None
) -> Optional[Text]:
    """
    Серверный подбор следующего задания:
    1. Ищет не виденное пользователем задание из пула (pool_unseen) по profile_key.
    2. Если нет: для N5/N4 генерирует параметрическое задание на лету.
    3. Если нет: возвращает None (слот переходит в placeholder).
    """
    exclude_ids = set(exclude_text_ids or [])

    # Находим уже решенные пользователем тексты
    solved_text_ids = {
        row[0] for row in db.query(UserTextState.text_id)
        .filter(UserTextState.user_id == user_id, UserTextState.status == "solved")
        .all()
    }
    exclude_ids.update(solved_text_ids)

    # Находим тексты, которые уже находятся в активных слотах пользователя
    active_slot_text_ids = {
        row[0] for row in db.query(TaskSlot.text_id)
        .filter(TaskSlot.user_id == user_id, TaskSlot.text_id.isnot(None))
        .all()
    }
    exclude_ids.update(active_slot_text_ids)

    # 1. Поиск в существующем пуле по profile_key
    query = (
        db.query(Text)
        .filter(
            Text.is_active == True,
            Text.profile_key == profile_key
        )
    )
    if exclude_ids:
        query = query.filter(~Text.id.in_(exclude_ids))

    candidate = query.order_by(func.random()).first()
    if candidate:
        return candidate

    # 2. Если точного совпадения по длине band нет, ищем по (level, category)
    parts = profile_key.split(":")
    if len(parts) >= 2:
        lvl, cat = parts[0], parts[1]
        fallback_query = (
            db.query(Text)
            .filter(
                Text.is_active == True,
                Text.level == lvl,
                Text.category == cat
            )
        )
        if exclude_ids:
            fallback_query = fallback_query.filter(~Text.id.in_(exclude_ids))

        fallback_candidate = fallback_query.order_by(func.random()).first()
        if fallback_candidate:
            return fallback_candidate

    # 3. Для уровней N5 и N4 используем детерминированный параметрический генератор
    if profile_key.startswith("N5") or profile_key.startswith("N4"):
        lvl = "N5" if profile_key.startswith("N5") else "N4"
        cat = parts[1] if len(parts) >= 2 else "short"
        param_text = generate_parametric_text(db, level=lvl, category=cat)
        if param_text:
            return param_text

    return None


def complete_task(
    db: Session,
    user_id: str,
    text_id: int,
    answers: List[Dict[str, int]],
    idempotency_key: str,
    mode: str = "first",
    solved_when: str = DEFAULT_SOLVED_WHEN,
    all_correct_max_attempts: int = ALL_CORRECT_MAX_ATTEMPTS
) -> Dict[str, Any]:
    """
    Атомарная фиксация решения задания, расчёт результатов,
    обновление UserTextState и подбор замены в task_slots.
    Защищено уникальным idempotency_key от дублирования при параллельных кликах.
    """
    # 1. Проверка идемпотентности: если попытка с таким ключом уже была, возвращаем сохраненный ответ
    existing_attempt = db.query(Attempt).filter(Attempt.idempotency_key == idempotency_key).first()
    if existing_attempt:
        user_state = (
            db.query(UserTextState)
            .filter(UserTextState.user_id == user_id, UserTextState.text_id == text_id)
            .first()
        )
        if user_state and user_state.status != "solved":
            return {
                "is_solved": False,
                "error_question_ids": user_state.error_question_ids or [],
                "attempts_used": user_state.attempts_count,
                "attempts_max": all_correct_max_attempts,
                "message": "Допущены ошибки в вопросах. Перепроверьте текст."
            }
        return get_solved_task_details(db, user_id, text_id, existing_attempt.score, is_retry=(existing_attempt.mode != "first"))

    text = (
        db.query(Text)
        .options(joinedload(Text.questions).joinedload(Question.options))
        .filter(Text.id == text_id)
        .first()
    )
    if not text:
        raise ValueError("Задание не найдено")

    # 2. Подсчет баллов
    user_answers_map = {ans["question_id"]: ans["selected_option_id"] for ans in answers if "question_id" in ans and "selected_option_id" in ans}
    total_questions = len(text.questions)
    correct_count = 0
    error_question_ids = []

    for q in text.questions:
        selected_opt_id = user_answers_map.get(q.id)
        correct_opt = next((opt for opt in q.options if opt.is_correct), None)
        correct_opt_id = correct_opt.id if correct_opt else -1

        if selected_opt_id is not None and selected_opt_id == correct_opt_id:
            correct_count += 1
        else:
            error_question_ids.append(q.id)

    score_percent = round((correct_count / total_questions * 100), 1) if total_questions > 0 else 0.0
    is_perfect = (score_percent == 100.0)

    # 3. Запись Attempt (с идемпотентным ключом)
    attempt = Attempt(
        user_id=user_id,
        text_id=text_id,
        answers=answers,
        score=score_percent,
        mode=mode,
        idempotency_key=idempotency_key,
        created_at=datetime.utcnow()
    )
    db.add(attempt)

    # 4. Обновление UserTextState
    user_state = (
        db.query(UserTextState)
        .filter(UserTextState.user_id == user_id, UserTextState.text_id == text_id)
        .first()
    )

    if not user_state:
        user_state = UserTextState(
            user_id=user_id,
            text_id=text_id,
            status="in_progress",
            started_at=datetime.utcnow(),
            attempts_count=0,
            best_score=0.0
        )
        db.add(user_state)

    user_state.attempts_count += 1
    user_state.last_score = score_percent
    user_state.best_score = max(user_state.best_score, score_percent)
    user_state.last_answers = answers
    user_state.error_question_ids = error_question_ids

    # 5. Определение перехода в "solved"
    is_solved = False
    if solved_when == "all_questions_answered":
        is_solved = True
    elif solved_when == "all_correct":
        if is_perfect or user_state.attempts_count >= all_correct_max_attempts:
            is_solved = True

    replacement_info = None

    if is_solved:
        user_state.status = "solved"
        user_state.solved_at = datetime.utcnow()
        user_state.perfect = is_perfect

        # Находим слот, где находился этот текст
        slot = (
            db.query(TaskSlot)
            .filter(TaskSlot.user_id == user_id, TaskSlot.text_id == text_id)
            .first()
        )

        if slot:
            # Подбираем замену того же профиля
            next_text = pick_next(db, user_id, slot.profile_key, exclude_text_ids={text_id})
            if next_text:
                slot.text_id = next_text.id
                slot.state = "active"
                slot.updated_at = datetime.utcnow()
                replacement_info = {
                    "position": slot.position,
                    "state": "active",
                    "text": {
                        "id": next_text.id,
                        "slug": next_text.slug,
                        "title": next_text.title,
                        "level": next_text.level,
                        "category": next_text.category,
                        "recommended_time_min": next_text.recommended_time_min,
                        "content_html": next_text.content_html,
                        "origin": next_text.origin,
                        "question_count": len(next_text.questions),
                        "questions": [
                            {
                                "id": q.id,
                                "question_number": q.question_number,
                                "question_text": q.question_text,
                                "options": [
                                    {
                                        "id": opt.id,
                                        "option_number": opt.option_number,
                                        "option_text": opt.option_text
                                    }
                                    for opt in sorted(q.options, key=lambda o: o.option_number)
                                ]
                            }
                            for q in sorted(next_text.questions, key=lambda x: x.question_number)
                        ]
                    }
                }
            else:
                slot.text_id = None
                slot.state = "placeholder"
                slot.updated_at = datetime.utcnow()
                replacement_info = {
                    "position": slot.position,
                    "state": "placeholder",
                    "text": None
                }

    db.commit()

    # Формируем ответ с учётом Anti-Cheat правил
    if not is_solved and solved_when == "all_correct":
        # В режиме "исправь ошибки": отдаются только номера неверных вопросов, БЕЗ правильных ответов!
        return {
            "is_solved": False,
            "status": "needs_correction",
            "score_percent": score_percent,
            "attempts_used": user_state.attempts_count,
            "attempts_max": all_correct_max_attempts,
            "error_question_ids": error_question_ids,
            "replacement": None,
            "message": f"Ошибки в {len(error_question_ids)} вопросах. Попробуйте исправить их (попытка {user_state.attempts_count} из {all_correct_max_attempts})."
        }

    # Если задание завершено (solved): возвращаем полный анализ, ответы и замену
    return get_solved_task_details(
        db, user_id, text_id, score_percent,
        replacement=replacement_info,
        user_answers_map=user_answers_map,
        perfect=user_state.perfect
    )


def get_solved_task_details(
    db: Session,
    user_id: str,
    text_id: int,
    score_percent: float,
    replacement: Optional[Dict[str, Any]] = None,
    user_answers_map: Optional[Dict[int, int]] = None,
    perfect: bool = False,
    is_retry: bool = False
) -> Dict[str, Any]:
    """Возвращает полный аналитический разбор завершённого задания."""
    text = (
        db.query(Text)
        .options(joinedload(Text.questions).joinedload(Question.options))
        .filter(Text.id == text_id)
        .first()
    )

    if user_answers_map is None:
        last_attempt = (
            db.query(Attempt)
            .filter(Attempt.user_id == user_id, Attempt.text_id == text_id)
            .order_by(Attempt.created_at.desc())
            .first()
        )
        if last_attempt and isinstance(last_attempt.answers, list):
            user_answers_map = {ans["question_id"]: ans["selected_option_id"] for ans in last_attempt.answers if "question_id" in ans}
        else:
            user_answers_map = {}

    questions_analysis = []
    correct_count = 0

    for q in sorted(text.questions, key=lambda x: x.question_number):
        selected_opt_id = user_answers_map.get(q.id)
        correct_opt = next((opt for opt in q.options if opt.is_correct), None)
        correct_opt_id = correct_opt.id if correct_opt else -1
        is_user_correct = (selected_opt_id is not None and selected_opt_id == correct_opt_id)
        if is_user_correct:
            correct_count += 1

        options_analysis = []
        for opt in sorted(q.options, key=lambda o: o.option_number):
            options_analysis.append({
                "id": opt.id,
                "option_number": opt.option_number,
                "option_text": opt.option_text,
                "is_correct": opt.is_correct,
                "trap_type": opt.trap_type,
                "option_explanation": opt.option_explanation,
                "was_selected": (selected_opt_id == opt.id)
            })

        questions_analysis.append({
            "id": q.id,
            "question_number": q.question_number,
            "question_text": q.question_text,
            "general_explanation": q.general_explanation,
            "evidence_span_id": q.evidence_span_id,
            "is_user_correct": is_user_correct,
            "selected_option_id": selected_opt_id,
            "correct_option_id": correct_opt_id,
            "options": options_analysis
        })

    return {
        "is_solved": True,
        "is_retry": is_retry,
        "text_id": text.id,
        "title": text.title,
        "level": text.level,
        "category": text.category,
        "score_percent": score_percent,
        "perfect": perfect,
        "total_questions": len(text.questions),
        "correct_count": correct_count,
        "content_html": text.content_html,
        "translation_ru": text.translation_ru,
        "vocabulary": text.vocabulary_json or [],
        "questions": questions_analysis,
        "replacement": replacement
    }


def list_solved_texts(
    db: Session,
    user_id: str,
    level: Optional[str] = None,
    only_perfect: Optional[bool] = None,
    only_errors: Optional[bool] = None,
    page: int = 1,
    page_size: int = 20
) -> Dict[str, Any]:
    """Возвращает список решённых заданий пользователя с пагинацией и фильтрами."""
    query = (
        db.query(UserTextState)
        .options(joinedload(UserTextState.text))
        .filter(UserTextState.user_id == user_id, UserTextState.status == "solved")
    )

    if level:
        query = query.join(Text).filter(Text.level == level.upper())
    if only_perfect is True:
        query = query.filter(UserTextState.perfect == True)
    elif only_errors is True:
        query = query.filter(UserTextState.perfect == False)

    total_count = query.count()
    items = (
        query
        .order_by(UserTextState.solved_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    results = []
    for s in items:
        if not s.text:
            continue
        results.append({
            "text_id": s.text.id,
            "slug": s.text.slug,
            "title": s.text.title,
            "level": s.text.level,
            "category": s.text.category,
            "origin": s.text.origin,
            "perfect": s.perfect,
            "best_score": s.best_score,
            "last_score": s.last_score,
            "attempts_count": s.attempts_count,
            "solved_at": s.solved_at.isoformat() if s.solved_at else None
        })

    return {
        "total": total_count,
        "page": page,
        "page_size": page_size,
        "items": results
    }

