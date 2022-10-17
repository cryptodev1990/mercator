"""Common functions and fixtures used in testing API routes."""
import random
from functools import partial
from string import ascii_letters, digits
from typing import Any, Callable, Dict, cast

import pytest
from fastapi import Depends
from sqlalchemy import text
from sqlalchemy.engine import Connection

from app.crud.organization import (
    add_user_to_org,
    create_organization,
    get_active_organization,
    get_organization,
    set_active_organization,
)
from app.crud.user import create_user as crud_create_user
from app.dependencies import get_connection, get_current_user_org, verify_token
from app.main import app
from app.schemas import User, UserOrganization

_ASCII_ALPHANUMERIC = ascii_letters + digits


def random_sub_id():
    prefix = "".join([random.choice(_ASCII_ALPHANUMERIC) for i in range(32)])
    return f"{prefix}@clients"


def create_user(conn: Connection, *, email: str, name: str) -> int:
    user = crud_create_user(
        conn,
        email=email,
        name=name,
        nickname=name,
        sub_id=random_sub_id(),
        iss="Fakeissuer",
    )
    return user.id


def insert_test_users_and_orgs(conn: Connection):
    organizations = [
        {
            "name": "Example.com",
            "users": [
                {"name": "Alice", "email": "alice@example.com"},
                {"name": "Bob", "email": "bob@example.com"},
            ],
        },
        {
            "name": "Example.net",
            "users": [{"name": "Carlos", "email": "carlos@example.net"}],
        },
    ]
    for org in organizations:
        organization_id = create_organization(
            conn, name=cast(Dict[str, str], org)["name"]
        ).id
        for user in org["users"]:
            user_id = create_user(conn, **user)  # type: ignore
            add_user_to_org(conn, user_id=user_id, organization_id=organization_id)
            set_active_organization(conn, user_id, organization_id)


@pytest.fixture(scope="function")
def conn(engine):
    conn = engine.connect()
    trans = conn.begin()
    try:
        insert_test_users_and_orgs(conn)
        yield conn
    finally:
        trans.rollback()
        conn.close()


from typing import Optional

from pydantic import UUID4


def get_current_user_org_override(
    *,
    user_id: int,
    organization_id: Optional[UUID4] = None,
    conn: Connection = Depends(get_connection),
) -> UserOrganization:
    """Return a particular existing user by id.

    This skips authentication of users to allow fake users.
    """
    user_res = conn.execute(
        text("SELECT * FROM users WHERE id = :id"), {"id": user_id}
    ).fetchone()
    user = User.from_orm(user_res)
    # Redis isn't available for tests so instead do this
    if organization_id is None:
        org = get_active_organization(conn, user.id)
    else:
        org = get_organization(conn, organization_id)
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
                get_current_user_org: partial(
                    get_current_user_org_override, user_id=user_id
                ),
                verify_token: lambda: {},
            }
        )

    return overrides
