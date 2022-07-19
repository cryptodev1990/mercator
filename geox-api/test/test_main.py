import os
import pathlib

from fastapi.testclient import TestClient

from app.core.access_token import get_access_token
from app.main import app

access_token = get_access_token()


client = TestClient(app)


here = pathlib.Path(__file__).parent.resolve()


def test_read_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"message": "OK"}


# TODO this is an integration test and should be in its own module
def test_invalid_jwt_auth():
    with open(os.path.join(here, "fixtures/fake-jwt.txt"), "r") as f:
        fake_jwt = f.read()
        client.get("/protected_health", headers={"Authorization": f"Bearer {fake_jwt}"})
        response = client.get("/protected_health")
        assert response.status_code == 403


# TODO this is an integration test and should be in its own module
def test_missing_bearer_auth():
    client.get("/protected_health")
    response = client.get("/protected_health")
    assert response.status_code == 403


# TODO this is an integration test and should be in its own module
def test_bearer_auth():
    response = client.get(
        "/protected_health", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    assert response.json() == {"message": "OK"}
