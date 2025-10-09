from typing import Dict

import pytest
from sqlalchemy.orm import Session
from pytest_bdd import given, scenarios, when, then, parsers

from app.services.auth_service import authenticate
from app.models.user import User, UserRole

# Vincula el .feature
scenarios("../features/auth_service.feature")


# Contexto simple para compartir estado entre steps
@pytest.fixture
def ctx() -> Dict[str, object]:
    return {}


@given("existe un usuario buyer en la base", target_fixture="ensure_buyer")
def ensure_buyer(buyer_user: User) -> User:
    return buyer_user


@when(parsers.parse('intento autenticar con password "{plain}"'))
def try_auth(db: Session, ensure_buyer: User, ctx: dict, plain: str):
    # ensure_buyer viene del step común y es un User real
    user = authenticate(db, ensure_buyer.email, plain)
    ctx["auth_user"] = user


@then("la autenticación falla")
def auth_fails(ctx: dict):
    assert ctx.get("auth_user") is None


@then("la autenticación es exitosa")
def auth_ok(ctx: dict, ensure_buyer: User):
    user = ctx.get("auth_user")
    assert user is not None
    assert user.email == ensure_buyer.email
    assert user.role == UserRole.buyer
