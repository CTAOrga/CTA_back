from datetime import datetime
from pydantic import BaseModel, Field

from app.models.purchase import PurchaseStatus


class PurchaseCreate(BaseModel):
    listing_id: int
    quantity: int = Field(default=1, ge=1)


class PurchaseOut(BaseModel):
    id: int
    listing_id: int
    buyer_id: int
    unit_price_amount: float
    unit_price_currency: str
    quantity: int
    status: PurchaseStatus


class AgencySaleOut(BaseModel):
    id: int
    listing_id: int
    buyer_id: int
    buyer_email: str

    brand: str
    model: str

    unit_price_amount: float
    unit_price_currency: str
    quantity: int
    total_amount: float

    status: PurchaseStatus
    created_at: datetime

    class Config:
        from_attributes = True


class AgencyCustomerOut(BaseModel):
    customer_id: int
    email: str
    total_purchases: int
    total_spent: float
    last_purchase_at: datetime

    class Config:
        from_attributes = True
