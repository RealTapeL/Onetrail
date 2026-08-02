import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from core.security import get_current_user
from database.session import get_db
from equipment.models import Equipment, EquipmentReview
from equipment.schemas import (
    EquipmentCreate,
    EquipmentResponse,
    EquipmentReviewCreate,
    EquipmentReviewResponse,
    EquipmentReviewSample,
    EquipmentReviewsSummary,
)
from identity.models import User

router = APIRouter(prefix="/equipment", tags=["装备比选"])


def get_equipment_or_404(db: Session, equipment_id: str) -> Equipment:
    item = db.get(Equipment, equipment_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="装备不存在")
    return item


def serialize_equipment(db: Session, item: Equipment) -> EquipmentResponse:
    ratings = db.scalars(select(EquipmentReview.rating).where(EquipmentReview.equipment_id == item.id)).all()
    review_count = len(ratings)
    average_rating = round(sum(ratings) / review_count, 1) if review_count else None
    return EquipmentResponse(
        id=item.id,
        name=item.name,
        category=item.category,
        brand=item.brand,
        price_cny=item.price_cny,
        weight_g=item.weight_g,
        specifications=json.loads(item.specifications),
        suitable_scenarios=json.loads(item.suitable_scenarios),
        source_url=item.source_url,
        image_url=item.image_url,
        average_rating=average_rating,
        review_count=review_count,
    )


def serialize_review(review: EquipmentReview) -> EquipmentReviewResponse:
    return EquipmentReviewResponse(
        id=review.id,
        author_id=review.author_id,
        rating=review.rating,
        content=review.content,
        created_at=review.created_at,
    )


@router.get("", response_model=list[EquipmentResponse])
def list_equipment(
    category: str | None = None,
    brand: str | None = None,
    db: Session = Depends(get_db),
) -> list[EquipmentResponse]:
    statement = select(Equipment).order_by(Equipment.created_at.desc())
    if category:
        statement = statement.where(Equipment.category == category)
    if brand:
        statement = statement.where(Equipment.brand == brand)
    return [serialize_equipment(db, item) for item in db.scalars(statement).all()]


@router.post("", response_model=EquipmentResponse, status_code=status.HTTP_201_CREATED)
def create_equipment(
    payload: EquipmentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> EquipmentResponse:
    item = Equipment(
        name=payload.name,
        category=payload.category,
        brand=payload.brand,
        price_cny=payload.price_cny,
        weight_g=payload.weight_g,
        specifications=json.dumps(payload.specifications, ensure_ascii=False),
        suitable_scenarios=json.dumps(payload.suitable_scenarios, ensure_ascii=False),
        source_url=str(payload.source_url) if payload.source_url else None,
        image_url=str(payload.image_url) if payload.image_url else None,
        submitted_by=current_user.id,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return serialize_equipment(db, item)


@router.get("/reviews/summary", response_model=EquipmentReviewsSummary)
def get_equipment_reviews_summary(db: Session = Depends(get_db)) -> EquipmentReviewsSummary:
    total_count = len(db.scalars(select(EquipmentReview.id)).all())
    latest = db.scalar(
        select(EquipmentReview)
        .where(EquipmentReview.content.is_not(None))
        .order_by(EquipmentReview.created_at.desc())
        .limit(1)
    )
    sample = None
    if latest is not None:
        item = db.get(Equipment, latest.equipment_id)
        sample = EquipmentReviewSample(
            quote=latest.content or "",
            equipment_id=latest.equipment_id,
            equipment_name=item.name if item else "",
        )
    return EquipmentReviewsSummary(total_count=total_count, sample=sample)


@router.get("/{equipment_id}", response_model=EquipmentResponse)
def get_equipment(equipment_id: str, db: Session = Depends(get_db)) -> EquipmentResponse:
    return serialize_equipment(db, get_equipment_or_404(db, equipment_id))


@router.get("/{equipment_id}/reviews", response_model=list[EquipmentReviewResponse])
def get_equipment_reviews(equipment_id: str, db: Session = Depends(get_db)) -> list[EquipmentReviewResponse]:
    get_equipment_or_404(db, equipment_id)
    reviews = db.scalars(
        select(EquipmentReview)
        .where(EquipmentReview.equipment_id == equipment_id)
        .order_by(EquipmentReview.created_at.desc())
    ).all()
    return [serialize_review(review) for review in reviews]


@router.post(
    "/{equipment_id}/reviews",
    response_model=EquipmentReviewResponse,
    status_code=status.HTTP_201_CREATED,
)
def post_equipment_review(
    equipment_id: str,
    payload: EquipmentReviewCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> EquipmentReviewResponse:
    get_equipment_or_404(db, equipment_id)
    review = EquipmentReview(
        equipment_id=equipment_id,
        author_id=current_user.id,
        rating=payload.rating,
        content=payload.content,
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return serialize_review(review)
