# LocalMaps SEO Audit — план запуска компании

> Владелец: CEO (Директор) · Issue: CHA-11 · **Ревизия: 2** · Дата: 2026-06-01  
> Ревизия 1 (ChannelPulse) **снята** — не соответствовала цели issue.

## Миссия

**LocalMaps SEO Audit** — автономная AI-компания, которая находит локальный бизнес в **Google Maps** (Европа + США), проводит **SEO/GBP-аудит**, упаковывает результат в **персональный PDF** и предлагает улучшение видимости и рекламы через **холодный outreach** (email, Telegram, WhatsApp).

Теглайн: *«Ваш бизнес на карте — видимость, которую можно измерить»*.

## Целевой продукт (MVP)

| Этап | Что делаем | Артефакт |
|------|------------|----------|
| 1 | Поиск лидов по ICP в Maps (ниша, город, рейтинг, слабые сигналы GBP) | `memory/leads/leads_{date}.json` |
| 2 | Авто-аудит (чеклист GBP + локальное SEO) | `memory/audits/{lead_id}.json` |
| 3 | Генерация PDF «мини-аудит + 3 quick wins» | `memory/audits/{lead_id}.pdf` |
| 4 | Персональный outreach с ссылкой/вложением PDF | `memory/outreach/drafts_{date}.json` |
| 5 | Compliance (GDPR EU / CAN-SPAM US) → approved | `memory/outreach/approved/` |

**Офферы (черновик цен — уточнит CMO):**

- **Free mini-audit PDF** — лид-магнит в первом касании  
- **Full audit + roadmap** — разовая услуга  
- **Monthly Maps + local SEO** — подписка на сопровождение и рекламные рекомендации  

## ICP (Европа + США)

- Локальный бизнес с карточкой Google Business Profile  
- Ниши: food, beauty, medical/dental, home services, auto, retail  
- Сигналы боли: мало отзывов, пустое описание, нет фото/постов, низкий рейтинг, конкуренты выше в Local Pack  
- Гео: приоритет EN/DE/FR/ES + US tier-2 cities (уточнение CMO)

## Критерии приёмки CHA-11 (issue-level)

Компания считается **готовой к операционному циклу**, когда:

1. [ ] Конфиг и роли новой компании в репозитории (`companies/localmaps-seo-audit/`)  
2. [ ] Оркестратор умеет запускать daily cycle для этой компании (отдельный config path)  
3. [ ] Шаблон PDF-аудита и пример сгенерированного файла  
4. [ ] Workflow лидов Maps → аудит → draft outreach (3 канала)  
5. [ ] Compliance-чеклист EU/US задокументирован  
6. [ ] GTM one-pager и 3 гипотезы лидогенерации (CMO)  
7. [ ] Human approval gates: отправка сообщений и платная реклама — только после board  

## C-suite и делегирование

| Роль | Зона | Child issue (создать в Paperclip) |
|------|------|-----------------------------------|
| **CTO** | Репо, оркестратор multi-company, пайплайн лидов/аудитов/PDF, тесты | `CHA-11-CTO` |
| **CMO** | Позиционирование EU/US, офферы, tone, 3 канала outreach | `CHA-11-CMO` |
| **UXDesigner** | Макет PDF-аудита, визуальная система отчёта | `CHA-11-UX` |

### → CTO — техническая платформа

**Objective:** Multi-company runtime + пайплайн Maps SEO audit.

**Acceptance criteria:**
- [ ] `companies/localmaps-seo-audit/config.yaml` подключён к `run_company` (`--company localmaps-seo-audit`)
- [ ] Daily plan: lead research → audit scoring → PDF stub/generator → sales drafts  
- [ ] `python -m scripts.run_company --cycle daily --mock --company localmaps-seo-audit` без ошибок  
- [ ] Тесты на новые модули аудита/лидов  
- [ ] README: cloud + local setup  

**Context:** ChannelPulse (`company/config.yaml`) не трогать без явного решения board.

---

### → CMO — GTM EU/US

**Objective:** Утвердить позиционирование и шаблоны первого касания.

**Acceptance criteria:**
- [ ] One-pager: ICP, офферы, отличие от «generic SEO agencies»  
- [ ] 3 гипотезы лидогенерации с UTM  
- [ ] Шаблоны outreach: email EN, Telegram RU/EN, WhatsApp short  
- [ ] Compliance notes: opt-out, GDPR lawful basis (legitimate interest / consent)  

---

### → UXDesigner — PDF-отчёт

**Objective:** Профессиональный мини-аудит PDF для холодного outreach.

**Acceptance criteria:**
- [ ] Figma/HTML-шаблон или markdown→PDF layout spec  
- [ ] Секции: обложка, score, 3 quick wins, CTA, брендинг LocalMaps  
- [ ] Пример заполненного PDF для демо-лида  

---

## Ограничения

- Не отправлять outreach без human approval  
- Не скрейпить Maps в нарушение ToS Google — использовать разрешённые источники/API или ручной research workflow (решение CTO)  
- Не обещать гарантированный #1 в Local Pack  
- **Paperclip API:** недоступен в cloud (`127.0.0.1:3100`) — child issues в `plans/paperclip-child-issues-CHA-11.json`  

## Следующие шаги CEO

1. **Запросить approval** плана rev.2 у board (`request_confirmation`, idempotency `confirmation:CHA-11:plan:2`)  
2. После approval — создать child issues CTO, CMO, UXDesigner  
3. Параллельный bootstrap трёх направлений  
4. Weekly review метрик воронки (Analyst — общая роль или hire под LocalMaps)  
