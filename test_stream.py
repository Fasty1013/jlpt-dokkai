#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Automated Test Suite for Two-Column Stream Lifecycle and Anti-Cheat.
Runs directly via `python test_stream.py`.
Tests:
1. 3 Active slots allocation and unseen replacement
2. Anti-Cheat answer isolation on active slots
3. Atomic completion with idempotency key protection
4. Solved archive with filters and pagination
5. Solved detail Anti-Cheat authorization (403 for unsolved)
6. all_questions_answered vs all_correct modes
7. Task defect reporting and auto-deactivation on threshold 3
"""

import sys
import uuid
from fastapi.testclient import TestClient

# Reconfigure stdout for Windows console
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from main import app
from app.core.database import SessionLocal
from app import models

client = TestClient(app)


def run_all_tests():
    db = SessionLocal()
    print("=" * 60)
    print("🚀 Starting Stream Lifecycle & Anti-Cheat Test Suite")
    print("=" * 60)

    try:
        # ---------------------------------------------------------
        # TEST 1: Active Slots Creation & Anti-Cheat Leak Check
        # ---------------------------------------------------------
        print("\n[TEST 1] Testing /api/stream/slots and Anti-Cheat isolation...")
        user_id = f"test-user-{uuid.uuid4().hex[:8]}"
        profile_key = "N5:short:detail:1:XS"

        res = client.get(f"/api/stream/slots?user_id={user_id}&profile_key={profile_key}")
        assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
        data = res.json()

        assert data["profile_key"] == profile_key
        assert data["user_id"] == user_id
        slots = data["slots"]
        assert len(slots) == 3, f"Expected 3 active slots, got {len(slots)}"

        for slot in slots:
            assert slot["position"] in [1, 2, 3]
            if slot["state"] == "active" and slot["text"]:
                text = slot["text"]
                assert "questions" in text
                for q in text["questions"]:
                    assert "evidence_span_id" not in q, "Anti-Cheat Leak: evidence_span_id found in slot question!"
                    assert "general_explanation" not in q, "Anti-Cheat Leak: general_explanation found in slot question!"
                    for opt in q["options"]:
                        assert "is_correct" not in opt, "Anti-Cheat Leak: is_correct found in slot option!"
                        assert "trap_type" not in opt, "Anti-Cheat Leak: trap_type found in slot option!"
                        assert "option_explanation" not in opt, "Anti-Cheat Leak: option_explanation found in slot option!"
        print("✅ [TEST 1 PASSED] 3 slots created, 0 leaks detected.")

        # ---------------------------------------------------------
        # TEST 2: Task Completion, Replacement & Idempotency
        # ---------------------------------------------------------
        print("\n[TEST 2] Testing completion lifecycle, replacement and idempotency...")
        slot1 = slots[0]
        assert slot1["text"] is not None
        target_text_id = slot1["text"]["id"]
        target_q = slot1["text"]["questions"][0]
        selected_opt = target_q["options"][0]["id"]
        idem_key = f"idem-{uuid.uuid4()}"

        payload = {
            "user_id": user_id,
            "text_id": target_text_id,
            "answers": [{"question_id": target_q["id"], "selected_option_id": selected_opt}],
            "idempotency_key": idem_key,
            "mode": "first",
            "solved_when": "all_questions_answered"
        }

        # Первичная сдача
        res_comp = client.post("/api/stream/complete", json=payload)
        assert res_comp.status_code == 200, f"Expected 200, got {res_comp.status_code}: {res_comp.text}"
        comp_data = res_comp.json()
        assert comp_data["is_solved"] is True
        assert "replacement" in comp_data
        replacement = comp_data["replacement"]
        assert replacement is not None
        if replacement["text"]:
            assert replacement["text"]["id"] != target_text_id, "Slot replacement must be a different unseen text!"
        print(f"  - Task {target_text_id} completed, replacement slot position: {replacement['position']}")

        # Проверка идемпотентности
        res_idem = client.post("/api/stream/complete", json=payload)
        assert res_idem.status_code == 200
        idem_data = res_idem.json()
        assert idem_data["text_id"] == target_text_id
        assert idem_data["score_percent"] == comp_data["score_percent"]

        attempts = db.query(models.Attempt).filter(models.Attempt.idempotency_key == idem_key).all()
        assert len(attempts) == 1, f"Expected exactly 1 attempt record for idem_key, got {len(attempts)}"
        print("✅ [TEST 2 PASSED] Atomic completion and idempotency verified.")

        # ---------------------------------------------------------
        # TEST 3: Solved Archive with Filters
        # ---------------------------------------------------------
        print("\n[TEST 3] Testing /api/stream/solved archive...")
        res_solved = client.get(f"/api/stream/solved?user_id={user_id}&level=N5")
        assert res_solved.status_code == 200
        solved_list = res_solved.json()
        assert solved_list["total"] >= 1
        assert any(item["text_id"] == target_text_id for item in solved_list["items"])
        print(f"  - User archive has {solved_list['total']} solved texts.")
        print("✅ [TEST 3 PASSED] Solved archive returns correct records.")

        # ---------------------------------------------------------
        # TEST 4: Anti-Cheat Unsolved Detail Authorization Check
        # ---------------------------------------------------------
        print("\n[TEST 4] Testing Anti-Cheat on /api/stream/solved/{text_id}...")
        fresh_user = f"unauth-user-{uuid.uuid4().hex[:8]}"
        res_slots_fresh = client.get(f"/api/stream/slots?user_id={fresh_user}&profile_key={profile_key}")
        unsolved_id = res_slots_fresh.json()["slots"][0]["text"]["id"]

        res_forbidden = client.get(f"/api/stream/solved/{unsolved_id}?user_id={fresh_user}")
        assert res_forbidden.status_code == 403, f"Expected 403 Forbidden, got {res_forbidden.status_code}"
        print("  - Access to unsolved task details correctly blocked with 403 Forbidden.")
        print("✅ [TEST 4 PASSED] Anti-Cheat access control verified.")

        # ---------------------------------------------------------
        # TEST 5: all_correct Mode with Retry & Mistake Hiding
        # ---------------------------------------------------------
        print("\n[TEST 5] Testing all_correct mode and retry flow...")
        ac_user = f"ac-user-{uuid.uuid4().hex[:8]}"
        res_ac_slots = client.get(f"/api/stream/slots?user_id={ac_user}&profile_key={profile_key}")
        ac_text = res_ac_slots.json()["slots"][0]["text"]
        ac_text_id = ac_text["id"]
        ac_q = ac_text["questions"][0]

        # Находим неверный вариант
        wrong_opt = (
            db.query(models.Option)
            .filter(models.Option.question_id == ac_q["id"], models.Option.is_correct == False)
            .first()
        )
        assert wrong_opt is not None

        # Попытка 1: сдаем неверный ответ
        p1 = {
            "user_id": ac_user,
            "text_id": ac_text_id,
            "answers": [{"question_id": ac_q["id"], "selected_option_id": wrong_opt.id}],
            "idempotency_key": f"ac-try-1-{uuid.uuid4()}",
            "mode": "first",
            "solved_when": "all_correct",
            "all_correct_max_attempts": 2
        }
        res_p1 = client.post("/api/stream/complete", json=p1)
        assert res_p1.status_code == 200
        d1 = res_p1.json()
        assert d1["is_solved"] is False
        assert d1["status"] == "needs_correction"
        assert ac_q["id"] in d1["error_question_ids"]
        assert "correct_option_id" not in d1, "Anti-Cheat leak: correct_option_id leaked during retry!"
        print("  - Attempt 1: task not solved, errors highlighted without leaking correct key.")

        # Попытка 2: повторная сдача (достижение лимита попыток)
        p2 = {
            "user_id": ac_user,
            "text_id": ac_text_id,
            "answers": [{"question_id": ac_q["id"], "selected_option_id": wrong_opt.id}],
            "idempotency_key": f"ac-try-2-{uuid.uuid4()}",
            "mode": "retry",
            "solved_when": "all_correct",
            "all_correct_max_attempts": 2
        }
        res_p2 = client.post("/api/stream/complete", json=p2)
        assert res_p2.status_code == 200
        d2 = res_p2.json()
        assert d2["is_solved"] is True
        print("  - Attempt 2: max attempts reached, task moved to solved with full review.")
        print("✅ [TEST 5 PASSED] all_correct mode and leak-proof retry verified.")

        # ---------------------------------------------------------
        # TEST 6: Defect Reporting & Auto-Deactivation
        # ---------------------------------------------------------
        print("\n[TEST 6] Testing defect reporting and auto-deactivation...")
        test_slug = f"report-test-{uuid.uuid4().hex[:6]}"
        t_obj = models.Text(
            slug=test_slug,
            title="Тест на дефекты",
            level="N5",
            category="short",
            content_html="<p>Текст с опечаткой</p>",
            translation_ru="Тестовый перевод задания",
            recommended_time_min=2,
            is_active=True,
            report_count=0
        )
        db.add(t_obj)
        db.commit()
        db.refresh(t_obj)
        t_id = t_obj.id

        # Жалобы 1 и 2
        for i in range(1, 3):
            r = client.post(f"/api/texts/{t_id}/report", json={"reason": f"Жалоба {i}"})
            assert r.status_code == 200
            assert r.json()["report_count"] == i
            assert r.json()["is_active"] is True

        # Жалоба 3 (порог = 3) -> auto deactivation
        r3 = client.post(f"/api/texts/{t_id}/report", json={"reason": "Критическая ошибка"})
        assert r3.status_code == 200
        assert r3.json()["report_count"] == 3
        assert r3.json()["is_active"] is False
        assert r3.json()["deactivated"] is True

        # Проверка в БД
        db.expire_all()
        check_text = db.query(models.Text).filter(models.Text.id == t_id).first()
        assert check_text.is_active is False
        print("  - 3 reports triggered auto-deactivation (is_active = False).")
        print("✅ [TEST 6 PASSED] Defect reporting and auto-deactivation verified.")

        print("\n" + "=" * 60)
        print("🎉 ALL 6 STREAM LIFECYCLE & ANTI-CHEAT TESTS PASSED!")
        print("=" * 60)

    finally:
        db.close()


if __name__ == "__main__":
    run_all_tests()
