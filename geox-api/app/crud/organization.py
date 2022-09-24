from typing import List, Optional, Set, cast

from pydantic import UUID4
from sqlalchemy import text, select
from sqlalchemy.orm import Session

from app import models
from app.crud.user import get_user


class OrganizationModelException(Exception):
    pass


def hard_delete_organization(db: Session, organization_id: UUID4) -> int:
    """Hard delete an organization and all of its members."""
    num_rows = (
        db.query(models.Organization)
        .filter(models.Organization.id == organization_id)
        .delete()
    )
    db.commit()
    return num_rows


def set_active_org(db: Session, user_id: int, organization_id: UUID4) -> bool:
    """Sets the active organization for a user"""
    db.execute(
        text(
            """
            UPDATE organization_members
            SET active = (organization_id = :organization_id)
            WHERE user_id = :user_id;
        """
        ),
        {"user_id": user_id, "organization_id": organization_id},
    )
    return True


# TODO make this consistent with the other get_* functions, use user instead of user_id
def get_active_org(db: Session, user_id: int) -> Optional[UUID4]:
    """Get the organization of a user.

    A user will only have one active organization at a time.
    """
    stmt = text("""
    SELECT organization_id
    FROM organization_members
    WHERE TRUE
        AND deleted_at IS NULL
        AND user_id = :user_id
        AND active
    ORDER BY updated_at DESC
    LIMIT 1
    """)
    res = db.execute(stmt, {"user_id": user_id}).first()
    if res:
        return res.organization_id
    return None


def get_personal_org_id(db: Session, user_id: int) -> UUID4:
    stmt = text("""
        SELECT og.id AS organization_id
        FROM organizations AS og
        JOIN organization_members AS om
        ON om.user_id = :user_id
          AND om.organization_id = og.id
          AND om.deleted_at IS NULL
          AND og.is_personal
        LIMIT 1
        """)
    res = db.execute(stmt, {"user_id": user_id}).first()
    return res.organization_id


def organization_s3_enabled(db: Session, organization_id: str) -> bool:
    """Return whether the organization has s3 export enabled."""
    stmt = text(
        "SELECT s3_export_enabled FROM organizations WHERE id = :organization_id"
    )
    res = db.execute(stmt, {"organization_id": organization_id}).scalar()
    return res
