#!/usr/bin/env python3
"""Фоновый автономный цикл компании (cron / служба Windows)."""

from __future__ import annotations

import argparse
import os
import sys
import time
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from dotenv import load_dotenv

load_dotenv(ROOT / ".env")

from company.orchestrator import run_daily_cycle


def main() -> None:
    parser = argparse.ArgumentParser(description="Автономный daemon ChannelPulse AI")
    parser.add_argument(
        "--interval-hours",
        type=float,
        default=float(os.environ.get("COMPANY_INTERVAL_HOURS", "24")),
        help="Пауза между циклами (часы)",
    )
    parser.add_argument("--once", action="store_true", help="Один цикл и выход")
    parser.add_argument("--mock", action="store_true", help="Без Cursor API")
    parser.add_argument("--force-new", action="store_true", help="Новый план каждый цикл")
    args = parser.parse_args()

    if args.mock:
        os.environ["COMPANY_MOCK"] = "1"
    os.environ.setdefault("COMPANY_AUTONOMOUS", "1")

    last_run_date: str | None = None

    while True:
        today = date.today().isoformat()
        force = args.force_new or (last_run_date != today)
        print(f"\n========== Цикл {today} force_new={force} ==========")
        code = run_daily_cycle(force_new=force, interactive=False)
        last_run_date = today
        if args.once:
            sys.exit(code)
        secs = max(60.0, args.interval_hours * 3600.0)
        print(f"Следующий цикл через {args.interval_hours} ч...")
        time.sleep(secs)


if __name__ == "__main__":
    main()
