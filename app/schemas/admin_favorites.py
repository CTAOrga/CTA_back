from datetime import datetime
from pydantic import BaseModel
from typing import List
from app.models.user import UserRole


class AdminFavoriteOut(BaseModel):
    id: int
    listing_id: int
    customer_id: int
    customer_email: str
    brand: str
    model: str
    created_at: datetime

    class Config:
        from_attributes = True


class PaginatedAdminFavoritesOut(BaseModel):
    items: List[AdminFavoriteOut]
    total: int
    page: int
    page_size: int
