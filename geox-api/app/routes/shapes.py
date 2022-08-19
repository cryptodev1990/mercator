from enum import Enum
from typing import List, Optional

from fastapi import APIRouter, Depends, Request, Security
from pydantic import UUID4
from sqlalchemy.orm import Session

from app.crud import shape as crud
from app.dependencies import verify_token, get_app_user_session, UserSession
from app.schemas import (
    GeoShape,
    GeoShapeCreate,
    GeoShapeRead,
    GeoShapeUpdate,
    ShapeCountResponse,
    User,
)

router = APIRouter(tags=["geofencer"], dependencies=[Depends(verify_token)])


class GetAllShapesRequestType(str, Enum):
    domain = "domain"
    user = "user"


@router.get("/geofencer/shapes/{uuid}", response_model=GeoShape)
def get_shape(
    uuid: UUID4,
    user_session: UserSession = Depends(get_app_user_session),
) -> Optional[GeoShape]:
    return crud.get_shape(user_session.session, GeoShapeRead(uuid=uuid))


@router.get("/geofencer/shapes", response_model=List[GeoShape])
def get_all_shapes(
    rtype: GetAllShapesRequestType,
    user_session: UserSession = Depends(get_app_user_session)
) -> Optional[List[GeoShape]]:
    # Set by ProtectedRoutesMiddleware
    user = user_session.user
    db_session = user_session.session
    shapes = []
    if rtype == GetAllShapesRequestType.user:
        shapes = crud.get_all_shapes_by_user(db_session, User(**user.__dict__))
    elif rtype == GetAllShapesRequestType.domain:
        email_domain = user.email.split("@")[1]
        shapes = crud.get_all_shapes_by_email_domain(db_session, email_domain)
    return shapes


@router.post("/geofencer/shapes", response_model=GeoShape)
def create_shape(
    geoshape: GeoShapeCreate,
    user_session: UserSession = Depends(get_app_user_session),
) -> GeoShape:
    # Set by ProtectedRoutesMiddleware
    shape = crud.create_shape(user_session.session, geoshape, user_id=user_session.user.id)
    return shape


@router.put("/geofencer/shapes/{uuid}", response_model=GeoShape)
def update_shape(
    geoshape: GeoShapeUpdate,
    user_session: UserSession = Depends(get_app_user_session),
) -> Optional[GeoShape]:
    # Set by ProtectedRoutesMiddleware
    shape = crud.update_shape(user_session.session, geoshape, user_session.user.id)
    return shape


@router.delete("/geofencer/shapes")
def bulk_soft_delete_shapes(
    shape_uuids: List[UUID4],
    user_session: UserSession = Depends(get_app_user_session),
) -> ShapeCountResponse:
    # Set by ProtectedRoutesMiddleware
    shape_count = crud.bulk_soft_delete_shapes(user_session.session, shape_uuids, user_session.user.id)
    return shape_count


@router.post("/geofencer/shapes/bulk")
def bulk_create_shapes(
    geoshapes: List[GeoShapeCreate],
    user_session: UserSession = Depends(get_app_user_session),
) -> ShapeCountResponse:
    # Set by ProtectedRoutesMiddleware
    num_shapes_created = crud.bulk_create_shapes(user_session.session, geoshapes, user_session.user.id)
    return num_shapes_created
