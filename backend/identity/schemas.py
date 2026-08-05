from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=12, max_length=128)
    display_name: str = Field(min_length=1, max_length=80)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=12, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: EmailStr
    display_name: str


class PreferenceUpsert(BaseModel):
    max_distance_km: float | None = Field(default=None, gt=0, le=300)
    max_elevation_gain_m: float | None = Field(default=None, ge=0, le=15000)
    preferred_duration_min: int | None = Field(default=None, gt=0, le=4320)
    difficulty_preference: str | None = Field(default=None, max_length=30)
    interests: list[str] = Field(default_factory=list, max_length=20)
    tbti_type: str | None = Field(default=None, max_length=8)


class PreferenceResponse(PreferenceUpsert):
    pass
