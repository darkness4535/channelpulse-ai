"""Указания владельца: что делать и чего не делать."""

from __future__ import annotations

import json
import threading
from datetime import datetime, timezone
from pathlib import Path

from company.context import get_active_company

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

_LOCALMAPS_DEFAULT = {
    "do": [
        "Фокус на локальном бизнесе EU/US с Google Business Profile",
        "Персонализировать outreach с PDF-аудитом",
        "Соблюдать GDPR (EU) и CAN-SPAM (US)",
    ],
    "dont": [
        "Не отправлять outreach без human approval",
        "Не скрейпить Google Maps в нарушение ToS",
        "Не обещать #1 в Local Pack",
        "Не собирать ПДн без правового основания",
    ],
    "freeform": "",
    "updated_at": None,
}


def _directives_path() -> Path:
    return get_active_company().directives_path


def _default_for_company() -> dict:
    if get_active_company().slug == "localmaps-seo-audit":
        return dict(_LOCALMAPS_DEFAULT)
    return dict(_DEFAULT)


def load_directives() -> dict:
    _ensure()
    with _lock:
        return json.loads(_directives_path().read_text(encoding="utf-8"))


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
        _directives_path().write_text(
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
    path = _directives_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(
            json.dumps(_default_for_company(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
