from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.api.deps import get_db, require_role, get_current_user
from app.models.user import User, UserRole
from app.models.favorite import Favorite
from app.models.listing import Listing
from app.schemas.favorite import FavoriteOut

router = APIRouter()


@router.get("/my", response_model=list[dict])
def my_favorites(
    db: Session = Depends(get_db),
    user: User = Depends(require_role("buyer")),
):
    q = (
        db.query(Favorite, Listing)
        .join(Listing, Listing.id == Favorite.listing_id)
        .filter(Favorite.customer_id == user.id)
        .order_by(Favorite.created_at.desc())
        .all()
    )
    # Armamos un payload amigable para el front
    result = []
    for fav, lst in q:
        result.append(
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
    return result


@router.post(
    "/{listing_id}",
    response_model=FavoriteOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role(UserRole.buyer))],
)
def add_favorite(
    listing_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    listing = db.get(Listing, listing_id)
    if not listing:
        raise HTTPException(404, "Listing no encontrada")

    fav = Favorite(customer_id=user.id, listing_id=listing_id)
    db.add(fav)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        # ya existía: devolvemos el existente
        fav = (
            db.query(Favorite)
            .filter(Favorite.customer_id == user.id, Favorite.listing_id == listing_id)
            .first()
        )
        return fav
    db.refresh(fav)
    return fav


@router.delete(
    "/{listing_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_role(UserRole.buyer))],
)
def remove_favorite(
    listing_id: int,
    db: Session = Depends(get_db),
    # user: User = Depends(require_role("buyer")),
    user: User = Depends(get_current_user),
):
    fav = (
        db.query(Favorite)
        .filter(Favorite.customer_id == user.id, Favorite.listing_id == listing_id)
        .first()
    )
    if not fav:
        # idempotente: no hay favorito; 204 igual
        return None
    db.delete(fav)
    db.commit()
    return None
