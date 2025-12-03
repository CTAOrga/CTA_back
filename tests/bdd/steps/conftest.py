from pytest_bdd import given
from starlette.testclient import TestClient
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
