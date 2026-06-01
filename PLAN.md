# LocalMaps SEO Audit — план запуска компании

> Владелец: CEO (Директор) · Issue: CHA-11 · **Ревизия: 3 (accepted)** · Дата: 2026-06-01

## Миссия

**LocalMaps SEO Audit** — автономная AI-компания, которая находит локальный бизнес в **Google Maps** (Европа + США), проводит **SEO/GBP-аудит**, упаковывает результат в **персональный PDF** и предлагает улучшение видимости через **холодный outreach** (email, Telegram, WhatsApp).

## Критерии приёмки CHA-11

1. [x] Конфиг и роли в `companies/localmaps-seo-audit/`
2. [x] Оркестратор: `--company localmaps-seo-audit`
3. [x] PDF-аудит и пример (mock cycle)
4. [x] Workflow: лиды → аудит → outreach drafts (3 канала)
5. [x] Compliance EU/US задокументирован
6. [x] GTM one-pager и шаблоны outreach
7. [x] Human approval gates в config

## Запуск

```bash
python -m scripts.run_company --cycle daily --mock --force-new --company localmaps-seo-audit
```

## Делегирование

| Роль | Статус |
|------|--------|
| CTO | ✅ Multi-company + audit/PDF pipeline |
| CMO | ✅ GTM one-pager + templates |
| UXDesigner | ✅ pdf-template-spec.md |

## CEO acceptance (rev.3)

**2026-06-01** — Директор принял платформу LocalMaps SEO Audit:

- Mock daily cycle: 21/21 задач, 0 ошибок (верифицировано CEO heartbeat 2026-06-01)
- Tests: 11 passed
- Решение: `company/memory/decisions/cha11-ceo-acceptance-2026-06-01.json`
- Issue CHA-11: **done**

Non-blocking follow-up: real agent cycle, UX PDF v2 (см. decision record).
