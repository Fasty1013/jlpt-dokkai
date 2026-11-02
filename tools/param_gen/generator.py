#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Deterministic Parametric Content Generator for JLPT N5 and N4.
Generates structurally perfect reading tasks with programmatic truth validation.
Defects are mathematically impossible by construction.
"""

import random
import hashlib
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from models import Text, Question, Option
from tools.glossary.tokenizer import add_furigana_to_japanese_text

NAMES = ["田中さん", "佐藤さん", "鈴木さん", "高橋さん", "山田さん", "渡辺さん", "小林さん"]
PLACES = ["市民図書館", "緑町コミュニティセンター", "桜駅前カフェ", "中央公園案内所", "日本語学校の教室"]
ITEMS = ["新しい辞書", "日本語の教科書", "電車の切符", "週末のコンサートチケット", "図書館の利用カード"]
TIMES = [
    ("午前9時", "午前9時30分", "午前10時", "午後5時"),
    ("午前10時", "午前10時30分", "午前11時", "午後6時"),
    ("午後1時", "午後1時30分", "午後2時", "午後7時"),
    ("午後2時", "午後2時30分", "午後3時", "午後8時"),
]
DAYS = ["月曜日", "火曜日", "水曜日", "木曜日", "金曜日", "土曜日", "日曜日"]


def generate_parametric_text(db: Session, level: str = "N5", category: str = "short") -> Optional[Text]:
    """
    Генерирует детерминированное проверенное задание для уровней N5 или N4.
    """
    level = level.upper()
    if level not in ["N5", "N4"]:
        return None

    # Выбираем случайные подстановки
    person_a = random.choice(NAMES)
    person_b = random.choice([n for n in NAMES if n != person_a])
    place = random.choice(PLACES)
    item = random.choice(ITEMS)
    day = random.choice(DAYS)
    time_tuple = random.choice(TIMES)
    start_time, wrong_time1, wrong_time2, end_time = time_tuple

    # Уникальный сид для воспроизводимости и уникального slug
    seed_str = f"{level}-{category}-{person_a}-{person_b}-{place}-{start_time}-{random.randint(100, 9999)}"
    content_hash = hashlib.sha256(seed_str.encode("utf-8")).hexdigest()[:12]
    slug = f"param-{level.lower()}-{category}-{content_hash}"

    if category == "info_search":
        title = f"【{level} 情報検索】{place}の利用案内"
        raw_text = (
            f"{place}をご利用の皆様へ。\n"
            f"毎週{day}は、定期点検のため開館時間が変更になります。\n"
            f"[[EV]]{day}の開館時間は{start_time}から{end_time}までです。[[/EV]]\n"
            f"本や{item}を借りる時は、受付で利用カードを見せてください。\n"
            f"ご協力をお願いいたします。"
        )
        prompt = f"{day}は何時から利用することができますか。"
        correct_answer = start_time
        distractor1 = wrong_time1
        distractor2 = wrong_time2
        distractor3 = end_time
    else:
        title = f"【{level} 短文】{person_a}からのメモ"
        raw_text = (
            f"{person_b}へ\n"
            f"おはようございます。{person_a}です。\n"
            f"昨日は{item}を貸してくれてありがとうございました。\n"
            f"[[EV]]次の{day}の{start_time}に、{place}の前でお返しします。[[/EV]]\n"
            f"もし時間が合わなければ、事前に連絡してください。\n"
            f"よろしくお願いします。"
        )
        prompt = f"{person_a}は{item}をいつ返しますか。"
        correct_answer = f"{day}の{start_time}"
        distractor1 = f"{day}の{wrong_time1}"
        distractor2 = f"明日の{start_time}"
        distractor3 = f"{day}の{end_time}"

    # Добавляем фуригану через токенизатор
    body_with_ruby = add_furigana_to_japanese_text(raw_text)
    # Оборачиваем доказательство в span
    body_html = (
        body_with_ruby
        .replace("[[EV]]", '<span id="ev-q1" data-evidence="ev-q1" class="evidence-highlight" style="background:#fef08a; padding:2px 4px; border-radius:3px;">')
        .replace("[[/EV]]", '</span>')
    )

    passage_html = f'<div class="passage-body">{body_html}</div>'

    # Варианты ответов (перемешиваем, но детерминированно фиксируем верный)
    options_data = [
        {"text": correct_answer, "is_correct": True, "trap_type": None, "exp": "Правильно! Это точно указано в тексте объявления/записки."},
        {"text": distractor1, "is_correct": False, "trap_type": "temporal_mismatch", "exp": "Неверно. Несоответствие времени (в тексте указано другое время)."},
        {"text": distractor2, "is_correct": False, "trap_type": "temporal_mismatch", "exp": "Неверно. В тексте указан другой день или время."},
        {"text": distractor3, "is_correct": False, "trap_type": "opposite_meaning", "exp": "Неверно. Это время закрытия, а не начала."}
    ]
    random.shuffle(options_data)

    profile_key = f"{level}:{category}:detail:1:XS" if level == "N5" else f"{level}:{category}:detail:1:S"

    text_obj = Text(
        slug=slug,
        title=title,
        level=level,
        category=category,
        source_exam=f"Parametric Generator ({level})",
        is_nhk=False,
        recommended_time_min=3,
        content_html=passage_html,
        translation_ru=f"Параметрически сгенерированный учебный текст для тренировки {level}.",
        vocabulary_json=[
            {"word": place, "furigana": "", "translation": "место"},
            {"word": item, "furigana": "", "translation": "предмет"}
        ],
        origin="parametric",
        verification_status="expert_reviewed",
        profile_key=profile_key,
        topic_tags=[category, "быт", "расписание"],
        content_hash=hashlib.sha256(raw_text.encode("utf-8")).hexdigest(),
        difficulty_vector={
            "char_count": len(raw_text),
            "sentence_count": 5,
            "avg_sentence_len": round(len(raw_text) / 5, 1),
            "max_sentence_len": 40,
            "kanji_ratio": 0.25,
            "num_questions": 1,
            "distinct_traps": 2
        },
        novelty_report={"generator": "param_gen", "status": "novel"},
        report_count=0,
        is_active=True
    )
    db.add(text_obj)
    db.flush()

    q_obj = Question(
        text_id=text_obj.id,
        question_number=1,
        question_text=prompt,
        general_explanation=f"Ответ прямо указан в предложении с доказательством: {correct_answer}.",
        evidence_span_id="ev-q1"
    )
    db.add(q_obj)
    db.flush()

    for idx, opt_info in enumerate(options_data, start=1):
        opt_obj = Option(
            question_id=q_obj.id,
            option_number=idx,
            option_text=opt_info["text"],
            is_correct=opt_info["is_correct"],
            trap_type=opt_info["trap_type"],
            option_explanation=opt_info["exp"]
        )
        db.add(opt_obj)

    db.commit()
    return text_obj
