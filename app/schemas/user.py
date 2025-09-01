from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from app.models.user import UserRole


class UserOut(BaseModel):
    id: int
    email: EmailStr
    role: UserRole
    agency_id: Optional[int] = None

    class Config:
        from_attributes = True


class RegisterBuyer(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)


class CreateAgencyUser(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    agency_name: str = Field(min_length=2, max_length=255)


class LoginInput(BaseModel):
    email: EmailStr
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: UserRole
    agency_id: Optional[int] = None
