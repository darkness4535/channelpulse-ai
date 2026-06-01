"""Multi-company runtime: config, memory paths, roles."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SLUG = "channelpulse"
COMPANY_ALIASES = {
    "": DEFAULT_SLUG,
    "default": DEFAULT_SLUG,
    "channelpulse": DEFAULT_SLUG,
    "channelpulse-ai": DEFAULT_SLUG,
}


@dataclass(frozen=True)
class CompanyContext:
    slug: str
    config_path: Path
    roles_dir: Path
    memory_root: Path
    tasks_path: Path
    staff_path: Path
    directives_path: Path
    project_root: Path = PROJECT_ROOT

    def load_config(self) -> dict:
        with self.config_path.open(encoding="utf-8") as f:
            return yaml.safe_load(f)

    def memory_path(self, key: str, cfg: dict | None = None) -> Path:
        if cfg is None:
            cfg = self.load_config()
        rel = cfg["operations"]["memory_dirs"][key]
        p = self.project_root / rel
        p.mkdir(parents=True, exist_ok=True)
        return p


def normalize_slug(slug: str | None) -> str:
    raw = (slug or os.environ.get("COMPANY_SLUG") or DEFAULT_SLUG).strip().lower()
    return COMPANY_ALIASES.get(raw, raw)


def resolve_company(slug: str | None = None) -> CompanyContext:
    normalized = normalize_slug(slug)
    if normalized == DEFAULT_SLUG:
        base = PROJECT_ROOT / "company"
        memory = base / "memory"
        return CompanyContext(
            slug=DEFAULT_SLUG,
            config_path=base / "config.yaml",
            roles_dir=PROJECT_ROOT / "roles",
            memory_root=memory,
            tasks_path=memory / "tasks.jsonl",
            staff_path=memory / "staff" / "hired.json",
            directives_path=memory / "directives.json",
        )

    base = PROJECT_ROOT / "companies" / normalized
    if not (base / "config.yaml").exists():
        available = list_companies()
        raise FileNotFoundError(
            f"Company «{normalized}» not found. Available: {', '.join(available)}"
        )

    memory = base / "memory"
    roles = base / "roles" if (base / "roles").is_dir() else PROJECT_ROOT / "roles"
    return CompanyContext(
        slug=normalized,
        config_path=base / "config.yaml",
        roles_dir=roles,
        memory_root=memory,
        tasks_path=memory / "tasks.jsonl",
        staff_path=memory / "staff" / "hired.json",
        directives_path=memory / "directives.json",
    )


def list_companies() -> list[str]:
    slugs = [DEFAULT_SLUG]
    companies_dir = PROJECT_ROOT / "companies"
    if companies_dir.is_dir():
        for path in sorted(companies_dir.iterdir()):
            if path.is_dir() and (path / "config.yaml").exists():
                slugs.append(path.name)
    return slugs


_active: CompanyContext | None = None


def get_active_company() -> CompanyContext:
    global _active
    if _active is None:
        _active = resolve_company()
    return _active


def set_active_company(slug: str | None) -> CompanyContext:
    global _active
    _active = resolve_company(slug)
    os.environ["COMPANY_SLUG"] = _active.slug
    return _active
