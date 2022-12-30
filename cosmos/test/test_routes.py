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

@pytest.mark.asyncio
def test_explicit_search(client: TestClient) -> None:
    """Test explicit search."""
    response = client.get("/search?query=alamo+square+park&type=named_place")
    assert_ok(response)
    assert response.json()["parse_result"]["entities"][0]["lookup"] == "alamo square park"
    assert response.json()["parse_result"]["geom"]["features"][0]["properties"]["name"] == "Alamo Square"
    assert response.json()["parse_result"]["geom"]["features"][0]["geometry"]["type"] == "Polygon"

    response = client.get("/search?query=irish+pubs&type=category")
    assert_ok(response)
    assert response.json()["parse_result"]["entities"][0]["lookup"] == "alamo square park"
    assert response.json()["parse_result"]["geom"]["features"][0]["properties"]["name"] == "Alamo Square"
    assert response.json()["parse_result"]["geom"]["features"][0]["geometry"]["type"] == "Polygon"

    response = client.get("/search?query=alamo&type=fuzzy")
    assert_ok(response)
    assert response.json()["parse_result"]["entities"][0]["lookup"] == "alamo square park"
    assert response.json()["parse_result"]["geom"]["features"][0]["properties"]["name"] == "Alamo Square"
    assert response.json()["parse_result"]["geom"]["features"][0]["geometry"]["type"] == "Polygon"


def test_osm_execute__x_in_y(client: TestClient) -> None:
    """TODO Passes with `pytest -k test_osm_execute` but fails with `pytest`, why?"""
    test_payload = {
        "name": "x_in_y",
        "args": {
            "needle_place_or_amenity": {
                "lookup": "coffee shops",
                "match_type": "fuzzy",
            },
            "haystack_place_or_amenity": {
                "lookup": "San Francisco",
                "match_type": "named_place",
            }
        }
    }
    response = client.post(
        "/osm/execute",
        json=test_payload
    )
    assert response.status_code == 200, "Encountered" + response.text
    assert response.json()["parse_result"]["entities"][0]["lookup"] == "coffee shops"
    assert response.json()["parse_result"]["geom"]["features"][0]["properties"]['tags']['name'] == "Robin's Cafe"
    

def test_osm_execute__x_between_y_and_z(client: TestClient) -> None:
    """TODO Passes with `pytest -k test_osm_execute` but fails with `pytest`, why?"""
    test_payload = {
        "name": "x_between_y_and_z",
        "args": {
            "named_place_or_amenity_0": {
                "lookup": "gas stations",
                "match_type": "fuzzy",
            },
            "named_place_or_amenity_1": {
                "lookup": "Union Square San Francisco",
                "match_type": "named_place",
            },
            "named_place_or_amenity_2": {
                "lookup": "Ocean Beach San Francisco",
                "match_type": "named_place",
            },
        }
    }
    response = client.post(
        "/osm/execute",
        json=test_payload
    )
    assert response.status_code == 200, "Encountered" + response.text
    assert response.json()["parse_result"]["entities"][0]["lookup"] == "gas stations"
    assert response.json()["parse_result"]["geom"]["features"][0]["properties"]['tags']['name'] == "Station K"


def test_osm_execute__raw_lookup_fuzzy(client: TestClient) -> None:
    """TODO Passes with `pytest -k test_osm_execute` but fails with `pytest`, why?"""
    test_payload = {
        "name": "raw_lookup",
            "args": {
                "search_term": {
                    "lookup": "gas stations",
                    "match_type": "fuzzy",
            }
        }
    }
    response = client.post(
        "/osm/execute",
        json=test_payload
    )
    assert response.status_code == 200, "Encountered" + response.text
    assert response.json()["parse_result"]["entities"][0]["lookup"] == "gas stations"
    assert response.json()["parse_result"]["geom"]["features"][0]["properties"]['tags']['name'] == "76 gas station"


def test_osm_execute__raw_lookup_named_place(client: TestClient) -> None:
    """TODO Passes with `pytest -k test_osm_execute` but fails with `pytest`, why?"""
    test_payload = {
        "name": "raw_lookup",
            "args": {
                "search_term": {
                    "lookup": "Alamo Square",
                    "match_type": "named_place",
            }
        }
    }
    response = client.post(
        "/osm/execute",
        json=test_payload
    )
    assert response.status_code == 200, "Encountered" + response.text
    parse = response.json()["parse_result"]
    assert parse["geom"]["features"][0]["properties"]['tags']['name'] == "Alamo Square"
    assert parse["geom"]["features"][0]["id"] == "W745183964"


def test_osm_execute__raw_lookup_category_match(client: TestClient) -> None:
    """TODO Passes with `pytest -k test_osm_execute` but fails with `pytest`, why?"""
    test_payload = {
        "name": "raw_lookup",
            "args": {
                "search_term": {
                    "lookup": "Alamo Square",
                    "match_type": "category",
            }
        }
    }
    response = client.post(
        "/osm/execute",
        json=test_payload
    )
    assert response.status_code == 200, "Encountered" + response.text
    parse = response.json()["parse_result"]
    assert parse["geom"]["features"][0]["properties"]['tags']['name'] == "Alamo Square"
    assert parse["geom"]["features"][0]["id"] == "W745183964"