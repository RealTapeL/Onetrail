from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.security import get_current_user
from database.session import get_db
from identity.models import User
from recommendation.providers import (
    ProviderNotConfigured,
    ProviderRequestError,
    get_map_provider,
    get_weather_provider,
    integration_status,
)
from recommendation.schemas import IntegrationStatus, RecommendationRequest, RecommendationResponse
from recommendation.service import recommend

router = APIRouter(prefix="/recommendations", tags=["智能线路推荐"])
integration_router = APIRouter(prefix="/integrations", tags=["基础能力"])


@router.post("/plan", response_model=RecommendationResponse)
def create_recommendation_plan(
    payload: RecommendationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RecommendationResponse:
    try:
        return recommend(db, current_user.id, payload, get_weather_provider(), get_map_provider())
    except ProviderNotConfigured as exc:
        raise HTTPException(status_code=status.HTTP_424_FAILED_DEPENDENCY, detail=str(exc)) from exc
    except ProviderRequestError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc


@integration_router.get("/status", response_model=IntegrationStatus)
def get_integration_status() -> IntegrationStatus:
    weather, map_ready = integration_status()
    return IntegrationStatus(
        weather=weather,
        map=map_ready,
        message="未配置的外部能力不会生成或返回虚构数据。",
    )
