import logging
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.listing import Listing
from app.models.purchase import Purchase, PurchaseStatus
from app.models.user import User
from app.schemas.purchase import AgencyCustomerOut, AgencySaleOut, PurchaseCreate

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
        status=PurchaseStatus.COMPLETED,
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


def list_sales_for_agency(
    db: Session,
    agency_id: int,
) -> list[AgencySaleOut]:
    """
    Devuelve todas las compras de los listings de una agencia.
    Por ahora sin paginación ni filtros, después refinamos.
    """
    rows = (
        db.query(Purchase, Listing, User)
        .join(Listing, Purchase.listing_id == Listing.id)
        .join(User, Purchase.buyer_id == User.id)
        .filter(
            Listing.agency_id == agency_id,
            Purchase.status == PurchaseStatus.COMPLETED,
        )
        .order_by(Purchase.created_at.desc())
        .all()
    )

    result: list[AgencySaleOut] = []

    for purchase, listing, buyer in rows:
        total_amount = float(purchase.unit_price_amount) * purchase.quantity

        result.append(
            AgencySaleOut(
                id=purchase.id,
                listing_id=purchase.listing_id,
                buyer_id=purchase.buyer_id,
                buyer_email=buyer.email,
                brand=listing.brand,
                model=listing.model,
                unit_price_amount=float(purchase.unit_price_amount),
                unit_price_currency=purchase.unit_price_currency,
                quantity=purchase.quantity,
                total_amount=total_amount,
                status=purchase.status,
                created_at=purchase.created_at,
            )
        )

    return result


def list_customers_for_agency(
    db: Session,
    agency_id: int,
) -> list[AgencyCustomerOut]:
    """
    Devuelve un resumen de clientes para una agencia:
    cuántas compras hicieron y cuánto gastaron.
    """
    from sqlalchemy import func

    rows = (
        db.query(
            User.id.label("customer_id"),
            User.email.label("email"),
            func.count(Purchase.id).label("total_purchases"),
            func.sum(Purchase.unit_price_amount * Purchase.quantity).label(
                "total_spent"
            ),
            func.max(Purchase.created_at).label("last_purchase_at"),
        )
        .join(Purchase, Purchase.buyer_id == User.id)
        .join(Listing, Purchase.listing_id == Listing.id)
        .filter(
            Listing.agency_id == agency_id,
            Purchase.status == PurchaseStatus.COMPLETED,
        )
        .group_by(User.id, User.email)
        .order_by(func.max(Purchase.created_at).desc())
        .all()
    )

    result: list[AgencyCustomerOut] = []

    for row in rows:
        result.append(
            AgencyCustomerOut(
                customer_id=row.customer_id,
                email=row.email,
                total_purchases=int(row.total_purchases),
                total_spent=float(row.total_spent or 0),
                last_purchase_at=row.last_purchase_at,
            )
        )

    return result
