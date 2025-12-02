from pydantic import BaseModel, Field
from typing import Dict


class AnalyzeRequestDTO(BaseModel):
    text: str = Field(...)

    model_config = {"extra": "forbid"}


class AnalyzeResponseDTO(BaseModel):
    label: str
    probabilities: Dict[str, float]

    model_config = {"from_attributes": True, "extra": "forbid"}
