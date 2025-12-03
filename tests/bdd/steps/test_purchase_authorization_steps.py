from typing import Any, Dict
import os

import pytest
from fastapi.testclient import TestClient
from fastapi import status
from pytest_bdd import scenarios, when, then

from app.models.listing import Listing

PURCHASE_PATH = os.getenv("PURCHASE_PATH", "/api/v1/purchases")

# Vincula el feature
scenarios("../features/purchase_authorization.feature")


@pytest.fixture
def ctx() -> Dict[str, Any]:
    return {}


@when("intento crear una compra para esa listing")
def create_purchase_as_buyer(
    client: TestClient,
    buyer_token: str,
    existing_listing: Listing,
    ctx: Dict[str, Any],
):
    headers = {"Authorization": f"Bearer {buyer_token}"}
    payload = {
        "listing_id": existing_listing.id,
    }
    resp = client.post(PURCHASE_PATH, json=payload, headers=headers)
    ctx["resp"] = resp


@then("la respuesta HTTP es 201")
def assert_201(ctx: Dict[str, Any]) -> None:
    resp = ctx["resp"]
    assert resp.status_code == status.HTTP_201_CREATED, resp.text


@then("la respuesta contiene una compra creada correctamente")
def assert_purchase_created(ctx: Dict[str, Any]) -> None:
    resp = ctx["resp"]
    body = resp.json()

    assert "id" in body
    assert "listing_id" in body
    assert isinstance(body["id"], int)
