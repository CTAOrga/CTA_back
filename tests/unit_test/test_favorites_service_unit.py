from sqlalchemy.orm import Session

from app.models.user import User
from app.models.listing import Listing
from app.models.car_model import CarModel
from app.schemas.favorite import FavoriteWithListingOut
from app.services.favorites import (
    add_favorite,
    remove_favorite,
    list_favorites_for_buyer,
)


def test_add_favorite_is_idempotent(
    db: Session,
    buyer_user: User,
    sample_listing: Listing,
) -> None:
    """
    add_favorite debe ser idempotente:
    - Si llamo dos veces con el mismo (user_id, listing_id),
      no se crean duplicados, se reutiliza el mismo Favorite.
    """
    fav1 = add_favorite(db, buyer_user.id, sample_listing.id)
    fav2 = add_favorite(db, buyer_user.id, sample_listing.id)

    # Mismo registro
    assert fav1.id == fav2.id

    # Y desde el punto de vista del "payload" de negocio,
    # el buyer sólo tiene un auto favorito.
    payload = list_favorites_for_buyer(db, buyer_user)
    assert len(payload) == 1

    first = payload[0]
    assert isinstance(first, FavoriteWithListingOut)
    assert first.listing_id == sample_listing.id
    assert first.brand == sample_listing.brand
    assert first.model == sample_listing.model


def test_remove_favorite_is_idempotent(
    db: Session,
    buyer_user: User,
    sample_listing: Listing,
) -> None:
    """
    remove_favorite también es idempotente:
    - Primera vez: elimina y devuelve True.
    - Segunda vez (ya no existe): devuelve False.
    """

    # Creamos primero el favorito
    add_favorite(db, buyer_user.id, sample_listing.id)

    # 1ª eliminación: existía
    removed_first = remove_favorite(db, buyer_user.id, sample_listing.id)
    assert removed_first is True

    # 2ª eliminación: ya no existe
    removed_second = remove_favorite(db, buyer_user.id, sample_listing.id)
    assert removed_second is False

    # El buyer no debe tener favoritos
    payload = list_favorites_for_buyer(db, buyer_user)
    assert payload == []


def test_list_favorites_returns_all_favorites_for_user(
    db: Session,
    buyer_user: User,
    agency,
) -> None:
    """
    Verificamos que el servicio de listado de favoritos devuelve
    todos los favoritos del buyer con la forma (payload) esperada.
    No dependemos del orden exacto porque los timestamps pueden coincidir.
    """

    # Creamos un CarModel para poder asociar las publicaciones
    car_model = CarModel(
        brand="Fiat",
        model="Cronos",
    )
    db.add(car_model)
    db.commit()
    db.refresh(car_model)

    # Creamos dos listings de la misma agencia
    l1 = Listing(
        agency_id=agency.id,
        car_model_id=car_model.id,
        brand="Fiat",
        model="Cronos",
        current_price_amount=10000.0,
        current_price_currency="USD",
        stock=1,
        seller_notes="OK",
    )
    l2 = Listing(
        agency_id=agency.id,
        car_model_id=car_model.id,
        brand="Toyota",
        model="Yaris",
        current_price_amount=15000.0,
        current_price_currency="USD",
        stock=1,
        seller_notes="OK",
    )
    db.add_all([l1, l2])
    db.commit()
    db.refresh(l1)
    db.refresh(l2)

    # Agregamos ambos a favoritos
    add_favorite(db, buyer_user.id, l1.id)
    add_favorite(db, buyer_user.id, l2.id)

    payload = list_favorites_for_buyer(db, buyer_user)

    # Validaciones básicas
    assert isinstance(payload, list)
    assert len(payload) == 2

    # Verificamos que estén los dos listings, sin asumir orden
    listing_ids = {fav.listing_id for fav in payload}
    assert listing_ids == {l1.id, l2.id}

    # Verificamos algunos campos de negocio
    brands = {fav.brand for fav in payload}
    models = {fav.model for fav in payload}

    assert "Fiat" in brands
    assert "Toyota" in brands
    assert "Cronos" in models
    assert "Yaris" in models

    # Todos deberían ser del mismo buyer y tener precio/currency seteados
    for fav in payload:
        assert isinstance(fav, FavoriteWithListingOut)
        assert fav.price is not None
        assert fav.currency == "USD"
        assert fav.agency_id == agency.id
        assert fav.created_at is not None
