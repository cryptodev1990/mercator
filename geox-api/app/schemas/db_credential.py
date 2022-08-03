import datetime
from typing import Optional

from pydantic import UUID4, BaseModel, Field


class DbCredentialCreate(BaseModel):
    name: str = Field(..., description="Name of the connection")
    is_default: bool = Field(
        False, description="Makes connection the default for publishing"
    )
    db_user: str
    db_password: str
    db_host: str
    db_port: str
    db_database: str
    # TODO make enum for supported databases
    db_driver: str
    db_extras: Optional[dict]


class DbCredentialRead(BaseModel):
    id: UUID4
    user_id: int


class DbCredentialUpdate(DbCredentialRead):
    name: Optional[str]
    should_delete: Optional[bool] = Field(
        False, description="If true, deletes the connection"
    )
    is_default: Optional[bool]
    db_user: Optional[str]
    db_password: Optional[str]
    db_host: Optional[str]
    db_port: Optional[str]
    db_database: Optional[str]
    db_extras: Optional[dict]
    # TODO make enum for supported databases
    db_driver: Optional[str]


class PublicDbCredential(BaseModel):
    id: UUID4
    name: Optional[str]
    is_default: Optional[bool]
    created_at: datetime.datetime
    created_by_user_id: int
    updated_at: datetime.datetime
    updated_by_user_id: int
    db_driver: str


class DbCredentialWithCreds(BaseModel):
    id: UUID4
    db_user: Optional[str]
    db_password: Optional[str]
    db_host: Optional[str]
    db_port: Optional[str]
    db_database: Optional[str]
    db_extras: Optional[dict] = Field(
        None, description="Extra credentials for the database"
    )
    db_driver: str


class EncryptedDbCredentialWithCreds(DbCredentialRead):
    encrypted_db_user: bytes
    encrypted_db_password: bytes
    encrypted_db_host: bytes
    encrypted_db_port: bytes
    encrypted_db_database: bytes
    encrypted_db_extras: Optional[bytes] = Field(
        None, description="Encrypted extras for db connection"
    )
    db_driver: str
