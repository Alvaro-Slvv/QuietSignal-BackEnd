from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from ...database.base import Base
from sqlalchemy.sql import func

class Journal(Base):
    __tablename__ = "journals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(200), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
