#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Automated Synthetic Test Suite for PDF Import & Staging Pipeline.
Uses reportlab to generate test fixtures dynamically:
1. Valid PDF with passage, 3 questions, 4 options each, answer key.
2. PDF without answer key (needs review).
3. Corrupted / invalid file header (validation error).
4. Scanned PDF without digital text layer (rejected / OCR check).
5. Draft isolation: staging drafts are invisible to public training API (GET /api/texts).
6. Human Review & Publication flow (publish_draft and reject_draft).
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path

# Set UTF-8 encoding for standard output
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from fastapi.testclient import TestClient

from main import app
from database import SessionLocal
from models import Text, Question, Option
from tools.pdf_import.pipeline import run_pdf_import_pipeline, STAGING_DIR
from tools.pdf_import.review import publish_draft, reject_draft, list_staging_drafts
from tools.pdf_import.validator import validate_pdf_file

# Register Japanese CID Font for ReportLab
try:
    pdfmetrics.registerFont(UnicodeCIDFont("HeiseiMin-W3"))
    CID_FONT_AVAILABLE = True
except Exception:
    CID_FONT_AVAILABLE = False


def create_sample_japanese_pdf(pdf_path: Path, include_answer_key: bool = True) -> Path:
    """Creates a synthetic multi-question JLPT Dokkai PDF using ReportLab."""
    c = canvas.Canvas(str(pdf_path))
    font_name = "HeiseiMin-W3" if CID_FONT_AVAILABLE else "Helvetica"

    # Page 1: Passage + 3 Questions with 4 options each
    t = c.beginText(50, 750)
    t.setFont(font_name, 11)
    t.textLine("日本における自然保護の歴史は古く、多くの人々が自然と共生してきました。")
    t.textLine("【1】自然を守るための多様な取り組みが全国各地で熱心に行われてきました。")
    t.textLine("最近では、地域社会と密接に連携した新しい活動が特に注目されています。")
    t.textLine("これからの時代は一人ひとりが環境問題を自分のこととして考える必要があります。")
    t.textLine("")
    t.textLine("問1 この文章の内容と最も合致しているものはどれですか。")
    t.textLine("1. 自然保護の取り組みは最近始まったばかりである。")
    t.textLine("2. 自然と共生することは昔から行われていなかった。")
    t.textLine("3. 自然を守るための多様な取り組みが全国で進められている。")
    t.textLine("4. 地域社会との連携はまったく必要とされていない。")
    t.textLine("")
    t.textLine("問2 地域社会の活動について筆者は何と述べていますか。")
    t.textLine("1. 最近特に注目を集めている。")
    t.textLine("2. 参加者が急激に減っている。")
    t.textLine("3. 全国で禁止されるようになった。")
    t.textLine("4. 効果がまったくないと結論づけられた。")
    t.textLine("")
    t.textLine("問3 筆者が最も伝えたいことは何ですか。")
    t.textLine("1. 自然保護活動を直ちに中止すべきだということ。")
    t.textLine("2. 過去の取り組みだけを評価すべきだということ。")
    t.textLine("3. 新しい技術だけで自然を守るべきだということ。")
    t.textLine("4. 一人ひとりが環境問題を自分のこととして考えることの大切さ。")
    c.drawText(t)
    c.showPage()

    # Page 2: Answer key section (if requested)
    if include_answer_key:
        t2 = c.beginText(50, 750)
        t2.setFont(font_name, 12)
        t2.textLine("解答一覧")
        t2.textLine("問1: 3")
        t2.textLine("問2: 1")
        t2.textLine("問3: 4")
        c.drawText(t2)
        c.showPage()

    c.save()
    return pdf_path


def create_scanned_dummy_pdf(pdf_path: Path) -> Path:
    """Creates a PDF with no text layer (simulates empty / raster scan)."""
    c = canvas.Canvas(str(pdf_path))
    c.rect(50, 50, 400, 600, stroke=1, fill=0)
    c.showPage()
    c.save()
    return pdf_path


class TestPDFImportPipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.temp_dir = tempfile.TemporaryDirectory()
        cls.temp_path = Path(cls.temp_dir.name)

    @classmethod
    def tearDownClass(cls):
        cls.temp_dir.cleanup()
        # Clean any remaining draft files from staging
        for draft_file in STAGING_DIR.glob("draft-test-*.json"):
            try:
                draft_file.unlink()
            except Exception:
                pass

    def test_01_valid_pdf_full_pipeline(self):
        """1. Valid PDF: 100% extraction, questions, 4 options, answer key matching."""
        pdf_path = self.temp_path / "sample_valid.pdf"
        create_sample_japanese_pdf(pdf_path, include_answer_key=True)

        res = run_pdf_import_pipeline(pdf_path, level="N3", category="short", title_override="Test N3 Book Import")

        self.assertTrue(res["success"], f"Pipeline failed: {res.get('error')}")
        self.assertEqual(res["total_drafts_created"], 1)
        self.assertEqual(res["answer_keys_found"], 3)

        draft = res["drafts"][0]
        self.assertEqual(draft["level"], "N3")
        self.assertEqual(draft["category"], "short")
        self.assertEqual(draft["title"], "Test N3 Book Import")
        self.assertGreaterEqual(draft["confidence"], 0.80)

        # Verify extracted questions
        questions = draft["questions"]
        self.assertEqual(len(questions), 3, "Must extract exactly 3 questions")

        expected_answers = {1: 3, 2: 1, 3: 4}
        for q in questions:
            q_num = q["question_number"]
            self.assertTrue(q["answer_matched"], f"Question {q_num} must have answer matched from key")
            self.assertEqual(len(q["options"]), 4, f"Question {q_num} must have 4 options")

            correct_opts = [opt for opt in q["options"] if opt["is_correct"]]
            self.assertEqual(len(correct_opts), 1, f"Question {q_num} must have exactly 1 correct option")
            self.assertEqual(correct_opts[0]["option_number"], expected_answers[q_num])

        # Cleanup staged file
        stage_file = STAGING_DIR / f"{draft['slug']}.json"
        self.assertTrue(stage_file.exists(), "Draft must be written to staging directory")
        stage_file.unlink()

    def test_02_pdf_without_answer_key(self):
        """2. PDF without answer key: marks needs_review and answer_unmatched."""
        pdf_path = self.temp_path / "sample_no_answers.pdf"
        create_sample_japanese_pdf(pdf_path, include_answer_key=False)

        res = run_pdf_import_pipeline(pdf_path, level="N3", category="short", title_override="Test No Key")

        self.assertTrue(res["success"])
        self.assertEqual(res["answer_keys_found"], 0)

        draft = res["drafts"][0]
        self.assertTrue(draft["needs_review"], "Draft must need manual review when answers are missing")
        self.assertLess(draft["confidence"], 0.80, "Confidence must be penalized when answers are missing")

        for q in draft["questions"]:
            self.assertFalse(q["answer_matched"], "Answer matched must be False")
            correct_opts = [opt for opt in q["options"] if opt["is_correct"]]
            self.assertEqual(len(correct_opts), 0, "No option should be marked correct without answer key")

        # Cleanup staged file
        stage_file = STAGING_DIR / f"{draft['slug']}.json"
        if stage_file.exists():
            stage_file.unlink()

    def test_03_corrupt_file_header(self):
        """3. Corrupted file header (non-PDF magic bytes) raises validation error."""
        corrupt_path = self.temp_path / "corrupt.pdf"
        with open(corrupt_path, "wb") as f:
            f.write(b"NOT_A_VALID_PDF_HEADER_DATA_1234567890")

        res = run_pdf_import_pipeline(corrupt_path, level="N2")

        self.assertFalse(res["success"])
        self.assertEqual(res["stage"], "validation")
        self.assertIn("magic bytes", res["error"])

    def test_04_scanned_pdf_without_text_layer(self):
        """4. Scanned PDF with no digital text layer is rejected with OCR notice."""
        scan_path = self.temp_path / "scanned_doc.pdf"
        create_scanned_dummy_pdf(scan_path)

        res = run_pdf_import_pipeline(scan_path, level="N3")

        self.assertFalse(res["success"])
        self.assertEqual(res["stage"], "ocr_unavailable")
        self.assertTrue(res.get("ocr_unavailable"))
        self.assertIn("сканом", res["error"])

    def test_05_draft_isolation_anti_cheat(self):
        """5. Draft isolation: staging drafts NEVER appear in public API or training texts."""
        # Create a mock draft in staging
        test_slug = "draft-test-isolated-slug-123"
        draft_file = STAGING_DIR / f"{test_slug}.json"
        mock_draft = {
            "slug": test_slug,
            "level": "N3",
            "category": "short",
            "title": "Confidential Unreleased Draft",
            "recommended_time_min": 3,
            "body_html": "<p>秘密のドラフト本文です。</p>",
            "translation_ru": "Секретный текст",
            "vocabulary": [],
            "needs_manual_review": [],
            "is_staged": True,
            "confidence": 0.95,
            "needs_review": False,
            "questions": []
        }
        with open(draft_file, "w", encoding="utf-8") as f:
            import json
            json.dump(mock_draft, f)

        try:
            # Query public API
            resp = self.client.get("/api/texts?level=N3")
            self.assertEqual(resp.status_code, 200)
            data = resp.json()

            # Ensure test_slug is NOT in results
            found = any(t.get("slug") == test_slug for t in data)
            self.assertFalse(found, f"CRITICAL LEAK: Staging draft {test_slug} was exposed in GET /api/texts!")

            # Query non-existent text endpoint
            resp_single = self.client.get("/api/texts/999999")
            self.assertEqual(resp_single.status_code, 404, "Non-existent text must return 404")
        finally:
            if draft_file.exists():
                draft_file.unlink()

    def test_06_review_publish_and_reject_flow(self):
        """6. Review workflow: publishing adds to DB, rejecting deletes from staging."""
        pdf_path = self.temp_path / "review_sample.pdf"
        create_sample_japanese_pdf(pdf_path, include_answer_key=True)

        res = run_pdf_import_pipeline(pdf_path, level="N3", category="short", title_override="Publish Test")
        self.assertTrue(res["success"])
        draft = res["drafts"][0]
        slug = draft["slug"]

        stage_file = STAGING_DIR / f"{slug}.json"
        self.assertTrue(stage_file.exists())

        # Test publication
        pub_success = publish_draft(slug)
        self.assertTrue(pub_success, "Draft publication must succeed")
        self.assertFalse(stage_file.exists(), "Draft file must be removed from staging after publication")

        # Verify DB entry
        db = SessionLocal()
        try:
            db_text = db.query(Text).filter(Text.slug == slug).first()
            self.assertIsNotNone(db_text, "Published text must exist in database")
            self.assertEqual(len(db_text.questions), 3, "Published text must have 3 questions")

            # Verify API returns published text using db_text.id
            api_resp = self.client.get(f"/api/texts/{db_text.id}")
            self.assertEqual(api_resp.status_code, 200)
            self.assertEqual(api_resp.json()["id"], db_text.id)

            # Cleanup DB (cascades to questions and options automatically)
            db.delete(db_text)
            db.commit()
        finally:
            db.close()

        # Test rejection flow
        res2 = run_pdf_import_pipeline(pdf_path, level="N3", category="short", title_override="Reject Test")
        slug2 = res2["drafts"][0]["slug"]
        stage_file2 = STAGING_DIR / f"{slug2}.json"
        self.assertTrue(stage_file2.exists())

        rej_success = reject_draft(slug2)
        self.assertTrue(rej_success)
        self.assertFalse(stage_file2.exists(), "Draft must be deleted upon rejection")


if __name__ == "__main__":
    unittest.main(verbosity=2)
