import logging
from sqlalchemy import desc, func
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.car_model import CarModel
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


def list_my_agency_listings(
    db: Session,
    agency_id: int,
    page: int = 1,
    page_size: int = 10,
):
    """
    Lista los listings de una agencia con paginación y orden por más nuevos primero.
    """

    if page < 1:
        page = 1
    if page_size < 1:
        page_size = 10

    # Query base
    query = (
        db.query(Listing, CarModel)
        .join(CarModel, Listing.car_model_id == CarModel.id)
        .filter(Listing.agency_id == agency_id)
    )

    # Total
    total = query.count()

    # Paginado
    offset = (page - 1) * page_size

    rows = (
        query.order_by(desc(Listing.created_at))  # más nuevos primero
        .offset(offset)
        .limit(page_size)
        .all()
    )

    items = []

    for listing, car_model in rows:
        items.append(
            {
                "id": listing.id,
                "car_model_id": listing.car_model_id,
                "price": float(listing.current_price_amount),
                "currency": listing.current_price_currency,
                "stock": listing.stock,
                "is_active": listing.is_active,
                "created_at": listing.created_at,
                "brand": car_model.brand,
                "model": car_model.model,
            }
        )

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
    }


def get_listing_owned_by_agency(
    db: Session,
    listing_id: int,
    agency_id: int,
) -> Listing:
    listing = (
        db.query(Listing)
        .filter(
            Listing.id == listing_id,
            Listing.agency_id == agency_id,
        )
        .first()
    )
    if not listing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Listing no encontrado",
        )
    return listing


def cancel_listing(
    db: Session,
    listing_id: int,
    agency_id: int,
):
    listing = get_listing_owned_by_agency(db, listing_id, agency_id)
    listing.is_active = False
    db.add(listing)
    db.commit()
    db.refresh(listing)
    return listing


def activate_listing(
    db: Session,
    listing_id: int,
    agency_id: int,
):
    listing = get_listing_owned_by_agency(db, listing_id, agency_id)
    listing.is_active = True
    db.add(listing)
    db.commit()
    db.refresh(listing)
    return listing


def delete_listing(
    db: Session,
    listing_id: int,
    agency_id: int,
):
    listing = get_listing_owned_by_agency(db, listing_id, agency_id)

    # Si querés proteger contra borrar algo con compras:
    if listing.purchases and len(listing.purchases) > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede eliminar una oferta con compras asociadas",
        )

    db.delete(listing)
    db.commit()
    return None
