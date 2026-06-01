"""Director orchestrator — autonomous parallel company cycle."""

from __future__ import annotations

import json
import os
import sys
from datetime import date
from pathlib import Path

from company.agent_runner import run_task, use_mock_mode
from company.context import CompanyContext, get_active_company, set_active_company
from company.directives import format_for_prompt
from company.events import log_event
from company import runtime_state
from company.hiring import ensure_hired_for_task, is_autonomous, prepare_team_for_cycle
from company.parallel import default_workers, run_tasks_parallel
from company.plans import build_daily_plan
from company.registry import hire
from company.staff import is_hired, print_roster
from company.tasks import Task, TaskStatus, append_task, load_tasks, supersede_daily_plans

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def load_config(ctx: CompanyContext | None = None) -> dict:
    return (ctx or get_active_company()).load_config()


def _memory_path(cfg: dict, key: str, ctx: CompanyContext | None = None) -> Path:
    return (ctx or get_active_company()).memory_path(key, cfg)


def today_plan_date() -> str:
    return date.today().isoformat()


def tasks_for_today_plan() -> list[Task]:
    today = today_plan_date()
    return sorted(
        [
            t
            for t in load_tasks()
            if t.metadata.get("cycle") == "daily"
            and t.metadata.get("plan_date") == today
        ],
        key=lambda t: t.priority,
    )


def enqueue_daily_cycle(cfg: dict, *, force_new: bool = False) -> list[Task]:
    today = today_plan_date()
    ctx = get_active_company()

    if force_new:
        n = supersede_daily_plans(today, include_today=True)
        if n:
            print(f"Задач заменено новым планом: {n}")
    else:
        n = supersede_daily_plans(today, include_today=False)
        if n:
            print(f"Устаревших задач закрыто: {n}")

    pending = [
        t
        for t in tasks_for_today_plan()
        if t.status in (TaskStatus.PENDING, TaskStatus.IN_PROGRESS)
    ]
    if pending and not force_new:
        return tasks_for_today_plan()

    for task in build_daily_plan(ctx.slug, cfg):
        append_task(task)
    return tasks_for_today_plan()


def format_agent_prompt(employee_role: str, task: Task, cfg: dict) -> str:
    employee = hire(employee_role)
    company_name = cfg["company"]["name"]
    locale = cfg["company"].get("locale", "ru-RU")
    lang_note = "EN" if locale.startswith("en") else "RU"
    return f"""# Роль
{employee.system_prompt}

# Контекст компании
Название: {company_name}
Ниша: {cfg["niche"]["description"]}
Услуги: {json.dumps(cfg["services"], ensure_ascii=False, indent=2)}

# Задача
**{task.title}**

{task.description}

# Правила
- Пиши файлы в репозиторий по указанным путям (создай папки при необходимости).
- Не отправляй сообщения лидам и не запускай рекламу — только черновики и файлы.
- Отвечай на {lang_note}, структурированно.
- В конце: краткий статус DONE / BLOCKED и что сделано.

{format_for_prompt()}
"""


def _runtime() -> tuple[str, Path, str]:
    api_key = os.environ.get("CURSOR_API_KEY", "").strip()
    model = os.environ.get("COMPANY_MODEL", "composer-2.5")
    cwd = Path(os.environ.get("COMPANY_CWD", PROJECT_ROOT))
    return api_key, cwd, model


