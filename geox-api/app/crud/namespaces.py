"""Namespace CRUD functions.

The CRUD functions here are written with the explicit parameters needed (columns, etc.)
rather than taking a pydantic model as an input.

The thought is that this will make it easier to reuse CRUD functions in prod and testing.
However, it may be more annoying than it is worth - so feel free to change later.

If it is easier to take a pydantic model as an input, we could make add a `data` argument that
would provide the extra arguments needed.

The functions are also written assuming the RLS is active. For example, the referencing a
namespace by name is assumed to provide one result, because an organization is set.

"""


import datetime
from tokenize import Name
from typing import Any, Dict, Generator, List, Optional, cast
from uuid import UUID

from pydantic import UUID4
from sqlalchemy import insert, select, text, update
from sqlalchemy.engine import Connection
from sqlalchemy.exc import IntegrityError

from app.db.metadata import namespaces as namespaces_tbl
from app.db.metadata import shapes as shapes_tbl
from app.schemas import Namespace


class NamespaceDoesNotExistError(Exception):
    """Namespace does not exist error."""

    pass


class NamespaceWithThisIdDoesNotExistError(NamespaceDoesNotExistError):
    """Namespace does not exist error."""

    def __init__(self, id_: UUID4) -> None:
        self.id_ = id_

    def __str__(self):
        return f"Namespace with id {self.id_} does not exist."


class NamespaceWithThisNameDoesNotExistError(NamespaceDoesNotExistError):
    """Namespace does not exist error."""

    def __init__(self, name: str) -> None:
        self.name = name

    def __str__(self):
        return f"Namespace with name '{self.name_}' does not exist."


class NamespaceExistsError(Exception):
    """Namespace already exists error."""

    def __init__(self, name: str, id_: UUID4) -> None:
        self.name = name
        self.id_ = id_

    def __str__(self):
        return f"Namespace {self.id_}, named '{self.name}' exists."


class DefaultNamespaceCannotBeRenamedError(Exception):
    """Namespace does not exist error."""

    def __init__(self, id_: UUID4) -> None:
        self.id = id_

    def __str__(self):
        return f"Namespace '{self.id_}' is the default namespace. Its name cannot be changed."


class DefaultNamespaceDoesNotExistError(Exception):
    """Namespace does not exist error."""

    def __init__(self, organization_id: UUID4) -> None:
        self.id = organization_id

    def __str__(self):
        return f"No default namespace exists for organization '{self.organization_id}'."


def name_normalizer(name: str) -> str:
    """Name normalizer.

    Strips whitespace from ends and converts to lowercase.
    """
    return name.strip().lower()


def _add_user_org_to_params(conn: Connection, params: Dict[str, Any]) -> Dict[str, Any]:
    # Modifies params in place
    user_id = params.get("user_id")
    org_id = params.get("organization_id")
    if not (user_id and org_id):
        app_user_and_org_stmt = text(
            "SELECT app_user_id() AS user_id, app_user_org() as organization_id"
        )
        app_user_and_org = conn.execute(app_user_and_org_stmt).first()
        params["user_id"] = user_id or app_user_and_org.user_id
        params["organization_id"] = org_id or app_user_and_org.organization_id
    return params


def select_namespaces(
    conn, id_: Optional[UUID4] = None, name: Optional[str] = None
) -> Generator[Namespace, None, None]:
    """Select namespaces by matching id or name."""
    n = namespaces_tbl
    stmt = select(n).where(n.c.deleted_at.is_(None)).order_by(n.c.created_at)  # type: ignore
    if name is not None:
        stmt = stmt.where(n.c.name_normalized == name_normalizer(str(name)))
    if id_ is not None:
        stmt = stmt.where(n.c.id == id_)
    for row in conn.execute(stmt):
        yield Namespace.from_orm(row)


def namespace_exists(conn, id_: UUID4, include_deleted: bool = False) -> bool:
    """Check whether a namespace exists or not."""
    stmt = select(namespaces_tbl.c.id).where(namespaces_tbl.c.id == id_)  # type: ignore
    if not include_deleted:
        stmt = stmt.where(namespaces_tbl.c.deleted_at.is_(None))
    res = conn.execute(stmt).first()
    return bool(res)


def get_namespace_by_id(conn, id_: UUID4, include_deleted: bool = False) -> Namespace:
    """Get a namespace by its id."""
    stmt = select(namespaces_tbl).where(namespaces_tbl.c.id == id_)  # type: ignore
    if not include_deleted:
        stmt = stmt.where(namespaces_tbl.c.deleted_at.is_(None))
    res = conn.execute(stmt).first()
    if res is None:
        raise NamespaceWithThisIdDoesNotExistError(id_)
    return Namespace.from_orm(res)


def get_namespace_by_name(
    conn,
    name: str,
) -> Namespace:
    """Get a namespace by its name."""
    name_normalized = name_normalizer(name)
    stmt = (
        select(namespaces_tbl)  # type: ignore
        .where(namespaces_tbl.c.deleted_at.is_(None))
        .where(namespaces_tbl.c.name_normalized == name_normalized)
    )
    res = conn.execute(stmt).first()
    if res is None:
        raise NamespaceWithThisNameDoesNotExistError(name_normalized)
    return Namespace.from_orm(res)


def get_default_namespace(conn, organization_id: UUID4) -> Namespace:
    """Return the default namespace of an organization."""
    stmt = text(
        """
        SELECT *
        FROM namespaces
        WHERE organization_id = :organization_id
            AND is_default
    """
    )
    values = {"organization_id": organization_id}
    res = conn.execute(stmt, values).first()
    if not res:
        raise DefaultNamespaceDoesNotExistError(organization_id)
    return Namespace.from_orm(res)


