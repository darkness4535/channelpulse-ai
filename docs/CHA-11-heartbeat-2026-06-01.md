# Heartbeat CHA-11 — Директор — 2026-06-01 (rev.2)

## Что изменилось

Предыдущий bootstrap (rev.1) **ошибочно** описал ChannelPulse (Telegram SMM). По тексту issue CHA-11 цель — **новая компания SEO-аудита Google Maps (EU/US)** с PDF-предложением и outreach через email / Telegram / WhatsApp.

## Действия CEO

1. **PLAN.md rev.2** — LocalMaps SEO Audit: миссия, MVP, ICP, критерии приёмки, делегирование CTO/CMO/UX.
2. **Scaffold** `companies/localmaps-seo-audit/config.yaml` + memory dirs (ChannelPulse не трогали).
3. **Спецификации child issues** в `plans/paperclip-child-issues-CHA-11.json` (API Paperclip недоступен: connection refused 127.0.0.1:3100).
4. **Решения** обновлены в `company/memory/decisions/bootstrap-2026-06-01.json`.

## Делегирование (ожидает API или ручного создания)

| Child | Assignee | Суть |
|-------|----------|------|
| CHA-11-CTO | CTO | Multi-company orchestrator + audit/PDF pipeline |
| CHA-11-CMO | CMO | GTM EU/US, шаблоны 3 каналов |
| CHA-11-UX | UXDesigner | Макет PDF мини-аудита |

## Статус issue

**in_review** — требуется approval плана rev.2 у board (`confirmation:CHA-11:plan:2`).

После approval CEO создаёт child issues и переводит CHA-11 в делегированный bootstrap.

## Blocker

- Paperclip API в cloud: недоступен. Unblock: board / инфраструктура Paperclip.

## Remaining

- [ ] Board: approve PLAN rev.2
- [ ] Создать child issues CTO, CMO, UX
- [ ] CTO: `--company localmaps-seo-audit` в run_company
- [ ] CMO: GTM one-pager + outreach templates
- [ ] UX: pdf-template-spec + demo PDF
