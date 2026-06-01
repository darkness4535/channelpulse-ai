# ChannelPulse AI — автономная AI-компания

**Папка проекта:** `C:\Users\Administrator\Projects\ai-company`

Директор, команда агентов, параллельные задачи, панель управления.

## Запуск

Двойной клик **`launcher.bat`** → http://127.0.0.1:8765

Или в терминале:

```powershell
cd C:\Users\Administrator\Projects\ai-company
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m scripts.run_company --cycle daily --mock --force-new
```

## Структура

```
ai-company/
  launcher.bat          # панель управления
  company/              # оркестратор, память, конфиг
  dashboard/            # веб-панель (API + UI)
  roles/                # промпты сотрудников
  scripts/
    run_company.py      # CLI цикл
    run_autonomous.py   # фоновый daemon
  tests/
```

## Переменные (.env)

| Переменная | Назначение |
|------------|------------|
| `CURSOR_API_KEY` | Реальные Cursor-агенты |
| `COMPANY_MOCK` / `--mock` | Демо без API |
| `COMPANY_AUTONOMOUS` | Автонайм (по умолчанию 1) |
| `COMPANY_PARALLEL_WORKERS` | Потоков в волне |
