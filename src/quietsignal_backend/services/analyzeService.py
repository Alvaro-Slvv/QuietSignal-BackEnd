"""
AnalyzeService — uses the ML model (joblib) to predict label + probabilities.

This file replaces the previous fake analyzer logic and:
- imports the ml loader implementation at src/quietsignal_backend/ml/modelLoader.py
- uses predict_emotion(text) -> dict[str, float] where keys are "0","1","2"
- normalizes labels to "positive" | "neutral" | "negative"
- returns AnalyzeResponseDTO (matches src/quietsignal_backend/models/dto/analyzeDTO.py)
"""

from typing import Dict, Tuple
from ..ml.modelLoader import predict_emotion  # per instruction: import ml version
from ..models.dto.analyzeDTO import AnalyzeResponseDTO

# Mapping of model class indices -> canonical labels
_INDEX_TO_LABEL = {
    "0": "negative",
    "1": "neutral",
    "2": "positive",
}


class AnalyzeService:
    @staticmethod
    def _probs_to_label(probs: Dict[str, float]) -> Tuple[str, Dict[str, float]]:
        """
        Given model output probs (keys are indices '0','1','2'), return canonical label
        and the probabilities mapped to canonical keys.
        """
        if not probs:
            raise ValueError("Empty probabilities from model")

        # best_idx is the key (string) with highest probability
        best_idx = max(probs, key=probs.get)
        label = _INDEX_TO_LABEL.get(best_idx, str(best_idx))

        # Map probabilities to canonical keys (negative/neutral/positive)
        mapped_probs = {
            _INDEX_TO_LABEL.get(k, k): float(v) for k, v in probs.items()
        }

        # Ensure all canonical keys exist (fill 0.0 if missing)
        for canonical in ("negative", "neutral", "positive"):
            mapped_probs.setdefault(canonical, 0.0)

        return label, mapped_probs

    @staticmethod
    def analyze_text(text: str) -> AnalyzeResponseDTO:
        """
        Analyze single text and return AnalyzeResponseDTO
        """
        probs = predict_emotion(text)  # returns dict[str, float] where keys '0','1','2'
        label, mapped_probs = AnalyzeService._probs_to_label(probs)
        # Build and return DTO
        return AnalyzeResponseDTO(label=label, probabilities=mapped_probs)

    @staticmethod
    def analyze(request):
        """
        Keep the existing service method signature used by routes:
        request is expected to be an AnalyzeRequestDTO (has .text)
        """
        text = request.text
        return AnalyzeService.analyze_text(text)
