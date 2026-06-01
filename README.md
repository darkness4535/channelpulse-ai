# ChannelPulse AI / LocalMaps — автономные AI-компании

**Папка проекта:** репозиторий `ai-company`

Директор, команда агентов, параллельные задачи, панель управления.

## Компании

| Slug | Описание |
|------|----------|
| `channelpulse` (default) | Telegram SMM для малого бизнеса (RU) |
| `localmaps-seo-audit` | Google Maps SEO-аудит EU/US + PDF outreach |

## Запуск

```bash
pip install -r requirements.txt

# ChannelPulse (по умолчанию)
python -m scripts.run_company --cycle daily --mock --force-new

# LocalMaps SEO Audit (CHA-11)
python -m scripts.run_company --cycle daily --mock --force-new --company localmaps-seo-audit

# Список компаний
python -m scripts.run_company --list-companies
```

Панель: двойной клик **`launcher.bat`** → http://127.0.0.1:8765

## Структура

```
ai-company/
  company/              # оркестратор, context, audit pipeline
  companies/
    localmaps-seo-audit/  # конфиг, роли, memory CHA-11
  dashboard/            # веб-панель (API + UI)
  roles/                # промпты ChannelPulse
  scripts/
    run_company.py      # CLI (--company slug)
  tests/
  PLAN.md               # план LocalMaps CHA-11
```

## LocalMaps — артефакты цикла

После mock-цикла:

- `companies/localmaps-seo-audit/memory/leads/leads_{date}.json`
- `companies/localmaps-seo-audit/memory/audits/{lead_id}.json` + `.pdf`
- `companies/localmaps-seo-audit/memory/outreach/drafts_{date}.json`
- `companies/localmaps-seo-audit/memory/outreach/approved/approved_{date}.json`

## Переменные (.env)

| Переменная | Назначение |
|------------|------------|
| `CURSOR_API_KEY` | Реальные Cursor-агенты |
| `COMPANY_MOCK` / `--mock` | Демо без API |
| `COMPANY_SLUG` / `--company` | Активная компания |
| `COMPANY_AUTONOMOUS` | Автонайм (по умолчанию 1) |

## Lead research (lawful)

LocalMaps использует **публичные данные** и ручной research workflow.  
Прямой скрейпинг Google Maps в нарушение ToS запрещён (см. `config.yaml` → `forbidden`).
