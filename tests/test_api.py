from fastapi.testclient import TestClient

from backend.app import app

client = TestClient(app)


def test_create_list_and_delete_geofence():
    # List initial
    resp = client.get("/api/geofences")
    assert resp.status_code == 200

    # Create geofence
    payload = {
        "name": "test_zone",
        "latitude": -23.55,
        "longitude": -46.63,
        "radius_meters": 300.0,
    }
    resp = client.post("/api/geofences", json=payload)
    assert resp.status_code == 201
    assert resp.json()["name"] == "test_zone"

    # Verify present
    resp = client.get("/api/geofences")
    assert resp.status_code == 200
    names = [g["name"] for g in resp.json()]
    assert "test_zone" in names

    # Delete geofence
    resp = client.delete("/api/geofences/test_zone")
    assert resp.status_code == 200
    assert resp.json() == {"status": "deleted", "name": "test_zone"}

    # Delete again -> 404
    resp = client.delete("/api/geofences/test_zone")
    assert resp.status_code == 404
