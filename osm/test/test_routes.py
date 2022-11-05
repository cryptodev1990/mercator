"""Test """
from fastapi.testclient import TestClient
from requests.models import Response


def assert_ok(response: Response) -> None:
    """Check that response is OK"""
    assert response.status_code == 200


def test_main(client: TestClient) -> None:
    """Test main."""
    response = client.get("/")
    assert_ok(response)


def test_health(client: TestClient) -> None:
    """Test health."""
    response = client.get("/health")
    assert_ok(response)


def test_db_health(client: TestClient) -> None:
    """Test db health."""
    response = client.get("/health/db")
    assert_ok(response)
