from __future__ import annotations
from typing import Sequence, List, Dict, Any, Tuple, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy.engine import Row

from app.models.favorite import Favorite
from app.models.listing import Listing


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


def toggle_favorite(db: Session, user_id: int, listing_id: int) -> bool:
    """Devuelve el estado final: True si quedó favorito, False si se quitó."""
    fav = get_favorite(db, user_id, listing_id)
    if fav:
        db.delete(fav)
        db.commit()
        return False
    add_favorite(db, user_id, listing_id)
    return True


def list_my_favorites_payload(db: Session, user_id: int) -> List[Dict[str, Any]]:
    """
    Devuelve exactamente el payload que hoy arma el controller /my
    (para que el front no cambie).
    """
    rows: Sequence[Row[tuple[Favorite, Listing]]] = (
        db.query(Favorite, Listing)
        .join(Listing, Listing.id == Favorite.listing_id)
        .filter(Favorite.customer_id == user_id)
        .order_by(Favorite.created_at.desc(), Favorite.id.desc())
        .all()
    )
    out: List[Dict[str, Any]] = []
    for fav, lst in rows:
        out.append(
            {
                "favorite_id": fav.id,
                "listing_id": lst.id,
                "brand": lst.brand,
                "model": lst.model,
                "price": float(lst.current_price_amount),
                "currency": lst.current_price_currency,
                "agency_id": lst.agency_id,
                "created_at": str(fav.created_at),
            }
        )
    return out
