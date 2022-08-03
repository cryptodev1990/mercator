from typing import Optional

from pydantic import UUID4, BaseModel, Field


class OrganizationRead(BaseModel):
    uuid: UUID4 = Field(..., description="Unique identifier for the organization")


class OrganizationCreate(BaseModel):
    name: str = Field(..., description="Name of the organization")


class OrganizationUpdate(BaseModel):
    uuid: UUID4
    name: Optional[str] = Field(None, description="Name of the organization")
    admin_email: Optional[str] = Field(
        None, description="Email of the organization admin"
    )
    admin_user_id: Optional[int] = Field(
        None, description="User ID of the organization admin"
    )
    should_delete: Optional[bool] = False


class Organization(BaseModel):
    uuid: str
    name: str
    admin_email: str
    admin_user_id: int
    created_at: str
    updated_at: str
