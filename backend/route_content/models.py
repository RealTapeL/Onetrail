import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base


class HikingRoute(Base):
    __tablename__ = "hiking_routes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title: Mapped[str] = mapped_column(String(160), index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    region: Mapped[str] = mapped_column(String(120), index=True)
    start_latitude: Mapped[float] = mapped_column(Float)
    start_longitude: Mapped[float] = mapped_column(Float)
    distance_km: Mapped[float] = mapped_column(Float)
    elevation_gain_m: Mapped[int] = mapped_column(Integer)
    estimated_duration_min: Mapped[int] = mapped_column(Integer)
    difficulty: Mapped[str] = mapped_column(String(30), index=True)
    video_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_by: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class RouteTag(Base):
    __tablename__ = "route_tags"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    route_id: Mapped[str] = mapped_column(ForeignKey("hiking_routes.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(60), index=True)
    category: Mapped[str] = mapped_column(String(30), index=True)  # scenery, terrain, safety, vibe
    safety_note: Mapped[str | None] = mapped_column(Text, nullable=True)


class RouteReview(Base):
    __tablename__ = "route_reviews"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    route_id: Mapped[str] = mapped_column(ForeignKey("hiking_routes.id", ondelete="CASCADE"), index=True)
    author_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    rating: Mapped[int] = mapped_column(Integer)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    impression_tags: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
