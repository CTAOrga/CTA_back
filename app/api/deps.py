# app/api/deps.py
from typing import Any
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.security import decode_token
from app.db.session import get_db
from app.models.user import User, UserRole

bearer = HTTPBearer(auto_error=True)


def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(bearer),
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

    # Aceptamos str o int y convertimos seguro
    if isinstance(sub, int):
        user_id = sub
    elif isinstance(sub, str):
        try:
            user_id = int(sub)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Token 'sub' inválido"
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token 'sub' inválido"
        )

    user = db.get(User, user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no válido"
        )

    return user


def require_role(*roles: UserRole):
    def _dep(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="forbidden"
            )
        return user

    return _dep
