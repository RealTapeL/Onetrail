import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from core.security import create_access_token, get_current_user, hash_password, verify_password
from core.rate_limit import auth_request_limit
from database.session import get_db
from identity.models import HikingPreference, User
from identity.schemas import (
    LoginRequest,
    PreferenceResponse,
    PreferenceUpsert,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)

router = APIRouter(prefix="/auth", tags=["身份与偏好"])
profile_router = APIRouter(prefix="/profile", tags=["身份与偏好"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(auth_request_limit)])
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> User:
    email = str(payload.email).lower()
    if db.scalar(select(User).where(User.email == email)):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="邮箱已注册")
    user = User(email=email, display_name=payload.display_name.strip(), password_hash=hash_password(payload.password))
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        # 并发下同邮箱注册撞唯一约束
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="邮箱已注册") from None
    db.refresh(user)
    return user


@router.post("/login", response_model=TokenResponse, dependencies=[Depends(auth_request_limit)])
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    user = db.scalar(select(User).where(User.email == str(payload.email).lower()))
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="邮箱或密码错误")
    return TokenResponse(access_token=create_access_token(user.id))


@profile_router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)) -> User:
    return current_user


@profile_router.get("/preferences", response_model=PreferenceResponse)
def get_preferences(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> PreferenceResponse:
    preference = db.get(HikingPreference, current_user.id)
    if preference is None:
        return PreferenceResponse()
    return PreferenceResponse(
        max_distance_km=preference.max_distance_km,
        max_elevation_gain_m=preference.max_elevation_gain_m,
        preferred_duration_min=preference.preferred_duration_min,
        difficulty_preference=preference.difficulty_preference,
        interests=json.loads(preference.interests or "[]"),
        tbti_type=preference.tbti_type,
    )


@profile_router.put("/preferences", response_model=PreferenceResponse)
def update_preferences(
    payload: PreferenceUpsert,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PreferenceResponse:
    # 只更新请求中显式传入的字段，避免部分提交抹掉已保存的其他偏好
    provided = payload.model_dump(exclude_unset=True)
    preference = db.get(HikingPreference, current_user.id) or HikingPreference(user_id=current_user.id)
    for field in ("max_distance_km", "max_elevation_gain_m", "preferred_duration_min", "difficulty_preference", "tbti_type"):
        if field in provided:
            setattr(preference, field, provided[field])
    if "interests" in provided:
        preference.interests = json.dumps(provided["interests"], ensure_ascii=False)
    db.add(preference)
    db.commit()
    db.refresh(preference)
    return PreferenceResponse(
        max_distance_km=preference.max_distance_km,
        max_elevation_gain_m=preference.max_elevation_gain_m,
        preferred_duration_min=preference.preferred_duration_min,
        difficulty_preference=preference.difficulty_preference,
        interests=json.loads(preference.interests or "[]"),
        tbti_type=preference.tbti_type,
    )
