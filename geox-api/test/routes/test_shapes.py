"""Test shapes/* routes."""

import datetime
import json
import pathlib
from functools import partial
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional
from uuid import UUID

import pytest
from fastapi import Depends, status
from fastapi.testclient import TestClient
from geojson_pydantic import Feature, Point
from ruamel.yaml import YAML
from sqlalchemy import insert, select, text
from sqlalchemy.engine import Connection, Row  # type: ignore

from app import schemas
from app.core.access_token import get_access_token
from app.core.config import get_settings
from app.db.session import engine
from app.dependencies import verify_token
from app.dependencies_alt import get_current_user, get_db_conn
from app.main import app
from app.models import Organization, OrganizationMember, Shape, User
from app.schemas import GeoShapeCreate

yaml = YAML(typ="safe")


def ymd(x):
    return x.strftime("%Y-%m-%dT%H:%M:%S.%f")


def assert_ok(response):
    assert response.status_code == status.HTTP_200_OK, "Not OK, got " + response.text


access_token = get_access_token()
headers = {"Authorization": f"Bearer {access_token}"}

client = TestClient(app)

here = pathlib.Path(__file__).parent.resolve()

settings = get_settings()

users_tbl = User.__table__
organizations_tbl = Organization.__table__
organization_members_tbl = OrganizationMember.__table__
shape_tbl = Shape.__table__


@pytest.fixture(scope="module")
def test_data():
    data_dir = Path("test/fixtures/db/test-data-1/")
    with open(data_dir / "users.yaml", "r") as f:
        users = yaml.load(f)

    with open(data_dir / "organizations.yaml", "r") as f:
        org_data_raw = yaml.load(f)

    with open(data_dir / "shapes_new.yaml", "r") as f:
        shapes = yaml.load(f)

    org_data = []
    org_member_data = []
    for org in org_data_raw:
        org_data.append({k: v for k, v in org.items() if k not in {"members"}})
        for member in org["members"]:
            org_member_data.append(
                {**member, "organization_id": org["id"], "active": False}
            )
    return {
        "organizations": org_data,
        "organization_members": org_member_data,
        "users": users,
        "shapes": shapes,
    }


def get_user_orgs(conn: Connection, user_id: int) -> List[Row]:
    stmt = text(
        """
    SELECT
        o.id AS organization_id
        , o.is_personal
    FROM organizations AS o
    INNER JOIN organization_members AS om
        ON o.id = om.organization_id
        AND om.user_id = :user_id
    """
    )
    return conn.execute(stmt, {"user_id": user_id}).fetchall()


def get_user_personal_org(conn: Connection, user_id: int) -> Optional[UUID]:
    stmt = text(
        """
    SELECT o.id AS organization_id
    FROM organizations AS o
    INNER JOIN organization_members AS om
        ON o.id = om.organization_id
        AND om.user_id = :user_id
        AND o   .is_personal
    LIMIT 1
    """
    )
    return conn.execute(stmt, {"user_id": user_id}).scalar()


def set_active_organization(conn, user_id: int, organization_id: UUID):
    stmt = text(
        """
        UPDATE organization_members
        SET active = (organization_id = :organization_id)
        WHERE user_id = :user_id
    """
    )
    conn.execute(stmt, {"organization_id": organization_id, "user_id": user_id})


@pytest.fixture()
def connection(test_data: Dict[str, Any]) -> Generator[Connection, None, None]:
    with engine.begin() as conn:
        conn.execute(insert(users_tbl), test_data["users"])
        conn.execute(insert(organizations_tbl), test_data["organizations"])
        for org_member in test_data["organization_members"]:
            conn.execute(insert(organization_members_tbl), org_member)
            set_active_organization(
                conn, org_member["user_id"], UUID(org_member["organization_id"])
            )
        conn.execute(insert(shape_tbl), test_data["shapes"])  # type: ignore
        try:
            yield conn
        finally:
            conn.rollback()


def get_db_conn_override(connection):
    """Override get_db_conn.

    The setup/teardown is done in connection fixture.
    This function ensures that the route uses the same connection value.
    The reason is that the test can be encapsulated in a single transaction that never commits to the database

    """

    def f():
        yield connection
        # reset role from APP_USER
        connection.execute(text("RESET ROLE"))

    return f


