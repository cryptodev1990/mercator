"""Test PATCH /geofencer/shapes/{shape_id}."""
import datetime
from typing import Any, Dict, Optional, cast

import pytest
from fastapi.testclient import TestClient
from geojson_pydantic import Feature, Polygon

from app.crud.namespaces import create_namespace
from app.crud.shape import create_shape, shape_exists
from app.schemas import BaseModel, GeoShape

from .conftest import ConnectionWithDepOverrides


@pytest.fixture()
def feature_1() -> Feature[Polygon, Dict[str, Any]]:
    return Feature.parse_obj(
        {
            "properties": {"name": "Shape 1"},
            "geometry": {
                "coordinates": [[[8, -57], [62, 10], [-1, 7], [-88, -27], [8, -57]]],
                "type": "Polygon",
            },
        }
    )


class ShapeTestCase(BaseModel):
    data: Dict[str, Any]
    feature: Feature[Polygon, Dict[str, Any]]
    geojson: Optional[Feature[Polygon, Dict[str, Any]]]


@pytest.fixture(
    params=[
        "name",
        "properties",
        "geometry",
        "geojson",
        "name+properties",
        "name+geometry",
        "name+geojson",
        "properties+geometry",
        "properties+geojson",
        "geometry+geojson",
        "name+properties+geometry",
        "name+properties+geojson",
        "name+properties+geometry+geojson",
    ]
)
def patch_test_cases(request, feature_1):
    def copy_feature() -> Feature[Polygon, Dict[str, Any]]:
        return Feature.parse_obj(feature_1.dict())

    out = []
    new_name: str = "New Name"
    new_props: Dict[str, Any] = {"foo": 1}
    new_geometry = Polygon.parse_obj(
        {
            "coordinates": [[[87, 51], [-46, 61], [-40, -30], [36, -49], [87, 51]]],
            "type": "Polygon",
        }
    )
    new_geojson = {
        "properties": {"bar": "abcdef"},
        "geometry": {
            "coordinates": [[[-41, 34], [-27, -32], [82, -66], [39, 50], [-41, 34]]],
            "type": "Polygon",
        },
    }

    new_namespace = None
    if request.param == "name":
        # change name
        data = {"name": new_name}
        expected = copy_feature()
        expected.properties["name"] = new_name  # type: ignore
    elif request.param == "properties":
        # change name
        data = {"properties": new_props}
        expected: Feature[Polygon, Dict[str, Any]] = copy_feature()
        expected.properties = {"name": None, **new_props}  # type: ignore
    elif request.param == "geojson":
        # updates properties, but with no name!!
        data = {"geojson": new_geojson}
        expected = Feature.parse_obj(new_geojson)
    elif request.param == "geometry":
        data = {"geometry": new_geometry.dict()}
        expected: Feature[Polygon, Dict[str, Any]] = copy_feature()
        expected.geometry = new_geometry
    elif request.param == "name+properties":
        data = {"name": new_name, "properties": new_props}
        expected: Feature[Polygon, Dict[str, Any]] = copy_feature()
        expected.properties = {**new_props, "name": new_name}
    elif request.param == "name+geometry":
        data = {"name": new_name, "geometry": new_geometry.dict()}
        expected: Feature[Polygon, Dict[str, Any]] = copy_feature()
        expected.properties["name"] = new_name  # type: ignore
        expected.geometry = new_geometry
    elif request.param == "name+geojson":
        data = {"name": new_name, "geojson": new_geojson}
        expected: Feature[Polygon, Dict[str, Any]] = copy_feature()
        expected = Feature.parse_obj(new_geojson)
        expected.properties["name"] = new_name  # type: ignore
    elif request.param == "properties+geometry":
        data = {
            "properties": {"name": None, **new_props},
            "geometry": new_geometry.dict(),
        }
        expected = Feature.parse_obj(data)
    elif request.param == "properties+geojson":
        data = {"properties": new_props, "geojson": new_geojson}
        expected = Feature.parse_obj(new_geojson)
        expected.properties = {"name": None, **new_props}  # type: ignore
    elif request.param == "geometry+geojson":
        data = {"geometry": new_geometry.dict(), "geojson": new_geojson}
        expected = Feature.parse_obj(new_geojson)
        expected.geometry = new_geometry
    elif request.param == "name+properties+geometry":
        data = {
            "name": new_name,
            "properties": new_props,
            "geometry": new_geometry.dict(),
        }
        expected = Feature(properties=new_props, geometry=new_geometry)  # type: ignore
        expected.properties["name"] = new_name  # type: ignore
    elif request.param == "name+properties+geojson":
        data = {"name": new_name, "properties": new_props, "geojson": new_geojson}
        expected = Feature.parse_obj(new_geojson)
        expected.properties = new_props
        expected.properties["name"] = new_name  # type: ignore
    elif request.param == "name+properties+geometry+geojson":
        data = {
            "name": new_name,
            "properties": new_props,
            "geometry": new_geometry.dict(),
            "geojson": new_geojson,
        }
        # everything in geojson is overwritten
        expected = Feature(properties=new_props, geometry=new_geometry)  # type: ignore
        expected.properties["name"] = new_name  # type: ignore
    else:
        raise ValueError(f"{request.param} is unknown")

    return ShapeTestCase(
        feature=feature_1, data=data, geojson=expected, namespace=new_namespace
    )


