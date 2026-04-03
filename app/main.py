from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.routers import fruit as fruit_router
from app.core.config import settings
from app.core.database import engine
from app.models import fruit 


# Lifespan (substitui @app.on_event deprecated)
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # startup: conexão com o banco está disponível via pool
    yield
    # shutdown: libera o pool de conexões
    engine.dispose()


# Aplicação
app = FastAPI(
    title=settings.APP_TITLE,
    version=settings.APP_VERSION,
    debug=settings.APP_DEBUG,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.APP_ENV == "development" else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(fruit_router.router, prefix="/api/v1")


# Health check
@app.get("/health", tags=["Infra"], include_in_schema=False)
def health() -> JSONResponse:
    return JSONResponse({"status": "ok", "version": settings.APP_VERSION})
