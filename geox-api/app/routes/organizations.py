from typing import List
from fastapi import APIRouter, Request, Security
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import UUID4

from app.db.session import SessionLocal
from app.schemas.organization import Organization, OrganizationCreate, OrganizationMemberCreate, OrganizationMemberDelete, OrganizationMemberUpdate
from app.crud.organization import add_user_to_organization_by_invite, caller_must_be_in_org, create_organization_and_assign_to_user, get_active_org, get_all_memberships, get_all_orgs_for_user, get_org_by_id, get_organization_members, set_active_organization, soft_delete_and_revert_to_personal_organization, soft_delete_organization_member
from app.schemas.user import UserWithMembership

from .common import security

router = APIRouter()

@router.get("/organizations", tags=["organizations"], response_model=List[Organization])
def get_organizations(request: Request) -> List[Organization]:
    user = request.state.user
    with SessionLocal() as db_session:
        orgs = get_all_orgs_for_user(db_session, user.id)
        return orgs


@router.post("/organizations", tags=["organizations"], response_model=UserWithMembership)
async def create_organization(
    request: Request,
    organization: OrganizationCreate,
    credentials: HTTPAuthorizationCredentials = Security(security),
):
    user = request.state.user
    with SessionLocal() as db_session:
        res = create_organization_and_assign_to_user(db_session, OrganizationCreate(
            name=organization.name), user.id)
        return res


@router.post("/organizations/members", tags=["organizations"], response_model=UserWithMembership)
async def create_organization_member(
    request: Request,
    organization: OrganizationMemberCreate,
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> UserWithMembership:
    own_user = request.state.user
    with SessionLocal() as db_session:
        res = add_user_to_organization_by_invite(db_session, organization.user_id, own_user.id, organization.organization_id)
        return res


@router.patch("/organizations/members", tags=["organizations"])
async def remove_user(
    request: Request,
    organization: OrganizationMemberDelete,
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> int:
    user = request.state.user
    with SessionLocal() as db_session:
        caller_must_be_in_org(db_session, organization.organization_id, user.id)
        num_rows = soft_delete_and_revert_to_personal_organization(db_session, organization_id=organization.organization_id, user_id=organization.user_id)
        return num_rows


@router.get("/organizations/members", tags=["organizations"], response_model=List[UserWithMembership])
async def list_organization_members(
    request: Request,
    organization_uuid: UUID4,
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> List[UserWithMembership]:
    user = request.state.user
    with SessionLocal() as db_session:
        caller_must_be_in_org(db_session, organization_uuid, user.id)
        members = get_organization_members(db=db_session, organization_id=organization_uuid)
        return members


@router.patch("/organizations/membership", tags=["organizations"])
async def update_organization_membership(
    request: Request,
    organization: OrganizationMemberUpdate,
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> List[Organization]:
    user = request.state.user
    with SessionLocal() as db_session:
        caller_must_be_in_org(db_session, organization.organization_id, user.id)
        if organization.active:
            set_active_organization(db_session, user.id, organization.organization_id)
        return get_all_orgs_for_user(db_session, user.id)

