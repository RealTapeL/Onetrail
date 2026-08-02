import json

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from core.logging import get_client_logger
from database.session import get_db
from identity.models import User
from route_content.models import HikingRoute, RouteFavorite, RouteReview

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


@meta_router.get("/community-pulse")
def community_pulse(db: Session = Depends(get_db)) -> dict:
    """社区动态聚合：热门路线（评价+收藏数排序）与最新评价，均为库内真实数据。"""
    routes = db.scalars(select(HikingRoute)).all()
    review_stats = {
        row[0]: (row[1], row[2])
        for row in db.execute(
            select(RouteReview.route_id, func.count(), func.avg(RouteReview.rating)).group_by(RouteReview.route_id)
        ).all()
    }
    fav_counts = {
        row[0]: row[1]
        for row in db.execute(select(RouteFavorite.route_id, func.count()).group_by(RouteFavorite.route_id)).all()
    }
    hot = sorted(
        routes,
        key=lambda r: review_stats.get(r.id, (0, None))[0] + fav_counts.get(r.id, 0),
        reverse=True,
    )[:5]
    hot_routes = [
        {
            "id": r.id,
            "title": r.title,
            "region": r.region,
            "review_count": review_stats.get(r.id, (0, None))[0],
            "average_rating": (
                round(review_stats[r.id][1], 1) if r.id in review_stats and review_stats[r.id][1] is not None else None
            ),
            "favorite_count": fav_counts.get(r.id, 0),
        }
        for r in hot
    ]
    latest = db.scalars(select(RouteReview).order_by(RouteReview.created_at.desc()).limit(8)).all()
    route_by_id = {r.id: r for r in routes}
    author_ids = {rv.author_id for rv in latest}
    authors = (
        {u.id: u for u in db.scalars(select(User).where(User.id.in_(author_ids))).all()} if author_ids else {}
    )
    latest_reviews = [
        {
            "id": rv.id,
            "route_id": rv.route_id,
            "route_title": route_by_id[rv.route_id].title if rv.route_id in route_by_id else "未知路线",
            "author": authors[rv.author_id].display_name if rv.author_id in authors else "徒步者",
            "rating": rv.rating,
            "content": rv.content,
            "impression_tags": json.loads(rv.impression_tags or "[]"),
            "created_at": rv.created_at.isoformat() if rv.created_at else None,
        }
        for rv in latest
    ]
    return {"hot_routes": hot_routes, "latest_reviews": latest_reviews}


class ClientLogPayload(BaseModel):
    level: str = Field(default="error", max_length=10)
    message: str = Field(max_length=2000)
    stack: str | None = Field(default=None, max_length=4000)
    url: str | None = Field(default=None, max_length=500)
    ts: str | None = Field(default=None, max_length=40)


@logs_router.post("/client", status_code=204)
def client_log(payload: ClientLogPayload) -> None:
    """接收前端上报的运行时错误，写入 logs/frontend.log。无需鉴权，字段限长防灌水。"""
    level = payload.level.lower()
    log = get_client_logger().error if level in ("error", "fatal") else get_client_logger().warning
    # 换行替换为空格，防止伪造多行日志
    clean = lambda s: s.replace("\n", " ⏎ ") if s else s
    parts = [clean(payload.message)]
    if payload.url:
        parts.append(f"url={clean(payload.url)}")
    if payload.ts:
        parts.append(f"ts={payload.ts}")
    if payload.stack:
        parts.append(f"stack={clean(payload.stack)}")
    log(" | ".join(parts))
