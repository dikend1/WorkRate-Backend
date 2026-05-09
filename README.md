# WorkRate Backend

Backend API для платформы IWork: отзывы о компаниях, зарплаты, профиль пользователя, поиск и базовая админ-модерация.

Проект написан на FastAPI с async SQLAlchemy, PostgreSQL и Alembic.

## Возможности

- Регистрация, вход, refresh token и JWT Bearer авторизация.
- Swagger Authorize: один раз вставляете `access_token`, и защищенные endpoints работают через `Authorization: Bearer <token>`.
- Google OAuth2.
- Facebook OAuth2, если настроены Facebook credentials.
- Email confirmation и password recovery в dev-режиме через выдачу токена в ответе API.
- CRUD компаний.
- CRUD отзывов.
- Upload файла/фото к отзыву.
- CRUD зарплат и статистика зарплат.
- Поиск и фильтры по компаниям, отзывам и зарплатам.
- Company Page endpoint с общей информацией, последними отзывами и статистикой зарплат.
- Профиль пользователя, contributions и настройки аккаунта.
- Admin endpoints: dashboard, модерация отзывов, scanner, просмотр/удаление зарплат.
- Alembic миграции для PostgreSQL.

## Стек

- Python 3.11+
- FastAPI
- SQLAlchemy async
- PostgreSQL
- Alembic
- Pydantic v2
- Authlib
- Redis опционально
- Uvicorn

## Структура

```text
app/
  api/routers/      # HTTP endpoints
  core/             # config, security, roles, dependencies
  db/               # engine/session/Base
  models/           # SQLAlchemy models
  schemas/          # Pydantic schemas
  services/         # business logic
  main.py           # FastAPI app
alembic/
  versions/         # database migrations
requirements.txt
alembic.ini
```

## Быстрый старт

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

После запуска:

- API: `http://127.0.0.1:8000`
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## Environment

Создайте `.env` в корне проекта:

```env
SECRET_KEY=change_me
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/iwork_db
REDIS_URL=redis://localhost:6379

ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=30
ALGORITHM=HS256
PROJECT_NAME=IWork Backend

OAUTH_GOOGLE_CLIENT_ID=your_google_client_id
OAUTH_GOOGLE_CLIENT_SECRET=your_google_client_secret

OAUTH_FACEBOOK_CLIENT_ID=
OAUTH_FACEBOOK_CLIENT_SECRET=

OPENAI_API_KEY=
FRONTEND_URL=http://localhost:3000
```

Важно:

- `DATABASE_URL` должен быть async: `postgresql+asyncpg://...`
- Redis опционален. Если Redis недоступен, backend продолжит работать.
- Facebook OAuth endpoints вернут `501`, если Facebook credentials не заданы.
- `OPENAI_API_KEY` зарезервирован под будущий настоящий AI scanner. Сейчас scanner работает локально по правилам.

## Миграции

```bash
alembic upgrade head
alembic downgrade -1
alembic heads
alembic revision --autogenerate -m "message"
```

Текущий head:

```text
docs_completion_fields
```

Если после изменения моделей появляется ошибка `column ... does not exist`, сначала выполните:

```bash
alembic upgrade head
```

## Авторизация

1. Зарегистрируйтесь через `POST /auth/register`.
2. Выполните `POST /auth/login`.
3. Скопируйте `access_token`.
4. В Swagger нажмите `Authorize`.
5. Вставьте токен.

Swagger сам отправит:

```http
Authorization: Bearer <access_token>
```

Защищенные endpoints больше не требуют `?token=...`.

## Auth Endpoints

- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/refresh`
- `GET /auth/me`
- `POST /auth/admin/users`
- `POST /auth/confirm-email/request`
- `POST /auth/confirm-email`
- `POST /auth/password-recovery`
- `POST /auth/reset-password`
- `GET /auth/google/login`
- `GET /auth/google/callback`
- `GET /auth/facebook/login`
- `GET /auth/facebook/callback`
- `GET /auth/success`

Для разработки `confirm-email/request` и `password-recovery` возвращают токены прямо в ответе. Для production нужно подключить email provider.

## Companies

- `POST /companies/`
- `GET /companies/`
- `GET /companies/{company_id}`
- `GET /companies/{company_id}/page`
- `PATCH /companies/{company_id}`
- `DELETE /companies/{company_id}`

Фильтры списка:

- `name`
- `location`
- `industry`
- `min_rating`
- `start_date`
- `end_date`

`GET /companies/{company_id}/page` возвращает компанию, последние отзывы и статистику зарплат.

## Reviews

- `POST /reviews/`
- `GET /reviews/`
- `GET /reviews/{review_id}`
- `GET /reviews/company/{company_id}`
- `PATCH /reviews/{review_id}`
- `POST /reviews/{review_id}/attachment`
- `DELETE /reviews/{review_id}`

Фильтры:

- `status`
- `company_id`
- `min_rating`
- `max_rating`
- `is_current_employee`
- `start_date`
- `end_date`
- `skip`
- `limit`

Upload attachments сохраняется в:

```text
uploads/reviews/
```

Файлы доступны через:

```text
/uploads/reviews/<filename>
```

## Salaries

- `POST /salaries/`
- `GET /salaries/`
- `GET /salaries/company/{company_id}`
- `GET /salaries/statistics`
- `PATCH /salaries/{salary_id}`
- `DELETE /salaries/{salary_id}`

Фильтры:

- `company_id`
- `position`
- `location`
- `currency`
- `min_salary`
- `max_salary`
- `min_experience`
- `max_experience`
- `employment_type`
- `start_date`
- `end_date`
- `skip`
- `limit`

## Search

- `GET /search/companies`
- `GET /search/reviews`
- `GET /search/salaries`

Поиск поддерживает основные фильтры по названию, отрасли, локации, рейтингу, тексту, статусу, зарплате, типу занятости и датам.

## Profile

- `GET /profile/me`
- `PATCH /profile/me`
- `POST /profile/change-password`
- `GET /profile/contributions`
- `GET /profile/settings`
- `PATCH /profile/settings`

Все profile endpoints требуют Bearer token.

## Admin

- `GET /admin/dashboard`
- `GET /admin/reviews`
- `PATCH /admin/reviews/{review_id}/moderate`
- `POST /admin/reviews/{review_id}/scan`
- `GET /admin/salaries`
- `DELETE /admin/salaries/{salary_id}`

Admin endpoints требуют роль `admin` или `moderator`, кроме удаления зарплаты, где нужна роль `admin`.

## Роли

Поддерживаемые роли:

- `user`
- `moderator`
- `admin`

Проверка ролей находится в:

```text
app/core/roles.py
```

## OAuth

### Google

1. `GET /auth/google/login`
2. Redirect на Google
3. Callback: `/auth/google/callback`
4. Backend создает или находит пользователя
5. Redirect на `/auth/success`

### Facebook

1. `GET /auth/facebook/login`
2. Redirect на Facebook
3. Callback: `/auth/facebook/callback`
4. Backend создает или находит пользователя
5. Redirect на `/auth/success`

Для OAuth нужен `SessionMiddleware`, он уже подключен в `app/main.py`.

## Development Notes

- `app/core/dependencies.py` содержит общий Bearer auth dependency.
- `app/core/security.py` отвечает за JWT и password hashing.
- `app/services/auth_service.py` отвечает за регистрацию, login, reset password и email confirmation tokens.
- `app/services/admin_service.py` содержит локальный scanner. Это не внешний AI provider.
- `app/main.py` монтирует `/uploads` как static files.

## Проверка

```bash
python3 -m compileall app
alembic heads
alembic upgrade head --sql
```

## Git

```bash
git add .
git commit -m "Implement IWork backend features and bearer auth"
git push
```
