from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from fastapi import status

from app.models.listing import Listing
from app.models.user import User

FAVORITES_BASE_PATH = "/api/v1/favorites"
ADMIN_REPORTS_FAVORITES_PATH = "/api/v1/admin/reports/top-favorites"


def _login(client: TestClient, email: str, password: str = "secret") -> str:
    resp = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert resp.status_code == status.HTTP_200_OK, resp.text
    return resp.json()["access_token"]


def test_buyer_favorites_listing_and_admin_sees_it_in_top_favorites(
    client: TestClient,
    db: Session,
    buyer_user: User,
    admin_user: User,
    sample_listing: Listing,
):
    # 1) Login buyer
    buyer_token = _login(client, buyer_user.email)

    # 2) Buyer marca como favorito el listing
    resp_fav = client.post(
        f"{FAVORITES_BASE_PATH}/{sample_listing.id}",
        headers={"Authorization": f"Bearer {buyer_token}"},
    )

    assert resp_fav.status_code == status.HTTP_201_CREATED, resp_fav.text

    if resp_fav.headers.get("content-type", "").startswith("application/json"):
        body = resp_fav.json()
        if isinstance(body, dict) and "listing_id" in body:
            assert body["listing_id"] == sample_listing.id

    # 3) Buyer consulta "mis favoritos" y el listing tiene que aparecer
    resp_my_favs = client.get(
        FAVORITES_BASE_PATH + "/my",
        headers={"Authorization": f"Bearer {buyer_token}"},
    )
    assert resp_my_favs.status_code == status.HTTP_200_OK, resp_my_favs.text
    my_favs = resp_my_favs.json()

    assert isinstance(my_favs, list)

    fav_entry = next(
        (f for f in my_favs if f.get("listing_id") == sample_listing.id),
        None,
    )
    assert (
        fav_entry is not None
    ), "El listing marcado como favorito no aparece en los favoritos del buyer"

    # Opcional: si el DTO incluye info básica del listing
    if "brand" in fav_entry:
        assert fav_entry["brand"] == sample_listing.brand
    if "model" in fav_entry:
        assert fav_entry["model"] == sample_listing.model

    # 4) Login admin
    admin_token = _login(client, admin_user.email)

    # 5) Admin consulta el reporte de “autos favoritos (Top 5)”
    resp_top_favs = client.get(
        ADMIN_REPORTS_FAVORITES_PATH,
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert resp_top_favs.status_code == status.HTTP_200_OK, resp_top_favs.text
    top_favorites = resp_top_favs.json()

    assert isinstance(top_favorites, list)

    favorite_entry = next(
        (
            item
            for item in top_favorites
            if item.get("brand") == sample_listing.brand
            and item.get("model") == sample_listing.model
        ),
        None,
    )

    assert (
        favorite_entry is not None
    ), "Admin no ve este auto en el reporte de autos favoritos (brand+model)"

    # Verificamos el contador de favoritos según el schema TopFavoriteCarOut
    assert favorite_entry["favorites_count"] >= 1
