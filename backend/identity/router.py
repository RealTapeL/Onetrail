import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from core.security import create_access_token, get_current_user, hash_password, verify_password
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


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> User:
    if db.scalar(select(User).where(User.email == payload.email)):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="邮箱已注册")
    user = User(email=payload.email, display_name=payload.display_name, password_hash=hash_password(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    user = db.scalar(select(User).where(User.email == payload.email))
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
    )


@profile_router.put("/preferences", response_model=PreferenceResponse)
def update_preferences(
    payload: PreferenceUpsert,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PreferenceResponse:
    preference = db.get(HikingPreference, current_user.id) or HikingPreference(user_id=current_user.id)
    preference.max_distance_km = payload.max_distance_km
    preference.max_elevation_gain_m = payload.max_elevation_gain_m
    preference.preferred_duration_min = payload.preferred_duration_min
    preference.difficulty_preference = payload.difficulty_preference
    preference.interests = json.dumps(payload.interests, ensure_ascii=False)
    db.add(preference)
    db.commit()
    return PreferenceResponse(**payload.model_dump())
