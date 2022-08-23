from enum import Enum
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import UUID4
from sqlalchemy.orm import Session

from app.crud import db_credentials as crud
from app.dependencies import UserSession, get_app_user_session, verify_token
from app.schemas import PublicDbCredential
from app.schemas.db_credential import DbCredentialCreate, DbCredentialUpdate

router = APIRouter(tags=["db_config"], dependencies=[Depends(verify_token)])


class GetAllConnectionsType(str, Enum):
    organization = "organization"


@router.post("/db_config/connections", response_model=PublicDbCredential)
def create_db_conn(
    new_db_conn: DbCredentialCreate,
    user_session: UserSession = Depends(get_app_user_session),
) -> Optional[PublicDbCredential]:
    """Creates a database connection"""
    user = user_session.user
    creds = crud.create_conn(user_session.session, new_db_conn, user.id)
    return creds


@router.get("/db_config/connections/{uuid}", response_model=PublicDbCredential)
def read_db_conn(
    uuid: UUID4,
    user_session: UserSession = Depends(get_app_user_session),
) -> Optional[PublicDbCredential]:
    """Read a single connection by UUID. Requires that the user be in the same organization as the connection."""
    user = user_session.user
    try:
        return crud.get_conn(
            db=user_session.session, db_credential_id=uuid, user_id=user.id
        )
    except crud.DbCredentialModelException as e:
        if "not found" in str(e):
            raise HTTPException(status_code=404, detail="Not found")


@router.get("/db_config/connections", response_model=List[PublicDbCredential])
def read_db_conns(
    type: GetAllConnectionsType = GetAllConnectionsType.organization,
    user_session: UserSession = Depends(get_app_user_session),
) -> List[PublicDbCredential]:
    """Read all connections. Requires that the user be in the same organization as the connection."""
    user = user_session.user
    if type == GetAllConnectionsType.organization:
        return crud.get_conns(db=user_session.session, user=user)
    else:
        raise HTTPException(status_code=404, detail="Not found")


@router.patch("/db_config/connections/{uuid}", response_model=PublicDbCredential)
def update_db_conn(
    conn_update: DbCredentialUpdate,
    user_session: UserSession = Depends(get_app_user_session),
) -> Optional[PublicDbCredential]:
    """Updates a single db connection"""
    user = user_session.user
    creds = crud.update_conn(
        user_session.session, conn_update=conn_update, user_id=user.id
    )
    return creds


@router.delete("/db_config/connections/{uuid}")
def delete_db_conn(
    uuid: UUID4,
    user_session: UserSession = Depends(get_app_user_session),
) -> bool:
    """Deletes a database connection"""
    user = user_session.user
    num_rows = crud.delete_conn(user_session.session, uuid, user.id)
    return num_rows > 0
