Captio
======

Captio - сервис автоматической генерации субтитров и перевода для видео.

Пользователь вставляет ссылку на видео, backend скачивает файл, передает его в
OpenAI Whisper, сохраняет результат обработки и возвращает текст с таймкодами.
Фронтенд умеет показать транскрипцию, историю обработок и скачать результат в
формате SRT.

Структура проекта
-----------------

- `frontend/` - React-приложение.
- `backend/` - основной Python backend на FastAPI.
- `backend-node/` - старый учебный Node.js backend. Его логика авторизации,
  ролей, пользователей и задач перенесена в Python backend.

Основные возможности
--------------------

- Генерация субтитров по ссылке на видео.
- Загрузка видео с Яндекс Диска.
- Базовая поддержка YouTube и прямых ссылок.
- Распознавание речи через Whisper.
- Возврат полного текста и сегментов с таймкодами.
- Формирование SRT-файла.
- История обработок.
- Регистрация и вход пользователей.
- JWT-авторизация.
- Роли `user` и `admin`.
- Защищенные маршруты.
- CRUD задач с проверкой владельца.
- Админское управление пользователями.
- прямой upload видео/аудио файла через /api/videos/upload;
- фоновая обработка задач и polling статуса через /api/videos/{job_id}/status;
- страница фронтенда /status/:id;
- режим транскрибации/перевода и выбор целевого языка;
- базовая i18n-структура интерфейса;
- ограничение размера загружаемых файлов;
- очистка старых uploads/outputs при старте и перед обработкой;
- API-тесты для upload и лимита размера.

Python backend
--------------

Backend находится в папке `backend/`.

Запуск для разработки:

```bash
cd backend
poetry install --no-root
make dev
```

После запуска API доступно на `http://localhost:8000`.

Полезные адреса:

- `GET /health` - проверка работоспособности.
- `POST /upload-video` - совместимый endpoint для фронтенда.
- `POST /api/videos` - обработка видео.
- `GET /api/videos/history` - история обработок.
- `GET /api/videos/{id}` - детали обработки.
- `GET /api/videos/{id}/srt` - скачивание SRT.
- `POST /api/auth/register` - регистрация.
- `POST /api/auth/login` - вход.
- `GET /api/auth/me` - текущий пользователь.
- `GET /api/auth/users` - список пользователей для администратора.
- `PATCH /api/auth/users/{id}/role` - изменение роли.
- `DELETE /api/auth/users/{id}` - удаление пользователя.
- `GET /api/tasks` - список задач.
- `POST /api/tasks` - создание задачи.
- `PATCH /api/tasks/{id}` - изменение задачи.
- `DELETE /api/tasks/{id}` - удаление задачи.

Тестовые пользователи создаются автоматически при первом запуске:

- `admin / admin123`, роль `admin`.
- `paimon / 123456`, роль `user`.

Настройки backend
-----------------

Настройки можно передать через переменные окружения:

- `CAPTIO_DATA_DIR` - папка данных, по умолчанию `data`.
- `CAPTIO_DB_PATH` или `DATABASE_PATH` - путь к SQLite базе.
- `CAPTIO_JWT_SECRET` - секрет для JWT.
- `CAPTIO_JWT_EXPIRES_HOURS` - срок жизни токена.
- `CAPTIO_WHISPER_MODEL` - модель Whisper, по умолчанию `large-v3`.
- `CAPTIO_CORS_ORIGINS` - разрешенные origins для фронтенда.

Frontend
--------

Фронтенд находится в папке `frontend/`.

```bash
cd frontend
npm install
npm start
```

Фронтенд ожидает Python backend на `http://localhost:8000`.

Docker
------

Backend можно собрать в Docker:

```bash
cd backend
make build
make run
```