def run_daily_cycle(
    *,
    dry_run: bool = False,
    interactive: bool = False,
    auto_no: bool = False,
    force_new: bool = False,
    workers: int | None = None,
    company: str | None = None,
) -> int:
    """Returns exit code 0 if all tasks done, 1 if any failed."""
    ctx = set_active_company(company) if company else get_active_company()
    cfg = ctx.load_config()
    for key in cfg["operations"]["memory_dirs"]:
        _memory_path(cfg, key, ctx)

    tasks = enqueue_daily_cycle(cfg, force_new=force_new)
    w = workers if workers is not None else default_workers(cfg)

    print(f"\n{cfg['company']['name']} — автономный цикл: {len(tasks)} задач, {w} потоков")
    print(f"Компания: {ctx.slug}")
    if is_autonomous(cfg) and not interactive:
        print("Режим: полная автономия (найм и выполнение без участия владельца)")
    print_roster()

    if dry_run:
        from company.parallel import compute_waves

        waves = compute_waves(tasks)
        for i, wave in enumerate(waves, 1):
            print(f"\n  Волна {i} (параллельно):")
            for t in wave:
                emp = hire(t.role)
                hired = "в штате" if is_hired(t.role) else "автонайм"
                print(f"    • {emp.hire_label} ({hired}): {t.title}")
        print("\nDry-run завершён.")
        return 0

    api_key, cwd, model = _runtime()
    if not api_key and not use_mock_mode():
        print(
            "CURSOR_API_KEY не задан. Используйте --mock или добавьте ключ в .env",
            file=sys.stderr,
        )
        return 1

    if use_mock_mode():
        print("Исполнение: MOCK (локальные файлы)\n")

    prepare_team_for_cycle(
        tasks,
        cfg,
        interactive=interactive,
        auto_no=auto_no,
        dry_run=False,
    )

    active = load_tasks()
    task_by_id = {t.id: t for t in active}
    for t in tasks:
        fresh = task_by_id.get(t.id, t)
        if fresh.status in (TaskStatus.DONE, TaskStatus.BLOCKED):
            continue
        ensure_hired_for_task(
            fresh, cfg, interactive=interactive, auto_no=auto_no
        )

    pending = [
        t
        for t in tasks_for_today_plan()
        if t.status not in (TaskStatus.DONE, TaskStatus.BLOCKED)
    ]

    from company.parallel import compute_waves

    waves = compute_waves(pending)
    runtime_state.write_state(waves_total=len(waves))

    def on_wave_start(num: int, wave: list[Task]) -> None:
        roles = ", ".join(sorted({t.role for t in wave}))
        print(f"\n── Волна {num}: {len(wave)} задач параллельно [{roles}] ──")
        runtime_state.write_state(
            wave=num,
            message=f"Волна {num}/{len(waves)}: {roles}",
        )
        log_event("wave_start", wave=num, roles=list({t.role for t in wave}))

    def on_task_start(task: Task) -> None:
        log_event(
            "task_start",
            task_id=task.id,
            role=task.role,
            title=task.title,
        )

    def on_task_end(task: Task, outcome) -> None:
        log_event(
            "task_end",
            task_id=task.id,
            role=task.role,
            title=task.title,
            ok=outcome.ok,
            error=outcome.error,
            preview=(outcome.output or "")[:300],
        )

    outcomes = run_tasks_parallel(
        pending,
        cfg=cfg,
        model=model,
        cwd=cwd,
        api_key=api_key,
        format_prompt=format_agent_prompt,
        workers=w,
        on_wave_start=on_wave_start,
        on_task_start=on_task_start,
        on_task_end=on_task_end,
    )

    failed = [o for o in outcomes if not o.ok]
    plan_tasks = tasks_for_today_plan()
    n_done = sum(1 for t in plan_tasks if t.status == TaskStatus.DONE)
    print(f"\nИтог: {n_done}/{len(plan_tasks)} задач закрыто, ошибок: {len(failed)}")
    reports_dir = cfg["operations"]["memory_dirs"].get("reports", "company/memory/reports")
    print(f"Артефакты: {reports_dir}/")
    return 1 if failed else 0


def run_single_role(
    role: str,
    task_text: str,
    *,
    dry_run: bool = False,
    interactive: bool = False,
    auto_no: bool = False,
    company: str | None = None,
) -> None:
    if company:
        set_active_company(company)
    cfg = load_config()
    task = Task(title="Ad-hoc", role=role, description=task_text, priority=0)
    if dry_run:
        print(format_agent_prompt(role, task, cfg)[:4000])
        return

    api_key, cwd, model = _runtime()
    if not api_key and not use_mock_mode():
        sys.exit("CURSOR_API_KEY required (or use --mock)")

    if not ensure_hired_for_task(
        task, cfg, interactive=interactive, auto_no=auto_no
    ):
        sys.exit(f"Роль «{role}» не нанята.")

    prompt = format_agent_prompt(role, task, cfg)
    print(run_task(task, prompt, model=model, cwd=cwd, api_key=api_key, cfg=cfg))
