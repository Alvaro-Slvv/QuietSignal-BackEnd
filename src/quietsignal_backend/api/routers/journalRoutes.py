# src/quietsignal_backend/api/routers/journalRoutes.py

from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
import json
from typing import Any

from ...common.apiResponse import APIResponse
from ...database.base import get_db
from ...api.deps import get_current_user

from ...services.journalService import JournalService
from ...models.dao.journalDAO import JournalDAO
from ...models.dto.entryDTO import EntryDTO, EntryCreateResponseDTO, EntryAppendBatchDTO

from ...ml.modelLoader import predict_emotion

router = APIRouter(prefix="/journals", tags=["Journals"])

EMOTION_LABELS = ["negative", "neutral", "positive"]

DEFAULT_PROBS = {
    "negative": 0.33,
    "neutral": 0.34,
    "positive": 0.33
}


def _ensure_texts_list(raw_texts: Any) -> list[str]:
    """
    Accept either:
      - a Python list of strings
      - a JSON string representing a list
      - None -> returns []
    """
    if raw_texts is None:
        return []
    if isinstance(raw_texts, list):
        return raw_texts
    if isinstance(raw_texts, str):
        try:
            parsed = json.loads(raw_texts)
            if isinstance(parsed, list):
                return parsed
            # fallback: wrap string
            return [raw_texts]
        except Exception:
            # not JSON, treat as single paragraph string
            return [raw_texts]
    # any other type: coerce to list of str
    return [str(raw_texts)]


def _ensure_probs_dict(raw_probs: Any) -> dict:
    """
    Accept either:
      - a Python dict {label: float}
      - a JSON string
      - None -> returns DEFAULT_PROBS
    """
    if raw_probs is None:
        return DEFAULT_PROBS.copy()
    if isinstance(raw_probs, dict):
        # ensure float values
        return {k: float(v) for k, v in raw_probs.items()}
    if isinstance(raw_probs, str):
        try:
            parsed = json.loads(raw_probs)
            if isinstance(parsed, dict):
                return {k: float(v) for k, v in parsed.items()}
            # fallback
            return DEFAULT_PROBS.copy()
        except Exception:
            return DEFAULT_PROBS.copy()
    # fallback for other types
    try:
        return dict(raw_probs)
    except Exception:
        return DEFAULT_PROBS.copy()


def analyzer_callable(texts: list[str]):
    """
    Weighted averaging analyzer: length-weight + recency-weight
    Returns (label: str, probabilities: dict[str,float])
    """
    p = 1.0
    gamma = 0.2

    N = len(texts)
    if N == 0:
        return "neutral", DEFAULT_PROBS.copy()

    paragraph_probs = []
    lengths = []

    for t in texts:
        raw = predict_emotion(t)
        # model returns {"0":..,"1":..,"2":..} or similar numeric keys
        try:
            mapped = {EMOTION_LABELS[int(i)]: float(prob) for i, prob in raw.items()}
        except (IndexError, ValueError, KeyError):
            # fallback if model output format is unexpected
            mapped = DEFAULT_PROBS.copy()
        paragraph_probs.append(mapped)
        lengths.append(max(1, len(t)))

    # compute weights
    if N == 1:
        weights = [1.0]
    else:
        weights = []
        for idx in range(N):
            length_component = lengths[idx] ** p
            rec_norm = idx / (N - 1)
            recency_component = 1 + gamma * rec_norm
            raw_w = length_component * recency_component
            weights.append(raw_w)
        total = sum(weights) or 1.0
        weights = [w / total for w in weights]

    final = {"negative": 0.0, "neutral": 0.0, "positive": 0.0}
    for w, probs in zip(weights, paragraph_probs):
        for k in final.keys():
            final[k] += probs.get(k, 0.0) * w

    final_label = max(final.keys(), key=lambda k: final[k])
    return final_label, final


