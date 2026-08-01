from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import get_settings
from database.base import Base
from database.session import engine
from equipment import models as equipment_models  # noqa: F401 - registers metadata
from equipment.router import router as equipment_router
from hiking_history import models as hiking_history_models  # noqa: F401 - registers metadata
from hiking_history.router import router as hiking_history_router
from identity import models as identity_models  # noqa: F401 - registers metadata
from identity.router import profile_router, router as identity_router
from platform_services.router import meta_router as platform_meta_router
from platform_services.router import router as platform_router
from recommendation.router import integration_router, meta_router, router as recommendation_router
from route_content import models as route_models  # noqa: F401 - registers metadata
from route_content.router import router as route_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    # This only creates empty schema tables. It never inserts demo routes or other business data.
    Base.metadata.create_all(bind=engine)
    yield


settings = get_settings()
app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