def get_current_user_override(
    *, user_id: int, conn: Connection = Depends(get_db_conn)
) -> schemas.User:
    """Return a particular existing user by id.

    This skips authentication of users to allow fake users.
    """
    user = conn.execute(select(users_tbl).where(users_tbl.c.id == user_id)).fetchone()
    out = schemas.User.from_orm(user)
    return out


@pytest.fixture()
def dep_override_factory(fastapi_dep, connection):
    """Return the common dependency overrides."""

    def overrides(user_id: int):
        return fastapi_dep(app).override(
            {
                get_db_conn: get_db_conn_override(connection),
                get_current_user: partial(get_current_user_override, user_id=user_id),
                verify_token: lambda: {},
            }
        )

    return overrides


def shape_exists(conn: Connection, shape_id: UUID) -> bool:
    stmt = text(
        """
    SELECT 1
    FROM shapes
    WHERE uuid = :shape_id
    """
    )
    return bool(conn.execute(stmt, {"shape_id": shape_id}).rowcount)


def test_policy_exists(connection):
    assert connection.execute(
        text(
            """
        SELECT exists(select 1 from pg_policies where tablename = 'shapes' and policyname = 'same_org')
        """
        )
    ).scalar()


def test_read_shape_self(connection, dep_override_factory):
    user_id = 1
    shape_id = "4f974f2d-572b-46f1-8741-56bf7f357d12"
    assert True
    assert shape_exists(connection, shape_id)
    with dep_override_factory(user_id):
        response = client.get(f"/geofencer/shapes/{shape_id}")
        body = response.json()
        assert body
        assert body.get("uuid") == shape_id


def test_read_shape_self_wrong_org(connection, dep_override_factory):
    user_id = 1
    shape_id = "4f974f2d-572b-46f1-8741-56bf7f357d12"
    # Change the org to the user's personal org
    personal_org = get_user_personal_org(connection, user_id)
    set_active_organization(connection, user_id, personal_org)
    assert shape_exists(connection, shape_id)
    with dep_override_factory(user_id):
        response = client.get(f"/geofencer/shapes/{shape_id}")
        body = response.json()
        assert body is None


def test_read_shape_diff_user_same_org(connection, dep_override_factory):
    """Read a shape from user in same org"""

    user_id = 1
    shape_id = "8073a55a-98d4-43a7-a1fa-eefab3980f7a"  # Owned by 4
    assert shape_exists(connection, shape_id)
    with dep_override_factory(user_id):
        response = client.get(
            f"/geofencer/shapes/{shape_id}",
        )
        body = response.json()
        assert body.get("uuid") == shape_id


def test_read_shape_diff_org(connection, dep_override_factory):
    """Cannot read a shape from a different org."""
    user_id = 1
    shape_id = "1f053556-c21b-4420-a188-09fc6931eb6f"  # Owned by 3 - diff org
    assert shape_exists(connection, shape_id)
    with dep_override_factory(user_id):
        response = client.get(f"/geofencer/shapes/{shape_id}", headers=headers)
        body = response.json()
        assert body == None


def test_read_shape_doesnt_exist(connection, dep_override_factory):
    """Cannot read a shape that doesn't exist."""
    user_id = 1
    shape_id = "59075662-68d4-408b-afe3-8a0b7af08bee"  # UUID doesn't exist

    # check that the uuid doesn't exist
    assert not shape_exists(connection, shape_id)
    with dep_override_factory(user_id):
        response = client.get(f"/geofencer/shapes/{shape_id}", headers=headers)
        body = response.json()
        assert body == None


def test_get_all_shapes_by_user(connection, dep_override_factory):
    user_id = 1
    user_shapes = {
        "4f974f2d-572b-46f1-8741-56bf7f357d12",
        "a5da808f-b717-41cb-a566-603674172bf2",
    }

    with dep_override_factory(user_id):
        response = client.get(f"/geofencer/shapes?rtype=user")
        assert_ok(response)
        body = response.json()
        assert body
        assert {shape["uuid"] for shape in body} == user_shapes


