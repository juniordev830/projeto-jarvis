"""Testes para o serviço e endpoint de inteligência de localização."""

import pytest
from fastapi.testclient import TestClient
from backend.app import app
from backend.location import get_location_info


client = TestClient(app)


def test_get_location_info_sp():
    info = get_location_info(-23.5505, -46.6333)
    assert info["latitude"] == -23.5505
    assert info["longitude"] == -46.6333
    assert info["country"] in ["Brasil", "Oceano / Território Internacional"]
    assert "demographics" in info
    assert "estimated_population" in info["demographics"]
    assert "business" in info
    assert "sample_companies" in info["business"]


def test_api_location_info_endpoint():
    response = client.get("/api/location/info?lat=-23.5505&lng=-46.6333")
    assert response.status_code == 200
    data = response.json()
    assert data["latitude"] == -23.5505
    assert data["longitude"] == -46.6333
    assert "demographics" in data
    assert "business" in data


def test_api_location_info_invalid_coords():
    response = client.get("/api/location/info?lat=100&lng=-46.6333")
    assert response.status_code == 400
