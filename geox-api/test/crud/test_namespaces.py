import uuid
from contextlib import contextmanager
from pathlib import Path
from tkinter.font import names
from tokenize import Name
from typing import Any, Dict, Generator, List, Optional, cast
from unicodedata import name
from uuid import UUID

import pytest
import ruamel.yaml
from pydantic import UUID4
from sqlalchemy import delete, insert, select, text, update
from sqlalchemy.engine import Connection, Engine


from typing import Tuple, Callable
from typing import Literal
from sqlalchemy import event

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
from app.crud.organization import get_active_org, set_active_org
from app.db.engine import create_app_engine
from app.db.metadata import common, namespaces as namespaces_tbl
from app.db.metadata import organization_members as org_mbr_tbl
from app.db.metadata import organizations as org_tbl
from app.db.metadata import shapes as shapes_tbl
from app.db.metadata import users as users_tbl
from app.dependencies import set_app_user_settings
from app.schemas import Namespace


from sqlalchemy.engine import Transaction

yaml = ruamel.yaml.YAML(typ="safe")


@pytest.fixture(scope="module")
def engine() -> Engine:
    return create_app_engine()


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


def cleanup_db(conn: Connection) -> None:
    for tbl in (shapes_tbl, org_mbr_tbl, org_tbl, users_tbl):
        conn.execute(delete(tbl))


def load_data(conn: Connection, test_data: Dict[str, Any]) -> None:
    conn.execute(insert(users_tbl), test_data["users"])  # type: ignore
    conn.execute(insert(org_tbl), test_data["organizations"])  # type: ignore
    for org_member in test_data["organization_members"]:
        conn.execute(insert(org_mbr_tbl), org_member)  # type: ignore
        # Set these new organizations to the active organization
        set_active_org(conn, org_member["user_id"], org_member["organization_id"])
    for row in test_data["shapes"]:
        data = {
            **row,
            "namespace_id": get_default_namespace(
                conn, UUID(row["organization_id"])
            ).id,
        }
        conn.execute(insert(shapes_tbl), data)  # type: ignore


@pytest.fixture()
def connection(engine, test_data: Dict[str, Any]):
    with engine.connect() as conn:
        trans = conn.begin()
        try:
            cleanup_db(conn)
            load_data(conn, test_data)
            yield conn
        finally:
            trans.rollback()


def setup_app_user(
    conn: Connection, user_id: int, organization_id: Optional[UUID4] = None
) -> Connection:
    if organization_id is None:
        organization_id = get_active_org(conn, user_id, use_cache=False)
    set_app_user_settings(conn, user_id, cast(UUID, organization_id))
    return conn


def get_organizations(conn: Connection) -> List[UUID]:
    return [
        row.id for row in conn.execute(text("SELECT id FROM organizations")).fetchall()
    ]


def test_default_namespaces_created(connection):
    """Check that default namespaces were created for all organizations."""
    for org_id in get_organizations(connection):
        assert get_default_namespace(connection, org_id)


def test_create_namespace(connection):
    """Check that default namespaces were created for all organizations."""
    values = {"name": "Nomen", "properties": {"color": "red"}}
    user_id = 1
    organization_id = get_active_org(connection, user_id, use_cache=False)
    namespace = create_namespace(
        connection, user_id=user_id, organization_id=organization_id, **values
    )
    assert isinstance(namespace.id, UUID)
    assert namespace.name == "Nomen"
    assert namespace.properties == values["properties"]


def test_create_namespace_error_if_existing(connection):
    """Check that default namespaces were created for all organizations."""
    values = {"name": "Default"}
    user_id = 1
    organization_id = get_active_org(connection, user_id, use_cache=False)
    with pytest.raises(NamespaceExistsError):
        create_namespace(
            connection, user_id=user_id, organization_id=organization_id, **values
        )


def test_create_namespace_error_if_existing_2(connection):
    """Check that default namespaces were created for all organizations."""
    user_id = 1
    organization_id = get_active_org(connection, user_id, use_cache=False)
    create_namespace(
        connection, user_id=user_id, organization_id=organization_id, name="Namespace 1"
    )
    with pytest.raises(NamespaceExistsError):
        create_namespace(
            connection,
            user_id=user_id,
            organization_id=organization_id,
            # make the actual names different
            name="NaMeSpaCE 1    ",
        )


