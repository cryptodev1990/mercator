import random
import uuid
from string import ascii_letters, digits
from typing import Any, Dict, List, Optional, Tuple, cast
from unicodedata import name
from uuid import UUID

import pytest
import ruamel.yaml
from pydantic import UUID4
from sqlalchemy import delete, event, insert, select, text, update
from sqlalchemy.engine import Connection

from app.crud.namespaces import (
    NamespaceExistsError,
    NamespaceWithThisIdDoesNotExistError,
    NamespaceWithThisNameDoesNotExistError,
    create_namespace,
    delete_namespace,
    delete_namespace_by_name,
    get_default_namespace,
    get_namespace_by_id,
    get_namespace_by_name,
    update_namespace,
    update_namespace_by_name,
)
from app.crud.organization import (
    add_user_to_org,
    create_organization,
    get_active_organization,
    set_active_organization,
)
from app.crud.user import create_user as crud_create_user
from app.crud.user import get_user_by_email
from app.db.metadata import namespaces as namespaces_tbl
from app.db.metadata import organization_members as org_mbr_tbl
from app.db.metadata import organizations as org_tbl
from app.db.metadata import shapes as shapes_tbl
from app.db.metadata import users as users_tbl
from app.dependencies import set_app_user_settings
from app.schemas import Namespace

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


def setup_app_user(
    conn: Connection, user_id: int, organization_id: Optional[UUID4] = None
) -> Connection:
    if organization_id is None:
        organization_id = get_active_organization(conn, user_id).id
    set_app_user_settings(conn, user_id, cast(UUID, organization_id))
    return conn


def get_organizations(conn: Connection) -> List[UUID]:
    return [
        row.id for row in conn.execute(text("SELECT id FROM organizations")).fetchall()
    ]


def test_default_namespaces_created(conn):
    """Check that default namespaces were created for all organizations."""
    for org_id in get_organizations(conn):
        assert get_default_namespace(conn, org_id)


def get_alice_ids(conn: Connection) -> Tuple[int, UUID4]:
    user_id = get_user_by_email(conn, "alice@example.com").id
    org_id = get_active_organization(conn, user_id).id
    return user_id, cast(UUID4, org_id)


def test_create_namespace(conn: Connection):
    """Check that default namespaces were created for all organizations."""
    values: Dict[str, Any] = {"name": "Nomen", "properties": {"color": "red"}}
    user_id, organization_id = get_alice_ids(conn)
    namespace = create_namespace(
        conn, user_id=user_id, organization_id=organization_id, **values
    )
    assert isinstance(namespace.id, UUID)
    assert namespace.name == "Nomen"
    assert namespace.properties == values["properties"]


def test_create_namespace_error_if_existing(conn: Connection):
    """Check that default namespaces were created for all organizations."""
    values: Dict[str, Any] = {"name": "Default"}
    user_id, organization_id = get_alice_ids(conn)
    with pytest.raises(NamespaceExistsError):
        create_namespace(
            conn, user_id=user_id, organization_id=organization_id, **values
        )


def test_create_namespace_error_if_existing_2(conn):
    """Check that default namespaces were created for all organizations."""
    user_id, organization_id = get_alice_ids(conn)
    create_namespace(
        conn, user_id=user_id, organization_id=organization_id, name="Namespace 1"
    )
    with pytest.raises(NamespaceExistsError):
        create_namespace(
            conn,
            user_id=user_id,
            organization_id=organization_id,
            # make the actual names different
            name="NaMeSpaCE 1    ",
        )


def test_update_namespace(conn):
    """Check that update namespace works correctly."""
    user_id, organization_id = get_alice_ids(conn)
    namespace = create_namespace(
        conn, user_id=user_id, organization_id=organization_id, name="Namespace 1"
    )
    assert namespace.id
    namespace_update = update_namespace(
        conn,
        namespace.id,
        name="This was changed",
        properties={"Foo": 1, "Bar": "Hello"},
    )
    assert isinstance(namespace_update, Namespace)
    assert namespace.id == namespace_update.id
    assert namespace_update.name == "This was changed"
    assert namespace_update.properties == {"Foo": 1, "Bar": "Hello"}
    assert namespace_update.updated_at >= namespace.updated_at
    for a in ["created_at"]:
        assert getattr(namespace, a) == getattr(namespace_update, a)


