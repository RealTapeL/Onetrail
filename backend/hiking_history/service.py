from dataclasses import dataclass
from statistics import median

from sqlalchemy import select
from sqlalchemy.orm import Session

from hiking_history.models import HikingActivity


@dataclass(frozen=True)
class CapabilityProfile:
    samples: int
    typical_distance_km: float | None
    typical_elevation_gain_m: float | None
    typical_duration_min: float | None


def get_capability_profile(db: Session, user_id: str, sample_limit: int = 30) -> CapabilityProfile:
    activities = db.scalars(
        select(HikingActivity)
        .where(HikingActivity.user_id == user_id)
        .order_by(HikingActivity.completed_on.desc())
        .limit(sample_limit)
    ).all()
    if not activities:
        return CapabilityProfile(0, None, None, None)
    return CapabilityProfile(
        samples=len(activities),
        typical_distance_km=round(median(item.distance_km for item in activities), 2),
        typical_elevation_gain_m=round(median(item.elevation_gain_m for item in activities), 1),
        typical_duration_min=round(median(item.duration_min for item in activities), 1),
    )

