import joblib
from pathlib import Path

MODEL_PATH = Path(__file__).resolve().parent.parent.parent.parent / "models" / "Model.joblib"
model = joblib.load(MODEL_PATH)

def predict_emotion(text: str) -> dict:
    # pipeline.predict_proba returns shape: (1, n_classes)
    probs = model.predict_proba([text])[0]

    return {
        str(i): float(p)
        for i, p in enumerate(probs)
    }
