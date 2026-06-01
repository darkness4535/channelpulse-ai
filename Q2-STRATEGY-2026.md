# Стратегия ChannelPulse AI — Q2 2026 (финальный спринт: июнь)

**Владелец:** Директор  
**Дата:** 2026-06-01  
**Статус:** на утверждении совета  
**Связанная задача:** CHA-7

## North Star (Q2)

Построить **повторяемую воронку выручки** для ведения Telegram-каналов SMB: автоматизированный поиск лидов → персональный outreach → пилотные клиенты → удержание.

## Текущая база (на 2026-06-01)

| Область | Состояние |
|---------|-----------|
| Команда | 7 ролей наняты (researcher, sales, compliance, AM, content, copy, marketer) |
| Клиенты | 1 демо-клиент (`example_client`), контент-план и посты готовы |
| Лиды / outreach | Mock-пайплайн работает; 2 лида, 1 черновик outreach |
| Маркетинг | 1 гипотеза (Telegram Ads → starter → local_food) |
| Инфра | Daily cycle в mock; `CURSOR_API_KEY` не подключён |
| Приоритет ниши | `local_food` с активным Instagram (решение D002) |

## KPI Q2 (измеряемые к 30 июня)

1. **25+ квалифицированных лидов** в `company/memory/leads/` (score ≥ 6)
2. **≥ 9 outreach-черновиков**, **≥ 3 approved** compliance
3. **≥ 2 пилотных клиента** на пакете starter или growth (карточки в `clients/`)
4. **≥ 3 протестированные маркетинговые гипотезы** с UTM и результатом
5. **SLA доставки контента:** план 7 дней + 3 поста на клиента без пропусков цикла

## 30-дневный план (1–30 июня 2026)

### Неделя 1 · 1–7 июня — «Фундамент воронки»

| ID | Веха | KPI | Владелец (Paperclip) |
|----|------|-----|----------------------|
| M1.1 | Расширить ICP-лист до 25 лидов | `leads_*.json` ≥ 25 записей | CMO → lead_researcher |
| M1.2 | Outreach: 9 черновиков, 3 approved | `drafts_*` + `approved_*` | CMO → head_of_sales + compliance |
| M1.3 | Запустить 1 marketing experiment | гипотеза + UTM + отчёт | CMO |
| M1.4 | Шаблон онбординга клиента | `_brief_template.json` | UXDesigner |
| M1.5 | KPI на dashboard | leads / outreach / clients на панели | CTO |

**Definition of Done недели:** dashboard показывает KPI; шаблон брифа принят AM; ≥ 15 лидов; ≥ 5 черновиков outreach.

### Неделя 2 · 8–14 июня — «Первые разговоры»

| ID | Веха | KPI | Владелец |
|----|------|-----|----------|
| M2.1 | 5 discovery-call скриптов | `memory/sales/playbooks/` | CMO |
| M2.2 | 2 запланированных созвона (human-approved) | статус в карточке лида | CMO |
| M2.3 | 1 пилотный клиент на starter | `clients/<id>.json` status=pilot | CMO + AM |
| M2.4 | Контент для пилота: план + 8 постов | deliverables starter | content + copy |

**DoD:** 1 paying/pilot client card; outreach conversion draft→approved ≥ 30%.

### Неделя 3 · 15–21 июня — «Продуктизация доставки»

| ID | Веха | KPI | Владелец |
|----|------|-----|----------|
| M3.1 | SOP онбординга (7 шагов) | `memory/operations/onboarding_sop.md` | UXDesigner + CTO |
| M3.2 | Авто-отчёт клиенту (weekly) | шаблон + 1 пример | AM + CTO |
| M3.3 | Второй пилотный клиент | 2 active/pilot clients | CMO |
| M3.4 | Путь mock → real agents | документ + env checklist | CTO |

**DoD:** 2 клиента в pipeline; SOP проходит dry-run на demo_coffee_01.

### Неделя 4 · 22–30 июня — «Масштаб и Q3»

| ID | Веха | KPI | Владелец |
|----|------|-----|----------|
| M4.1 | 3-я гипотеза роста + итоги Q2 | `marketing/q2_retrospective.json` | CMO |
| M4.2 | Referral offer draft | 1-pager для SMB | CMO |
| M4.3 | Q3 draft (июль–сентябрь) | `Q3-STRATEGY-DRAFT.md` | Директор |
| M4.4 | Найм analyst (если KPI tracking bottleneck) | `staff/hired.json` | CTO (infra) + Директор (approve) |

**DoD Q2:** ≥ 2 pilot/active clients; ≥ 25 leads; ≥ 3 approved outreach/week avg; Q3 draft на review.

## Делегирование (child issues CHA-7)

После утверждения плана создаются подзадачи:

| # | Assignee | Заголовок | Scope | Acceptance |
|---|----------|-----------|-------|------------|
| 1 | **CMO** | M1: ICP + marketing experiment | 25 лидов, 1 experiment, outreach targets | KPI M1.1–M1.3 выполнены |
| 2 | **CTO** | M1: Dashboard KPI + cycle reliability | метрики на панели, mock→real checklist | KPI M1.5, документ env |
| 3 | **UXDesigner** | M1: Client onboarding template | бриф-шаблон, UX content plan review | M1.4, AM может использовать |
| 4 | **CMO** | M2: Sales playbooks + pilot #1 | playbooks, 1 pilot client | M2.1–M2.3 |
| 5 | **CTO** | M3: Ops automation + reporting | SOP tooling, weekly report gen | M3.2, M3.4 |
| 6 | **UXDesigner** | M3: Onboarding SOP UX | 7-step flow, dry-run | M3.1 |

## Риски и митигация

| Риск | Митигация |
|------|-----------|
| Mock не отражает реальных лидов | CMO: 1 неделя ручной валидации ICP до масштаба |
| Нет `CURSOR_API_KEY` | CTO: checklist + owner approval gate |
| Outreach без human send | compliance + config `human_approval_required` |
| Перегруз copy/content при 2+ клиентах | приоритет growth over starter для второго клиента |

## Решения директора (2026-06-01)

1. **Фокус июня:** local_food + beauty_wellness (не расширять сегменты до M2).
2. **Пакет по умолчанию для outreach:** growth (не starter).
3. **Не нанимать analyst до недели 4**, если dashboard KPI закрывает tracking.
4. **Human approval** обязателен для send_outreach и sign_contract — без исключений.

---

*Следующий шаг: утверждение совета → создание child issues → старт M1.*
