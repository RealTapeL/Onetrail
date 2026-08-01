import json

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from core.security import get_current_user
from database.session import get_db
from equipment.models import Equipment
from equipment.schemas import EquipmentCreate, EquipmentResponse
from identity.models import User

router = APIRouter(prefix="/equipment", tags=["装备比选"])


def serialize_equipment(item: Equipment) -> EquipmentResponse:
    return EquipmentResponse(
        id=item.id,
        name=item.name,
        category=item.category,
        brand=item.brand,
        price_cny=item.price_cny,
        weight_g=item.weight_g,
        specifications=json.loads(item.specifications),
        suitable_scenarios=json.loads(item.suitable_scenarios),
        source_url=item.source_url,
    )


@router.get("", response_model=list[EquipmentResponse])
def list_equipment(
    category: str | None = None,
    brand: str | None = None,
    db: Session = Depends(get_db),
) -> list[EquipmentResponse]:
    statement = select(Equipment).order_by(Equipment.created_at.desc())
    if category:
        statement = statement.where(Equipment.category == category)
    if brand:
        statement = statement.where(Equipment.brand == brand)
    return [serialize_equipment(item) for item in db.scalars(statement).all()]


@router.post("", response_model=EquipmentResponse, status_code=status.HTTP_201_CREATED)
def create_equipment(
    payload: EquipmentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> EquipmentResponse:
    item = Equipment(
        name=payload.name,
        category=payload.category,
        brand=payload.brand,
        price_cny=payload.price_cny,
        weight_g=payload.weight_g,
        specifications=json.dumps(payload.specifications, ensure_ascii=False),
        suitable_scenarios=json.dumps(payload.suitable_scenarios, ensure_ascii=False),
        source_url=str(payload.source_url) if payload.source_url else None,
        submitted_by=current_user.id,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return serialize_equipment(item)


@router.get("/{equipment_id}", response_model=EquipmentResponse)
def get_equipment(equipment_id: str, db: Session = Depends(get_db)) -> EquipmentResponse:
    from fastapi import HTTPException

    item = db.get(Equipment, equipment_id)
    if item is None:
        raise HTTPException(status_code=404, detail="装备不存在")
    return serialize_equipment(item)
