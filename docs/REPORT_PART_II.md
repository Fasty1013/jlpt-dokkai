# Отчёт по Части II (рефакторинг, Шаги 6–10)

Ветка `refactor/decomposition`, дата проверки 2026-11-10. Ветка `main` — worktree `Dokkai-main-compare` (a47db8b).

## Что сделано
| Шаг | Итог |
|---|---|
| 7a/7b | storage/sync/config перенесены в `static/js/*`; инструмент `compare_storage_snapshot.cjs` |
| 7c-1 | `storage.js` разделён на constants, idb_schema, fallback_store, migration, backup + класс |
| 7c-2 | `cloud_sync.js` разделён на config_store, auth_errors, sdk_loader, merge + класс |
| 8a | бэкап БД, `tools/api_snapshot.py` (38 запросов) |
| 8b | `main.py` 638 → 63 строки; `app/{core,models,schemas,services,routers}` |
| 9a | удалены shim-модули бэкенда, неиспользуемые импорты |
| 9b | удалены 6 неиспользуемых JS-констант |
| 10 | сквозная проверка, `tools/stress_scenarios.cjs`, README |

## Результаты проверок (ветка :8000 против main :8001)
- Интерактивный обход: 92/92, 0 расхождений.
- Вычисленные стили (9 экранов): 0 расхождений.
- Сетевые запросы: 28/28 bit-for-bit.
- Снимок хранилища и Firestore payload: 10/10.
- Паритет active_session: 100% bit-for-bit.
- Скриншоты + `pixel_diff.py`: 0 различающихся пикселей в просмотренных строках отчёта.
- Action dispatcher: 9/9; hostile data: 35 сценариев, 0 XSS; утечки слушателей: 0 (54/54/54).
- Граф ES-модулей: 79 модулей, 0 циклов.
- API snapshot: 38/38 (ветка против golden, снятого с кода ветки).
- Playwright (desktop_hd_light + mobile_iphone_class_390): 99 passed, 1 skipped, 0 failed, финальный прогон.
- Стресс-сценарии (ветка): 9/9 — холодный старт, IndexedDB недоступна/кидает исключение/событие error,
  битый localStorage, офлайн-перезагрузка через SW, очищенный Cache Storage, недоступный API,
  облако без ключей.

## Anti-Cheat
До отправки ответов ни один проверенный эндпоинт не отдаёт `is_correct`, `explanation`, `trap_type`,
`evidence_span_id` (проверка встроена в `tools/api_snapshot.py`). Клиентский код упоминает эти поля
только в `analysis_view.js` (после отправки) и `pdf_staging.js` (админ-черновики).

## Ограничения и открытые вопросы
- Golden API снят с кода ветки. Относительно `main` в бэкенде уже была дельта (middleware кэш-заголовков,
  `GET /sw.js`), зафиксированная до Шага 8.
- Стресс-сценарии на `main` (:8001) не удалось дождаться: прогон превысил таймаут и был остановлен,
  сравнения со `main` для них нет.
- Мосты `window.*` в `static/js/main.js` сохранены: используются кодом и тестами.
- Нестабильность: на Шаге 9b в одном из прогонов Playwright падали/были нестабильны `13/01` (desktop) и
  `17/03` (mobile), повтор — зелёный. Причина не установлена. Ранее (7c-1) один раз был flaky `15/03`.
- Не запускались: `test_api.py`, `test_stream.py`, `test_pdf_import.py` (скрипты пишут в рабочую БД).
- Корневой мусор частично оставлен (`Agent.md`/`AGENTS.md` дубли, `run_agents.py`, `scratch/` и др.).
- ruff: оставшиеся замечания стиля FastAPI (B008, DTZ003 и др.) не менялись.
