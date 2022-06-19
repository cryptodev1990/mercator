from fastapi.testclient import TestClient

from app.main import app

from .model import GeoLiftParams

client = TestClient(app)


def test_read_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"message": "OK"}
