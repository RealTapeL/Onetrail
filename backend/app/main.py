from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

from core.config import get_settings
from core.logging import setup_logging
from database.base import Base
from database.session import engine
from equipment import models as equipment_models  # noqa: F401 - registers metadata
from equipment.router import router as equipment_router
from hiking_history import models as hiking_history_models  # noqa: F401 - registers metadata
from hiking_history.router import router as hiking_history_router
from identity import models as identity_models  # noqa: F401 - registers metadata
from identity.router import profile_router, router as identity_router
from platform_services.router import logs_router as platform_logs_router
from platform_services.router import meta_router as platform_meta_router
from platform_services.router import router as platform_router
from recommendation.router import integration_router, meta_router, router as recommendation_router
from route_content import models as route_models  # noqa: F401 - registers metadata
from route_content.router import router as route_router

setup_logging()


@asynccontextmanager
async def lifespan(_: FastAPI):
    # This only creates empty schema tables. It never inserts demo routes or other business data.
    if settings.auto_create_schema:
        Base.metadata.create_all(bind=engine)
    yield


settings = get_settings()
app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    lifespan=lifespan,
    docs_url=None if settings.is_production else "/docs",
    redoc_url=None if settings.is_production else "/redoc",
    openapi_url=None if settings.is_production else "/openapi.json",
)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.allowed_host_list)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
)


@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "no-referrer")
    response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=(self)")
    if settings.is_production and request.url.scheme == "https":
        response.headers.setdefault("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
    if request.url.path.startswith("/api/v1/auth") or request.url.path.startswith("/api/v1/profile"):
        response.headers.setdefault("Cache-Control", "no-store")
    return response

app.include_router(platform_router)
app.include_router(identity_router, prefix="/api/v1")
app.include_router(profile_router, prefix="/api/v1")
app.include_router(route_router, prefix="/api/v1")
app.include_router(recommendation_router, prefix="/api/v1")
app.include_router(equipment_router, prefix="/api/v1")
app.include_router(hiking_history_router, prefix="/api/v1")
app.include_router(integration_router, prefix="/api/v1")
app.include_router(meta_router, prefix="/api/v1")
app.include_router(platform_meta_router, prefix="/api/v1")
app.include_router(platform_logs_router, prefix="/api/v1")


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """兜底：未捕获异常（含数据库错误）记录到 logs/backend.log 后返回 500。"""
    import logging

    logging.getLogger("onetrail.backend").exception(
        "未处理异常 %s %s: %s", request.method, request.url.path, exc
    )
    return JSONResponse(status_code=500, content={"detail": "服务器内部错误"})
