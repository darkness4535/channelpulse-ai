"""Состояние фонового цикла для панели."""

from __future__ import annotations

import json
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

STATE_PATH = Path(__file__).resolve().parent / "memory" / "runtime_state.json"
_lock = threading.Lock()


def _default() -> dict:
    return {
        "status": "idle",
        "message": "Ожидание",
        "wave": 0,
        "waves_total": 0,
        "mock": False,
        "started_at": None,
        "finished_at": None,
        "last_error": None,
    }


def read_state() -> dict:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not STATE_PATH.exists():
        return _default()
    with _lock:
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))


def write_state(**updates: Any) -> dict:
    state = read_state()
    state.update(updates)
    with _lock:
        STATE_PATH.write_text(
            json.dumps(state, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    return state


def set_idle(message: str = "Ожидание") -> dict:
    return write_state(
        status="idle",
        message=message,
        wave=0,
        finished_at=datetime.now(timezone.utc).isoformat(),
    )


def set_running(message: str, *, mock: bool, waves_total: int = 0) -> dict:
    return write_state(
        status="running",
        message=message,
        mock=mock,
        waves_total=waves_total,
        wave=0,
        started_at=datetime.now(timezone.utc).isoformat(),
        finished_at=None,
        last_error=None,
    )
