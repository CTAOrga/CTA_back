from typing import Optional
from sqlalchemy.orm import Session

from app.models.user import User
from app.core.security import verify_password


def authenticate(db: Session, email: str, password: str) -> Optional[User]:
    """
    Autentica por email+password.
    Devuelve el User si es válido y está activo; si no, None.
    """
    user = db.query(User).filter(User.email == email).first()
    if not user or not user.is_active:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user
