"""Utility to create a common test organization and some users"""
from typing import Dict, Optional, Tuple, cast

import random
from uuid import UUID
from pydantic import UUID4
import pytest
import ruamel.yaml

from string import ascii_letters, digits

from sqlalchemy.engine import Connection

from app.crud.user import create_user as crud_create_user, get_user_by_email
from app.crud.organization import add_user_to_org, create_organization, get_active_organization, set_active_organization
from app.dependencies import set_app_user_settings


yaml = ruamel.yaml.YAML(typ="safe")


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
            add_user_to_org(conn, user_id=user_id,
                            organization_id=organization_id)
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


def setup_app_user(
    conn: Connection, user_id: int, organization_id: Optional[UUID4] = None
) -> Connection:
    if organization_id is None:
        organization_id = get_active_organization(conn, user_id).id
    set_app_user_settings(conn, user_id, cast(UUID, organization_id))
    return conn


def get_alice_ids(conn: Connection) -> Tuple[int, UUID4]:
    user_id = get_user_by_email(conn, "alice@example.com").id
    org_id = get_active_organization(conn, user_id).id
    return user_id, cast(UUID4, org_id)
