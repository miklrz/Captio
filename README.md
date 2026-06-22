# Captio

Captio - клиент-серверный сервис автоматической генерации субтитров и перевода для видео.

Пользователь отправляет ссылку или загружает файл, backend создает задание обработки, запускает распознавание речи через Whisper, сохраняет результат и возвращает текст, таймкоды и SRT-файл. Frontend показывает форму загрузки, страницу статуса, историю, профиль, CRUD-задачи и административное управление пользователями.

## Ссылки

- Репозиторий: <https://github.com/miklrz/Captio>
- Локальный backend: <http://localhost:8000>
- Swagger UI: <http://localhost:8000/docs>
- Локальный frontend: <http://localhost:3000>

Production URL задается после публикации через Render Blueprint из `render.yaml`.

## Структура проекта

| Путь | Назначение |
| --- | --- |
| `backend/` | Основной FastAPI backend |
| `frontend/` | React + Redux frontend |
| `backend-node/` | Старый учебный Node.js backend, оставлен как legacy-код |
| `docs/api-test-results.md` | Результаты API-тестирования с HTTP-кодами |
| `docs/fuzzing-results.md` | Результаты автоматизированного fuzzing |
| `docs/deployment.md` | Docker, Render, CI/CD и Twelve-Factor App |
| `docker-compose.yml` | Production-like запуск frontend + backend |
| `render.yaml` | Конфигурация облачного deploy на Render |
| `.github/workflows/ci.yml` | GitHub Actions workflow |
| `.env.example` | Безопасный пример конфигурации |

## Возможности

- регистрация и вход пользователей;
- JWT-аутентификация;
- роли `user` и `admin`;
- RBAC для управления пользователями и задачами;
- CRUD-задачи с проверкой владельца;
- загрузка локального видео/аудио;
- обработка ссылок YouTube, Yandex Disk и прямых URL;
- режимы `transcribe` и `translate`;
- выбор исходного и целевого языка;
- фоновая обработка video job;
- polling статуса через `/api/videos/{job_id}/status`;
- генерация и скачивание SRT;
- история обработок;
- ограничения размера и расширений файлов;
- автоматическая очистка старых uploads/outputs;
- API-тесты и fuzzing-тестирование.

## Backend

```bash
cd backend
poetry install --no-root
make dev
```

После запуска:

- API: <http://localhost:8000>
- healthcheck: <http://localhost:8000/health>
- Swagger UI: <http://localhost:8000/docs>

Полезные команды:

```bash
make test   # полный pytest
make fuzz   # только fuzzing-тесты
make build  # сборка backend Docker image
make run    # запуск backend Docker image
```

Тестовые пользователи создаются при `CAPTIO_SEED_DEMO_USERS=true`:

- `admin / admin123`, роль `admin`;
- `paimon / 123456`, роль `user`.

В production рекомендуется отключить demo seed и задать собственные значения через env.

## Frontend

```bash
cd frontend
npm install
npm start
```

Frontend использует переменную:

```text
REACT_APP_API_BASE_URL=http://localhost:8000
```

Production build:

```bash
cd frontend
npm run build
```

## Переменные окружения

Скопируйте пример:

```bash
cp .env.example .env
```

Основные параметры:

| Переменная | Назначение |
| --- | --- |
| `CAPTIO_ENV` | Окружение: `development`, `testing`, `production` |
| `DATABASE_URL` | SQLite URL, например `sqlite:///data/captio.db` |
| `CAPTIO_DB_PATH` | Альтернативный путь к SQLite-файлу |
| `CAPTIO_DATA_DIR` | Каталог данных uploads/outputs |
| `CAPTIO_JWT_SECRET` | Секрет подписи JWT, обязателен в production |
| `CAPTIO_JWT_EXPIRES_HOURS` | Срок жизни JWT |
| `CAPTIO_WHISPER_MODEL` | Модель Whisper |
| `CAPTIO_MAX_UPLOAD_SIZE_MB` | Максимальный размер upload |
| `CAPTIO_ALLOWED_VIDEO_EXTENSIONS` | Allowlist расширений |
| `CAPTIO_CORS_ORIGINS` | Разрешенные frontend origins |
| `CAPTIO_SEED_DEMO_USERS` | Создавать ли demo-пользователей |
| `REACT_APP_API_BASE_URL` | Base URL backend для frontend |

## Docker Compose

```bash
cp .env.example .env
# задайте CAPTIO_JWT_SECRET в .env
docker compose up --build
```

Проверка:

```bash
curl http://localhost:8000/health
curl http://localhost:3000/health
```

## Облачное развертывание

Подготовлен Render Blueprint `render.yaml`:

- `captio-api` - Docker web service из `backend`;
- `captio-web` - static site из `frontend`;
- persistent disk `/app/data` для SQLite и файлов;
- healthcheck `/health`;
- секреты задаются в панели Render.

Подробная инструкция: [docs/deployment.md](docs/deployment.md).

## Тестирование

Локальный прогон после исправлений:

```text
135 passed, 1 warning in 44.85s
```

Документы с результатами:

- [docs/api-test-results.md](docs/api-test-results.md);
- [docs/fuzzing-results.md](docs/fuzzing-results.md).

Проверенные группы:

- auth: регистрация, вход, `/me`, ошибки `401`, `409`, `422`;
- RBAC: admin/user доступы и недопустимые роли;
- tasks CRUD: create/read/update/delete и `404`;
- videos: upload, status, SRT, лимиты размера и расширений;
- fuzzing: 129 сгенерированных негативных и граничных API-кейсов.

## CI/CD

Workflow `.github/workflows/ci.yml` запускает:

- backend: Python 3.12, Poetry, `pytest -q`;
- frontend: Node.js 22, `npm ci`, `npm run build`.

После подключения Render к GitHub успешный push может использоваться как release boundary для облачного deploy.
