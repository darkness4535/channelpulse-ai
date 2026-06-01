# LocalMaps SEO Audit — план запуска компании

> Владелец: CEO (Директор) · Issue: CHA-11 · **Ревизия: 2** · Дата: 2026-06-01

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
