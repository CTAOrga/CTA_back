from app.models.car_model import CarModel
from app.models.listing import Listing
from app.schemas.favorite import FavoriteWithListingOut
from app.services.favorites import (
    add_favorite,
    toggle_favorite,
    list_favorites_for_buyer,
)
from app.models.favorite import Favorite
import time


# Simula el click en favoritos para una oferta
def test_toggle_favorite(db, buyer_user, sample_listing):

    assert db.query(Favorite).count() == 0

    state = toggle_favorite(db, buyer_user.id, sample_listing.id)
    assert state is True
    assert db.query(Favorite).count() == 1

    state = toggle_favorite(db, buyer_user.id, sample_listing.id)
    assert state is False
    assert db.query(Favorite).count() == 0


# Devuelve la lista de favoritos para un usuario
def test_list_my_favorites_payload_empty(db, buyer_user):
    payload = list_favorites_for_buyer(db, buyer_user)
    assert isinstance(payload, list)
    assert payload == []


# Creamos dos ofertas y las agregamos a favoritos para un usuario
def test_list_my_favorites_payload_happy_path(db, buyer_user, agency):
    car_model = CarModel(
        brand="Fiat",
        model="Cronos",
    )
    db.add(car_model)
    db.commit()
    db.refresh(car_model)
    # Creamos 2 listings
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

    # Agregamos primero l1 y luego l2 a favoritos.
    # El service ordena por Favorite.created_at DESC,
    # así que l2 debería aparecer antes que l1.
    add_favorite(db, buyer_user.id, l1.id)
    add_favorite(db, buyer_user.id, l2.id)

    # Ejecutamos el service
    payload = list_favorites_for_buyer(db, buyer_user)

    # Validaciones básicas
    assert isinstance(payload, list)
    assert len(payload) == 2

    # Todos los elementos deben ser del tipo esperado
    for item in payload:
        assert isinstance(item, FavoriteWithListingOut)

    # Chequeamos que estén ambos listings, sin asumir el orden
    listing_ids = {item.listing_id for item in payload}
    assert listing_ids == {l1.id, l2.id}

    # Shape esperado por el front
    required_keys = {
        "favorite_id",
        "listing_id",
        "brand",
        "model",
        "price",
        "currency",
        "agency_id",
        "created_at",
    }
    assert required_keys <= set(FavoriteWithListingOut.model_fields.keys())

    # Buscamos el Yaris en el payload y validamos sus datos
    yaris = next(item for item in payload if item.listing_id == l2.id)
    assert isinstance(yaris.price, float)
    assert yaris.currency == "USD"
    assert yaris.brand == "Toyota"
    assert yaris.model == "Yaris"