def test_update_namespace(connection):
    """Check that update namespace works correctly."""
    user_id = 1
    organization_id = get_active_org(connection, user_id, use_cache=False)
    namespace = create_namespace(
        connection, user_id=user_id, organization_id=organization_id, name="Namespace 1"
    )
    assert namespace.id
    namespace_update = update_namespace(
        connection,
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


def test_update_namespace_when_existing_name(connection):
    """Check that `update_namespace()` raises exception when new name exists."""
    user_id = 1
    organization_id = get_active_org(connection, user_id, use_cache=False)
    namespace_1 = create_namespace(
        connection, user_id=user_id, organization_id=organization_id, name="Namespace 1"
    )
    namespace_2 = create_namespace(
        connection, user_id=user_id, organization_id=organization_id, name="Namespace 2"
    )
    with pytest.raises(NamespaceExistsError):
        update_namespace(connection, namespace_1.id, name=namespace_2.name)


def test_update_namespace_by_name(connection):
    """Check that update namespace by name works correctly."""
    user_id = 1
    organization_id = get_active_org(connection, user_id, use_cache=False)
    namespace = create_namespace(
        connection, user_id=user_id, organization_id=organization_id, name="Namespace 1"
    )
    assert namespace.id
    namespace_update = update_namespace_by_name(
        connection,
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


def test_update_namespace_by_name_not_exists(connection):
    with pytest.raises(NamespaceWithThisNameDoesNotExistError):
        update_namespace_by_name(
            connection, "I have a name that doesn't exist", properties={"foo": 1}
        )


def test_update_namespace_by_name_to_existing_name(connection):
    user_id = 1
    organization_id = get_active_org(connection, user_id, use_cache=False)
    namespace_1 = create_namespace(
        connection,
        user_id=user_id,
        organization_id=organization_id,
        name="Namespace 1",
    )
    namespace_2 = create_namespace(
        connection,
        user_id=user_id,
        organization_id=organization_id,
        name="Namespace 2",
    )
    with pytest.raises(NamespaceExistsError):
        update_namespace(connection, namespace_1.id, name=namespace_2.name)


def test_delete_namespace(connection):
    """Check that update namespace by name works correctly."""
    user_id = 1
    organization_id = get_active_org(connection, user_id, use_cache=False)
    namespace_1 = create_namespace(
        connection,
        user_id=user_id,
        organization_id=organization_id,
        name="Namespace 1",
    )
    shapes = delete_namespace(connection, namespace_1.id)
    # TODO: add shapes
    assert shapes == []
    with pytest.raises(NamespaceWithThisIdDoesNotExistError):
        delete_namespace(connection, namespace_1.id)


def test_delete_namespace_by_name(connection):
    """Check that update namespace by name works correctly."""
    user_id = 1
    organization_id = get_active_org(connection, user_id, use_cache=False)
    namespace_1 = create_namespace(
        connection,
        user_id=user_id,
        organization_id=organization_id,
        name="Namespace 1",
    )
    shapes = delete_namespace_by_name(connection, namespace_1.name)
    assert shapes == []
    # Check that it will raise error if deleted again
    with pytest.raises(NamespaceWithThisNameDoesNotExistError):
        delete_namespace_by_name(connection, namespace_1.name)


def test_get_namespace_by_id(connection):
    """Check that update namespace by name works correctly."""
    user_id = 1
    organization_id = get_active_org(connection, user_id, use_cache=False)
    namespace_1 = create_namespace(
        connection,
        user_id=user_id,
        organization_id=organization_id,
        name="Namespace 1",
    )
    namespace_ret = get_namespace_by_id(connection, namespace_1.id)
    assert isinstance(namespace_ret, Namespace)
    for k in ("id", "name", "properties"):
        assert getattr(namespace_ret, k) == getattr(namespace_1, k)


def test_get_namespace_by_id_not_exists(connection):
    """Check that update namespace by name works correctly."""
    with pytest.raises(NamespaceWithThisIdDoesNotExistError):
        get_namespace_by_id(connection, uuid.UUID(int=0))


def test_get_namespace_by_name(connection):
    """Check that update namespace by name works correctly."""
    user_id = 1
    organization_id = get_active_org(connection, user_id, use_cache=False)
    namespace_1 = create_namespace(
        connection,
        user_id=user_id,
        organization_id=organization_id,
        name="Namespace 1",
    )
    namespace_ret = get_namespace_by_name(connection, namespace_1.name)
    assert isinstance(namespace_ret, Namespace)
    for k in ("id", "name", "properties"):
        assert getattr(namespace_ret, k) == getattr(namespace_1, k)


def test_get_namespace_by_name_not_exists(connection):
    """Check that update namespace by name works correctly."""
    with pytest.raises(NamespaceWithThisNameDoesNotExistError):
        get_namespace_by_name(
            connection, "This is a name that definitely does not exist."
        )
