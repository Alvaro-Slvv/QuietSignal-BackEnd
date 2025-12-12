# src/quietsignal_backend/models/dao/journalEntryDAO.py

from sqlalchemy.orm import Session
from ..entities.journalEntryEntity import JournalEntry
from typing import Optional, List
import json


class JournalEntryDAO:
    @staticmethod
    def create(db: Session, journal_id: int):
        entry = JournalEntry(
            journal_id=journal_id,
            texts="[]",
            label=None,
            probabilities=None
        )
        db.add(entry)
        db.commit()
        db.refresh(entry)
        return entry

    @staticmethod
    def get_by_id(db: Session, entry_id: int) -> Optional[JournalEntry]:
        return db.query(JournalEntry).filter(JournalEntry.id == entry_id).first()

    @staticmethod
    def append_paragraph(db: Session, entry: JournalEntry, paragraph: str) -> JournalEntry:
        texts = json.loads(entry.texts)
        texts.append(paragraph)
        entry.texts = json.dumps(texts)
        db.add(entry)
        db.commit()
        db.refresh(entry)
        return entry

    @staticmethod
    def update_analysis(db: Session, entry: JournalEntry, label: str, probabilities: str) -> JournalEntry:
        entry.label = label
        entry.probabilities = probabilities
        db.add(entry)
        db.commit()
        db.refresh(entry)
        return entry

    @staticmethod
    def list_for_journal(db: Session, journal_id: int):
        return db.query(JournalEntry).filter(JournalEntry.journal_id == journal_id).all()

    @staticmethod
    def list_all(db: Session) -> List[JournalEntry]:
        """Return all journal entries (admin use)."""
        return db.query(JournalEntry).all()
