from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from core.logging import get_client_logger
from database.session import get_db
from identity.models import User
from route_content.models import HikingRoute

router = APIRouter(tags=["基础能力"])
meta_router = APIRouter(prefix="/meta", tags=["基础能力"])
logs_router = APIRouter(prefix="/logs", tags=["日志"])


@router.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@meta_router.get("/brand-stats")
def brand_stats(db: Session = Depends(get_db)) -> dict[str, int]:
    route_count = db.scalar(select(func.count()).select_from(HikingRoute)) or 0
    hiker_count = db.scalar(select(func.count()).select_from(User)) or 0
    city_count = db.scalar(select(func.count(func.distinct(HikingRoute.region)))) or 0
    return {"routeCount": route_count, "hikerCount": hiker_count, "cityCount": city_count}


class ClientLogPayload(BaseModel):
    level: str = "error"
    message: str
    stack: str | None = None
    url: str | None = None
    ts: str | None = None


@logs_router.post("/client", status_code=204)
def client_log(payload: ClientLogPayload) -> None:
    """接收前端上报的运行时错误，写入 logs/frontend.log。本地开发用，无需鉴权。"""
    level = payload.level.lower()
    log = get_client_logger().error if level in ("error", "fatal") else get_client_logger().warning
    parts = [payload.message]
    if payload.url:
        parts.append(f"url={payload.url}")
    if payload.ts:
        parts.append(f"ts={payload.ts}")
    if payload.stack:
        parts.append(f"stack={payload.stack}")
    log(" | ".join(parts))
