from enum import Enum
from typing import List, Optional

from fastapi import APIRouter, Depends, Request, Security, HTTPException
from pydantic import UUID4
from sqlalchemy.orm import Session

from app.crud import db_credentials as crud
from app.dependencies import get_db, verify_token
from app.schemas import PublicDbCredential
from app.schemas.db_credential import DbCredentialCreate, DbCredentialUpdate

router = APIRouter(tags=["db_config"], dependencies=[Depends(verify_token)])


class GetAllConnectionsType(str, Enum):
    organization = "organization"


@router.post("/db_config/connections", response_model=PublicDbCredential)
def create_db_conn(
    request: Request, new_db_conn: DbCredentialCreate, db_session=Depends(get_db)
) -> Optional[PublicDbCredential]:
    """Creates a database connection"""
    user = request.state.user
    creds = crud.create_conn(db_session, new_db_conn, user.id)
    return creds


@router.get("/db_config/connections/{uuid}", response_model=PublicDbCredential)
def read_db_conn(
    request: Request,
    uuid: UUID4,
    db_session: Session = Depends(get_db),
) -> Optional[PublicDbCredential]:
    """Read a single connection by UUID. Requires that the user be in the same organization as the connection."""
    user = request.state.user
    try:
        return crud.get_conn(db=db_session, db_credential_id=uuid, user_id=user.id)
    except crud.DbCredentialModelException as e:
        if "not found" in str(e):
            raise HTTPException(status_code=404, detail="Not found")


@router.get("/db_config/connections", response_model=List[PublicDbCredential])
def read_db_conns(
    request: Request,
    type: GetAllConnectionsType = GetAllConnectionsType.organization,
    db_session: Session = Depends(get_db),
) -> List[PublicDbCredential]:
    """Read all connections. Requires that the user be in the same organization as the connection."""
    user = request.state.user
    if type == GetAllConnectionsType.organization:
        return crud.get_conns(db=db_session, user=user)
    else:
        raise HTTPException(status_code=404, detail="Not found")


@router.patch("/db_config/connections/{uuid}", response_model=PublicDbCredential)
def update_db_conn(
    request: Request,
    conn_update: DbCredentialUpdate,
    db_session: Session = Depends(get_db),
) -> Optional[PublicDbCredential]:
    """Updates a single db connection"""
    user = request.state.user
    creds = crud.update_conn(db_session, conn_update=conn_update, user_id=user.id)
    return creds


@router.delete("/db_config/connections/{uuid}")
def delete_db_conn(
    request: Request,
    uuid: UUID4,
    db_session: Session = Depends(get_db),
) -> bool:
    """Deletes a database connection"""
    user = request.state.user
    num_rows = crud.delete_conn(db_session, uuid, user.id)
    return num_rows > 0
