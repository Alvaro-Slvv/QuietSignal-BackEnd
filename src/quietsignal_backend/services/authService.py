from sqlalchemy.orm import Session
from ..models.dao.userDAO import UserDAO
from ..utils.security import verify_password, hash_password
from ..utils.jwtHandler import create_access_token


class AuthService:
    @staticmethod
    def register(db, dto):
        # duplicate checks omitted
        hashed = hash_password(dto.password)
        return UserDAO.create(db, dto, hashed)
    
    @staticmethod
    def authenticate(db, username, password):
        user = UserDAO.get_by_username(db, username)
        if not user or not verify_password(password, user.hashed_password):
            return None
        token = create_access_token({"sub": user.username, "role": user.role})
        return token, user
