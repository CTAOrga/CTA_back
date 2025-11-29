# app/services/admin_reviews.py
from datetime import date, datetime, time, timedelta
from typing import Optional

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.models.review import Review
from app.models.user import User
from app.models.car_model import CarModel
from app.schemas.admin_reviews import AdminReviewOut, PaginatedAdminReviewsOut


def list_reviews(
    db: Session,
    page: int = 1,
    page_size: int = 20,
    q: Optional[str] = None,  # busca en email, brand, model, comment
    min_rating: Optional[int] = None,
    max_rating: Optional[int] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
) -> PaginatedAdminReviewsOut:

    if page < 1:
        page = 1
    if page_size < 1:
        page_size = 20

    query = (
        db.query(Review, User, CarModel)
        .join(User, Review.author_id == User.id)
        .join(CarModel, Review.car_model_id == CarModel.id)
    )

    if q:
        like = f"%{q}%"
        query = query.filter(
            or_(
                User.email.ilike(like),
                CarModel.brand.ilike(like),
                CarModel.model.ilike(like),
                Review.comment.ilike(like),
            )
        )

    if min_rating is not None:
        query = query.filter(Review.rating >= min_rating)

    if max_rating is not None:
        query = query.filter(Review.rating <= max_rating)

    if date_from:
        dt_from = datetime.combine(date_from, time.min)
        query = query.filter(Review.created_at >= dt_from)

    if date_to:
        dt_to = datetime.combine(date_to + timedelta(days=1), time.min)
        query = query.filter(Review.created_at < dt_to)

    total = query.count()

    offset = (page - 1) * page_size
    rows = (
        query.order_by(Review.created_at.desc()).offset(offset).limit(page_size).all()
    )

    items: list[AdminReviewOut] = []
    for review, user, car_model in rows:
        items.append(
            AdminReviewOut(
                id=review.id,
                car_model_id=car_model.id,
                brand=car_model.brand,
                model=car_model.model,
                buyer_id=user.id,
                buyer_email=user.email,
                rating=review.rating,
                comment=review.comment,
                created_at=review.created_at,
            )
        )

    return PaginatedAdminReviewsOut(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )
