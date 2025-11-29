from datetime import datetime
from pydantic import BaseModel, EmailStr


class AdminReviewOut(BaseModel):
    id: int
    car_model_id: int
    brand: str
    model: str
    buyer_id: int
    buyer_email: EmailStr
    rating: int
    comment: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class PaginatedAdminReviewsOut(BaseModel):
    items: list[AdminReviewOut]
    total: int
    page: int
    page_size: int