@router.get("/", response_model=APIResponse)
def list_user_journals(
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    journals = JournalService.list_user_journals(db, user.id)

    data = [
        {
            "journal_id": j.id,
            "title": j.title,
            "created_at": j.created_at.isoformat(),
        }
        for j in journals
    ]

    return APIResponse.success(data=data, message="User journals listed")


# -----------------------------
# Create journal
# -----------------------------
@router.post("/", response_model=APIResponse, status_code=201)
def create_journal(
    title: str,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        journal = JournalService.create_journal(db, user.id, title)
        return APIResponse.success(
            data={"journal_id": journal.id, "title": journal.title},
            message="Journal created",
            code=201,
        )
    except Exception as e:
        return APIResponse.error(message=f"Create journal failed: {e}", code=500)
# -----------------------------
# Create Entry
# -----------------------------
@router.post("/{journal_id}/entries", response_model=APIResponse)
def create_entry(
    journal_id: int,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    journal = JournalDAO.get_by_id(db, journal_id)
    if not journal:
        raise HTTPException(status_code=404, detail="Journal not found")
    if journal.user_id != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    entry = JournalService.create_entry(db, journal_id)
    dto = EntryCreateResponseDTO(entry_id=entry.id)
    return APIResponse.success(data=dto.model_dump(), message="Entry created")


# -----------------------------
# Append a single paragraph
# -----------------------------
@router.post("/{journal_id}/entries/{entry_id}/append", response_model=APIResponse)
def append_paragraph(
    journal_id: int,
    entry_id: int,
    paragraph: str = Body(..., embed=True),
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    journal = JournalDAO.get_by_id(db, journal_id)
    if not journal:
        raise HTTPException(status_code=404, detail="Journal not found")
    if journal.user_id != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    updated = JournalService.append_and_analyze(db, entry_id, paragraph, analyzer_callable)
    if not updated:
        raise HTTPException(status_code=404, detail="Entry not found")
    if updated.journal_id != journal_id:
        raise HTTPException(status_code=400, detail="Entry does not belong to this journal")

    texts = _ensure_texts_list(updated.texts)
    probs = _ensure_probs_dict(updated.probabilities)

    dto = EntryDTO(
        entry_id=updated.id,
        texts=texts,
        label=updated.label or "neutral",
        probabilities=probs,
        created_at=updated.created_at.isoformat(),
    )

    return APIResponse.success(data=dto.model_dump(), message="Paragraph appended")


# -----------------------------
# Batch append
# -----------------------------
@router.post("/{journal_id}/entries/{entry_id}/append-batch", response_model=APIResponse)
def append_batch(
    journal_id: int,
    entry_id: int,
    body: EntryAppendBatchDTO,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    journal = JournalDAO.get_by_id(db, journal_id)
    if not journal:
        raise HTTPException(status_code=404, detail="Journal not found")
    if journal.user_id != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    updated = JournalService.append_batch_and_analyze(db, entry_id, body.paragraphs, analyzer_callable)
    if not updated:
        raise HTTPException(status_code=404, detail="Entry not found")
    if updated.journal_id != journal_id:
        raise HTTPException(status_code=400, detail="Entry does not belong to this journal")

    texts = _ensure_texts_list(updated.texts)
    probs = _ensure_probs_dict(updated.probabilities)

    dto = EntryDTO(
        entry_id=updated.id,
        texts=texts,
        label=updated.label or "neutral",
        probabilities=probs,
        created_at=updated.created_at.isoformat(),
    )

    return APIResponse.success(data=dto.model_dump(), message="Batch appended & analyzed")


# -----------------------------
# Get Entry
# -----------------------------
@router.get("/{journal_id}/entries/{entry_id}", response_model=APIResponse)
def get_entry(
    journal_id: int,
    entry_id: int,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    journal = JournalDAO.get_by_id(db, journal_id)
    if not journal:
        raise HTTPException(status_code=404, detail="Journal not found")
    if journal.user_id != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    entry = JournalService.get_entry(db, entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    if entry.journal_id != journal_id:
        raise HTTPException(status_code=400, detail="Entry mismatch")

    texts = _ensure_texts_list(entry.texts)
    probs = _ensure_probs_dict(entry.probabilities)

    dto = EntryDTO(
        entry_id=entry.id,
        texts=texts,
        label=entry.label or "neutral",
        probabilities=probs,
        created_at=entry.created_at.isoformat(),
    )

    return APIResponse.success(data=dto.model_dump())


# -----------------------------
# List all entries in journal
# -----------------------------
@router.get("/{journal_id}/entries", response_model=APIResponse)
def list_entries(
    journal_id: int,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    journal = JournalDAO.get_by_id(db, journal_id)
    if not journal:
        raise HTTPException(status_code=404, detail="Journal not found")
    if journal.user_id != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    entries = JournalService.list_entries(db, journal_id)

    out = []
    for e in entries:
        texts = _ensure_texts_list(e.texts)
        probs = _ensure_probs_dict(e.probabilities)

        dto = EntryDTO(
            entry_id=e.id,
            texts=texts,
            label=e.label or "neutral",
            probabilities=probs,
            created_at=e.created_at.isoformat(),
        )
        out.append(dto.model_dump())

    return APIResponse.success(data=out, message="Entries listed")

@router.get("/me", response_model=APIResponse)
def get_my_journal(
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    journal = JournalService.get_user_journal(db, user.id)
    if not journal:
        raise HTTPException(status_code=404, detail="Journal not found")

    return APIResponse.success(
        data={
            "journal_id": journal.id,
            "title": journal.title,
            "created_at": journal.created_at.isoformat(),
        }
    )