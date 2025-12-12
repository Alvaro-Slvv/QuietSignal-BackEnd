# src/quietsignal_backend/api/routers/adminRoutes.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import json
from typing import Dict

from ...common.apiResponse import APIResponse
from ...database.base import get_db
from ...api.deps import get_current_user

from ...models.dao.journalEntryDAO import JournalEntryDAO
from ...models.dao.journalDAO import JournalDAO

from ...ml.modelLoader import predict_emotion

router = APIRouter(prefix="/admin", tags=["Admin"])

# same label mapping used elsewhere
EMOTION_LABELS = ["negative", "neutral", "positive"]

DEFAULT_P = 1.0
DEFAULT_GAMMA = 0.2


def _analyze_texts_weighted(
    texts: list[str],
    p: float = DEFAULT_P,
    gamma: float = DEFAULT_GAMMA
) -> tuple[str, dict[str, float]]:
    """
    Weighted averaging of per-paragraph predictions.
    Reimplementation here to avoid circular imports.
    """
    if not texts:
        return "neutral", {"negative": 0.33, "neutral": 0.34, "positive": 0.33}

    # get per-paragraph predictions
    paragraph_probs = []
    lengths = []
    for t in texts:
        raw = predict_emotion(t)  # returns {"0": .., "1": .., "2": ..}
        mapped = {EMOTION_LABELS[int(i)]: float(prob) for i, prob in raw.items()}
        paragraph_probs.append(mapped)
        lengths.append(max(1, len(t)))

    N = len(texts)
    weights = []
    if N == 1:
        weights = [1.0]
    else:
        for idx in range(N):
            length_component = lengths[idx] ** p
            recency_norm = idx / (N - 1)
            recency_component = 1 + gamma * recency_norm
            raw_w = length_component * recency_component
            weights.append(raw_w)
        total = sum(weights) or 1.0
        weights = [w / total for w in weights]

    final = {"negative": 0.0, "neutral": 0.0, "positive": 0.0}
    for w, probs in zip(weights, paragraph_probs):
        for k in final.keys():
            final[k] += probs[k] * w

    final_label = max(final.keys(), key=lambda k: final[k])
    return final_label, final


def _is_admin(user) -> bool:
    """
    Check whether provided user is admin.
    Assumes user has attribute `role` with value 'admin' for admin users.
    """
    if not user:
        return False
    role = getattr(user, "role", None)
    if role is None:
        # attempt alternative attribute
        return getattr(user, "is_admin", False)
    return str(role).lower() == "admin"


@router.post("/recalculate_entries", response_model=APIResponse)
def recalculate_all_entries(user = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Admin endpoint: re-run analysis for ALL JournalEntry rows and update DB.
    """
    if not _is_admin(user):
        raise HTTPException(status_code=403, detail="Admin privileges required")

    entries = JournalEntryDAO.list_all(db)
    updated_count = 0
    errors = []

    for e in entries:
        try:
            texts = json.loads(e.texts) if e.texts else []
            label, probs = _analyze_texts_weighted(texts)
            JournalEntryDAO.update_analysis(db, e, label, json.dumps(probs))
            updated_count += 1
        except Exception as ex:
            errors.append({"entry_id": getattr(e, "id", None), "error": str(ex)})

    return APIResponse.success(
        data={"updated": updated_count, "errors": errors},
        message=f"Recalculated {updated_count} entries"
    )
