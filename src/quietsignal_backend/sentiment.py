import os
from typing import Dict

import joblib
from sklearn.pipeline import Pipeline

MODEL_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),  # up to repo root
    "models",
    "sentiment_mlp.joblib",
)


class SentimentModel:
    def __init__(self, model_path: str = MODEL_PATH):
        self.pipeline: Pipeline = joblib.load(model_path)
        self._labels = list(self.pipeline.classes_)

    @property
    def labels(self):
        return self._labels

    def predict(self, text: str) -> str:
        pred = self.pipeline.predict([text])[0]
        return str(pred)

    def predict_proba(self, text: str) -> Dict[str, float]:
        probs = self.pipeline.predict_proba([text])[0]
        return {label: float(round(p, 4)) for label, p in zip(self._labels, probs)}


sentiment_model = SentimentModel()
