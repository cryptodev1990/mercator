"""Test PATCH /geofencer/shapes/{shape_id}."""
from typing import Any, Dict, List, Set

import pytest
from fastapi.testclient import TestClient
from pydantic import UUID4
from sqlalchemy import text
from sqlalchemy.engine import Connection

from app.crud.namespaces import get_namespace_by_slug

from .conftest import ExampleDbAbc

_new_geom = {
    "coordinates": [[[8, -57], [62, 10], [-1, 7], [-88, -27], [8, -57]]],
    "type": "Polygon",
}
_new_name = "bright-curve"
_new_props = {"foo": "bar"}


EXAMPLES = [
    (
        "geojson only",
        {
            "geojson": {
                "geometry": _new_geom,
                "properties": {"name": _new_name, **_new_props},
            }
        },
    ),
    (
        "geojson with name",
        {
            "name": _new_name,
            "geojson": {
                "geometry": _new_geom,
                "properties": {"name": "bad name", **_new_props},
            },
        },
    ),
    (
        "no name or props",
        {
            "geojson": {
                "geometry": _new_geom,
                "properties": {},
            },
        },
    ),
    (
        "with namespace",
        {
            "geojson": {
                "geometry": _new_geom,
                "properties": {},
            },
            "namespace": "new-namespace",
        },
    ),
    (
        "geometry, properties, name",
        {
            "geometry": _new_geom,
            "name": _new_name,
            "properties": {"name": "bad name"},
        },
    ),
]

from app.crud.shape import shape_exists


@pytest.mark.parametrize("description,data", EXAMPLES)
def test_post(
    client: TestClient, db: ExampleDbAbc, description: str, data: Dict[str, Any]
) -> None:
    if "namespace" in data:
        data["namespace"] = str(
            get_namespace_by_slug(
                db.conn, data["namespace"], organization_id=db.alice.organization.id
            ).id
        )
    response = client.post("/geofencer/shapes", json=data)
    print(response.json())
    assert response.status_code == 200
    actual = response.json()
    assert actual["geojson"]["geometry"] == _new_geom
    shape_id = actual["uuid"]
    # check that shape exists on the database
    assert shape_exists(db.conn, shape_id)
