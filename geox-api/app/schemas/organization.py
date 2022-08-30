import datetime
from typing import Optional

from pydantic import UUID4, BaseModel, Field


class OrganizationRead(BaseModel):
    uuid: UUID4 = Field(..., description="Unique identifier for the organization")


class OrganizationCreate(BaseModel):
    name: str = Field(..., description="Name of the organization")


class OrganizationUpdate(BaseModel):
    name: Optional[str] = None


class Organization(BaseModel):
    id: UUID4
    name: str
    is_personal: bool
    created_at: datetime.datetime
    updated_at: datetime.datetime


class OrganizationMember(BaseModel):
    uuid: UUID4
    organization_id: UUID4
    name: str
    user_id: int
    added_by_user_id: int
    created_at: str
    updated_at: str


class OrganizationMemberCreate(BaseModel):
    organization_id: UUID4
    user_id: int


class OrganizationMemberDelete(BaseModel):
    organization_id: UUID4
    user_id: int


class OrganizationMemberUpdate(BaseModel):
    organization_id: UUID4
    active: Optional[bool] = None
