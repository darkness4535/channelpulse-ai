#!/usr/bin/env python3
"""CLI entrypoint for ChannelPulse AI."""

from __future__ import annotations

import argparse
import os
import sys
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
os.environ.setdefault("COMPANY_AUTONOMOUS", "1")

from company.orchestrator import load_config, run_daily_cycle, run_single_role
from company.registry import hire, list_roles
from company.staff import fire_from_staff, hire_to_staff, is_hired, print_roster


def main() -> None:
    parser = argparse.ArgumentParser(
        description="ChannelPulse AI — автономная компания (параллельно, без участия)"
    )
    parser.add_argument("--cycle", choices=["daily"], help="Дневной цикл")
    parser.add_argument("--role", help="Одна роль")
    parser.add_argument("--task", help="Задача для --role")
    parser.add_argument("--dry-run", action="store_true", help="План и волны без API")
    parser.add_argument("--mock", action="store_true", help="Локально без Cursor API")
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Спросить y/n при найме (старый режим)",
    )
    parser.add_argument("--no-hire", action="store_true", help="Не нанимать новых")
    parser.add_argument("--force-new", action="store_true", help="Новый план дня")
    parser.add_argument(
        "--workers",
        type=int,
        default=None,
        help="Потоков параллельно (по умолчанию из config)",
    )
    parser.add_argument("--list-roles", action="store_true")
    parser.add_argument("--staff", action="store_true")
    parser.add_argument("--hire", metavar="ROLE")
    parser.add_argument("--fire", metavar="ROLE")
    args = parser.parse_args()

    if args.mock:
        os.environ["COMPANY_MOCK"] = "1"

    if args.interactive:
        os.environ["COMPANY_AUTONOMOUS"] = "0"

    if args.list_roles:
        for r in list_roles():
            mark = "✓" if is_hired(r) else " "
            print(f"  [{mark}] {r}")
        return

    if args.staff:
        print_roster()
        return

    if args.hire:
        hire_to_staff(args.hire)
        print(f"Нанят: {hire(args.hire).hire_label}")
        return

    if args.fire:
        if fire_from_staff(args.fire):
            print(f"Уволен: {args.fire}")
        else:
            print(f"Не в штате: {args.fire}")
        return

    if args.cycle == "daily":
        code = run_daily_cycle(
            dry_run=args.dry_run,
            interactive=args.interactive,
            auto_no=args.no_hire,
            force_new=args.force_new,
            workers=args.workers,
        )
        sys.exit(code)

    if args.role:
        if not args.task:
            raise SystemExit("--task required with --role")
        run_single_role(
            args.role,
            args.task,
            dry_run=args.dry_run,
            interactive=args.interactive,
            auto_no=args.no_hire,
        )
        return

    cfg = load_config()
    print(f"\n{cfg['company']['name']} — автономный режим (по умолчанию)")
    print("  python -m scripts.run_company --cycle daily --mock --force-new")
    print("  python -m scripts.run_autonomous --once --mock")
    print("  python -m scripts.run_autonomous --interval-hours 24 --mock  # daemon")


if __name__ == "__main__":
    main()
