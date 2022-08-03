from pydantic import UUID4
from sqlalchemy.orm import Session

from .. import schemas


def create_organization(
    db: Session, organization: schemas.OrganizationCreate, user_id: UUID4
) -> UUID4:
    res = db.execute(
        """
    INSERT INTO organizations (
        uuid,
        admin_email,
        admin_user_id,
        name,
        created_at,
        updated_at
    ) VALUES (
        GEN_RANDOM_UUID(),
        (SELECT email FROM users WHERE uuid = :admin_user_id),
        :admin_user_id,
        :name,
        NOW(),
        NOW()
    )
        RETURNING uuid;
    """,
        {
            "name": organization.name,
            "admin_user_id": user_id,
        },
    )
    rows = res.mappings().all()
    uuid: UUID4 = rows[0]["uuid"]
    return uuid


def hard_delete_organization(db: Session, organization_uuid: UUID4) -> UUID4:
    res = db.execute(
        """
    DELETE FROM organizations WHERE uuid = :organization_uuid
    RETURNING uuid;
    """,
        {
            "organization_uuid": organization_uuid,
        },
    )
    rows = res.mappings().all()
    uuid: UUID4 = rows[0]["uuid"]
    return uuid
