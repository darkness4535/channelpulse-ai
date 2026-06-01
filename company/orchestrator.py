"""Director orchestrator — autonomous parallel company cycle."""

from __future__ import annotations

import json
import os
import sys
from datetime import date
from pathlib import Path

import yaml

from company.agent_runner import run_task, use_mock_mode
from company.directives import format_for_prompt
from company.events import log_event
from company import runtime_state
from company.hiring import ensure_hired_for_task, is_autonomous, prepare_team_for_cycle
from company.parallel import default_workers, run_tasks_parallel
from company.registry import hire
from company.staff import is_hired, print_roster
from company.tasks import Task, TaskStatus, append_task, load_tasks, supersede_daily_plans

CONFIG_PATH = Path(__file__).resolve().parent / "config.yaml"
PROJECT_ROOT = Path(__file__).resolve().parent.parent


def load_config() -> dict:
    with CONFIG_PATH.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def _memory_path(cfg: dict, key: str) -> Path:
    rel = cfg["operations"]["memory_dirs"][key]
    p = PROJECT_ROOT / rel
    p.mkdir(parents=True, exist_ok=True)
    return p


def _plan_meta(today: str, stage: str, depends_on: list[str] | None = None, **extra) -> dict:
    meta = {"cycle": "daily", "plan_date": today, "stage": stage}
    if depends_on:
        meta["depends_on"] = depends_on
    meta.update(extra)
    return meta


def build_daily_plan(cfg: dict) -> list[Task]:
    """Director plan with dependency stages for parallel waves."""
    today = date.today().isoformat()
    sales = cfg["sales"]
    return [
        Task(
            title=f"Lead research {today}",
            role="lead_researcher",
            description=(
                f"Найди {sales['daily_lead_target']} потенциальных клиентов по ICP из config. "
                "Для каждого: название, ниша, ссылка на TG/сайт, почему подходят, score 1-10. "
                f"Сохрани JSON в company/memory/leads/leads_{today}.json"
            ),
            priority=1,
            metadata=_plan_meta(today, "leads"),
        ),
        Task(
            title=f"Client delivery check {today}",
            role="account_manager",
            description=(
                "Проверь company/memory/clients/*.json. Для активных клиентов: "
                "статус, что сделано, что нужно сегодня. Если клиентов нет — "
                "создай шаблон example_client.json с демо-брифом кофейни."
            ),
            priority=2,
            metadata=_plan_meta(today, "clients"),
        ),
        Task(
            title=f"Marketing hypotheses {today}",
            role="marketer",
            description=(
                "На основе ICP и услуг из config: 3 рекламные гипотезы "
                "(канал, оффер, UTM, краткий креатив). "
                f"Сохрани company/memory/marketing/hypotheses_{today}.json"
            ),
            priority=3,
            metadata=_plan_meta(today, "marketing"),
        ),
        Task(
            title=f"Qualify leads {today}",
            role="head_of_sales",
            description=(
                f"Прочитай leads_{today}.json. Оставь топ-{sales['daily_outreach_drafts']} "
                "лидов. Для каждого: боль, пакет (starter/growth/premium), "
                "черновик первого сообщения (RU, персонально). "
                f"Сохрани company/memory/outreach/drafts_{today}.json. Не отправлять."
            ),
            priority=4,
            metadata=_plan_meta(today, "sales", ["leads"]),
        ),
        Task(
            title=f"Content pipeline {today}",
            role="content_strategist",
            description=(
                "Для каждого активного клиента: контент-план на 7 дней "
                "в memory/clients/<id>_content_plan.json"
            ),
            priority=5,
            metadata=_plan_meta(today, "content", ["clients"]),
        ),
        Task(
            title=f"Compliance review outreach {today}",
            role="compliance",
            description=(
                f"Проверь drafts_{today}.json: запреты из config, тон. "
                "Одобренные — outreach/approved/approved_{today}.json"
            ),
            priority=6,
            metadata=_plan_meta(today, "compliance", ["sales"]),
        ),
        Task(
            title=f"Copywriting {today}",
            role="copywriter",
            description=(
                "По content_plan: тексты постов на 3 дня. Заголовок, текст, CTA, хештеги. RU."
            ),
            priority=7,
            metadata=_plan_meta(today, "copy", ["content"]),
        ),
        Task(
            title=f"Director summary {today}",
            role="director",
            description=(
                f"Итог дня в company/memory/reports/daily_{today}.md: "
                "лиды, outreach, маркетинг, клиенты, риски, план на завтра."
            ),
            priority=9,
            metadata=_plan_meta(
                today,
                "director",
                ["leads", "clients", "marketing", "sales", "content", "compliance", "copy"],
                final=True,
            ),
        ),
    ]


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

    for task in build_daily_plan(cfg):
        append_task(task)
    return tasks_for_today_plan()


def format_agent_prompt(employee_role: str, task: Task, cfg: dict) -> str:
    employee = hire(employee_role)
    company_name = cfg["company"]["name"]
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
- Не отправляй сообщения лидам и не публикуй в Telegram — только черновики и файлы.
- Отвечай по-русски, структурированно.
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
) -> int:
    """Returns exit code 0 if all tasks done, 1 if any failed."""
    cfg = load_config()
    for key in cfg["operations"]["memory_dirs"]:
        _memory_path(cfg, key)

    tasks = enqueue_daily_cycle(cfg, force_new=force_new)
    w = workers if workers is not None else default_workers(cfg)

    print(f"\n{cfg['company']['name']} — автономный цикл: {len(tasks)} задач, {w} потоков")
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

    # Автонайм перед параллельным запуском (на случай ad-hoc ролей)
    active = load_tasks()
    task_by_id = {t.id: t for t in active}
    for t in tasks:
        fresh = task_by_id.get(t.id, t)
        if fresh.status in (TaskStatus.DONE, TaskStatus.BLOCKED):
            continue
        ensure_hired_for_task(
            fresh, cfg, interactive=interactive, auto_no=auto_no
        )

    today = today_plan_date()
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
    print("Артефакты: company/memory/reports/")
    return 1 if failed else 0


def run_single_role(
    role: str,
    task_text: str,
    *,
    dry_run: bool = False,
    interactive: bool = False,
    auto_no: bool = False,
) -> None:
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
