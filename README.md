# 🇯🇵 JLPT Dokkai Master (読解トレーナー)

Интерактивный веб-тренажёр по чтению на японском языке (**JLPT 読解**) со строгим экзаменационным режимом (Anti-Cheat) и глубоким пошаговым разбором ошибок, ловушек и доказательств в тексте.

---

## 💡 О проекте и концепция

В изучении японского языка существует огромное количество приложений для запоминания иероглифов (Anki, WaniKani) и грамматики (Bunpro), но раздел **чтения (読解 / Dokkai)** почти не представлен в удобном цифровом формате.

**JLPT Dokkai Master** закрывает этот пробел:
1. **Строгий экзаменационный режим (Anti-Cheat):**
   - На уровне API (`GET /api/texts/{id}`) сервер передает **только** текст, вопросы и текст вариантов ответа.
   - Правильные ответы (`is_correct`), разбор вариантов (`option_explanation`), общий разбор (`general_explanation`), перевод (`translation_ru`) и ID предложений-доказательств (`evidence_span_id`) **не передаются в браузер** до момента подтверждения решения.
   - Кнопка отправки заблокирована до тех пор, пока пользователь не выберет ответы на все вопросы.
2. **Экран интерактивного анализа (Post-Submit Mode):**
   - **Подсветка доказательств в тексте:** Автоматически подсвечиваются и анимируются ключевые предложения (`<span id="ev-...">`), на которых строился правильный ответ.
   - **Разбор каждого дистрактора:** Под каждым вариантом объясняется, почему правильный вариант верен и в чём заключалась грамматическая или логическая ловушка остальных вариантов (ловушка ложного обобщения, ловушка крайности, подмена субъекта).
   - **Инструменты изучения:**
     - Переключатель фуриганы (включение/скрытие тегов `<rt>`).
     - Выдвижная панель с полным переводом на русский язык и словарём сложных слов с кандзи и чтением.
     - Секундомер реального времени со сравнением с рекомендуемым экзаменационным таймингом.
3. **Разноуровневый каталог:**
   - **N5:** Короткие записки, объявления и памятки (`short`).
   - **N4:** Рассказы от первого лица, дневники и путевые заметки (`medium`).
   - **N3:** Эссе с экзаменационными ловушками и поиск информации по расписаниям/флаерам (`info_search`).
   - **N2:** Полноценные публицистические статьи и журнальные колонки (`article`).

---

## 🛠 Технологический стек

- **Backend:** Python 3.10+, FastAPI, Pydantic v2
- **Database:** SQLAlchemy ORM (SQLite по умолчанию, переключается на PostgreSQL заменой `DATABASE_URL`)
- **Frontend:** Vanilla JavaScript (ES6+), HTML5, современный CSS3 (CSS Variables, Flexbox/Grid, Split-View, Google Fonts `Noto Sans JP`)
- **Без тяжёлых сборщиков:** Мгновенный запуск без Webpack, Vite или Node.js.

---

## 🚀 Быстрый старт локально

### 1. Клонирование репозитория
```bash
git clone https://github.com/Fasty1013/jlpt-dokkai.git
cd jlpt-dokkai
```

### 2. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 3. Запуск сервера
```bash
uvicorn main:app --reload --port 8000
```

При первом запуске база данных `dokkai.db` создаётся и автоматически наполняется материалами N5–N2.

