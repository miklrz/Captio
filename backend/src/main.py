import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import init_db
from .helpers import cleanup_old_uploads
from .routers import auth, tasks, videos
from .settings import get_settings

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description="API сервиса автоматической генерации субтитров и перевода для видео.",
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
from contextlib import asynccontextmanager
from fastapi import FastAPI

from src.database import init_db
from src.helpers import cleanup_old_uploads


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    cleanup_old_uploads()
    yield


app = FastAPI(
    title="Captio API",
    lifespan=lifespan,
)


@app.get("/health")
@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "service": settings.app_name}


app.include_router(auth.router)
app.include_router(tasks.router)
app.include_router(videos.router)


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    uvicorn.run("src.main:app", host="0.0.0.0", port=port)
