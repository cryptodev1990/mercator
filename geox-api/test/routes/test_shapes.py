import json
from functools import partial
from operator import ge
from pathlib import Path
from typing import Optional
from uuid import UUID

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from geojson_pydantic import Feature, Point
from pydantic import UUID4
from pytest_fastapi_deps import DependencyOverrider
from ruamel.yaml import YAML
from sqlalchemy import select, text, update
from sqlalchemy.engine import Connection

from app.crud.organization import get_active_organization
from app.crud.user import get_user_by_email
from app.schemas import UserOrganization


import uuid


from app.crud.shape import shape_exists

from app.core.config import get_settings
from app.crud import organization
from app.crud.namespaces import get_default_namespace
from app.crud.organization import (
    get_active_organization,
    get_personal_org_id,
    set_active_organization,
)
from app.crud.shape import create_shape
from app.crud.user import get_user_by_email
from app.db.metadata import organization_members as org_mbr_tbl
from app.db.metadata import shapes as shapes_tbl
from app.dependencies import get_connection, get_current_user, verify_token
from app.main import app
from app.schemas import GeoShapeCreate
from app.schemas.organizations import Organization

from .conftest import get_connection_override, get_current_user_override
from fastapi import status

# used in fixtures
# from .conftest import connection, dep_override_factory  # type: ignore

yaml = YAML(typ="safe")


def ymd(x):
    return x.strftime("%Y-%m-%dT%H:%M:%S.%f")


def assert_ok(response):
    assert response.status_code == status.HTTP_200_OK


def assert_status_code(response, status_code: int):
    assert response.status_code == status_code


def dep_overrider(conn: Connection) -> DependencyOverrider:
    def f(user_id: int, organization_id: Optional[UUID4] = None):
        return DependencyOverrider(
            app,
            {
                get_connection: get_connection_override(conn),
                get_current_user: partial(
                    get_current_user_override,
                    user_id=user_id,
                    organization_id=organization_id,
                ),
                verify_token: lambda: {},
            },
        )

    return f


def get_user_org_by_email(conn: Connection, email: str) -> UserOrganization:
    user = get_user_by_email(conn, email)
    org = get_active_organization(conn, user.id)
    return UserOrganization(user=user, organization=org)


@pytest.fixture(scope="function")
def alice(conn: Connection) -> UserOrganization:
    return get_user_org_by_email(conn, "alice@example.com")


@pytest.fixture(scope="function")
def bob(conn: Connection) -> UserOrganization:
    return get_user_org_by_email(conn, "bob@example.com")


@pytest.fixture(scope="function")
def carlos(conn: Connection) -> UserOrganization:
    return get_user_org_by_email(conn, "carlos@example.net")


from app.schemas import BaseModel, User


class ConnectionWithDepOverrides(BaseModel):
    user: User
    organization: Organization
    conn: Connection
    dep_overrides: DependencyOverrider


@pytest.fixture(scope="function")
def alice_conn(conn: Connection, alice: UserOrganization) -> ConnectionWithDepOverrides:

    return ConnectionWithDepOverrides.parse_obj(
        {
            **alice.dict(),
            "conn": conn,
            "dep_overrides": dep_overrider(conn)(alice.user.id, alice.organization.id),
        }
    )


from geojson.utils import generate_random as generate_random_shape
from geojson_pydantic import Feature
from randomname import get_name as get_random_name

from app.schemas import GeoShapeCreate


def random_geojson(include_name=True):
    if include_name:
        name = get_random_name()
    else:
        name = None
    return Feature(
        geometry=generate_random_shape("Polygon", numberVertices=4),
        properties={"name": get_random_name()},
    )


from app.schemas import GeoShape


def test_read_shape_self(
    client: TestClient, alice_conn: ConnectionWithDepOverrides, bob: UserOrganization
):
    shape = create_shape(
        alice_conn.conn,
        user_id=alice_conn.user.id,
        organization_id=alice_conn.organization.id,
        geojson=random_geojson(),
    )
    with alice_conn.dep_overrides:
        response = client.get(f"/geofencer/shapes/{shape.uuid}")
        body = response.json()
        assert_ok(response)
        assert GeoShape.parse_obj(body) == shape


def test_read_shape_not_exists(
    client: TestClient, alice_conn: ConnectionWithDepOverrides
):
    # don't create any shapes
    shape_id = uuid.uuid4()
    with alice_conn.dep_overrides:
        response = client.get(f"/geofencer/shapes/{shape_id}")
        assert_status_code(response, status.HTTP_404_NOT_FOUND)


def test_read_shape_other_user_same_org(
    client: TestClient, alice_conn: ConnectionWithDepOverrides, bob: UserOrganization
):
    shape = create_shape(
        alice_conn.conn,
        user_id=bob.user.id,
        organization_id=bob.organization.id,
        geojson=random_geojson(),
    )
    with alice_conn.dep_overrides:
        response = client.get(f"/geofencer/shapes/{shape.uuid}")
        body = response.json()
        assert_ok(response)
        assert GeoShape.parse_obj(body) == shape


def test_read_shape_other_org(
    client: TestClient, alice_conn: ConnectionWithDepOverrides, carlos: UserOrganization
):
    shape = create_shape(
        alice_conn.conn,
        user_id=carlos.user.id,
        organization_id=carlos.organization.id,
        geojson=random_geojson(),
    )
    with alice_conn.dep_overrides:
        response = client.get(f"/geofencer/shapes/{shape.uuid}")
        assert_status_code(response, status.HTTP_404_NOT_FOUND)


