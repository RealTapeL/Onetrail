import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base


class HikingActivity(Base):
    __tablename__ = "hiking_activities"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    route_id: Mapped[str | None] = mapped_column(ForeignKey("hiking_routes.id", ondelete="SET NULL"), nullable=True, index=True)
    completed_on: Mapped[date] = mapped_column(Date)
    distance_km: Mapped[float] = mapped_column(Float)
    elevation_gain_m: Mapped[int] = mapped_column(Integer)
    duration_min: Mapped[int] = mapped_column(Integer)
    rating: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

