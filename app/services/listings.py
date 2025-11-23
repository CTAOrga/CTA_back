import logging
from sqlalchemy import func
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.listing import Listing
from app.models.favorite import Favorite
from app.models.review import Review
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
    avg_rating = None
    reviews_count = 0

    if listing.car_model_id is not None:
        avg_val, count_val = (
            db.query(
                func.avg(Review.rating),
                func.count(Review.id),
            )
            .filter(Review.car_model_id == listing.car_model_id)
            .one()
        )
        if count_val:
            avg_rating = float(avg_val)  # avg_val puede venir como Decimal
            reviews_count = int(count_val)

    # devolvemos el ListingOut enriquecido
    return ListingOut.model_validate(listing, from_attributes=True).model_copy(
        update={
            "is_favorite": is_fav,
            "avg_rating": avg_rating,
            "reviews_count": reviews_count,
        }
    )
