from enum import Enum
from typing import List, Optional

from fastapi import APIRouter, Request, Security, Depends
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import UUID4
from sqlalchemy.orm import Session

from app.crud import db_credentials as crud
from app.db.session import get_db
from app.schemas import PublicDbCredential
from app.schemas.db_credential import DbCredentialCreate, DbCredentialRead

from .common import security

router = APIRouter(tags=["db_config"])


class GetAllConnectionsType(str, Enum):
    organization = "organization"


@router.get("/db_config/connections/{uuid}", response_model=PublicDbCredential)
def get_db_conn(
    request: Request,
    uuid: UUID4,
    credentials: HTTPAuthorizationCredentials = Security(security),
    db_session: Session = Depends(get_db)
) -> Optional[PublicDbCredential]:
    """Read a single connection by UUID. Requires that the user be in the same organization as the connection."""
    user = request.state.user
    return crud.get_conn(db_session, DbCredentialRead(uuid=uuid, user_id=user.id))


@router.post("/db_config/connections", response_model=PublicDbCredential)
def create_db_conn(
    request: Request,
    new_db_conn: DbCredentialCreate,
    credentials: HTTPAuthorizationCredentials = Security(security),
    db_session: Session = Depends(get_db)
) -> Optional[PublicDbCredential]:
    """Create a database connection."""
    user = request.state.user
    creds = crud.create_conn(db_session, new_db_conn, user.id)
    return creds
