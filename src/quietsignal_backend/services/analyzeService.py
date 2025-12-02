# src/quietsignal_backend/services/analyze_service.py
import json
from ..ml.modelLoader import predict_emotion
from ..sentiment import index_to_label


class AnalyzeService:
    @staticmethod
    def analyze_text(text: str):
        probs = predict_emotion(text)  # dict[str, float]
        # pick highest
        best_idx = max(probs, key=probs.get)
        label = index_to_label(best_idx)
        # keep probs as JSON-safe mapping string->float
        return label, probs
