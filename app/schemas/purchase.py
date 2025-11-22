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

    class Config:
        from_attributes = True
