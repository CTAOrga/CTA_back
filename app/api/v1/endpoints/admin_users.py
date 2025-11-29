from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user, require_role
from app.models.user import User, UserRole
from app.schemas.user import PaginatedUsersOut
from app.services import admin_users as admin_users_service

router = APIRouter()


@router.get(
    "",
    response_model=PaginatedUsersOut,
    dependencies=[Depends(require_role(UserRole.admin))],
)
def list_registered_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    q: Optional[str] = Query(None, description="Filtro por email (like)"),
    role: Optional[UserRole] = Query(None, description="Filtro por rol"),
    db: Session = Depends(get_db),
):
    """
    Lista usuarios registrados (solo admin),
    con paginado y filtros básicos.
    """
    return admin_users_service.list_users(
        db=db,
        page=page,
        page_size=page_size,
        q=q,
        role=role,
    )
