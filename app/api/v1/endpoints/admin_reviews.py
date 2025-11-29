# app/api/v1/endpoints/admin_reviews.py
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_role
from app.models.user import UserRole
from app.schemas.admin_reviews import PaginatedAdminReviewsOut
from app.services import admin_reviews as admin_reviews_service

router = APIRouter()


@router.get(
    "",
    response_model=PaginatedAdminReviewsOut,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_role(UserRole.admin))],
)
def list_admin_reviews(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    q: Optional[str] = Query(
        None,
        description="Buscar por email, auto (brand/model) o comentario",
    ),
    min_rating: Optional[int] = Query(None, ge=1, le=5),
    max_rating: Optional[int] = Query(None, ge=1, le=5),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    db: Session = Depends(get_db),
):

    return admin_reviews_service.list_reviews(
        db=db,
        page=page,
        page_size=page_size,
        q=q,
        min_rating=min_rating,
        max_rating=max_rating,
        date_from=date_from,
        date_to=date_to,
    )
