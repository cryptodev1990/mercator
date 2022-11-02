"""Test PATCH /geofencer/shapes/{shape_id}."""
import datetime
import uuid
from typing import Any, Dict, cast

from fastapi.testclient import TestClient

from app.schemas import GeoShape

from .conftest import ExampleDbAbc, get_unused_shape_id

_new_geom = {
    "coordinates": [[[8, -57], [62, 10], [-1, 7], [-88, -27], [8, -57]]],
    "type": "Polygon",
}
_new_name = "bright-curve"
_new_props = {"foo": "bar"}


def test_patch_other_org(client: TestClient, db: ExampleDbAbc):
    shape_id = db.shapes["several-sword"].uuid
    data = {"name": _new_name}
    response = client.patch(f"/geofencer/shapes/{shape_id}", json=data)
    assert response.status_code == 404


def test_patch_shape_does_not_exist(client: TestClient, db: ExampleDbAbc):
    shape_id = get_unused_shape_id(db.conn)
    data = {"name": _new_name}
    response = client.patch(f"/geofencer/shapes/{shape_id}", json=data)
    assert response.status_code == 404


def check_update_shape(actual: GeoShape, expected: GeoShape) -> None:
    assert actual.geojson.geometry == expected.geojson.geometry
    assert actual.geojson.id == str(actual.uuid)
    assert actual.uuid == expected.uuid
    assert actual.geojson.properties == expected.geojson.properties
    assert actual.created_at == expected.created_at
    assert cast(datetime.datetime, actual.updated_at) > cast(
        datetime.datetime, expected.updated_at
    )


import pytest
from geojson_pydantic import Feature
from pydantic import UUID4

from app.schemas import BaseModel, GeoShapeUpdate


class ExampleTestCase(BaseModel):
    shape_id: UUID4
    data: GeoShapeUpdate
    expected: GeoShape


@pytest.fixture(
    params=[
        "name",
        "properties",
        "geometry",
        "geojson",
        "empty dict",
        "empty values ignored",
        "empty property dict",
    ]
)
def example_test_cases(request, db: ExampleDbAbc) -> ExampleTestCase:
    old_shape = db.shapes["pink-objective"]
    shape_id = old_shape.uuid
    expected = GeoShape.parse_obj(old_shape.dict())
    expected.geojson.properties = expected.geojson.properties or {}
    data: Dict[str, Any]
    if request.param == "name":
        data = {"name": _new_name}
        cast(Dict[str, Any], expected.geojson.properties)["name"] = _new_name
    elif request.param == "properties":
        data = {"properties": _new_props}
        expected.geojson.properties = {
            **_new_props,
            "name": (expected.geojson.properties or {}).get("name"),
            "__uuid": shape_id,
        }
    elif request.param == "geometry":
        data = {"geom": _new_geom}
        expected.geojson.geometry = _new_geom
    elif request.param == "geojson":
        data = {
            "geojson": {
                "geometry": _new_geom,
                "properties": {**_new_props, "name": _new_name, "__uuid": shape_id},
            }
        }
        expected.geojson.geometry = _new_geom
        expected.geojson.properties = {
            **_new_props,
            "name": _new_name,
            "__uuid": shape_id,
        }
    elif request.param == "empty dict":
        data = {}
    elif request.param == "empty values ignored":
        data = {"name": None, "properties": None, "geojson": None, "geom": None}
    elif request.param == "empty property dict":
        data = {"properties": {}}
        expected.geojson.properties = {
            "name": (expected.geojson.properties or {}).get("name")
        }
    elif request.param == "properties with __uuid":
        data = {"properties": {**_new_props, "__uuid": uuid.uuid4()}}
        expected.geojson.properties = {
            **_new_props,
            "name": (expected.geojson.properties or {}).get("name"),
            "__uuid": shape_id,
        }
    elif request.param == "geojson.properties with __uuid":
        data = {
            "geojson": {
                "geometry": _new_geom,
                "properties": {
                    **_new_props,
                    "name": _new_name,
                    "__uuid": str(shape_id),
                },
            }
        }
        expected.geojson.geometry = _new_geom
        expected.geojson.properties = {
            **_new_props,
            "name": _new_name,
            "__uuid": shape_id,
        }
    else:
        raise ValueError("Invalid param")
    return ExampleTestCase(
        shape_id=shape_id, data=GeoShapeUpdate.parse_obj(data), expected=expected
    )


def test_patch_shape_works(
    client: TestClient, db: ExampleDbAbc, example_test_cases
) -> None:
    old_shape = db.shapes["pink-objective"]
    data = {"name": _new_name}
    expected = GeoShape.parse_obj(old_shape.dict())
    cast(Dict[str, Any], expected.geojson.properties)["name"] = _new_name
    response = client.patch(f"/geofencer/shapes/{old_shape.uuid}", json=data)
    assert response.status_code == 200
    actual = GeoShape.parse_obj(response.json())
    check_update_shape(actual, expected)
