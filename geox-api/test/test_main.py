import os
import pathlib
import pytest
import time
from fastapi.testclient import TestClient
from app.lib.access_token import get_access_token

from app.main import app


access_token = get_access_token()


client = TestClient(app)


here = pathlib.Path(__file__).parent.resolve()


def test_read_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"message": "OK"}


@pytest.mark.skipif(True, reason="Test is not complete")
def test_run_experiment():
    response = client.post(
        "/geolift/validate",
        # TODO what's the JSON that should go here?
        json={"id": "bazz", "title": "Bazz", "description": "Drop the bazz"},
    )
    assert response.status_code == 200
    assert response.json() == {"message": "OK"}


# TODO this is an integration test and should be in its own module
def test_worker():
    response = client.post("/tasks/add?a=1&b=2")
    response = response.json()
    assert response["task_id"]
    task_id = response["task_id"]
    response = client.get(f"/tasks/{task_id}").json()
    poll_count = 0
    while response["task_status"] != "SUCCESS":
        response = client.get(f"/tasks/{task_id}").json()
        task_id = response["task_id"]
        time.sleep(1)
        # Timeout test
        poll_count += 1
        if poll_count > 10:
            assert False, "Timeout"
    assert response["task_result"] == 3


# TODO this is an integration test and should be in its own module
def test_invalid_jwt_auth():
    with open(os.path.join(here, "fixtures/fake-jwt.txt"), "r") as f:
        fake_jwt = f.read()
        client.get(
            "/protected_health", headers={"Authorization": f"Bearer {fake_jwt}"}
        )
        response = client.get("/protected_health")
        assert response.status_code == 403


# TODO this is an integration test and should be in its own module
def test_missing_bearer_auth():
    client.get("/protected_health")
    response = client.get("/protected_health")
    assert response.status_code == 403


# TODO this is an integration test and should be in its own module
def test_bearer_auth():
    response = client.get("/protected_health", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    assert response.json() == {"message": "OK"}