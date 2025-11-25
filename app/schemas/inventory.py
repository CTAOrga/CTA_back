from pydantic import BaseModel, Field
from typing import Optional


class InventoryItemBase(BaseModel):
    brand: str = Field(..., min_length=1, max_length=80)
    model: str = Field(..., min_length=1, max_length=80)
    quantity: int = Field(..., ge=0)
    is_used: bool = False


class InventoryItemCreate(InventoryItemBase):
    """Entrada para crear inventario de agencia."""

    pass


class InventoryItemUpdate(BaseModel):
    quantity: Optional[int] = Field(None, ge=0)
    is_used: Optional[bool] = None


class InventoryItemOut(BaseModel):
    id: int
    car_model_id: int
    brand: str
    model: str
    quantity: int
    is_used: bool

    class Config:
        from_attributes = True


class PaginatedInventoryOut(BaseModel):
    items: list[InventoryItemOut]
    total: int
    page: int
    page_size: int
