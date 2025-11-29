from datetime import date
from typing import Optional, List

from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, require_role
from app.models.user import User, UserRole
from app.schemas.reports import (
    TopAgencyOut,
    TopBuyerOut,
    TopFavoriteCarOut,
    TopSoldCarOut,
)
from app.services import admin_reports as reports_service
from app.utils.parse_date_param import _parse_date_param

router = APIRouter()


@router.get(
    "/top-sold-cars",
    response_model=List[TopSoldCarOut],
    dependencies=[Depends(require_role(UserRole.admin))],
)
def get_top_sold_cars(
    date_from: Optional[date] = Query(
        None, description="Filtrar compras desde esta fecha (YYYY-MM-DD)"
    ),
    date_to: Optional[date] = Query(
        None, description="Filtrar compras hasta esta fecha (YYYY-MM-DD)"
    ),
    limit: int = Query(
        5,
        ge=1,
        le=50,
        description="Cantidad máxima de autos a devolver (Top N)",
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # El require_role ya valida que sea admin, pero dejamos esto por claridad si querés
    if current_user.role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo un administrador puede ver estos reportes",
        )

    return reports_service.top_sold_cars(
        db=db,
        date_from=date_from,
        date_to=date_to,
        limit=limit,
    )


@router.get(
    "/top-buyers",
    response_model=list[TopBuyerOut],
    dependencies=[Depends(require_role(UserRole.admin))],
)
def get_top_buyers_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    date_from: Optional[str] = Query(
        None, description="Fecha desde (YYYY-MM-DD) sobre Purchase.created_at"
    ),
    date_to: Optional[str] = Query(
        None, description="Fecha hasta (YYYY-MM-DD) sobre Purchase.created_at"
    ),
    limit: int = Query(5, ge=1, le=100, description="Cantidad máxima de filas"),
):
    """
    Devuelve los usuarios con más compras (Top N).
    Solo Admin.
    """
    # Convertimos strings del query a datetime
    dt_from = _parse_date_param(date_from)
    dt_to = _parse_date_param(date_to)

    return reports_service.get_top_buyers(
        db=db,
        date_from=dt_from,
        date_to=dt_to,
        limit=limit,
    )


@router.get(
    "/top-favorites",
    response_model=list[TopFavoriteCarOut],
    dependencies=[Depends(require_role(UserRole.admin))],
)
def get_top_favorites_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    date_from: Optional[str] = Query(
        None, description="Fecha desde (YYYY-MM-DD) sobre Favorite.created_at"
    ),
    date_to: Optional[str] = Query(
        None, description="Fecha hasta (YYYY-MM-DD) sobre Favorite.created_at"
    ),
    limit: int = Query(5, ge=1, le=100, description="Cantidad máxima de filas"),
):
    """
    Devuelve los autos más marcados como favoritos (Top N).
    Solo Admin.
    """
    dt_from = _parse_date_param(date_from)
    dt_to = _parse_date_param(date_to)

    return reports_service.get_top_favorites(
        db=db,
        date_from=dt_from,
        date_to=dt_to,
        limit=limit,
    )


@router.get(
    "/top-agencies",
    response_model=list[TopAgencyOut],
    dependencies=[Depends(require_role(UserRole.admin))],
)
def get_top_agencies_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    date_from: Optional[str] = Query(None, description="Fecha desde (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="Fecha hasta (YYYY-MM-DD)"),
    limit: int = Query(5, ge=1, le=100, description="Cantidad máxima de filas"),
):
    dt_from = _parse_date_param(date_from)
    dt_to = _parse_date_param(date_to)

    return reports_service.get_top_agencies(
        db=db,
        date_from=dt_from,
        date_to=dt_to,
        limit=limit,
    )
