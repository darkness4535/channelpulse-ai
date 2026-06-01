"""Локальное выполнение задач без Cursor API — для проверки пайплайна."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from company.tasks import Task

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MEMORY = Path(__file__).resolve().parent / "memory"


def _write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def run_task_mock(task: Task, cfg: dict) -> str:
    today = date.today().isoformat()
    company = cfg["company"]["name"]
    role = task.role

    if role == "lead_researcher":
        path = MEMORY / "leads" / f"leads_{today}.json"
        data = {
            "date": today,
            "source": "mock",
            "leads": [
                {
                    "name": "Кофейня «Зерно»",
                    "niche": "local_food",
                    "telegram": "@zereno_demo",
                    "score": 8,
                    "why": "Редкие посты, активны в VK",
                },
                {
                    "name": "Салон «Блеск»",
                    "niche": "beauty_wellness",
                    "site": "https://example.com/blesk",
                    "score": 7,
                    "why": "Нет Telegram-канала",
                },
            ],
        }
        _write_json(path, data)
        return f"[MOCK] Лиды записаны: {path}"

    if role == "head_of_sales":
        path = MEMORY / "outreach" / f"drafts_{today}.json"
        data = {
            "date": today,
            "status": "draft",
            "items": [
                {
                    "lead": "Кофейня «Зерно»",
                    "package": "starter",
                    "message": "Здравствуйте! Заметили редкие посты в TG — можем вести канал под ключ.",
                }
            ],
        }
        _write_json(path, data)
        return f"[MOCK] Черновики outreach: {path}"

    if role == "compliance":
        drafts = MEMORY / "outreach" / f"drafts_{today}.json"
        approved_dir = MEMORY / "outreach" / "approved"
        approved_dir.mkdir(parents=True, exist_ok=True)
        out = approved_dir / f"approved_{today}.json"
        if drafts.exists():
            payload = json.loads(drafts.read_text(encoding="utf-8"))
            payload["compliance"] = "approved"
            _write_json(out, payload)
        else:
            _write_json(out, {"date": today, "compliance": "approved", "items": []})
        return f"[MOCK] Compliance OK: {out}"

    if role == "account_manager":
        clients = MEMORY / "clients"
        clients.mkdir(parents=True, exist_ok=True)
        path = clients / "example_client.json"
        _write_json(
            path,
            {
                "id": "example_client",
                "name": "Кофейня «Зерно»",
                "status": "active",
                "brief": "Уютная кофейня, аудитория 25-40, tone friendly",
            },
        )
        return f"[MOCK] Клиент: {path}"

    if role == "content_strategist":
        path = MEMORY / "clients" / "example_client_content_plan.json"
        _write_json(
            path,
            {
                "client_id": "example_client",
                "days": [
                    {"day": 1, "rubric": "За кулисами", "topic": "Обжарка зёрен"},
                    {"day": 2, "rubric": "Меню", "topic": "Новый раф"},
                ],
            },
        )
        return f"[MOCK] Контент-план: {path}"

    if role == "copywriter":
        path = MEMORY / "clients" / "example_client_posts.json"
        _write_json(
            path,
            {
                "posts": [
                    {
                        "title": "Свежая обжарка",
                        "body": "Сегодня в печи — бразилия. Заходите на дегустацию ☕",
                        "cta": "Напишите в комментариях любимый сорт",
                    }
                ],
            },
        )
        return f"[MOCK] Посты: {path}"

    if role == "marketer":
        path = MEMORY / "marketing" / f"hypotheses_{today}.json"
        _write_json(
            path,
            {
                "date": today,
                "hypotheses": [
                    {
                        "channel": "telegram_ads",
                        "offer": "starter",
                        "utm": "cp_tg_starter_may",
                        "note": "Тест на локальный food",
                    }
                ],
            },
        )
        return f"[MOCK] Маркетинг: {path}"

    if role == "analyst":
        path = MEMORY / "reports" / f"metrics_{today}.json"
        _write_json(path, {"date": today, "leads": 2, "drafts": 1, "note": "mock metrics"})
        return f"[MOCK] Метрики: {path}"

    if role == "director":
        path = MEMORY / "reports" / f"daily_{today}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            f"# Отчёт {company} — {today}\n\n"
            "- Лиды: mock 2\n"
            "- Outreach: 1 черновик\n"
            "- Клиенты: example_client активен\n"
            "- Риски: нет\n"
            "- Завтра: продолжить воронку\n",
            encoding="utf-8",
        )
        return f"[MOCK] Отчёт директора: {path}"

    decisions = MEMORY / "decisions"
    decisions.mkdir(parents=True, exist_ok=True)
    note = decisions / f"mock_{task.id[:8]}.txt"
    note.write_text(f"Mock run: {task.title}\n{task.description}\n", encoding="utf-8")
    return f"[MOCK] Задача «{task.title}» — заметка в {note}"
