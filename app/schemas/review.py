from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class ReviewCreate(BaseModel):
    listing_id: int
    rating: int = Field(ge=1, le=5)
    comment: Optional[str] = None


class ReviewUpdate(BaseModel):
    rating: Optional[int] = Field(default=None, ge=1, le=5)
    comment: Optional[str] = None


class ReviewOut(BaseModel):
    id: int
    car_model_id: int
    author_id: int
    rating: int
    comment: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class MyReviewRow(BaseModel):
    """
    Fila para 'Mis reseñas' del comprador.
    Incluye datos del modelo y un listing_id opcional para ir al detalle.
    """

    id: int
    car_model_id: int
    brand: str
    model: str
    rating: int
    comment: Optional[str]
    created_at: datetime
    listing_id: Optional[int] = None
