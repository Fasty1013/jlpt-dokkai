# 🗺️ Карта данных и границы приватности (Data Map)

В соответствии с принципами **Local-First** и постоянными правилами проекта (`AGENTS.md`), персональные учебные действия пользователя остаются на его личном устройстве. Сервер является минималистичным координатором аутентификации, серий дней (streaks), очков (XP) и публичной таблицы лидеров.

---

## 1. Сравнительная матрица хранения данных

| Тип данных | Где хранится | Доступно ли серверу? | Видно ли другим пользователям? |
| :--- | :--- | :--- | :--- |
| **Выбранные варианты ответов** (`selected_option_id`) | **Только IndexedDB** | ❌ **НЕТ** (сервер получает только массив ID для валидации в момент submit, но не сохраняет в БД) | ❌ НЕТ |
| **Ошибки пользователя и разбор ловушек** | **Только IndexedDB** | ❌ **НЕТ** | ❌ НЕТ |
| **Личные заметки и закладки текстов** | **Только IndexedDB** | ❌ **НЕТ** | ❌ НЕТ |
| **Избранные слова глоссария** | **Только IndexedDB** | ❌ **НЕТ** | ❌ НЕТ |
| **ID аккаунта (`account_id`)** | Сервер (Neon DB) | ✅ ДА | ❌ НЕТ (внутренний UUID) |
| **Провайдер (`google`, `telegram`, `guest`)** | Сервер (Neon DB) | ✅ ДА | ❌ НЕТ |
| **ID провайдера (Google `sub`, Telegram `id`)** | Сервер (Neon DB) | ✅ ДА (хэширован/защищён) | ❌ НЕТ |
| **Email пользователя** | Сервер (Neon DB) | ✅ ДА (только для привязки) | ❌ **СТРОГО НЕТ** (никогда не попадает в лидерборд) |
| **Публичный никнейм (`nickname`)** | Сервер (Neon DB) | ✅ ДА | ✅ ДА (в лидерборде, если включен opt-in) |
| **Аватар (`avatar_choice` / системная иконка)** | Сервер (Neon DB) | ✅ ДА | ✅ ДА (в лидерборде, если включен opt-in) |
| **Часовой пояс (`timezone`)** | Сервер (Neon DB) | ✅ ДА (для корректного расчёта streak) | ❌ НЕТ |
| **Очки опыта (XP) и уровень** | Сервер (Neon DB) | ✅ ДА | ✅ ДА (в лидерборде, если включен opt-in) |
| **Текущая и лучшая серия дней (Streak)** | Сервер (Neon DB) | ✅ ДА | ✅ ДА (в лидерборде, если включен opt-in) |
| **Заработанные бейджи (`badges`)** | Сервер (Neon DB) | ✅ ДА | ✅ ДА (в профиле/лидерборде) |
| **Список решённых текстов (Компактно: `text_id`, `score`, `points`, `timestamp`)** | Сервер (Neon DB) | ✅ ДА (для дедупликации слотов) | ❌ НЕТ |
| **Флаг участия в лидерборде (`opt_in`)** | Сервер (Neon DB) | ✅ ДА | ❌ НЕТ (управляет видимостью) |

---

## 2. Локальное хранилище клиента (IndexedDB: `dokkai_local_v1`)

### Object Stores:
1. `study_sessions`:
   - Ключ: `session_id` (UUID)
   - Поля: `text_id`, `level`, `category`, `started_at`, `completed_at`, `duration_seconds`, `questions: [{ question_id, chosen_option_id, is_correct, time_spent_ms }]`, `feedback_notes`.
2. `user_notes`:
   - Ключ: `id` (auto-increment)
   - Поля: `text_id`, `created_at`, `sentence_ruby`, `user_comment`, `tags`.
3. `favorites`:
   - Ключ: `composite [type, item_id]` (text / word)
   - Поля: `saved_at`, `preview_title`, `level`.
4. `offline_queue`:
   - Очередь для синхронизации набранных очков XP и завершённых заданий с бэкендом при восстановлении связи.

### Экспорт и импорт данных:
- В настройках профиля доступна функция **«Резервная копия»**:
  - `Экспорт данных (.json)` — формирует полный снимок локальной базы для сохранения на компьютер или телефон.
  - `Восстановить из файла (.json)` — восстанавливает локальные заметки и историю без потери данных.

---

## 3. Серверная база данных (Neon PostgreSQL)

### Таблица `users`:
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    provider VARCHAR(20) NOT NULL, -- 'google', 'telegram', 'guest'
    provider_sub VARCHAR(128) NOT NULL,
    nickname VARCHAR(32) NOT NULL,
    avatar_id VARCHAR(32) DEFAULT 'student_1',
    timezone VARCHAR(64) DEFAULT 'UTC',
    timezone_last_changed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    xp INTEGER NOT NULL DEFAULT 0,
    current_streak INTEGER NOT NULL DEFAULT 0,
    max_streak INTEGER NOT NULL DEFAULT 0,
    last_qualifying_date DATE,
    streak_freeze_available BOOLEAN DEFAULT TRUE,
    streak_freeze_used_month VARCHAR(7), -- 'YYYY-MM'
    
    badges JSONB DEFAULT '[]'::jsonb,
    is_leaderboard_public BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT uq_provider_sub UNIQUE (provider, provider_sub)
);
CREATE INDEX idx_users_leaderboard ON users (xp DESC) WHERE is_leaderboard_public = TRUE;
```

### Таблица `completions_compact`:
```sql
CREATE TABLE completions_compact (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    text_id INTEGER NOT NULL REFERENCES texts(id) ON DELETE CASCADE,
    completed_date DATE NOT NULL,
    score_percent SMALLINT NOT NULL,
    points_awarded SMALLINT NOT NULL,
    seconds_spent INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT uq_user_text_completion UNIQUE (user_id, text_id)
);
CREATE INDEX idx_completions_user ON completions_compact (user_id);
CREATE INDEX idx_completions_date ON completions_compact (user_id, completed_date);
```

---

## 4. Соблюдение правил Anti-Cheat и безопасности

1. **Anti-Cheat:**
   - Никаких полей `is_correct`, `explanation`, `trap_type`, `evidence_span_id` в API выдачи заданий.
   - Эндпоинт `/api/stream/complete` принимает массив ответов, на стороне сервера вычисляет `score_percent` и `points_awarded`, обновляет `current_streak` и `xp`, и только в этот момент возвращает клиенту подробный разбор для записи в клиентский IndexedDB.
2. **Минимальное время на вопрос:**
   - Задание считается квалификационным для очков XP и серии дней только если среднее время ответа составляет $\ge 8$ секунд на вопрос (защита от скриптов быстрого клика).
3. **Дневной лимит очков:**
   - Максимум **500 XP в день** (защита от фарминга и аномальных скачков в лидерборде).
4. **Защита часовых поясов (Streak abuse):**
   - Смена часового пояса разрешена не чаще 1 раза в 30 дней (`timezone_last_changed_at`).
5. **Приватность Лидерборда:**
   - По умолчанию `is_leaderboard_public = false` (Opt-in).
   - Email пользователя **никогда не выводится** в публичные списки. Отображается только выбранный `nickname` и `avatar_id`.

