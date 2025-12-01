from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..models import AnalyzeRequest, AnalyzeResponse, User
from ..sentiment import sentiment_model
from .auth_routes import get_current_user
from ..database import get_db

router = APIRouter(prefix="/analyze", tags=["analysis"])


@router.post("/", response_model=AnalyzeResponse)
def analyze_text(
    request: AnalyzeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    label = sentiment_model.predict(request.text)
    probs = sentiment_model.predict_proba(request.text)

    return AnalyzeResponse(
        label=label,
        probabilities=probs,
    )
