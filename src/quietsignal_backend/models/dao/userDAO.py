from sqlalchemy.orm import Session
from ..entities.userEntity import User


class UserDAO:
    @staticmethod
    def get_by_username(db: Session, username: str):
        return db.query(User).filter(User.username == username).first()

    @staticmethod
    def get_by_id(db: Session, user_id: int):
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def create(db: Session, name :str, username: str, hashed_password: str, email: str = None) -> User:
        user = User(name= name, username=username, hashed_password=hashed_password, email=email)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
