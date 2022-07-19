import datetime
from typing import Optional

from geojson_pydantic import Feature
from pydantic import UUID4, BaseModel, Field


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
    updated_at: Optional[datetime.datetime]
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


class GeoShapeCreate(BaseModel):
    name: Optional[str] = Field(None, description="Name of the shape")
    geojson: Feature = Field(..., description="GeoJSON representation of the shape")


class GeoShapeRead(BaseModel):
    uuid: UUID4 = Field(..., description="Unique identifier for the shape")


class GeoShapeUpdate(GeoShapeRead):
    name: Optional[str]
    geojson: Optional[Feature]
    should_delete: Optional[bool] = Field(
        False, description="If true, deletes the shape"
    )


class GeoShape(GeoShapeRead, GeoShapeCreate):
    created_by_user_id: int = Field(..., description="User ID of the creator")
    created_at: datetime.datetime = Field(..., description="Date and time of creation")
    updated_by_user_id: Optional[int] = Field(
        None, description="User ID of the most recent updater"
    )
    updated_at: Optional[datetime.datetime] = Field(
        None, description="Date and time of most recent updater"
    )
