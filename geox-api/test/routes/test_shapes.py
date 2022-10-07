import json
from pathlib import Path
from uuid import UUID

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from geojson_pydantic import Feature, Point
from pydantic import UUID4
from ruamel.yaml import YAML
from sqlalchemy import select, text, update
from sqlalchemy.engine import Connection

from app.core.config import get_settings
from app.crud.organization import get_active_org, get_personal_org_id
from app.db.metadata import organization_members as org_mbr_tbl
from app.db.metadata import shapes as shapes_tbl
from app.main import app
from app.schemas import GeoShapeCreate

# used in fixtures
from .route_utils import connection, dep_override_factory  # type: ignore

client = TestClient(app)

yaml = YAML(typ="safe")


settings = get_settings()


def shape_exists(conn: Connection, shape_id: UUID4) -> bool:
    stmt = text("SELECT 1 FROM shapes where uuid = :id")
    return bool(conn.execute(stmt, {"id": shape_id}).first())


def ymd(x):
    return x.strftime("%Y-%m-%dT%H:%M:%S.%f")


def assert_ok(response):
    assert response.status_code == status.HTTP_200_OK, "Not OK, got " + response.text


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


def set_active_organization(
    conn: Connection, user_id: int, organization_id: UUID
) -> None:
    stmt = (
        update(org_mbr_tbl)  # type: ignore
        .where(org_mbr_tbl.c.user_id == user_id)
        .values(active=(org_mbr_tbl.c.organization_id == organization_id))
        .returning(org_mbr_tbl)
    )
    res = conn.execute(stmt).fetchall()
    return res


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
    shape_id = UUID("4f974f2d-572b-46f1-8741-56bf7f357d12")
    assert shape_exists(connection, shape_id)
    with dep_override_factory(user_id):
        response = client.get(f"/geofencer/shapes/{shape_id}")
        body = response.json()
        assert body
        assert UUID(body.get("uuid")) == shape_id


def test_read_shape_self_wrong_org(connection, dep_override_factory):
    user_id = 1
    shape_id = UUID("4f974f2d-572b-46f1-8741-56bf7f357d12")
    # Change the org to the user's personal org
    personal_org = get_personal_org_id(connection, user_id)
    assert personal_org
    print(personal_org)
    get_active_org(connection, user_id, use_cache=False)
    set_active_organization(connection, user_id, personal_org)
    assert get_active_org(connection, user_id, use_cache=False) == personal_org
    assert shape_exists(connection, shape_id)
    with dep_override_factory(user_id):
        response = client.get(f"/geofencer/shapes/{shape_id}")
        assert response.status_code == 404


def test_read_shape_diff_user_same_org(connection, dep_override_factory):
    """Read a shape from user in same org."""

    user_id = 1
    shape_id = UUID("8073a55a-98d4-43a7-a1fa-eefab3980f7a")  # Owned by 4
    assert shape_exists(connection, shape_id)
    with dep_override_factory(user_id):
        response = client.get(
            f"/geofencer/shapes/{shape_id}",
        )
        body = response.json()
        assert UUID(body.get("uuid")) == shape_id


def test_read_shape_diff_org(connection, dep_override_factory):
    """Cannot read a shape from a different org."""
    user_id = 1
    # Owned by 3 - diff org
    shape_id = UUID("1f053556-c21b-4420-a188-09fc6931eb6f")
    assert shape_exists(connection, shape_id)
    with dep_override_factory(user_id):
        response = client.get(f"/geofencer/shapes/{shape_id}")
        assert response.status_code == 404


def test_read_shape_doesnt_exist(connection, dep_override_factory):
    """Cannot read a shape that doesn't exist."""
    user_id = 1
    # UUID doesn't exist
    shape_id = UUID("59075662-68d4-408b-afe3-8a0b7af08bee")

    # check that the uuid doesn't exist
    assert not shape_exists(connection, shape_id)
    with dep_override_factory(user_id):
        response = client.get(f"/geofencer/shapes/{shape_id}")
        assert response.status_code == 404


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
        assert not body

    connection.commit()
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
        geojson=Feature(
            id="1",
            type="Feature",
            geometry=Point(type="Point", coordinates=(-6.364088, -65.21654)),
            properties={"test": "test"},
        ),
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
            geojson=Feature(
                id="1",
                type="Feature",
                properties={"test": 1},
                geometry=Point(type="Point", coordinates=(-6.364088, -65.21654)),
            ),
        ),
        GeoShapeCreate(
            name="acute-vignette",
            geojson=Feature(
                id="2",
                type="Feature",
                properties={"test": 1},
                geometry=Point(type="Point", coordinates=(-20.586622, 53.832401)),
            ),
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
