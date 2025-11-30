from datetime import date, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.listing import Listing
from app.models.review import Review
from app.models.user import User
from app.schemas.review import BuyerReviewOut, ReviewCreate, ReviewUpdate
from app.models.car_model import CarModel


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


def update_review_for_buyer(
    db: Session,
    buyer: User,
    review_id: int,
    payload: ReviewUpdate,
) -> Review:
    """
    Permite que un comprador actualice sus propias reseñas.
    """
    review = (
        db.query(Review)
        .filter(
            Review.id == review_id,
            Review.author_id == buyer.id,
        )
        .first()
    )
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reseña no encontrada",
        )

    if payload.rating is not None:
        review.rating = payload.rating
    if payload.comment is not None:
        review.comment = payload.comment

    db.add(review)
    db.commit()
    db.refresh(review)

    return review


def list_reviews_for_buyer(
    db: Session,
    author: User,
    brand: Optional[str] = None,
    model: Optional[str] = None,
    min_rating: Optional[int] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
) -> List[BuyerReviewOut]:

    query = (
        db.query(
            Review.id.label("id"),
            Review.car_model_id.label("car_model_id"),
            Review.rating.label("rating"),
            Review.comment.label("comment"),
            Review.created_at.label("created_at"),
            CarModel.brand.label("brand"),
            CarModel.model.label("model"),
        )
        .join(CarModel, CarModel.id == Review.car_model_id)
        .filter(Review.author_id == author.id)
    )

    if brand:
        query = query.filter(CarModel.brand.ilike(f"%{brand}%"))
    if model:
        query = query.filter(CarModel.model.ilike(f"%{model}%"))
    if min_rating is not None:
        query = query.filter(Review.rating >= min_rating)
    if date_from:
        query = query.filter(Review.created_at >= date_from)
    if date_to:
        query = query.filter(Review.created_at < date_to + timedelta(days=1))

    query = query.order_by(Review.created_at.desc())
    rows = query.all()

    return [
        BuyerReviewOut(
            id=row.id,
            car_model_id=row.car_model_id,
            brand=row.brand,
            model=row.model,
            rating=row.rating,
            comment=row.comment,
            created_at=row.created_at,
        )
        for row in rows
    ]
