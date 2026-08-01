from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class EquipmentCreate(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    category: str = Field(pattern="^(backpack|footwear|tent|sleeping_bag)$")
    brand: str | None = Field(default=None, max_length=80)
    price_cny: float | None = Field(default=None, ge=0)
    weight_g: float | None = Field(default=None, gt=0)
    specifications: dict[str, str | int | float | bool] = Field(default_factory=dict)
    suitable_scenarios: list[str] = Field(default_factory=list, max_length=30)
    source_url: HttpUrl | None = None


class EquipmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    category: str
    brand: str | None
    price_cny: float | None
    weight_g: float | None
    specifications: dict[str, str | int | float | bool]
    suitable_scenarios: list[str]
    source_url: str | None
    average_rating: float | None
    review_count: int


class EquipmentReviewCreate(BaseModel):
    rating: int = Field(ge=1, le=5)
    content: str | None = Field(default=None, max_length=5000)


class EquipmentReviewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    author_id: str
    rating: int
    content: str | None
    created_at: datetime | None


class EquipmentReviewSample(BaseModel):
    quote: str
    equipment_id: str
    equipment_name: str


class EquipmentReviewsSummary(BaseModel):
    total_count: int
    sample: EquipmentReviewSample | None

