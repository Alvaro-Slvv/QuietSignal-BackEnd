from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.dao.userDAO import UserDAO
from ..utils.jwtHandler import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_db_dep():
    return Depends(get_db)


def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = decode_access_token(token)
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
    except Exception:
        raise credentials_exception

    user = UserDAO.get_by_username(db, username)
    if user is None:
        raise credentials_exception
    return user
