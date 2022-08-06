from typing import List, Optional

from pydantic import UUID4
from sqlalchemy.orm import Session

import app.crud.user as user_crud
from app import models, schemas


class OrganizationModelException(Exception):
    pass


def get_or_create_organization_for_user(
    db: Session, user_id: int
) -> schemas.UserWithMembership:
    member = get_membership(db, user_id)
    if member:
        return member
    user = user_crud.get_user(db, user_id)
    workspace_name = user.name + "'s Team" if user.name else "Workspace"
    return create_organization_and_assign_to_user(
        db, schemas.OrganizationCreate(name=workspace_name), user_id
    )


def has_membership(db: Session, organization_id: UUID4, user_id: int) -> bool:
    """Check if user is member of organization."""
    org = (
        db.query(models.OrganizationMember)
        .filter(
            models.OrganizationMember.organization_id == organization_id,
            models.OrganizationMember.user_id == user_id,
        )
        .first()
    )
    return org is not None


def create_organization_and_assign_to_user(
    db: Session,
    organization: schemas.OrganizationCreate,
    user_id: int,
    added_by_user_id: Optional[int] = None,
) -> schemas.UserWithMembership:
    """Creates an organization and assigns it to the user who created it"""
    org_id = create_organization(db, organization)
    org_member = upsert_organization_for_user(db, user_id, org_id)
    return org_member


def create_organization(db: Session, organization: schemas.OrganizationCreate) -> UUID4:
    """Creates an organization without assigning it to a user"""
    db_org = models.Organization(name=organization.name)
    db.add(db_org)
    db.commit()
    res = (
        db.query(models.Organization)
        .filter(models.Organization.id == db_org.id)
        .first()
    )
    if not res:
        raise OrganizationModelException("Organization failed to create")
    return res.id


def hard_delete_organization(db: Session, organization_id: UUID4) -> int:
    """Hard deletes an organization and all of its members"""
    num_rows = (
        db.query(models.Organization)
        .filter(models.Organization.id == organization_id)
        .delete()
    )
    db.commit()
    return num_rows


def upsert_organization_for_user(
    db: Session, user_id: int, organization_id: UUID4
) -> schemas.UserWithMembership:
    """Update or insert an organization for a user."""
    candidate_org_membership = models.OrganizationMember(
        user_id=user_id, organization_id=organization_id
    )
    live_org_membership = (
        db.query(models.OrganizationMember)
        .filter(
            # TODO modify to support multiple organizations
            # models.OrganizationMember.user_id == user_id, models.OrganizationMember.organization_id == organization_id
            models.OrganizationMember.user_id
            == user_id
        )
        .first()
    )
    # If the user is already a member of the organization, replace the existing membership.
    if live_org_membership:
        live_org_membership.organization_id = organization_id  # type: ignore
        db.commit()
    # Otherwise, insert a new membership.
    else:
        db.add(candidate_org_membership)
        db.commit()
    # Pull user to get the new organization membership.
    user_org_membership = get_membership(db, user_id)
    assert user_org_membership is not None
    return user_org_membership


def add_user_to_organization(
    db: Session,
    invited_user_id: int,
    added_by_user_id: int,
    organization_id: Optional[UUID4] = None,
) -> bool:
    """Adds a user to an organization"""
    organization_id = organization_id or get_org(db, added_by_user_id)
    invited_user_org = get_org(db, invited_user_id)
    if not organization_id:
        raise OrganizationModelException("No organization to add user to")
    if invited_user_org == organization_id:
        raise OrganizationModelException("User already in organization")
    if get_org(db, added_by_user_id) != organization_id:
        raise OrganizationModelException(
            "Adding user can only add to organizations they are a member of"
        )
    # TODO support multiple organizations
    # new_org_member = models.OrganizationMember(
    #     organization_id=organization_id, user_id=invited_user_id, added_by_user_id=added_by_user_id,
    #     has_read=True, has_write=True, is_admin=True
    # )
    # db.add(new_org_member)
    upsert_organization_for_user(db, invited_user_id, organization_id)
    db.commit()
    return True


def get_organization_members(
    db: Session, organization_id: UUID4
) -> List[schemas.UserWithMembership]:
    """Returns a list of all members of an organization"""
    res = db.execute(
        """SELECT u.*
        , organization_id
        FROM users u
        JOIN organization_members o
        ON o.user_id = u.id
        WHERE o.organization_id = :organization_id""",
        {"organization_id": organization_id},
    )
    rows = res.mappings().all()
    return [schemas.UserWithMembership(**row) for row in rows]


def delete_organization_member(db: Session, user_id: int, organization_id: int) -> int:
    """Deletes a member of an organization"""
    num_rows = (
        db.query(models.OrganizationMember)
        .filter(
            models.OrganizationMember.user_id == user_id,
            models.OrganizationMember.organization_id == organization_id,
        )
        .delete()
    )
    db.commit()
    return num_rows


def deactivate_organization_member(
    db: Session, user_id: int, organization_id: int
) -> bool:
    """Deactivates a member of an organization"""
    member = (
        db.query(models.OrganizationMember)
        .filter(
            models.OrganizationMember.user_id == user_id,
            models.OrganizationMember.organization_id == organization_id,
        )
        .one()
    )
    member.update(has_read=False, has_write=False, is_admin=False)
    db.commit()
    return True


def get_org_by_id(db: Session, organization_id: UUID4) -> schemas.Organization:
    """Returns an organization by id"""
    res = (
        db.query(models.Organization)
        .filter(models.Organization.id == organization_id)
        .first()
    )
    if not res:
        raise OrganizationModelException("Organization not found")
    return schemas.Organization(**res.__dict__)


def remove_orphaned_orgs(db: Session):
    """Removes organizations that have no members"""
    db.execute(
        """DELETE FROM organizations WHERE id NOT IN (SELECT DISTINCT organization_id FROM organization_members)"""
    )
    db.commit()


# TODO make this consistent with the other get_* functions, use user instead of user_id
def get_org(db: Session, user_id: int) -> Optional[UUID4]:
    organization_member = (
        db.query(models.OrganizationMember)
        .filter(models.OrganizationMember.user_id == user_id)
        .first()
    )
    if organization_member:
        return organization_member.__dict__['organization_id']
    return None


def get_membership(db: Session, user_id: int) -> Optional[schemas.UserWithMembership]:
    res = db.execute(
        """SELECT u.*
        , organization_id
        FROM users u
        JOIN organization_members o
        ON o.user_id = u.id
          AND u.id = :user_id""",
        {"user_id": user_id},
    )
    if not res.rowcount:
        return None
    row = res.mappings().first()
    return schemas.UserWithMembership(**row)