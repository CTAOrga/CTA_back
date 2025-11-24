from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Optional


class ListingBase(BaseModel):
    brand: str = Field(..., min_length=1, max_length=80)
    model: str = Field(..., min_length=1, max_length=80)
    current_price_amount: float = Field(..., ge=0)
    current_price_currency: str = Field(default="USD", min_length=3, max_length=3)
    stock: int = Field(default=1, ge=0)
    seller_notes: Optional[str] = None
    expires_on: Optional[str] = None  # ISO datetime string


class ListingCreate(ListingBase):
    agency_id: int  # para agency podemos inferirlo del user.agency_id (ver endpoint)


class ListingUpdate(BaseModel):
    brand: Optional[str] = None
    model: Optional[str] = None
    current_price_amount: Optional[float] = Field(None, ge=0)
    current_price_currency: Optional[str] = Field(None, min_length=3, max_length=3)
    stock: Optional[int] = Field(None, ge=0)
    seller_notes: Optional[str] = None
    expires_on: Optional[str] = None


class ListingOut(BaseModel):
    id: int
    agency_id: int
    brand: str
    model: str
    current_price_amount: float
    current_price_currency: str
    stock: int
    seller_notes: Optional[str] = None
    is_favorite: bool = False
    avg_rating: Optional[float] = None
    reviews_count: int = 0


class ListingAgencyOut(BaseModel):
    id: int
    car_model_id: int
    price: float
    currency: str
    stock: int
    is_active: bool
    created_at: datetime

    brand: str
    model: str

    class Config:
        from_attributes = True  # pydantic v2: permite orm -> schema


class PaginatedListingsOut(BaseModel):
    items: List[ListingAgencyOut]
    total: int
    page: int
    page_size: int
