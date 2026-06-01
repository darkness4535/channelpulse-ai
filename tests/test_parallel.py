"""Tests for parallel wave scheduling."""

from __future__ import annotations

import unittest

from company.parallel import compute_waves
from company.tasks import Task


class ParallelTests(unittest.TestCase):
    def test_three_waves(self) -> None:
        tasks = [
            Task("a", "lead_researcher", "x", metadata={"stage": "leads"}),
            Task("b", "account_manager", "x", metadata={"stage": "clients"}),
            Task(
                "c",
                "head_of_sales",
                "x",
                metadata={"stage": "sales", "depends_on": ["leads"]},
            ),
            Task(
                "d",
                "director",
                "x",
                metadata={"stage": "director", "depends_on": ["leads", "sales"]},
            ),
        ]
        waves = compute_waves(tasks)
        self.assertEqual(len(waves), 3)
        wave1_roles = {t.role for t in waves[0]}
        self.assertIn("lead_researcher", wave1_roles)
        self.assertIn("account_manager", wave1_roles)


if __name__ == "__main__":
    unittest.main()
