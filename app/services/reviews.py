from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.listing import Listing
from app.models.review import Review
from app.models.user import User
from app.schemas.review import ReviewCreate, ReviewUpdate
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
    buyer: User,
) -> list[dict]:
    """
    Devuelve todas las reseñas del comprador, junto con datos del modelo
    y (si existe) algún listing para poder ir al detalle.
    """
    rows = (
        db.query(Review, CarModel)
        .join(CarModel, Review.car_model_id == CarModel.id)
        .filter(Review.author_id == buyer.id)
        .order_by(Review.created_at.desc())
        .all()
    )

    result: list[dict] = []

    for review, car_model in rows:
        # Buscamos algún listing activo para ese modelo (el primero que haya)
        listing = (
            db.query(Listing.id)
            .filter(Listing.car_model_id == car_model.id)
            .order_by(Listing.id.asc())
            .first()
        )
        listing_id = listing[0] if listing else None

        result.append(
            {
                "id": review.id,
                "car_model_id": car_model.id,
                "brand": car_model.brand,
                "model": car_model.model,
                "rating": review.rating,
                "comment": review.comment,
                "created_at": review.created_at,
                "listing_id": listing_id,
            }
        )

    return result
