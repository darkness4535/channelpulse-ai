"""Параллельное выполнение задач по волнам зависимостей."""

from __future__ import annotations

import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass

from company.agent_runner import run_task
from company.registry import hire
from company.tasks import Task, TaskStatus, reload_task


def default_workers(cfg: dict) -> int:
    env = os.environ.get("COMPANY_PARALLEL_WORKERS", "").strip()
    if env.isdigit():
        return max(1, int(env))
    auto = cfg.get("autonomous", {})
    return max(1, int(auto.get("parallel_workers", 6)))


def compute_waves(tasks: list[Task]) -> list[list[Task]]:
    """Группирует задачи в волны: внутри волны — параллельно, между волнами — по зависимостям."""
    pending = [
        t
        for t in tasks
        if t.status not in (TaskStatus.DONE, TaskStatus.BLOCKED)
    ]
    completed_stages: set[str] = set()
    waves: list[list[Task]] = []

    while pending:
        ready: list[Task] = []
        for task in pending:
            deps = task.metadata.get("depends_on") or []
            if all(dep in completed_stages for dep in deps):
                ready.append(task)

        if not ready:
            stuck = [t.title for t in pending]
            raise RuntimeError(
                f"Зависимости не разрешены для: {', '.join(stuck)}. "
                "Проверьте metadata.depends_on / stage."
            )

        waves.append(sorted(ready, key=lambda t: t.priority))
        for task in ready:
            pending.remove(task)
            stage = task.metadata.get("stage")
            if stage:
                completed_stages.add(stage)

    return waves


@dataclass
class TaskOutcome:
    task_id: str
    title: str
    role: str
    ok: bool
    output: str
    error: str | None = None


def _run_one(
    task: Task,
    *,
    cfg: dict,
    model: str,
    cwd,
    api_key: str,
    format_prompt,
    on_task_start=None,
) -> TaskOutcome:
    fresh = reload_task(task.id) or task
    if fresh.status == TaskStatus.DONE:
        return TaskOutcome(
            task_id=fresh.id,
            title=fresh.title,
            role=fresh.role,
            ok=True,
            output="[skip] already done",
        )
    if fresh.status == TaskStatus.BLOCKED:
        return TaskOutcome(
            task_id=fresh.id,
            title=fresh.title,
            role=fresh.role,
            ok=False,
            output="",
            error="blocked",
        )

    emp = hire(fresh.role)
    prompt = format_prompt(fresh.role, fresh, cfg)
    if on_task_start:
        on_task_start(fresh)
    try:
        text = run_task(
            fresh,
            prompt,
            model=model,
            cwd=cwd,
            api_key=api_key,
            cfg=cfg,
        )
        return TaskOutcome(
            task_id=fresh.id,
            title=fresh.title,
            role=fresh.role,
            ok=True,
            output=text,
        )
    except Exception as err:
        return TaskOutcome(
            task_id=fresh.id,
            title=fresh.title,
            role=fresh.role,
            ok=False,
            output="",
            error=str(err),
        )


def run_tasks_parallel(
    tasks: list[Task],
    *,
    cfg: dict,
    model: str,
    cwd,
    api_key: str,
    format_prompt,
    workers: int,
    on_wave_start=None,
    on_task_start=None,
    on_task_end=None,
) -> list[TaskOutcome]:
    """Выполняет все задачи; возвращает итоги. При ошибке в волне остальные волны всё равно идут."""
    waves = compute_waves(tasks)
    all_outcomes: list[TaskOutcome] = []

    for wave_num, wave in enumerate(waves, start=1):
        if on_wave_start:
            on_wave_start(wave_num, wave)

        with ThreadPoolExecutor(max_workers=min(workers, len(wave))) as pool:
            futures = {
                pool.submit(
                    _run_one,
                    task,
                    cfg=cfg,
                    model=model,
                    cwd=cwd,
                    api_key=api_key,
                    format_prompt=format_prompt,
                    on_task_start=on_task_start,
                ): task
                for task in wave
            }
            for future in as_completed(futures):
                outcome = future.result()
                all_outcomes.append(outcome)
                src = futures[future]
                if on_task_end:
                    on_task_end(src, outcome)
                tag = "OK" if outcome.ok else "FAIL"
                print(f"  [{tag}] {outcome.role}: {outcome.title}")
                if outcome.ok and outcome.output:
                    preview = outcome.output[:500]
                    if len(outcome.output) > 500:
                        preview += "..."
                    print(f"       {preview}")
                elif outcome.error:
                    print(f"       ! {outcome.error}")

    return all_outcomes
