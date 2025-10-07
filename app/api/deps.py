from typing import Any, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.security import decode_token
from app.db.session import get_db
from app.models.user import User, UserRole

bearer_required = HTTPBearer(auto_error=True)
bearer_optional = HTTPBearer(auto_error=False)


def _as_int_id(value: object) -> Optional[int]:
    """Convierte str|int a int, sino None. Ayuda a Pylance a inferir tipos."""
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        try:
            return int(value)
        except ValueError:
            return None
    return None


def optional_current_user(
    creds: Optional[HTTPAuthorizationCredentials] = Depends(bearer_optional),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """
    Devuelve el User si viene 'Authorization: Bearer <token>' válido.
    Si no hay header o el token es inválido, devuelve None (no rompe).
    """
    if not creds:
        return None

    token = creds.credentials
    try:
        payload: dict[str, Any] = decode_token(token)
    except JWTError:
        return None

    user_id = _as_int_id(payload.get("sub"))
    if user_id is None:
        return None

    return db.get(User, user_id)


def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(bearer_required),
    db: Session = Depends(get_db),
) -> User:
    token = creds.credentials
    try:
        payload: dict[str, Any] = decode_token(token)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido"
        )

    sub = payload.get("sub")
    if sub is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token sin 'sub'"
        )

    user_id = _as_int_id(payload.get("sub"))
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token 'sub' inválido"
        )

    user = db.get(User, user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no válido"
        )
    return user


def require_role(*roles: UserRole | str):
    """
    Uso:
      dependencies=[Depends(require_role(UserRole.admin))]
      dependencies=[Depends(require_role(UserRole.admin, UserRole.agency))]
    """
    allowed: set[str] = set()
    for r in roles:
        if isinstance(r, UserRole):
            allowed.add(r.value)
        else:
            allowed.add(str(r))

    def _dep(user: User = Depends(get_current_user)) -> None:
        current = user.role.value if isinstance(user.role, UserRole) else str(user.role)
        if current not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        # no retornamos nada; si pasa, está autorizado

    return _dep
