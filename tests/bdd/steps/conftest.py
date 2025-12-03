from pytest_bdd import given, parsers
from starlette.testclient import TestClient
from app.models.car_model import CarModel
from app.models.listing import Listing
from app.models.user import User


@given("existe un usuario buyer en la base", target_fixture="ensure_buyer")
def ensure_buyer(buyer_user: User) -> User:
    # Reusa la fixture buyer_user definida en tests/conftest.py
    return buyer_user


@given("existe un usuario admin en la base", target_fixture="ensure_admin")
def ensure_admin(admin_user: User) -> User:
    # Reusa la fixture admin_user definida en tests/conftest.py
    return admin_user


@given("existe un usuario buyer logueado", target_fixture="buyer_token")
def buyer_token(client: TestClient, buyer_user: User) -> str:
    # En conftest, buyer_user se crea con password "secret"
    resp = client.post(
        "/api/v1/auth/login",
        json={"email": buyer_user.email, "password": "secret"},
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert "access_token" in data, data
    return data["access_token"]


@given("existe un usuario admin logueado", target_fixture="admin_token")
def admin_token(client: TestClient, admin_user: User) -> str:
    resp = client.post(
        "/api/v1/auth/login",
        json={"email": admin_user.email, "password": "secret"},
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert "access_token" in data, data
    return data["access_token"]


@given("existe un usuario agency en la base", target_fixture="ensure_agency_user")
def ensure_agency_user(agency_user: User) -> User:
    return agency_user


@given("existe un usuario agency logueado", target_fixture="agency_token")
def agency_token(client: TestClient, agency_user: User) -> str:
    resp = client.post(
        "/api/v1/auth/login",
        json={"email": agency_user.email, "password": "secret"},
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert "access_token" in data, data
    return data["access_token"]


@given(
    parsers.parse('existe un CarModel "{brand}" "{model}" en el catálogo'),
    target_fixture="carmodel",
)
def ensure_carmodel(fiat_cronos_carmodel: CarModel, brand: str, model: str) -> CarModel:
    # Reusa la fixture fiat_cronos_carmodel definida en tests/conftest.py
    # nos aseguramos de eso (si cambia el feature, este assert avisa).
    assert brand == "Fiat"
    assert model == "Cronos"
    return fiat_cronos_carmodel


@given("existe una listing disponible", target_fixture="existing_listing")
def existing_listing(sample_listing: Listing) -> Listing:
    # Reusa la fixture sample_listing de tests/conftest.py
    return sample_listing
