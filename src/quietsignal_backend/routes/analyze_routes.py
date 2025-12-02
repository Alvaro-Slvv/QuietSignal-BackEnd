from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import AnalyzeRequest, AnalyzeResponse
from ..ml.ml import predict_emotion  # <-- import ML

router = APIRouter(prefix="/analyze", tags=["analyze"])

@router.post("/", response_model=AnalyzeResponse)
def analyze_text(request: AnalyzeRequest, db: Session = Depends(get_db)):

    text = request.text

    clean_probs = predict_emotion(text)

    label = max(clean_probs, key=clean_probs.get)

    return AnalyzeResponse(
        label=label,
        probabilities=clean_probs,
    )
