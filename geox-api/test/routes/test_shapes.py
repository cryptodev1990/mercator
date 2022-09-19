import datetime
import json
import pathlib
from functools import partial
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import UUID

import pytest
from fastapi import Depends, status
from fastapi.testclient import TestClient
from geojson_pydantic import Feature, Point
from pytest_fastapi_deps import fastapi_dep  # type: ignore
from ruamel.yaml import YAML
from sqlalchemy import MetaData, delete, insert, select, text, update
from sqlalchemy.engine import Connection, Row  # type: ignore
from sqlalchemy.orm import Session

from app import models, schemas
from app.core.access_token import get_access_token
from app.core.config import get_settings
from app.db.base import Organization, OrganizationMember, User
from app.db.session import SessionLocal, engine
from app.dependencies import get_current_user, get_db, verify_token
from app.main import app
from app.models import Organization, OrganizationMember, Shape, User
from app.schemas import GeoShapeCreate
from app.schemas.shape import ShapeCountResponse

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


def clear_all_tables(conn: Connection, meta: MetaData):
    for table in reversed(meta.sorted_tables):
        conn.execute(table.delete())


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
        update(OrganizationMember)  # type: ignore
        .where(OrganizationMember.user_id == user_id)
        .values(active=(OrganizationMember.organization_id == organization_id))
    )
    return conn.execute(stmt)


def get_user_orgs(conn: Connection, user_id: int) -> List[Row]:
    stmt = select(
        Organization.id.label("organization_id"),  # type: ignore
        Organization.is_personal,
    ).join(OrganizationMember.organization.and_(OrganizationMember.user_id == user_id))
    return conn.execute(stmt).fetchall()


def get_user_personal_org(conn: Connection, user_id: int) -> Optional[UUID]:
    stmt = (
        select(Organization.id)  # type: ignore
        .join(OrganizationMember)  # type: ignore
        .filter(OrganizationMember.user_id == user_id, Organization.is_personal)
        .limit(1)
    )
    return conn.execute(stmt).scalar()


@pytest.fixture()
def connection(test_data: Dict[str, Any]):

    with engine.connect() as conn:
        with conn.begin():
            conn.execute(insert(User), test_data["users"])  # type: ignore
            conn.execute(
                insert(Organization), test_data["organizations"]
            )  # type: ignore
            for org_member in test_data["organization_members"]:
                conn.execute(insert(OrganizationMember),
                             org_member)  # type: ignore
                # Set these new organizations to the active organization
                set_active_organization(
                    conn, org_member["user_id"], org_member["organization_id"]
                )
            conn.execute(insert(Shape), test_data["shapes"])  # type: ignore
            conn.commit()

        yield conn

        # Can't trust routes to handle their transactions correctly so close any open
        # transactions
        try:
            conn.commit()
        except:
            pass

        with conn.begin():
            for tbl in (Shape, OrganizationMember, Organization, User):
                conn.execute(delete(tbl))  # type: ignore
            conn.commit()

        # clear_all_tables(conn, Base.metadata(bind=conn))


def get_current_user_override(*, user_id: int, db_session: Session = Depends(get_db)):
    """Return a particular existing user by id.

    This skips authentication of users to allow fake users.
    """
    user = db_session.execute(
        select(models.User).filter(models.User.id == user_id)  # type: ignore
    ).fetchone()
    return schemas.User.from_orm(user[0])


def get_db_override(connection):
    def f():
        db = SessionLocal(bind=connection)
        try:
            yield db
            try:
                db.commit()
            except:
                pass
        finally:
            db.close()

    return f


@pytest.fixture()
def dep_override_factory(fastapi_dep, connection):
    """Return the common dependency overrides."""

    def overrides(user_id: int):
        return fastapi_dep(app).override(
            {
                get_db: get_db_override(connection),
                get_current_user: partial(get_current_user_override, user_id=user_id),
                verify_token: lambda: {},
            }
        )

    return overrides


def shape_exists(conn: Connection, shape_id: UUID) -> bool:
    stmt = select(Shape).filter(Shape.uuid == shape_id)  # type: ignore
    return bool(conn.execute(stmt).fetchone())


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


# TODO: What to return if No UUID
# TODO: What to do if inalid UUID


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

    with engine.connect() as conn:
        shape_old = conn.execute(
            text(
                "SELECT * FROM shapes WHERE uuid = :uuid LIMIT 1"), {"uuid": shape_id}
        ).fetchone()

    new_name = "fuchsia-auditor"
    new_shape = Feature(geometry=Point(coordinates=[-6.364088, -65.21654]))

    with dep_override_factory(user_id):
        response = client.put(
            f"/geofencer/shapes/{shape_id}",
            json={"uuid": str(shape_id),
                  "geojson": new_shape.dict(), "name": new_name},
        )
        assert_ok(response)
        body = response.json()
        assert body
        geom = Feature.parse_obj(body.get("geojson"))
        assert body.get("name") == new_name, "Name should be updated"
        assert geom == new_shape, "GeoJSON should be updated"
        assert (
            datetime.datetime.strptime(
                body.get("created_at"), "%Y-%m-%dT%H:%M:%S")
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
        geojson=Feature(id=None, geometry=Point(
            coordinates=[-6.364088, -65.21654], properties={})),
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
            geojson=Feature(geometry=Point(
                coordinates=[-6.364088, -65.21654])),
        ),
        GeoShapeCreate(
            name="acute-vignette",
            geojson=Feature(geometry=Point(
                coordinates=[-20.586622, 53.832401])),
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
                text("SELECT uuid FROM shapes WHERE name = :name"), {
                    "name": shp.name}
            ).rowcount
            == 1
        )
