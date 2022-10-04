import datetime
from typing import Optional

from pydantic import UUID4, Field

from app.schemas.common import BaseModel

# This is imported by __init__ with *
# Append all objects to exported in __all__
__all__ = []


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    """All user fields included from Auth0."""

    sub_id: str
    given_name: Optional[str] = None
    family_name: Optional[str] = None
    nickname: str
    name: Optional[str] = None
    picture: Optional[str] = None
    locale: Optional[str] = None
    updated_at: Optional[datetime.datetime] = Field(
        None, description="The time the user was last updated"
    )
    email_verified: bool
    iss: str


__all__.append("UserCreate")


class User(UserBase):
    id: int
    sub_id: str
    given_name: Optional[str] = None
    family_name: Optional[str] = None
    nickname: Optional[str] = None
    name: Optional[str] = None
    locale: Optional[str] = None
    picture: Optional[str] = None
    is_active: bool = True


__all__.append("User")


class UserWithMembership(User):
    organization_id: UUID4
    is_personal: bool


__all__.append("UserWithMembership")
