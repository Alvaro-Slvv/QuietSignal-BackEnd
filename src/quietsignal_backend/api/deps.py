from fastapi import Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import Optional, Callable
from ..utils.jwtHandler import decode_token
from ..models.entities.userEntity import User
from ..models.dao.userDAO import UserDAO
from ..database import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")  # used by docs and header flows

def _get_token_from_request(request: Request) -> Optional[str]:
    # 1) Check Authorization header first (Bearer ...)
    auth: str = request.headers.get("Authorization")
    if auth and auth.lower().startswith("bearer "):
        return auth.split(" ", 1)[1].strip()
    # 2) Then check cookie "access_token"
    token = request.cookies.get("access_token")
    return token

def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    token = _get_token_from_request(request)
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = decode_token(token)
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user = UserDAO.get_by_username(db, username)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

# variant that returns None instead of raising - useful for /me where you may want to handle not logged in
def get_current_user_or_none(request: Request, db: Session = Depends(get_db)) -> Optional[User]:
    token = _get_token_from_request(request)
    if not token:
        return None
    try:
        payload = decode_token(token)
        username: str = payload.get("sub")
        if not username:
            return None
    except Exception:
        return None
    return UserDAO.get_by_username(db, username)

# role enforcement dependency factory
def require_role(role: str) -> Callable:
    def _require_role(user: User = Depends(get_current_user)):
        if user.role != role:
            raise HTTPException(status_code=403, detail="Insufficient privileges")
        return user
    return _require_role
