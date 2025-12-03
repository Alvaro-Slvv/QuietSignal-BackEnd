from sqlalchemy.orm import Session
from ..entities.userEntity import User
from ...models.dto.userDTO import UserCreateDTO


class UserDAO:
    @staticmethod
    def get_by_username(db: Session, username: str):
        return db.query(User).filter(User.username == username).first()

    @staticmethod
    def get_by_id(db: Session, user_id: int):
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def create(db: Session, dto: UserCreateDTO, hashed_password: str):
        user = User(
            name=dto.name,
            username=dto.username,
            hashed_password=hashed_password,
            email=dto.email
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def get_by_email(db: Session, email: str):
        return db.query(User).filter(User.email == email).first()