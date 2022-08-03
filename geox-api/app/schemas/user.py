import datetime
from typing import Optional

from pydantic import BaseModel, Field


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    # All from Auth0
    sub_id: str
    given_name: str
    family_name: str
    nickname: str
    name: str
    picture: str
    locale: str
    updated_at: Optional[datetime.datetime] = Field(
        None, description="The time the user was last updated"
    )
    email_verified: bool
    iss: str


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
