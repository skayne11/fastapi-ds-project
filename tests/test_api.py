"""
Tests unitaires pour l'API FastAPI Data Science
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root():
    """Test endpoint racine"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data


def test_health():
    """Test health check"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_generate_dataset_clean():
    """Test génération dataset clean"""
    response = client.post(
        "/dataset/generate",
        json={
            "phase": "clean",
            "seed": 42,
            "n": 100
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "meta" in data
    assert "result" in data
    assert data["meta"]["dataset_id"] == "clean_42_100"


def test_generate_dataset_eda():
    """Test génération dataset eda"""
    response = client.post(
        "/dataset/generate",
        json={
            "phase": "eda",
            "seed": 123,
            "n": 200
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["meta"]["dataset_id"] == "eda_123_200"


def test_clean_report():
    """Test rapport qualité"""
    # D'abord générer un dataset
    client.post(
        "/dataset/generate",
        json={"phase": "clean", "seed": 42, "n": 100}
    )
    
    # Ensuite obtenir le rapport
    response = client.get("/clean/report/clean_42_100")
    assert response.status_code == 200
    data = response.json()
    assert "report" in data
    assert "missing_values" in data["report"]
    assert "duplicates" in data["report"]


def test_clean_fit_transform():
    """Test pipeline de nettoyage complet"""
    # Générer dataset
    client.post(
        "/dataset/generate",
        json={"phase": "clean", "seed": 42, "n": 100}
    )
    
    # Fitter le pipeline
    fit_response = client.post(
        "/clean/fit",
        json={
            "meta": {"dataset_id": "clean_42_100"},
            "params": {
                "impute_strategy": "mean",
                "outlier_strategy": "clip",
                "categorical_strategy": "one_hot"
            }
        }
    )
    assert fit_response.status_code == 200
    cleaner_id = fit_response.json()["result"]["cleaner_id"]
    
    # Transformer
    transform_response = client.post(
        "/clean/transform",
        json={
            "meta": {"dataset_id": "clean_42_100"},
            "params": {"cleaner_id": cleaner_id}
        }
    )
    assert transform_response.status_code == 200
    assert "processed_dataset_id" in transform_response.json()["result"]


def test_invalid_phase():
    """Test avec phase invalide"""
    response = client.post(
        "/dataset/generate",
        json={
            "phase": "invalid_phase",
            "seed": 42,
            "n": 100
        }
    )
    assert response.status_code == 400


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
