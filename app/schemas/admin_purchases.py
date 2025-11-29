from datetime import datetime
from pydantic import BaseModel
from app.models.purchase import PurchaseStatus


class AdminPurchaseOut(BaseModel):
    id: int
    listing_id: int
    buyer_id: int
    buyer_email: str
    agency_id: int
    agency_name: str
    brand: str
    model: str
    unit_price_amount: float
    unit_price_currency: str
    quantity: int
    total_amount: float
    status: PurchaseStatus
    created_at: datetime


class PaginatedAdminPurchasesOut(BaseModel):
    items: list[AdminPurchaseOut]
    total: int
    page: int
    page_size: int

    class Config:
        from_attributes = True
