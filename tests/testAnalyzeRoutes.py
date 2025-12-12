from fastapi.testclient import TestClient
from src.quietsignal_backend.main import app
from unittest.mock import patch

client = TestClient(app)

def fake_predict(text):
    return {"0": 0.05, "1": 0.85, "2": 0.10}

@patch("src.quietsignal_backend.ml.modelLoader.predict_emotion", side_effect=fake_predict)
def test_analyze_route_returns_apiresponse(mock_predict):
    resp = client.post("/analyze/", json={"text": "it's ok"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["code"] == 200
    assert body["message"] == "Analysis completed successfully"
    assert body["data"]["label"] == "neutral"
    assert "probabilities" in body["data"]
