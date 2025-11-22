import logging
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.listing import Listing
from app.models.purchase import Purchase, PurchaseStatus
from app.models.user import User
from app.schemas.purchase import PurchaseCreate

logger = logging.getLogger(__name__)


def create_purchase_for_buyer(
    db: Session,
    buyer: User,
    payload: PurchaseCreate,
) -> Purchase:
    listing = db.get(Listing, payload.listing_id)
    if not listing:
        raise HTTPException(status_code=404, detail="Listing no encontrada")

    if listing.stock <= 0:
        raise HTTPException(
            status_code=400,
            detail="No hay stock disponible para esta oferta",
        )

    if payload.quantity > listing.stock:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Cantidad solicitada ({payload.quantity}) supera "
                f"el stock disponible ({listing.stock})"
            ),
        )

    purchase = Purchase(
        buyer_id=buyer.id,
        listing_id=listing.id,
        unit_price_amount=listing.current_price_amount,
        unit_price_currency=listing.current_price_currency,
        quantity=payload.quantity,
        status=PurchaseStatus.ACTIVE,
    )

    # Descontar stock
    listing.stock = listing.stock - payload.quantity

    db.add(purchase)
    db.add(listing)
    db.commit()
    db.refresh(purchase)

    logger.info(
        "Compra creada",
        extra={
            "purchase_id": purchase.id,
            "buyer_id": buyer.id,
            "listing_id": listing.id,
        },
    )

    return purchase


def list_purchases_for_buyer(db: Session, buyer: User) -> list[Purchase]:
    rows = (
        db.query(Purchase)
        .filter(Purchase.buyer_id == buyer.id)
        .order_by(Purchase.created_at.desc())
        .all()
    )
    return rows


def cancel_purchase_for_buyer(
    db: Session,
    buyer: User,
    purchase_id: int,
) -> Purchase:
    purchase = db.get(Purchase, purchase_id)
    if not purchase:
        raise HTTPException(status_code=404, detail="Compra no encontrada")

    if purchase.buyer_id != buyer.id:
        raise HTTPException(
            status_code=403,
            detail="No podés cancelar compras de otro usuario",
        )

    if purchase.status == PurchaseStatus.CANCELLED:
        raise HTTPException(
            status_code=400,
            detail="La compra ya está cancelada",
        )

    listing = purchase.listing
    if not listing:
        raise HTTPException(
            status_code=500,
            detail="Inconsistencia: la compra no tiene listing asociado",
        )

    # Al cancelar, devolvemos el stock
    listing.stock = listing.stock + purchase.quantity
    purchase.status = PurchaseStatus.CANCELLED

    db.add(listing)
    db.add(purchase)
    db.commit()
    db.refresh(purchase)

    logger.info(
        "Compra cancelada",
        extra={
            "purchase_id": purchase.id,
            "buyer_id": buyer.id,
            "listing_id": listing.id,
        },
    )

    return purchase


def reactivate_purchase_for_buyer(
    db: Session,
    buyer: User,
    purchase_id: int,
) -> Purchase:
    purchase = db.get(Purchase, purchase_id)
    if not purchase:
        raise HTTPException(status_code=404, detail="Compra no encontrada")

    if purchase.buyer_id != buyer.id:
        raise HTTPException(
            status_code=403,
            detail="No podés reactivar compras de otro usuario",
        )

    if purchase.status != PurchaseStatus.CANCELLED:
        raise HTTPException(
            status_code=400,
            detail="Solo se pueden reactivar compras canceladas",
        )

    listing = purchase.listing
    if not listing:
        raise HTTPException(
            status_code=500,
            detail="Inconsistencia: la compra no tiene listing asociado",
        )

    if listing.stock < purchase.quantity:
        raise HTTPException(
            status_code=400,
            detail=(
                "No hay stock suficiente para reactivar la compra. "
                f"Stock actual: {listing.stock}, cantidad de la compra: {purchase.quantity}"
            ),
        )

    # Al reactivar, volvemos a descontar stock
    listing.stock = listing.stock - purchase.quantity
    purchase.status = PurchaseStatus.ACTIVE

    db.add(listing)
    db.add(purchase)
    db.commit()
    db.refresh(purchase)

    logger.info(
        "Compra reactivada",
        extra={
            "purchase_id": purchase.id,
            "buyer_id": buyer.id,
            "listing_id": listing.id,
        },
    )

    return purchase
