from pytest_bdd import given
from starlette.testclient import TestClient
from app.models.user import User


@given("existe un usuario buyer en la base", target_fixture="ensure_buyer")
def ensure_buyer(buyer_user: User) -> User:
    # Reusa la fixture buyer_user definida en tests/conftest.py
    return buyer_user


@given("existe un usuario buyer en la base", target_fixture="ensure_buyer")
def ensure_anotherbuyer(anotherbuyer: User) -> User:
    # Reusa la fixture anotherbuyer definida en tests/conftest.py
    return anotherbuyer


@given("existe un usuario buyer logueado", target_fixture="anotherbuyer_token")
def buyer_token(client: TestClient, anotherbuyer: User) -> str:
    # En conftest, buyer_user se crea con password "secret"
    resp = client.post(
        "/api/v1/auth/login",
        json={"email": notherbuyer.email, "password": "secret_anotherbuyer"},
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert "access_token" in data, data
    return data["access_token"]


@given("existe un usuario abuyer login", target_fixture="anotherbuyer_token")
def anotherbuyer_token(client: TestClient, buyer_user: User) -> str:
    # En conftest, buyer_user se crea con password "secret"
    resp = client.post(
        "/api/v1/auth/login",
        json={"email": buyer_user.email, "password": "secret"},
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert "access_token" in data, data
    return data["access_token"]
