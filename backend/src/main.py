import os
from contextlib import asynccontextmanager
import logging
import time

from fastapi import Request
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import init_db
from .helpers import cleanup_old_uploads
from .routers import auth, tasks, videos
from .settings import get_settings

settings = get_settings()
logger = logging.getLogger("captio.api")
logging.basicConfig(level=os.getenv("CAPTIO_LOG_LEVEL", "INFO"))


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    cleanup_old_uploads()
    yield


app = FastAPI(
    title=settings.app_name,
    description="API сервиса автоматической генерации субтитров и перевода для видео.",
    version="0.3.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_origin_regex=settings.cors_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_logging(request: Request, call_next):
    started = time.perf_counter()
    origin = request.headers.get("origin", "-")
    try:
        response = await call_next(request)
    except Exception:
        logger.exception(
            "request_failed method=%s path=%s origin=%s",
            request.method,
            request.url.path,
            origin,
        )
        raise

    duration_ms = (time.perf_counter() - started) * 1000
    logger.info(
        "request method=%s path=%s status=%s origin=%s duration_ms=%.1f",
        request.method,
        request.url.path,
        response.status_code,
        origin,
        duration_ms,
    )
    if request.method == "OPTIONS" and response.status_code >= 400:
        logger.warning(
            "cors_preflight_rejected path=%s origin=%s request_method=%s request_headers=%s allowed_origins=%s allowed_origin_regex=%s",
            request.url.path,
            origin,
            request.headers.get("access-control-request-method", "-"),
            request.headers.get("access-control-request-headers", "-"),
            settings.cors_origins,
            settings.cors_origin_regex,
        )
    return response


@app.get("/health")
@app.get("/api/health")
def health() -> dict:
    return {
        "status": "ok",
        "service": settings.app_name,
        "environment": settings.environment,
    }


@app.get("/")
@app.head("/")
def root() -> dict:
    return health()


app.include_router(auth.router)
app.include_router(tasks.router)
app.include_router(videos.router)


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    uvicorn.run("src.main:app", host="0.0.0.0", port=port)
