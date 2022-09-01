import logging
from asyncio.log import logger
from enum import Enum
from typing import List, Optional

from fastapi import APIRouter, Depends, Request, Security
from pydantic import UUID4
from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from app.crud import shape as crud
from app.dependencies import UserSession, get_app_user_session, verify_token
from app.schemas import (
    GeoShape,
    GeoShapeCreate,
    GeoShapeRead,
    GeoShapeUpdate,
    ShapeCountResponse,
)


logger = logging.getLogger(__name__)

router = APIRouter(tags=["geofencer"], dependencies=[Depends(verify_token)])


class GetAllShapesRequestType(str, Enum):
    """Valid shape request types."""
    user = "user"
    organization = "organization"


@router.get("/geofencer/shapes/{uuid}", response_model=GeoShape)
def get_shape(
    uuid: UUID4,
    user_session: UserSession = Depends(get_app_user_session),
) -> Optional[GeoShape]:
    """Read a shape."""
    return crud.get_shape(user_session.session, GeoShapeRead(uuid=uuid))


@router.get("/geofencer/shapes", response_model=List[GeoShape])
def get_all_shapes(
    rtype: GetAllShapesRequestType,
    user_session: UserSession = Depends(get_app_user_session),
) -> Optional[List[GeoShape]]:
    """Read shapes."""
    # Failure cases:
    # No shapes
    # Invalid user_id, organization_id
    # Unable to authorize for organization
    user = user_session.user
    db_session = user_session.session
    shapes = []
    if rtype == GetAllShapesRequestType.user:
        shapes = crud.get_all_shapes_by_user(db_session, user.id)
    elif rtype == GetAllShapesRequestType.organization:
        organization_id = db_session.execute(select(func.app_user_org())).scalar()
        shapes = crud.get_all_shapes_by_organization(db_session, organization_id)
    return shapes


@router.post("/geofencer/shapes", response_model=GeoShape)
def create_shape(
    geoshape: GeoShapeCreate,
    user_session: UserSession = Depends(get_app_user_session),
) -> GeoShape:
    """Create a shape."""
    shape = crud.create_shape(user_session.session, geoshape)
    return shape


@router.put("/geofencer/shapes/{uuid}", response_model=GeoShape)
def update_shape(
    geoshape: GeoShapeUpdate,
    user_session: UserSession = Depends(get_app_user_session),
) -> Optional[GeoShape]:
    """Update a shape."""
    shape: Optional[GeoShape]
    if geoshape.should_delete:
        crud.delete_shape(user_session.session, geoshape.uuid)
        return None
    else:
        shape = crud.update_shape(user_session.session, geoshape)
        return shape


@router.delete("/geofencer/shapes/bulk", response_model=ShapeCountResponse)
def bulk_delete_shapes(
    shape_uuids: List[UUID4],
    user_session: UserSession = Depends(get_app_user_session),
) -> ShapeCountResponse:
    """Delete multiple shapes."""
    shape_count = crud.delete_many_shapes(user_session.session, shape_uuids)
    return ShapeCountResponse(num_shapes=shape_count)


@router.post("/geofencer/shapes/bulk", response_model=ShapeCountResponse)
def bulk_create_shapes(
    geoshapes: List[GeoShapeCreate],
    user_session: UserSession = Depends(get_app_user_session),
) -> ShapeCountResponse:
    """Create multiple shapes."""
    num_shapes_created = crud.create_many_shapes(user_session.session, geoshapes)
    return ShapeCountResponse(num_shapes=num_shapes_created)
