from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.listing import Listing
from app.models.review import Review
from app.models.user import User
from app.schemas.review import ReviewCreate


def create_review_for_buyer(
    db: Session,
    buyer: User,
    payload: ReviewCreate,
) -> Review:
    # 1) Buscar la Listing
    listing = db.get(Listing, payload.listing_id)
    if not listing:
        raise HTTPException(status_code=404, detail="Listing no encontrada")

    if listing.car_model_id is None:
        raise HTTPException(
            status_code=400,
            detail="La oferta no tiene CarModel asociado",
        )

    # 2) Crear la Review asociada al CarModel
    review = Review(
        car_model_id=listing.car_model_id,
        author_id=buyer.id,
        rating=payload.rating,
        comment=payload.comment,
    )

    db.add(review)
    db.commit()
    db.refresh(review)

    return review


def list_reviews_for_listing(
    db: Session,
    listing: Listing,
) -> list[Review]:
    """
    Trae todas las reviews del CarModel de una listing.
    """
    if listing.car_model_id is None:
        return []

    rows = (
        db.query(Review)
        .filter(Review.car_model_id == listing.car_model_id)
        .order_by(Review.created_at.desc())
        .all()
    )
    return rows
