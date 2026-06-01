"""LocalMaps SEO Audit — daily operational plan."""

from __future__ import annotations

from datetime import date

from company.context import get_active_company
from company.tasks import Task


def _plan_meta(today: str, stage: str, depends_on: list[str] | None = None, **extra) -> dict:
    meta = {"cycle": "daily", "plan_date": today, "stage": stage}
    if depends_on:
        meta["depends_on"] = depends_on
    meta.update(extra)
    return meta


def _mem(key: str) -> str:
    ctx = get_active_company()
    cfg = ctx.load_config()
    return cfg["operations"]["memory_dirs"][key]


def build_daily_plan(cfg: dict) -> list[Task]:
    today = date.today().isoformat()
    sales = cfg["sales"]
    leads_dir = _mem("leads")
    audits_dir = _mem("audits")
    outreach_dir = _mem("outreach")
    marketing_dir = _mem("marketing")
    reports_dir = _mem("reports")

    return [
        Task(
            title=f"Maps lead research {today}",
            role="lead_researcher",
            description=(
                f"Найди {sales['daily_lead_target']} локальных компаний EU/US с Google Business Profile "
                "по ICP из config. Для каждого: lead_id, name, segment, city, country, "
                "maps_url, rating, review_count, website, contact_email (если публично), "
                "pain_signals[], score 1-10, source (manual research / public directory). "
                f"Сохрани {leads_dir}/leads_{today}.json. "
                "Не скрейпить Maps в нарушение ToS — только публичные данные."
            ),
            priority=1,
            metadata=_plan_meta(today, "leads"),
        ),
        Task(
            title=f"GBP SEO audit {today}",
            role="seo_auditor",
            description=(
                f"Прочитай {leads_dir}/leads_{today}.json. Для каждого лида с score >= 6: "
                "проведи чеклист GBP (15 пунктов), рассчитай visibility_score 0-100, "
                "выдели 3 quick wins. Сохрани JSON в "
                f"{audits_dir}/{{lead_id}}.json и PDF через audit pipeline. "
                "Используй company.audit для генерации PDF."
            ),
            priority=2,
            metadata=_plan_meta(today, "audits", ["leads"]),
        ),
        Task(
            title=f"Marketing hypotheses {today}",
            role="marketer",
            description=(
                "3 GTM-гипотезы для EU/US (канал, оффер mini_audit_pdf, UTM, креатив). "
                f"Сохрани {marketing_dir}/hypotheses_{today}.json"
            ),
            priority=3,
            metadata=_plan_meta(today, "marketing"),
        ),
        Task(
            title=f"Outreach drafts {today}",
            role="head_of_sales",
            description=(
                f"Топ-{sales['daily_outreach_drafts']} лидов с готовым PDF-аудитом. "
                "Для каждого: channel (email/telegram_dm/whatsapp), offer (mini/full/monthly), "
                "персональный черновик EN (EU/US), ссылка на PDF. "
                f"Сохрани {outreach_dir}/drafts_{today}.json. Не отправлять."
            ),
            priority=4,
            metadata=_plan_meta(today, "sales", ["leads", "audits"]),
        ),
        Task(
            title=f"Compliance review {today}",
            role="compliance",
            description=(
                f"Проверь {outreach_dir}/drafts_{today}.json: GDPR/CAN-SPAM, opt-out, "
                "запреты из config, персонализация. "
                f"Одобренные → {outreach_dir}/approved/approved_{today}.json"
            ),
            priority=5,
            metadata=_plan_meta(today, "compliance", ["sales"]),
        ),
        Task(
            title=f"Funnel metrics {today}",
            role="analyst",
            description=(
                f"Сводка воронки: leads → audits → drafts → approved. "
                f"Сохрани {reports_dir}/metrics_{today}.json"
            ),
            priority=6,
            metadata=_plan_meta(today, "metrics", ["leads", "audits", "compliance"]),
        ),
        Task(
            title=f"Director summary {today}",
            role="director",
            description=(
                f"Итог дня в {reports_dir}/daily_{today}.md: "
                "лиды, аудиты, outreach, метрики, риски, план на завтра."
            ),
            priority=9,
            metadata=_plan_meta(
                today,
                "director",
                ["leads", "audits", "marketing", "sales", "compliance", "metrics"],
                final=True,
            ),
        ),
    ]
