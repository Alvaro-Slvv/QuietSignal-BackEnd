CLASS_LABELS = {
    "0": "negative",
    "1": "neutral",
    "2": "positive",
}

def index_to_label(idx: str) -> str:
    return CLASS_LABELS.get(idx, idx)
