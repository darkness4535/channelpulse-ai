"""Tests for multi-company context."""

from __future__ import annotations

import unittest

from company.context import list_companies, normalize_slug, resolve_company, set_active_company


class ContextTests(unittest.TestCase):
    def test_list_companies_includes_both(self) -> None:
        slugs = list_companies()
        self.assertIn("channelpulse", slugs)
        self.assertIn("localmaps-seo-audit", slugs)

    def test_resolve_localmaps(self) -> None:
        ctx = resolve_company("localmaps-seo-audit")
        self.assertEqual(ctx.slug, "localmaps-seo-audit")
        cfg = ctx.load_config()
        self.assertEqual(cfg["company"]["name"], "LocalMaps SEO Audit")
        self.assertIn("audits", cfg["operations"]["memory_dirs"])

    def test_normalize_aliases(self) -> None:
        self.assertEqual(normalize_slug("channelpulse-ai"), "channelpulse")
        self.assertEqual(normalize_slug(None), "channelpulse")

    def test_set_active_company(self) -> None:
        ctx = set_active_company("localmaps-seo-audit")
        self.assertEqual(ctx.slug, "localmaps-seo-audit")
        set_active_company("channelpulse")


if __name__ == "__main__":
    unittest.main()