def test_get_all_shapes_by_organization(connection, dep_override_factory):
    user_id = 1
    organization_id = "5b706ffe-9608-4edd-bb00-ab9cbcb7384f"
    user_shapes = {
        "4f974f2d-572b-46f1-8741-56bf7f357d12",
        "8073a55a-98d4-43a7-a1fa-eefab3980f7a",
        "59955baf-9ffb-4c63-a6fa-6e790286d307",
        "88707385-829f-4edd-9860-927675a48c70",
        "a5da808f-b717-41cb-a566-603674172bf2",
        "45cd0ce9-7e2f-47cc-922a-fb02b0cf115b",
        "13c0b2ee-dada-421b-92eb-f756ef79d883",
    }

    with dep_override_factory(user_id):
        response = client.get(f"/geofencer/shapes?rtype=organization")
        assert_ok(response)
        body = response.json()
        assert body
        assert {shape["uuid"] for shape in body} == user_shapes


def test_update_shape(connection, dep_override_factory):
    user_id = 1
    shape_id = "4f974f2d-572b-46f1-8741-56bf7f357d12"

    shape_old = connection.execute(
        text("SELECT * FROM shapes WHERE uuid = :uuid LIMIT 1"), {"uuid": shape_id}
    ).fetchone()

    new_name = "fuchsia-auditor"
    new_shape = Feature(geometry=Point(coordinates=[-6.364088, -65.21654]))

    with dep_override_factory(user_id):
        response = client.put(
            f"/geofencer/shapes/{shape_id}",
            json={"uuid": str(shape_id), "geojson": new_shape.dict(), "name": new_name},
        )
        assert_ok(response)
        body = response.json()
        assert body
        geom = Feature.parse_obj(body.get("geojson"))
        assert body.get("name") == new_name, "Name should be updated"
        assert geom == new_shape, "GeoJSON should be updated"
        assert (
            datetime.datetime.strptime(body.get("created_at"), "%Y-%m-%dT%H:%M:%S")
            == shape_old.created_at
        ), "Created at should be the same"
        assert (
            body.get("updated_at") != shape_old.updated_at
        ), "Updated at should be different"


def test_delete_shape(connection, dep_override_factory):
    user_id = 1
    shape_id = "4f974f2d-572b-46f1-8741-56bf7f357d12"
    with dep_override_factory(user_id):
        response = client.put(
            f"/geofencer/shapes/{shape_id}",
            json={"uuid": str(shape_id), "should_delete": True},
        )
        assert_ok(response)
        body = response.json()
        assert body

    res = connection.execute(
        text(
            "SELECT uuid, deleted_at, deleted_by_user_id FROM shapes WHERE uuid = :uuid"
        ),
        {"uuid": shape_id},
    )
    row = res.fetchone()
    assert row.uuid == UUID(shape_id)
    assert row.deleted_at is not None
    assert row.deleted_by_user_id == user_id


def test_create_shape(connection, dep_override_factory):
    user_id = 1
    shape = GeoShapeCreate(
        name="fuchsia-auditor",
        geojson=Feature(id=None, geometry=Point(coordinates=[-6.364088, -65.21654])),
    )

    uuid = None

    with dep_override_factory(user_id):
        response = client.post(f"/geofencer/shapes", json=shape.dict())
        assert_ok(response)
        body = response.json()
        uuid = body["uuid"]
        assert body
        assert uuid
        assert body["name"] == shape.name
        assert body["created_by_user_id"] == user_id
        assert body["geojson"] == json.loads(json.dumps(shape.geojson.dict()))

    assert (
        connection.execute(
            text("SELECT uuid FROM shapes WHERE uuid = :uuid"), {"uuid": uuid}
        ).rowcount
        == 1
    )


def test_bulk_create_shapes(connection, dep_override_factory):
    user_id = 1
    shapes = [
        GeoShapeCreate(
            name="fuchsia-auditor",
            geojson=Feature(geometry=Point(coordinates=[-6.364088, -65.21654])),
        ),
        GeoShapeCreate(
            name="acute-vignette",
            geojson=Feature(geometry=Point(coordinates=[-20.586622, 53.832401])),
        ),
    ]

    with dep_override_factory(user_id):
        response = client.post(
            f"/geofencer/shapes/bulk", json=[s.dict() for s in shapes]
        )
        assert_ok(response)
        body = response.json()
        assert body
        assert body["num_shapes"] == 2

    for shp in shapes:
        assert (
            connection.execute(
                text("SELECT uuid FROM shapes WHERE name = :name"), {"name": shp.name}
            ).rowcount
            == 1
        )
