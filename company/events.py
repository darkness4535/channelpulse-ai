"""Журнал событий для панели управления."""

from __future__ import annotations

import json
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

EVENTS_PATH = Path(__file__).resolve().parent / "memory" / "events.jsonl"
_lock = threading.Lock()
_MAX_READ = 500


def log_event(event_type: str, **payload: Any) -> dict:
    record = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "type": event_type,
        **payload,
    }
    EVENTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with _lock:
        with EVENTS_PATH.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    return record


def load_events(limit: int = 100) -> list[dict]:
    if not EVENTS_PATH.exists():
        return []
    lines = EVENTS_PATH.read_text(encoding="utf-8").splitlines()
    items: list[dict] = []
    for line in lines[-_MAX_READ:]:
        line = line.strip()
        if line:
            items.append(json.loads(line))
    return items[-limit:]
