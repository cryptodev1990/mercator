from typing import List, Optional, Set, cast

from pydantic import UUID4
from sqlalchemy import text
from sqlalchemy.orm import Session

from app import models, schemas
from app.crud.user import get_user


class OrganizationModelException(Exception):
    pass


def caller_must_be_in_org(db: Session, organization_id: UUID4, user_id: int) -> bool:
    """Check if user is member of organization."""
    res = (
        db.query(models.OrganizationMember)
        .filter(
            models.OrganizationMember.organization_id == organization_id,
            models.OrganizationMember.user_id == user_id,
            models.OrganizationMember.deleted_at.is_(None),
        )
        .first()
    )
    if res:
        return True
    raise OrganizationModelException("User is not in organization")


def get_org_by_id(db: Session, organization_id: UUID4) -> schemas.Organization:
    """Return an organization by id."""
    res = (
        db.query(models.Organization)
        .filter(models.Organization.id == organization_id)
        .first()
    )
    if not res:
        raise OrganizationModelException("Organization not found")
    return schemas.Organization(**res.__dict__)


def create_organization_and_assign_to_user(
    db: Session,
    organization: schemas.OrganizationCreate,
    user_id: int,
) -> schemas.UserWithMembership:
    """Create an organization and assigns it to the user who created it."""
    org = create_organization(db, organization, user_id)
    new_org_member = models.OrganizationMember(
        organization_id=org.id, user_id=user_id, active=False
    )
    db.add(new_org_member)
    db.commit()
    set_active_organization(db, user_id, org.id)
    member = get_all_memberships(db, user_id)  # most recent membership
    assert member[0]
    return member[0]


def create_organization(
    db: Session, organization: schemas.OrganizationCreate, user_id: int
) -> schemas.Organization:
    """Create an organization without assigning it to a user."""
    db_org = models.Organization(
        name=organization.name, created_by_user_id=user_id, is_personal=False
    )
    db.add(db_org)
    db.commit()
    res = (
        db.query(models.Organization)
        .filter(models.Organization.id == db_org.id)
        .first()
    )
    if not res:
        raise OrganizationModelException("Organization failed to create")
    set_active_organization(db, user_id, cast(UUID4, db_org.id))
    db.refresh(res)
    return schemas.Organization(**res.__dict__)


def hard_delete_organization(db: Session, organization_id: UUID4) -> int:
    """Hard delete an organization and all of its members."""
    num_rows = (
        db.query(models.Organization)
        .filter(models.Organization.id == organization_id)
        .delete()
    )
    db.commit()
    return num_rows


def guarded_hard_delete_organization(
    db: Session, organization_id: UUID4, user_id: int
) -> int:
    """Hard delete an organization and all of its members."""
    caller_must_be_in_org(db, organization_id, user_id)
    if get_personal_org_id(db, user_id) == organization_id:
        raise OrganizationModelException("Cannot delete personal organization")
    num_rows = (
        db.query(models.Organization)
        .filter(models.Organization.id == organization_id)
        .delete()
    )
    db.commit()
    return num_rows


def update_organization(
    db: Session, organization_id: UUID4, organization: schemas.OrganizationUpdate
) -> schemas.Organization:
    """Update an organization."""
    db_org = (
        db.query(models.Organization)
        .filter(
            models.Organization.id == organization_id,
            models.Organization.is_personal == False,
        )
        .first()
    )
    if not db_org:
        raise OrganizationModelException("Organization not found")
    db_org.name = organization.name or db_org.name  # type: ignore
    db.commit()
    db.refresh(db_org)
    return schemas.Organization(**db_org.__dict__)


def has_membership(db: Session, organization_id: UUID4, user_id: int) -> bool:
    """Check if user is member of organization."""
    org = (
        db.query(models.OrganizationMember)
        .filter(
            models.OrganizationMember.organization_id == organization_id,
            models.OrganizationMember.user_id == user_id,
            models.OrganizationMember.deleted_at.is_(None),
        )
        .first()
    )
    return org is not None


def add_user_to_organization_by_invite(
    db: Session,
    invited_user_id: int,
    added_by_user_id: int,
    organization_id: Optional[UUID4] = None,
) -> schemas.UserWithMembership:
    """Add a user to an organizatio."""
    organization_id = organization_id or get_active_org(db, added_by_user_id)
    if not organization_id:
        raise OrganizationModelException("No organization to add user to")

    caller_must_be_in_org(db, organization_id, added_by_user_id)
    # TODO user has agreed to invite
    new_org_member = add_user_to_organization(db, invited_user_id, organization_id)
    return schemas.UserWithMembership(**new_org_member.__dict__)


