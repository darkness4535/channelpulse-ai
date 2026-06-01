"""Штат компании — кого директор уже нанял с одобрения владельца."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

STAFF_DIR = Path(__file__).resolve().parent / "memory" / "staff"
ROSTER_PATH = STAFF_DIR / "hired.json"

# CEO всегда в системе; найм не спрашиваем.
EXEMPT_FROM_HIRE_GATE = frozenset({"director"})


@dataclass
class HiredMember:
    role_id: str
    hired_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    approved_by: str = "owner"


def _ensure_staff_dir() -> None:
    STAFF_DIR.mkdir(parents=True, exist_ok=True)
    if not ROSTER_PATH.exists():
        ROSTER_PATH.write_text("[]", encoding="utf-8")


def load_roster() -> list[HiredMember]:
    _ensure_staff_dir()
    raw = json.loads(ROSTER_PATH.read_text(encoding="utf-8"))
    return [HiredMember(**item) for item in raw]


def list_hired_ids() -> list[str]:
    return [m.role_id for m in load_roster()]


def is_hired(role_id: str) -> bool:
    if role_id in EXEMPT_FROM_HIRE_GATE:
        return True
    return role_id in list_hired_ids()


def hire_to_staff(role_id: str) -> HiredMember:
    _ensure_staff_dir()
    members = load_roster()
    if any(m.role_id == role_id for m in members):
        return next(m for m in members if m.role_id == role_id)
    member = HiredMember(role_id=role_id)
    members.append(member)
    ROSTER_PATH.write_text(
        json.dumps([asdict(m) for m in members], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return member


def fire_from_staff(role_id: str) -> bool:
    if role_id in EXEMPT_FROM_HIRE_GATE:
        raise ValueError("Нельзя уволить директора")
    members = load_roster()
    kept = [m for m in members if m.role_id != role_id]
    if len(kept) == len(members):
        return False
    ROSTER_PATH.write_text(
        json.dumps([asdict(m) for m in kept], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return True


def print_roster() -> None:
    ids = list_hired_ids()
    if not ids:
        print("Штат пуст. Директор предложит найм при запуске цикла.")
        return
    print("В штате:")
    for role_id in sorted(ids):
        print(f"  • {role_id}")
