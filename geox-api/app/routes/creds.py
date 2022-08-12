from enum import Enum
from typing import List, Optional

from fastapi import APIRouter, Depends, Request, Security
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import UUID4
from sqlalchemy.orm import Session

from app.crud import db_credentials as crud
from app.db.session import get_db
from app.schemas import PublicDbCredential
from app.schemas.db_credential import DbCredentialCreate, DbCredentialUpdate

from .common import security

router = APIRouter(tags=["db_config"])


class GetAllConnectionsType(str, Enum):
    organization = "organization"


@router.post("/db_config/connections", response_model=PublicDbCredential)
def create_db_conn(
    request: Request,
    new_db_conn: DbCredentialCreate,
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> Optional[PublicDbCredential]:
    """Creates a database connection"""
    user = request.state.user
    with SessionLocal() as db_session:
        creds = crud.create_conn(db_session, new_db_conn, user.id)
        return creds


@router.get("/db_config/connections/{uuid}", response_model=PublicDbCredential)
def read_db_conn(
    request: Request,
    uuid: UUID4,
    credentials: HTTPAuthorizationCredentials = Security(security),
    db_session: Session = Depends(get_db),
) -> Optional[PublicDbCredential]:
    """Read a single connection by UUID. Requires that the user be in the same organization as the connection."""
    user = request.state.user
    with SessionLocal() as db_session:
        return crud.get_conn(db=db_session, db_credential_id=uuid, user_id=user.id)


@router.patch("/db_config/connections/{uuid}", response_model=PublicDbCredential)
def update_db_conn(
    request: Request,
    conn_update: DbCredentialUpdate,
    credentials: HTTPAuthorizationCredentials = Security(security),
    db_session: Session = Depends(get_db),
) -> Optional[PublicDbCredential]:
    """Updates a single db connection"""
    user = request.state.user
    with SessionLocal() as db_session:
        creds = crud.update_conn(db_session, conn_update=conn_update, user_id=user.id)
        return creds


@router.delete("/db_config/connections/{uuid}")
def delete_db_conn(
    request: Request,
    uuid: UUID4,
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> bool:
    """Deletes a database connection"""
    user = request.state.user
    with SessionLocal() as db_session:
        num_rows = crud.delete_conn(db_session, uuid, user.id)
        return num_rows > 0