def test_patch_shape(
    client: TestClient,
    alice_conn: ConnectionWithDepOverrides,
    patch_test_cases: ShapeTestCase,
):
    # data = shape to create
    _: ConnectionWithDepOverrides = alice_conn
    assert True

    shape = create_shape(
        _.conn,
        user_id=_.user.id,
        organization_id=_.organization.id,
        geojson=patch_test_cases.feature,
    )
    namespace = create_namespace(
        _.conn,
        name="Other namespace",
        user_id=_.user.id,
        organization_id=_.organization.id,
    )

    with _.dep_overrides:
        response = client.patch(
            f"/geofencer/shapes/{shape.uuid}", json=patch_test_cases.data
        )
        assert response.status_code == 200
        actual = GeoShape.parse_obj(response.json())
        assert cast(datetime.datetime, actual.updated_at) > cast(
            datetime.datetime, shape.updated_at
        )
        assert cast(datetime.datetime, actual.created_at) == cast(
            datetime.datetime, shape.created_at
        )
        if patch_test_cases.geojson:
            assert actual.geojson == patch_test_cases.geojson
        else:
            assert actual.geojson == shape.geojson
        assert actual.namespace_id == shape.namespace_id
        assert actual.uuid == shape.uuid

    assert shape_exists(_.conn, actual.uuid)


def test_patch_shape_with_namespace(
    client: TestClient,
    alice_conn: ConnectionWithDepOverrides,
    feature_1: Feature[Polygon, Dict[str, Any]],
):
    # data = shape to create
    _: ConnectionWithDepOverrides = alice_conn
    assert True

    shape = create_shape(
        _.conn,
        user_id=_.user.id,
        organization_id=_.organization.id,
        geojson=feature_1,
    )
    namespace = create_namespace(
        _.conn,
        name="Other namespace",
        user_id=_.user.id,
        organization_id=_.organization.id,
    )

    with _.dep_overrides:
        response = client.patch(
            f"/geofencer/shapes/{shape.uuid}", json={"namespace": str(namespace.id)}
        )
        assert response.status_code == 200
        actual = GeoShape.parse_obj(response.json())
        assert cast(datetime.datetime, actual.updated_at) > cast(
            datetime.datetime, shape.updated_at
        )
        assert cast(datetime.datetime, actual.created_at) == cast(
            datetime.datetime, shape.created_at
        )
        assert actual.geojson == shape.geojson
        assert actual.namespace_id == namespace.id
        assert actual.uuid == shape.uuid

    assert shape_exists(_.conn, actual.uuid)
