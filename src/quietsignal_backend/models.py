from typing import Optional, Dict

from pydantic import BaseModel, Field
from sqlalchemy import Column, Integer, String

from .database import Base

# --- SQLAlchemy model ---

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)


# --- Pydantic schemas ---


class UserRegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(
        ...,
        min_length=6,
        max_length=72,  # bcrypt limit
        description="User password, max 72 characters due to bcrypt limitations",
    )


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class AnalyzeRequest(BaseModel):
    text: str = Field(..., min_length=1)


class AnalyzeResponse(BaseModel):
    label: str
    probabilities: Optional[Dict[str, float]] = None
