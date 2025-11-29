from datetime import datetime
from pydantic import BaseModel, EmailStr


class TopSoldCarOut(BaseModel):
    brand: str
    model: str
    units_sold: int
    total_amount: float


class TopBuyerOut(BaseModel):
    buyer_id: int
    email: EmailStr
    purchases_count: int
    total_spent: float
    last_purchase_at: datetime | None = None


class TopAgencyOut(BaseModel):
    agency_id: int
    agency_name: str
    sales_count: int
    total_amount: float


class TopFavoriteCarOut(BaseModel):
    brand: str
    model: str
    favorites_count: int

    class Config:
        orm_mode = True
