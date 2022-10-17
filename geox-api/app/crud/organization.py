"""CRUD functions for organizations."""
from ast import Or
from typing import Literal, Optional

from pydantic import UUID4
from sqlalchemy import insert, select, text
from sqlalchemy.engine import Connection

from app.db.metadata import organization_members as org_mbr_tbl
from app.db.metadata import organizations as org_tbl
from app.schemas import Organization


class OrganizationDoesNotExistError(Exception):
    def __init__(self, id_: UUID4) -> None:
        self.id = id_

    def __str__(self) -> str:
        return f"Organization {self.id} does not exist."


class UserHasNoActiveOrganizationError(Exception):
    def __init__(self, id_: int) -> None:
        self.id = id_

    def __str__(self) -> str:
        return f"User {self.id} has no active organization."


class UserHasNoPersonalOrganizationError(Exception):
    def __init__(self, id_: int) -> None:
        self.id = id_

    def __str__(self) -> str:
        return f"User {self.id} has no personal organization."


class UserNotInOrgError(Exception):
    def __init__(self, user_id: int, organization_id: UUID4) -> None:
        self.user_id = user_id
        self.organization_id = organization_id

    def __str__(self) -> str:
        return f"User {self.user_id} is not in organization {self.organization_id}"


def create_organization(conn: Connection, *, name: str) -> Organization:
    stmt = insert(org_tbl).returning(org_tbl)
    res = conn.execute(stmt, {"name": name}).first()
    return Organization.from_orm(res)


def organization_exists(conn: Connection, organization_id: UUID4) -> bool:
    stmt = text("SELECT 1 FROM organizations WHERE id = :id")
    res = conn.execute(stmt, {"id": organization_id}).scalar()
    return bool(res)


def get_organization(conn: Connection, organization_id: UUID4) -> Organization:
    """Get an organization by id.

    Returns:
        An organization with that id. If there is no such organization,
        then ``None`` is returned. It is up to caller to handle ``None``
        values.

    """
    stmt = select(org_tbl).where(org_tbl.c.id == organization_id)  # type: ignore
    res = conn.execute(stmt, {"id": organization_id}).first()
    if res is None:
        raise OrganizationDoesNotExistError(organization_id)
    return Organization.from_orm(res)


def add_user_to_org(conn: Connection, *, user_id: int, organization_id: UUID4) -> None:
    stmt = insert(org_mbr_tbl).returning(org_mbr_tbl.c.id)
    res = conn.execute(
        stmt, {"organization_id": organization_id, "user_id": user_id}
    ).first()
    return res.id


def is_user_in_org(conn: Connection, *, user_id: int, organization_id: UUID4) -> bool:
    stmt = text(
        "SELECT id FROM organization_members WHERE user_id = :user_id AND organization_id = :organization_id"
    )
    res = conn.execute(stmt, {"organization_id": organization_id, "user_id": user_id})
    return bool(res is not None)


def get_personal_org(conn: Connection, user_id: int) -> Organization:
    """Return user personal org."""
    stmt = text(
        """
        SELECT o.*
        FROM organizations AS o
        INNER JOIN organization_members AS om
        ON o.id = om.organization_id
        WHERE om.user_id = :user_id
            AND o.is_personal
            AND om.deleted_at IS NULL
        """
    )
    res = conn.execute(stmt, {"user_id": user_id}).first()
    if res is None:
        raise UserHasNoPersonalOrganizationError(user_id)
    return Organization.from_orm(res)


def get_personal_org_id(conn: Connection, user_id: int) -> UUID4:
    """Return user personal organization id."""
    return get_personal_org(conn, user_id).id


def set_active_organization(
    conn: Connection, user_id: int, organization_id: UUID4
) -> None:
    """Set the active organization for a user.

    Args:
        conn: Database connection
        user_id: ID of the user.
        organization_id: Organization to set for the user.

    Returns:
        Always returns true if it executes. If organization id is not already an organzation of the
        user, then nothing will happen and active membership is False for all organizations that the
        user belongs to.
    """
    if not is_user_in_org(conn, user_id=user_id, organization_id=organization_id):
        raise UserNotInOrgError(user_id, organization_id)
    stmt = text(
        """
        UPDATE organization_members
        SET active = (organization_id = :organization_id)
        WHERE user_id = :user_id
            AND deleted_at IS NULL
        """
    )
    conn.execute(stmt, {"user_id": user_id, "organization_id": organization_id})


def get_active_org_id(conn: Connection, user_id: int) -> UUID4:
    """Get the acttive organization of a user.

    A user will only have one active organization at a time.

    Args:
        conn: Database connection

    Returns:
        Id of the active organization if one exists. ``None`` if there is no active org.
        Users of this function are responsible for raising exceptions or otherwise
        handling the case of no active organization for the user.
    """
    stmt = text(
        """
        SELECT organization_id
        FROM organization_members
        WHERE user_id = :user_id
            AND deleted_at IS NULL
            AND active
        """
    )
    res = conn.execute(stmt, {"user_id": user_id}).first()
    # Return str intead of UUID because UUID can't natively be cached in redis
    # Also this function is consistent with the return type of check_cache() if converted to str
    res = conn.execute(stmt, {"user_id": user_id}).scalar()
    if res is None:
        raise UserHasNoActiveOrganizationError(user_id)
    return res


def get_active_organization(conn: Connection, user_id: int) -> Organization:
    """Get the acttive organization of a user.

    A user will only have one active organization at a time.

    Returns:
        Data on the user's active org. ``None`` if no active organization is found.
        User must handle a missing active org.
    """
    stmt = text(
        """
        SELECT o.*
        FROM organization_members AS om
        INNER JOIN organizations AS o
            ON o.id = om.organization_id
        WHERE om.user_id = :user_id
            AND om.deleted_at IS NULL
            AND om.active
        """
    )
    res = conn.execute(stmt, {"user_id": user_id}).first()
    if res is None:
        raise UserHasNoActiveOrganizationError(user_id)
    return Organization.from_orm(res)
