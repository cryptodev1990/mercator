from enum import Enum
from typing import List, Optional

from app.crud import shape as crud
from app.db.session import SessionLocal
from app.schemas import (GeoShape, GeoShapeCreate, GeoShapeRead,
                         GeoShapeUpdate, User)
from fastapi import APIRouter, Request, Security
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import UUID4

from .common import security

router = APIRouter(tags=["geofencer"])


class GetAllShapesRequestType(str, Enum):
    domain = "domain"
    user = "user"


@router.get("/geofencer/shapes/{uuid}", response_model=GeoShape)
def get_shape(
    uuid: UUID4, credentials: HTTPAuthorizationCredentials = Security(security)
) -> Optional[GeoShape]:
    with SessionLocal() as db_session:
        return crud.get_shape(db_session, GeoShapeRead(uuid=uuid))


@router.get("/geofencer/shapes", response_model=List[GeoShape])
def get_all_shapes(
    request: Request,
    rtype: GetAllShapesRequestType,
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> Optional[List[GeoShape]]:
    # Set by ProtectedRoutesMiddleware
    user = request.state.user
    with SessionLocal() as db_session:
        shapes = []
        if rtype == GetAllShapesRequestType.user:
            shapes = crud.get_all_shapes_by_user(db_session, User(**user.__dict__))
        elif rtype == GetAllShapesRequestType.domain:
            email_domain = user.email.split("@")[1]
            shapes = crud.get_all_shapes_by_email_domain(db_session, email_domain)
        return shapes


@router.post("/geofencer/shapes", response_model=GeoShape)
def create_shape(
    request: Request,
    geoshape: GeoShapeCreate,
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> GeoShape:
    # Set by ProtectedRoutesMiddleware
    user = request.state.user
    with SessionLocal() as db_session:
        shape = crud.create_shape(db_session, geoshape, user_id=user.id)
        return shape


@router.put("/geofencer/shapes/{uuid}", response_model=GeoShape)
def update_shape(
    request: Request,
    geoshape: GeoShapeUpdate,
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> Optional[GeoShape]:
    # Set by ProtectedRoutesMiddleware
    user = request.state.user
    with SessionLocal() as db_session:
        shape = crud.update_shape(db_session, geoshape, user.id)
        return shape
