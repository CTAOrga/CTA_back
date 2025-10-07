from sqlalchemy.orm import sessionmaker
from app.db.session import get_engine
from app.models.agency import Agency
from app.models.listing import Listing


def run():
    engine = get_engine()
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    with db.begin():
        # Aseguro agencias 1 y 2 (si no existen)
        for i, name in [(1, "CompraCar"), (2, "Libertad")]:
            if not db.get(Agency, i):
                db.add(Agency(id=i, name=name))

        # Semilla de listings si está vacío
        if db.query(Listing).count() == 0:
            db.add_all(
                [
                    Listing(
                        agency_id=1,
                        brand="Chevrolet",
                        model="Onix",
                        current_price_amount=9200,
                        current_price_currency="USD",
                        stock=4,
                        seller_notes="Muy buen estado",
                    ),
                    Listing(
                        agency_id=2,
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
