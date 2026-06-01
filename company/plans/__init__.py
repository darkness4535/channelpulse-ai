"""Daily plan builders per company."""

from __future__ import annotations

from company.plans.channelpulse import build_daily_plan as build_channelpulse_plan
from company.plans.localmaps import build_daily_plan as build_localmaps_plan

BUILDERS = {
    "channelpulse": build_channelpulse_plan,
    "localmaps-seo-audit": build_localmaps_plan,
}


def build_daily_plan(slug: str, cfg: dict):
    builder = BUILDERS.get(slug)
    if builder is None:
        raise KeyError(f"No daily plan for company: {slug}")
    return builder(cfg)
