import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    display_name: Mapped[str] = mapped_column(String(80))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class HikingPreference(Base):
    __tablename__ = "hiking_preferences"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    max_distance_km: Mapped[float | None] = mapped_column(Float, nullable=True)
    max_elevation_gain_m: Mapped[float | None] = mapped_column(Float, nullable=True)
    preferred_duration_min: Mapped[int | None] = mapped_column(nullable=True)
    difficulty_preference: Mapped[str | None] = mapped_column(String(30), nullable=True)
    interests: Mapped[str | None] = mapped_column(Text, nullable=True)
    # TBTI 徒步者人格类型（前端测评判型，如 JUAN/WOLF/FOXI），绑定账号跨设备同步
    tbti_type: Mapped[str | None] = mapped_column(String(8), nullable=True)
