# app/schemas/favorite.py
from pydantic import BaseModel


class FavoriteOut(BaseModel):
    id: int
    listing_id: int

    class Config:
        from_attributes = True
