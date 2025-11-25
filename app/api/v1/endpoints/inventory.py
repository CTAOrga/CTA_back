from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from app.api.deps import get_current_user, require_role
from app.db.session import get_db
from app.models.user import User, UserRole
from app.schemas.car_model import CarModelOut, CarModelCreate
from app.schemas.inventory import InventoryItemOut
from app.services import inventory as inventory_service

from app.schemas.inventory import (
    InventoryItemCreate,
    InventoryItemOut,
    PaginatedInventoryOut,
)

router = APIRouter()


@router.get(
    "",
    response_model=PaginatedInventoryOut,
    dependencies=[Depends(require_role(UserRole.agency))],
)
def list_inventory(
    brand: Optional[str] = None,
    model: Optional[str] = None,
    is_used: Optional[bool] = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.agency_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario de agencia no tiene una agency_id asociada",
        )

    return inventory_service.list_inventory_items(
        db=db,
        agency_id=current_user.agency_id,
        page=page,
        page_size=page_size,
        brand=brand,
        model=model,
        is_used=is_used,
    )


@router.post(
    "",
    response_model=InventoryItemOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role(UserRole.agency))],
)
def create_inventory_item(
    payload: InventoryItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.agency_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario de agencia no tiene una agency_id asociada",
        )

    inv = inventory_service.create_inventory_item(
        db=db,
        agency_id=current_user.agency_id,
        brand=payload.brand,
        model=payload.model,
        quantity=payload.quantity,
        is_used=payload.is_used,
    )

    # opcional: devolverlo “formateado” como en list_inventory_items
    return {
        "id": inv.id,
        "car_model_id": inv.car_model_id,
        "brand": inv.car_model.brand,
        "model": inv.car_model.model,
        "quantity": inv.quantity,
        "is_used": inv.is_used,
    }
