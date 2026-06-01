# ChannelPulse AI — стратегия Q2 2026

> **Владелец:** CEO (Директор) · Issue: CHA-7 · **Ревизия: 1** · Дата: 2026-06-01  
> Горизонт: **30 дней** (1–30 июня 2026) — закрывающий месяц Q2.

## North Star

**Первый платящий клиент на пакете Growth + воспроизводимая воронка «лид → одобренный outreach → созвон → контракт».**

| Метрика | Сейчас (baseline) | Цель к 30.06 |
|---------|-------------------|--------------|
| Квалифицированные лиды / неделя | ~2 (mock) | ≥ 15 реальных |
| Approved outreach / неделя | 1 черновик | ≥ 9 (3/день × 3 недели активной работы) |
| Активные платящие клиенты | 0 | ≥ 1 на Growth |
| Демо-клиенты с полным delivery | 1 (example) | ≥ 2 (1 demo + 1 pilot) |

## Контекст

- **Продукт:** ведение и рост Telegram-каналов для SMB (кофейни, салоны, клиники, B2B).
- **ICP:** малый бизнес с слабым или редким TG-контентом, активный в других соцсетях.
- **Пакеты:** Starter (25k ₽), Growth (45k ₽), Premium (75k ₽) — приоритет **Growth** для local_food.
- **Ограничения board:** outreach и публикации только после human approval; без спама и ложных обещаний.
- **Техническое состояние:** daily cycle работает в mock; Paperclip API недоступен из cloud (`127.0.0.1:3100`).

## Стратегические приоритеты Q2 (июнь)

1. **Revenue** — конвертировать pipeline в первую выручку, не расширять продуктовую линейку.
2. **Repeatability** — стабильный daily cycle с реальными (не mock) артефактами в `company/memory/`.
3. **Proof** — кейс/отзыв от pilot-клиента для GTM Q3.
4. **Focus** — один ICP-сегмент (local_food) до первого контракта; остальные сегменты — backlog.

## Вехи на 30 дней

### Неделя 1 · 1–7 июня — «Pipeline Ready»

| Владелец | Результат | DoD |
|----------|-----------|-----|
| CMO | Уточнённый ICP one-pager + 3 outreach-шаблона (RU) | `company/memory/marketing/icp-onepager.md`, `company/memory/outreach/templates/` |
| CTO | Стабильный daily cycle без mock-fallback на ключевых ролях | `run_company --cycle daily` завершается; отчёт в `reports/daily_{date}.md` |
| Lead Researcher | ≥ 25 лидов в pipeline (5/день × 5 дней) | `leads/leads_{date}.json` с score ≥ 6 |
| Head of Sales | ≥ 15 квалифицированных черновиков | `outreach/drafts_{date}.json` |
| Compliance | ≥ 10 approved | `outreach/approved/approved_{date}.json` |

**Gate недели 1:** board approval на отправку ≥ 3 лучших outreach (приоритет: «Кофейня Зерно»).

### Неделя 2 · 8–14 июня — «First Conversations»

| Владелец | Результат | DoD |
|----------|-----------|-----|
| Head of Sales | ≥ 5 диалогов / follow-up sequences | CRM-статус в `memory/leads/` или `clients/` |
| CMO | Landing one-pager + pricing FAQ для созвона | `company/memory/marketing/sales-enablement.md` |
| Content Strategist | Pilot offer: «7 дней контента бесплатно» для топ-лида | `clients/{lead_id}_pilot_plan.json` |
| Director | Weekly review #1 | `company/memory/reports/weekly_2026-06-07.md` |

**Gate недели 2:** ≥ 2 созвона назначены; ≥ 1 лид в статусе `negotiation`.

### Неделя 3 · 15–21 июня — «Pilot Delivery»

| Владелец | Результат | DoD |
|----------|-----------|-----|
| Account Manager | 1 pilot-клиент onboarded | `clients/{id}.json` status=`pilot` |
| Content + Copy | 7-дневный контент-план + 4 готовых поста | `*_content_plan.json`, `*_posts.json` |
| UXDesigner | Шаблон welcome-pack / brand guidelines для клиента | `company/docs/client-welcome-template.md` |
| Analyst | Воронка: лиды → drafts → approved → replies → meetings | `company/memory/reports/funnel_2026-06-21.json` |

**Gate недели 3:** pilot delivery принят board; NPS-опрос (качественный) у pilot-клиента.

### Неделя 4 · 22–30 июня — «First Revenue»

| Владелец | Результат | DoD |
|----------|-----------|-----|
| Head of Sales | ≥ 1 подписанный Growth-контракт | `clients/{id}.json` status=`active`, package=`growth` |
| CMO | Case study draft (1 страница) | `company/memory/marketing/case-study-draft.md` |
| CTO | Dashboard метрик воронки в `dashboard/` | API endpoint или UI виджет с weekly KPI |
| Director | Q2 retrospective + Q3 draft goals | `company/memory/reports/q2-retrospective_2026-06-30.md` |

**Gate месяца:** ≥ 1 платящий клиент **или** board-решение о pivot с обоснованием метрик.

## Делегирование C-suite

| Роль | Зона ответственности | Child issue |
|------|---------------------|-------------|
| **CMO** | ICP, GTM, outreach-шаблоны, sales enablement, case study | `CHA-7-CMO` |
| **CTO** | Надёжность daily cycle, метрики, infra для cloud-агентов | `CHA-7-CTO` |
| **UXDesigner** | Client welcome-pack, визуальные шаблоны контента | `CHA-7-UX` |

Спецификации child issues: `plans/paperclip-child-issues-CHA-7.json`.

## Критерии приёмки CHA-7 (issue-level)

1. [x] Документ стратегии Q2 с North Star и 4 недельными вехами (этот файл)
2. [x] Child issues специфицированы для CMO, CTO, UXDesigner
3. [ ] Board approval стратегии (`request_confirmation`, key: `confirmation:CHA-7:plan:1`)
4. [ ] Child issues созданы в Paperclip и назначены исполнителям
5. [ ] Неделя 1 запущена (pipeline ready gate)

## Риски и митигация

| Риск | Митигация | Владелец |
|------|-----------|----------|
| Paperclip API недоступен в cloud | Child issues JSON + ручное создание board | CEO → board |
| cursor_cloud: detached HEAD / default branch | Агенты работают на `main`; feature branches через PR | CTO |
| Нет CURSOR_API_KEY | Mock cycle + ручное исполнение ролей через IDE | Director |
| Board не одобряет outreach | Еженедельный batch approval, max 3 сообщения | CEO |

## Следующие шаги CEO

1. **Запросить approval** rev.1 у board (`confirmation:CHA-7:plan:1`)
2. После approval — создать child issues из `plans/paperclip-child-issues-CHA-7.json`
3. Параллельный старт недели 1: CMO (шаблоны) + CTO (cycle) + Lead Research
4. Weekly review каждый понедельник; эскалация на board при блокере > 48ч
