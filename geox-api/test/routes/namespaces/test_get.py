from fastapi.testclient import TestClient

from .conftest import ExampleDbAbc


def test_get_namespaces(client: TestClient, db: ExampleDbAbc) -> None:
    response = client.get("/geofencer/namespaces")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
