import pytest
from fastapi.testclient import TestClient
from y2h_ppi.api.main import app

client = TestClient(app)

def test_api_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_api_predict_endpoint():
    payload = {"protein_a": "YFL039C", "protein_b": "YAL001C"}
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "calibrated_probability" in data
    assert "documentation" in data

def test_api_known_interactors_endpoint():
    response = client.get("/protein/YFL039C/known_interactors")
    assert response.status_code == 200
    data = response.json()
    assert "query_gene" in data
    assert "nodes" in data
