from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, require_role
from app.models.user import UserRole, User
from app.models.car_model import CarModel
from app.schemas.car_model import CarModelOut
from app.services import car_models as car_models_service


router = APIRouter()


@router.get(
    "",
    response_model=list[CarModelOut],
    dependencies=[Depends(require_role(UserRole.agency))],
)
def search_car_models(
    q: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Devuelve modelos de auto del catálogo global (tabla car_models),
    filtrando por marca o modelo que contengan el texto `q`.
    """
    car_models = car_models_service.search_car_models(db=db, q=q, limit=20)
    return car_models
