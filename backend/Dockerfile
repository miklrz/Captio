FROM python:3.12-slim

# System dependency for Whisper/FFmpeg processing.
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN pip install poetry

# Copy dependencies first to improve Docker layer caching.
COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false \
    && poetry install --no-root

COPY src/ ./src/

RUN mkdir -p data/uploads data/outputs models/whisper

ENV PORT=8000

CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
