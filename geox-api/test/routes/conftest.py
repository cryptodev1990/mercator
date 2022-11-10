# pylint: disable=redefined-outer-name,duplicate-code
"""Common functions and fixtures used in testing API routes."""
import uuid
from functools import partial
from typing import Callable, Dict, Generator, List, Optional, TypedDict, cast

import pytest
from fastapi import Depends
from fastapi.testclient import TestClient
from pydantic import Field
from pydantic.types import UUID4  # pylint: disable=no-name-in-module
from pytest_fastapi_deps import DependencyOverrider
from sqlalchemy import text
from sqlalchemy.engine import Connection

from app.crud.namespaces import create_namespace, get_default_namespace
from app.crud.organization import (
    add_user_to_org,
    create_organization,
    get_active_organization,
    get_organization,
    set_active_organization,
)
from app.crud.user import create_user as crud_create_user
from app.crud.user import get_user_by_email
from app.dependencies import get_connection, get_current_user_org, verify_token
from app.main import app
from app.schemas import GeoShape, Namespace, Organization, User, UserOrganization


@pytest.fixture(scope="module")
def client() -> TestClient:
    return TestClient(app)


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


def get_unused_namespace_id(conn: Connection) -> UUID4:
    """Return a shape UUID that does not exist yet."""
    ids = set(conn.execute(text("SELECT id from namespaces")).scalars())
    while (id_not_exist := uuid.uuid4()) in ids:
        pass
    return id_not_exist


def get_unused_shape_id(conn: Connection) -> UUID4:
    """Return a namespace UUID that does not exist yet."""
    ids = set(conn.execute(text("SELECT uuid from shapes")).scalars())
    while (id_not_exist := uuid.uuid4()) in ids:
        pass
    return id_not_exist


def get_user_org_by_email(conn: Connection, email: str) -> UserOrganization:
    user = get_user_by_email(conn, email)
    org = get_active_organization(conn, user.id)
    return UserOrganization(user=user, organization=org)


@pytest.fixture(scope="function")
def conn(engine) -> Generator[Connection, None, None]:
    conn = engine.connect()
    trans = conn.begin()
    try:
        yield conn
    finally:
        # This always rollsback the changes so the database state stays clean
        trans.rollback()
        conn.close()


class _UserData(TypedDict):
    name: str
    email: str
    sub_id: str
    iss: str
    namespaces: List[str]


class _OrgData(TypedDict):
    name: str
    users: List[_UserData]


ORGANIZATIONS: List[_OrgData] = [
    {
        "name": "example.com",
        "users": [
            {
                "name": "Alice",
                "email": "alice@example.com",
                "sub_id": "ehTL6xNQ8Dm2fZ380T9305fewiRJzbAz3@clients",
                "iss": "notarealissuer.example.com",
                "namespaces": ["New namespace"],
            },
            {
                "name": "Bob",
                "email": "bob@example.com",
                "sub_id": "W90rxiUvFUZBmZN6BkfFfXY8XMHmxOgd@clients",
                "iss": "notarealissuer.example.com",
                "namespaces": [],
            },
        ],
    },
    {
        "name": "example.net",
        "users": [
            {
                "name": "Carlos",
                "email": "carlos@example.net",
                "sub_id": "k7p6zN93a8NBlCjdmhCticEkIWLol74i@clients",
                "iss": "notarealissuer.example.com",
                "namespaces": [],
            }
        ],
    },
]


class DbExampleUser(User):
    organization: "DbExampleOrg"


class DbExampleOrg(Organization):
    users: Dict[str, DbExampleUser] = Field(default_factory=dict)
    namespaces: Dict[str, Namespace] = Field(default_factory=dict)

    @property
    def default_namespace(self) -> Namespace:
        return self.namespaces["default"]


DbExampleUser.update_forward_refs()


# pylint: disable=unused-argument
def create_user(
    conn: Connection, *, email: str, name: str, sub_id: str, iss: str, **kwargs
) -> User:
    user = crud_create_user(
        conn, email=email, name=name, nickname=name, sub_id=sub_id, iss=iss
    )
    return user


# pylint: enable=unused-argument


class ExampleDbAbc:
    def __init__(self, conn: Connection, data: List[_OrgData]) -> None:
        self.conn = conn
        self.organizations: Dict[str, DbExampleOrg] = {}
        self.shapes: Dict[str, GeoShape] = {}
        for o in data:
            org = DbExampleOrg.from_orm(
                create_organization(conn, name=cast(Dict[str, str], o)["name"])
            )
            org.namespaces["default"] = get_default_namespace(conn, org.id)
            for u in o.get("users", []):
                user = create_user(conn, **u, organization=org)  # type: ignore
                add_user_to_org(conn, user_id=user.id, organization_id=org.id)
                set_active_organization(conn, user.id, org.id)
                org.users[user.email] = DbExampleUser(**user.dict(), organization=org)
                namespaces = u.get("namespaces", [])
                if namespaces:
                    for n in namespaces:
                        namespace = create_namespace(
                            conn, name=n, user_id=user.id, organization_id=org.id
                        )
                        org.namespaces[namespace.slug] = namespace
            self.organizations[org.name] = org

    @property
    def alice(self) -> DbExampleUser:
        return self["example.com"].users["alice@example.com"]

    @property
    def bob(self) -> DbExampleUser:
        return self["example.com"].users["bob@example.com"]

    @property
    def carlos(self) -> DbExampleUser:
        return self["example.net"].users["carlos@example.net"]

    def __getitem__(self, name: str) -> DbExampleOrg:
        return self.organizations[name]

    # pylint: disable=redefined-outer-name
    def dep_overrides(self) -> DependencyOverrider:
        return DependencyOverrider(
            app,
            {
                get_connection: get_connection_override(self.conn),
                get_current_user_org: partial(
                    get_current_user_org_override, user_id=self.alice.id
                ),
                verify_token: lambda: {},
            },
        )


@pytest.fixture(scope="function")
def abc_example_data(conn: Connection) -> ExampleDbAbc:
    return ExampleDbAbc(conn, ORGANIZATIONS)


@pytest.fixture(scope="function")
def db(abc_example_data: ExampleDbAbc) -> Generator[ExampleDbAbc, None, None]:
    # Overrides fastapi dependencies
    with abc_example_data.dep_overrides():
        yield abc_example_data
