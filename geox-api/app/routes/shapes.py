from enum import Enum
from typing import List, Optional

from fastapi import APIRouter, Depends, Request, Security
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import UUID4
from sqlalchemy.orm import Session

from app.crud import shape as crud
from app.db.session import get_db
from app.schemas import (
    GeoShape,
    GeoShapeCreate,
    GeoShapeRead,
    GeoShapeUpdate,
    ShapeCountResponse,
    User,
)

from .common import security

router = APIRouter(tags=["geofencer"])


class GetAllShapesRequestType(str, Enum):
    domain = "domain"
    user = "user"


@router.get("/geofencer/shapes/{uuid}", response_model=GeoShape)
def get_shape(
    uuid: UUID4,
    credentials: HTTPAuthorizationCredentials = Security(security),
    db_session: Session = Depends(get_db),
) -> Optional[GeoShape]:
    return crud.get_shape(db_session, GeoShapeRead(uuid=uuid))


@router.get("/geofencer/shapes", response_model=List[GeoShape])
def get_all_shapes(
    request: Request,
    rtype: GetAllShapesRequestType,
    credentials: HTTPAuthorizationCredentials = Security(security),
    db_session: Session = Depends(get_db),
) -> Optional[List[GeoShape]]:
    # Set by ProtectedRoutesMiddleware
    user = request.state.user
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
    db_session: Session = Depends(get_db),
) -> GeoShape:
    # Set by ProtectedRoutesMiddleware
    user = request.state.user
    shape = crud.create_shape(db_session, geoshape, user_id=user.id)
    return shape


@router.put("/geofencer/shapes/{uuid}", response_model=GeoShape)
def update_shape(
    request: Request,
    geoshape: GeoShapeUpdate,
    credentials: HTTPAuthorizationCredentials = Security(security),
    db_session: Session = Depends(get_db),
) -> Optional[GeoShape]:
    # Set by ProtectedRoutesMiddleware
    user = request.state.user
    shape = crud.update_shape(db_session, geoshape, user.id)
    return shape


@router.delete("/geofencer/shapes")
def bulk_soft_delete_shapes(
    request: Request,
    shape_uuids: List[UUID4],
    credentials: HTTPAuthorizationCredentials = Security(security),
    db_session: Session = Depends(get_db),
) -> ShapeCountResponse:
    # Set by ProtectedRoutesMiddleware
    user = request.state.user
    shape_count = crud.bulk_soft_delete_shapes(db_session, shape_uuids, user.id)
    return shape_count


@router.post("/geofencer/shapes/bulk")
def bulk_create_shapes(
    request: Request,
    geoshapes: List[GeoShapeCreate],
    credentials: HTTPAuthorizationCredentials = Security(security),
    db_session: Session = Depends(get_db),
) -> ShapeCountResponse:
    # Set by ProtectedRoutesMiddleware
    user = request.state.user
    num_shapes_created = crud.bulk_create_shapes(db_session, geoshapes, user.id)
    return num_shapes_created
