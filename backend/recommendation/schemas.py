from datetime import date

from pydantic import BaseModel, Field


class RecommendationRequest(BaseModel):
    travel_date: date
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    group_size: int = Field(default=1, ge=1, le=50)
    budget_cny: float | None = Field(default=None, ge=0)
    max_distance_km: float | None = Field(default=None, gt=0, le=300)
    max_elevation_gain_m: int | None = Field(default=None, ge=0, le=15000)
    max_duration_min: int | None = Field(default=None, gt=0, le=10080)
    owned_equipment_ids: list[str] = Field(default_factory=list)


class WeatherAssessment(BaseModel):
    weather: str
    temperature_min_c: float | None
    temperature_max_c: float | None
    wind_power: str | None
    mud_risk: str
    mud_risk_basis: str
    caution_notes: list[str]


class TransportOption(BaseModel):
    mode: str
    distance_km: float | None
    duration_min: int | None
    summary: str
    steps: list[str] = Field(default_factory=list)


class SupplyPoint(BaseModel):
    name: str
    category: str
    address: str | None
    distance_m: float | None
    location: str | None


class EquipmentSuggestion(BaseModel):
    equipment_id: str
    name: str
    category: str
    reason: str


class HikingSpot(BaseModel):
    """高德 POI 发现的周边徒步地：名称/地址/距离为真实数据，无路线参数。"""

    name: str
    category: str
    address: str | None = None
    distance_m: float | None = None
    location: str | None = None


class RecommendedRoute(BaseModel):
    route_id: str
    title: str
    region: str
    distance_km: float
    elevation_gain_m: int
    estimated_duration_min: int
    difficulty: str
    scene_tags: list[str] = Field(default_factory=list)
    score: float = Field(ge=0, le=100)
    reasons: list[str]
    risk_notes: list[str] = Field(default_factory=list)
    transport_options: list[TransportOption] = Field(default_factory=list)
    supply_points: list[SupplyPoint] = Field(default_factory=list)
    equipment_suggestions: list[EquipmentSuggestion] = Field(default_factory=list)


class RecommendationResponse(BaseModel):
    travel_date: date
    region_name: str
    data_sources: list[str]
    weather: WeatherAssessment | None = None
    capability_samples: int = 0
    routes: list[RecommendedRoute]
    alternates: list[RecommendedRoute] = Field(default_factory=list)
    hiking_spots: list[HikingSpot] = Field(default_factory=list)
    notice: str | None = None


class IntegrationStatus(BaseModel):
    weather: bool
    map: bool
    message: str
