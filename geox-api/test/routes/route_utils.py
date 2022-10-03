"""Common functions and fixtures used in testing API routes."""
from functools import partial
from typing import Any, Callable, Dict, List

import pytest
from fastapi import Depends
from sqlalchemy import delete, insert, select, text
from sqlalchemy.engine import Connection, Row  # type: ignore

from app.crud.organization import set_active_org
from app.db.engine import engine
from app.dependencies import get_current_user, get_connection, verify_token
from app.main import app
from app.schemas import User

from app.db.metadata import organizations as org_tbl
from app.db.metadata import organization_members as org_mbr_tbl
from app.db.metadata import shapes as shapes_tbl
from app.db.metadata import users as users_tbl



@pytest.fixture()
def connection(test_data: Dict[str, Any]):
    with engine.connect() as conn:
        trans = conn.begin()
        try:
            for tbl in (shapes_tbl, org_mbr_tbl, org_tbl, users_tbl):
                conn.execute(delete(tbl))
            conn.execute(insert(users_tbl), test_data["users"])  # type: ignore
            conn.execute(insert(org_tbl), test_data["organizations"])  # type: ignore
            for org_member in test_data["organization_members"]:
                conn.execute(insert(org_mbr_tbl), org_member)  # type: ignore
                # Set these new organizations to the active organization
                set_active_org(
                    conn, org_member["user_id"], org_member["organization_id"]
                )
            conn.execute(insert(shapes_tbl), test_data["shapes"])  # type: ignore

            yield conn
        finally:
            trans.rollback


def get_current_user_override(
    *, user_id: int, conn: Connection = Depends(get_connection)
):
    """Return a particular existing user by id.

    This skips authentication of users to allow fake users.
    """
    stmt = text("SELECT * FROM users WHERE id = :id")
    user = conn.execute(stmt, {"id": int(user_id)}).fetchone()
    return User.from_orm(user)


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
