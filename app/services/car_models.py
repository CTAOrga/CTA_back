from typing import Optional, List

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.car_model import CarModel


def search_car_models(
    db: Session,
    q: Optional[str] = None,
    limit: int = 20,
) -> List[CarModel]:

    query = db.query(CarModel)

    if q:
        like = f"%{q}%"
        query = query.filter(
            or_(
                CarModel.brand.ilike(like),
                CarModel.model.ilike(like),
            )
        )

    return query.order_by(CarModel.brand, CarModel.model).limit(limit).all()
