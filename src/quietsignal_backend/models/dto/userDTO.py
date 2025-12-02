from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class UserCreateDTO(BaseModel):
    name: str = Field(..., min_length=3, max_length=50)
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=128)
    email: Optional[EmailStr] = None

    model_config = {"extra": "forbid"}


class UserOutDTO(BaseModel):
    id: int
    name: str
    username: str
    email: Optional[EmailStr] = None

    model_config = {"from_attributes": True, "extra": "forbid"}


class TokenResponseDTO(BaseModel):
    access_token: str
    token_type: str = "bearer"

    model_config = {"extra": "forbid"}


class LoginRequestDTO(BaseModel):
    username: str
    password: str

    model_config = {"extra": "forbid"}
