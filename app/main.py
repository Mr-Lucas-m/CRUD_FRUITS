import time
import uuid
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.api.v1.routers import auth as auth_router
from app.api.v1.routers import category as category_router
from app.api.v1.routers import fruit as fruit_router
from app.api.v1.routers import stock as stock_router
from app.core.config import settings
from app.core.database import engine
from app.core.limiter import limiter
from app.core.logging import configure_logging
from app.models import category, fruit, stock_movement, user  # noqa: F401

configure_logging()
logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("startup", env=settings.APP_ENV, version=settings.APP_VERSION)
    yield
    engine.dispose()
    logger.info("shutdown")


app = FastAPI(
    title=settings.APP_TITLE,
    version=settings.APP_VERSION,
    debug=settings.APP_DEBUG,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── Rate limiting ───────────────────────────────────────────────────────────────
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    return JSONResponse(
        status_code=429,
        content={"detail": f"Rate limit excedido: {exc.detail}. Tente novamente em breve."},
    )


# ── CORS ───────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.APP_ENV == "development" else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Logging middleware ─────────────────────────────────────────────────────────
@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())
    start = time.time()
    response = await call_next(request)
    duration_ms = round((time.time() - start) * 1000, 2)
    logger.info(
        "request",
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        duration_ms=duration_ms,
        request_id=request_id,
    )
    return response


# ── Routers ────────────────────────────────────────────────────────────────────
app.include_router(fruit_router.router, prefix="/api/v1")
app.include_router(category_router.router, prefix="/api/v1")
app.include_router(stock_router.router, prefix="/api/v1")
app.include_router(auth_router.router, prefix="/api/v1")


# ── Health check ───────────────────────────────────────────────────────────────
@app.get("/health", tags=["Infra"], include_in_schema=False)
def health() -> JSONResponse:
    return JSONResponse({"status": "ok", "version": settings.APP_VERSION})
