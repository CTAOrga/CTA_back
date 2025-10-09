from typing import Any, Dict
from fastapi.testclient import TestClient
import pytest
from pytest_bdd import scenarios, given, when, then
import os
from fastapi import status

# Ajustá este path si tu endpoint real es distinto
CREATE_AGENCY_PATH = os.getenv("CREATE_AGENCY_PATH", "/api/v1/agencies")

# Vincula el feature correspondiente
scenarios("../features/authorization_agency_creation.feature")


@pytest.fixture
def ctx() -> Dict[str, Any]:
    return {}


@given("existe un usuario buyer logueado", target_fixture="buyer_token")
def given_buyer_logged_in(client: TestClient, buyer_user) -> str:
    # buyer_user viene de conftest y tiene password "secret"
    resp = client.post(
        "/api/v1/auth/login",
        json={"email": buyer_user.email, "password": "secret"},
    )
    assert resp.status_code == status.HTTP_200_OK, resp.text
    data = resp.json()
    return data["access_token"]


@when("intento crear un usuario agencia desde el endpoint protegido")
def call_create_agency(client: TestClient, buyer_token: str, ctx: Dict[str, Any]):
    payload = {
        "email": "nuevaagencia@example.com",
        "password": "AlgoSeguro123!",
        "name": "Agencia Test",
    }
    headers = {"Authorization": f"Bearer {buyer_token}"}
    resp = client.post(CREATE_AGENCY_PATH, json=payload, headers=headers)
    ctx["resp"] = resp


@then("la respuesta HTTP es 403")
def assert_403(ctx: Dict[str, Any]):
    resp = ctx["resp"]
    assert resp.status_code == status.HTTP_403_FORBIDDEN, resp.text
