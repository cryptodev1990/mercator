"""Routes to interct with shapes."""
import logging
from enum import Enum
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import UUID4
from sqlalchemy import func, select

from app.crud.new import shape as crud
from app.dependencies_alt import UserConnection, get_user_connection, verify_token
from app.schemas import (
    GeoShape,
    GeoShapeCreate,
    GeoShapeRead,
    GeoShapeUpdate,
    ShapeCountResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["geofencer"])


class GetAllShapesRequestType(str, Enum):
    """Valid shape request types."""

    user = "user"
    organization = "organization"


@router.post("/geofencer/shapes", response_model=GeoShape)
def create_shape(
    geoshape: GeoShapeCreate,
    user_conn: UserConnection = Depends(get_user_connection),
) -> GeoShape:
    """Create a shape."""
    shape = crud.create_shape(user_conn.connection, geoshape)
    return shape


@router.get("/geofencer/shapes", response_model=List[GeoShape])
def get_all_shapes(
    rtype: GetAllShapesRequestType,
    user_conn: UserConnection = Depends(get_user_connection),
) -> Optional[List[GeoShape]]:
    """Read shapes."""
    user = user_conn.user
    conn = user_conn.connection
    shapes = []
    if rtype == GetAllShapesRequestType.user:
        shapes = crud.get_all_shapes_by_user(conn, user.id)
    elif rtype == GetAllShapesRequestType.organization:
        organization_id = conn.execute(select(func.app_user_org())).scalar()
        shapes = crud.get_all_shapes_by_organization(conn, organization_id)
    return shapes


@router.get("/geofencer/shapes/{uuid}", response_model=GeoShape)
def get_shape(
    uuid: UUID4,
    user_conn: UserConnection = Depends(get_user_connection),
) -> Optional[GeoShape]:
    """Read a shape."""
    return crud.get_shape(user_conn.connection, GeoShapeRead(uuid=uuid))


@router.put("/geofencer/shapes/{uuid}", response_model=GeoShape)
def update_shape(
    geoshape: GeoShapeUpdate,
    user_conn: UserConnection = Depends(get_user_connection),
) -> Optional[GeoShape]:
    """Update a shape."""
    shape: Optional[GeoShape]
    if geoshape.should_delete:
        shape = crud.delete_shape(user_conn.connection, geoshape.uuid)
    else:
        shape = crud.update_shape(user_conn.connection, geoshape)
    return shape


@router.post("/geofencer/shapes/bulk", response_model=ShapeCountResponse)
def bulk_create_shapes(
    geoshapes: List[GeoShapeCreate],
    user_conn: UserConnection = Depends(get_user_connection),
) -> ShapeCountResponse:
    """Create multiple shapes."""
    shapes_uuid = crud.create_many_shapes(user_conn.connection, geoshapes)
    return ShapeCountResponse(num_shapes=len(shapes_uuid))


@router.delete("/geofencer/shapes/bulk", response_model=ShapeCountResponse)
def bulk_delete_shapes(
    shape_uuids: List[UUID4],
    user_conn: UserConnection = Depends(get_user_connection),
) -> ShapeCountResponse:
    """Create multiple shapes."""
    print(shape_uuids)
    row_count = crud.delete_many_shapes(user_conn.connection, shape_uuids)
    return ShapeCountResponse(num_shapes=row_count)
