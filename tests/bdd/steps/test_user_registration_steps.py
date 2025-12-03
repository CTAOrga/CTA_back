from typing import Any, Dict
import os

import pytest
from fastapi.testclient import TestClient
from pytest_bdd import scenarios, when, then, parsers
from fastapi import status
from sqlalchemy.orm import Session

from app.models.user import User, UserRole

REGISTER_PATH = os.getenv("REGISTER_PATH", "/api/v1/auth/register")

scenarios("../features/user_registration.feature")


@pytest.fixture
def ctx() -> Dict[str, Any]:
    return {}


@when(parsers.parse('me registro con email "{email}" y password "{password}"'))
def register_user(client: TestClient, ctx: Dict[str, Any], email: str, password: str):
    payload = {
        "email": email,
        "password": password,
    }
    resp = client.post(REGISTER_PATH, json=payload)
    ctx["resp"] = resp


@then("el registro es exitoso")
def assert_register_ok(ctx: Dict[str, Any]):
    resp = ctx["resp"]
    assert resp.status_code == status.HTTP_201_CREATED, resp.text


@then("el usuario registrado tiene rol buyer")
def assert_registered_user_is_buyer(ctx: Dict[str, Any], db: Session):
    resp = ctx["resp"]
    body = resp.json()

    assert "email" in body
    assert "role" in body

    email = body["email"]
    role = body["role"]

    user = db.query(User).filter(User.email == email).first()
    assert user is not None
    assert user.role == UserRole.buyer

    assert role == UserRole.buyer
