from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from core.security import get_current_user
from database.session import get_db
from hiking_history.models import HikingActivity
from hiking_history.schemas import ActivityCreate, ActivityResponse
from identity.models import User
from route_content.models import HikingRoute

router = APIRouter(prefix="/history", tags=["徒步历史"])


@router.post("", response_model=ActivityResponse, status_code=status.HTTP_201_CREATED)
def create_activity(
    payload: ActivityCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ActivityResponse:
    if payload.route_id and db.get(HikingRoute, payload.route_id) is None:
        raise HTTPException(status_code=404, detail="关联路线不存在")
    activity = HikingActivity(user_id=current_user.id, **payload.model_dump())
    db.add(activity)
    db.commit()
    db.refresh(activity)
    return activity


@router.get("", response_model=list[ActivityResponse])
def list_activities(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ActivityResponse]:
    return list(
        db.scalars(
            select(HikingActivity)
            .where(HikingActivity.user_id == current_user.id)
            .order_by(HikingActivity.completed_on.desc())
        )
    )

