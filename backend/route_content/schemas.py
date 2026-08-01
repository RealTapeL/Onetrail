from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class RouteTagInput(BaseModel):
    name: str = Field(min_length=1, max_length=60)
    category: str = Field(pattern="^(scenery|terrain|safety|vibe)$")
    safety_note: str | None = Field(default=None, max_length=2000)


class RouteTagResponse(RouteTagInput):
    model_config = ConfigDict(from_attributes=True)
    id: str


class RouteCreate(BaseModel):
    title: str = Field(min_length=1, max_length=160)
    description: str | None = Field(default=None, max_length=10000)
    region: str = Field(min_length=1, max_length=120)
    start_latitude: float = Field(ge=-90, le=90)
    start_longitude: float = Field(ge=-180, le=180)
    distance_km: float = Field(gt=0, le=1000)
    elevation_gain_m: int = Field(ge=0, le=30000)
    estimated_duration_min: int = Field(gt=0, le=10080)
    difficulty: str = Field(pattern="^(easy|moderate|hard|expert)$")
    video_url: HttpUrl | None = None
    tags: list[RouteTagInput] = Field(default_factory=list, max_length=50)


class RouteSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    region: str
    distance_km: float
    elevation_gain_m: int
    estimated_duration_min: int
    difficulty: str


class RouteDetail(RouteSummary):
    description: str | None
    start_latitude: float
    start_longitude: float
    video_url: str | None
    tags: list[RouteTagResponse]


class ReviewCreate(BaseModel):
    rating: int = Field(ge=1, le=5)
    content: str | None = Field(default=None, max_length=5000)
    impression_tags: list[str] = Field(default_factory=list, max_length=20)


class ReviewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    author_id: str
    rating: int
    content: str | None
    impression_tags: list[str]
    created_at: datetime | None

