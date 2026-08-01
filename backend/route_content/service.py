import json

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from route_content.models import HikingRoute, RouteReview, RouteTag
from route_content.schemas import RouteCreate, RouteDetail, RouteSummary


def get_route_or_404(db: Session, route_id: str) -> HikingRoute:
    route = db.get(HikingRoute, route_id)
    if route is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="路线不存在")
    return route


def route_tags(db: Session, route_id: str) -> list[RouteTag]:
    return list(db.scalars(select(RouteTag).where(RouteTag.route_id == route_id).order_by(RouteTag.name)))


def serialize_route_detail(db: Session, route: HikingRoute) -> RouteDetail:
    return RouteDetail(
        id=route.id,
        title=route.title,
        description=route.description,
        region=route.region,
        start_latitude=route.start_latitude,
        start_longitude=route.start_longitude,
        distance_km=route.distance_km,
        elevation_gain_m=route.elevation_gain_m,
        estimated_duration_min=route.estimated_duration_min,
        difficulty=route.difficulty,
        video_url=route.video_url,
        tags=route_tags(db, route.id),
    )


def create_route(db: Session, owner_id: str, payload: RouteCreate) -> HikingRoute:
    route = HikingRoute(
        **payload.model_dump(exclude={"tags", "video_url"}),
        video_url=str(payload.video_url) if payload.video_url else None,
        created_by=owner_id,
    )
    db.add(route)
    db.flush()
    db.add_all([RouteTag(route_id=route.id, **tag.model_dump()) for tag in payload.tags])
    db.commit()
    db.refresh(route)
    return route


def list_routes(
    db: Session, query: str | None, region: str | None, difficulty: str | None, tag: str | None
) -> list[RouteSummary]:
    statement = select(HikingRoute).order_by(HikingRoute.created_at.desc())
    if query:
        statement = statement.where(HikingRoute.title.contains(query))
    if region:
        statement = statement.where(HikingRoute.region == region)
    if difficulty:
        statement = statement.where(HikingRoute.difficulty == difficulty)
    if tag:
        statement = statement.join(RouteTag).where(RouteTag.name == tag)
    return [RouteSummary.model_validate(route) for route in db.scalars(statement).unique().all()]


def serialize_review(review: RouteReview):
    from route_content.schemas import ReviewResponse

    return ReviewResponse(
        id=review.id,
        author_id=review.author_id,
        rating=review.rating,
        content=review.content,
        impression_tags=json.loads(review.impression_tags or "[]"),
        created_at=review.created_at,
    )
