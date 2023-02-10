# pylint: disable=redefined-outer-name
import uuid
from test.crud.common import get_alice_ids, insert_test_users_and_orgs
from typing import Any, Dict, List
from uuid import UUID

import pytest
from sqlalchemy import text
from sqlalchemy.engine import Connection

from app.crud.namespaces import (
    NamespaceExistsError,
    NamespaceWithThisIdDoesNotExistError,
    NamespaceWithThisSlugDoesNotExistError,
    create_namespace,
    delete_namespace,
    get_default_namespace,
    get_namespace,
    get_namespace_by_slug,
    update_namespace,
)
from app.schemas import Namespace, NamespaceUpdate


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


def get_organizations(conn: Connection) -> List[UUID]:
    return [
        row.id for row in conn.execute(text("SELECT id FROM organizations")).fetchall()
    ]


def test_default_namespaces_created(conn):
    """Check that default namespaces were created for all organizations."""
    for org_id in get_organizations(conn):
        assert get_default_namespace(conn, org_id)


def test_create_namespace(conn: Connection):
    """Check that default namespaces were created for all organizations."""
    values: Dict[str, Any] = {
        "name": "Nomen",
        "properties": {"color": "red"},
    }
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
        create_namespace(conn, user_id=user_id, organization_id=organization_id, **values)


def test_create_namespace_error_if_existing_2(conn):
    """Check that default namespaces were created for all organizations."""
    user_id, organization_id = get_alice_ids(conn)
    create_namespace(
        conn,
        user_id=user_id,
        organization_id=organization_id,
        name="Namespace 1",
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
        conn,
        user_id=user_id,
        organization_id=organization_id,
        name="Namespace 1",
    )
    assert namespace.id
    data = NamespaceUpdate(name="This was changed", properties={"color": {"r": 255, "g": 0, "b": 0}})
    namespace_update = update_namespace(
        conn,
        namespace.id,
        data
    )
    assert isinstance(namespace_update, Namespace)
    assert namespace.id == namespace_update.id
    assert namespace_update.name == "This was changed"
    assert namespace_update.slug == "this-was-changed"
    assert namespace_update.properties == {"color": {"r": 255, "g": 0, "b": 0}}
    assert namespace_update.updated_at >= namespace.updated_at
    for a in ["created_at"]:
        assert getattr(namespace, a) == getattr(namespace_update, a)


def test_update_namespace_when_existing_name(conn):
    """Check that `update_namespace()` raises exception when new slug exists."""
    user_id, organization_id = get_alice_ids(conn)
    namespace_1 = create_namespace(
        conn,
        user_id=user_id,
        organization_id=organization_id,
        name="Namespace 1",
    )
    create_namespace(
        conn,
        user_id=user_id,
        organization_id=organization_id,
        name="Namespace 2",
    )
    with pytest.raises(NamespaceExistsError):
        data = NamespaceUpdate(name="Namespace 2")
        update_namespace(conn, namespace_1.id, data)


def test_delete_namespace(conn):
    """Check that deleting a namespace works correctly."""
    user_id, organization_id = get_alice_ids(conn)
    namespace_1 = create_namespace(
        conn,
        user_id=user_id,
        organization_id=organization_id,
        name="Namespace 1",
    )
    shapes = delete_namespace(conn, namespace_1.id)
    assert shapes == []
    with pytest.raises(NamespaceWithThisIdDoesNotExistError):
        delete_namespace(conn, namespace_1.id)


def test_get_namespace_by_id(conn):
    """Check that update namespace by name works correctly."""
    user_id, organization_id = get_alice_ids(conn)
    namespace_1 = create_namespace(
        conn,
        user_id=user_id,
        organization_id=organization_id,
        name="Namespace 1",
    )
    namespace_ret = get_namespace(conn, namespace_1.id)
    assert isinstance(namespace_ret, Namespace)
    for k in ("id", "name", "properties"):
        assert getattr(namespace_ret, k) == getattr(namespace_1, k)


def test_get_namespace_by_id_not_exists(conn):
    """Check that update namespace by name works correctly."""
    with pytest.raises(NamespaceWithThisIdDoesNotExistError):
        get_namespace(conn, uuid.UUID(int=0))


def test_get_namespace_by_slug(conn):
    """Check that update namespace by name works correctly."""
    user_id, organization_id = get_alice_ids(conn)
    namespace_1 = create_namespace(
        conn,
        user_id=user_id,
        organization_id=organization_id,
        name="New Namespace",
    )
    namespace_ret = get_namespace_by_slug(conn, namespace_1.slug)
    assert isinstance(namespace_ret, Namespace)
    for k in ("id", "name", "properties"):
        assert getattr(namespace_ret, k) == getattr(namespace_1, k)


def test_get_namespace_by_slug_not_exists(conn):
    """Check that update namespace by name works correctly."""
    with pytest.raises(NamespaceWithThisSlugDoesNotExistError):
        get_namespace_by_slug(conn, "sgasgdgsa-asgsdgsa-asdgasgsa-adgasdgsa-agsdgsg")


def test_namespace_can_have_a_deleted_name(conn):
    """Check that a new namespace can have the same namey."""
    user_id, organization_id = get_alice_ids(conn)
    namespace_1 = create_namespace(
        conn,
        user_id=user_id,
        organization_id=organization_id,
        name="New namespace",
    )
    delete_namespace(conn, namespace_1.id)
    namespace_2 = create_namespace(
        conn,
        user_id=user_id,
        organization_id=organization_id,
        name="New namespace",
    )
    assert namespace_2.slug == "new-namespace"
