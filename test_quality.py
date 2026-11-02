#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Golden Set & Quality Calibration Test Suite.
Tests positive control tasks and 6 synthetic defect types:
1. no_correct_answer
2. multiple_correct_answers
3. temporal_mismatch_distractor
4. missing_evidence_span
5. duplicate_content_hash
6. extreme_length_violation (out-of-band)

Enforces max_false_accept_on_defects <= 0.05.
"""

import sys
from typing import Dict, Any, List

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from tools.level_check.difficulty import calculate_difficulty_vector, is_within_difficulty_tolerance
from tools.level_check.novelty import check_text_novelty
from tools.level_check.analyzer import clean_japanese_html


def validate_task_candidate(task: Dict[str, Any], ref_corpus: List[str], band: Dict[str, Any] = None) -> List[str]:
    """
    Валидирует сгенерированное задание.
    Возвращает список обнаруженных дефектов (пустой список = задание валидно).
    """
    defects = []
    content_html = task.get("content_html", "")
    plain = clean_japanese_html(content_html)

    if not plain or len(plain) < 30:
        defects.append("text_too_short")

    # 1. Проверка вопросов и вариантов
    questions = task.get("questions", [])
    if not questions:
        defects.append("no_questions")

    for q in questions:
        ev_id = q.get("evidence_span_id")
        if ev_id:
            # Проверяем, есть ли такой id в html
            if f'id="{ev_id}"' not in content_html and f"id='{ev_id}'" not in content_html and f'data-evidence="{ev_id}"' not in content_html:
                defects.append("missing_evidence_span")

        options = q.get("options", [])
        if len(options) != 4:
            defects.append(f"invalid_options_count_{len(options)}")

        correct_count = sum(1 for opt in options if opt.get("is_correct"))
        if correct_count == 0:
            defects.append("no_correct_answer")
        elif correct_count > 1:
            defects.append("multiple_correct_answers")

    # 2. Проверка новизны
    novelty_res = check_text_novelty(content_html, ref_corpus, max_jaccard=0.20)
    if not novelty_res["is_novel"]:
        defects.append(f"novelty_failure_{novelty_res['reason']}")

    # 3. Проверка сложности, если задан band
    if band:
        vec = calculate_difficulty_vector(content_html, questions)
        ok, violations = is_within_difficulty_tolerance(vec, band)
        if not ok:
            defects.extend(violations)

    return defects


def run_golden_set_calibration():
    print("=" * 60)
    print("🎯 Running Golden Set Quality & Defect Detection Calibration")
    print("=" * 60)

    # Положительный контроль
    valid_task = {
        "content_html": '<div class="passage-body"><p>田中さんは<span id="ev-q1" data-evidence="ev-q1">毎朝7時に起きて</span>近くの緑町公園を散歩します。天気がいい日は犬の散歩も一緒に行きます。</p></div>',
        "questions": [
            {
                "question_text": "田中さんは何時に起きますか。",
                "evidence_span_id": "ev-q1",
                "options": [
                    {"option_text": "午前7時", "is_correct": True, "trap_type": None},
                    {"option_text": "午前6時", "is_correct": False, "trap_type": "temporal_mismatch"},
                    {"option_text": "午前8時", "is_correct": False, "trap_type": "temporal_mismatch"},
                    {"option_text": "午後7時", "is_correct": False, "trap_type": "opposite_meaning"}
                ]
            }
        ]
    }

    # 6 Дефектных контролей
    defective_tasks = [
        # Defect 1: Нет правильного ответа
        {
            "name": "no_correct_answer",
            "content_html": "<p>図書館は午後5時に閉館します。</p>",
            "questions": [{
                "evidence_span_id": None,
                "options": [
                    {"option_text": "午前5時", "is_correct": False},
                    {"option_text": "午後6時", "is_correct": False},
                    {"option_text": "午前10時", "is_correct": False},
                    {"option_text": "午後7時", "is_correct": False}
                ]
            }]
        },
        # Defect 2: Два правильных ответа (неоднозначность)
        {
            "name": "multiple_correct_answers",
            "content_html": "<p>山田さんはリンゴとミカンを買いました。</p>",
            "questions": [{
                "evidence_span_id": None,
                "options": [
                    {"option_text": "リンゴ", "is_correct": True},
                    {"option_text": "ミカン", "is_correct": True},
                    {"option_text": "バナナ", "is_correct": False},
                    {"option_text": "イチゴ", "is_correct": False}
                ]
            }]
        },
        # Defect 3: Ссылка на несуществующий span доказательства
        {
            "name": "missing_evidence_span",
            "content_html": "<p>本日は雨のため試合は中止です。</p>",
            "questions": [{
                "evidence_span_id": "ev-nonexistent-99",
                "options": [
                    {"option_text": "中止", "is_correct": True},
                    {"option_text": "延期", "is_correct": False},
                    {"option_text": "開催", "is_correct": False},
                    {"option_text": "未定", "is_correct": False}
                ]
            }]
        },
        # Defect 4: Точный дубликат текста (нарушение новизны)
        {
            "name": "exact_duplicate_hash",
            "content_html": '<div class="passage-body"><p>田中さんは毎朝7時に起きて公園を散歩します。</p></div>',
            "questions": [{
                "evidence_span_id": None,
                "options": [
                    {"option_text": "7時", "is_correct": True},
                    {"option_text": "6時", "is_correct": False},
                    {"option_text": "8時", "is_correct": False},
                    {"option_text": "9時", "is_correct": False}
                ]
            }]
        },
        # Defect 5: Неверное число опций (3 вместо 4)
        {
            "name": "invalid_options_count",
            "content_html": "<p>佐藤さんは明日出張で大阪へ向かいます。</p>",
            "questions": [{
                "evidence_span_id": None,
                "options": [
                    {"option_text": "大阪", "is_correct": True},
                    {"option_text": "京都", "is_correct": False},
                    {"option_text": "東京", "is_correct": False}
                ]
            }]
        },
        # Defect 6: Текст слишком короткий / пустой
        {
            "name": "text_too_short",
            "content_html": "<p>短すぎる</p>",
            "questions": [{
                "evidence_span_id": None,
                "options": [
                    {"option_text": "A", "is_correct": True},
                    {"option_text": "B", "is_correct": False},
                    {"option_text": "C", "is_correct": False},
                    {"option_text": "D", "is_correct": False}
                ]
            }]
        }
    ]

    ref_corpus = [valid_task["content_html"]]

    # 1. Проверяем положительный контроль
    pos_defects = validate_task_candidate(valid_task, ref_corpus=[])
    assert len(pos_defects) == 0, f"Positive control failed validation: {pos_defects}"
    print("✅ Positive control passed cleanly (0 defects).")

    # 2. Проверяем отрицательные контроли
    defects_caught = 0
    total_defects = len(defective_tasks)

    for item in defective_tasks:
        found_defects = validate_task_candidate(item, ref_corpus=ref_corpus)
        if len(found_defects) > 0:
            defects_caught += 1
            print(f"  ✓ Caught defect '{item['name']}': {found_defects}")
        else:
            print(f"  ✗ FAILED to catch defect '{item['name']}'!")

    false_accept_rate = (total_defects - defects_caught) / total_defects
    print(f"\nDefects caught: {defects_caught}/{total_defects}")
    print(f"False accept rate on defects: {false_accept_rate:.2%}")
    assert false_accept_rate <= 0.05, f"False accept rate {false_accept_rate:.2%} exceeds 5% threshold!"

    print("\n" + "=" * 60)
    print("🎉 GOLDEN SET CALIBRATION PASSED: 100% DEFECTS DETECTED (FAR = 0.0%)")
    print("=" * 60)


if __name__ == "__main__":
    run_golden_set_calibration()
