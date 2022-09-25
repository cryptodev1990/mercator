from typing import List, Optional, Set, Union, cast

from pydantic import UUID4
from sqlalchemy import text
from sqlalchemy.engine import Connection
from sqlalchemy.orm import Session


def set_active_org(
    db: Union[Session, Connection], user_id: int, organization_id: UUID4
) -> True:
    """Set the active organization for a user.

    Args:
        db: Database connection or session.
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
        WHERE user_id = :user_id;
        """
    )
    db.execute(stmt, {"user_id": user_id, "organization_id": organization_id})
    return True


# TODO make this consistent with the other get_* functions, use user instead of user_id
def get_active_org(db: Session, user_id: int) -> Optional[UUID4]:
    """Get the acttive organization of a user.

    A user will only have one active organization at a time.

    Returns:
        Id of the active organization if one exists. ``None`` if there is no active org.
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
    res = db.execute(stmt, {"user_id": user_id}).first()
    return res.organization_id if res else None


def get_personal_org_id(db: Session, user_id: int) -> UUID4:
    res = db.execute(
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


def organization_s3_enabled(db: Session, organization_id: UUID4) -> bool:
    """Return whether the organization has s3 export enabled."""
    stmt = text(
        "SELECT s3_export_enabled FROM organizations WHERE id = :organization_id"
    )
    res = db.execute(stmt, {"organization_id": organization_id}).scalar()
    return res
