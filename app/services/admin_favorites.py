from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.favorite import Favorite
from app.models.listing import Listing
from app.models.user import User
from app.schemas.admin_favorites import AdminFavoriteOut, PaginatedAdminFavoritesOut


def list_favorites(
    db: Session,
    page: int = 1,
    page_size: int = 20,
    q: Optional[str] = None,  # busca por email / brand / model
) -> PaginatedAdminFavoritesOut:
    if page < 1:
        page = 1
    if page_size < 1:
        page_size = 20

    query = (
        db.query(Favorite, Listing, User)
        .join(Listing, Favorite.listing_id == Listing.id)
        .join(User, Favorite.customer_id == User.id)
    )

    if q:
        like = f"%{q}%"
        query = query.filter(
            (User.email.ilike(like))
            | (Listing.brand.ilike(like))
            | (Listing.model.ilike(like))
        )

    total = query.count()

    offset = (page - 1) * page_size

    rows = (
        query.order_by(Favorite.created_at.desc()).offset(offset).limit(page_size).all()
    )

    items: list[AdminFavoriteOut] = []
    for fav, listing, user in rows:
        items.append(
            AdminFavoriteOut(
                id=fav.id,
                listing_id=listing.id,
                customer_id=user.id,
                customer_email=user.email,
                brand=listing.brand,
                model=listing.model,
                created_at=fav.created_at,
            )
        )

    return PaginatedAdminFavoritesOut(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )
