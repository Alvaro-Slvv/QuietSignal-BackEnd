from datetime import datetime
from typing import Optional
import jwt

from ..config import settings

def create_access_token(data: dict, expires_delta: Optional[int] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (settings.access_token_expires)
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return token


def decode_access_token(token: str) -> dict:
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    return payload
