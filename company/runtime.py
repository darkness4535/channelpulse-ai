"""Фоновый запуск цикла компании из панели."""

from __future__ import annotations

import os
import threading

from company import runtime_state
from company.events import log_event

_cycle_thread: threading.Thread | None = None
_start_lock = threading.Lock()


def is_running() -> bool:
    return runtime_state.read_state().get("status") == "running"


def start_cycle(*, force_new: bool = False, mock: bool = False) -> tuple[bool, str]:
    global _cycle_thread

    with _start_lock:
        if is_running():
            return False, "Цикл уже выполняется"

        if mock:
            os.environ["COMPANY_MOCK"] = "1"
        os.environ.setdefault("COMPANY_AUTONOMOUS", "1")

        def _worker() -> None:
            from company.orchestrator import run_daily_cycle

            runtime_state.set_running(
                "Дневной цикл",
                mock=mock,
            )
            log_event("cycle_start", mock=mock, force_new=force_new)
            try:
                code = run_daily_cycle(force_new=force_new, interactive=False)
                msg = "Цикл завершён успешно" if code == 0 else "Цикл завершён с ошибками"
                runtime_state.set_idle(msg)
                log_event("cycle_end", ok=code == 0)
            except Exception as err:
                runtime_state.write_state(
                    status="idle",
                    message="Ошибка",
                    last_error=str(err),
                    finished_at=runtime_state.read_state().get("finished_at"),
                )
                log_event("cycle_error", error=str(err))

        _cycle_thread = threading.Thread(target=_worker, daemon=True, name="company-cycle")
        _cycle_thread.start()
        return True, "Цикл запущен"


def start_owner_task(task_id: str, *, mock: bool = False) -> tuple[bool, str]:
    global _cycle_thread

    with _start_lock:
        if is_running():
            return False, "Дождитесь окончания текущего цикла"

        if mock:
            os.environ["COMPANY_MOCK"] = "1"

        def _worker() -> None:
            from company.orchestrator import (
                _runtime,
                format_agent_prompt,
                load_config,
            )
            from company.agent_runner import run_task, use_mock_mode
            from company.hiring import ensure_hired_for_task
            from company.tasks import reload_task

            runtime_state.set_running("Задача владельца", mock=mock)
            try:
                cfg = load_config()
                task = reload_task(task_id)
                if not task:
                    raise RuntimeError("Задача не найдена")
                if not ensure_hired_for_task(task, cfg):
                    raise RuntimeError("Роль не нанята")
                api_key, cwd, model = _runtime()
                if not api_key and not use_mock_mode():
                    raise RuntimeError("Нужен CURSOR_API_KEY или mock")
                prompt = format_agent_prompt(task.role, task, cfg)
                log_event("task_start", task_id=task.id, role=task.role, title=task.title)
                out = run_task(
                    task, prompt, model=model, cwd=cwd, api_key=api_key, cfg=cfg
                )
                log_event(
                    "task_end",
                    task_id=task.id,
                    role=task.role,
                    title=task.title,
                    ok=True,
                    preview=out[:300],
                )
                runtime_state.set_idle("Задача выполнена")
            except Exception as err:
                runtime_state.write_state(
                    status="idle",
                    message="Ошибка задачи",
                    last_error=str(err),
                )
                log_event("task_error", task_id=task_id, error=str(err))

        _cycle_thread = threading.Thread(
            target=_worker, daemon=True, name="owner-task"
        )
        _cycle_thread.start()
        return True, "Задача запущена"
