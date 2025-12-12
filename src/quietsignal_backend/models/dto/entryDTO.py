from pydantic import BaseModel
from typing import List, Dict


class EntryCreateResponseDTO(BaseModel):
    entry_id: int


class EntryAppendBatchDTO(BaseModel):
    paragraphs: List[str]


class EntryDTO(BaseModel):
    entry_id: int
    texts: List[str]
    label: str
    probabilities: Dict[str, float]
    created_at: str
