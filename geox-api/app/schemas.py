from pydantic import BaseModel

import datetime


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    # All from Auth0
    given_name: str
    family_name: str
    nickname: str
    name: str
    picture: str
    locale: str
    updated_at: datetime.datetime
    email_verified: bool
    iss: str


class User(UserBase):
    id: int
    given_name: str
    family_name: str
    nickname: str
    name: str
    locale: str
    picture: str
    last_login_at: datetime.datetime
    is_active: bool

    class Config:
        orm_mode = True
