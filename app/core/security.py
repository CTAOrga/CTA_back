from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import jwt, JWTError
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)


def create_access_token(
    *,
    sub: str,
    role: str,
    agency_id: Optional[int] = None,
    expires_minutes: Optional[int] = None
) -> str:
    exp_min = expires_minutes or settings.ACCESS_TOKEN_EXPIRE_MINUTES
    expire = datetime.now(timezone.utc) + timedelta(minutes=exp_min)
    payload = {"sub": sub, "role": role, "exp": expire}
    if agency_id is not None:
        payload["agency_id"] = agency_id
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    # Levantá JWTError en quien lo use si falla
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
