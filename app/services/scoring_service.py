"""Post-submit evaluation: scores answers and builds the full analysis payload (Step 8b).

Anti-Cheat: this is the ONLY place where correctness, explanations, trap types and
evidence span ids are assembled; it is reachable only after the user submitted answers.
"""
from app.models import Text
from app.schemas import (
    SubmitPayloadSchema,
    TextAnalysisSchema,
    QuestionAnalysisSchema,
    OptionAnalysisSchema,
    VocabularyItemSchema,
)


def build_text_analysis(text: Text, payload: SubmitPayloadSchema) -> TextAnalysisSchema:
    user_answers_map = {ans.question_id: ans.selected_option_id for ans in payload.answers}

    total_questions = len(text.questions)
    correct_count = 0
    questions_analysis = []

    for q in text.questions:
        selected_opt_id = user_answers_map.get(q.id)
        correct_opt = next((opt for opt in q.options if opt.is_correct), None)
        correct_opt_id = correct_opt.id if correct_opt else -1

        is_user_correct = (selected_opt_id is not None and selected_opt_id == correct_opt_id)
        if is_user_correct:
            correct_count += 1

        options_analysis = []
        for opt in q.options:
            was_selected = (selected_opt_id == opt.id)
            options_analysis.append(
                OptionAnalysisSchema(
                    id=opt.id,
                    option_number=opt.option_number,
                    option_text=opt.option_text,
                    is_correct=opt.is_correct,
                    trap_type=opt.trap_type,
                    option_explanation=opt.option_explanation,
                    was_selected=was_selected
                )
            )

        questions_analysis.append(
            QuestionAnalysisSchema(
                id=q.id,
                question_number=q.question_number,
                question_text=q.question_text,
                general_explanation=q.general_explanation,
                evidence_span_id=q.evidence_span_id,
                is_user_correct=is_user_correct,
                selected_option_id=selected_opt_id,
                correct_option_id=correct_opt_id,
                options=options_analysis
            )
        )

    score_percent = round((correct_count / total_questions * 100), 1) if total_questions > 0 else 0.0

    raw_vocab = text.vocabulary_json or []
    vocab_items = [
        VocabularyItemSchema(
            word=item.get("word", ""),
            furigana=item.get("furigana", ""),
            translation=item.get("translation", "")
        )
        for item in raw_vocab
    ]

    return TextAnalysisSchema(
        id=text.id,
        title=text.title,
        level=text.level,
        category=text.category,
        source_exam=text.source_exam,
        is_nhk=text.is_nhk,
        recommended_time_min=text.recommended_time_min,
        content_html=text.content_html,
        translation_ru=text.translation_ru,
        vocabulary=vocab_items,
        total_questions=total_questions,
        correct_count=correct_count,
        score_percent=score_percent,
        time_spent_sec=payload.time_spent_sec,
        questions=questions_analysis
    )
