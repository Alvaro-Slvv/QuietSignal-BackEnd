from fastapi import Depends, Cookie, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..utils.jwtHandler import decode_token
from ..models.dao.userDAO import UserDAO


def get_current_user(
    db: Session = Depends(get_db),
    token: str | None = Cookie(default=None, alias="access_token")
):
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = decode_token(token)
        username: str = payload.get("sub")
    except:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    if not username:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    user = UserDAO.get_by_username(db, username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user
