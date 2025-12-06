import pytest
from sqlalchemy.orm import Session
from app.models.agency import Agency
from app.models.car_model import CarModel
from app.models.listing import Listing


@pytest.fixture()
def listings_for_top_selling(db: Session, agency: Agency) -> list[Listing]:
    cars_data = [
        ("Fiat", "Cronos"),  # 0
        ("Ford", "Focus"),  # 1
        ("Toyota", "Corolla"),  # 2
        ("Peugeot", "208"),  # 3
        ("Chevrolet", "Onix"),  # 4
        ("Renault", "Sandero"),  # 5
        ("Volkswagen", "Golf"),  # 6
    ]

    listings: list[Listing] = []

    for brand, model in cars_data:
        car_model = CarModel(brand=brand, model=model)
        db.add(car_model)
        db.commit()
        db.refresh(car_model)

        listing = Listing(
            agency_id=agency.id,
            car_model_id=car_model.id,
            brand=brand,
            model=model,
            current_price_amount=10000.0,
            current_price_currency="USD",
            stock=50,  # stock holgado para el test
            seller_notes="Listing para test de top-selling",
        )
        db.add(listing)
        db.commit()
        db.refresh(listing)

        listings.append(listing)

    return listings
