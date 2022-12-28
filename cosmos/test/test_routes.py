import os
import pytest

from fastapi.testclient import TestClient
import httpx


def assert_ok(response: httpx.Response) -> None:
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

# Mark to run only if the environment variable is set
@pytest.mark.skipif(
    os.environ.get("COSMOS_ASYNC_TEST") is None,
    reason="COSMOS_ASYNC_TEST environment variable not set",
)
def test_osm_query(client: TestClient) -> None:
    """Test osm query."""
    response = client.get("/osm/query?query=alamo+square+park")
    assert_ok(response)
    assert response.json()["parse_result"]["entities"][0]["lookup"] == "alamo square park"
    assert response.json()["parse_result"]["geom"]["features"][0]["properties"]["name"] == "Alamo Square"
    assert response.json()["parse_result"]["geom"]["features"][0]["geometry"]["type"] == "Polygon"

