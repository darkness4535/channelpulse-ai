"""Указания владельца: что делать и чего не делать."""

from __future__ import annotations

import json
import threading
from datetime import datetime, timezone
from pathlib import Path

DIRECTIVES_PATH = Path(__file__).resolve().parent / "memory" / "directives.json"
_lock = threading.Lock()

_DEFAULT = {
    "do": [
        "Фокус на малом бизнесе и Telegram-каналах",
        "Персонализировать outreach, без спама",
    ],
    "dont": [
        "Не отправлять сообщения лидам и не публиковать в Telegram",
        "Не обещать гарантированные продажи",
        "Не собирать персональные данные без согласия",
    ],
    "freeform": "",
    "updated_at": None,
}


def load_directives() -> dict:
    _ensure()
    with _lock:
        return json.loads(DIRECTIVES_PATH.read_text(encoding="utf-8"))


def save_directives(
    *,
    do: list[str] | None = None,
    dont: list[str] | None = None,
    freeform: str | None = None,
) -> dict:
    current = load_directives()
    if do is not None:
        current["do"] = [s.strip() for s in do if s.strip()]
    if dont is not None:
        current["dont"] = [s.strip() for s in dont if s.strip()]
    if freeform is not None:
        current["freeform"] = freeform.strip()
    current["updated_at"] = datetime.now(timezone.utc).isoformat()
    with _lock:
        DIRECTIVES_PATH.write_text(
            json.dumps(current, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    return current


def format_for_prompt() -> str:
    d = load_directives()
    lines = ["# Указания владельца (обязательны)"]
    if d.get("freeform"):
        lines.append(d["freeform"])
    if d.get("do"):
        lines.append("\n## Делать")
        lines.extend(f"- {x}" for x in d["do"])
    if d.get("dont"):
        lines.append("\n## Не делать")
        lines.extend(f"- {x}" for x in d["dont"])
    return "\n".join(lines)


def _ensure() -> None:
    DIRECTIVES_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not DIRECTIVES_PATH.exists():
        DIRECTIVES_PATH.write_text(
            json.dumps(_DEFAULT, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
