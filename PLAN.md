# ChannelPulse AI — план запуска компании

> Владелец: CEO (Директор) · Issue: CHA-11 · Ревизия: 1 · Дата: 2026-06-01

## Миссия

**ChannelPulse AI** — автономная AI-компания по ведению и росту Telegram-каналов для малого бизнеса (SMB).  
Теглайн: *«Telegram-каналы, которые продают — без найма SMM-отдела»*.

## Цели первых 30 дней

| # | Цель | Метрика успеха | Владелец |
|---|------|----------------|----------|
| 1 | Запустить ежедневный операционный цикл | ≥5 рабочих циклов подряд без сбоев зависимостей | CTO → Director |
| 2 | Наполнить верх воронки | ≥5 квалифицированных лидов / неделя | Lead Researcher → Head of Sales |
| 3 | Подготовить outreach без отправки | ≥3 approved drafts / неделя, 0 нарушений compliance | Head of Sales → Compliance |
| 4 | Проверить product-market fit гипотез | ≥3 маркетинговые гипотезы с UTM | CMO → Marketer |
| 5 | Доставка контента демо-клиенту | Контент-план 7 дней + ≥3 поста | Content Strategist → Copywriter |

## Организационная структура

### C-suite (Paperclip — прямые подчинённые CEO)

| Роль | Зона ответственности | Статус |
|------|---------------------|--------|
| **CTO** | Код, инфра, оркестратор, CI, devtools | ⏳ Требует найма / делегирования |
| **CMO** | Позиционирование, growth, devrel, контент-стратегия бренда | ⏳ Требует найма / делегирования |
| **UXDesigner** | Dashboard, design-system, UX-исследования | ⏳ По необходимости (фаза 2) |

### Операционная команда (ChannelPulse roles — уже в штате)

- Lead Researcher, Head of Sales, Compliance, Account Manager  
- Content Strategist, Copywriter, Marketer, **Analyst** (добавлен при bootstrap)

## Делегирование bootstrap (CHA-11)

### → CTO: Техническая готовность платформы

**Objective:** Репозиторий и оркестратор готовы к ежедневным циклам в cloud и локально.

**Acceptance criteria:**
- [ ] `python -m scripts.run_company --cycle daily --mock --force-new` завершается без ошибок
- [ ] Dashboard (`dashboard/app.py`) поднимается на :8765
- [ ] Документирован dev setup в README (cloud + local)
- [ ] Зависимости и тесты (`tests/`) проходят

**Кontext:** Paperclip API недоступен в cloud (127.0.0.1:3100). Артефакты цикла 2026-06-01 уже в `company/memory/`.

---

### → CMO: Go-to-market и positioning

**Objective:** Утвердить позиционирование и 30-дневный GTM-план.

**Acceptance criteria:**
- [ ] One-pager: ICP, офферы (starter/growth/premium), конкурентное отличие
- [ ] 3 маркетинговые гипотезы (сейчас 1 — довести до 3)
- [ ] Каналы лидогенерации с приоритетами (TG Ads, outreach, партнёрства)
- [ ] Tone of voice для outreach и контента

**Context:** Базовые гипотезы в `company/memory/marketing/hypotheses_2026-06-01.json`.

---

### → Director (self): Операционный ритм

**Objective:** Ежедневный цикл и отчётность без ручного вмешательства board.

**Acceptance criteria:**
- [x] Штат операционной команды укомплектован (включая Analyst)
- [x] Directives владельца зафиксированы (`company/memory/directives.json`)
- [ ] Первый полный цикл с real agents (после CURSOR_API_KEY)
- [ ] Еженедельный синтез метрик (Analyst)

## Ограничения и gates

- **Human approval required:** send_outreach, publish_telegram, sign_contract, hire_staff
- **Не делать:** массовый спам, гарантии продаж, сбор ПДн без согласия
- **Paperclip API:** заблокирован в cloud-среде — child issues создаются при восстановлении API

## Следующие шаги CEO

1. Создать child issues CHA-11 → CTO, CMO (когда API доступен)
2. Запросить у board approval плана (revision 1)
3. После approval — запустить параллельный bootstrap CTO + CMO
4. Мониторить первый weekly review (Analyst) — 2026-06-08
