from typing import Dict

import pytest
from sqlalchemy.orm import Session
from pytest_bdd import given, scenarios, when, then, parsers

from app.services.auth_service import authenticate
from app.models.user import User, UserRole

# Vincula el .feature
scenarios("../features/authenticate_service.feature")


# Contexto simple para compartir estado entre steps
@pytest.fixture
def ctx() -> Dict[str, object]:
    return {}


@when(parsers.parse('intento autenticar con password "{plain}"'))
def try_auth_buyer(db: Session, ensure_buyer: User, ctx: dict, plain: str):
    user = authenticate(db, ensure_buyer.email, plain)
    ctx["auth_user"] = user


@when(parsers.parse('intento autenticar el admin con password "{plain}"'))
def try_auth_admin(db: Session, ensure_admin: User, ctx: dict, plain: str):
    user = authenticate(db, ensure_admin.email, plain)
    ctx["auth_user"] = user


@then("la autenticación es exitosa")
def auth_ok(ctx: dict, ensure_buyer: User):
    user = ctx.get("auth_user")
    assert user is not None
    assert user.email == ensure_buyer.email
    assert user.role == UserRole.buyer


@then("la autenticación falla")
def auth_fails(ctx: dict):
    assert ctx.get("auth_user") is None


@then("la autenticación es exitosa como admin")
def auth_ok_admin(ctx: dict, ensure_admin: User):
    user = ctx.get("auth_user")
    assert user is not None
    assert user.email == ensure_admin.email
    assert user.role == UserRole.admin
