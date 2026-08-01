from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from database.session import get_db
from identity.models import User
from route_content.models import HikingRoute

router = APIRouter(tags=["基础能力"])
meta_router = APIRouter(prefix="/meta", tags=["基础能力"])


@router.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@meta_router.get("/brand-stats")
def brand_stats(db: Session = Depends(get_db)) -> dict[str, int]:
    route_count = db.scalar(select(func.count()).select_from(HikingRoute)) or 0
    hiker_count = db.scalar(select(func.count()).select_from(User)) or 0
    city_count = db.scalar(select(func.count(func.distinct(HikingRoute.region)))) or 0
    return {"routeCount": route_count, "hikerCount": hiker_count, "cityCount": city_count}
