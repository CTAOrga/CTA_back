from datetime import datetime
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.purchase import Purchase, PurchaseStatus
from app.models.listing import Listing
from app.models.user import User
from app.models.agency import Agency
from app.schemas.admin_purchases import AdminPurchaseOut, PaginatedAdminPurchasesOut


def list_purchases_for_admin(
    db: Session,
    page: int = 1,
    page_size: int = 20,
    q: Optional[str] = None,  # busca en email, auto, agencia
    status: Optional[PurchaseStatus] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
) -> PaginatedAdminPurchasesOut:

    # Query base
    query = (
        db.query(Purchase, Listing, User, Agency)
        .join(Listing, Purchase.listing_id == Listing.id)
        .join(User, Purchase.buyer_id == User.id)
        .join(Agency, Listing.agency_id == Agency.id)
    )

    # Filtro por status (opcional)
    if status is not None:
        query = query.filter(Purchase.status == status)

    # Filtro por rango de fechas
    if date_from is not None:
        query = query.filter(Purchase.created_at >= date_from)
    if date_to is not None:
        query = query.filter(Purchase.created_at <= date_to)

    # Búsqueda global (email, marca, modelo, agencia)
    if q:
        like = f"%{q}%"
        query = query.filter(
            (User.email.ilike(like))
            | (Listing.brand.ilike(like))
            | (Listing.model.ilike(like))
            | (Agency.name.ilike(like))
        )

    total = query.count()

    # Paginación
    if page < 1:
        page = 1
    if page_size < 1:
        page_size = 20

    offset = (page - 1) * page_size

    rows = (
        query.order_by(Purchase.created_at.desc()).offset(offset).limit(page_size).all()
    )

    items: list[AdminPurchaseOut] = []

    for purchase, listing, buyer, agency in rows:
        total_amount = float(purchase.unit_price_amount) * purchase.quantity

        items.append(
            AdminPurchaseOut(
                id=purchase.id,
                listing_id=purchase.listing_id,
                buyer_id=purchase.buyer_id,
                buyer_email=buyer.email,
                agency_id=agency.id,
                agency_name=agency.name,
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

    return PaginatedAdminPurchasesOut(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )
