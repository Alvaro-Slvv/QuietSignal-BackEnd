from sqlalchemy.orm import Session
from ..entities.journalEntryEntity import JournalEntry
import json


class JournalEntryDAO:

    @staticmethod
    def create(db: Session, journal_id: int):
        entry = JournalEntry(journal_id=journal_id, texts="[]", label="", probabilities="")
        db.add(entry)
        db.commit()
        db.refresh(entry)
        return entry

    @staticmethod
    def get_by_id(db: Session, entry_id: int):
        return db.query(JournalEntry).filter(JournalEntry.id == entry_id).first()

    @staticmethod
    def append_paragraphs(db: Session, entry: JournalEntry, paragraphs: list[str]):
        """
        Appends several paragraphs to an entry.
        """
        existing = json.loads(entry.texts) if entry.texts else []
        updated = existing + paragraphs

        entry.texts = json.dumps(updated)
        db.commit()
        db.refresh(entry)
        return entry

    @staticmethod
    def update_emotion(db: Session, entry: JournalEntry, label: str, probs: dict):
        entry.label = label
        entry.probabilities = json.dumps(probs)
        db.commit()
        db.refresh(entry)
        return entry

    @staticmethod
    def list_by_journal(db: Session, journal_id: int):
        return (
            db.query(JournalEntry)
            .filter(JournalEntry.journal_id == journal_id)
            .order_by(JournalEntry.created_at.asc())
            .all()
        )

    @staticmethod
    def list_all(db: Session):
        return db.query(JournalEntry).all()

    @staticmethod
    def update_analysis(db: Session, entry: JournalEntry, label: str, probs_json: str):
        entry.label = label
        entry.probabilities = probs_json
        db.commit()
        db.refresh(entry)
        return entry