from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_read_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"message": "OK"}



def test_run_experiment():
    response = client.post(
        "/geolift/validate",
        # TODO what's the JSON that should go here?
        json={"id": "bazz", "title": "Bazz", "description": "Drop the bazz"}
    )
    assert response.status_code == 200
    assert response.json() == {"message": "OK"}
