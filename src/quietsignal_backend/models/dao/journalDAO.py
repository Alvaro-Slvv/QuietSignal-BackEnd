from sqlalchemy.orm import Session
from ...models.entities.journalEntity import Journal
from typing import Optional, List


class JournalDAO:
    @staticmethod
    def create(db: Session, user_id: int, title: str) -> Journal:
        journal = Journal(user_id=user_id, title=title)
        db.add(journal)
        db.commit()
        db.refresh(journal)
        return journal

    @staticmethod
    def get_by_id(db: Session, journal_id: int) -> Optional[Journal]:
        return db.query(Journal).filter(Journal.id == journal_id).first()

    @staticmethod
    def list_for_user(db: Session, user_id: int) -> List[Journal]:
        return db.query(Journal).filter(Journal.user_id == user_id).all()
    @staticmethod
    def get_by_user(db: Session, user_id: int):
        return db.query(Journal).filter(Journal.user_id == user_id).order_by(Journal.created_at.desc()).all()

