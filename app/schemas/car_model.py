from pydantic import BaseModel
from typing import Optional


class CarModelBase(BaseModel):
    brand: str
    model: str
    year: Optional[int] = None
    is_used: bool = False
    quantity: int = 0


class CarModelCreate(CarModelBase):
    pass


class CarModelOut(CarModelBase):
    id: int

    class Config:
        from_attributes = True