def test_create_shape(
    client: TestClient, alice_conn: ConnectionWithDepOverrides, carlos: UserOrganization
):
    shape = random_geojson()
    create_shape = GeoShapeCreate(geojson=shape)
    with alice_conn.dep_overrides:
        response = client.post(f"/geofencer/shapes", json=create_shape.dict())
        print(response.json())
        assert_ok(response)
        actual = GeoShape.parse_obj(response.json())
        assert actual.geojson.geometry == shape.geometry
        assert actual.geojson.properties == shape.properties
    # check that it was created in the database
    assert shape_exists(alice_conn.conn, actual.uuid)


# def test_get_all_shapes_by_user(client, connection, dep_override_factory):
#     user_id = 1
#     user_shapes = {
#         "4f974f2d-572b-46f1-8741-56bf7f357d12",
#         "a5da808f-b717-41cb-a566-603674172bf2",
#     }

#     with dep_override_factory(user_id):
#         response = client.get(f"/geofencer/shapes?user=true")
#         assert_ok(response)
#         body = response.json()
#         assert body
#         assert {shape["uuid"] for shape in body} == user_shapes


# def test_get_all_shapes_by_organization(client, connection, dep_override_factory):
#     user_id = 1
#     organization_id = "5b706ffe-9608-4edd-bb00-ab9cbcb7384f"
#     user_shapes = {
#         "4f974f2d-572b-46f1-8741-56bf7f357d12",
#         "8073a55a-98d4-43a7-a1fa-eefab3980f7a",
#         "59955baf-9ffb-4c63-a6fa-6e790286d307",
#         "88707385-829f-4edd-9860-927675a48c70",
#         "a5da808f-b717-41cb-a566-603674172bf2",
#         "45cd0ce9-7e2f-47cc-922a-fb02b0cf115b",
#         "13c0b2ee-dada-421b-92eb-f756ef79d883",
#     }

#     with dep_override_factory(user_id):
#         response = client.get(f"/geofencer/shapes")
#         assert_ok(response)
#         body = response.json()
#         assert body
#         assert {shape["uuid"] for shape in body} == user_shapes


# def test_delete_shape(client, connection, dep_override_factory):
#     user_id = 1
#     shape_id = "4f974f2d-572b-46f1-8741-56bf7f357d12"

#     with dep_override_factory(user_id):
#         response = client.put(
#             f"/geofencer/shapes/{shape_id}",
#             json={"uuid": str(shape_id), "should_delete": True},
#         )
#         assert_ok(response)
#         body = response.json()
#         assert not body

#     connection.commit()
#     res = connection.execute(
#         text(
#             "SELECT uuid, deleted_at, deleted_by_user_id FROM shapes WHERE uuid = :uuid"
#         ),
#         {"uuid": shape_id},
#     )
#     row = res.fetchone()
#     assert row.uuid == UUID(shape_id)
#     assert row.deleted_at is not None
#     assert row.deleted_by_user_id == user_id


# def test_create_shape(client, connection, dep_override_factory):
#     user_id = 1
#     shape = GeoShapeCreate(
#         name="fuchsia-auditor",
#         geojson=Feature(
#             id="1",
#             type="Feature",
#             geometry=Point(type="Point", coordinates=(-6.364088, -65.21654)),
#             properties={"test": "test"},
#         ),
#     )

#     uuid = None

#     with dep_override_factory(user_id):
#         response = client.post(f"/geofencer/shapes", json=shape.dict())
#         assert_ok(response)
#         body = response.json()
#         uuid = body["uuid"]
#         assert body
#         assert uuid
#         assert body["name"] == shape.name
#         assert (
#             tuple(body["geojson"]["geometry"]["coordinates"])
#             == shape.geojson.geometry.dict()["coordinates"]
#         )
#         assert body["geojson"]["geometry"]["type"] == shape.geojson.geometry.type

#     assert (
#         connection.execute(
#             text("SELECT uuid FROM shapes WHERE uuid = :uuid"), {"uuid": uuid}
#         ).rowcount
#         == 1
#     )


# def test_bulk_create_shapes(client, connection, dep_override_factory):
#     user_id = 1
#     shapes = [
#         GeoShapeCreate(
#             name="fuchsia-auditor",
#             geojson=Feature(
#                 id="1",
#                 type="Feature",
#                 properties={"test": 1},
#                 geometry=Point(type="Point", coordinates=(-6.364088, -65.21654)),
#             ),
#         ),
#         GeoShapeCreate(
#             name="acute-vignette",
#             geojson=Feature(
#                 id="2",
#                 type="Feature",
#                 properties={"test": 1},
#                 geometry=Point(type="Point", coordinates=(-20.586622, 53.832401)),
#             ),
#         ),
#     ]

#     with dep_override_factory(user_id):
#         response = client.post(
#             f"/geofencer/shapes/bulk", json=[s.dict() for s in shapes]
#         )
#         assert_ok(response)
#         body = response.json()
#         assert body
#         assert body["num_shapes"] == 2

#     for shp in shapes:
#         assert (
#             connection.execute(
#                 text("SELECT uuid FROM shapes WHERE name = :name"),
#                 {"name": shp.name},
#             ).rowcount
#             == 1
#         )
