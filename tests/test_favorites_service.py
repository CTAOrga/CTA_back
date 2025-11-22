from app.models.listing import Listing
from app.services.favorites import (
    add_favorite,
    toggle_favorite,
    list_my_favorites_payload,
)
from app.models.favorite import Favorite
import time


# Simula el click en favoritos para una oferta
def test_toggle_favorite(db, buyer_user, sample_listing):
    state = toggle_favorite(db, buyer_user.id, sample_listing.id)
    assert state is True
    assert db.query(Favorite).count() == 1

    state = toggle_favorite(db, buyer_user.id, sample_listing.id)
    assert state is False
    assert db.query(Favorite).count() == 0


# Devuelve la lista de favoritos para un usuario
def test_list_my_favorites_payload_empty(db, buyer_user):
    payload = list_my_favorites_payload(db, buyer_user.id)
    assert isinstance(payload, list)
    assert payload == []


# Creamos dos ofertas y las agregamos a favoritos para un usuario
def test_list_my_favorites_payload_happy_path(db, buyer_user, agency):
    # Creamos 2 listings
    l1 = Listing(
        agency_id=agency.id,
        brand="Fiat",
        model="Cronos",
        current_price_amount=10000.0,
        current_price_currency="USD",
        stock=1,
        seller_notes="OK",
    )
    db.add(l1)
    db.commit()
    db.refresh(l1)

    # Favorito 1
    add_favorite(db, buyer_user.id, l1.id)

    l2 = Listing(
        agency_id=agency.id,
        brand="Toyota",
        model="Yaris",
        current_price_amount=15000.0,
        current_price_currency="USD",
        stock=1,
        seller_notes="OK",
    )
    db.add(l2)
    db.commit()
    db.refresh(l2)

    # Favorito 2 (debería aparecer primero en el payload)
    add_favorite(db, buyer_user.id, l2.id)

    # Ejecutamos el service
    payload = list_my_favorites_payload(db, buyer_user.id)

    # Validaciones básicas
    assert isinstance(payload, list)
    assert len(payload) == 2

    # Debe venir ordenado por created_at DESC -> l2 primero
    first, second = payload[0], payload[1]
    assert first["listing_id"] == l2.id
    assert second["listing_id"] == l1.id

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
    assert required_keys <= set(first.keys())

    # Tipos y valores representativos
    assert isinstance(first["price"], float)
    assert first["currency"] == "USD"
    assert first["brand"] == "Toyota"
    assert first["model"] == "Yaris"
