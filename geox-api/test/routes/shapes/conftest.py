"""Common fixtures."""
from functools import partial
from typing import Optional

import pytest
from fastapi import status
from geojson.utils import generate_random as generate_random_geometry
from geojson_pydantic import Feature
from pydantic import UUID4
from pytest_fastapi_deps import DependencyOverrider
from randomname import get_name as get_random_name
from sqlalchemy.engine import Connection

from app.crud.organization import get_active_organization
from app.crud.user import get_user_by_email
from app.dependencies import get_connection, get_current_user_org, verify_token
from app.main import app
from app.schemas import BaseModel, User, UserOrganization
from app.schemas.organizations import Organization

from ..conftest import get_connection_override, get_current_user_org_override


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
                get_current_user_org: partial(
                    get_current_user_org_override,
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


def random_geojson(include_name=True):
    if include_name:
        name = get_random_name()
    else:
        name = None
    return Feature(
        geometry=generate_random_geometry("Polygon", numberVertices=4),
        properties={"name": name},
    )
