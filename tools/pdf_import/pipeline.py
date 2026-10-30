#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
End-to-End PDF Import Pipeline.
Coordinates validation, extraction, segmentation, answer key matching,
confidence scoring, level verification, and staging.
"""

import os
import json
import uuid
from pathlib import Path
from typing import Dict, Any, List, Optional

from .validator import validate_pdf_file
from .extractor import extract_pdf_pages
from .segmenter import segment_passage_and_questions, parse_answer_key
from tools.level_check.analyzer import analyze

BASE_DIR = Path(__file__).resolve().parent.parent.parent
STAGING_DIR = BASE_DIR / "content" / "staging"
STAGING_DIR.mkdir(parents=True, exist_ok=True)

def run_pdf_import_pipeline(
    file_path: Path,
    level: str,
    category: str = "short",
    title_override: Optional[str] = None
) -> Dict[str, Any]:
    """
    Executes the complete PDF ingestion pipeline.
    Drafts are saved into content/staging/ and NEVER published automatically.
    """
    file_path = Path(file_path).resolve()
    val_res = validate_pdf_file(file_path)

    if not val_res["is_valid"]:
        return {
            "success": False,
            "error": val_res["error"],
            "stage": "validation",
            "file_hash": val_res.get("file_hash", "")
        }

    if val_res["is_scanned"]:
        return {
            "success": False,
            "error": "Файл является растровым сканом без текстового слоя. Tesseract OCR не установлен в системе.",
            "stage": "ocr_unavailable",
            "ocr_unavailable": True,
            "file_hash": val_res["file_hash"]
        }

    # Extract pages
    pages = extract_pdf_pages(file_path)
    if not pages:
        return {
            "success": False,
            "error": "Не удалось извлечь текстовые страницы из документа",
            "stage": "extraction"
        }

    # Search for answer key: check all pages (especially from the end)
    all_text = "\n\n".join(p["text"] for p in pages)
    answer_key = parse_answer_key(all_text)

    # Segment passages
    drafts = []
    file_hash = val_res["file_hash"][:8]

    for p in pages:
        # If page is too short or is answer key page, skip as separate passage
        if p["char_count"] < 40 or any(hdr in p["text"] for hdr in ["解答一覧", "正解表", "Answer Key"]):
            continue

        segmented = segment_passage_and_questions(p["text"], p["html_with_ruby"])
        passage_text = segmented["passage_text"]
        passage_html = segmented["passage_html"]
        raw_questions = segmented["questions"]

        if len(passage_text) < 40:
            continue

        doc_title = title_override or f"PDF Import: {file_path.stem} (Стр. {p['page_number']})"
        slug = f"draft-{level.lower()}-{category}-{file_hash}-p{p['page_number']}"

        # Confidence calculation
        confidence = 1.0
        confidence_reasons = []

        if not p["furigana_reliable"]:
            confidence -= 0.15
            confidence_reasons.append("Ненадёжная или отсутствующая фуригана")

        if len(raw_questions) == 0:
            confidence -= 0.35
            confidence_reasons.append("Вопросы на странице не обнаружены")

        # Questions processing
        formatted_questions = []
        for q_idx, q in enumerate(raw_questions, start=1):
            q_num = q["question_number"]
            options = q["options"]
            q_slug = f"{slug}-q{q_idx}"

            # Pad options to 4 if needed
            while len(options) < 4:
                missing_num = len(options) + 1
                options.append({
                    "option_number": missing_num,
                    "text": f"（選択肢 {missing_num}：要確認）"
                })
                confidence -= 0.10
                confidence_reasons.append(f"Вопрос {q_num}: недостающие варианты дополнены заглушками")

            # Match answer key
            matched_opt_num = answer_key.get(q_num)
            has_matched_answer = (matched_opt_num is not None)

            if not has_matched_answer:
                confidence -= 0.25
                confidence_reasons.append(f"Вопрос {q_num}: правильный ответ в ключе не найден (answer_unmatched)")

            formatted_options = []
            for opt in options[:4]:
                o_num = opt["option_number"]
                is_corr = (has_matched_answer and o_num == matched_opt_num)
                formatted_options.append({
                    "option_number": o_num,
                    "text": opt["text"],
                    "is_correct": is_corr,
                    "trap_type": None if is_corr else "misinterpretation",
                    "explanation_ru": f"Вариант {o_num} из книги. Требует ручной проверки."
                })

            formatted_questions.append({
                "slug": q_slug,
                "question_number": q_num,
                "type": "detail" if category == "short" else "claim",
                "prompt": q["prompt"],
                "evidence_span_id": q["evidence_span_id"],
                "general_explanation": f"Вопрос из {file_path.name}, стр. {p['page_number']}.",
                "options": formatted_options,
                "answer_matched": has_matched_answer
            })

        # Ensure evidence spans exist in passage_html
        for q in formatted_questions:
            ev = q["evidence_span_id"]
            if ev not in passage_html:
                # Wrap first sentence as fallback evidence
                passage_html = f'<span id="{ev}" data-evidence="{ev}">' + passage_html + '</span>'

        confidence = max(0.0, min(1.0, round(confidence, 2)))
        needs_review = (confidence < 0.70) or any(not q["answer_matched"] for q in formatted_questions)

        # Level check audit
        lvl_report = analyze(passage_html, level)
        level_warning = None
        if lvl_report["verdict"] != "ok":
            level_warning = f"Анализатор сложности указал вердикт: {lvl_report['verdict']} ({', '.join(lvl_report['reasons'][:2])})"

        draft_record = {
            "slug": slug,
            "level": level.upper(),
            "category": category,
            "title": doc_title,
            "source_type": "pdf_import",
            "source_note": f"PDF: {file_path.name}, стр. {p['page_number']} (SHA256: {file_hash})",
            "recommended_time_min": 3 if category == "short" else 5,
            "body_html": f'<div class="passage-body">{passage_html}</div>',
            "translation_ru": f"Черновик импорта из книги {file_path.name} (страница {p['page_number']}). Требует добавления перевода при ревью.",
            "vocabulary": [],
            "needs_manual_review": confidence_reasons,
            "is_staged": True,
            "confidence": confidence,
            "needs_review": needs_review,
            "level_warning": level_warning,
            "provenance": {
                "file_name": file_path.name,
                "file_hash": val_res["file_hash"],
                "page_number": p["page_number"],
                "is_vertical": p["is_vertical"]
            },
            "questions": formatted_questions
        }

        # Save to staging directory
        stage_file = STAGING_DIR / f"{slug}.json"
        with open(stage_file, "w", encoding="utf-8") as f:
            json.dump(draft_record, f, ensure_ascii=False, indent=2)

        drafts.append(draft_record)

    return {
        "success": True,
        "total_drafts_created": len(drafts),
        "file_name": file_path.name,
        "page_count": len(pages),
        "answer_keys_found": len(answer_key),
        "drafts": drafts
    }
