from collections.abc import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings

_engine = None
_SessionLocal = None

def get_engine():
    global _engine, _SessionLocal
    if _engine is None:
        if not settings.DATABASE_URL:
            raise RuntimeError("DATABASE_URL no está configurada en .env")
        _engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)
    return _engine

def get_db() -> Generator[Session, None, None]:
    global _SessionLocal
    if _SessionLocal is None:
        get_engine()
    db = _SessionLocal()
    try:
        yield db
    finally:
        db.close()
