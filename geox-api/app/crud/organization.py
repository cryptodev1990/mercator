from typing import List, Optional, Set, cast

from pydantic import UUID4
from sqlalchemy import text
from sqlalchemy.orm import Session

from app import models, schemas
from app.crud.user import get_user


class OrganizationModelException(Exception):
    pass



def set_active_organization(db: Session, user_id: int, organization_id: UUID4) -> bool:
    """Sets the active organization for a user."""
    db.execute(
        text(
            """
        UPDATE organization_members
          SET active = False
          WHERE user_id = (organization_id = :organization_id);
        """
        ),
        {"user_id": user_id, "organization_id": organization_id},
    )
    return True


# TODO make this consistent with the other get_* functions, use user instead of user_id
def get_active_org(db: Session, user_id: int) -> Optional[UUID4]:
    """Gets the organization of a user.

    A user will only have one active organization at a time.
    """
    stmt = """
    SELECT organization_id
    FROM organization_members
    WHERE user_id = :user_id
        AND deleted_at IS NULL
        AND active
    """
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


def organization_s3_enabled(db: Session, organization_id: str) -> bool:
    """Return whether the organization has s3 export enabled."""
    stmt = text(
        "SELECT s3_export_enabled FROM organizations WHERE id = :organization_id"
    )
    res = db.execute(stmt, {"organization_id": organization_id}).scalar()
    return res
