# app/db/seed.py
from sqlalchemy.orm import sessionmaker

from app.db.session import get_engine
from app.models.agency import Agency
from app.models.listing import Listing
from app.models.car_model import CarModel


def get_or_create_carmodel(db, brand: str, model: str) -> CarModel:
    """
    Busca un CarModel por (brand, model). Si existe, lo devuelve.
    Si no existe, lo crea, lo agrega a la sesión y lo devuelve.
    """
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
    db.flush()  # para que tenga cm.id sin hacer commit todavía
    return cm


def run():
    engine = get_engine()
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    with db.begin():
        # Agencias demo
        for i, name in [(1, "CompraCar"), (2, "Libertad")]:
            if not db.get(Agency, i):
                db.add(Agency(id=i, name=name))

        # Listings demo
        if db.query(Listing).count() == 0:
            # creamos (o reutilizamos) los CarModels
            onix_cm = get_or_create_carmodel(db, "Chevrolet", "Onix")
            cronos_cm = get_or_create_carmodel(db, "Fiat", "Cronos")

            db.add_all(
                [
                    Listing(
                        agency_id=1,
                        car_model_id=onix_cm.id,
                        brand="Chevrolet",
                        model="Onix",
                        current_price_amount=9200,
                        current_price_currency="USD",
                        stock=4,
                        seller_notes="Muy buen estado",
                    ),
                    Listing(
                        agency_id=2,
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

    db.close()


if __name__ == "__main__":
    run()
