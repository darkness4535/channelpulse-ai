"""Tests for GBP audit scoring and PDF generation."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from company.audit import audit_lead, audit_leads_file, generate_audit_pdf


class AuditTests(unittest.TestCase):
    def test_audit_lead_scores_and_quick_wins(self) -> None:
        lead = {
            "lead_id": "test-cafe",
            "name": "Test Cafe",
            "city": "Berlin",
            "country": "DE",
            "rating": 3.5,
            "review_count": 5,
            "website": "https://example.com",
            "pain_signals": ["few photos", "empty description", "no posts"],
            "score": 8,
        }
        audit = audit_lead(lead)
        self.assertEqual(audit["lead_id"], "test-cafe")
        self.assertLessEqual(audit["visibility_score"], 100)
        self.assertGreaterEqual(audit["visibility_score"], 0)
        self.assertEqual(len(audit["quick_wins"]), 3)

    def test_generate_pdf(self) -> None:
        audit = audit_lead(
            {
                "lead_id": "pdf-test",
                "name": "PDF Test Shop",
                "city": "Austin",
                "country": "US",
                "rating": 4.0,
                "review_count": 10,
                "pain_signals": ["no responses"],
                "score": 7,
            }
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "pdf-test.pdf"
            generate_audit_pdf(audit, path)
            self.assertTrue(path.exists())
            self.assertGreater(path.stat().st_size, 100)

    def test_audit_leads_file_pipeline(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            leads_path = tmp_path / "leads.json"
            audits_dir = tmp_path / "audits"
            leads_path.write_text(
                json.dumps(
                    {
                        "leads": [
                            {
                                "lead_id": "high-score",
                                "name": "High Score Biz",
                                "score": 8,
                                "rating": 3.0,
                                "review_count": 3,
                                "pain_signals": ["empty description"],
                            },
                            {
                                "lead_id": "low-score",
                                "name": "Low Score Biz",
                                "score": 4,
                            },
                        ]
                    }
                ),
                encoding="utf-8",
            )
            results = audit_leads_file(leads_path, audits_dir, company_name="Test Co")
            self.assertEqual(len(results), 1)
            self.assertTrue((audits_dir / "high-score.json").exists())
            self.assertTrue((audits_dir / "high-score.pdf").exists())
            self.assertFalse((audits_dir / "low-score.json").exists())


if __name__ == "__main__":
    unittest.main()
