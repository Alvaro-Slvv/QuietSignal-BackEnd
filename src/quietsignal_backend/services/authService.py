# src/quietsignal_backend/services/auth_service.py
from sqlalchemy.orm import Session
from ..models.dao.userDAO import UserDAO
from ..utils.security import hash_password, verify_password
from ..utils.jwtHandler import create_access_token


class AuthService:
    @staticmethod
    def register_user(db: Session, name: str, username: str, password: str, email: str = None):
        existing = UserDAO.get_by_username(db, username)
        if existing:
            raise ValueError("username_taken")
        hashed = hash_password(password)
        user = UserDAO.create(db, name=name, username=username, hashed_password=hashed, email=email)
        token = create_access_token({"sub": user.username})
        return token, user

    @staticmethod
    def authenticate(db: Session, username: str, password: str):
        user = UserDAO.get_by_username(db, username)
        if not user or not verify_password(password, user.hashed_password):
            return None
        token = create_access_token({"sub": user.username})
        return token, user
