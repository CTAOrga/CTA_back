from pydantic import BaseModel, Field


class ItemCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)


class ItemOut(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True
