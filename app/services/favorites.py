from __future__ import annotations
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.favorite import Favorite
from app.models.listing import Listing
from app.models.user import User
from app.schemas.favorite import FavoriteWithListingOut


def get_favorite(db: Session, user_id: int, listing_id: int) -> Optional[Favorite]:
    return (
        db.query(Favorite)
        .filter(Favorite.customer_id == user_id, Favorite.listing_id == listing_id)
        .first()
    )


def add_favorite(db: Session, user_id: int, listing_id: int) -> Favorite:
    """Idempotente: si ya existe, devuelve el existente."""
    existing = get_favorite(db, user_id, listing_id)
    if existing:
        return existing

    fav = Favorite(customer_id=user_id, listing_id=listing_id)
    db.add(fav)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        # en caso de carrera, leemos el existente
        fav = get_favorite(db, user_id, listing_id)
        if fav:
            return fav
        raise
    db.refresh(fav)
    return fav


def remove_favorite(db: Session, user_id: int, listing_id: int) -> bool:
    """Idempotente: True si eliminó, False si no existía."""
    fav = get_favorite(db, user_id, listing_id)
    if not fav:
        return False
    db.delete(fav)
    db.commit()
    return True


def list_favorites_for_buyer(
    db: Session,
    buyer: User,
    brand: Optional[str] = None,
    model: Optional[str] = None,
    agency_id: Optional[int] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
) -> List[FavoriteWithListingOut]:
    q = (
        db.query(
            Favorite.id.label("favorite_id"),
            Favorite.created_at.label("created_at"),
            Listing.id.label("listing_id"),
            Listing.brand.label("brand"),
            Listing.model.label("model"),
            Listing.agency_id.label("agency_id"),
            Listing.current_price_amount.label("price"),
            Listing.current_price_currency.label("currency"),
        )
        .join(Listing, Listing.id == Favorite.listing_id)
        .filter(Favorite.customer_id == buyer.id)
    )

    if brand:
        q = q.filter(Listing.brand.ilike(f"%{brand}%"))
    if model:
        q = q.filter(Listing.model.ilike(f"%{model}%"))
    if agency_id is not None:
        q = q.filter(Listing.agency_id == agency_id)
    if min_price is not None:
        q = q.filter(Listing.current_price_amount >= min_price)
    if max_price is not None:
        q = q.filter(Listing.current_price_amount <= max_price)

    q = q.order_by(Favorite.created_at.desc())

    rows = q.all()

    return [
        FavoriteWithListingOut(
            favorite_id=row.favorite_id,
            listing_id=row.listing_id,
            brand=row.brand,
            model=row.model,
            agency_id=row.agency_id,
            price=float(row.price) if row.price is not None else None,
            currency=row.currency,
            created_at=row.created_at,
        )
        for row in rows
    ]
