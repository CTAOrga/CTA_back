import logging
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.car_model import CarModel
from app.models.inventory import Inventory

logger = logging.getLogger(__name__)


def create_inventory_item(
    db: Session,
    *,
    agency_id: int,
    brand: str,
    model: str,
    quantity: int,
) -> Inventory:

    car_model = (
        db.query(CarModel)
        .filter(
            CarModel.brand == brand,
            CarModel.model == model,
        )
        .first()
    )

    if not car_model:
        raise HTTPException(
            status_code=400,
            detail=f"El modelo {brand} {model} no existe en el catálogo",
        )

    # Podrías consolidar si ya existe uno igual (agency+car_model+is_used)
    existing = (
        db.query(Inventory)
        .filter(
            Inventory.agency_id == agency_id,
            Inventory.car_model_id == car_model.id,
        )
        .first()
    )
    if existing:
        existing.quantity += quantity
        db.add(existing)
        db.commit()
        db.refresh(existing)
        return existing

    inv = Inventory(
        agency_id=agency_id,
        car_model_id=car_model.id,
        quantity=quantity,
    )
    db.add(inv)
    db.commit()
    db.refresh(inv)
    return inv


def list_inventory_items(
    db: Session,
    *,
    agency_id: int,
    page: int = 1,
    page_size: int = 20,
    brand: Optional[str] = None,
    model: Optional[str] = None,
):
    if page < 1:
        page = 1
    if page_size < 1:
        page_size = 20

    query = (
        db.query(Inventory, CarModel)
        .join(CarModel, Inventory.car_model_id == CarModel.id)
        .filter(Inventory.agency_id == agency_id)
    )

    if brand:
        query = query.filter(CarModel.brand.ilike(f"%{brand}%"))
    if model:
        query = query.filter(CarModel.model.ilike(f"%{model}%"))

    total = query.count()
    offset = (page - 1) * page_size

    rows = (
        query.order_by(CarModel.brand.asc(), CarModel.model.asc())
        .offset(offset)
        .limit(page_size)
        .all()
    )

    items = []
    for inv, car_model in rows:
        items.append(
            {
                "id": inv.id,
                "car_model_id": car_model.id,
                "brand": car_model.brand,
                "model": car_model.model,
                "quantity": inv.quantity,
                "is_used": inv.is_used,
            }
        )

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
    }


def get_inventory_item_for_agency(
    db: Session,
    *,
    inventory_id: int,
    agency_id: int,
) -> Inventory:
    inv = (
        db.query(Inventory)
        .filter(
            Inventory.id == inventory_id,
            Inventory.agency_id == agency_id,
        )
        .first()
    )
    if not inv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item de inventario no encontrado para esta agencia",
        )
    return inv


def update_inventory_item(
    db: Session,
    *,
    inventory_id: int,
    agency_id: int,
    quantity: Optional[int] = None,
) -> Inventory:
    inv = get_inventory_item_for_agency(
        db, inventory_id=inventory_id, agency_id=agency_id
    )

    if quantity is not None:
        inv.quantity = quantity

    db.add(inv)
    db.commit()
    db.refresh(inv)
    return inv


def delete_inventory_item(
    db: Session,
    *,
    inventory_id: int,
    agency_id: int,
) -> None:
    """
    Elimina un item de inventario perteneciente a la agencia.
    """
    inv = get_inventory_item_for_agency(
        db,
        inventory_id=inventory_id,
        agency_id=agency_id,
    )

    db.delete(inv)
    db.commit()
