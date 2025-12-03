from typing import Any, Dict
import os

import pytest
from fastapi.testclient import TestClient
from fastapi import status
from pytest_bdd import scenarios, when, then

# Path base al endpoint de inventario (el router de inventory suele estar montado en /api/v1/inventory)
INVENTORY_PATH = os.getenv("INVENTORY_PATH", "/api/v1/inventory")

# Vinculamos el feature
scenarios("../features/inventory_authorization.feature")


@pytest.fixture
def ctx() -> Dict[str, Any]:
    return {}


@when("intento crear un item de inventario")
def create_inventory_as_buyer(
    client: TestClient,
    buyer_token: str,
    ctx: Dict[str, Any],
) -> None:
    payload = {
        "brand": "Fiat",
        "model": "Cronos",
        "quantity": 5,
    }
    headers = {"Authorization": f"Bearer {buyer_token}"}
    resp = client.post(INVENTORY_PATH, json=payload, headers=headers)
    ctx["resp"] = resp


@when("intento crear un item de inventario como agency")
def create_inventory_as_agency(
    client: TestClient,
    agency_token: str,
    ctx: Dict[str, Any],
) -> None:
    payload = {
        "brand": "Fiat",
        "model": "Cronos",
        "quantity": 5,
    }
    headers = {"Authorization": f"Bearer {agency_token}"}
    resp = client.post(INVENTORY_PATH, json=payload, headers=headers)
    ctx["resp"] = resp


@then("la respuesta HTTP es 403")
def assert_403(ctx: Dict[str, Any]) -> None:
    resp = ctx["resp"]
    assert resp.status_code == status.HTTP_403_FORBIDDEN, resp.text


@then("la respuesta HTTP es 201")
def assert_201(ctx: Dict[str, Any]) -> None:
    resp = ctx["resp"]
    assert resp.status_code == status.HTTP_201_CREATED, resp.text


@then("la respuesta contiene un item de inventario creado correctamente")
def assert_inventory_created(ctx: Dict[str, Any]) -> None:
    resp = ctx["resp"]
    body = resp.json()
    # shape básico del InventoryItemOut
    assert "id" in body
    assert body["brand"] == "Fiat"
    assert body["model"] == "Cronos"
    assert body["quantity"] == 5
    # si querés, podés chequear is_used si está siempre en el schema
    # assert body["is_used"] is False
