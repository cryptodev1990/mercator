"""Common functions and fixtures used in testing API routes."""
from functools import partial
from typing import Any, Callable, Dict

import pytest
from fastapi import Depends
from sqlalchemy import delete, insert, text
from sqlalchemy.engine import Connection
from app.crud.namespaces import get_default_namespace

from app.crud.organization import get_active_org_data, set_active_org
from app.db.engine import engine
from app.db.metadata import organization_members as org_mbr_tbl
from app.db.metadata import organizations as org_tbl
from app.db.metadata import shapes as shapes_tbl
from app.db.metadata import users as users_tbl
from app.db.metadata import namespaces as namespaces_tbl
from app.dependencies import get_connection, get_current_user, verify_token
from app.main import app
from app.schemas import User, UserOrganization


@pytest.fixture()
def connection(test_data: Dict[str, Any]):
    with engine.connect() as conn:
        trans = conn.begin()
        try:
            for tbl in (shapes_tbl, namespaces_tbl, org_mbr_tbl, org_tbl, users_tbl):
                conn.execute(delete(tbl))
            conn.execute(insert(users_tbl), test_data["users"])  # type: ignore
            conn.execute(insert(org_tbl), test_data["organizations"])  # type: ignore
            for org_member in test_data["organization_members"]:
                conn.execute(insert(org_mbr_tbl), org_member)  # type: ignore
                # Set these new organizations to the active organization
                set_active_org(
                    conn, org_member["user_id"], org_member["organization_id"]
                )
            for shape in test_data["shapes"]:
                namespace_id = get_default_namespace(conn, shape["organization_id"]).id
                data = {**shape}
                data["name"] = data["geojson"]["properties"]["name"]
                data["properties"] = data["geojson"]["properties"]
                data["namespace_id"] = namespace_id
                conn.execute(insert(shapes_tbl), data)

            yield conn
        finally:
            trans.rollback


def get_current_user_override(
    *, user_id: int, conn: Connection = Depends(get_connection)
):
    """Return a particular existing user by id.

    This skips authentication of users to allow fake users.
    """
    user_res = conn.execute(
        text("SELECT * FROM users WHERE id = :id"), {"id": user_id}
    ).fetchone()
    user = User.from_orm(user_res)
    # Redis isn't available for tests so instead do this
    org = get_active_org_data(conn, user.id, use_cache=False)
    if org is None:
        raise ValueError(f"No active organization found for user = {user.id}")
    return UserOrganization(user=user, organization=org)


def get_connection_override(
    conn: Connection,
) -> Callable:
    """Return a connection.

    This merely returns a provided connection, which allows the route to
    use a connection defined outside the route. This makes it easier to
    test changes to the database made by a route while also wrapping it
    inside a transaction to keep those changes from being committed.

    """

    async def f() -> Connection:
        return conn

    return f


@pytest.fixture()
def dep_override_factory(fastapi_dep, connection):
    """Return the common dependency overrides."""

    def overrides(user_id: int):
        return fastapi_dep(app).override(
            {
                get_connection: get_connection_override(connection),
                get_current_user: partial(get_current_user_override, user_id=user_id),
                verify_token: lambda: {},
            }
        )

    return overrides
