from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class ActivityCreate(BaseModel):
    route_id: str | None = None
    completed_on: date
    distance_km: float = Field(gt=0, le=1000)
    elevation_gain_m: int = Field(ge=0, le=30000)
    duration_min: int = Field(gt=0, le=10080)
    rating: int | None = Field(default=None, ge=1, le=5)


class ActivityResponse(ActivityCreate):
    model_config = ConfigDict(from_attributes=True)
    id: str
    user_id: str
    created_at: datetime | None

