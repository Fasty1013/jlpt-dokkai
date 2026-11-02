# 📋 Чек-лист: Что должен сделать человек ($0 Setup Guide)

Все сервисы ниже **строго бесплатны** и **НЕ требуют ввода данных банковской карты**.  
Если какой-то сервис предлагает ввести карту для «пробного периода» — откажитесь или пропустите этот шаг.

---

## Шаг 1: Создание базы данных Neon PostgreSQL (Занимает 2 минуты)

1. Перейдите на [neon.tech](https://neon.tech) и нажмите **Sign Up** (через GitHub или Google).
2. Нажмите **Create Project**:
   - Project name: `dokkai-db`
   - Postgres version: `16` (или последняя стабильная)
   - Region: выберите ближайший к вашим пользователям (например, `Frankfurt (eu-central-1)`).
3. После создания скопируйте строку подключения:
   - Выберите вкладку **Connection string** $\rightarrow$ **Pooled connection** (или Direct connection).
   - Формат: `postgresql://[user]:[password]@[host]/[dbname]?sslmode=require`
4. Сохраните эту строку как переменную окружения `DATABASE_URL`.

---

## Шаг 2: Настройка авторизации Google (OAuth 2.0 Web Client)

1. Откройте [Google Cloud Console](https://console.cloud.google.com/).
2. Создайте новый бесплатный проект (например, `dokkai-app`). **Биллинг / карту НЕ подключать!**
3. В боковом меню перейдите в **APIs & Services** $\rightarrow$ **OAuth consent screen**:
   - User Type: выберите **External** (Внешний).
   - Нажмите **Create**.
   - App information: App name = `JLPT Dokkai`, User support email = ваш email.
   - Developer contact email: ваш email.
   - Нажмите **Save and Continue**.
4. Вкладка **Scopes**:
   - Нажмите **Add or Remove Scopes**.
   - Отметьте только три базовых бесплатных скоупа: `.../auth/userinfo.email`, `.../auth/userinfo.profile`, `openid`.
   - Нажмите **Save and Continue**.
5. Статус публикации:
   - Можно оставить **Testing** (добавив свой email в список тестовых пользователей) или нажать **Publish App** (для базовых скоупов верификация Google не требуется и плата не взимается).
6. Перейдите во вкладку **Credentials** $\rightarrow$ **Create Credentials** $\rightarrow$ **OAuth client ID**:
   - Application type: **Web application**.
   - Name: `Dokkai Web Client`.
   - **Authorized redirect URIs**:
     - Для локальной разработки: `http://localhost:8000/api/auth/google/callback`
     - Для облака Render: `https://<ваше-имя-сервиса>.onrender.com/api/auth/google/callback`
   - Нажмите **Create**.
7. Скопируйте **Client ID** и **Client Secret**:
   - `GOOGLE_CLIENT_ID`
   - `GOOGLE_CLIENT_SECRET`

---

## Шаг 3: Настройка авторизации Telegram (@BotFather)

1. Откройте Telegram и найдите официального бота [@BotFather](https://t.me/BotFather).
2. Отправьте команду: `/newbot`
3. Укажите имя бота (например, `JLPT Dokkai Master`) и юзернейм (например, `jlpt_dokkai_bot`).
4. Скопируйте полученный **HTTP API Token** (сохраните как `TELEGRAM_BOT_TOKEN`).
5. В диалоге с `@BotFather` настройте домен для авторизации:
   - Отправьте команду: `/setdomain`
   - Выберите вашего бота.
   - Отправьте домен вашего приложения на Render (без `https://`): `<ваше-имя-сервиса>.onrender.com`
   *(Для локального тестирования авторизация в Dokkai работает через Dev-Auth / Guest Mode, поэтому связывать localhost с ботом не обязательно).*

---

## Шаг 4: Развёртывание на Render (Web Service Free)

1. Зарегистрируйтесь на [render.com](https://render.com) через GitHub.
2. Нажмите **New +** $\rightarrow$ **Web Service**.
3. Подключите ваш репозиторий `Fasty1013/jlpt-dokkai`.
4. Заполните параметры:
   - **Name:** `jlpt-dokkai` (или любое свободное имя, которое сформирует `https://jlpt-dokkai.onrender.com`)
   - **Environment:** `Python 3` (или `Docker`)
   - **Region:** `Frankfurt (EU Central)` (рядом с базой Neon)
   - **Branch:** `main`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type:** **Free** ($0 / month, 512 MB RAM)
5. В разделе **Environment Variables** добавьте:
   - `DATABASE_URL`: ваша строка из Шага 1 (`postgresql://...`)
   - `SECRET_KEY`: случайная длинная строка (32+ символа, например из `python -c "import secrets; print(secrets.token_hex(32))"`)
   - `GOOGLE_CLIENT_ID`: из Шага 2
   - `GOOGLE_CLIENT_SECRET`: из Шага 2
   - `TELEGRAM_BOT_TOKEN`: из Шага 3
   - `TELEGRAM_BOT_USERNAME`: юзернейм бота из Шага 3 (без `@`)
   - `ENV`: `production`
6. Нажмите **Create Web Service**. Сервис соберется и запустится автоматически.

---

## Шаг 5: Проверка и активация

1. Откройте адрес `https://<ваше-имя-сервиса>.onrender.com`.
2. Дождитесь загрузки (первый холодный старт может занять ~50 сек).
3. Проверьте:
   - Гостевой вход работает без ввода учетных данных.
   - Вход через Google и Telegram открывает диалоговое окно провайдера.
   - Таблица лидеров и серии дней корректно обновляются.
