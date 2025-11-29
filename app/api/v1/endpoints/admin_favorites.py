from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, require_role
from app.models.user import User, UserRole
from app.schemas.admin_favorites import PaginatedAdminFavoritesOut
from app.services import admin_favorites as admin_favorites_service

router = APIRouter()


@router.get(
    "",
    response_model=PaginatedAdminFavoritesOut,
    dependencies=[Depends(require_role(UserRole.admin))],
)
def list_admin_favorites(
    page: int = 1,
    page_size: int = 20,
    q: Optional[str] = Query(
        None, description="Buscar por email de cliente o marca/modelo"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Lista paginada de autos de interés (favoritos) guardados por los usuarios.
    """
    return admin_favorites_service.list_favorites(
        db=db,
        page=page,
        page_size=page_size,
        q=q,
    )
