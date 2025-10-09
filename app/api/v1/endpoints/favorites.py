from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.api.deps import get_db, require_role, get_current_user
from app.models.user import User, UserRole
from app.models.favorite import Favorite
from app.models.listing import Listing
from app.schemas.favorite import FavoriteOut
from app.services.favorites import (
    list_my_favorites_payload,
    add_favorite as svc_add_favorite,
    remove_favorite as svc_remove_favorite,
)

router = APIRouter()


@router.get("/my", response_model=list[dict])
def my_favorites(
    db: Session = Depends(get_db),
    user: User = Depends(require_role(UserRole.buyer)),
):
    return list_my_favorites_payload(db, user.id)


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
    fav = svc_add_favorite(db, user.id, listing_id)
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
