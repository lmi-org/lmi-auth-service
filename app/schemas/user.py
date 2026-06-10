from datetime import datetime

from pydantic import BaseModel, EmailStr, ConfigDict


class UserBase(BaseModel):
    email: EmailStr
    username: str
    display_name: str


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    display_name: str | None = None


class UserResponse(UserBase):
    id: str
    is_verified: bool
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
    