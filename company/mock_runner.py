"""Локальное выполнение задач без Cursor API — для проверки пайплайна."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from company.audit import audit_leads_file
from company.context import get_active_company
from company.tasks import Task

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _memory_dir(key: str, cfg: dict) -> Path:
    rel = cfg["operations"]["memory_dirs"][key]
    return PROJECT_ROOT / rel


def _write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _run_localmaps_mock(task: Task, cfg: dict, today: str, company: str) -> str:
    leads_dir = _memory_dir("leads", cfg)
    audits_dir = _memory_dir("audits", cfg)
    outreach_dir = _memory_dir("outreach", cfg)
    marketing_dir = _memory_dir("marketing", cfg)
    reports_dir = _memory_dir("reports", cfg)
    role = task.role

    if role == "lead_researcher":
        path = leads_dir / f"leads_{today}.json"
        data = {
            "date": today,
            "source": "mock",
            "region": "EU/US",
            "leads": [
                {
                    "lead_id": "brew-corner-berlin",
                    "name": "Brew Corner Coffee",
                    "segment": "local_food",
                    "city": "Berlin",
                    "country": "DE",
                    "maps_url": "https://maps.google.com/?q=Brew+Corner+Coffee+Berlin",
                    "rating": 3.8,
                    "review_count": 12,
                    "website": "https://example.com/brew-corner",
                    "contact_email": "hello@brew-corner.example",
                    "pain_signals": ["few photos", "empty description", "no posts"],
                    "score": 8,
                    "source": "public directory",
                },
                {
                    "lead_id": "glow-studio-austin",
                    "name": "Glow Studio Spa",
                    "segment": "beauty_wellness",
                    "city": "Austin",
                    "country": "US",
                    "maps_url": "https://maps.google.com/?q=Glow+Studio+Austin",
                    "rating": 4.1,
                    "review_count": 34,
                    "website": "https://example.com/glow-studio",
                    "pain_signals": ["no responses", "no social"],
                    "score": 7,
                    "source": "manual research",
                },
                {
                    "lead_id": "quick-fix-plumbing-dallas",
                    "name": "QuickFix Plumbing",
                    "segment": "home_services",
                    "city": "Dallas",
                    "country": "US",
                    "maps_url": "https://maps.google.com/?q=QuickFix+Plumbing+Dallas",
                    "rating": 4.5,
                    "review_count": 89,
                    "website": "https://example.com/quickfix",
                    "score": 5,
                    "source": "manual research",
                },
            ],
        }
        _write_json(path, data)
        return f"[MOCK] Maps leads: {path}"

    if role == "seo_auditor":
        leads_path = leads_dir / f"leads_{today}.json"
        if not leads_path.exists():
            return "[MOCK] BLOCKED: leads file missing"
        audits = audit_leads_file(
            leads_path,
            audits_dir,
            company_name=company,
        )
        return f"[MOCK] GBP audits + PDF: {len(audits)} files in {audits_dir}"

    if role == "head_of_sales":
        path = outreach_dir / f"drafts_{today}.json"
        data = {
            "date": today,
            "status": "draft",
            "items": [
                {
                    "lead_id": "brew-corner-berlin",
                    "lead": "Brew Corner Coffee",
                    "channel": "email",
                    "offer": "mini_audit_pdf",
                    "language": "en",
                    "pdf_path": str(audits_dir / "brew-corner-berlin.pdf"),
                    "message": (
                        "Hi — I put together a free Google Maps visibility report for "
                        "Brew Corner (score 47/100). Three quick wins inside. "
                        "Want the full 90-day roadmap?"
                    ),
                },
                {
                    "lead_id": "glow-studio-austin",
                    "lead": "Glow Studio Spa",
                    "channel": "whatsapp",
                    "offer": "mini_audit_pdf",
                    "language": "en",
                    "pdf_path": str(audits_dir / "glow-studio-austin.pdf"),
                    "message": (
                        "Hi Glow Studio — your Maps profile has room to grow. "
                        "Attached a mini-audit PDF with 3 fixes. Reply STOP to opt out."
                    ),
                },
            ],
        }
        _write_json(path, data)
        return f"[MOCK] Outreach drafts: {path}"

    if role == "compliance":
        drafts = outreach_dir / f"drafts_{today}.json"
        approved_dir = outreach_dir / "approved"
        approved_dir.mkdir(parents=True, exist_ok=True)
        out = approved_dir / f"approved_{today}.json"
        if drafts.exists():
            payload = json.loads(drafts.read_text(encoding="utf-8"))
            payload["compliance"] = "approved"
            payload["checks"] = ["gdpr_lawful_basis", "can_spam_opt_out", "personalized"]
            _write_json(out, payload)
        else:
            _write_json(out, {"date": today, "compliance": "approved", "items": []})
        return f"[MOCK] Compliance OK: {out}"

    if role == "marketer":
        path = marketing_dir / f"hypotheses_{today}.json"
        _write_json(
            path,
            {
                "date": today,
                "hypotheses": [
                    {
                        "channel": "cold_email_eu_food",
                        "offer": "mini_audit_pdf",
                        "utm": "lm_email_food_de",
                        "note": "Berlin/Munich coffee shops, EN+DE subject lines",
                    },
                    {
                        "channel": "whatsapp_us_home_services",
                        "offer": "full_audit",
                        "utm": "lm_wa_home_us",
                        "note": "Dallas/Houston plumbers, short video + PDF",
                    },
                    {
                        "channel": "telegram_beauty_eu",
                        "offer": "monthly_growth",
                        "utm": "lm_tg_beauty_eu",
                        "note": "Salons with IG but weak Maps",
                    },
                ],
            },
        )
        return f"[MOCK] Marketing hypotheses: {path}"

    if role == "analyst":
        path = reports_dir / f"metrics_{today}.json"
        n_leads = 0
        n_audits = 0
        leads_path = leads_dir / f"leads_{today}.json"
        if leads_path.exists():
            n_leads = len(json.loads(leads_path.read_text())["leads"])
        if audits_dir.is_dir():
            n_audits = len(list(audits_dir.glob("*.json")))
        _write_json(
            path,
            {
                "date": today,
                "leads": n_leads,
                "audits": n_audits,
                "drafts": 2,
                "approved": 2,
                "funnel": "leads→audit→draft→approved",
            },
        )
        return f"[MOCK] Metrics: {path}"

    if role == "director":
        path = reports_dir / f"daily_{today}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            f"# Daily Report — {company} — {today}\n\n"
            "## Summary\n"
            "- Leads: 3 (EU/US Maps research)\n"
            "- Audits + PDF: 2 (score >= 6)\n"
            "- Outreach drafts: 2 (email + WhatsApp)\n"
            "- Compliance: approved\n\n"
            "## Risks\n"
            "- None in mock mode\n\n"
            "## Tomorrow\n"
            "- Continue funnel, test real agent cycle\n",
            encoding="utf-8",
        )
        return f"[MOCK] Director report: {path}"

    return _run_channelpulse_fallback(task, cfg, today, company)


def _run_channelpulse_fallback(task: Task, cfg: dict, today: str, company: str) -> str:
    role = task.role
    memory = PROJECT_ROOT / "company" / "memory"

    if role == "lead_researcher":
        path = memory / "leads" / f"leads_{today}.json"
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
            ],
        }
        _write_json(path, data)
        return f"[MOCK] Лиды записаны: {path}"

    if role == "head_of_sales":
        path = memory / "outreach" / f"drafts_{today}.json"
        _write_json(
            path,
            {
                "date": today,
                "status": "draft",
                "items": [{"lead": "Кофейня «Зерно»", "package": "starter", "message": "..."}],
            },
        )
        return f"[MOCK] Черновики outreach: {path}"

    if role == "compliance":
        drafts = memory / "outreach" / f"drafts_{today}.json"
        approved_dir = memory / "outreach" / "approved"
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
        clients = memory / "clients"
        clients.mkdir(parents=True, exist_ok=True)
        path = clients / "example_client.json"
        _write_json(
            path,
            {"id": "example_client", "name": "Кофейня «Зерно»", "status": "active"},
        )
        return f"[MOCK] Клиент: {path}"

    if role == "content_strategist":
        path = memory / "clients" / "example_client_content_plan.json"
        _write_json(path, {"client_id": "example_client", "days": [{"day": 1, "topic": "..."}]})
        return f"[MOCK] Контент-план: {path}"

    if role == "copywriter":
        path = memory / "clients" / "example_client_posts.json"
        _write_json(path, {"posts": [{"title": "Test", "body": "..."}]})
        return f"[MOCK] Посты: {path}"

    if role == "marketer":
        path = memory / "marketing" / f"hypotheses_{today}.json"
        _write_json(path, {"date": today, "hypotheses": [{"channel": "telegram_ads"}]})
        return f"[MOCK] Маркeting: {path}"

    if role == "analyst":
        path = memory / "reports" / f"metrics_{today}.json"
        _write_json(path, {"date": today, "leads": 1})
        return f"[MOCK] Метрики: {path}"

    if role == "director":
        path = memory / "reports" / f"daily_{today}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"# Отчёт {company} — {today}\n", encoding="utf-8")
        return f"[MOCK] Отчёт директора: {path}"

    decisions = memory / "decisions"
    decisions.mkdir(parents=True, exist_ok=True)
    note = decisions / f"mock_{task.id[:8]}.txt"
    note.write_text(f"Mock run: {task.title}\n", encoding="utf-8")
    return f"[MOCK] Задача «{task.title}» — заметка в {note}"


def run_task_mock(task: Task, cfg: dict) -> str:
    today = date.today().isoformat()
    company = cfg["company"]["name"]
    ctx = get_active_company()

    if ctx.slug == "localmaps-seo-audit":
        return _run_localmaps_mock(task, cfg, today, company)

    return _run_channelpulse_fallback(task, cfg, today, company)
