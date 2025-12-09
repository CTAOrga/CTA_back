from sqlalchemy.orm import sessionmaker

from app.db.session import get_engine
from app.db.base import Base
from app.models.user import User, UserRole
from app.models.agency import Agency
from app.models.car_model import CarModel
from app.core.security import hash_password


def reset_database(engine):
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def create_perf_car_models(db):

    base_models = [
        {
            "brand": "Chevrolet",
            "model": "Onyx",
            "year": 2012,
        },
        {
            "brand": "Fiat",
            "model": "Cronos",
            "year": 2018,
        },
        {
            "brand": "Volkswagen",
            "model": "Gol trend",
            "year": 2008,
        },
    ]

    for data in base_models:
        existing = (
            db.query(CarModel)
            .filter(
                CarModel.brand == data["brand"],
                CarModel.model == data["model"],
                CarModel.year == data["year"],
            )
            .first()
        )
        if existing:
            continue

        cm = CarModel(**data)
        db.add(cm)

    db.commit()
    print("CarModels PERF creados/asegurados.")


def run():
    engine = get_engine()

    # Opcional: si querés que cta_perf se resetee siempre:
    reset_database(engine)

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    try:
        # 1) Agency PERF
        agency_name = "Agencia Perf CTA"
        agency = db.query(Agency).filter(Agency.name == agency_name).first()
        if not agency:
            agency = Agency(name=agency_name)
            db.add(agency)
            db.commit()
            db.refresh(agency)

        # 2) Usuarios PERF
        def get_or_create_user(email: str, role: UserRole, agency_id=None):
            u = db.query(User).filter(User.email == email).first()
            if u:
                return u
            u = User(
                email=email,
                password_hash=hash_password("Perf1234!"),
                role=role,
                is_active=True,
                agency_id=agency_id,
            )
            db.add(u)
            db.commit()
            db.refresh(u)
            return u

        agency_user = get_or_create_user(
            "agency_perf@cta.com", UserRole.agency, agency_id=agency.id
        )
        buyer_user = get_or_create_user(
            "buyer_perf@cta.com", UserRole.buyer, agency_id=None
        )

        # 3) CarModels PERF
        create_perf_car_models(db)

        print("Seed PERF mínimo ejecutado OK:")
        print(f"- Agency user: {agency_user.email}")
        print(f"- Buyer user:  {buyer_user.email}")
        print(f"- Agency:      {agency.name} (id={agency.id})")

    except Exception as e:
        db.rollback()
        print("Error en seed_perf:", e)
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run()
