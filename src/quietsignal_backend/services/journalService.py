import json
from sqlalchemy.orm import Session

from ..models.dao.journalEntryDAO import JournalEntryDAO
from ..models.dao.journalDAO import JournalDAO


class JournalService:

    @staticmethod
    def create_journal(db: Session, user_id: int, title: str):
        return JournalDAO.create(db, user_id, title)

    @staticmethod
    def create_entry(db: Session, journal_id: int):
        return JournalEntryDAO.create(db, journal_id)

    @staticmethod
    def append_and_analyze(db: Session, entry_id: int, paragraph: str, analyzer_callable):
        entry = JournalEntryDAO.get_by_id(db, entry_id)
        if not entry:
            return None

        JournalEntryDAO.append_paragraphs(db, entry, [paragraph])

        texts = json.loads(entry.texts)
        label, probs = analyzer_callable(texts)
        JournalEntryDAO.update_emotion(db, entry, label, probs)

        return entry

    @staticmethod
    def append_batch_and_analyze(db: Session, entry_id: int, paragraphs: list[str], analyzer_callable):
        entry = JournalEntryDAO.get_by_id(db, entry_id)
        if not entry:
            return None

        JournalEntryDAO.append_paragraphs(db, entry, paragraphs)

        texts = json.loads(entry.texts)
        label, probs = analyzer_callable(texts)
        JournalEntryDAO.update_emotion(db, entry, label, probs)

        return entry

    @staticmethod
    def get_entry(db: Session, entry_id: int):
        return JournalEntryDAO.get_by_id(db, entry_id)

    @staticmethod
    def list_entries(db: Session, journal_id: int):
        return JournalEntryDAO.list_by_journal(db, journal_id)
    
    @staticmethod
    def list_user_journals(db: Session, user_id: int):
        return JournalDAO.get_by_user(db, user_id)
