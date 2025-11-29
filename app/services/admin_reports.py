from datetime import date, datetime, timedelta
from typing import Optional, List, Dict

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.agency import Agency
from app.models.favorite import Favorite
from app.models.purchase import Purchase, PurchaseStatus
from app.models.listing import Listing
from app.models.car_model import CarModel
from app.models.user import User
from app.schemas.reports import TopAgencyOut, TopBuyerOut, TopFavoriteCarOut


def top_sold_cars(
    db: Session,
    date_from: Optional[date],
    date_to: Optional[date],
    limit: int = 5,
) -> List[Dict]:

    query = (
        db.query(
            CarModel.brand.label("brand"),
            CarModel.model.label("model"),
            func.sum(Purchase.quantity).label("units_sold"),
            func.sum(Purchase.unit_price_amount * Purchase.quantity).label(
                "total_amount"
            ),
        )
        .join(Listing, Listing.id == Purchase.listing_id)
        .join(CarModel, CarModel.id == Listing.car_model_id)
        .filter(Purchase.status == PurchaseStatus.COMPLETED)
    )

    if date_from:
        query = query.filter(Purchase.created_at >= date_from)

    if date_to:
        query = query.filter(Purchase.created_at < date_to + timedelta(days=1))

    rows = (
        query.group_by(CarModel.id, CarModel.brand, CarModel.model)
        .order_by(func.sum(Purchase.quantity).desc())
        .limit(limit)
        .all()
    )

    result: List[Dict] = []
    for row in rows:
        result.append(
            {
                "brand": row.brand,
                "model": row.model,
                "units_sold": int(row.units_sold or 0),
                "total_amount": float(row.total_amount or 0.0),
            }
        )

    return result


def get_top_favorites(
    db: Session,
    date_from: datetime | None,
    date_to: datetime | None,
    limit: int = 5,
) -> list[TopFavoriteCarOut]:
    """
    Top de autos (brand + model) con más favoritos.
    El rango de fechas se aplica sobre Favorite.created_at.
    """

    query = db.query(
        Listing.brand.label("brand"),
        Listing.model.label("model"),
        func.count(Favorite.id).label("favorites_count"),
    ).join(Listing, Favorite.listing_id == Listing.id)

    if date_from is not None:
        query = query.filter(Favorite.created_at >= date_from)
    if date_to is not None:
        query = query.filter(Favorite.created_at <= date_to)

    query = (
        query.group_by(Listing.brand, Listing.model)
        .order_by(func.count(Favorite.id).desc())
        .limit(limit)
    )

    rows = query.all()

    return [
        TopFavoriteCarOut(
            brand=row.brand,
            model=row.model,
            favorites_count=int(row.favorites_count),
        )
        for row in rows
    ]


def get_top_buyers(
    db: Session,
    date_from: datetime | None,
    date_to: datetime | None,
    limit: int = 5,
) -> list[TopBuyerOut]:

    query = (
        db.query(
            User.id.label("buyer_id"),
            User.email.label("email"),
            func.count(Purchase.id).label("purchases_count"),
            func.sum(Purchase.unit_price_amount * Purchase.quantity).label(
                "total_spent"
            ),
            func.max(Purchase.created_at).label("last_purchase_at"),
        )
        .join(User, Purchase.buyer_id == User.id)
        .filter(Purchase.status == PurchaseStatus.COMPLETED)
    )

    if date_from is not None:
        query = query.filter(Purchase.created_at >= date_from)
    if date_to is not None:
        query = query.filter(Purchase.created_at <= date_to)

    query = (
        query.group_by(User.id, User.email)
        .order_by(func.count(Purchase.id).desc())
        .limit(limit)
    )

    rows = query.all()

    return [
        TopBuyerOut(
            buyer_id=row.buyer_id,
            email=row.email,
            purchases_count=int(row.purchases_count),
            total_spent=float(row.total_spent or 0),
            last_purchase_at=row.last_purchase_at,
        )
        for row in rows
    ]


def get_top_agencies(
    db: Session,
    date_from: datetime | None,
    date_to: datetime | None,
    limit: int = 5,
) -> list[TopAgencyOut]:

    query = (
        db.query(
            Agency.id.label("agency_id"),
            Agency.name.label("agency_name"),
            func.count(Purchase.id).label("sales_count"),
            func.sum(Purchase.unit_price_amount * Purchase.quantity).label(
                "total_amount"
            ),
        )
        .join(Listing, Listing.agency_id == Agency.id)
        .join(Purchase, Purchase.listing_id == Listing.id)
        .filter(Purchase.status == PurchaseStatus.COMPLETED)
    )

    if date_from is not None:
        query = query.filter(Purchase.created_at >= date_from)
    if date_to is not None:
        query = query.filter(Purchase.created_at <= date_to)

    query = (
        query.group_by(Agency.id, Agency.name)
        .order_by(func.count(Purchase.id).desc())
        .limit(limit)
    )

    rows = query.all()

    return [
        TopAgencyOut(
            agency_id=row.agency_id,
            agency_name=row.agency_name,
            sales_count=int(row.sales_count or 0),
            total_amount=float(row.total_amount or 0.0),
        )
        for row in rows
    ]
