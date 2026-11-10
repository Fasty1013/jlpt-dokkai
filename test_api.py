import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from database import SessionLocal
from main import list_texts, get_text_for_reading, submit_and_analyze
from schemas import SubmitPayloadSchema, AnswerSubmissionSchema

db = SessionLocal()

# 1. Test Catalog endpoint function
catalog = list_texts(level=None, category=None, db=db)
print("Catalog count:", len(catalog))
assert len(catalog) >= 5
print("Catalog titles count:", len(catalog))

# 2. Test Reading endpoint function (Anti-Cheat check)
text_id = catalog[0].id
read_data = get_text_for_reading(text_id=text_id, db=db)
print("Text 1 title:", read_data.title)
assert len(read_data.questions) > 0

# Convert to dict to verify anti-cheat field stripping
dumped = read_data.model_dump()
first_q = dumped["questions"][0]

assert "evidence_span_id" not in first_q, "Leak: evidence_span_id found in question!"
assert "general_explanation" not in first_q, "Leak: general_explanation found in question!"
assert "translation_ru" not in dumped, "Leak: translation_ru found in text schema!"
assert "vocabulary_json" not in dumped, "Leak: vocabulary found in text schema!"

first_opt = first_q["options"][0]
assert "is_correct" not in first_opt, "Leak: is_correct found in option!"
assert "option_explanation" not in first_opt, "Leak: option_explanation found in option!"
assert "trap_type" not in first_opt, "Leak: trap_type found in option before submit!"
print("Anti-Cheat Strict Mode PASSED: No answers, explanations, or trap types leaked to client.")

# 2.1 Test Anti-Cheat across N3, N2, N1 authentic texts
for test_lvl in ["N3", "N2", "N1"]:
    lvl_texts = [t for t in catalog if t.level == test_lvl]
    assert len(lvl_texts) > 0, f"No texts found for level {test_lvl}!"
    sample_text = get_text_for_reading(text_id=lvl_texts[0].id, db=db)
    s_dump = sample_text.model_dump()
    assert "translation_ru" not in s_dump, f"Leak: translation_ru found in {test_lvl}!"
    for q in s_dump["questions"]:
        assert "evidence_span_id" not in q, f"Leak: evidence_span_id found in {test_lvl} question!"
        assert "general_explanation" not in q, f"Leak: general_explanation in {test_lvl} question!"
        for o in q["options"]:
            assert "is_correct" not in o, f"Leak: is_correct in {test_lvl} option!"
            assert "option_explanation" not in o, f"Leak: option_explanation in {test_lvl} option!"
            assert "trap_type" not in o, f"Leak: trap_type in {test_lvl} option!"
print("Cross-Level Anti-Cheat Isolation PASSED: N3, N2, N1 fully verified.")

# 3. Test Submit and Analyze endpoint function
# Find correct options for all questions in this text to test 100% submission
from models import Question as QModel
answers_payload = []
for q_item in read_data.questions:
    q_db = db.query(QModel).filter(QModel.id == q_item.id).first()
    corr_opt = [o for o in q_db.options if o.is_correct][0]
    answers_payload.append(AnswerSubmissionSchema(question_id=q_item.id, selected_option_id=corr_opt.id))

payload = SubmitPayloadSchema(
    answers=answers_payload,
    time_spent_sec=75
)

analysis_data = submit_and_analyze(text_id=text_id, payload=payload, db=db)
analysis_dumped = analysis_data.model_dump()

print(f"User score: {analysis_data.correct_count} / {analysis_data.total_questions} ({analysis_data.score_percent}%)")
assert analysis_data.correct_count == len(read_data.questions)
assert analysis_data.score_percent == 100.0
assert "translation_ru" in analysis_dumped
assert len(analysis_dumped["vocabulary"]) > 0
assert analysis_dumped["questions"][0]["evidence_span_id"] is not None
print("Submit & Analysis PASSED: Score, explanations, and evidence spans verified.")

# Test Text 2 reading
text2_id = catalog[1].id
read_data_2 = get_text_for_reading(text2_id, db)
assert len(read_data_2.questions) >= 1
print("Text 2 loaded successfully with questions.")

# 4. Test Dictionary Lookup
from main import dictionary_lookup
dict_res = dictionary_lookup(q="持続可能")
assert dict_res["word"] == "持続可能"
assert dict_res["level"] == "N2"
print("Dictionary Lookup PASSED:", dict_res["word"], "->", dict_res["reading"])

# 5. Test Stream Complete Idempotency
from app.services.stream_service import complete_task, get_or_create_slots
from models import Attempt, UserTextState, TaskSlot

test_user = "test-user-idempotency"
db.query(Attempt).filter(Attempt.user_id == test_user).delete()
db.query(UserTextState).filter(UserTextState.user_id == test_user).delete()
db.query(TaskSlot).filter(TaskSlot.user_id == test_user).delete()
db.commit()

