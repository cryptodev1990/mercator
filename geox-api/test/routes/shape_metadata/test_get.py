# pylint: disable=unused-argument
"""Test PATCH /geofencer/shapes/{shape_id}."""
from typing import Set

import pytest
from fastapi.testclient import TestClient
from requests import Response

from app.crud.namespaces import get_namespace_by_slug

from ..conftest import ExampleDbAbc, get_unused_namespace_id


def _response_shape_names(response: Response) -> Set[str]:
    return {x["name"] for x in response.json()}  # type: ignore


def check_shapes(response: Response, expected_names: Set[str]) -> None:
    assert response.status_code == 200
    actual_names = _response_shape_names(response)
    assert actual_names == expected_names
    # check that the response is in the correct sort order
    response_ids = [shp["uuid"] for shp in response.json()]
    assert response_ids == sorted(response_ids)


def test_read_all_shapes(client: TestClient, db: ExampleDbAbc) -> None:
    response = client.get("/geofencer/shape-metadata")
    check_shapes(
        response,
        {
            "pink-objective",
            "convoluted-sledder",
            "isobaric-concentration",
            "short-bulldozer",
            "thundering-use",
        },
    )


def test_read_shapes_same_user(client: TestClient, db: ExampleDbAbc) -> None:
    response = client.get("/geofencer/shape-metadata", params={"user": True})
    check_shapes(
        response,
        {
            "pink-objective",
            "convoluted-sledder",
            "isobaric-concentration",
            "short-bulldozer",
        },
    )


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
    response = client.get("/geofencer/shape-metadata", params={"namespace": namespace_id})
    check_shapes(response, expected)


def test_read_shapes_namespace_not_exists(client: TestClient, db: ExampleDbAbc) -> None:
    """Return an empty list if there are no shapes in the namespace."""
    namespace_id = get_unused_namespace_id(db.conn)
    response = client.get(
        "/geofencer/shape-metadata", params={"namespace": str(namespace_id)}
    )
    check_shapes(response, set())


def test_get_shapes_with_uuid(client: TestClient, db: ExampleDbAbc) -> None:
    shape_ids = [
        str(shp.uuid)
        for nm, shp in db.shapes.items()
        if nm in {"pink-objective", "isobaric-concentration"}
    ]
    response = client.get("/geofencer/shape-metadata", params={"id": shape_ids})
    check_shapes(response, {"pink-objective", "isobaric-concentration"})


def test_get_shapes_with_one_uuid(client: TestClient, db: ExampleDbAbc) -> None:
    shape_id = str(db.shapes["pink-objective"].uuid)
    response = client.get("/geofencer/shape-metadata", params={"id": shape_id})
    check_shapes(response, {"pink-objective"})


# TODO: redo shapes so that a more restrictive bounding box could be used
def test_read_shapes_by_bbox(client: TestClient, db: ExampleDbAbc) -> None:
    response = client.get(
        "/geofencer/shape-metadata", params={"bbox": [-123, 37, -121, 38]}
    )
    check_shapes(
        response,
        {
            "pink-objective",
            "isobaric-concentration",
            "short-bulldozer",
        },
    )
