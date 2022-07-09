from enum import Enum
from typing import Optional, List

from fastapi import APIRouter, Request, Security
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import UUID4

from app.schemas import GeoShape, GeoShapeRead, GeoShapeUpdate, User, GeoShapeCreate

from ..models import SessionLocal
from ..crud import shape as crud
from .common import security


router = APIRouter(tags=["geofencer"])


class GetAllShapesRequestType(str, Enum):
    domain = "domain"
    user = "user"


@router.get("/geofencer/shapes/{uuid}")
def get_shape(uuid: UUID4, credentials: HTTPAuthorizationCredentials = Security(security)) -> Optional[GeoShape]:
    with SessionLocal() as db_session:
        return crud.get_shape(db_session, GeoShapeRead(uuid=uuid))


@router.get("/geofencer/shapes")
def get_all_shapes(request: Request, rtype: GetAllShapesRequestType, credentials: HTTPAuthorizationCredentials = Security(security)) -> Optional[List[GeoShape]]:
    # Set by ProtectedRoutesMiddleware
    user = request.state.user
    with SessionLocal() as db_session:
        if rtype == GetAllShapesRequestType.user:
            return crud.get_all_shapes_by_user(db_session, User(**user.__dict__))
        elif rtype == GetAllShapesRequestType.domain:
            email_domain = user.email.split("@")[1]
            return crud.get_all_shapes_by_email_domain(db_session, email_domain)


@router.post("/geofencer/shapes")
def create_shape(request: Request, geoshape: GeoShapeCreate, credentials: HTTPAuthorizationCredentials = Security(security)) -> Optional[List[GeoShape]]:
    # Set by ProtectedRoutesMiddleware
    user = request.state.user
    with SessionLocal() as db_session:
        return crud.create_shape(db_session, geoshape, user_id=user.id)


@router.put("/geofencer/shapes/{uuid}")
def update_shape(request: Request, geoshape: GeoShapeUpdate, credentials: HTTPAuthorizationCredentials = Security(security)) -> Optional[GeoShape]:
    # Set by ProtectedRoutesMiddleware
    user = request.state.user
    with SessionLocal() as db_session:
        return crud.update_shape(db_session, geoshape, user.id)
