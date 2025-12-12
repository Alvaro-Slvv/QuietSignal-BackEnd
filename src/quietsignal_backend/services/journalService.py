import json
from typing import Callable, Dict, Tuple, Optional
from sqlalchemy.orm import Session

from ..models.dao.journalDAO import JournalDAO
from ..models.dao.journalEntryDAO import JournalEntryDAO
from ..models.entities.journalEntryEntity import JournalEntry


class JournalService:

    @staticmethod
    def create_journal(db: Session, user_id: int, title: str):
        return JournalDAO.create(db, user_id=user_id, title=title)

    @staticmethod
    def create_entry(db: Session, journal_id: int):
        return JournalEntryDAO.create(db, journal_id)

    @staticmethod
    def append_and_analyze(
        db: Session,
        entry_id: int,
        paragraph: str,
        analyzer: Callable[[list[str]], Tuple[str, Dict[str, float]]]
    ) -> Optional[JournalEntry]:

        entry = JournalEntryDAO.get_by_id(db, entry_id)
        if not entry:
            return None

        entry = JournalEntryDAO.append_paragraph(db, entry, paragraph)

        texts = json.loads(entry.texts)

        # Weighted analysis
        label, probs = analyzer(texts)

        updated = JournalEntryDAO.update_analysis(
            db,
            entry,
            label,
            json.dumps(probs)
        )

        return updated

    @staticmethod
    def get_entry(db: Session, entry_id: int):
        return JournalEntryDAO.get_by_id(db, entry_id)

    @staticmethod
    def list_entries(db: Session, journal_id: int):
        return JournalEntryDAO.list_for_journal(db, journal_id)
