from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.api.deps import get_db, require_role, get_current_user
from app.models.user import User, UserRole
from app.models.favorite import Favorite
from app.models.listing import Listing
from app.schemas.favorite import FavoriteOut, FavoriteWithListingOut
from app.services.favorites import (
    list_favorites_for_buyer,
    add_favorite as svc_add_favorite,
    remove_favorite as svc_remove_favorite,
)

router = APIRouter()


@router.get(
    "/my",
    response_model=List[FavoriteWithListingOut],
    dependencies=[Depends(require_role(UserRole.buyer))],
)
def list_my_favorites(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    brand: Optional[str] = Query(None),
    model: Optional[str] = Query(None),
    agency_id: Optional[int] = Query(None, ge=1),
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
):
    return list_favorites_for_buyer(
        db=db,
        buyer=current_user,
        brand=brand,
        model=model,
        agency_id=agency_id,
        min_price=min_price,
        max_price=max_price,
    )


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
