FROM python:3.12-slim

# System dependencies for Whisper/FFmpeg processing and yt-dlp YouTube extraction.
RUN apt-get update && apt-get install -y \
    ca-certificates \
    curl \
    ffmpeg \
    unzip \
    && curl -fsSL https://deno.land/install.sh | DENO_INSTALL=/usr/local sh \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_NO_INTERACTION=1 \
    PORT=8000

RUN pip install poetry

# Copy dependencies first to improve Docker layer caching.
COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false \
    && poetry install --no-root

COPY src/ ./src/

RUN mkdir -p data/uploads data/outputs models/whisper

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD python -c "import json, os, urllib.request; port=os.getenv('PORT', '8000'); data=json.load(urllib.request.urlopen(f'http://127.0.0.1:{port}/health', timeout=3)); raise SystemExit(0 if data.get('status') == 'ok' else 1)"

CMD ["sh", "-c", "python -m uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
