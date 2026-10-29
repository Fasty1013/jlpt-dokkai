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
assert len(catalog) == 2
print("Catalog titles:", [item.title for item in catalog])

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
print("Anti-Cheat Strict Mode PASSED: No answers or explanations leaked to client.")

# 3. Test Submit and Analyze endpoint function
# For Text 1: Option 3 is correct
q_id = first_q["id"]
opt_id = first_q["options"][2]["id"]  # Option 3
payload = SubmitPayloadSchema(
    answers=[AnswerSubmissionSchema(question_id=q_id, selected_option_id=opt_id)],
    time_spent_sec=75
)

analysis_data = submit_and_analyze(text_id=text_id, payload=payload, db=db)
analysis_dumped = analysis_data.model_dump()

print(f"User score: {analysis_data.correct_count} / {analysis_data.total_questions} ({analysis_data.score_percent}%)")
assert analysis_data.correct_count == 1
assert analysis_data.score_percent == 100.0
assert "translation_ru" in analysis_dumped
assert len(analysis_dumped["vocabulary"]) > 0
assert analysis_dumped["questions"][0]["evidence_span_id"] == "ev-1"
assert analysis_dumped["questions"][0]["options"][2]["is_correct"] is True
assert len(analysis_dumped["questions"][0]["options"][0]["option_explanation"]) > 0

print("Submit & Analysis PASSED: Score, explanations, and evidence spans verified.")

# Test Text 2 (Info search with 2 questions)
text2_id = catalog[1].id
read_data_2 = get_text_for_reading(text2_id, db)
assert len(read_data_2.questions) == 2
print("Text 2 (Info search) loaded with 2 questions.")

db.close()
print("ALL BACKEND & ANTI-CHEAT TESTS PASSED!")
