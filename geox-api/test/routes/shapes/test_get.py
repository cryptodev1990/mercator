"""Test PATCH /geofencer/shapes/{shape_id}."""
from typing import List, Set

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.crud.namespaces import get_namespace_by_slug

from .conftest import ExampleDbAbc, get_unused_namespace_id


def _response_shape_names(response) -> List[str]:
    return set([x["geojson"]["properties"]["name"] for x in response.json()])  # type: ignore


def test_read_all_shapes(client: TestClient, db: ExampleDbAbc) -> None:
    response = client.get(f"/geofencer/shapes")
    assert response.status_code == 200
    names = set([x["geojson"]["properties"]["name"] for x in response.json()])
    assert names == {
        "pink-objective",
        "convoluted-sledder",
        "isobaric-concentration",
        "short-bulldozer",
        "thundering-use",
    }


def test_read_shapes_same_user(client: TestClient, db: ExampleDbAbc) -> None:
    response = client.get(f"/geofencer/shapes", params={"user": True})
    assert response.status_code == 200
    names = set([x["geojson"]["properties"]["name"] for x in response.json()])
    assert names == {
        "pink-objective",
        "convoluted-sledder",
        "isobaric-concentration",
        "short-bulldozer",
    }


@pytest.mark.parametrize(
    "namespace,expected",
    [
        [
            "default",
            {"pink-objective", "convoluted-sledder", "thundering-use"},
        ],
        [
            "new-namespace",
            {
                "isobaric-concentration",
                "short-bulldozer",
            },
        ],
    ],
)
def test_read_shapes_namespace(
    client: TestClient, db: ExampleDbAbc, namespace: str, expected: Set[str]
) -> None:
    namespace_id = str(get_namespace_by_slug(db.conn, namespace).id)
    response = client.get(f"/geofencer/shapes", params={"namespace": namespace_id})
    assert response.status_code == 200
    assert _response_shape_names(response) == expected


def test_read_shapes_namespace_not_exists(client: TestClient, db: ExampleDbAbc) -> None:
    namespace_id = get_unused_namespace_id(db.conn)
    response = client.get(f"/geofencer/shapes", params={"namespace": str(namespace_id)})
    assert response.status_code == 200
    assert response.json() == []


def test_get_shapes_with_uuid(client: TestClient, db: ExampleDbAbc) -> None:
    shape_ids = [
        str(shp.uuid)
        for nm, shp in db.shapes.items()
        if nm in {"pink-objective", "isobaric-concentration"}
    ]
    response = client.get(f"/geofencer/shapes", params={"shape_ids": shape_ids})
    assert response.status_code == 200
    assert _response_shape_names(response) == {
        "pink-objective",
        "isobaric-concentration",
    }


def test_get_shapes_with_one_uuid(client: TestClient, db: ExampleDbAbc) -> None:
    shape_id = str(db.shapes["pink-objective"].uuid)
    response = client.get(f"/geofencer/shapes", params={"shape_ids": shape_id})
    assert response.status_code == 200
    assert _response_shape_names(response) == {
        "pink-objective",
    }


# TODO: redo shapes so that a more restrictive bounding box could be used
def test_read_shapes_by_bbox(client: TestClient, db: ExampleDbAbc) -> None:
    response = client.get(f"/geofencer/shapes", params={"bbox": [-123, 37, -121, 38]})
    print(response.json())
    assert response.status_code == 200
    assert _response_shape_names(response) == {
        "pink-objective",
        "isobaric-concentration",
        "short-bulldozer",
    }
