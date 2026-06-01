"""Найм: автономный (по умолчанию) или с подтверждением владельца."""

from __future__ import annotations

import os
from collections import defaultdict

from company.registry import Employee, hire, role_display_name
from company.staff import hire_to_staff, is_hired, list_hired_ids
from company.tasks import Task, TaskStatus, update_task


def is_autonomous(cfg: dict | None = None) -> bool:
    env = os.environ.get("COMPANY_AUTONOMOUS", "").strip().lower()
    if env in ("0", "false", "no"):
        return False
    if env in ("1", "true", "yes"):
        return True
    if cfg:
        return bool(cfg.get("autonomous", {}).get("auto_hire", True))
    return True


def role_pitch(role_id: str, cfg: dict) -> str:
    pitches = cfg.get("hiring", {}).get("role_pitches", {})
    if role_id in pitches:
        return pitches[role_id]
    emp = hire(role_id)
    return (
        f"{emp.name} выполняет задачи по роли «{role_id}». "
        f"Зона: {emp.tools_hint[:200] if emp.tools_hint else 'см. roles/' + role_id + '.md'}"
    )


def ask_owner_to_hire(
    employee: Employee,
    *,
    pitch: str,
    task_titles: list[str],
) -> bool:
    print()
    print("=" * 52)
    print("  ДИРЕКТОР: запрос на найм")
    print("=" * 52)
    print(f"  Сотрудник: {role_display_name(employee.role_id)} ({employee.role_id})")
    print(f"  Зачем:     {pitch}")
    if task_titles:
        print("  Задачи:")
        for title in task_titles[:5]:
            print(f"    — {title}")
    print()

    while True:
        try:
            answer = input("  Нанять на работу? [y/n]: ").strip().lower()
        except EOFError:
            print("\n  Нет ввода. Запустите с автономным режимом (по умолчанию) или --yes.")
            return False
        if answer in ("y", "yes", "д", "да"):
            return True
        if answer in ("n", "no", "н", "нет"):
            return False
        print("  Введите y (да) или n (нет)")


def auto_hire_role(role_id: str, *, quiet: bool = False) -> None:
    if is_hired(role_id):
        return
    hire_to_staff(role_id)
    if not quiet:
        emp = hire(role_id)
        print(f"  [автонайм] {emp.hire_label}")


def ensure_hired_for_role(
    role_id: str,
    cfg: dict,
    *,
    task_titles: list[str] | None = None,
    interactive: bool = False,
    auto_no: bool = False,
) -> bool:
    if is_hired(role_id):
        return True
    if auto_no:
        return False
    if is_autonomous(cfg) and not interactive:
        auto_hire_role(role_id)
        return True

    employee = hire(role_id)
    pitch = role_pitch(role_id, cfg)
    approved = ask_owner_to_hire(employee, pitch=pitch, task_titles=task_titles or [])
    if approved:
        hire_to_staff(role_id)
        print(f"  ✓ {employee.hire_label} принят в штат.\n")
        return True
    print(f"  ✗ {employee.hire_label} не нанят.\n")
    return False


def prepare_team_for_cycle(
    tasks: list[Task],
    cfg: dict,
    *,
    interactive: bool = False,
    auto_no: bool = False,
    dry_run: bool = False,
) -> set[str]:
    """Нанимает всех нужных для цикла (автономно — без вопросов)."""
    pending = [t for t in tasks if t.status != TaskStatus.DONE]
    by_role: dict[str, list[Task]] = defaultdict(list)
    for task in pending:
        if task.role == "director":
            continue
        if not is_hired(task.role):
            by_role[task.role].append(task)

    if not by_role:
        return set(list_hired_ids())

    if dry_run:
        return set(list_hired_ids())

    autonomous = is_autonomous(cfg) and not interactive

    if autonomous:
        print("Автонайм команды:")
        for role_id in sorted(by_role):
            auto_hire_role(role_id, quiet=False)
        return set(list_hired_ids())

    print()
    print("─" * 52)
    print("  ДИРЕКТОР: для плана нужны сотрудники")
    print("─" * 52)
    for role_id in sorted(by_role):
        print(f"  • {role_display_name(role_id)}")

    approved_roles: set[str] = set(list_hired_ids())
    for role_id, role_tasks in sorted(by_role.items()):
        titles = [t.title for t in role_tasks]
        if ensure_hired_for_role(
            role_id, cfg, task_titles=titles, interactive=True, auto_no=auto_no
        ):
            approved_roles.add(role_id)
        else:
            for task in role_tasks:
                update_task(
                    task.id,
                    status=TaskStatus.BLOCKED,
                    metadata={
                        **task.metadata,
                        "blocked_reason": "not_hired",
                        "role": role_id,
                    },
                )

    return approved_roles


def ensure_hired_for_task(
    task: Task, cfg: dict, *, interactive: bool = False, auto_no: bool = False
) -> bool:
    if is_hired(task.role):
        return True
    if not ensure_hired_for_role(
        task.role,
        cfg,
        task_titles=[task.title],
        interactive=interactive,
        auto_no=auto_no,
    ):
        update_task(
            task.id,
            status=TaskStatus.BLOCKED,
            metadata={**task.metadata, "blocked_reason": "not_hired"},
        )
        return False
    return True
