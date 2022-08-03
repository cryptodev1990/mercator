from typing import Optional

from pydantic import BaseModel, Field


class Namespace(BaseModel):
    uuid: str
    name: str
    admin_email: str
    admin_user_id: int
    created_at: str
    updated_at: str


class NamespaceCreate(BaseModel):
    name: str
    user_id: int


class NamespaceMember(BaseModel):
    user_id: int
    namespace_id: int
    has_read: bool
    has_write: bool
    is_admin: bool
    created_at: str
    updated_at: str


class NamespaceMemberCreate(BaseModel):
    user_id: int
    namespace_id: int
    has_read: bool
    has_write: bool
    is_admin: bool


class NamespaceMemberUpdate(BaseModel):
    namespace_id: int
    user_id: int
    has_read: Optional[bool] = Field(
        None, description="Whether the user has read access to the namespace"
    )
    has_write: Optional[bool] = Field(
        None, description="Whether the user has write access to the namespace"
    )
    is_admin: Optional[bool] = Field(
        None, description="Whether the user is an admin of the namespace"
    )
