from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.security import get_current_user
from core.rate_limit import external_request_limit
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
meta_router = APIRouter(prefix="/meta", tags=["基础能力"])


@router.post("/plan", response_model=RecommendationResponse, dependencies=[Depends(external_request_limit)])
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


@meta_router.get("/weather-tip", dependencies=[Depends(external_request_limit)])
def get_weather_tip(latitude: float, longitude: float) -> dict[str, str]:
    try:
        map_context = get_map_provider().get_context(latitude, longitude, date.today())
        forecast = get_weather_provider().get_forecast(map_context.adcode, date.today())
    except ProviderNotConfigured as exc:
        raise HTTPException(status_code=status.HTTP_424_FAILED_DEPENDENCY, detail=str(exc)) from exc
    except ProviderRequestError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
    parts = [map_context.region_name, f"今日{forecast.weather}"]
    if forecast.temperature_min_c is not None and forecast.temperature_max_c is not None:
        parts.append(f"{forecast.temperature_min_c:g}–{forecast.temperature_max_c:g}°C")
    if forecast.wind_power:
        parts.append(f"风力{forecast.wind_power}级")
    return {"text": " · ".join(parts)}


@meta_router.get("/geocode", dependencies=[Depends(external_request_limit)])
def geocode_city(city: str) -> dict:
    """城市/地名 → 坐标（S1/M1 表单的目的地输入用）。"""
    if not city.strip():
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="city 不能为空")
    try:
        location = get_map_provider().geocode_city(city.strip())
    except ProviderNotConfigured as exc:
        raise HTTPException(status_code=status.HTTP_424_FAILED_DEPENDENCY, detail=str(exc)) from exc
    except ProviderRequestError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
    return {
        "latitude": location.latitude,
        "longitude": location.longitude,
        "formatted_address": location.formatted_address,
    }
