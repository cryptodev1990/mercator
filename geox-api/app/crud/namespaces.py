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
import logging
from typing import Any, Dict, Generator, List, Optional, cast
from uuid import UUID

from pydantic import UUID4  # pylint: disable=no-name-in-module
from slugify import slugify
from sqlalchemy import select, text, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.engine import Connection
from sqlalchemy.exc import IntegrityError

from app.core.logging import get_logger
from app.core.stats import time_db_query
from app.db.metadata import namespaces as namespaces_tbl
from app.db.metadata import shapes as shapes_tbl
from app.schemas import Namespace
from fastapi.encoders import jsonable_encoder
from app.schemas import Namespace, NamespaceCreate, NamespaceUpdate, RequestErrorModel

logger = get_logger(__name__)


class NamespaceDoesNotExistError(Exception):
    """Namespace does not exist error."""


class NamespaceWithThisIdDoesNotExistError(NamespaceDoesNotExistError):
    """Namespace does not exist error."""

    def __init__(self, id_: UUID4) -> None:
        self.id_ = id_

    def __str__(self):
        return f"Namespace with id {self.id_} does not exist."


class NamespaceWithThisSlugDoesNotExistError(NamespaceDoesNotExistError):
    """Namespace does not exist error."""

    def __init__(self, slug: str) -> None:
        self.slug = slug

    def __str__(self):
        return f"Namespace with slug '{self.slug}' does not exist."


class NamespaceExistsError(Exception):
    """Namespace already exists error."""

    def __init__(self, name: str, slug: str, id_: UUID4) -> None:
        self.name = name
        self.slug = slug
        self.id_ = id_

    def __str__(self):
        return f"Namespace {self.id_}, name='{self.name}', slug='{self.slug}' exists."


class DefaultNamespaceCannotBeRenamedError(Exception):
    """Namespace does not exist error."""

    def __init__(self, id_: UUID4) -> None:
        self.id = id_

    def __str__(self):
        return (
            f"Namespace '{self.id}' is the default namespace. Its name cannot be changed."
        )


class DefaultNamespaceDoesNotExistError(Exception):
    """Namespace does not exist error."""

    def __init__(self, organization_id: UUID4) -> None:
        self.id = organization_id

    def __str__(self):
        return f"No default namespace exists for organization '{self.id}'."


def _add_user_org_to_params(conn: Connection, params: Dict[str, Any]) -> Dict[str, Any]:
    # Modifies params in place
    user_id = params.get("user_id")
    org_id = params.get("organization_id")
    if not (user_id and org_id):
        app_user_and_org_stmt = text(
            "SELECT app_user_id() AS user_id, app_user_org() as organization_id"
        )
        with time_db_query("get_app_user_and_org"):
            app_user_and_org = conn.execute(app_user_and_org_stmt).first()
        params["user_id"] = user_id or app_user_and_org.user_id
        params["organization_id"] = org_id or app_user_and_org.organization_id
    return params


_select_namespaces = select(namespaces_tbl).where(  # type: ignore
    namespaces_tbl.c.deleted_at.is_(None)
)


def slugify_name(name: str) -> str:
    return slugify(name)


def select_namespaces(
    conn,
    id_: Optional[UUID4] = None,
    name: Optional[str] = None,
    slug: Optional[str] = None,
) -> Generator[Namespace, None, None]:
    """Select namespaces by matching id or name."""
    n = namespaces_tbl
    stmt = _select_namespaces.order_by(n.c.created_at)  # type: ignore
    if id_ is not None:
        stmt = stmt.where(n.c.id == id_)
    if name is not None:
        stmt = stmt.where(n.c.name == name)
    if slug is not None:
        stmt = stmt.where(n.c.slug == slug)
    with time_db_query("select_namespaces"):
        rows = conn.execute(stmt)
    for row in rows:
        yield Namespace.from_orm(row)


def namespace_exists(conn, id_: UUID4, include_deleted: bool = False) -> bool:
    """Check whether a namespace exists or not."""
    stmt = select(namespaces_tbl.c.id).where(namespaces_tbl.c.id == id_)  # type: ignore
    if not include_deleted:
        stmt = stmt.where(namespaces_tbl.c.deleted_at.is_(None))
    with time_db_query("namespace_exists"):
        res = conn.execute(stmt).first()
    return bool(res)


def get_namespace(conn, id_: UUID4, include_deleted: bool = False) -> Namespace:
    """Get a namespace by its id."""
    stmt = select(namespaces_tbl).where(namespaces_tbl.c.id == id_)  # type: ignore
    if not include_deleted:
        stmt = stmt.where(namespaces_tbl.c.deleted_at.is_(None))
    with time_db_query("get_namespace"):
        res = conn.execute(stmt).first()
    if res is None:
        raise NamespaceWithThisIdDoesNotExistError(id_)
    return Namespace.from_orm(res)