def create_namespace(
    conn: Connection,
    name: str,
    properties: Optional[Dict[str, Any]] = None,
    user_id: Optional[int] = None,
    organization_id: Optional[UUID4] = None,
) -> Namespace:
    """Create a new namespace."""
    name = name.strip()
    name_normalized = name_normalizer(name)
    stmt = insert(namespaces_tbl).returning(namespaces_tbl)
    params: Dict[str, Any] = {
        "name": name,
        "name_normalized": name_normalized,
        "properties": properties or {},
        "user_id": user_id,
        "organization_id": organization_id,
    }
    # If user_id and org_id are missing use the values of
    # app.user_id and app.user_org instead.
    params = _add_user_org_to_params(conn, params)
    # Use a SAVEPOINT to allow rollback in case of error
    # the entire connection is already wrapped in a transaction
    nested_trans = conn.begin_nested()
    try:
        res = conn.execute(stmt, params).first()
    except IntegrityError as exc:
        nested_trans.rollback()
        try:
            existing_namespace = get_namespace_by_name(conn, name)
        except NamespaceWithThisNameDoesNotExistError:
            # this shouldn't happen - so set the value to null and then when NamespaceExistsError
            # is raised, an exception for missing attribute errors will be raised - indicating
            # that something went horribly wrong
            existing_namespace = None
        raise NamespaceExistsError(
            cast(Namespace, existing_namespace).name,
            cast(Namespace, existing_namespace).id,
        )
    return Namespace.from_orm(res)


def update_namespace(
    conn: Connection,
    id_: UUID,
    name: Optional[str] = None,
    properties: Optional[Dict[str, Any]] = None,
) -> Namespace:
    """Update a namespace."""
    # See whether it exists - this could be handled impliclty by update -
    # but we need to also check other values.
    # This will raise values if the namespace does not exist.
    namespace = get_namespace_by_id(conn, id_)

    # Don't need user_id and organization_id. That is handled by RLS -
    # or it is an admin user and it doesn't matter.
    params: Dict[str, Any] = {}
    if name is not None:
        # check that the name does not exist - ideally the partial index should handle it
        # but it appears that it does not
        if namespace.is_default:
            raise DefaultNamespaceCannotBeRenamedError(id_)
        try:
            namespace_with_same_name = get_namespace_by_name(conn, name)
            raise NamespaceExistsError(
                namespace_with_same_name.name, namespace_with_same_name.id
            )
        except NamespaceWithThisNameDoesNotExistError:
            params["name"] = name
        params["normalized_name"] = name_normalizer(params["name"])
    if properties is not None:
        params["properties"] = properties
    stmt = (
        update(namespaces_tbl)
        .where(namespaces_tbl.c.id == id_)
        .where(namespaces_tbl.c.deleted_at.is_(None))
        .returning(namespaces_tbl)
    )
    nested_trans = conn.begin_nested()
    try:
        res = conn.execute(stmt, params).first()
    except IntegrityError as exc:
        # If the user didn't try to change the name ... then this error shouldn't have happend
        if params["name"] is None:
            raise exc
        # the user tried to change the name of a namespace when it already has a name
        try:
            nested_trans.rollback()
            existing_namespace = get_namespace_by_name(conn, params["name"])
            raise NamespaceExistsError(existing_namespace.name, existing_namespace.id)
        except NamespaceWithThisNameDoesNotExistError:
            # this shouldn't happen - so set the value to null and then when NamespaceExistsError
            # is raised, an exception for missing attribute errors will be raised - indicating
            # that something went horribly wrong
            raise exc
    # If None is returned - then no row was updated - meaning
    # that the namespace doesn't exist. However, we checked for existence
    # with get_namespace_by_id()
    return Namespace.from_orm(res)


def update_namespace_by_name(
    conn: Connection,
    name: str,
    new_name: Optional[str] = None,
    properties: Optional[Dict[str, Any]] = None,
) -> Namespace:
    """Update a namespace referencing it by its."""
    namespace = get_namespace_by_name(conn, name)
    return update_namespace(
        conn, id_=namespace.id, name=new_name, properties=properties
    )


def delete_namespace(conn: Connection, id_: UUID4) -> List[UUID4]:
    """Delete a namespace.

    Returns:
        A list of the associated shapes that were deleted.

    """
    now = datetime.datetime.utcnow()
    params = {"deleted_at": now}
    del_namespace_stmt = (
        update(namespaces_tbl)
        .values(deleted_at=now)
        .where(namespaces_tbl.c.id == id_)
        .where(
            namespaces_tbl.c.deleted_at.is_(None)
        )  # cannot delete a namespace that already was deleted
        .returning(namespaces_tbl.c.id)
    )
    res = conn.execute(del_namespace_stmt, params).first()
    # If nothing is returned then no rows were updated, which means that no namespace
    # has that ID
    if res is None:
        raise NamespaceWithThisIdDoesNotExistError(id_)
    # Delete all shapes with that namespace
    del_shapes_stmt = (
        update(shapes_tbl)
        .where(shapes_tbl.c.namespace_id == id_)
        .where(shapes_tbl.c.deleted_at.is_(None))
        .returning(shapes_tbl.c.uuid)
    )
    shapes_deleted = [
        row.uuid for row in conn.execute(del_shapes_stmt, params).fetchall()
    ]
    return shapes_deleted


def delete_namespace_by_name(conn: Connection, name: str) -> List[UUID4]:
    """Delete a namespace by its name."""
    namespace = get_namespace_by_name(conn, name)
    return delete_namespace(conn, namespace.id)
