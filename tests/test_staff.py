"""Tests for staff roster and hiring gates."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from company.context import CompanyContext, set_active_company
from company import staff
from company.staff import HiredMember, fire_from_staff, hire_to_staff, is_hired, list_hired_ids


class StaffTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        staff_dir = Path(self.tmp.name) / "staff"
        staff_dir.mkdir()
        self.ctx = CompanyContext(
            slug="test-co",
            config_path=Path("/dev/null"),
            roles_dir=Path("/dev/null"),
            memory_root=Path(self.tmp.name),
            tasks_path=Path(self.tmp.name) / "tasks.jsonl",
            staff_path=staff_dir / "hired.json",
            directives_path=Path(self.tmp.name) / "directives.json",
        )
        self.patcher = mock.patch(
            "company.staff.get_active_company", return_value=self.ctx
        )
        self.patcher.start()
        self.addCleanup(self.patcher.stop)
        set_active_company("channelpulse")

    def test_hire_and_fire(self) -> None:
        self.assertFalse(is_hired("marketer"))
        hire_to_staff("marketer")
        self.assertTrue(is_hired("marketer"))
        self.assertIn("marketer", list_hired_ids())
        self.assertTrue(fire_from_staff("marketer"))
        self.assertFalse(is_hired("marketer"))

    def test_director_exempt(self) -> None:
        self.assertTrue(is_hired("director"))

    def test_roster_persistence(self) -> None:
        hire_to_staff("copywriter")
        data = json.loads(self.ctx.staff_path.read_text(encoding="utf-8"))
        self.assertEqual(data[0]["role_id"], "copywriter")


if __name__ == "__main__":
    unittest.main()
