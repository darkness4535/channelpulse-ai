"""ChannelPulse AI — daily operational plan."""

from __future__ import annotations

from datetime import date

from company.tasks import Task


def _plan_meta(today: str, stage: str, depends_on: list[str] | None = None, **extra) -> dict:
    meta = {"cycle": "daily", "plan_date": today, "stage": stage}
    if depends_on:
        meta["depends_on"] = depends_on
    meta.update(extra)
    return meta


def build_daily_plan(cfg: dict) -> list[Task]:
    today = date.today().isoformat()
    sales = cfg["sales"]
    return [
        Task(
            title=f"Lead research {today}",
            role="lead_researcher",
            description=(
                f"Найди {sales['daily_lead_target']} потенциальных клиентов по ICP из config. "
                "Для каждого: название, ниша, ссылка на TG/сайт, почему подходят, score 1-10. "
                f"Сохрани JSON в company/memory/leads/leads_{today}.json"
            ),
            priority=1,
            metadata=_plan_meta(today, "leads"),
        ),
        Task(
            title=f"Client delivery check {today}",
            role="account_manager",
            description=(
                "Проверь company/memory/clients/*.json. Для активных клиентов: "
                "статус, что сделано, что нужно сегодня. Если клиентов нет — "
                "создай шаблон example_client.json с демо-брифом кофейни."
            ),
            priority=2,
            metadata=_plan_meta(today, "clients"),
        ),
        Task(
            title=f"Marketing hypotheses {today}",
            role="marketer",
            description=(
                "На основе ICP и услуг из config: 3 рекламные гипотезы "
                "(канал, оффер, UTM, краткий креатив). "
                f"Сохрани company/memory/marketing/hypotheses_{today}.json"
            ),
            priority=3,
            metadata=_plan_meta(today, "marketing"),
        ),
        Task(
            title=f"Qualify leads {today}",
            role="head_of_sales",
            description=(
                f"Прочитай leads_{today}.json. Оставь топ-{sales['daily_outreach_drafts']} "
                "лидов. Для каждого: боль, пакет (starter/growth/premium), "
                "черновик первого сообщения (RU, персонально). "
                f"Сохрани company/memory/outreach/drafts_{today}.json. Не отправлять."
            ),
            priority=4,
            metadata=_plan_meta(today, "sales", ["leads"]),
        ),
        Task(
            title=f"Content pipeline {today}",
            role="content_strategist",
            description=(
                "Для каждого активного клиента: контент-план на 7 дней "
                "в memory/clients/<id>_content_plan.json"
            ),
            priority=5,
            metadata=_plan_meta(today, "content", ["clients"]),
        ),
        Task(
            title=f"Compliance review outreach {today}",
            role="compliance",
            description=(
                f"Проверь drafts_{today}.json: запреты из config, тон. "
                "Одобренные — outreach/approved/approved_{today}.json"
            ),
            priority=6,
            metadata=_plan_meta(today, "compliance", ["sales"]),
        ),
        Task(
            title=f"Copywriting {today}",
            role="copywriter",
            description=(
                "По content_plan: тексты постов на 3 дня. Заголовок, текст, CTA, хештеги. RU."
            ),
            priority=7,
            metadata=_plan_meta(today, "copy", ["content"]),
        ),
        Task(
            title=f"Director summary {today}",
            role="director",
            description=(
                f"Итог дня в company/memory/reports/daily_{today}.md: "
                "лиды, outreach, маркетинг, клиенты, риски, план на завтра."
            ),
            priority=9,
            metadata=_plan_meta(
                today,
                "director",
                ["leads", "clients", "marketing", "sales", "content", "compliance", "copy"],
                final=True,
            ),
        ),
    ]