Откройте в браузере:
- 🌐 Приложение: **[http://localhost:8000](http://localhost:8000)**
- 📖 Swagger API Docs: **[http://localhost:8000/docs](http://localhost:8000/docs)**

---

## ☁️ Развёртывание в облако 24/7 (Deploy)

Приложение готово к развёртыванию на бесплатных или дешёвых платформах (например, **Render** или **Railway**):

1. **Build Command:** `pip install -r requirements.txt`
2. **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
3. **Переменная `SHUFFLE_SECRET`** — секретный ключ HMAC для перемешивания вариантов ответов (в `render.yaml` создаётся автоматически). Задайте один раз и не меняйте: при смене ключа порядок вариантов в незавершённых попытках изменится.

---

## 🤖 Мультиагентная система (.agents)

В проекте настроена специализированная мультиагентная система для совместной работы над образовательным контентом и архитектурой кода:
- **`@jlpt-expert`** (`.agents/agents/jlpt-expert.md`): Методолог экзамена JLPT (N5–N1), лингвист, специалист по грамматике, дистракторам и кандзи.
- **`@senior-dev`** (`.agents/agents/senior-dev.md`): Senior Software Engineer (FastAPI, архитектура, безопасность Anti-Cheat, фронтенд, тесты).

Подробная инструкция доступна в [**AGENTS.md**](./AGENTS.md).

### Быстрый запуск агентов:
```bash
# Интерактивное меню выбора
python run_agents.py

# Только Лингвист-методолог JLPT
python run_agents.py --expert

# Только Senior-разработчик (с запуском тестов и аудитом Anti-Cheat)
python run_agents.py --dev

# Совместный запуск (Оркестратор: Эксперт + Разработчик)
python run_agents.py --both -t "Добавление новых заданий N3"

# Самодиагностика проекта (Синтаксис + Anti-Cheat + Тесты)
python run_agents.py --check
```

---

## 📂 Структура проекта

```text
├── main.py                  # Точка входа ASGI (`uvicorn main:app`): app, lifespan, роутеры
├── app/
│   ├── core/                # config (пути), database (engine, сессия SQLAlchemy)
│   ├── models/              # Модели SQLAlchemy: Text, Question, Option, TaskSlot, ...
│   ├── schemas/             # Pydantic-схемы (чтение без ответов vs анализ после отправки)
│   ├── services/            # scoring_service, stream_service, dictionary_service
│   └── routers/             # health, catalog, reading, dictionary, analysis, stream,
│                            # reports, admin, pages
├── seed.py, content_loader.py, validate_content.py   # Наполнение и проверка контента
├── content/, tools/         # Тексты, генераторы, миграции, импорт PDF, QA-скрипты
├── static/
│   ├── index.html, manifest.json, sw.js
│   ├── css/                 # Модульный CSS
│   └── js/
│       ├── main.js          # Точка входа ES-модулей (оркестрация)
│       ├── app/             # Инициализация, действия, persistence
│       ├── features/        # Фичи: catalog, exercise, analysis, notebook, sync_ui, ...
│       ├── state/           # store.js, elements.js
│       ├── storage/         # IndexedDB + localStorage fallback (DokkaiStorage)
│       ├── sync/            # Firebase Auth + Firestore sync (DokkaiCloudSync)
│       └── config/          # firebase-config.js
├── tests/qa/                # Playwright (Desktop HD / Mobile iPhone 390), axe-core
├── docs/                    # Заметки, отчёты, INTENTIONAL_DIFFERENCES.md
├── .agents/, AGENTS.md      # Мультиагентная система (jlpt-expert, senior-dev)
└── requirements.txt, Procfile, render.yaml, Dockerfile
```

### Потоки данных

1. **Чтение:** `GET /api/texts/{id}` отдаёт только текст и варианты без ответов (Anti-Cheat).
2. **Проверка:** `POST /api/stream/complete` (и `POST /api/texts/{id}/submit`, только при `DOKKAI_TEST_MODE=1`) — единственные места, где
   сервер раскрывает правильность, объяснения, `trap_type` и `evidence_span_id`.
3. **Хранение:** результаты и настройки пишутся в IndexedDB (`dokkai_master_db`), при её
   недоступности — в localStorage (`dokkai_idb_*`).
4. **Облако:** при входе через Firebase выполняется lossless-слияние с `users/{uid}/sync/state`.
   Без входа приложение полностью работает офлайн.

### Проверки паритета и качества

```bash
python tools/api_snapshot.py                        # API: 38 запросов против golden
node tools/compare_storage_snapshot.cjs --baseline  # IndexedDB / localStorage / Firestore payload
node tools/check_dependency_graph.cjs               # ES-модули без циклов
node tools/stress_scenarios.cjs                     # холодный старт, сломанная IndexedDB, офлайн
cd tests/qa && npx playwright test --project=desktop_hd_light --project=mobile_iphone_class_390
```

Сравнения с веткой `main` (`tools/compare_*.cjs`, `tools/pixel_diff.py`) требуют двух серверов:
ветка на `:8000`, `main` на `:8001`.

---

## 🧪 Автотесты и тестовый режим (DOKKAI_TEST_MODE)

В проекте настроен полный сьют интеграционных, E2E и визуальных тестов:
- **Backend / Anti-Cheat тесты:** `python test_api.py` (или `python run_agents.py --check`)
- **E2E Playwright тесты:** `cd tests/qa && npx playwright test`
- **Пиксельное сравнение экранов (Pixel Diff):** `python tools/pixel_diff.py`
- **Проверка вычисленных стилей (Style Protection, обязательный Pre-Merge Check):**
  ```bash
  node tools/compare_computed_styles.cjs
  ```
  *Скрипт автоматически сравнивает вычисленные стили (`getComputedStyle` по 38 свойствам, включая `:hover` и `:focus`) между `main` (порт 8001) и веткой (порт 8000) по 9 ключевым экранам. Допуск: строго 0 расхождений.*

### Переменная окружения `DOKKAI_TEST_MODE`:
Для безопасного тестирования динамического обновления версий Service Worker (тест деплоя новой версии) бэкенд проверяет флаг `DOKKAI_TEST_MODE=1`.
- **В локальных тестах:** Playwright автоматически передаёт `DOKKAI_TEST_MODE=1` в `webServer` конфига (`tests/qa/playwright.config.ts`).
  При ручном запуске сервера для тестов выполните:
  ```powershell
  $env:DOKKAI_TEST_MODE="1"; python -m uvicorn main:app --port 8000
  ```
- **На проде (Production):** Переменная `DOKKAI_TEST_MODE` не задана. Любые запросы с параметром `?version=...` к `/sw.js` строго игнорируются, исключая подделку версий извне.

---

## ⚙️ Управление Service Worker и очистка кэша

В приложении работает легковесный Service Worker (`/sw.js`), обеспечивающий автономную работу (PWA) и кэширование статических файлов (CSS/JS) по стратегии **Network-First** (свежая версия всегда запрашивается из сети).

### Как отключить Service Worker или сбросить застрявший кэш
Если требуется принудительно отключить Service Worker или очистить локальный кэш браузера, выполните в DevTools Console (F12):

```javascript
// 1. Отмена регистрации всех активных Service Workers
navigator.serviceWorker.getRegistrations().then(registrations => {
    for (const reg of registrations) {
        reg.unregister();
        console.log('[PWA] Service Worker unregistered:', reg.scope);
    }
});

// 2. Очистка хранилища Cache Storage
caches.keys().then(cacheNames => {
    for (const name of cacheNames) {
        caches.delete(name);
        console.log('[PWA] Cache deleted:', name);
    }
});
```
После выполнения обновите страницу с жестким сбросом: `Ctrl + F5` (или `Cmd + Shift + R`).

---

## 📜 Лицензия
MIT License.

