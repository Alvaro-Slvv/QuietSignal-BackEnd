from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from ...database.base import Base


class JournalEntry(Base):
    __tablename__ = "journal_entries"

    id = Column(Integer, primary_key=True, index=True)
    journal_id = Column(Integer, ForeignKey("journals.id", ondelete="CASCADE"), nullable=False)

    # list of paragraphs stored as JSON string
    texts = Column(Text, nullable=False, default="[]")

    # last analysis
    label = Column(String(32), nullable=True)
    probabilities = Column(String(2048), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
