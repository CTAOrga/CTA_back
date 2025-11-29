from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.user import User, UserRole
from app.models.agency import Agency
from app.schemas.user import AdminUserSummary, PaginatedUsersOut


def list_users(
    db: Session,
    page: int = 1,
    page_size: int = 20,
    q: Optional[str] = None,
    role: Optional[UserRole] = None,
) -> PaginatedUsersOut:

    if page < 1:
        page = 1
    if page_size < 1:
        page_size = 20

    query = db.query(User, Agency).outerjoin(Agency, User.agency_id == Agency.id)

    if q:
        like = f"%{q}%"
        query = query.filter(User.email.ilike(like))

    if role is not None:
        query = query.filter(User.role == role)

    total = query.count()

    offset = (page - 1) * page_size

    rows = query.order_by(User.id.asc()).offset(offset).limit(page_size).all()

    items: list[AdminUserSummary] = []
    for user, agency in rows:
        items.append(
            AdminUserSummary(
                id=user.id,
                email=user.email,
                role=user.role,
                agency_id=user.agency_id,
                agency_name=agency.name if agency else None,
                created_at=user.created_at,
            )
        )

    return PaginatedUsersOut(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )
