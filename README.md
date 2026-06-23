# Captio

Captio - клиент-серверный сервис автоматической генерации субтитров и перевода для видео.

Пользователь отправляет ссылку или загружает файл, backend создает задание обработки, запускает распознавание речи через Whisper, сохраняет результат и возвращает текст, таймкоды и SRT-файл. Frontend показывает форму загрузки, страницу статуса, историю, профиль, CRUD-задачи и административное управление пользователями.

## Ссылки

- Репозиторий: <https://github.com/miklrz/Captio>
- Сайт: <https://captio-front.onrender.com/>
- Backend: <https://captio-lnrg.onrender.com>
- Swagger UI: <https://captio-lnrg.onrender.com/docs>

**Локально:**
- Локальный backend: <http://localhost:8000>
- Локальный Swagger UI: <http://localhost:8000/docs>
- Локальный frontend: <http://localhost:3000>

Production окружение развернуто на Render как два отдельных Web Service: backend и frontend.

## Структура проекта

| Путь | Назначение |
| --- | --- |
| `backend/` | Основной FastAPI backend |
| `frontend/` | React + Redux frontend |
| `docker-compose.yml` | Production-like запуск frontend + backend |
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
| `CAPTIO_CORS_ORIGIN_REGEX` | Regex для облачных frontend origins |
| `CAPTIO_SEED_DEMO_USERS` | Создавать ли demo-пользователей |
| `CAPTIO_YTDLP_COOKIES_FILE` | Путь к cookies-файлу Netscape/Mozilla для YouTube через `yt-dlp` |
| `CAPTIO_YTDLP_COOKIES_CONTENT` | Содержимое cookies-файла для YouTube, если Secret File недоступен |
| `REACT_APP_API_BASE_URL` | Base URL backend для frontend |

## Docker Compose

```bash
cp .env.example .env
# задайте CAPTIO_JWT_SECRET в .env
docker-compose up --build
```

Проверка:

```bash
curl http://localhost:8000/health
curl http://localhost:3000/health
```

## Облачное развертывание

Приложение развернуто на Render как два отдельных Web Service:

- backend service собирается из `backend/Dockerfile`;
- frontend service собирается из `frontend/Dockerfile`;
- backend слушает переменную `PORT` и предоставляет healthcheck `/health`;
- frontend отдает production-сборку React через nginx;
- секреты и параметры окружения задаются отдельно в настройках каждого сервиса Render.

Для backend service задаются основные переменные:

```text
CAPTIO_ENV=production
DATABASE_URL=sqlite:////app/data/captio.db
CAPTIO_DATA_DIR=/app/data
CAPTIO_JWT_SECRET=<secret>
CAPTIO_WHISPER_MODEL=base
CAPTIO_CORS_ORIGINS=https://captio-front.onrender.com
CAPTIO_SEED_DEMO_USERS=false
```

Для ссылок YouTube на Render может потребоваться cookies-файл, потому что YouTube часто проверяет датацентровые IP. Рекомендуемый вариант: добавить cookies как Render Secret File и задать:

```text
CAPTIO_YTDLP_COOKIES_FILE=/etc/secrets/youtube_cookies.txt
```

Файл должен быть в формате Netscape/Mozilla cookies.txt. Backend Docker image устанавливает Deno, а Python-зависимости включают `yt-dlp[default]` с `yt-dlp-ejs`; вместе они нужны `yt-dlp` для новых YouTube JavaScript challenge.
Render Secret File монтируется read-only, поэтому backend перед запуском `yt-dlp` копирует cookies в runtime-файл внутри `CAPTIO_DATA_DIR`; исходный файл в `/etc/secrets` не изменяется.

Для frontend service задается URL backend:

```text
REACT_APP_API_BASE_URL=https://captio-lnrg.onrender.com
```

Если для backend подключен Render Disk, его нужно смонтировать в `/app/data`, чтобы SQLite-база, загруженные файлы и результаты обработки сохранялись после перезапуска сервиса.

## Тестирование

Локальный прогон после исправлений:

```text
135 passed, 1 warning in 44.85s
```

Проверенные группы:

- auth: регистрация, вход, `/me`, ошибки `401`, `409`, `422`;
- RBAC: admin/user доступы и недопустимые роли;
- tasks CRUD: create/read/update/delete и `404`;
- videos: upload, status, SRT, лимиты размера и расширений;
- fuzzing: 129 сгенерированных негативных и граничных API-кейсов.

## CI

Workflow `.github/workflows/ci.yml` запускает:

- backend: Python 3.12, Poetry, `pytest -q`;
- frontend: Node.js 22, `npm ci`, `npm run build`.