def get_namespace_by_slug(
    conn, slug: str, organization_id: Optional[UUID4] = None
) -> Namespace:
    """Get a namespace by its id."""
    # No include_deleted because slug is unique only for undeleted namespaces
    stmt = select(namespaces_tbl).where(namespaces_tbl.c.slug == slug)  # type: ignore
    if organization_id is not None:
        stmt = stmt.where(namespaces_tbl.c.organization_id == organization_id)
    with time_db_query("get_namespace_by_slug"):
        res = conn.execute(stmt).first()
    if res is None:
        raise NamespaceWithThisSlugDoesNotExistError(slug)
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
    with time_db_query("get_default_namespace"):
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
    slug = slugify_name(name)
    stmt = insert(namespaces_tbl).returning(namespaces_tbl)
    params: Dict[str, Any] = {
        "name": name,
        "slug": slug,
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
        with time_db_query("create_namespace"):
            res = conn.execute(stmt, params).first()
    except IntegrityError:
        nested_trans.rollback()
        try:
            existing_namespace = get_namespace_by_slug(conn, slug)
        except NamespaceWithThisSlugDoesNotExistError:
            # this shouldn't happen - so set the value to null and then when NamespaceExistsError
            # is raised, an exception for missing attribute errors will be raised - indicating
            # that something went horribly wrong
            existing_namespace = None
        raise NamespaceExistsError(
            cast(Namespace, existing_namespace).name,
            cast(Namespace, existing_namespace).slug,
            cast(Namespace, existing_namespace).id,
        ) from None
    return Namespace.from_orm(res)

def delete_none(_dict):
    """Delete None values recursively from all of the dictionaries"""
    for key, value in list(_dict.items()):
        if isinstance(value, dict):
            delete_none(value)
        elif value is None:
            del _dict[key]
        elif isinstance(value, list):
            for v_i in value:
                if isinstance(v_i, dict):
                    delete_none(v_i)

    return _dict


def update_namespace(
    conn: Connection,
    id_: UUID,
    data: NamespaceUpdate,
) -> Namespace:
    """Update a namespace."""
    values: Dict[str, Any] = {}
    # See whether it exists - this could be handled impliclty by update -
    # but we need to also check other values.
    # This will raise values if the namespace does not exist.
    namespace = get_namespace(conn, id_)

    if namespace.is_default and "name" in data:
        raise DefaultNamespaceCannotBeRenamedError(id_)
    # check that the slug does not exist - ideally the partial index should handle it
    # but it appears that it does not
    # slug = slugify_name(namespace.name)
    # try:
    #     namespace_with_slug = get_namespace_by_slug(conn, slug)
    #     raise NamespaceExistsError(
    #         namespace_with_slug.name,
    #         namespace_with_slug.slug,
    #         namespace_with_slug.id,
    #     )
    # except NamespaceWithThisSlugDoesNotExistError:
    #     pass
    values = delete_none(jsonable_encoder(data))


    stmt = (
        update(namespaces_tbl).where(namespaces_tbl.c.id == id_).returning(namespaces_tbl)
    )
    nested_trans = conn.begin_nested()
    try:
        with time_db_query("update_namespace"):
            res = conn.execute(stmt, values).first()
    except IntegrityError as exc:
        # If the user didn't try to change the name ... then this error shouldn't have happend
        # and we have a bigger problem that we need to log
        if values["slug"] is None:
            raise exc
        # the user tried to change the name of a namespace when it already has a name
        try:
            nested_trans.rollback()
            existing_namespace = get_namespace_by_slug(conn, values["slug"])
            raise NamespaceExistsError(
                existing_namespace.name, existing_namespace.slug, existing_namespace.id
            ) from None
        except NamespaceWithThisSlugDoesNotExistError:
            # this shouldn't happen - so set the value to null and then when NamespaceExistsError
            # is raised, an exception for missing attribute errors will be raised - indicating
            # that something went horribly wrong
            raise exc from exc
    # If None is returned - then no row was updated - meaning
    # that the namespace doesn't exist. However, we checked for existence
    # with get_namespace()
    return Namespace.from_orm(res)


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
    with time_db_query("delete_namespace"):
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
    with time_db_query("delete_namespace_shapes"):
        rows = conn.execute(del_shapes_stmt, params).fetchall()
    shapes_deleted = [row.uuid for row in rows]
    return shapes_deleted
