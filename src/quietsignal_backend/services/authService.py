from sqlalchemy.orm import Session
from ..models.dao.userDAO import UserDAO
from ..utils.security import verify_password
from ..utils.jwtHandler import create_access_token


class AuthService:

    @staticmethod
    def authenticate(db: Session, username: str, password: str):
        user = UserDAO.get_by_username(db, username)

        if not user:
            return None

        if not verify_password(password, user.hashed_password):
            return None

        token, expire = create_access_token({"sub": user.username})
        return token, user