def test_update_namespace_when_existing_name(conn):
    """Check that `update_namespace()` raises exception when new name exists."""
    user_id, organization_id = get_alice_ids(conn)
    namespace_1 = create_namespace(
        conn, user_id=user_id, organization_id=organization_id, name="Namespace 1"
    )
    namespace_2 = create_namespace(
        conn, user_id=user_id, organization_id=organization_id, name="Namespace 2"
    )
    with pytest.raises(NamespaceExistsError):
        update_namespace(conn, namespace_1.id, name=namespace_2.name)


def test_update_namespace_by_name(conn):
    """Check that update namespace by name works correctly."""
    user_id, organization_id = get_alice_ids(conn)
    namespace = create_namespace(
        conn, user_id=user_id, organization_id=organization_id, name="Namespace 1"
    )
    assert namespace.id
    namespace_update = update_namespace_by_name(
        conn,
        namespace.name,
        new_name="This was changed",
        properties={"Foo": 1, "Bar": "Hello"},
    )
    assert namespace.id == namespace_update.id
    assert namespace_update.name == "This was changed"
    assert namespace_update.properties == {"Foo": 1, "Bar": "Hello"}
    assert namespace_update.updated_at >= namespace.updated_at
    for a in ["created_at"]:
        assert getattr(namespace, a) == getattr(namespace_update, a)


def test_update_namespace_by_name_not_exists(conn):
    with pytest.raises(NamespaceWithThisNameDoesNotExistError):
        update_namespace_by_name(
            conn, "I have a name that doesn't exist", properties={"foo": 1}
        )


def test_update_namespace_by_name_to_existing_name(conn):
    user_id, organization_id = get_alice_ids(conn)
    namespace_1 = create_namespace(
        conn,
        user_id=user_id,
        organization_id=organization_id,
        name="Namespace 1",
    )
    namespace_2 = create_namespace(
        conn,
        user_id=user_id,
        organization_id=organization_id,
        name="Namespace 2",
    )
    with pytest.raises(NamespaceExistsError):
        update_namespace(conn, namespace_1.id, name=namespace_2.name)


def test_delete_namespace(conn):
    """Check that update namespace by name works correctly."""
    user_id, organization_id = get_alice_ids(conn)
    namespace_1 = create_namespace(
        conn,
        user_id=user_id,
        organization_id=organization_id,
        name="Namespace 1",
    )
    shapes = delete_namespace(conn, namespace_1.id)
    # TODO: add shapes
    assert shapes == []
    with pytest.raises(NamespaceWithThisIdDoesNotExistError):
        delete_namespace(conn, namespace_1.id)


def test_delete_namespace_by_name(conn):
    """Check that update namespace by name works correctly."""
    user_id, organization_id = get_alice_ids(conn)
    namespace_1 = create_namespace(
        conn,
        user_id=user_id,
        organization_id=organization_id,
        name="Namespace 1",
    )
    shapes = delete_namespace_by_name(conn, namespace_1.name)
    assert shapes == []
    # Check that it will raise error if deleted again
    with pytest.raises(NamespaceWithThisNameDoesNotExistError):
        delete_namespace_by_name(conn, namespace_1.name)


def test_get_namespace_by_id(conn):
    """Check that update namespace by name works correctly."""
    user_id, organization_id = get_alice_ids(conn)
    namespace_1 = create_namespace(
        conn,
        user_id=user_id,
        organization_id=organization_id,
        name="Namespace 1",
    )
    namespace_ret = get_namespace_by_id(conn, namespace_1.id)
    assert isinstance(namespace_ret, Namespace)
    for k in ("id", "name", "properties"):
        assert getattr(namespace_ret, k) == getattr(namespace_1, k)


def test_get_namespace_by_id_not_exists(conn):
    """Check that update namespace by name works correctly."""
    with pytest.raises(NamespaceWithThisIdDoesNotExistError):
        get_namespace_by_id(conn, uuid.UUID(int=0))


def test_get_namespace_by_name(conn):
    """Check that update namespace by name works correctly."""
    user_id, organization_id = get_alice_ids(conn)
    namespace_1 = create_namespace(
        conn,
        user_id=user_id,
        organization_id=organization_id,
        name="Namespace 1",
    )
    namespace_ret = get_namespace_by_name(conn, namespace_1.name)
    assert isinstance(namespace_ret, Namespace)
    for k in ("id", "name", "properties"):
        assert getattr(namespace_ret, k) == getattr(namespace_1, k)


def test_get_namespace_by_name_not_exists(conn):
    """Check that update namespace by name works correctly."""
    with pytest.raises(NamespaceWithThisNameDoesNotExistError):
        get_namespace_by_name(conn, "This is a name that definitely does not exist.")
