# tests/conftest.py
import os, sys
import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from collections.abc import Iterator

# --- Config test ---
os.environ.setdefault("APP_ENV", "test")
os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")

from app.db.base import Base
from app.main import app
from app.api.deps import get_db
from starlette.testclient import TestClient

from app.models.user import User, UserRole
from app.models.agency import Agency
from app.models.listing import Listing
from app.core.security import hash_password

engine = create_engine(
    os.environ["DATABASE_URL"],
    connect_args={"check_same_thread": False},
    future=True,
)
TestingSessionLocal = sessionmaker(
    bind=engine, autoflush=False, autocommit=False, future=True
)


# ------ Esquema una vez por sesión de test ------
@pytest.fixture(scope="session", autouse=True)
def create_schema():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


# ------ Sesión por test ------
@pytest.fixture()
def db() -> Iterator[Session]:
    s = TestingSessionLocal()
    try:
        yield s
    finally:
        # Limpieza simple: borrar tablas en orden inverso de FKs
        # (para SQLite suele ir bien; si usás FKs estrictas, podés desactivar/activar)
        for tbl in reversed(Base.metadata.sorted_tables):
            s.execute(tbl.delete())
        s.commit()
        s.close()


# ------ Override FastAPI get_db para usar la misma sesión del test ------
@pytest.fixture(autouse=True)
def _override_db_dep(db: Session):
    def _override_get_db():
        try:
            yield db
        finally:
            # la fixture db maneja el cierre/limpieza
            pass

    app.dependency_overrides[get_db] = _override_get_db
    yield
    app.dependency_overrides.pop(get_db, None)


# ------ Cliente HTTP de pruebas ------
@pytest.fixture()
def client():
    return TestClient(app)


# ------ Datos base (usan SIEMPRE la sesión 'db' del test) ------
@pytest.fixture()
def buyer_user(db: Session) -> User:
    u = User(
        email="buyer@example.com",
        password_hash=hash_password("secret"),
        role=UserRole.buyer,
        is_active=True,
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


@pytest.fixture()
def agency(db: Session) -> Agency:
    a = Agency(name="CompraCar")
    db.add(a)
    db.commit()
    db.refresh(a)
    return a


@pytest.fixture()
def sample_listing(db: Session, agency: Agency) -> Listing:
    l = Listing(
        agency_id=agency.id,
        brand="Fiat",
        model="Cronos",
        current_price_amount=10000.0,
        current_price_currency="USD",
        stock=1,
        seller_notes="OK",
    )
    db.add(l)
    db.commit()
    db.refresh(l)
    return l
