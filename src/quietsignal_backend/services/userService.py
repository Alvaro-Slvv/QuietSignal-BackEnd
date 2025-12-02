# src/quietsignal_backend/services/user_service.py
from sqlalchemy.orm import Session
from ..models.dao.userDAO import UserDAO
from ..models.dto.userDTO import UserCreateDTO, UserOutDTO
from ..utils.security import hash_password


class UserService:
    @staticmethod
    def create_user(db: Session, data: UserCreateDTO):
        hashed = hash_password(data.password)
        user = UserDAO.create(db, username=data.username, hashed_password=hashed, email=data.email)
        return UserOutDTO.model_validate(user)
