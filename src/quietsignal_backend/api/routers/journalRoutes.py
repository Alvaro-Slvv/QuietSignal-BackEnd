from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import json

from ...common.apiResponse import APIResponse
from ...database.base import get_db
from ...api.deps import get_current_user

from ...services.journalService import JournalService
from ...models.dao.journalDAO import JournalDAO
from ...models.dto.entryDTO import EntryCreateResponseDTO, EntryDTO

from ...ml.modelLoader import predict_emotion

router = APIRouter(prefix="/journals", tags=["Journals"])

EMOTION_LABELS = ["negative", "neutral", "positive"]

DEFAULT_PROBS = {
    "negative": 0.33,
    "neutral": 0.34,
    "positive": 0.33
}


def analyzer_callable(texts: list[str]):
    """
    Weighted averaging model:
    - Predict per paragraph
    - Weight by length
    - Weight newest paragraphs slightly more (recency weighting)
    """

    p = 1.0        # length exponent
    gamma = 0.2    # recency gain (0 to 1)

    N = len(texts)
    if N == 0:
        return "neutral", DEFAULT_PROBS.copy()

    # Per-paragraph predictions
    paragraph_probs = []
    lengths = []

    for t in texts:
        raw = predict_emotion(t)
        mapped = {EMOTION_LABELS[int(i)]: float(p) for i, p in raw.items()}
        paragraph_probs.append(mapped)
        lengths.append(max(1, len(t)))  # avoid zero division

    # Compute weights
    weights = []
    if N == 1:
        weights = [1.0]
    else:
        for idx in range(N):
            length_component = lengths[idx] ** p
            rec_norm = idx / (N - 1)             # 0 oldest → 1 newest
            recency_component = 1 + gamma * rec_norm
            raw_w = length_component * recency_component
            weights.append(raw_w)

        total = sum(weights)
        weights = [w / total for w in weights]

    # Weighted probability aggregation
    final = {"negative": 0.0, "neutral": 0.0, "positive": 0.0}

    for w, probs in zip(weights, paragraph_probs):
        for k in final.keys():
            final[k] += probs[k] * w

    final_label = max(final.keys(), key=lambda k: final[k])
    return final_label, final


@router.post("/", response_model=APIResponse)
def create_journal(
    title: str,
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        journal = JournalService.create_journal(db, user.id, title)
        return APIResponse.success(
            data={"journal_id": journal.id, "title": journal.title},
            message="Journal created",
            code=201
        )
    except Exception as e:
        return APIResponse.error(message=f"Create journal failed: {e}", code=500)


@router.post("/{journal_id}/entries", response_model=APIResponse)
def create_entry(
    journal_id: int,
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    journal = JournalDAO.get_by_id(db, journal_id)
    if not journal:
        raise HTTPException(status_code=404, detail="Journal not found")

    if journal.user_id != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    entry = JournalService.create_entry(db, journal_id)
    dto = EntryCreateResponseDTO(entry_id=entry.id)
    return APIResponse.success(data=dto.model_dump(), message="Entry created")


@router.post("/{journal_id}/entries/{entry_id}/append", response_model=APIResponse)
def append_paragraph(
    journal_id: int,
    entry_id: int,
    paragraph: str,
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    journal = JournalDAO.get_by_id(db, journal_id)
    if not journal:
        raise HTTPException(status_code=404, detail="Journal not found")

    if journal.user_id != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    updated = JournalService.append_and_analyze(db, entry_id, paragraph, analyzer_callable)
    if not updated:
        raise HTTPException(status_code=404, detail="Entry not found")

    dto = EntryDTO(
        entry_id=updated.id,
        texts=json.loads(updated.texts),
        label=updated.label if updated.label else "neutral",
        probabilities=json.loads(updated.probabilities) if updated.probabilities else DEFAULT_PROBS,
        created_at=updated.created_at.isoformat()
    )

    return APIResponse.success(
        data=dto.model_dump(),
        message="Paragraph appended and analyzed"
    )


@router.get("/{journal_id}/entries/{entry_id}", response_model=APIResponse)
def get_entry(
    journal_id: int,
    entry_id: int,
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    entry = JournalService.get_entry(db, entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")

    dto = EntryDTO(
        entry_id=entry.id,
        texts=json.loads(entry.texts),
        label=entry.label if entry.label else "neutral",
        probabilities=json.loads(entry.probabilities) if entry.probabilities else DEFAULT_PROBS,
        created_at=entry.created_at.isoformat()
    )

    return APIResponse.success(data=dto.model_dump())


@router.get("/{journal_id}/entries", response_model=APIResponse)
def list_entries(
    journal_id: int,
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    journal = JournalDAO.get_by_id(db, journal_id)
    if not journal:
        raise HTTPException(status_code=404, detail="Journal not found")

    if journal.user_id != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    entries = JournalService.list_entries(db, journal_id)
    out = []

    for e in entries:
        dto = EntryDTO(
            entry_id=e.id,
            texts=json.loads(e.texts),
            label=e.label if e.label else "neutral",
            probabilities=json.loads(e.probabilities) if e.probabilities else DEFAULT_PROBS,
            created_at=e.created_at.isoformat()
        )
        out.append(dto.model_dump())

    return APIResponse.success(data=out, message="Entries listed")
