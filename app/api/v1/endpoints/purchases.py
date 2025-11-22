# app/api/v1/endpoints/purchases.py
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, require_role
from app.models.user import User, UserRole
from app.schemas.purchase import PurchaseCreate, PurchaseOut
from app.services import purchases as purchases_service

router = APIRouter()


@router.post(
    "",
    response_model=PurchaseOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role(UserRole.buyer))],
)
def create_purchase(
    payload: PurchaseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return purchases_service.create_purchase_for_buyer(
        db=db,
        buyer=current_user,
        payload=payload,
    )


@router.get(
    "/my",
    response_model=list[PurchaseOut],
    dependencies=[Depends(require_role(UserRole.buyer))],
)
def list_my_purchases(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Devuelve las compras del buyer logueado (activas y canceladas).
    Ideal para la pantalla 'Mis compras'.
    """
    return purchases_service.list_purchases_for_buyer(db=db, buyer=current_user)


@router.post(
    "/{purchase_id}/cancel",
    response_model=PurchaseOut,
    dependencies=[Depends(require_role(UserRole.buyer))],
)
def cancel_purchase(
    purchase_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return purchases_service.cancel_purchase_for_buyer(
        db=db,
        buyer=current_user,
        purchase_id=purchase_id,
    )


@router.post(
    "/{purchase_id}/reactivate",
    response_model=PurchaseOut,
    dependencies=[Depends(require_role(UserRole.buyer))],
)
def reactivate_purchase(
    purchase_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return purchases_service.reactivate_purchase_for_buyer(
        db=db,
        buyer=current_user,
        purchase_id=purchase_id,
    )
