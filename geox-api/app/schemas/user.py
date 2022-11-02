import datetime
from email.message import EmailMessage
from typing import Optional

from pydantic import UUID4, EmailStr, Field

from app.schemas.common import BaseModel

# This is imported by __init__ with *
# Append all objects to exported in __all__
__all__ = ["UserBase", "UserCreate", "User"]


class UserBase(BaseModel):
    """The minimal user information."""

    id: int
    email: EmailStr
    sub_id: str


class User(UserBase):
    """Full user information."""

    given_name: Optional[str] = None
    family_name: Optional[str] = None
    nickname: Optional[str] = None
    name: Optional[str] = None
    locale: Optional[str] = None
    picture: Optional[str] = None
    is_active: bool = True
    email_verified: Optional[bool] = False


class UserCreate(User):
    """All user fields included from Auth0."""

    email: EmailStr
    sub_id: str
    email_verified: bool
    iss: str
    nickname: str  # This is needed for the namespace name
    given_name: Optional[str] = None
    family_name: Optional[str] = None
    name: Optional[str] = None
    picture: Optional[str] = None
    locale: Optional[str] = None
    updated_at: Optional[datetime.datetime] = Field(
        None, description="The time the user was last updated"
    )