def add_user_to_organization(
    db: Session,
    user_id: int,
    organization_id: UUID4,
) -> schemas.UserWithMembership:
    """Add a user to an organization.

    TODO this is potentially leaky, since a user can be added
    from outside the organization if you know their ID (easy to guess)
    """
    org_set = get_all_orgs_for_user_as_set(db, user_id)
    if organization_id in org_set:
        raise OrganizationModelException("User is already in organization")

    org = get_org_by_id(db, organization_id)
    if org.is_personal:
        raise OrganizationModelException("Cannot add a user to a personal organization")

    new_org_member = models.OrganizationMember(
        organization_id=organization_id,
        user_id=user_id,
    )
    db.add(new_org_member)
    db.commit()
    user = get_user(db, user_id)
    args = user.__dict__
    args["organization_id"] = organization_id
    args["is_personal"] = org.is_personal
    set_active_organization(db, user_id, organization_id)
    return schemas.UserWithMembership(**args)


def get_organization_members(
    db: Session, organization_id: UUID4
) -> List[schemas.UserWithMembership]:
    """Return a list of all members of an organization."""
    res = db.execute(
        text(
            """SELECT u.*
        , organization_id
        , is_personal
        FROM users u
        JOIN organization_members om
        ON om.user_id = u.id
        JOIN organizations o
        ON o.id = om.organization_id
        WHERE 1=1
          AND om.organization_id = :organization_id
          AND om.deleted_at IS NULL"""
        ),
        {"organization_id": organization_id},
    )
    rows = res.mappings().all()
    return [schemas.UserWithMembership(**row) for row in rows]


def delete_organization_member(db: Session, user_id: int, organization_id: int) -> int:
    """Hard deletes an member of an organization."""
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


def soft_delete_organization_member(
    db: Session, user_id: int, organization_id: UUID4
) -> int:
    """Soft deletes a member of an organization"""
    org = get_org_by_id(db, organization_id)
    if org.is_personal:
        raise OrganizationModelException("Cannot delete personal organization")
    num_rows = (
        db.query(models.OrganizationMember)
        .filter(
            models.OrganizationMember.user_id == user_id,
            models.OrganizationMember.organization_id == organization_id,
        )
        .update({"is_deleted": True, "active": False})
    )
    db.commit()
    return num_rows


def soft_delete_and_revert_to_personal_organization(
    db: Session, user_id: int, organization_id: UUID4
) -> int:
    """Soft deletes a member of an organization."""
    num_rows = soft_delete_organization_member(db, user_id, organization_id)
    personal_org_id = get_personal_org_id(db, user_id)
    set_active_organization(db, user_id, personal_org_id)
    return num_rows


def set_active_organization(db: Session, user_id: int, organization_id: UUID4) -> bool:
    """Sets the active organization for a user"""
    db.execute(
        text(
            """
        BEGIN;
        UPDATE organization_members
          SET active = False
          WHERE user_id = :user_id
        ;
        UPDATE organization_members
          SET active = True
          WHERE user_id = :user_id AND organization_id = :organization_id
        ;
        END;
        """
        ),
        {"user_id": user_id, "organization_id": organization_id},
    )
    return True


# TODO make this consistent with the other get_* functions, use user instead of user_id
def get_active_org(db: Session, user_id: int) -> Optional[UUID4]:
    """Gets the organization of a user

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


def get_all_memberships(db: Session, user_id: int) -> List[schemas.UserWithMembership]:
    """Generates an object with User and OrganizationMember fields"""
    res = db.execute(
        text(
            """SELECT u.*
        , om.organization_id
        , og.is_personal
        FROM users u
        JOIN organization_members om
        ON om.user_id = u.id
        JOIN organizations og
        ON og.id = om.organization_id
          AND om.user_id = u.id
        WHERE 1=1
          AND u.id = :user_id
          AND om.deleted_at IS NULL
        ORDER BY om.created_at DESC"""
        ),
        {"user_id": user_id},
    )
    rows = res.mappings().all()
    return [schemas.UserWithMembership(**row) for row in rows]


def get_all_orgs_for_user(db: Session, user_id: int) -> List[schemas.Organization]:
    """Generates an object with User and OrganizationMember fields"""
    res = db.execute(
        text(
            """
        SELECT og.id
        , og.name
        , og.is_personal
        , og.created_at
        , og.updated_at
        FROM organization_members om
        JOIN organizations og
        ON om.user_id = :user_id
          AND om.deleted_at IS NULL
          AND om.organization_id = og.id
        ORDER BY om.created_at ASC"""
        ),
        {"user_id": user_id},
    )
    rows = res.mappings().all()
    return [schemas.Organization(**row) for row in rows]


def get_all_orgs_for_user_as_set(db: Session, user_id: int) -> Set[UUID4]:
    """Generates an object with User and OrganizationMember fields"""
    res = db.execute(
        text(
            """
        SELECT og.id
        , og.name
        , og.is_personal
        , og.created_at
        FROM organization_members om
        JOIN organizations og
        ON om.user_id = :user_id
          AND om.organization_id = og.id
          AND om.deleted_at IS NULL
        ORDER BY om.created_at ASC"""
        ),
        {"user_id": user_id},
    )
    rows = res.mappings().all()
    return {row["id"] for row in rows}


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
