from pydantic import BaseModel
from datetime import datetime


class FavoriteOut(BaseModel):
    id: int
    listing_id: int


class FavoriteWithListingOut(BaseModel):
    favorite_id: int
    listing_id: int
    brand: str
    model: str
    agency_id: int | None = None
    price: float | None = None
    currency: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True
