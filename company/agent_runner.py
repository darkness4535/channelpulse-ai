"""Запуск агента: Cursor SDK или локальный mock."""

from __future__ import annotations

import os
from pathlib import Path

from company.mock_runner import run_task_mock
from company.tasks import Task, TaskStatus, update_task


def use_mock_mode() -> bool:
    return os.environ.get("COMPANY_MOCK", "").strip() in ("1", "true", "yes")


def run_task(
    task: Task,
    prompt: str,
    *,
    model: str,
    cwd: Path,
    api_key: str,
    cfg: dict,
) -> str:
    update_task(task.id, status=TaskStatus.IN_PROGRESS)

    if use_mock_mode():
        text = run_task_mock(task, cfg)
        update_task(task.id, status=TaskStatus.DONE)
        return text

    if not api_key:
        update_task(task.id, status=TaskStatus.BLOCKED)
        raise RuntimeError(
            "CURSOR_API_KEY не задан. Добавьте ключ в .env или запустите с --mock"
        )

    from cursor_sdk import Agent, AgentOptions, CursorAgentError, LocalAgentOptions

    try:
        result = Agent.prompt(
            prompt,
            AgentOptions(
                api_key=api_key,
                model=model,
                local=LocalAgentOptions(cwd=str(cwd)),
            ),
        )
    except CursorAgentError as err:
        update_task(task.id, status=TaskStatus.BLOCKED)
        raise RuntimeError(f"Agent startup failed: {err.message}") from err

    if result.status == "error":
        update_task(task.id, status=TaskStatus.BLOCKED)
        raise RuntimeError(f"Run failed: {getattr(result, 'id', '?')}")

    text = getattr(result, "result", None) or str(result)
    update_task(task.id, status=TaskStatus.DONE)
    return text
