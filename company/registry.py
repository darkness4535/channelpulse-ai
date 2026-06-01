"""Role registry — «найм» сотрудников по id роли."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from company.context import get_active_company

DEFAULT_ROLES_DIR = Path(__file__).resolve().parent.parent / "roles"


def _roles_dir() -> Path:
    return get_active_company().roles_dir


@dataclass(frozen=True)
class Employee:
    role_id: str
    name: str
    system_prompt: str
    tools_hint: str

    @property
    def hire_label(self) -> str:
        return f"{self.name} ({self.role_id})"


def discover_role_ids() -> list[str]:
    roles_dir = _roles_dir()
    if not roles_dir.is_dir():
        return []
    return sorted(p.stem for p in roles_dir.glob("*.md"))


def role_display_name(role_id: str) -> str:
    titles = {
        "director": "Генеральный директор",
        "head_of_sales": "Руководитель продаж",
        "lead_researcher": "Исследователь лидов",
        "account_manager": "Аккаунт-менеджер",
        "content_strategist": "Контент-стратег",
        "copywriter": "Копирайтер",
        "analyst": "Аналитик",
        "compliance": "Комплаенс",
        "marketer": "Маркетолог",
        "seo_auditor": "SEO-аудитор GBP",
    }
    return titles.get(role_id, role_id.replace("_", " ").title())


def _read_role(role_id: str) -> str:
    path = _roles_dir() / f"{role_id}.md"
    if not path.exists():
        raise KeyError(f"Unknown role: {role_id}")
    return path.read_text(encoding="utf-8")


def hire(role_id: str) -> Employee:
    available = discover_role_ids()
    if role_id not in available:
        raise KeyError(f"Unknown role: {role_id}. Available: {', '.join(available)}")

    raw = _read_role(role_id)
    name = role_display_name(role_id)
    tools_hint = ""
    if "## Tools" in raw:
        _, tools_block = raw.split("## Tools", 1)
        tools_hint = tools_block.strip().split("\n##")[0].strip()

    return Employee(
        role_id=role_id,
        name=name,
        system_prompt=raw,
        tools_hint=tools_hint,
    )


def list_roles() -> list[str]:
    return discover_role_ids()
