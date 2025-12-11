from sqlalchemy.orm import sessionmaker

from app.db.session import get_engine
from app.db.base import Base
from app.models.user import User, UserRole
from app.models.agency import Agency
from app.models.car_model import CarModel
from app.models.listing import Listing
from app.core.security import hash_password


def reset_database(engine):

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def get_or_create_carmodel(db, brand: str, model: str) -> CarModel:
    cm = (
        db.query(CarModel)
        .filter(
            CarModel.brand == brand,
            CarModel.model == model,
        )
        .first()
    )
    if cm:
        return cm

    cm = CarModel(brand=brand, model=model)
    db.add(cm)
    db.flush()
    return cm


def get_or_create_user(db, email: str, role: UserRole, password: str, agency_id=None):
    u = db.query(User).filter(User.email == email).first()
    if u:
        return u
    u = User(
        email=email,
        password_hash=hash_password(password),
        role=role,
        is_active=True,
        agency_id=agency_id,
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


def run():
    engine = get_engine()
    reset_database(engine)

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    try:
        # 1) Agencias demo
        agencia1 = Agency(name="Agency_demo_k6")
        agencia2 = Agency(name="Agency2_demo_k6")
        db.add_all([agencia1, agencia2])
        db.commit()
        db.refresh(agencia1)
        db.refresh(agencia2)

        # 2) Usuarios DEMO (para k6)
        admin_user = get_or_create_user(
            db,
            email="admin3@example.com",
            role=UserRole.admin,
            password="Admin3123!",
            agency_id=None,
        )

        agency_user = get_or_create_user(
            db,
            email="agency_demo@cta.com",
            role=UserRole.agency,
            password="Demo1234!",
            agency_id=agencia1.id,
        )

        buyer_user = get_or_create_user(
            db,
            email="buyer_demo@cta.com",
            role=UserRole.buyer,
            password="Demo1234!",
            agency_id=None,
        )

        # 3) CarModels + Listings demo
        onix_cm = get_or_create_carmodel(db, "Chevrolet", "Onix")
        cronos_cm = get_or_create_carmodel(db, "Fiat", "Cronos")

        db.add_all(
            [
                Listing(
                    agency_id=agencia1.id,
                    car_model_id=onix_cm.id,
                    brand="Chevrolet",
                    model="Onix",
                    current_price_amount=9200,
                    current_price_currency="USD",
                    stock=4,
                    seller_notes="Muy buen estado",
                ),
                Listing(
                    agency_id=agencia2.id,
                    car_model_id=cronos_cm.id,
                    brand="Fiat",
                    model="Cronos",
                    current_price_amount=10500,
                    current_price_currency="USD",
                    stock=3,
                    seller_notes="Pocos km",
                ),
            ]
        )
        db.commit()

        print("Seed DEMO K6 ejecutado OK:")
        print(f"- Admin user:  {admin_user.email}")
        print(f"- Agency user: {agency_user.email}")
        print(f"- Buyer user:  {buyer_user.email}")
        print(f"- Agencia1:    {agencia1.name} (id={agencia1.id})")
        print(f"- Agencia2:    {agencia2.name} (id={agencia2.id})")

    except Exception as e:
        db.rollback()
        print("Error en seed_demo_k6:", e)
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run()
