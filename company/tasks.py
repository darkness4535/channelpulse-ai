"""JSONL task queue for the company."""

from __future__ import annotations

import json
import threading
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Iterator

from company.context import get_active_company

_queue_lock = threading.Lock()


def _queue_path() -> Path:
    return get_active_company().tasks_path


def ensure_queue() -> None:
    path = _queue_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text("", encoding="utf-8")


class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    DONE = "done"
    BLOCKED = "blocked"


@dataclass
class Task:
    title: str
    role: str
    description: str
    priority: int = 5
    status: TaskStatus = TaskStatus.PENDING
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    metadata: dict = field(default_factory=dict)

    def to_json(self) -> str:
        data = asdict(self)
        data["status"] = self.status.value
        return json.dumps(data, ensure_ascii=False)

    @classmethod
    def from_dict(cls, data: dict) -> Task:
        data = dict(data)
        data["status"] = TaskStatus(data["status"])
        return cls(**data)


def append_task(task: Task) -> Task:
    ensure_queue()
    with _queue_lock:
        with _queue_path().open("a", encoding="utf-8") as f:
            f.write(task.to_json() + "\n")
    return task


def load_tasks(status: TaskStatus | None = None) -> list[Task]:
    ensure_queue()
    tasks: list[Task] = []
    for line in _queue_path().read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        task = Task.from_dict(json.loads(line))
        if status is None or task.status == status:
            tasks.append(task)
    return tasks


def iter_pending() -> Iterator[Task]:
    for task in sorted(load_tasks(TaskStatus.PENDING), key=lambda t: t.priority):
        yield task


def update_task(task_id: str, **changes) -> bool:
    with _queue_lock:
        tasks = load_tasks()
        updated = False
        lines: list[str] = []
        for task in tasks:
            if task.id == task_id:
                for key, value in changes.items():
                    if key == "status" and isinstance(value, str):
                        value = TaskStatus(value)
                    setattr(task, key, value)
                updated = True
            lines.append(task.to_json())
        if updated:
            _queue_path().write_text(
                "\n".join(lines) + ("\n" if lines else ""), encoding="utf-8"
            )
    return updated


def reload_task(task_id: str) -> Task | None:
    for task in load_tasks():
        if task.id == task_id:
            return task
    return None


def supersede_daily_plans(plan_date: str, *, include_today: bool = False) -> int:
    """Помечает дневные задачи как заменённые новым планом."""
    count = 0
    with _queue_lock:
        tasks = load_tasks()
        lines: list[str] = []
        for task in tasks:
            if task.metadata.get("cycle") != "daily":
                lines.append(task.to_json())
                continue
            td = task.metadata.get("plan_date")
            stale = td != plan_date if td else True
            if include_today and td == plan_date:
                stale = True
            if stale and task.status in (
                TaskStatus.PENDING,
                TaskStatus.IN_PROGRESS,
            ):
                task.status = TaskStatus.BLOCKED
                task.metadata = {
                    **task.metadata,
                    "blocked_reason": "superseded",
                }
                count += 1
            lines.append(task.to_json())
        _queue_path().write_text(
            "\n".join(lines) + ("\n" if lines else ""), encoding="utf-8"
        )
    return count
