"""CRUD functions for organizations."""
from typing import Literal, Optional

from pydantic import UUID4
from sqlalchemy import text
from sqlalchemy.engine import Connection

from app.db.cache import check_cache
from app.schemas import Organization


def get_user_personal_org_id(conn: Connection, user_id: int) -> Optional[UUID4]:
    """Return user personal org."""
    stmt = text(
        """
    SELECT o.id
    FROM organizations AS o
    INNER JOIN organization_members AS om
    ON o.id = om.organization_id
    WHERE om.user_id = :user_id
        AND o.is_personal
        AND om.deleted_at IS NULL
    """
    )
    return conn.execute(stmt, {"user_id": user_id}).scalar()


def set_active_org(
    conn: Connection, user_id: int, organization_id: UUID4
) -> Literal[True]:
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
    stmt = text(
        """
        UPDATE organization_members
        SET active = (organization_id = :organization_id)
        WHERE user_id = :user_id
            AND deleted_at IS NULL
        """
    )
    conn.execute(stmt, {"user_id": user_id, "organization_id": organization_id})
    return True


def get_active_org(
    conn: Connection, user_id: int, use_cache: bool = True
) -> Optional[UUID4]:
    """Get the acttive organization of a user.

    This will check a cache for the value of the user's active organization before running
    a query against the database.

    A user will only have one active organization at a time.

    Args:
        conn: Database connection
        user_id: User id
        use_cache: If ``True`` looks in cache for the organization, otherwise
            runs a query to retrieve the information.


    Returns:
        Id of the active organization if one exists. ``None`` if there is no active org.
        Users of this function are responsible for raising exceptions or otherwise
        handling the case of no active organization for the user.
    """
    # _get_active_org will return str not UUID to make it more
    if use_cache:
        value = check_cache(user_id, "organization_id", _get_active_org, conn, user_id)
    else:
        value = _get_active_org(conn, user_id)
    if value is None:
        return None
    try:
        # If value is valid UUID string - str(str) str('c90981e7-ba7b-4299-9a07-b689bdb03d3a') = 'c90981e7-ba7b-4299-9a07-b689bdb03d3a'
        # If value is somehow already a UUID, then str(UUID('c90981e7-ba7b-4299-9a07-b689bdb03d3a')) = 'c90981e7-ba7b-4299-9a07-b689bdb03d3a'
        # Case of None handled above
        # Otherwise it must be an illformed string
        return UUID4(str(value))
    except ValueError:
        return None


def _get_active_org(conn: Connection, user_id: int) -> Optional[str]:
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
    return str(res.organization_id) if res else None


def get_organization(conn: Connection, id: UUID4) -> Optional[Organization]:
    """Get an organization by id.

    Returns:
        An organization with that id. If there is no such organization,
        then ``None`` is returned. It is up to caller to handle ``None``
        values.

    """
    stmt = text(
        """
        SELECT *
        FROM organizations
        WHERE id = :id
    """
    )
    res = conn.execute(stmt, {"id": id}).first()
    return Organization.from_orm(res) if res else None


def get_active_org_data(
    db: Connection, user_id: int, use_cache: bool = True
) -> Optional[Organization]:
    """Get the acttive organization of a user.

    A user will only have one active organization at a time.

    Returns:
        Data on the user's active org. ``None`` if no active organization is found.
        User must handle a missing active org.
    """
    org_id = get_active_org(db, user_id, use_cache=use_cache)
    if org_id:
        return get_organization(db, org_id)
    return None


def get_personal_org_id(conn: Connection, user_id: int) -> UUID4:
    res = conn.execute(
        text(
            """
        SELECT og.id
        FROM organizations og
        JOIN organization_members om
        ON om.user_id = :user_id
          AND om.organization_id = og.id
          AND om.deleted_at IS NULL
          AND og.is_personal = True
        """
        ),
        {"user_id": user_id},
    )
    return res.first()[0]
