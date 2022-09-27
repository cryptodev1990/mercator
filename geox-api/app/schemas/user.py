import datetime
from typing import Optional

from pydantic import Field, UUID4
from app.schemas.common import BaseModel

__all__ = []

class UserBase(BaseModel):
    email: str

__all__.append("UserBase")

class UserCreate(UserBase):
    # All from Auth0
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
    given_name: Optional[str]
    family_name: Optional[str]
    nickname: Optional[str]
    name: Optional[str]
    locale: Optional[str]
    picture: Optional[str]
    last_login_at: Optional[datetime.datetime]
    is_active: bool

    class Config:
        orm_mode = True

__all__.append("User")

class UserWithMembership(User):
    organization_id: UUID4
    is_personal: bool

__all__.append("UserWithMembership")
