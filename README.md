# WorkRate Backend

Backend API для платформы отзывов о компаниях и зарплатах (FastAPI + PostgreSQL + SQLAlchemy Async + Alembic).

## Что есть в проекте

- JWT-аутентификация (register/login/refresh/me)
- Google OAuth2 авторизация
- Роли пользователей: user, moderator, admin
- CRUD для компаний
- CRUD для отзывов
- CRUD для зарплат
- Статистика зарплат (average/median/min/max/percentiles)
- Alembic миграции

## Технологии

- Python 3.10+
- FastAPI
- SQLAlchemy (async)
- PostgreSQL
- Alembic
- Redis (опционально, для refresh token)
- Authlib (Google OAuth)

## Структура проекта

```text
app/
	api/routers/        # HTTP роуты
	core/               # config, security, roles, redis client
	db/                 # engine, session, Base
	models/             # SQLAlchemy модели
	schemas/            # Pydantic схемы
	services/           # бизнес-логика
	main.py             # точка входа FastAPI
alembic/              # миграции
requirements.txt
alembic.ini
```

## Быстрый старт

1. Клонируйте репозиторий и перейдите в папку проекта.
2. Создайте и активируйте виртуальное окружение.
3. Установите зависимости.
4. Создайте файл .env.
5. Примените миграции.
6. Запустите сервер.

Пример команд:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

После запуска:

- API: http://127.0.0.1:8000
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## Переменные окружения

Обязательные переменные (см. app/core/config.py):

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
```

Примечания:

- DATABASE_URL должен быть в async формате (postgresql+asyncpg://...).
- REDIS_URL опционален. Если Redis недоступен, часть логики refresh-token работает в fallback режиме.

## Миграции

```bash
# применить все миграции
alembic upgrade head

# откатить последнюю миграцию
alembic downgrade -1

# создать новую миграцию
alembic revision --autogenerate -m "your_message"
```

## Авторизация и роли

- JWT создается в auth-сервисе.
- Проверка прав выполняется через dependencies в core/roles.py.
- Алиасы ролей:
	- require_user
	- require_moderator
	- require_admin

Важно: в части роутов токен ожидается как query-параметр token, а не через Authorization header.

## Основные эндпоинты

### Auth

- POST /auth/register
- POST /auth/login
- POST /auth/refresh
- GET /auth/me
- POST /auth/admin/users
- GET /auth/admin/dashboard
- GET /auth/moderator/reviews
- GET /auth/google/login
- GET /auth/google/callback
- GET /auth/success

### Companies

- POST /companies/
- GET /companies/
- GET /companies/{company_id}
- PATCH /companies/{company_id}
- DELETE /companies/{company_id}

### Reviews

- POST /reviews/
- GET /reviews/
- GET /reviews/{review_id}
- GET /reviews/company/{company_id}
- PATCH /reviews/{review_id}
- DELETE /reviews/{review_id}

### Salaries

- POST /salaries/
- GET /salaries/company/{company_id}
- PATCH /salaries/{salary_id}
- DELETE /salaries/{salary_id}
- GET /salaries/statistics

## Google OAuth2

Реализован поток через redirect:

1. Переход на GET /auth/google/login
2. Редирект на Google
3. Callback на GET /auth/google/callback
4. Создание/поиск пользователя
5. Редирект на /auth/success

Для корректной работы нужен SessionMiddleware (уже подключен в app/main.py).

## Ограничения текущей версии

- Роутер поиска /search подключен, но полноценные публичные эндпоинты поиска еще не реализованы.
- В сервисе поиска есть обращения к полям, которых нет в текущих моделях (size, popularity, amount, position в reviews).
- В файле app/api/routers/router_auth.py присутствует служебная строка def --- IGNORE ---, которую нужно удалить, иначе приложение не стартует из-за SyntaxError.

## Полезные файлы

- app/main.py: инициализация приложения и middleware
- app/core/config.py: настройки через .env
- app/core/security.py: хеширование паролей и JWT
- app/core/roles.py: role-based access
- app/services/: бизнес-логика
- alembic/versions/: история схемы БД

## Что можно улучшить дальше

- Привести авторизацию к единому формату Bearer token в headers
- Закрыть TODO по поиску и фильтрации
- Добавить unit/integration тесты
- Добавить линтеры/форматтеры в CI
- Ужесточить CORS и session настройки для production
