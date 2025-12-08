import os, sys
import pytest
from sqlalchemy import StaticPool, create_engine
from sqlalchemy.orm import sessionmaker, Session
from collections.abc import Iterator

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

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
from app.models.car_model import CarModel
from app.models.inventory import Inventory
from app.core.security import hash_password

engine = create_engine(
    os.environ["DATABASE_URL"],
    connect_args={"check_same_thread": False},
    future=True,
    poolclass=StaticPool,
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
        s.rollback()
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
    existing = db.query(User).filter_by(email="buyer@example.com").first()
    if existing:
        return existing
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
def admin_user(db: Session) -> User:
    existing = db.query(User).filter_by(email="admin@example.com").first()
    if existing:
        return existing

    u = User(
        email="admin@example.com",
        password_hash=hash_password("secret"),
        role=UserRole.admin,
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
def agency_user(db: Session, agency: Agency) -> User:
    existing = db.query(User).filter_by(email="agency@example.com").first()
    if existing:
        return existing

    u = User(
        email="agency@example.com",
        password_hash=hash_password("secret"),
        role=UserRole.agency,
        is_active=True,
        agency_id=agency.id,
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


@pytest.fixture()
def fiat_cronos_carmodel(db: Session) -> CarModel:
    existing = db.query(CarModel).filter_by(brand="Fiat", model="Cronos").first()
    if existing:
        return existing

    cm = CarModel(brand="Fiat", model="Cronos")
    db.add(cm)
    db.commit()
    db.refresh(cm)
    return cm


@pytest.fixture()
def sample_listing(db: Session, agency: Agency) -> Listing:
    car_model = CarModel(
        brand="Fiat",
        model="Cronos",
        # year es opcional
    )
    db.add(car_model)
    db.commit()
    db.refresh(car_model)
    l = Listing(
        agency_id=agency.id,
        car_model_id=car_model.id,
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


@pytest.fixture()
def second_buyer_user(db: Session) -> User:

    existing = db.query(User).filter_by(email="buyer2@example.com").first()
    if existing:
        return existing
    u = User(
        email="buyer2@example.com",
        password_hash=hash_password("secret"),
        role=UserRole.buyer,
        is_active=True,
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


@pytest.fixture()
def fiat_cronos_inventory(
    db: Session,
    agency: Agency,
    fiat_cronos_carmodel: CarModel,
) -> Inventory:

    existing = (
        db.query(Inventory)
        .filter_by(agency_id=agency.id, car_model_id=fiat_cronos_carmodel.id)
        .first()
    )
    if existing:
        return existing

    inv = Inventory(
        agency_id=agency.id,
        car_model_id=fiat_cronos_carmodel.id,
        quantity=10,
    )
    db.add(inv)
    db.commit()
    db.refresh(inv)
    return inv
