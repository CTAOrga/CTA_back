from typing import Any, Dict
from fastapi.testclient import TestClient
import pytest
from pytest_bdd import scenarios, when, then
import os
from fastapi import status


CREATE_AGENCY_PATH = os.getenv("CREATE_AGENCY_PATH", "/api/v1/agencies/")

# Vincula el feature correspondiente
scenarios("../features/authorization_agency_creation.feature")


@pytest.fixture
def ctx() -> Dict[str, Any]:
    return {}


@when("intento crear un usuario agencia desde el endpoint protegido")
def call_create_agency_as_buyer(
    client: TestClient, buyer_token: str, ctx: Dict[str, Any]
):
    payload = {
        "email": "nuevaagencia_buyer@example.com",
        "password": "AlgoSeguro123!",
        "agency_name": "Agencia Test Buyer",
    }
    headers = {"Authorization": f"Bearer {buyer_token}"}
    resp = client.post(CREATE_AGENCY_PATH, json=payload, headers=headers)
    ctx["resp"] = resp


@when("intento crear un usuario agencia desde el endpoint protegido como admin")
def call_create_agency_as_admin(
    client: TestClient, admin_token: str, ctx: Dict[str, Any]
):
    payload = {
        "email": "nuevaagencia_admin@example.com",
        "password": "AlgoSeguro123!",
        "agency_name": "Agencia Test Admin",
    }
    headers = {"Authorization": f"Bearer {admin_token}"}
    resp = client.post(CREATE_AGENCY_PATH, json=payload, headers=headers)
    ctx["resp"] = resp


@then("la respuesta HTTP es 403")
def assert_403(ctx: Dict[str, Any]):
    resp = ctx["resp"]
    assert resp.status_code == status.HTTP_403_FORBIDDEN, resp.text


@then("la respuesta HTTP es 201")
def assert_201(ctx: Dict[str, Any]) -> None:
    resp = ctx["resp"]
    assert resp.status_code == status.HTTP_201_CREATED, resp.text


@then("la respuesta contiene un usuario agencia creado correctamente")
def assert_agency_created(ctx: Dict[str, Any]) -> None:
    resp = ctx["resp"]
    body = resp.json()
    # Aca chequeamos “lo básico” de que se creó algo razonable
    assert "id" in body
    assert "email" in body
    assert "role" in body
    assert "agency_id" in body

    assert body["role"] == "agency"

    assert body["agency_id"] is not None

    assert body["email"] == "nuevaagencia_admin@example.com"
