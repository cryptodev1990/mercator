"""CRUD functions for organizations and organization membership."""
from typing import List, Optional, Set, Union

from pydantic import UUID4
from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.engine import Connection

from app import models, schemas


class OrganizationModelException(Exception):
    pass


def set_active_org(
    db: Union[Connection, Session], user_id: int, organization_id: UUID4
) -> bool:
    """Set the active organization for a user."""
    db.execute(
        text(
            """
            UPDATE organization_members
            SET active = (organization_id = :organization_id)
            WHERE user_id = :user_id
            ;
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
    organization_member = (
        db.query(models.OrganizationMember)
        .filter(
            models.OrganizationMember.user_id == user_id,
            models.OrganizationMember.deleted_at.is_(None),
            models.OrganizationMember.active == True,
        )
        .order_by(models.OrganizationMember.created_at.desc())
        .first()
    )
    if organization_member:
        return organization_member.__dict__["organization_id"]
    return None


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


def organization_s3_enabled(db: Session, organization_id: str) -> bool:
    """Return whether the organization has s3 export enabled."""
    stmt = text(
        "SELECT s3_export_enabled FROM organizations WHERE id = :organization_id"
    )
    res = db.execute(stmt, {"organization_id": organization_id}).scalar()
    return res
