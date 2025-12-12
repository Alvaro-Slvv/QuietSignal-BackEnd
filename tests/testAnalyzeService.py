import pytest
from unittest.mock import patch
from src.quietsignal_backend.services.analyzeService import AnalyzeService

def fake_predict_emotion(text):
    # deterministic fake probabilities for testing
    return {"0": 0.1, "1": 0.2, "2": 0.7}

@patch("src.quietsignal_backend.ml.modelLoader.predict_emotion", side_effect=fake_predict_emotion)
def test_analyze_text_returns_expected(mock_predict):
    dto = AnalyzeService.analyze_text("I like this")
    assert dto.label == "positive"
    assert isinstance(dto.probabilities, dict)
    assert dto.probabilities["positive"] == pytest.approx(0.7)
