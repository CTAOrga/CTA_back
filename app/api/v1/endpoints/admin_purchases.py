from datetime import date, datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_role
from app.models.user import UserRole
from app.models.purchase import PurchaseStatus
from app.schemas.admin_purchases import PaginatedAdminPurchasesOut
from app.services import admin_purchases as admin_purchases_service

router = APIRouter()


@router.get(
    "",
    response_model=PaginatedAdminPurchasesOut,
    dependencies=[Depends(require_role(UserRole.admin))],
)
def list_all_purchases(
    page: int = 1,
    page_size: int = 20,
    q: Optional[str] = Query(None, description="Email, auto o agencia"),
    status: Optional[PurchaseStatus] = Query(
        None,
        description="Status de la compra (PENDING, COMPLETED, CANCELLED, etc.)",
    ),
    date_from: Optional[date] = Query(
        None,
        description="Fecha desde (YYYY-MM-DD) sobre Purchase.created_at",
    ),
    date_to: Optional[date] = Query(
        None,
        description="Fecha hasta (YYYY-MM-DD, inclusive)",
    ),
    db: Session = Depends(get_db),
):
    # Normalizar fechas a datetime (comienzo y fin del día)
    dt_from: datetime | None = None
    dt_to: datetime | None = None

    if date_from:
        dt_from = datetime.combine(date_from, datetime.min.time())
    if date_to:
        dt_to = datetime.combine(date_to, datetime.max.time())

    return admin_purchases_service.list_purchases_for_admin(
        db=db,
        page=page,
        page_size=page_size,
        q=q,
        status=status,
        date_from=dt_from,
        date_to=dt_to,
    )
