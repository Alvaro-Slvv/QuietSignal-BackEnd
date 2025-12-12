from pydantic import BaseModel, Field
from typing import List, Dict, Optional


class EntryCreateResponseDTO(BaseModel):
    entry_id: int = Field(..., description="ID of the newly created entry")


class EntryDTO(BaseModel):
    entry_id: int
    texts: List[str]
    label: Optional[str] = None
    probabilities: Optional[Dict[str, float]] = None
    created_at: str
