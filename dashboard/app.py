"""Панель управления ChannelPulse AI."""

from __future__ import annotations

import os
import sys
from datetime import date
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
load_dotenv(ROOT / ".env")
os.environ.setdefault("COMPANY_AUTONOMOUS", "1")

from company.directives import load_directives, save_directives
from company.events import load_events
from company.orchestrator import load_config, today_plan_date
from company.registry import hire, list_roles, role_display_name
from company.runtime import is_running, start_cycle, start_owner_task
from company import runtime_state
from company.staff import fire_from_staff, hire_to_staff, list_hired_ids
from company.tasks import (
    Task,
    TaskStatus,
    append_task,
    load_tasks,
    reload_task,
    update_task,
)

STATIC = Path(__file__).resolve().parent / "static"

app = FastAPI(title="ChannelPulse AI Panel")
app.mount("/static", StaticFiles(directory=STATIC), name="static")


def task_dict(t: Task) -> dict:
    return {
        "id": t.id,
        "title": t.title,
        "role": t.role,
        "role_label": role_display_name(t.role),
        "description": t.description,
        "status": t.status.value,
        "priority": t.priority,
        "created_at": t.created_at,
        "metadata": t.metadata,
    }


class DirectivesBody(BaseModel):
    do: str = ""
    dont: str = ""
    freeform: str = ""


class NewTaskBody(BaseModel):
    role: str
    description: str
    title: str = "Задача от владельца"


class CycleBody(BaseModel):
    force_new: bool = False
    mock: bool = True


@app.get("/")
def index():
    return FileResponse(STATIC / "index.html")


@app.get("/api/status")
def api_status():
    cfg = load_config()
    state = runtime_state.read_state()
    today = today_plan_date()
    plan = [t for t in load_tasks() if t.metadata.get("plan_date") == today]
    by_status: dict[str, int] = {}
    for t in plan:
        by_status[t.status.value] = by_status.get(t.status.value, 0) + 1

    return {
        "company": cfg["company"],
        "runtime": state,
        "running": is_running(),
        "plan_date": today,
        "staff": [
            {"id": r, "label": role_display_name(r), "hired": True}
            for r in list_hired_ids()
        ],
        "roles_available": [
            {"id": r, "label": role_display_name(r), "hired": r in list_hired_ids()}
            for r in list_roles()
        ],
        "task_counts": by_status,
        "has_api_key": bool(os.environ.get("CURSOR_API_KEY", "").strip()),
        "mock_env": os.environ.get("COMPANY_MOCK", ""),
    }


@app.get("/api/tasks")
def api_tasks(plan_date: str | None = None):
    pd = plan_date or today_plan_date()
    tasks = [
        task_dict(t)
        for t in load_tasks()
        if t.metadata.get("plan_date") == pd or not t.metadata.get("plan_date")
    ]
    tasks.sort(key=lambda x: (x["status"], x["priority"]))
    grouped = {
        "in_progress": [],
        "pending": [],
        "done": [],
        "blocked": [],
        "other": [],
    }
    for t in tasks:
        s = t["status"]
        if s == "in_progress":
            grouped["in_progress"].append(t)
        elif s == "pending":
            grouped["pending"].append(t)
        elif s == "done":
            grouped["done"].append(t)
        elif s == "blocked":
            grouped["blocked"].append(t)
        else:
            grouped["other"].append(t)
    return {"plan_date": pd, "grouped": grouped, "all": tasks}


@app.get("/api/events")
def api_events(limit: int = 80):
    return {"events": load_events(limit)}


@app.get("/api/directives")
def api_get_directives():
    return load_directives()


@app.post("/api/directives")
def api_save_directives(body: DirectivesBody):
    do_list = [ln.strip() for ln in body.do.splitlines() if ln.strip()]
    dont_list = [ln.strip() for ln in body.dont.splitlines() if ln.strip()]
    saved = save_directives(do=do_list, dont=dont_list, freeform=body.freeform)
    from company.events import log_event

    log_event("directives_updated")
    return saved


@app.post("/api/tasks")
def api_new_task(body: NewTaskBody):
    if body.role not in list_roles():
        raise HTTPException(400, f"Неизвестная роль: {body.role}")
    today = today_plan_date()
    task = Task(
        title=body.title,
        role=body.role,
        description=body.description,
        priority=0,
        metadata={
            "cycle": "owner",
            "plan_date": today,
            "stage": f"owner_{body.role}",
            "from_owner": True,
        },
    )
    append_task(task)
    hire_to_staff(body.role)
    from company.events import log_event

    log_event(
        "owner_task",
        task_id=task.id,
        role=body.role,
        title=body.title,
    )
    return task_dict(task)


@app.post("/api/tasks/{task_id}/run")
def api_run_task(task_id: str, mock: bool = True):
    t = reload_task(task_id)
    if not t:
        raise HTTPException(404, "Задача не найдена")
    ok, msg = start_owner_task(task_id, mock=mock)
    if not ok:
        raise HTTPException(409, msg)
    return {"ok": True, "message": msg}


@app.post("/api/tasks/{task_id}/cancel")
def api_cancel_task(task_id: str):
    t = reload_task(task_id)
    if not t:
        raise HTTPException(404, "Задача не найдена")
    meta = {**t.metadata, "blocked_reason": "cancelled_by_owner"}
    ok = update_task(task_id, status=TaskStatus.BLOCKED, metadata=meta)
    if not ok:
        raise HTTPException(404, "Задача не найдена")
    from company.events import log_event

    log_event("task_cancelled", task_id=task_id)
    return {"ok": True}


@app.post("/api/cycle/start")
def api_cycle_start(body: CycleBody):
    ok, msg = start_cycle(force_new=body.force_new, mock=body.mock)
    if not ok:
        raise HTTPException(409, msg)
    return {"ok": True, "message": msg}


@app.post("/api/staff/{role_id}/hire")
def api_hire(role_id: str):
    if role_id not in list_roles():
        raise HTTPException(400, "Неизвестная роль")
    hire_to_staff(role_id)
    return {"ok": True, "role": role_id}


@app.post("/api/staff/{role_id}/fire")
def api_fire(role_id: str):
    if not fire_from_staff(role_id):
        raise HTTPException(404, "Не в штате")
    return {"ok": True}
