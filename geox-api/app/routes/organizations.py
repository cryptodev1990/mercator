from typing import List

from fastapi import APIRouter, Depends, Request
from pydantic import UUID4
from sqlalchemy.orm import Session

from app.crud.organization import (
    add_user_to_organization_by_invite,
    caller_must_be_in_org,
    create_organization_and_assign_to_user,
    get_active_org,
    get_all_orgs_for_user,
    get_org_by_id,
    get_organization_members,
    guarded_hard_delete_organization,
    set_active_organization,
    soft_delete_and_revert_to_personal_organization,
    update_organization,
)
from app.db.session import SessionLocal
from app.dependencies import UserSession, get_app_user_session, verify_token
from app.schemas.organization import (
    Organization,
    OrganizationCreate,
    OrganizationMemberCreate,
    OrganizationMemberDelete,
    OrganizationMemberUpdate,
    OrganizationUpdate,
)
from app.schemas.user import UserWithMembership

router = APIRouter(dependencies=[Depends(verify_token)])


@router.get("/organizations", tags=["organizations"], response_model=List[Organization])
def get_organizations(
    user_session: UserSession = Depends(get_app_user_session),
) -> List[Organization]:
    orgs = get_all_orgs_for_user(user_session.session, user_session.user.id)
    return orgs


@router.get(
    "/organizations/active", tags=["organizations"], response_model=Organization
)
def fetch_active_org(
    user_session: UserSession = Depends(get_app_user_session),
) -> Organization:
    orgs = get_all_orgs_for_user(user_session.session, user_session.user.id)
    active = get_active_org(user_session.session, user_session.user.id)
    assert active, "User has no active organization"
    org = get_org_by_id(user_session.session, active)
    return org


@router.post(
    "/organizations/active", tags=["organizations"], response_model=Organization
)
def set_active_org(
    organization_uuid: UUID4, user_session: UserSession = Depends(get_app_user_session)
) -> Organization:
    db_session = user_session.session
    caller_must_be_in_org(db_session, organization_uuid, user_session.user.id)
    res = set_active_org(organization_uuid, user_session=user_session)
    return res


@router.post(
    "/organizations", tags=["organizations"], response_model=UserWithMembership
)
async def create_organization(
    organization: OrganizationCreate,
    user_session: UserSession = Depends(get_app_user_session),
):
    res = create_organization_and_assign_to_user(
        user_session.session,
        OrganizationCreate(name=organization.name),
        user_session.user.id,
    )
    return res


@router.get(
    "/organizations/{organization_id}",
    tags=["organizations"],
    response_model=Organization,
)
async def get_organization(
    organization_id: UUID4, user_session: UserSession = Depends(get_app_user_session)
):
    db_session = user_session.session
    caller_must_be_in_org(db_session, organization_id, user_session.user.id)
    org = get_org_by_id(db_session, organization_id)
    return org


@router.delete("/organizations/{organization_id}", tags=["organizations"])
async def delete_organization(
    organization_id: UUID4, user_session: UserSession = Depends(get_app_user_session)
) -> bool:
    guarded_hard_delete_organization(
        user_session.session, organization_id, user_session.user.id
    )
    return True


@router.put(
    "/organizations/{organization_id}",
    tags=["organizations"],
    response_model=Organization,
)
async def update_organization_(
    organization_id: UUID4,
    organization: OrganizationUpdate,
    user_session: UserSession = Depends(get_app_user_session),
) -> Organization:
    db_session = user_session.session
    caller_must_be_in_org(db_session, organization_id, user_session.user.id)
    org = update_organization(db_session, organization_id, organization)
    return org


@router.post(
    "/organizations/members", tags=["organizations"], response_model=UserWithMembership
)
async def create_organization_member(
    organization: OrganizationMemberCreate,
    user_session: UserSession = Depends(get_app_user_session),
) -> UserWithMembership:
    own_user = user_session.user
    res = add_user_to_organization_by_invite(
        user_session.session,
        organization.user_id,
        own_user.id,
        organization.organization_id,
    )
    return res


@router.patch("/organizations/members", tags=["organizations"])
async def remove_user(
    organization: OrganizationMemberDelete,
    user_session: UserSession = Depends(get_app_user_session),
) -> int:
    user = user_session.user
    db_session = user_session.session
    caller_must_be_in_org(db_session, organization.organization_id, user.id)
    num_rows = soft_delete_and_revert_to_personal_organization(
        db_session,
        organization_id=organization.organization_id,
        user_id=organization.user_id,
    )
    return num_rows


@router.get(
    "/organizations/members",
    tags=["organizations"],
    response_model=List[UserWithMembership],
)
async def list_organization_members(
    organization_uuid: UUID4, user_session: UserSession = Depends(get_app_user_session)
) -> List[UserWithMembership]:
    db_session = user_session.session
    caller_must_be_in_org(db_session, organization_uuid, user_session.user.id)
    members = get_organization_members(db=db_session, organization_id=organization_uuid)
    return members


@router.put("/organizations/member", tags=["organizations"])
async def update_organization_membership(
    organization: OrganizationMemberUpdate,
    user_session: UserSession = Depends(get_app_user_session),
) -> List[Organization]:
    user = user_session.user
    db_session = user_session.session
    caller_must_be_in_org(db_session, organization.organization_id, user.id)
    if organization.active:
        set_active_organization(db_session, user.id, organization.organization_id)
    return get_all_orgs_for_user(db_session, user.id)
