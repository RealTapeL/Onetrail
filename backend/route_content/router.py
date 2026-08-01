import json

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from core.security import get_current_user
from database.session import get_db
from identity.models import User
from route_content.models import HikingRoute, RouteFavorite, RouteReview
from route_content.schemas import (
    FavoriteResponse,
    ReviewCreate,
    ReviewResponse,
    RouteCreate,
    RouteDetail,
    RouteSummary,
)
from route_content.service import (
    create_route,
    get_route_or_404,
    list_routes,
    serialize_review,
    serialize_route_detail,
)

router = APIRouter(prefix="/routes", tags=["路线内容与社区"])


@router.get("", response_model=list[RouteSummary])
def get_routes(
    query: str | None = None,
    region: str | None = None,
    difficulty: str | None = None,
    tag: str | None = None,
    db: Session = Depends(get_db),
) -> list[RouteSummary]:
    return list_routes(db, query, region, difficulty, tag)


@router.post("", response_model=RouteDetail, status_code=status.HTTP_201_CREATED)
def post_route(
    payload: RouteCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RouteDetail:
    return serialize_route_detail(db, create_route(db, current_user.id, payload))


@router.get("/favorites/mine", response_model=list[RouteSummary])
def get_my_favorites(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[RouteSummary]:
    statement = (
        select(HikingRoute)
        .join(RouteFavorite, RouteFavorite.route_id == HikingRoute.id)
        .where(RouteFavorite.user_id == current_user.id)
        .order_by(RouteFavorite.created_at.desc())
    )
    return [RouteSummary.model_validate(route) for route in db.scalars(statement).all()]


@router.get("/{route_id}", response_model=RouteDetail)
def get_route(route_id: str, db: Session = Depends(get_db)) -> RouteDetail:
    return serialize_route_detail(db, get_route_or_404(db, route_id))


@router.get("/{route_id}/reviews", response_model=list[ReviewResponse])
def get_reviews(route_id: str, db: Session = Depends(get_db)) -> list[ReviewResponse]:
    get_route_or_404(db, route_id)
    reviews = db.scalars(select(RouteReview).where(RouteReview.route_id == route_id).order_by(RouteReview.created_at.desc())).all()
    return [serialize_review(review) for review in reviews]


@router.post("/{route_id}/reviews", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
def post_review(
    route_id: str,
    payload: ReviewCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ReviewResponse:
    get_route_or_404(db, route_id)
    review = RouteReview(
        route_id=route_id,
        author_id=current_user.id,
        rating=payload.rating,
        content=payload.content,
        impression_tags=json.dumps(payload.impression_tags, ensure_ascii=False),
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return serialize_review(review)


@router.post("/{route_id}/favorite", response_model=FavoriteResponse, status_code=status.HTTP_201_CREATED)
def post_favorite(
    route_id: str,
    response: Response,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> FavoriteResponse:
    get_route_or_404(db, route_id)
    favorite = db.scalar(
        select(RouteFavorite).where(
            RouteFavorite.route_id == route_id,
            RouteFavorite.user_id == current_user.id,
        )
    )
    if favorite is not None:
        response.status_code = status.HTTP_200_OK
        return FavoriteResponse(route_id=route_id, created_at=favorite.created_at)
    favorite = RouteFavorite(route_id=route_id, user_id=current_user.id)
    db.add(favorite)
    db.commit()
    db.refresh(favorite)
    return FavoriteResponse(route_id=route_id, created_at=favorite.created_at)


@router.delete("/{route_id}/favorite", status_code=status.HTTP_204_NO_CONTENT)
def delete_favorite(
    route_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    favorite = db.scalar(
        select(RouteFavorite).where(
            RouteFavorite.route_id == route_id,
            RouteFavorite.user_id == current_user.id,
        )
    )
    if favorite is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="尚未收藏该路线")
    db.delete(favorite)
    db.commit()
