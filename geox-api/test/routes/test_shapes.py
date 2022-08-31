import json
import os
import pathlib
from functools import partial
from pathlib import Path
from uuid import UUID

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from ruamel.yaml import YAML
from sqlalchemy import MetaData, delete, insert, select, text
from sqlalchemy.engine import Connection

from app.core.access_token import get_access_token
from app.core.config import get_settings
from app.db.base import Organization, OrganizationMember, User
from app.db.session import SessionLocal, engine
from app.main import app
from app.models import Organization, OrganizationMember, Shape, User

yaml = YAML(typ="safe")


def ymd(x):
    return x.strftime("%Y-%m-%dT%H:%M:%S.%f")


def assert_ok(response):
    assert response.status_code == status.HTTP_200_OK, "Not OK, got " + response.text


access_token = get_access_token()
headers = {"Authorization": f"Bearer {access_token}"}


client = TestClient(app)

here = pathlib.Path(__file__).parent.resolve()

geojson = json.loads(open(os.path.join(here, "../fixtures/bbox.geojson")).read())

settings = get_settings()


def clear_all_tables(conn: Connection, meta: MetaData):
    for table in reversed(meta.sorted_tables):
        conn.execute(table.delete())


settings = get_settings()


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


from typing import Any, Dict, List
from uuid import UUID

from sqlalchemy import update
from sqlalchemy.engine import Row


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


from typing import Optional
from uuid import UUID


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
            conn.execute(insert(Organization), test_data["organizations"])  # type: ignore
            for org_member in test_data["organization_members"]:
                conn.execute(insert(OrganizationMember), org_member)  # type: ignore
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


from fastapi import Depends
from pytest_fastapi_deps import fastapi_dep
from sqlalchemy import delete, insert, select
from sqlalchemy.orm import Session

from app import models, schemas
from app.dependencies import get_current_user, get_db, verify_token


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
    shape_id = "1f053556-c21b-4420-a188-09fc6931eb6a"  # UUID doesn't exist

    # check that the uuid doesn't exist
    assert not shape_exists(connection, shape_id)
    with dep_override_factory(user_id):
        response = client.get(f"/geofencer/shapes/{shape_id}", headers=headers)
        body = response.json()
        assert body == None


def test_get_all_shapes_user(connection, dep_override_factory):
    user_id = 1

    with dep_override_factory(user_id):
        response = client.get(f"/geofencer/shapes?rtype=user")
        assert_ok(response)
        body = response.json()
        assert body
        print(body)


# def test_update_shape():
#     def _test(shape: Shape):
#         edited_geojson = json.loads(
#             open(os.path.join(here, "../fixtures/edited-bbox.geojson")).read()
#         )
#         response = client.put(
#             f"/geofencer/shapes/" + str(shape.uuid),
#             json={
#                 "uuid": str(shape.uuid),
#                 "name": "edited test shape",
#                 "geojson": edited_geojson,
#             },
#             headers=headers,
#         )

#         body = response.json()
#         geom = body.get("geojson")["geometry"]
#         assert_ok(response)
#         assert body.get("name") == "edited test shape", "Name should be updated"
#         assert geom == edited_geojson["geometry"], "GeoJSON should be updated"
#         assert geom != geojson["geometry"], "GeoJSON should be updated"
#         assert ymd(shape.created_at) == body.get(
#             "created_at"
#         ), "created_at should be the same"
#         assert ymd(shape.updated_at) < body.get(
#             "updated_at"
#         ), "updated_at should be updated"

#     run_shape_test(_test)


# def test_soft_delete_update_shape():
#     def _test(shape: Shape):
#         response = client.put(
#             f"/geofencer/shapes/" + str(shape.uuid),
#             json={"should_delete": True, "uuid": str(shape.uuid)},
#             headers=headers,
#         )
#         assert_ok(response)
#         body = response.json()
#         assert not body

#     run_shape_test(_test)


# def test_bulk_delete_shapes():
#     try:
#         _, shape1 = setup_shape()
#         _, shape2 = setup_shape(should_cleanup=False, should_create_test_user=False)
#         _, shape3 = setup_shape(should_cleanup=False, should_create_test_user=False)
#         response = client.get(f"/geofencer/shapes?rtype=user", headers=headers)
#         body = response.json()
#         assert len(body) == 3
#         response = client.delete(
#             f"/geofencer/shapes/bulk",
#             json=[str(shape1.uuid), str(shape2.uuid), str(shape3.uuid)],
#             headers=headers,
#         )
#         assert_ok(response)
#         body = response.json()
#         assert body == {"num_shapes": 3}
#     finally:
#         cleanup()


# def test_bulk_create_shapes():
#     try:
#         payload = [{"name": f"test shape {i}", "geojson": geojson} for i in range(0, 3)]
#         response = client.post(f"/geofencer/shapes/bulk", json=payload, headers=headers)
#         assert_ok(response)
#         body = response.json()
#         assert body == {"num_shapes": 3}
#         response = client.get(f"/geofencer/shapes?rtype=user", headers=headers)
#         assert_ok(response)
#         body = response.json()
#         assert [shape["name"] == f"test shape {i}" for i, shape in enumerate(body)]
#     finally:
#         cleanup()
