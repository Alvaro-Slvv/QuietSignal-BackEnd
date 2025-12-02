import joblib
from pathlib import Path
from fastapi import HTTPException

MODEL_PATH = Path(__file__).resolve().parents[3] / "mlmodel" / "Model.joblib"

try:
    MODEL = joblib.load(MODEL_PATH)
except Exception:
    MODEL = None


def predict_emotion(text: str):
    """
    Returns dict[str,float] where keys are class indices as strings.
    Raises HTTPException if model missing.
    """
    if MODEL is None:
        raise HTTPException(status_code=500, detail="Model not found. Place Model.joblib in models/ folder.")

    probs = MODEL.predict_proba([text])[0]
    return {str(i): float(p) for i, p in enumerate(probs)}
