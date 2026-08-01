import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base


class Equipment(Base):
    __tablename__ = "equipment"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(160), index=True)
    category: Mapped[str] = mapped_column(String(30), index=True)  # backpack, footwear, tent, sleeping_bag
    brand: Mapped[str | None] = mapped_column(String(80), nullable=True, index=True)
    price_cny: Mapped[float | None] = mapped_column(Float, nullable=True)
    weight_g: Mapped[float | None] = mapped_column(Float, nullable=True)
    specifications: Mapped[str] = mapped_column(Text)
    suitable_scenarios: Mapped[str] = mapped_column(Text)
    source_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    submitted_by: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
