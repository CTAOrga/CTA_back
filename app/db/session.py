from collections.abc import Generator
from sqlalchemy import create_engine, text
import time
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings
from sqlalchemy.exc import OperationalError

_engine = None
_SessionLocal = None


def _wait_for_db(url: str, attempts: int = 45, delay: float = 2.0) -> None:
    """
    Intenta conectar y hacer SELECT 1 con reintentos (máx ~90s).
    Lanza OperationalError si no consigue conectar.
    """
    last_err = None
    for i in range(1, attempts + 1):
        try:
            # engine efímero solo para test, no lo guardamos
            tmp_engine = create_engine(url, pool_pre_ping=True)
            with tmp_engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            tmp_engine.dispose()
            return
        except OperationalError as e:
            last_err = e
            print(
                f"[DB] Intento {i}/{attempts}: MySQL no responde aún ({e.__class__.__name__}). "
                f"Reintentando en {delay}s…"
            )
            time.sleep(delay)
    if last_err:
        raise last_err
    raise RuntimeError("DB no disponible tras reintentos")


def get_engine():
    global _engine, _SessionLocal
    if _engine is None:
        if not settings.DATABASE_URL:
            raise RuntimeError("DATABASE_URL no está configurada en .env")

        # Espera activa a que MySQL quede listo
        _wait_for_db(settings.DATABASE_URL)

        _engine = create_engine(
            settings.DATABASE_URL,
            pool_pre_ping=True,  # valida sockets antes de reutilizarlos
            pool_recycle=1800,  # opcional, evita conexiones viejas
        )
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
