import re

def simple_cleanup(text: str) -> str:
    txt = text.strip().lower()
    txt = re.sub(r"\s+", " ", txt)
    return txt
