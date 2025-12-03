from typing import Any, Dict
import os

import pytest
from fastapi.testclient import TestClient
from fastapi import status
from pytest_bdd import scenarios, when, then, parsers

LOGIN_PATH = os.getenv("LOGIN_PATH", "/api/v1/auth/login")

scenarios("../features/login.feature")


@pytest.fixture
def ctx() -> Dict[str, Any]:
    return {}


@when(parsers.parse('hago login con email "{email}" y password "{password}"'))
def do_login(
    client: TestClient, ctx: Dict[str, Any], email: str, password: str
) -> None:
    resp = client.post(
        LOGIN_PATH,
        json={"email": email, "password": password},
    )
    ctx["resp"] = resp


@then("la autenticación HTTP es exitosa")
def assert_login_ok(ctx: Dict[str, Any]) -> None:
    resp = ctx["resp"]
    assert resp.status_code == status.HTTP_200_OK, resp.text


@then("la respuesta incluye un access token")
def assert_access_token_present(ctx: Dict[str, Any]) -> None:
    resp = ctx["resp"]
    data = resp.json()
    assert "access_token" in data
    assert isinstance(data["access_token"], str)
    assert data["access_token"]


@then("la autenticación HTTP falla")
def assert_login_fails(ctx: Dict[str, Any]) -> None:
    resp = ctx["resp"]
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED, resp.text
