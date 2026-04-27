FROM python:3.12-slim

# Системные зависимости для ffmpeg и whisper
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Устанавливаем poetry
RUN pip install poetry

# Копируем зависимости отдельно — для кэширования слоёв
COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false \
    && poetry install --no-root

# Копируем код
COPY src/ ./src/

# Модель кэшируем отдельно (большой файл ~3GB)
COPY models/ ./models/

ENV PORT=8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]