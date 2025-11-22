import logging
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.listing import Listing
from app.models.favorite import Favorite
from app.models.user import User
from app.schemas.listing import ListingOut

logger = logging.getLogger(__name__)


def get_listing_for_buyer(
    db: Session,
    buyer: User,
    listing_id: int,
) -> ListingOut:

    logger.info(f"[service] buyer={buyer!r}, listing_id={listing_id}")
    listing = db.get(Listing, listing_id)
    logger.info(f"[service] listing={listing!r}")
    if not listing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Listing no encontrada",
        )

    fav = (
        db.query(Favorite)
        .filter(
            Favorite.customer_id == buyer.id,
            Favorite.listing_id == listing_id,
        )
        .first()
    )
    is_fav = fav is not None

    logger.info(f"[service] fav_exists={fav!r}")
    return ListingOut.model_validate(listing, from_attributes=True).model_copy(
        update={"is_favorite": is_fav}
    )
