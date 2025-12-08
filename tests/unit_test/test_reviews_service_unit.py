from sqlalchemy.orm import Session

from app.models.user import User
from app.models.agency import Agency
from app.models.car_model import CarModel
from app.models.listing import Listing
from app.models.review import Review
from app.schemas.review import ReviewCreate, ReviewUpdate, BuyerReviewOut
from app.services.reviews import (
    create_review_for_buyer,
    update_review_for_buyer,
    list_reviews_for_buyer,
)


def _create_listing(
    db: Session,
    agency: Agency,
    brand: str,
    model: str,
) -> Listing:
    """
    Helper interno para crear CarModel + Listing consistente con el dominio.
    """
    car_model = CarModel(brand=brand, model=model)
    db.add(car_model)
    db.commit()
    db.refresh(car_model)

    listing = Listing(
        agency_id=agency.id,
        car_model_id=car_model.id,
        brand=brand,
        model=model,
        current_price_amount=10000.0,
        current_price_currency="USD",
        stock=1,
        seller_notes="OK",
    )
    db.add(listing)
    db.commit()
    db.refresh(listing)
    return listing


def test_create_review_for_buyer_creates_review(
    db: Session,
    buyer_user: User,
    agency: Agency,
) -> None:
    """
    create_review_for_buyer:
      - Crea una reseña asociada al CarModel de la listing.
    """
    listing = _create_listing(db, agency, brand="Fiat", model="Cronos")

    payload = ReviewCreate(
        listing_id=listing.id,
        rating=4,
        comment="Muy buen auto",
    )

    review = create_review_for_buyer(
        db=db,
        buyer=buyer_user,
        payload=payload,
    )

    assert isinstance(review, Review)
    assert review.rating == 4
    assert review.comment == "Muy buen auto"
    assert review.author_id == buyer_user.id
    assert review.car_model_id == listing.car_model_id


def test_update_review_for_buyer_updates_own_review(
    db: Session,
    buyer_user: User,
    agency: Agency,
) -> None:
    """
    update_review_for_buyer:
      - El comprador puede actualizar rating/comentario de su propia reseña.
    """
    listing = _create_listing(db, agency, brand="Fiat", model="Cronos")

    # Creamos primero la review con el service
    created = create_review_for_buyer(
        db=db,
        buyer=buyer_user,
        payload=ReviewCreate(
            listing_id=listing.id,
            rating=3,
            comment="Está bien",
        ),
    )

    assert isinstance(created, Review)
    assert created.rating == 3
    assert created.comment == "Está bien"

    # Ahora la actualizamos
    update_payload = ReviewUpdate(
        rating=5,
        comment="Mejor de lo esperado",
    )

    updated = update_review_for_buyer(
        db=db,
        buyer=buyer_user,
        review_id=created.id,
        payload=update_payload,
    )

    assert updated.id == created.id
    assert updated.rating == 5
    assert updated.comment == "Mejor de lo esperado"
    assert updated.author_id == buyer_user.id


def test_list_reviews_for_buyer_filters_and_orders(
    db: Session,
    buyer_user: User,
    agency: Agency,
) -> None:
    """
    list_reviews_for_buyer:
      - Devuelve solo reviews del autor indicado.
      - Ordenadas por created_at DESC (última primero).
      - Filtra por brand y min_rating.
    """
    # Creamos dos listings de distintas marcas
    listing_fiat = _create_listing(db, agency, brand="Fiat", model="Cronos")
    listing_toyota = _create_listing(db, agency, brand="Toyota", model="Yaris")

    # Creamos 2 reseñas para el mismo buyer, en momentos distintos
    r1 = create_review_for_buyer(
        db=db,
        buyer=buyer_user,
        payload=ReviewCreate(
            listing_id=listing_fiat.id,
            rating=3,
            comment="Normalito",
        ),
    )

    r2 = create_review_for_buyer(
        db=db,
        buyer=buyer_user,
        payload=ReviewCreate(
            listing_id=listing_toyota.id,
            rating=5,
            comment="Excelente",
        ),
    )

    # 1) Sin filtros: deben venir las 2, y la última creada (Toyota) primero
    result = list_reviews_for_buyer(
        db=db,
        author=buyer_user,
        brand=None,
        model=None,
        min_rating=None,
        date_from=None,
        date_to=None,
    )

    assert isinstance(result, list)
    assert len(result) == 2

    first, second = result[0], result[1]
    assert isinstance(first, BuyerReviewOut)
    assert isinstance(second, BuyerReviewOut)

    # Orden DESC → r2 primero
    assert first.id == r2.id
    assert second.id == r1.id

    # 2) Filtro por brand = "Fiat" → solo la del Cronos
    result_fiat = list_reviews_for_buyer(
        db=db,
        author=buyer_user,
        brand="Fiat",
        model=None,
        min_rating=None,
        date_from=None,
        date_to=None,
    )

    assert len(result_fiat) == 1
    only = result_fiat[0]
    assert only.brand == "Fiat"
    assert only.model == "Cronos"
    assert only.id == r1.id

    # 3) Filtro por min_rating = 4 → solo la de Toyota (rating 5)
    result_high_rating = list_reviews_for_buyer(
        db=db,
        author=buyer_user,
        brand=None,
        model=None,
        min_rating=4,
        date_from=None,
        date_to=None,
    )

    assert len(result_high_rating) == 1
    high = result_high_rating[0]
    assert high.id == r2.id
    assert high.rating == 5
    assert high.brand == "Toyota"
    assert high.model == "Yaris"