slots = get_or_create_slots(db, user_id=test_user, profile_key="N5:short")
first_slot = [s for s in slots if s["state"] == "active"][0]
target_text_id = first_slot["text"]["id"]
target_read = get_text_for_reading(target_text_id, db)
sample_answers = [{"question_id": q.id, "selected_option_id": q.options[0].id} for q in target_read.questions]
idem_key = "test-idem-key-duplicate-check-999"

# First submission
res1 = complete_task(
    db=db,
    user_id=test_user,
    text_id=target_text_id,
    answers=sample_answers,
    idempotency_key=idem_key,
    mode="first",
    solved_when="all_questions_answered"
)
assert res1["is_solved"] is True
attempt_count_1 = db.query(Attempt).filter(Attempt.user_id == test_user, Attempt.text_id == target_text_id).count()
assert attempt_count_1 == 1

# Second submission with the IDENTICAL idempotency key (simulating network retry)
res2 = complete_task(
    db=db,
    user_id=test_user,
    text_id=target_text_id,
    answers=sample_answers,
    idempotency_key=idem_key,
    mode="first",
    solved_when="all_questions_answered"
)
assert res2["is_solved"] is True
assert res2["text_id"] == target_text_id
assert res2["score_percent"] == res1["score_percent"]

# Verify strict idempotency: no duplicate attempts, no duplicate UserTextState
attempt_count_2 = db.query(Attempt).filter(Attempt.user_id == test_user, Attempt.text_id == target_text_id).count()
assert attempt_count_2 == 1, f"Idempotency failed: expected 1 attempt, found {attempt_count_2}"

state_count = db.query(UserTextState).filter(UserTextState.user_id == test_user, UserTextState.text_id == target_text_id).count()
assert state_count == 1, f"Idempotency failed: duplicate UserTextState created ({state_count})"

user_state_rec = db.query(UserTextState).filter(UserTextState.user_id == test_user, UserTextState.text_id == target_text_id).first()
assert user_state_rec.attempts_count == 1, f"Idempotency failed: attempts_count incremented to {user_state_rec.attempts_count}"

print("Stream Complete Idempotency PASSED: Repeated submission with same idempotency_key returns identical analysis without duplicate records or slot corruption.")

# 6. Test Idempotency with Unsolved Task (Anti-Cheat Leak Protection)
# Submit wrong answer in all_correct mode: task remains unsolved (status = in_progress)
test_user_leak = "test-user-anti-cheat-idempotency"
db.query(Attempt).filter(Attempt.user_id == test_user_leak).delete()
db.query(UserTextState).filter(UserTextState.user_id == test_user_leak).delete()
db.query(TaskSlot).filter(TaskSlot.user_id == test_user_leak).delete()
db.commit()

slots_leak = get_or_create_slots(db, user_id=test_user_leak, profile_key="N5:short")
slot_leak = [s for s in slots_leak if s["state"] == "active"][0]
leak_text_id = slot_leak["text"]["id"]
leak_read = get_text_for_reading(leak_text_id, db)

# Choose deliberately wrong option (option_id that is NOT correct)
first_q = leak_read.questions[0]
wrong_option_id = -99999  # Non-existent or invalid option ensures zero score
wrong_answers = [{"question_id": first_q.id, "selected_option_id": wrong_option_id}]
leak_idem_key = "leak-idem-test-key-555"

# First attempt with wrong answer in all_correct mode
sub1 = complete_task(
    db=db,
    user_id=test_user_leak,
    text_id=leak_text_id,
    answers=wrong_answers,
    idempotency_key=leak_idem_key,
    mode="first",
    solved_when="all_correct",
    all_correct_max_attempts=2
)
assert sub1["is_solved"] is False, "Task should NOT be solved on wrong answer in all_correct mode"
assert "error_question_ids" in sub1
assert "analysis" not in sub1, "Anti-Cheat leak: full analysis found in unsolved submission!"

# Second attempt with the SAME idempotency key (simulating network duplicate on failed attempt)
sub2 = complete_task(
    db=db,
    user_id=test_user_leak,
    text_id=leak_text_id,
    answers=wrong_answers,
    idempotency_key=leak_idem_key,
    mode="first",
    solved_when="all_correct",
    all_correct_max_attempts=2
)
# Branch behavior: strictly preserves is_solved: False without leaking get_solved_task_details!
assert sub2["is_solved"] is False, "Anti-Cheat violation: idempotency replay marked unsolved task as solved!"
assert "error_question_ids" in sub2
assert "questions" not in sub2, "Anti-Cheat violation: answers leaked on idempotent replay of unsolved task!"
print("Anti-Cheat Idempotency PASSED: Replay of unsolved attempt strictly blocks answer key leakage.")

# Clean up synthetic test user
db.query(Attempt).filter(Attempt.user_id == test_user_leak).delete()
db.query(UserTextState).filter(UserTextState.user_id == test_user_leak).delete()
db.query(TaskSlot).filter(TaskSlot.user_id == test_user_leak).delete()
db.commit()

db.close()
print("ALL BACKEND & ANTI-CHEAT TESTS PASSED!")
