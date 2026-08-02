import json
from collections import Counter

from fastapi import HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from route_content.models import HikingRoute, RouteReview, RouteTag
from route_content.schemas import ImpressionStat, ReviewResponse, RouteCreate, RouteDetail, RouteSummary


DIFFICULTY_LEVELS = {"easy": 1, "moderate": 2, "hard": 4, "expert": 5}


def difficulty_level(difficulty: str) -> int:
    return DIFFICULTY_LEVELS.get(difficulty, 0)


def get_route_or_404(db: Session, route_id: str) -> HikingRoute:
    route = db.get(HikingRoute, route_id)
    if route is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="路线不存在")
    return route


def route_tags(db: Session, route_id: str) -> list[RouteTag]:
    return list(db.scalars(select(RouteTag).where(RouteTag.route_id == route_id).order_by(RouteTag.name)))


def _review_stats(db: Session, route_id: str) -> tuple[float | None, int, list[ImpressionStat]]:
    reviews = db.scalars(select(RouteReview).where(RouteReview.route_id == route_id)).all()
    if not reviews:
        return None, 0, []
    average = round(sum(review.rating for review in reviews) / len(reviews), 1)
    counter: Counter[str] = Counter()
    for review in reviews:
        counter.update(json.loads(review.impression_tags or "[]"))
    stats = [ImpressionStat(tag=tag, count=count) for tag, count in counter.most_common()]
    return average, len(reviews), stats


def _average_rating(db: Session, route_id: str) -> float | None:
    average, _, _ = _review_stats(db, route_id)
    return average


def serialize_route_summary(db: Session, route: HikingRoute) -> RouteSummary:
    return RouteSummary(
        id=route.id,
        title=route.title,
        region=route.region,
        distance_km=route.distance_km,
        elevation_gain_m=route.elevation_gain_m,
        estimated_duration_min=route.estimated_duration_min,
        difficulty=route.difficulty,
        level=difficulty_level(route.difficulty),
        average_rating=_average_rating(db, route.id),
    )


def serialize_route_detail(db: Session, route: HikingRoute) -> RouteDetail:
    average_rating, review_count, impression_stats = _review_stats(db, route.id)
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
        level=difficulty_level(route.difficulty),
        suitable_for=route.suitable_for,
        video_url=route.video_url,
        tags=route_tags(db, route.id),
        average_rating=average_rating,
        review_count=review_count,
        impression_stats=impression_stats,
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
    db: Session,
    query: str | None,
    region: str | None,
    difficulty: str | None,
    tag: str | None,
    level_min: int | None,
    level_max: int | None,
    max_distance_km: float | None,
    crowd: str | None,
    page: int,
    page_size: int,
) -> tuple[int, list[RouteSummary]]:
    statement = select(HikingRoute).order_by(HikingRoute.created_at.desc())
    if query:
        statement = statement.where(
            or_(
                HikingRoute.title.contains(query),
                HikingRoute.description.contains(query),
                HikingRoute.region.contains(query),
            )
        )
    if region:
        statement = statement.where(HikingRoute.region == region)
    if difficulty:
        statement = statement.where(HikingRoute.difficulty == difficulty)
    if tag:
        statement = statement.join(RouteTag).where(RouteTag.name == tag)
    if max_distance_km is not None:
        statement = statement.where(HikingRoute.distance_km <= max_distance_km)
    if crowd:
        statement = statement.where(HikingRoute.suitable_for.contains(crowd))
    routes = list(db.scalars(statement).unique().all())
    if level_min is not None or level_max is not None:
        routes = [
            route
            for route in routes
            if (level_min is None or difficulty_level(route.difficulty) >= level_min)
            and (level_max is None or difficulty_level(route.difficulty) <= level_max)
        ]
    total = len(routes)
    start = (page - 1) * page_size
    return total, [serialize_route_summary(db, route) for route in routes[start : start + page_size]]


def serialize_review(review: RouteReview):
    return ReviewResponse(
        id=review.id,
        author_id=review.author_id,
        rating=review.rating,
        content=review.content,
        impression_tags=json.loads(review.impression_tags or "[]"),
        created_at=review.created_at,
    )
